"""Gera as respostas de referência do Python para os testes do core em Java.

    python android/core/referencias.py --checkpoints checkpoints --livro data/books/gutenberg_24455.txt

Usa o código original (model.py, tokenizers, rag.py, memory.py, chat.build_prompt) e grava
arquivos .jsonl em android/core/build/referencias/. Depois:  cd android && gradle :core:test
Os testes conferem se o Java dá o mesmo resultado (tokens, logits, busca, memória, prompt).
"""

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tokenizers import Tokenizer  # noqa: E402

from chat import build_prompt  # noqa: E402
from data_utils import content_words, wants_rag  # noqa: E402
from memory import Memory  # noqa: E402
from model import build_model  # noqa: E402
from rag import RagIndex  # noqa: E402

PERGUNTAS = [
    "Qual é o seu nome?", "Oi", "O que é um vulcão?", "Quem foi Santos Dumont?", "Qual é a capital da França?",
    "Complete a frase: Quem espera", "Escreva uma frase com a palavra noite.", "O que são os dinossauros?",
    "Como funciona um computador?", "O que é o ciclo da água?", "Quem foi a Laika?", "O que é reciclagem?",
    "Fale sobre a floresta amazônica", "Quais são as estações do ano?", "O que é archeologia christã?",
    "O que é uma basílica?", "Quem foi Pelé?", "O que é o Sistema Solar?", "Me conte sobre o futebol",
    "Quanto é 2 + 2?", "Você gosta de música?", "O que é a fotossíntese?", "Onde fica o Brasil?",
    "Como estudar melhor para a prova?", "O que tem no corpo humano?", "Qual a origem das catacumbas?",
    "Igrejas romanas antigas", "O que é um sarcófago?", "Corrija: eu fui na escola ontem",
    "Quem descobriu o Brasil em 1500?", "Dê um exemplo de verbo", "O que é a Lua?",
    "Faça um texto sobre planárias.", "O que você sabe sobre vulcões?", "Escreva um parágrafo a respeito da Lua.",
    "Fale sobre você", "E o capitalismo?", "Me conte sobre a cidade de Roma",
]

MEMORIA = [
    "meu nome é ana maria", "Qual é o meu nome?", "eu moro em Recife e gosto de futebol",
    "Onde eu moro?", "eu tenho 12 anos", "Quantos anos eu tenho?", "não gosto de chuva",
    "Do que eu não gosto?", "minha cor favorita é azul", "Qual é a minha cor favorita?",
    "meu animal favorito é o gato", "Qual é o meu animal favorito?",
    "Lembre que amanhã tenho prova de matemática.", "lembre-se de comprar pão",
    "O que você lembra de mim?", "Me chamo João e moro no Rio de Janeiro", "Quem sou eu?",
    "Você gosta de futebol?", "O que é um vulcão?", "Do que eu gosto?",
    "Esqueça tudo", "O que você sabe sobre mim?", "Qual é o meu nome?",
    "Meu nome é", "Eu moro em", "Lembre que", "eu não gosto de", "Eu tenho", "Lembre-se:", "Meu nome é Bia.",
]


def textos_tokenizer(livro):
    textos = [
        "<|user|> Olá, tudo bem?  Quem foi Santos Dumont?\nContexto: x <|assistant|>",
        "", " ", "  dois espaços", "fim com espaço ", "\n\nparágrafos\n\n\nmuitos", "ação, coração, pães e leões!",
        "Números: 1234567 3,14 1.000.000 2026", "emoji 😀🐶 e 中文 e кириллица", "tab\taqui", "it's I'll we've",
        "<|user|><|assistant|><|end|><|endoftext|>[PAD][UNK]", "<|user", "a <|end|>b", "“aspas” — travessão…",
        "ÇÃO MAIÚSCULAS Ñ ü", " espaço duro ", "x" * 300,
    ]
    for p in PERGUNTAS:
        textos.append(f"<|user|> {p} <|assistant|>")
    if livro:
        linhas = [l for l in Path(livro).read_text(encoding="utf-8").split("\n\n") if l.strip()]
        rng = random.Random(0)
        textos += rng.sample(linhas, min(300, len(linhas)))
    for f in sorted((ROOT / "data/qa").glob("*.txt")):
        blocos = f.read_text(encoding="utf-8").split("\n\n")
        textos += random.Random(1).sample(blocos, min(100, len(blocos)))
    return textos


def modelo_fp16(path):
    """Mesmo modelo, com os pesos arredondados para float16 como no app."""
    ckpt = torch.load(path, map_location="cpu")
    model = build_model(ckpt["config"], dropout=0.0)
    model.load_state_dict({k: v.half().float() for k, v in ckpt["model"].items()})
    model.eval()
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints", default="checkpoints")
    parser.add_argument("--livro", default=None, help="um livro .txt para testar o tokenizer")
    parser.add_argument("--rag-db", default=str(ROOT / "android/app/src/main/assets/laika_rag_mini.db"))
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "build/referencias"))
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ck = Path(args.checkpoints)
    tok = Tokenizer.from_file(str(ck / "tokenizer.json"))

    def gravar(nome, linhas):
        with open(out / nome, "w", encoding="utf-8") as f:
            for l in linhas:
                f.write(json.dumps(l, ensure_ascii=False) + "\n")
        print(f"{nome}: {len(linhas)} casos")

    textos = textos_tokenizer(args.livro)
    gravar("tokenizer.jsonl", [{"texto": t, "ids": tok.encode(t).ids, "decod": tok.decode(tok.encode(t).ids)}
                               for t in textos])

    torch.manual_seed(0)
    casos = []
    for nome in ["finetuned", "pretrain_best"]:
        model = modelo_fp16(ck / f"{nome}.pt")
        for p in PERGUNTAS[:8] + ["Era uma vez um menino que morava"]:
            prompt = f"<|user|> {p} <|assistant|>" if nome == "finetuned" else p
            ids = tok.encode(prompt).ids
            with torch.no_grad():
                logits = model(torch.tensor([ids]))[0, -1].float()
                # Sequência gulosa de 20 tokens (recalculando tudo, sem cache).
                seq = list(ids)
                for _ in range(20):
                    nxt = int(model(torch.tensor([seq[-256:]]))[0, -1].argmax())
                    seq.append(nxt)
            casos.append({"modelo": nome, "ids": ids, "logits": logits.numpy().round(5).tolist(),
                          "guloso": seq[len(ids):]})
        # Um prompt longo (240 tokens) que passa da janela de 256 durante a geração gulosa.
        longo = tok.encode(" ".join(textos[40:80]))
        ids = longo.ids[:240]
        with torch.no_grad():
            seq = list(ids)
            for _ in range(30):
                seq.append(int(model(torch.tensor([seq[-256:]]))[0, -1].argmax()))
        casos.append({"modelo": nome, "ids": ids, "logits": None, "guloso": seq[len(ids):]})
    gravar("modelo.jsonl", casos)

    rag = RagIndex(args.rag_db)
    linhas = []
    for p in PERGUNTAS:
        top = [[r["title"], round(r["score"], 6), r["coverage"]] for r in rag.search(p)[:8]]
        best = rag.best(p)
        linhas.append({"pergunta": p, "palavras": content_words(p), "quer_rag": wants_rag(p), "top": top,
                       "melhor": best["title"] if best else None})
    gravar("rag.jsonl", linhas)

    with tempfile.TemporaryDirectory() as tmp:
        mem = Memory(Path(tmp) / "memoria.json")
        linhas = []
        for m in MEMORIA:
            resp = mem.handle(m)
            linhas.append({"msg": m, "resposta": resp, "contexto": mem.context_for(m),
                           "resumo": mem.summary()})
        gravar("memoria.jsonl", linhas)

        mem = Memory(Path(tmp) / "m2.json")
        mem.handle("lembre que o vulcão da feira de ciências é de argila")
        linhas = []
        for p in PERGUNTAS:
            for usar_mem in (False, True):
                prompt, fonte = build_prompt(p, tok, 256, rag, mem if usar_mem else None, 80)
                linhas.append({"pergunta": p, "memoria": usar_mem, "prompt": prompt, "fonte": fonte})
        linhas.append({"pergunta": "vulcão de argila", "memoria": True,
                       "prompt": build_prompt("vulcão de argila", tok, 256, rag, mem, 80)[0],
                       "fonte": build_prompt("vulcão de argila", tok, 256, rag, mem, 80)[1]})
        gravar("prompt.jsonl", linhas)


if __name__ == "__main__":
    main()
