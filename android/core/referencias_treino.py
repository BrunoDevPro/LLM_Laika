"""Respostas do PyTorch para conferir o treino na GPU do app (android/core/.../treino).

    python android/core/referencias_treino.py

Cria um TinyLLM pequeno (pesos aleatórios), calcula a perda, os gradientes e um passo do
AdamW (com corte da norma) como o train.py/finetune.py fazem, e grava tudo em
android/core/build/referencias/treino_*.f32. O teste RedeGpuTest roda o mesmo nos
shaders (Mesa, GPU por software) e compara.
"""

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from model import build_model  # noqa: E402

OUT = Path(__file__).resolve().parent / "build/referencias"


def ordem(layers):
    n = ["tok_emb.weight", "pos_emb.weight"]
    for i in range(layers):
        p = f"blocks.{i}."
        n += [p + s for s in ["ln1.weight", "ln1.bias", "attn.qkv.weight", "attn.proj.weight", "ln2.weight",
                              "ln2.bias", "ff.net.0.weight", "ff.net.0.bias", "ff.net.2.weight", "ff.net.2.bias"]]
    return n + ["ln_f.weight", "ln_f.bias"]


def plano(model, nomes, grad=False):
    sd = dict(model.named_parameters())
    return torch.cat([(sd[n].grad if grad else sd[n].detach()).reshape(-1) for n in nomes]).numpy().astype("<f4")


def caso(nome, cfg, B, T, lr, wd_matriz, wd_vetor, betas, clip, seed):
    torch.manual_seed(seed)
    model = build_model(dict(cfg, dropout=0.0))
    with torch.no_grad():  # LayerNorm e vieses diferentes de 1/0, para o teste pegar erros neles
        for n, p in model.named_parameters():
            if p.dim() == 1:
                p.add_(torch.randn_like(p) * 0.1)
    nomes = ordem(cfg["layers"])
    x = torch.randint(0, cfg["vocab_size"], (B, T))
    y = torch.randint(0, cfg["vocab_size"], (B, T))
    y[0, : T // 3] = -100  # como a pergunta no fine-tuning
    pesos0 = plano(model, nomes)
    model.train()
    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)
    loss.backward()
    grads = plano(model, nomes, grad=True)
    decay = [p for p in model.parameters() if p.dim() >= 2]
    no_decay = [p for p in model.parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": wd_matriz}, {"params": no_decay, "weight_decay": wd_vetor}],
                            lr=lr, betas=betas)
    norma = torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
    opt.step()
    pesos1 = plano(model, nomes)
    OUT.mkdir(parents=True, exist_ok=True)
    for sufixo, arr in [("pesos0", pesos0), ("grads", grads), ("pesos1", pesos1)]:
        arr.tofile(OUT / f"treino_{nome}_{sufixo}.f32")
    meta = dict(cfg=cfg, B=B, T=T, tokens=x.reshape(-1).tolist(), alvos=y.reshape(-1).clamp(min=-1).tolist(),
                perda=loss.item(), norma=norma.item(), lr=lr, wd_matriz=wd_matriz, wd_vetor=wd_vetor,
                b1=betas[0], b2=betas[1], clip=clip)
    (OUT / f"treino_{nome}.json").write_text(json.dumps(meta))
    print(f"{nome}: perda {loss.item():.5f}, norma {norma.item():.4f}, {len(pesos0)} parâmetros")


def tokenizer_ref(livro=None):
    """BPE treinado pela biblioteca tokenizers, para comparar com o TreinadorBpe do app."""
    from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
    sys.path.insert(0, str(ROOT / "android"))
    from exportar_modelo import export_tokenizer
    from data_utils import SPECIAL_TOKENS, UNK_TOKEN
    arquivos = sorted(str(p) for p in (ROOT / "data/modern").glob("*.txt"))
    if livro:
        arquivos.append(str(livro))
    arquivos += sorted(str(p) for p in (ROOT / "data/qa").glob("*.txt"))
    tok = Tokenizer(models.BPE(unk_token=UNK_TOKEN))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(vocab_size=3000, special_tokens=SPECIAL_TOKENS,
                                  initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), show_progress=False)
    tok.train(arquivos, trainer)
    OUT.mkdir(parents=True, exist_ok=True)
    tok.save(str(OUT / "bpe_ref.json"))
    export_tokenizer(OUT / "bpe_ref.json", OUT / "bpe_ref.txt")
    (OUT / "bpe_arquivos.txt").write_text("\n".join(arquivos), encoding="utf-8")


def main():
    tokenizer_ref(sys.argv[1] if len(sys.argv) > 1 else None)
    # Bordas dos blocos de 64 do matmul: dimensões que não são múltiplas de 64.
    caso("pequeno", dict(vocab_size=50, block_size=16, embed_size=32, heads=4, layers=2), B=3, T=16,
         lr=1e-3, wd_matriz=0.1, wd_vetor=0.0, betas=(0.9, 0.95), clip=1.0, seed=1)
    # Cabeças de 64 dimensões (como o colab_big) e T menor que o block.
    caso("cabeca64", dict(vocab_size=70, block_size=24, embed_size=128, heads=2, layers=1), B=2, T=20,
         lr=5e-5, wd_matriz=0.01, wd_vetor=0.01, betas=(0.9, 0.999), clip=0.05, seed=2)


if __name__ == "__main__":
    main()
