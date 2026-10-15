"""Fine-tuning: ensina o formato pergunta -> resposta.

Para o modelo não decorar o pergeresp (e responder tudo com ele), cada lote mistura:
  1) exemplos do data/qa/*.txt (limitados a ~15% dos exemplos de chat);
  2) exemplos sintéticos gerados dos livros ("continue o texto", "frase com a palavra X",
     "complete a frase"), cujas respostas vêm do que o modelo aprendeu no pré-treino;
  3) trechos de livro puros (replay), para não esquecer o português do pré-treino.

Parte de checkpoints/pretrain_best.pt e grava em checkpoints/finetuned.pt, então o
pré-treino nunca é sobrescrito: dá para repetir só este script à vontade.
"""

import argparse
import math
import random
from pathlib import Path

import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

from chat import generate
from data_utils import (load_qa_examples, synthetic_examples, ASSISTANT_TOKEN, END_TOKEN,
                        EOT_TOKEN, PAD_TOKEN, USER_TOKEN)
from model import build_model

parser = argparse.ArgumentParser()
parser.add_argument("--books", default="data/books")
parser.add_argument("--qa", default="data/qa")
parser.add_argument("--out", default="checkpoints")
parser.add_argument("--epochs", type=int, default=4)
parser.add_argument("--lr", type=float, default=5e-5)
parser.add_argument("--batch-size", type=int, default=16)
parser.add_argument("--synthetic", type=int, default=4000, help="nº de exemplos gerados dos livros")
parser.add_argument("--qa-share", type=float, default=0.15, help="fração dos exemplos de chat vinda do pergeresp")
parser.add_argument("--replay", type=float, default=0.25, help="fração de cada lote com texto puro dos livros")
parser.add_argument("--val-fraction", type=float, default=0.1)
parser.add_argument("--patience", type=int, default=2)
parser.add_argument("--dropout", type=float, default=0.1)
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()

random.seed(args.seed)
torch.manual_seed(args.seed)
out_dir = Path(args.out)
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = Tokenizer.from_file(str(out_dir / "tokenizer.json"))
ckpt = torch.load(out_dir / "pretrain_best.pt", map_location=device)
cfg = ckpt["config"]
block = cfg["block_size"]

model = build_model(cfg, dropout=args.dropout).to(device)
model.load_state_dict(ckpt["model"])
print(f"Pré-treino carregado (val loss {ckpt['val_loss']:.4f}, step {ckpt['step']})")

assistant_id = tokenizer.token_to_id(ASSISTANT_TOKEN)
end_id = tokenizer.token_to_id(END_TOKEN)
pad_id = tokenizer.token_to_id(PAD_TOKEN)
eot_id = tokenizer.token_to_id(EOT_TOKEN)


# ---------- Dados ----------
book_files = sorted(Path(args.books).glob("*.txt"))
if not book_files:
    raise SystemExit(f"Nenhum livro em {args.books}: o fine-tuning usa os livros para gerar exemplos.")
book_texts = [p.read_text(encoding="utf-8") for p in book_files]

print("Lendo perguntas/respostas:")
qa_texts = load_qa_examples(args.qa)
syn_texts = synthetic_examples(book_texts, args.synthetic, seed=args.seed)
print(f"Exemplos sintéticos gerados dos livros: {len(syn_texts)}")
for sample in random.sample(syn_texts, min(3, len(syn_texts))):
    print("   ", sample[:160])


def encode_chat(texts):
    items, too_long = [], 0
    for text in texts:
        ids = tokenizer.encode(text).ids
        if len(ids) > block:
            too_long += 1
            continue
        if assistant_id not in ids or end_id not in ids:
            continue
        answer_start = ids.index(assistant_id) + 1
        inputs = ids[:-1]
        # Loss só na RESPOSTA (e no <|end|>); a pergunta vira -100.
        labels = [tok if pos + 1 >= answer_start else -100 for pos, tok in enumerate(ids[1:])]
        items.append((inputs, labels))
    return items, too_long


qa_data, qa_long = encode_chat(qa_texts)
syn_data, _ = encode_chat(syn_texts)
if qa_long:
    print(f"ATENÇÃO: {qa_long} exemplos do pergeresp passam de {block} tokens e foram descartados.")
if not syn_data:
    raise SystemExit("Não consegui gerar exemplos dos livros. Confira os .txt em data/books.")


def split(items):
    random.shuffle(items)
    n_val = max(1, int(len(items) * args.val_fraction)) if len(items) >= 10 else 0
    return items[n_val:], items[:n_val]


qa_train, qa_val = split(qa_data)
syn_train, syn_val = split(syn_data)

# Repete o pergeresp só o suficiente para ele ser ~qa_share dos exemplos de chat.
qa_repeat = 0
if qa_train:
    wanted = args.qa_share / (1 - args.qa_share) * len(syn_train)
    qa_repeat = max(1, round(wanted / len(qa_train)))
print(f"Treino: {len(syn_train)} sintéticos + {len(qa_train)} do pergeresp (x{qa_repeat}) | "
      f"validação: {len(syn_val)} sintéticos + {len(qa_val)} do pergeresp")

# Texto contínuo dos livros para o replay.
stream = []
for text in book_texts:
    stream.extend(tokenizer.encode(text).ids)
    stream.append(eot_id)
stream = torch.tensor(stream, dtype=torch.long)
n_replay = round(args.batch_size * args.replay / (1 - args.replay)) if args.replay > 0 else 0


def replay_items(n):
    if n == 0:
        return []
    starts = torch.randint(0, len(stream) - block - 1, (n,)).tolist()
    return [(stream[s:s + block].tolist(), stream[s + 1:s + block + 1].tolist()) for s in starts]


def make_batch(items):
    longest = max(len(inp) for inp, _ in items)
    xs, ys = [], []
    for inp, lab in items:
        pad = longest - len(inp)
        # Padding à direita: com máscara causal, as posições reais nunca enxergam o padding.
        xs.append(inp + [pad_id] * pad)
        ys.append(lab + [-100] * pad)
    return torch.tensor(xs, device=device), torch.tensor(ys, device=device)


def batch_loss(items):
    x, y = make_batch(items)
    logits = model(x)
    return F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)


@torch.no_grad()
def validate(items):
    if not items:
        return float("nan")
    model.eval()
    losses = [batch_loss(items[i:i + args.batch_size]).item()
              for i in range(0, len(items), args.batch_size)]
    model.train()
    return sum(losses) / len(losses)


SAMPLE_PROMPTS = ["Oi", "O que é um rio?", "Escreva uma frase com a palavra noite.",
                  "Continue o texto: Era uma manhã fria quando ele saiu de casa.",
                  "Quem escreveu Dom Casmurro?"]


@torch.no_grad()
def show_samples():
    model.eval()
    for question in SAMPLE_PROMPTS:
        prompt = f"{USER_TOKEN} {question} {ASSISTANT_TOKEN}"
        answer = generate(model, tokenizer, prompt, device, max_new_tokens=60)
        print(f"   Você: {question}\n   LLM:  {answer}")
    model.train()


# ---------- Treino ----------
optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
items_per_epoch = len(syn_train) + len(qa_train) * qa_repeat
steps_per_epoch = math.ceil(items_per_epoch / args.batch_size)
total_steps = steps_per_epoch * args.epochs
warmup = min(100, total_steps // 10)
print(f"{steps_per_epoch} steps por época, até {total_steps} no total "
      f"(lote = {args.batch_size} de chat + {n_replay} de livro)")


def lr_at(step):
    if step < warmup:
        return args.lr * (step + 1) / warmup
    progress = (step - warmup) / max(1, total_steps - warmup)
    return args.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0))))


print("\nAntes do fine-tuning:")
show_samples()

best_val, bad_epochs, step = float("inf"), 0, 0
best_path = out_dir / "finetuned.pt"
model.train()

for epoch in range(1, args.epochs + 1):
    train_items = syn_train + qa_train * qa_repeat
    random.shuffle(train_items)
    running = 0.0
    for i in range(0, len(train_items), args.batch_size):
        for group in optimizer.param_groups:
            group["lr"] = lr_at(step)
        loss = batch_loss(train_items[i:i + args.batch_size] + replay_items(n_replay))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        running += loss.item()
        step += 1

    syn_v, qa_v = validate(syn_val), validate(qa_val)
    # Critério de parada: os dois tipos de pergunta contam igual.
    combined = syn_v if math.isnan(qa_v) else 0.5 * (syn_v + qa_v)
    note = ""
    if combined < best_val:
        best_val, bad_epochs, note = combined, 0, "  <- melhor, salvo"
        torch.save({"model": model.state_dict(), "config": cfg, "val_loss": combined,
                    "finetuned": True}, best_path)
    else:
        bad_epochs += 1
    print(f"\népoca {epoch} | treino {running / steps_per_epoch:.4f} | val livros {syn_v:.4f} | "
          f"val pergeresp {qa_v:.4f}{note}", flush=True)
    show_samples()
    if bad_epochs >= args.patience:
        print("Early stopping.")
        break

print("=" * 40)
print(f"Fine-tuning concluído. Melhor val: {best_val:.4f} -> {best_path}")
print("Se ainda repetir o pergeresp: rode de novo com --qa-share 0.08 ou --lr 3e-5.")
print("Converse com: python chat.py")
