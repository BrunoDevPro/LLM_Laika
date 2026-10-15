"""Conversa com o modelo.

  python chat.py            -> modo chat (usa checkpoints/finetuned.pt)
  python chat.py --base     -> modo "completar texto" com o modelo só pré-treinado
                               (bom para avaliar se o pré-treino já escreve português)
"""

import argparse
from pathlib import Path

import torch

from data_utils import USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN, EOT_TOKEN, PAD_TOKEN
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


@torch.no_grad()
def generate(model, tokenizer, prompt, device, max_new_tokens=120, temperature=0.7,
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

        # Penaliza só tokens que o próprio modelo já gerou (não a pergunta).
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
    parser.add_argument("--max-new-tokens", type=int, default=120)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, tokenizer = load(args.out, args.base, device)
    print("Digite 'sair' para encerrar.")

    while True:
        text = input("\nVocê: " if not args.base else "\nInício do texto: ").strip()
        if text.lower() in {"sair", "exit", "quit"}:
            break
        if not text:
            continue
        if args.base:
            answer = generate(model, tokenizer, text, device, args.max_new_tokens,
                              args.temperature, stop_at_end=False)
            print("Continuação:", text, answer)
        else:
            prompt = f"{USER_TOKEN} {text} {ASSISTANT_TOKEN}"
            answer = generate(model, tokenizer, prompt, device, args.max_new_tokens, args.temperature)
            print("LLM:", answer)


if __name__ == "__main__":
    main()
