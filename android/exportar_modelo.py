"""Converte os checkpoints da Laika para os arquivos que o app Android lê.

    python android/exportar_modelo.py --checkpoints checkpoints --livros data/books

Gera em android/app/src/main/assets/:
  laika_chat.bin       pesos do finetuned.pt (float16, ~14 MB)
  laika_base.bin       pesos do pretrain_best.pt (modo "completar texto")
  tokenizer.txt        vocabulário e merges do tokenizer.json, num formato simples
  laika_rag_mini.db    índice RAG pequeno (data/modern + os livros passados em --livros)

O app não usa PyTorch: o transformer é refeito em Java (android/core). Por isso os pesos
vão num formato próprio, na ordem que o Java espera (ver ModelWeights.java).
Os pesos ficam em float16 para o APK ficar menor; o cálculo no celular é em float32.
"""

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MAGIC = b"LAIKA001"


def tensor_order(layers):
    names = ["tok_emb.weight", "pos_emb.weight"]
    for i in range(layers):
        p = f"blocks.{i}."
        names += [p + "ln1.weight", p + "ln1.bias", p + "attn.qkv.weight", p + "attn.proj.weight",
                  p + "ln2.weight", p + "ln2.bias", p + "ff.net.0.weight", p + "ff.net.0.bias",
                  p + "ff.net.2.weight", p + "ff.net.2.bias"]
    return names + ["ln_f.weight", "ln_f.bias"]  # head.weight = tok_emb.weight (compartilhado)


def export_weights(ckpt_path, out_path):
    ckpt = torch.load(ckpt_path, map_location="cpu")
    cfg, state = ckpt["config"], ckpt["model"]
    if not torch.equal(state["head.weight"], state["tok_emb.weight"]):
        raise SystemExit(f"{ckpt_path}: head.weight diferente de tok_emb.weight (o app espera pesos compartilhados)")
    with open(out_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<5i", cfg["vocab_size"], cfg["block_size"], cfg["embed_size"],
                            cfg["heads"], cfg["layers"]))
        for name in tensor_order(cfg["layers"]):
            f.write(state[name].float().numpy().astype("<f2").tobytes())
    print(f"{out_path.name}: {out_path.stat().st_size / 1e6:.1f} MB "
          f"(val loss {ckpt.get('val_loss', float('nan')):.3f})")


def export_tokenizer(json_path, out_path):
    tok = json.loads(Path(json_path).read_text(encoding="utf-8"))
    model = tok["model"]
    if model["type"] != "BPE" or tok["pre_tokenizer"]["type"] != "ByteLevel":
        raise SystemExit("O app só entende o tokenizer BPE byte-level do train.py.")
    vocab = sorted(model["vocab"].items(), key=lambda kv: kv[1])
    if [i for _, i in vocab] != list(range(len(vocab))):
        raise SystemExit("Os ids do vocabulário não são contínuos.")
    special = [t["content"] for t in tok["added_tokens"] if t.get("special")]
    merges = [m if isinstance(m, str) else " ".join(m) for m in model["merges"]]
    for token, _ in vocab:
        if any(c.isspace() for c in token):
            raise SystemExit(f"Token com espaço não cabe no formato simples: {token!r}")
    lines = [f"vocab {len(vocab)}", *[t for t, _ in vocab], f"special {len(special)}", *special,
             f"merges {len(merges)}", *merges]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out_path.name}: {len(vocab)} tokens, {len(merges)} merges")


def export_mini_rag(out_path, book_dir):
    import rag

    sources = [(str(ROOT / "data/modern"), "texto")]
    if book_dir and Path(book_dir).is_dir() and list(Path(book_dir).glob("*.txt")):
        sources.append((str(book_dir), "livro"))
    rag.SOURCES = sources
    if out_path.exists():
        out_path.unlink()
    rag.build(str(out_path), force=True)
    out_path.with_suffix(".json").unlink(missing_ok=True)  # o app não usa o .json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints", default="checkpoints",
                        help="pasta com finetuned.pt, pretrain_best.pt e tokenizer.json")
    parser.add_argument("--livros", default=None,
                        help="pasta com livros .txt (e titulos.tsv) para o índice pequeno do app")
    parser.add_argument("--out", default=str(ROOT / "android/app/src/main/assets"))
    args = parser.parse_args()

    ck, out = Path(args.checkpoints), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    export_weights(ck / "finetuned.pt", out / "laika_chat.bin")
    if (ck / "pretrain_best.pt").exists():
        export_weights(ck / "pretrain_best.pt", out / "laika_base.bin")
    else:
        print("pretrain_best.pt não encontrado: o modo 'completar texto' fica desligado no app.")
    export_tokenizer(ck / "tokenizer.json", out / "tokenizer.txt")
    export_mini_rag(out / "laika_rag_mini.db", args.livros)


if __name__ == "__main__":
    main()
