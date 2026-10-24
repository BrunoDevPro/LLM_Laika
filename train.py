"""Pré-treinamento: aprende português a partir dos textos em data/books, data/wiki e data/modern
(e, para os modelos grandes, data/carolina e data/gigaverbo, baixados pelo prepare_data.py)."""

import argparse
import hashlib
import shutil
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers

from config import PRESETS
from data_utils import SPECIAL_TOKENS, EOT_TOKEN, UNK_TOKEN
from model import build_model

parser = argparse.ArgumentParser()
parser.add_argument("--preset", default="tiny", choices=PRESETS.keys())
parser.add_argument("--books", nargs="+",
                    default=["data/books", "data/wiki", "data/modern", "data/carolina", "data/gigaverbo"],
                    help="pastas com .txt para o pré-treino (as que não existirem são ignoradas)")
parser.add_argument("--modern-repeat", type=int, default=3,
                    help="quantas vezes os textos de data/modern entram no treino (são poucos e modernos)")
parser.add_argument("--qa", default="data/qa")
parser.add_argument("--out", default="checkpoints")
parser.add_argument("--max-steps", type=int, default=None)
parser.add_argument("--batch-size", type=int, default=None, help="troca o lote do preset (testes rápidos)")
parser.add_argument("--accum", type=int, default=None,
                    help="troca a acumulação de gradiente (ex.: faltou memória na GPU: --batch-size 8 --accum 16)")
parser.add_argument("--tokenizer-mb", type=float, default=None,
                    help="treina o tokenizer numa amostra de N MB, equilibrada entre as pastas (0 = todos os textos)")
parser.add_argument("--compile", action="store_true", help="usa torch.compile (GPU; mais rápido depois de compilar)")
parser.add_argument("--eval-iters", type=int, default=None, help="troca o nº de lotes da validação")
parser.add_argument("--eval-every", type=int, default=None, help="troca de quantos em quantos passos validar")
parser.add_argument("--tokens-dir", default="data/tokens",
                    help="onde guardar os textos já tokenizados (uint16 em disco, lidos com memmap)")
parser.add_argument("--tokens-backup", default=None,
                    help="pasta (ex.: no Drive) para guardar uma cópia dos tokens: numa máquina nova, copiar de "
                         "volta é mais rápido do que tokenizar bilhões de tokens de novo")
parser.add_argument("--resume", action="store_true",
                    help="continua: retoma um treino interrompido (pretrain_last.pt) do ponto em que parou, "
                         "ou parte dos pesos do pretrain_best.pt com um agendamento novo")
args = parser.parse_args()

cfg = dict(PRESETS[args.preset])
cfg.setdefault("accum", 1)
cfg["preset"] = args.preset
for chave, valor in [("max_steps", args.max_steps), ("batch_size", args.batch_size), ("eval_iters", args.eval_iters),
                     ("eval_every", args.eval_every), ("accum", args.accum)]:
    if valor:
        cfg[chave] = valor
ARQUITETURA = ("vocab_size", "block_size", "embed_size", "heads", "layers", "rope")

out_dir = Path(args.out)
out_dir.mkdir(exist_ok=True)
tokenizer_path = out_dir / "tokenizer.json"
best_path = out_dir / "pretrain_best.pt"
last_path = out_dir / "pretrain_last.pt"

device = "cuda" if torch.cuda.is_available() else "cpu"
use_cuda = device == "cuda"
# bf16 na A100/L4/H100 (não precisa do GradScaler); fp16 na T4.
bf16 = use_cuda and torch.cuda.is_bf16_supported()
amp_dtype = torch.bfloat16 if bf16 else torch.float16
if use_cuda:
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
print("Dispositivo:", device, "(bf16)" if bf16 else "(fp16)" if use_cuda else "")

book_files = []
for folder in args.books:
    found = sorted(Path(folder).glob("*.txt"))
    if not found and folder in ("data/carolina", "data/gigaverbo"):
        continue  # só existem se o prepare_data.py baixou
    size = sum(f.stat().st_size for f in found) / 1e6
    print(f"{folder}: {len(found)} arquivos ({size:.1f} MB)")
    book_files.extend(found)
if not book_files:
    raise SystemExit(f"Nenhum .txt em {args.books}. Rode prepare_data.py ou coloque seus livros lá.")


# ---------- Tokenizer ----------
def amostra_tokenizer(files, mb, pasta):
    """Uma amostra de ~mb MB para treinar o tokenizer, dividida igualmente entre as pastas (a que tem menos
    texto entra inteira e o que sobra vai para as outras). Com 8 GB de texto, treinar o BPE em tudo gastaria
    dezenas de GB de RAM; e assim o português antigo dos livros não domina o vocabulário."""
    pasta.mkdir(parents=True, exist_ok=True)
    por_pasta = {}
    for f in files:
        por_pasta.setdefault(f.parent, []).append(f)
    tamanhos = {d: sum(f.stat().st_size for f in fs) for d, fs in por_pasta.items()}
    restante, faltam, saida = mb * 1e6, len(por_pasta), []
    for d in sorted(por_pasta, key=tamanhos.get):
        cota = min(tamanhos[d], restante / faltam)
        restante -= cota
        faltam -= 1
        por_arquivo = cota / len(por_pasta[d])
        destino = pasta / f"{d.name}.txt"
        with open(destino, "w", encoding="utf-8") as out:
            for f in por_pasta[d]:
                with open(f, encoding="utf-8", errors="ignore") as g:
                    texto = g.read(int(por_arquivo) + 1)
                if len(texto) > por_arquivo:
                    texto = texto[:texto.rfind("\n\n") if "\n\n" in texto else len(texto)]
                out.write(texto.replace(EOT_TOKEN, "") + "\n\n")
        saida.append(destino)
        print(f"  amostra do tokenizer: {d} {cota / 1e6:,.0f} MB")
    return saida


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
    amostra_mb = args.tokenizer_mb if args.tokenizer_mb is not None else cfg.get("tokenizer_mb", 0)
    total_mb = sum(f.stat().st_size for f in book_files) / 1e6
    if amostra_mb and total_mb > amostra_mb:
        pasta_amostra = out_dir / "_amostra_tokenizer"
        arquivos = amostra_tokenizer(book_files, amostra_mb, pasta_amostra)
        tokenizer.train([str(p) for p in arquivos + qa_files], trainer)
        shutil.rmtree(pasta_amostra, ignore_errors=True)
    else:
        tokenizer.train([str(p) for p in book_files + qa_files], trainer)
    tokenizer.save(str(tokenizer_path))
    print("Tokenizer treinado e salvo em", tokenizer_path)

cfg["vocab_size"] = tokenizer.get_vocab_size()
eot_id = tokenizer.token_to_id(EOT_TOKEN)


# ---------- Dados: tokens em disco ----------
# Validação = os últimos 5% de CADA arquivo (antes era só o fim do último livro, o que media um
# livro só). Os tokens vão para dois arquivos uint16 (treino e validação) lidos com np.memmap:
# com 1 milhão de artigos (~450 M tokens) eles não caberiam na RAM como antes. Se os textos e o
# tokenizer não mudaram, os arquivos da execução anterior são reaproveitados.
def assinatura(files):
    h = hashlib.sha1(tokenizer_path.read_bytes())
    h.update(f"repeat={args.modern_repeat}".encode())
    for f in files:
        h.update(f"{f.parent.name}/{f.name}:{f.stat().st_size}\n".encode())
    return h.hexdigest()[:16]


def pedacos(texto, tamanho=1 << 20):
    """Textos grandes em pedaços de ~1 MB, cortados no fim de um parágrafo."""
    if len(texto) <= 8 << 20:
        return [texto]
    partes, ini = [], 0
    while ini < len(texto):
        fim = texto.find("\n\n", ini + tamanho)
        fim = len(texto) if fim < 0 else fim + 2
        partes.append(texto[ini:fim])
        ini = fim
    return partes


def grupos_para_tokenizar(files, max_chars=32 << 20, max_arquivos=16):
    """Junta arquivos em grupos de até 16 arquivos ou ~32 milhões de caracteres: (arquivos, textos, nº de pedaços)."""
    grupo, textos, partes, chars = [], [], [], 0
    for path in files:
        p = pedacos(path.read_text(encoding="utf-8"))
        grupo.append(path)
        textos += p
        partes.append(len(p))
        chars += sum(len(t) for t in p)
        if len(grupo) >= max_arquivos or chars >= max_chars:
            yield grupo, textos, partes
            grupo, textos, partes, chars = [], [], [], 0
    if grupo:
        yield grupo, textos, partes


def tokenizar_para_disco(files, pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    sig = assinatura(files)
    meta, treino, val = pasta / f"{sig}.json", pasta / f"{sig}_treino.bin", pasta / f"{sig}_val.bin"
    copia = Path(args.tokens_backup) if args.tokens_backup else None
    if not (meta.exists() and treino.exists() and val.exists()) and copia and (copia / meta.name).exists():
        print(f"Copiando os tokens já calculados de {copia}...", flush=True)
        for f in (treino, val, meta):  # o .json por último: só vale se os .bin chegaram inteiros
            shutil.copy(copia / f.name, f)
    if meta.exists() and treino.exists() and val.exists():
        print(f"Tokens já calculados em {pasta} ({sig}).")
    else:
        for antigo in pasta.iterdir():  # caches de outros textos/tokenizers só ocupam espaço
            if not antigo.name.startswith(sig):
                antigo.unlink()
        dtype = np.uint16 if tokenizer.get_vocab_size() <= 65535 else np.uint32
        n_treino = n_val = feitos = avisado = 0
        inicio = ultimo_aviso = time.time()
        with open(treino, "wb") as ft, open(val, "wb") as fv:
            for grupo, textos, partes in grupos_para_tokenizar(files):
                # encode_batch tokeniza em paralelo. Arquivos pequenos vão inteiros (os mesmos tokens de antes);
                # os grandes (Carolina, GigaVerbo) vão em pedaços de ~1 MB, para não gastar dezenas de GB de RAM.
                codigos = tokenizer.encode_batch(textos)
                k = 0
                for path, n_partes in zip(grupo, partes):
                    ids = np.concatenate([np.asarray(enc.ids, dtype=dtype) for enc in codigos[k:k + n_partes]]
                                         + [np.array([eot_id], dtype=dtype)])
                    k += n_partes
                    cut = int(len(ids) * 0.95)
                    repeat = args.modern_repeat if path.parent.name == "modern" else 1
                    for _ in range(max(1, repeat)):
                        ft.write(ids[:cut].tobytes())
                    fv.write(ids[cut:].tobytes())
                    n_treino += cut * max(1, repeat)
                    n_val += len(ids) - cut
                feitos += len(grupo)
                if feitos - avisado >= 160 or feitos == len(files) or time.time() - ultimo_aviso > 60:
                    avisado, ultimo_aviso = feitos, time.time()
                    print(f"  tokenizados {feitos}/{len(files)} arquivos ({n_treino:,} tokens, "
                          f"{time.time() - inicio:.0f}s)", flush=True)
        meta.write_text(json.dumps({"treino": n_treino, "val": n_val, "dtype": np.dtype(dtype).name}))
        if copia:
            copia.mkdir(parents=True, exist_ok=True)
            for antigo in copia.iterdir():
                if not antigo.name.startswith(sig):
                    antigo.unlink()
            print(f"Guardando uma cópia dos tokens em {copia}...", flush=True)
            for f in (treino, val, meta):
                shutil.copy(f, copia / f.name)
    info = json.loads(meta.read_text())
    return (np.memmap(treino, dtype=info["dtype"], mode="r"), np.memmap(val, dtype=info["dtype"], mode="r"))


block = cfg["block_size"]
train_data, val_data = tokenizar_para_disco(book_files, Path(args.tokens_dir))
if len(val_data) < block * 10 or len(train_data) < block * 100:
    raise SystemExit(f"Poucos dados ({len(train_data)} tokens). Adicione mais livros.")

# Parâmetros vs. tokens: regra prática ~20 tokens de treino por parâmetro.
model = build_model(cfg).to(device)
# torch.compile: o modelo compilado só faz as contas; os pesos salvos são os do model (mesmos tensores).
rodar_modelo = torch.compile(model) if args.compile and use_cuda else model
n_params = model.num_params()
tokens_por_passo = cfg["batch_size"] * cfg["accum"] * block
print(f"Tokens: {len(train_data):,} | Parâmetros: {n_params:,} | "
      f"tokens/parâmetro: {len(train_data) / n_params:.1f} (ideal ≈ 20) | "
      f"{tokens_por_passo:,} tokens por passo, {cfg['max_steps']:,} passos "
      f"(~{tokens_por_passo * cfg['max_steps'] / max(1, len(train_data)):.1f} passadas pelos dados)")


def mesma_arquitetura(config):
    return all(bool(config.get(k)) == bool(cfg.get(k)) if k == "rope" else config.get(k) == cfg.get(k)
               for k in ARQUITETURA)


def descrever(config):
    return (f"preset {config.get('preset', '?')}: {config['embed_size']} dim, {config['layers']} camadas, "
            f"contexto {config['block_size']}, vocabulário {config['vocab_size']}")


def get_batch(source):
    starts = np.random.randint(0, len(source) - block - 1, size=cfg["batch_size"])
    x = torch.from_numpy(np.stack([source[i:i + block] for i in starts]).astype(np.int64))
    y = torch.from_numpy(np.stack([source[i + 1:i + block + 1] for i in starts]).astype(np.int64))
    if use_cuda:
        return x.pin_memory().to(device, non_blocking=True), y.pin_memory().to(device, non_blocking=True)
    return x, y


@torch.no_grad()
def evaluate():
    model.eval()
    losses = []
    for _ in range(cfg["eval_iters"]):
        x, y = get_batch(val_data)
        with torch.autocast(device_type=device, dtype=amp_dtype, enabled=use_cuda):
            logits = rodar_modelo(x)
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
scaler = torch.amp.GradScaler("cuda", enabled=use_cuda and not bf16)


def lr_at(step):
    if step < cfg["warmup_steps"]:
        return cfg["learning_rate"] * (step + 1) / cfg["warmup_steps"]
    progress = (step - cfg["warmup_steps"]) / max(1, cfg["max_steps"] - cfg["warmup_steps"])
    return cfg["learning_rate"] * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0))))


# ---------- De onde começar ----------
start_step, best_val, evals_without_gain, retomado = 0, float("inf"), 0, False
if args.resume and last_path.exists():
    last = torch.load(last_path, map_location=device, weights_only=False)
    if not mesma_arquitetura(last["config"]):
        raise SystemExit(f"O treino interrompido no Drive é do {descrever(last['config'])}. Para trocar de "
                         f"preset ({args.preset}), use MODO = \"do_zero\".")
    if last["step"] < cfg["max_steps"]:
        model.load_state_dict(last["model"])
        optimizer.load_state_dict(last["optimizer"])
        scaler.load_state_dict(last["scaler"])
        start_step, best_val, evals_without_gain = last["step"], last["best_val"], last["evals_without_gain"]
        torch.set_rng_state(last["rng_torch"].cpu())
        np.random.set_state(last["rng_numpy"])
        random.setstate(last["rng_python"])
        if use_cuda and last.get("rng_cuda") is not None:
            torch.cuda.set_rng_state(last["rng_cuda"].cpu())
        retomado = True
        print(f"Retomando o treino interrompido no passo {start_step} (melhor val loss até aqui {best_val:.4f}).")
    del last
if not retomado and args.resume and best_path.exists():
    ckpt = torch.load(best_path, map_location=device, weights_only=False)
    if not mesma_arquitetura(ckpt["config"]):
        raise SystemExit(f"O pré-treino do Drive é do {descrever(ckpt['config'])}. Para trocar de preset "
                         f"({args.preset}), use MODO = \"do_zero\".")
    model.load_state_dict(ckpt["model"])
    print(f"Pesos carregados de {best_path} (val loss {ckpt['val_loss']:.4f}); agendamento novo.")
    del ckpt


def salvar_ultimo(step):
    """Estado completo (pesos, otimizador, passo, sorteios) para continuar se a sessão cair."""
    tmp = last_path.with_suffix(".tmp")
    torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(), "scaler": scaler.state_dict(),
                "config": cfg, "step": step, "best_val": best_val, "evals_without_gain": evals_without_gain,
                "rng_torch": torch.get_rng_state(), "rng_numpy": np.random.get_state(),
                "rng_python": random.getstate(), "rng_cuda": torch.cuda.get_rng_state() if use_cuda else None},
               tmp)
    os.replace(tmp, last_path)


# ---------- Treino ----------
start = time.time()
tokens_feitos, inicio_janela = 0, time.time()
model.train()

for step in range(start_step, cfg["max_steps"] + 1):
    for group in optimizer.param_groups:
        group["lr"] = lr_at(step)

    if step % cfg["eval_every"] == 0 and not (retomado and step == start_step):
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
        salvar_ultimo(step)

    optimizer.zero_grad(set_to_none=True)
    for _ in range(cfg["accum"]):  # acumulação: o lote efetivo é batch_size × accum
        x, y = get_batch(train_data)
        with torch.autocast(device_type=device, dtype=amp_dtype, enabled=use_cuda):
            logits = rodar_modelo(x)
        loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1)) / cfg["accum"]
        scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(optimizer)
    scaler.update()
    tokens_feitos += tokens_por_passo

    if step % 100 == 0:
        agora = time.time()
        print(f"step {step:>6} | train loss {loss.item() * cfg['accum']:.4f} | "
              f"{tokens_feitos / max(1e-9, agora - inicio_janela):,.0f} tokens/s", flush=True)
        tokens_feitos, inicio_janela = 0, agora

# Terminou (passos ou early stopping): o próximo "continuar" parte do melhor, com agendamento novo.
if last_path.exists():
    last_path.unlink()
print("=" * 40)
print(f"Pré-treino concluído. Melhor val loss: {best_val:.4f} -> {best_path}")
print("Referência: val loss > 4.5 = ainda não aprendeu gramática; < 3.5 = frases já fazem sentido.")
print("Teste a fluência com: python chat.py --base")
