"""Conversa com o modelo.

  python chat.py            -> modo chat (checkpoints/finetuned.pt), com RAG e memória
  python chat.py --base     -> modo "completar texto" com o modelo só pré-treinado
  python chat.py --no-rag   -> sem busca nos textos
  python chat.py --no-memory
  python chat.py --no-history -> sem as últimas mensagens no prompt

Comandos durante a conversa:
  /fontes   mostra ou esconde o "*Nome do artigo" no fim das respostas que usaram o RAG
  /rag      liga ou desliga a busca nos textos
  /memoria  mostra o que a Laika lembra sobre você
  /limpar   esquece as mensagens anteriores (a "memória de IA": as últimas trocas entram no prompt)
  sair      encerra
"""

import argparse
from pathlib import Path

import torch

from data_utils import (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN, EOT_TOKEN, PAD_TOKEN, MAX_CONTEXT_WORDS,
                        MAX_HISTORY, chat_turn, fit_context, rag_chunks, wants_rag)
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


def build_prompt(question, tokenizer, block_size, rag=None, memory=None, max_new_tokens=80, history=None):
    """Monta o prompt do chat. Devolve (prompt, título do artigo usado pelo RAG ou None).

    Se a pergunta pede informação (wants_rag) e o RAG acha trechos relevantes (1 a 3, conforme a
    janela do modelo), ou se há anotações da memória ligadas à pergunta, a pergunta ganha um
    "Contexto:", no mesmo formato usado no fine-tuning, cortado para caber na janela.
    history: as trocas anteriores [(pergunta, resposta), ...], da mais antiga para a mais nova
    ("memória de IA"). Entram as mais recentes (até MAX_HISTORY) que couberem depois da pergunta.
    """
    budget = block_size - max_new_tokens

    def count(text):
        return len(tokenizer.encode(text).ids)

    context_parts, source = [], None
    if memory is not None:
        note = memory.context_for(question)
        if note:
            context_parts.append(note)
    hits = rag.contexts(question, rag_chunks(block_size)) if rag is not None and wants_rag(question) else []
    if hits:
        context_parts += [h["text"] for h in hits]
        source = hits[0]["title"]
    current = f"{USER_TOKEN} {question} {ASSISTANT_TOKEN}"
    if context_parts:
        user_text = fit_context(lambda t: count(f"{USER_TOKEN} {t} {ASSISTANT_TOKEN}"), question,
                                " ".join(context_parts), budget, max_words=MAX_CONTEXT_WORDS * max(1, len(hits)))
        if user_text is None:
            source = None
        else:
            current = f"{USER_TOKEN} {user_text} {ASSISTANT_TOKEN}"

    turns = []
    for q, a in reversed(list(history or [])[-MAX_HISTORY:]):
        candidate = [chat_turn(q, a)] + turns
        if count(" ".join(candidate + [current])) > budget:
            break
        turns = candidate
    return " ".join(turns + [current]), source


def with_citation(answer, source):
    """Acrescenta ' *Nome do artigo' no fim da resposta quando o RAG foi usado."""
    return f"{answer} *{source}" if source else answer


def min_answer_tokens(max_new_tokens):
    """Com um tamanho máximo grande, a resposta tende a ser mais longa: até este número de tokens,
    o <|end|> perde força (sem ser proibido). 80 -> 10, 120 -> 30, 60 ou menos -> 0."""
    return max(0, (max_new_tokens - 60) // 2)


def end_penalty(step, min_tokens):
    """Quanto tirar do logit do <|end|> no passo `step` (0 = primeiro token da resposta)."""
    return 0.0 if step >= min_tokens else 3.0 * (1 - step / min_tokens)


@torch.no_grad()
def generate(model, tokenizer, prompt, device, max_new_tokens=80, temperature=0.7,
             top_k=40, top_p=0.9, repetition_penalty=1.15, stop_at_end=True):
    ids = tokenizer.encode(prompt).ids
    prompt_len = len(ids)
    end_id = tokenizer.token_to_id(END_TOKEN)
    banned = [tokenizer.token_to_id(t) for t in (USER_TOKEN, ASSISTANT_TOKEN, PAD_TOKEN, EOT_TOKEN)]
    if not stop_at_end:
        banned.append(end_id)
    min_tokens = min_answer_tokens(max_new_tokens) if stop_at_end else 0

    for _ in range(max_new_tokens):
        context = ids[-model.block_size:]
        x = torch.tensor([context], dtype=torch.long, device=device)
        logits = model(x)[0, -1].float()

        for token_id in banned:
            if token_id is not None:
                logits[token_id] = -float("inf")
        if min_tokens and end_id is not None:
            logits[end_id] -= end_penalty(len(ids) - prompt_len, min_tokens)

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
    parser.add_argument("--no-history", action="store_true",
                        help="não põe as últimas mensagens da conversa no prompt (memória de IA)")
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
    history = None if args.no_history else []
    print(f"RAG: {'ligado' if rag else 'desligado'} | memória: {'ligada' if memory else 'desligada'} | "
          f"memória de IA: {'ligada' if history is not None else 'desligada'}")
    print("Digite 'sair' para encerrar. Comandos: /fontes, /rag, /memoria, /limpar")

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
        if text == "/limpar":
            history = None if history is None else []
            print("(conversa esquecida: a Laika não vê mais as mensagens anteriores)")
            continue

        answer = memory.handle(text) if memory is not None else None
        if answer:
            print("LLM:", answer)
        else:
            prompt, source = build_prompt(text, tokenizer, model.block_size, rag, memory, args.max_new_tokens,
                                          history)
            answer = generate(model, tokenizer, prompt, device, args.max_new_tokens, args.temperature)
            print("LLM:", with_citation(answer, source) if show_sources else answer)
        if history is not None and answer:
            history = (history + [(text, answer)])[-MAX_HISTORY:]


if __name__ == "__main__":
    main()
