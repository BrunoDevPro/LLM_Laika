"""Fine-tuning: ensina o formato pergunta -> resposta usando data/qa/*.txt.

Parte de checkpoints/pretrain_best.pt e grava em checkpoints/finetuned.pt, então
o pré-treino nunca é sobrescrito (dá para repetir o fine-tuning à vontade).
"""

import argparse
import math
import random
from pathlib import Path

import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

from data_utils import load_qa_examples, ASSISTANT_TOKEN, END_TOKEN, PAD_TOKEN
from model import build_model

parser = argparse.ArgumentParser()
parser.add_argument("--qa", default="data/qa")
parser.add_argument("--out", default="checkpoints")
parser.add_argument("--epochs", type=int, default=30)
parser.add_argument("--lr", type=float, default=1e-4)
parser.add_argument("--batch-size", type=int, default=16)
parser.add_argument("--val-fraction", type=float, default=0.15)
parser.add_argument("--patience", type=int, default=4)
parser.add_argument("--dropout", type=float, default=0.1)
args = parser.parse_args()

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

print("Lendo perguntas/respostas:")
texts = load_qa_examples(args.qa)

dataset, too_long = [], 0
for text in texts:
    ids = tokenizer.encode(text).ids
    if len(ids) > block:
        too_long += 1
        continue
    if assistant_id not in ids or end_id not in ids:
        continue
    answer_start = ids.index(assistant_id) + 1
    inputs = ids[:-1]
    # Só calcula a loss nos tokens da RESPOSTA (e no <|end|>); a pergunta vira -100.
    labels = [tok if pos + 1 >= answer_start else -100 for pos, tok in enumerate(ids[1:])]
    dataset.append((inputs, labels))

print(f"Exemplos utilizáveis: {len(dataset)} de {len(texts)}")
if too_long:
    print(f"ATENÇÃO: {too_long} exemplos passam de {block} tokens e foram descartados "
          f"({100 * too_long / max(1, len(texts)):.0f}%). Encurte as respostas.")
if len(dataset) < 20:
    raise SystemExit("Poucos exemplos válidos. Adicione mais perguntas/respostas em data/qa/.")
if len(dataset) < 200:
    print("Aviso: menos de 200 exemplos — o modelo tende a decorar. Quanto mais variedade, melhor.")

random.seed(0)
random.shuffle(dataset)
n_val = max(1, int(len(dataset) * args.val_fraction))
val_set, train_set = dataset[:n_val], dataset[n_val:]
print(f"Treino: {len(train_set)} | Validação: {len(val_set)}")


def make_batch(items):
    longest = max(len(inp) for inp, _ in items)
    xs, ys = [], []
    for inp, lab in items:
        pad = longest - len(inp)
        # Padding à direita: com máscara causal, as posições reais nunca enxergam o padding.
        xs.append(inp + [pad_id] * pad)
        ys.append(lab + [-100] * pad)
    return (torch.tensor(xs, device=device), torch.tensor(ys, device=device))


def batch_loss(x, y):
    logits = model(x)
    return F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)


@torch.no_grad()
def validate():
    model.eval()
    total, count = 0.0, 0
    for i in range(0, len(val_set), args.batch_size):
        x, y = make_batch(val_set[i:i + args.batch_size])
        total += batch_loss(x, y).item()
        count += 1
    model.train()
    return total / count


optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
steps_per_epoch = math.ceil(len(train_set) / args.batch_size)
total_steps = steps_per_epoch * args.epochs
warmup = min(30, total_steps // 10)


def lr_at(step):
    if step < warmup:
        return args.lr * (step + 1) / warmup
    progress = (step - warmup) / max(1, total_steps - warmup)
    return args.lr * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0)))


best_val, bad_epochs, step = float("inf"), 0, 0
best_path = out_dir / "finetuned.pt"
model.train()

for epoch in range(1, args.epochs + 1):
    random.shuffle(train_set)
    running = 0.0
    for i in range(0, len(train_set), args.batch_size):
        for group in optimizer.param_groups:
            group["lr"] = lr_at(step)
        x, y = make_batch(train_set[i:i + args.batch_size])
        loss = batch_loss(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        running += loss.item()
        step += 1

    val = validate()
    note = ""
    if val < best_val:
        best_val, bad_epochs, note = val, 0, "  <- melhor, salvo"
        torch.save({"model": model.state_dict(), "config": cfg, "val_loss": val,
                    "finetuned": True}, best_path)
    else:
        bad_epochs += 1
    print(f"época {epoch:>3} | treino {running / steps_per_epoch:.4f} | val {val:.4f}{note}", flush=True)
    if bad_epochs >= args.patience:
        print("Early stopping.")
        break

print("=" * 40)
print(f"Fine-tuning concluído. Melhor val loss: {best_val:.4f} -> {best_path}")
print("Converse com: python chat.py")
