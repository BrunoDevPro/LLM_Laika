"""Pré-treinamento: aprende português a partir dos livros em data/books/*.txt."""

import argparse
import math
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers

from config import PRESETS
from data_utils import SPECIAL_TOKENS, EOT_TOKEN, UNK_TOKEN
from model import build_model

parser = argparse.ArgumentParser()
parser.add_argument("--preset", default="tiny", choices=PRESETS.keys())
parser.add_argument("--books", default="data/books")
parser.add_argument("--qa", default="data/qa")
parser.add_argument("--out", default="checkpoints")
parser.add_argument("--max-steps", type=int, default=None)
parser.add_argument("--resume", action="store_true",
                    help="continua a partir de checkpoints/pretrain_best.pt (mesmo tokenizer e tamanho)")
args = parser.parse_args()

cfg = dict(PRESETS[args.preset])
if args.max_steps:
    cfg["max_steps"] = args.max_steps

out_dir = Path(args.out)
out_dir.mkdir(exist_ok=True)
tokenizer_path = out_dir / "tokenizer.json"
best_path = out_dir / "pretrain_best.pt"

device = "cuda" if torch.cuda.is_available() else "cpu"
use_cuda = device == "cuda"
print("Dispositivo:", device)

book_files = sorted(Path(args.books).glob("*.txt"))
if not book_files:
    raise SystemExit(f"Nenhum .txt em {args.books}. Rode prepare_data.py ou coloque seus livros lá.")
print(f"{len(book_files)} livros em {args.books}")


# ---------- Tokenizer ----------
if args.resume and tokenizer_path.exists():
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    print("Tokenizer carregado de", tokenizer_path)
else:
    tokenizer = Tokenizer(models.BPE(unk_token=UNK_TOKEN))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=cfg["vocab_size"],
        special_tokens=SPECIAL_TOKENS,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )
    qa_files = sorted(Path(args.qa).glob("*.txt")) if Path(args.qa).exists() else []
    tokenizer.train([str(p) for p in book_files + qa_files], trainer)
    tokenizer.save(str(tokenizer_path))
    print("Tokenizer treinado e salvo em", tokenizer_path)

cfg["vocab_size"] = tokenizer.get_vocab_size()
eot_id = tokenizer.token_to_id(EOT_TOKEN)


# ---------- Dados ----------
ids = []
for path in book_files:
    ids.extend(tokenizer.encode(path.read_text(encoding="utf-8")).ids)
    ids.append(eot_id)
data = torch.tensor(ids, dtype=torch.long)

block = cfg["block_size"]
n_val = max(block * 40, int(len(data) * 0.05))
if len(data) < n_val + block * 10:
    raise SystemExit(f"Poucos dados ({len(data)} tokens). Adicione mais livros.")
train_data, val_data = data[:-n_val], data[-n_val:]

# Parâmetros vs. tokens: regra prática ~20 tokens de treino por parâmetro.
model = build_model(cfg).to(device)
n_params = model.num_params()
print(f"Tokens: {len(data):,} | Parâmetros: {n_params:,} | "
      f"tokens/parâmetro: {len(train_data) / n_params:.1f} (ideal ≈ 20)")

if args.resume and best_path.exists():
    ckpt = torch.load(best_path, map_location=device)
    if ckpt["config"]["vocab_size"] != cfg["vocab_size"]:
        raise SystemExit("vocab_size do checkpoint não bate com o tokenizer atual.")
    model.load_state_dict(ckpt["model"])
    print(f"Pesos carregados de {best_path} (val loss {ckpt['val_loss']:.4f})")


def get_batch(source):
    starts = torch.randint(0, len(source) - block - 1, (cfg["batch_size"],))
    x = torch.stack([source[i:i + block] for i in starts])
    y = torch.stack([source[i + 1:i + block + 1] for i in starts])
    return x.to(device), y.to(device)


@torch.no_grad()
def evaluate():
    model.eval()
    losses = []
    for _ in range(cfg["eval_iters"]):
        x, y = get_batch(val_data)
        with torch.autocast(device_type=device, dtype=torch.float16, enabled=use_cuda):
            logits = model(x)
        losses.append(F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1)).item())
    model.train()
    return sum(losses) / len(losses)


# ---------- Otimizador ----------
decay = [p for p in model.parameters() if p.dim() >= 2]
no_decay = [p for p in model.parameters() if p.dim() < 2]
optimizer = torch.optim.AdamW(
    [{"params": decay, "weight_decay": 0.1}, {"params": no_decay, "weight_decay": 0.0}],
    lr=cfg["learning_rate"], betas=(0.9, 0.95),
)
scaler = torch.amp.GradScaler("cuda", enabled=use_cuda)


def lr_at(step):
    if step < cfg["warmup_steps"]:
        return cfg["learning_rate"] * (step + 1) / cfg["warmup_steps"]
    progress = (step - cfg["warmup_steps"]) / max(1, cfg["max_steps"] - cfg["warmup_steps"])
    return cfg["learning_rate"] * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0))))


# ---------- Treino ----------
best_val = float("inf")
evals_without_gain = 0
start = time.time()
model.train()

for step in range(cfg["max_steps"] + 1):
    for group in optimizer.param_groups:
        group["lr"] = lr_at(step)

    if step % cfg["eval_every"] == 0:
        val_loss = evaluate()
        marker = ""
        if val_loss < best_val:
            best_val, evals_without_gain, marker = val_loss, 0, "  <- melhor, salvo"
            torch.save({"model": model.state_dict(), "config": cfg, "step": step,
                        "val_loss": val_loss}, best_path)
        else:
            evals_without_gain += 1
        print(f"step {step:>6} | val loss {val_loss:.4f} (ppl {math.exp(val_loss):.0f}) | "
              f"{time.time() - start:.0f}s{marker}", flush=True)
        if evals_without_gain >= cfg["patience"]:
            print("Early stopping: a validação parou de melhorar.")
            break
        if step == cfg["max_steps"]:
            break

    x, y = get_batch(train_data)
    with torch.autocast(device_type=device, dtype=torch.float16, enabled=use_cuda):
        logits = model(x)
    loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))

    optimizer.zero_grad(set_to_none=True)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(optimizer)
    scaler.update()

    if step % 100 == 0:
        print(f"step {step:>6} | train loss {loss.item():.4f}", flush=True)

print("=" * 40)
print(f"Pré-treino concluído. Melhor val loss: {best_val:.4f} -> {best_path}")
print("Referência: val loss > 4.5 = ainda não aprendeu gramática; < 3.5 = frases já fazem sentido.")
print("Teste a fluência com: python chat.py --base")
