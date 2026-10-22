"""Conversa com o modelo.

  python chat.py            -> modo chat (checkpoints/finetuned.pt), com RAG e memória
  python chat.py --base     -> modo "completar texto" com o modelo só pré-treinado
  python chat.py --no-rag   -> sem busca nos textos
  python chat.py --no-memory

Comandos durante a conversa:
  /fontes   mostra ou esconde de onde veio o contexto
  /rag      liga ou desliga a busca nos textos
  /memoria  mostra o que a Laika lembra sobre você
  sair      encerra
"""

import argparse
from pathlib import Path

import torch

from data_utils import (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN, EOT_TOKEN, PAD_TOKEN,
                        fit_context, wants_rag)
from model import build_model


def load(out_dir, base, device):
    from tokenizers import Tokenizer

    out_dir = Path(out_dir)
    tokenizer = Tokenizer.from_file(str(out_dir / "tokenizer.json"))
    path = out_dir / ("pretrain_best.pt" if base else "finetuned.pt")
    if not path.exists():
        raise SystemExit(f"{path} não existe. Rode train.py{'' if base else ' e finetune.py'} antes.")
    ckpt = torch.load(path, map_location=device)
    model = build_model(ckpt["config"], dropout=0.0).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, tokenizer


def build_prompt(question, tokenizer, block_size, rag=None, memory=None, max_new_tokens=80):
    """Monta o prompt do chat. Devolve (prompt, fonte ou None).

    Se a pergunta pede informação (wants_rag) e o RAG acha um trecho relevante, ou se há
    anotações da memória ligadas à pergunta, o prompt ganha um "Contexto:", no mesmo
    formato usado no fine-tuning. O contexto é cortado para caber na janela do modelo.
    """
    context_parts, source = [], None
    if memory is not None:
        note = memory.context_for(question)
        if note:
            context_parts.append(note)
            source = "memória"
    if rag is not None and wants_rag(question):
        hit = rag.best(question)
        if hit:
            context_parts.append(hit["text"])
            source = f"{hit['title']} ({hit['kind']})" if not source else f"{source} + {hit['title']}"
    plain = f"{USER_TOKEN} {question} {ASSISTANT_TOKEN}"
    if not context_parts:
        return plain, None

    def count(user_text):
        return len(tokenizer.encode(f"{USER_TOKEN} {user_text} {ASSISTANT_TOKEN}").ids)

    budget = block_size - max_new_tokens
    user_text = fit_context(count, question, " ".join(context_parts), budget)
    if user_text is None:
        return plain, None
    return f"{USER_TOKEN} {user_text} {ASSISTANT_TOKEN}", source


@torch.no_grad()
def generate(model, tokenizer, prompt, device, max_new_tokens=80, temperature=0.7,
             top_k=40, top_p=0.9, repetition_penalty=1.15, stop_at_end=True):
    ids = tokenizer.encode(prompt).ids
    prompt_len = len(ids)
    end_id = tokenizer.token_to_id(END_TOKEN)
    banned = [tokenizer.token_to_id(t) for t in (USER_TOKEN, ASSISTANT_TOKEN, PAD_TOKEN, EOT_TOKEN)]
    if not stop_at_end:
        banned.append(end_id)

    for _ in range(max_new_tokens):
        context = ids[-model.block_size:]
        x = torch.tensor([context], dtype=torch.long, device=device)
        logits = model(x)[0, -1].float()

        for token_id in banned:
            if token_id is not None:
                logits[token_id] = -float("inf")

        # Penaliza só tokens que o próprio modelo já gerou (não a pergunta nem o contexto).
        for token_id in set(ids[prompt_len:][-60:]):
            logits[token_id] = logits[token_id] / repetition_penalty if logits[token_id] > 0 \
                else logits[token_id] * repetition_penalty

        logits = logits / temperature
        values, indices = torch.topk(logits, min(top_k, logits.size(-1)))
        probs = torch.softmax(values, dim=-1)

        # top-p (nucleus) dentro do top-k
        sorted_probs, order = torch.sort(probs, descending=True)
        cumulative = torch.cumsum(sorted_probs, dim=-1)
        keep = cumulative - sorted_probs < top_p
        sorted_probs = sorted_probs * keep
        sorted_probs = sorted_probs / sorted_probs.sum()
        choice = order[torch.multinomial(sorted_probs, 1)]
        next_id = indices[choice].item()

        if stop_at_end and next_id == end_id:
            break
        ids.append(next_id)

    # Decodifica SÓ o que foi gerado, sem repetir o prompt.
    return tokenizer.decode(ids[prompt_len:]).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="checkpoints")
    parser.add_argument("--base", action="store_true", help="usa o modelo pré-treinado (completar texto)")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--rag-db", default="data/rag/laika_rag.db")
    parser.add_argument("--no-rag", action="store_true")
    parser.add_argument("--memory", default="checkpoints/memoria.json")
    parser.add_argument("--no-memory", action="store_true")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, tokenizer = load(args.out, args.base, device)

    if args.base:
        print("Modo completar texto. Digite 'sair' para encerrar.")
        while True:
            text = input("\nInício do texto: ").strip()
            if text.lower() in {"sair", "exit", "quit"}:
                break
            if text:
                answer = generate(model, tokenizer, text, device, args.max_new_tokens * 2,
                                  args.temperature, stop_at_end=False)
                print("Continuação:", text, answer)
        return

    from memory import Memory
    from rag import open_index

    rag = None if args.no_rag else open_index(args.rag_db)
    memory = None if args.no_memory else Memory(args.memory)
    show_sources = True
    print(f"RAG: {'ligado' if rag else 'desligado'} | memória: {'ligada' if memory else 'desligada'}")
    print("Digite 'sair' para encerrar. Comandos: /fontes, /rag, /memoria")

    while True:
        text = input("\nVocê: ").strip()
        if text.lower() in {"sair", "exit", "quit"}:
            break
        if not text:
            continue
        if text == "/fontes":
            show_sources = not show_sources
            print(f"(fontes {'visíveis' if show_sources else 'escondidas'})")
            continue
        if text == "/rag":
            rag = None if rag else open_index(args.rag_db)
            print(f"(RAG {'ligado' if rag else 'desligado'})")
            continue
        if text == "/memoria":
            print("LLM:", memory.summary() if memory else "A memória está desligada.")
            continue

        if memory is not None:
            remembered = memory.handle(text)
            if remembered:
                print("LLM:", remembered)
                continue

        prompt, source = build_prompt(text, tokenizer, model.block_size, rag, memory, args.max_new_tokens)
        answer = generate(model, tokenizer, prompt, device, args.max_new_tokens, args.temperature)
        print("LLM:", answer)
        if source and show_sources:
            print(f"     (contexto: {source})")


if __name__ == "__main__":
    main()
