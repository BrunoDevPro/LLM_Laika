"""Gera as respostas de referência do Python para os testes do core em Java.

    python android/core/referencias.py --checkpoints checkpoints --livro data/books/gutenberg_24455.txt
    (opcional) --rope pasta/pretrain_best.pt   um checkpoint com RoPE (ex.: train.py --preset tiny_rope)

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

from chat import build_prompt, end_penalty, min_answer_tokens  # noqa: E402
from data_utils import (content_words, follows_up, question_name, rag_queries, wants_long, wants_rag,  # noqa: E402
                        without_trigger)
from memory import Memory  # noqa: E402
from model import build_model  # noqa: E402
from rag import RagIndex, _stem  # noqa: E402

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
    "O que Santos Dumont inventou?", "Santos Dumont inventou o quê?", "Quando nasceu Machado de Assis?",
    "Onde fica Roma?", "Compare Brasil e Portugal", "Quem foi Dom Pedro II?", "Você conhece o Rio de Janeiro?",
    "Me fale de \"Santos Dumont\".", "Roma", "O vulcão Vesúvio fica em Nápoles?",
    "E da Itália?", "Por quê?", "Quem foi ele?", "Continue.", "Explique melhor.", "E o Brasil?", "O que ela fez?",
    "Obrigado!", "E aí, tudo bem?", "Não entendi", "Como esta o tempo?", "Resuma isso.",
    "O que havia antes do Big Bang?", "O Sol é uma estrela?", "Explique passo a passo: quanto é 23 × 4?",
    "O que é a pedra? Explique melhor.", "Resposta longa: o que é a rocha?", "O que é um vulcão? Resposta longa.",
    "Resposta longa.", "Responda com detalhes.", "E o que ele fez?", "Quem foi Machado de Assis? Resposta longa.",
    "Quem foi Santos Dumont? Explica melhor, por favor.", "Fale sobre Roma. Responda com detalhes.",
    "Pesquise sobre a cadela Laika.", "Quem foi a cadela Laika?", "Você sabe quem foi a cadela Laika?",
    "Quem é você, Laika?", "Você conhece a Laika?", "Você sabe o que é um vulcão?", "Você pode me dizer o que é o Sol?",
    "O que é pedra?", "O que é madeira?", "O que é areia?", "Qual é a capital de Portugal?", "Os vulcões entram em erupção?",
    "O que os planetas têm?", "Quais animais vivem nos rios?", "O que é o ciclo da água?",
    "O planeta Marte tem água?", "Qual é o tamanho do rio Amazonas?", "O que foi o Sputnik 2?",
    "Quem foi Pedro II do Brasil?", "Para que serve o petróleo?", "Fale sobre o escritor Machado de Assis.",
    "Qual é a língua da França?", "Saturno tem anéis?", "Qual é a população do Brasil?",
    "Mas em que mês foi?", "Foi em que mês?", "E o mês?", "Quem era o líder?", "Mas quem fez isso?",
    "Quem governava na época?", "Mas quando?", "Em que mês nasce a primavera?", "Quando foi a queda de Constantinopla?",
    "O que foi a queda de Constantinopla e por que aconteceu?", "Faça uma frase com o meu nome.",
    "Faça uma frase com o nome dele.", "O que é um século?", "Qual foi o motivo?",
]

# Conversas anteriores para a "memória de IA" (histórico no prompt).
HISTORICO = [
    ("Qual é a capital da França?", "A capital da França é Paris."),
    ("E da Itália?", "A capital da Itália é Roma."),
    ("Meu nome é Ana.", "Prazer, Ana! Vou lembrar o seu nome."),
    ("O que é um vulcão?", "Um vulcão é uma abertura na crosta da Terra por onde sai lava, cinzas e gases. "
     "Ele pode ficar adormecido por muito tempo e depois entrar em erupção."),
    ("Oi", "Oi! Tudo bem? Em que posso ajudar?"),
    ("Conte uma história curta.", "Era uma vez uma cadela chamada Laika, que foi ao espaço em 1957. " * 4),
]

MEMORIA = [
    "Faça uma frase com o meu nome.", "meu nome é ana maria", "Faça uma frase com o meu nome.", "Qual é o meu nome?", "eu moro em Recife e gosto de futebol",
    "Onde eu moro?", "eu tenho 12 anos", "Quantos anos eu tenho?", "não gosto de chuva",
    "Do que eu não gosto?", "minha cor favorita é azul", "Qual é a minha cor favorita?",
    "meu animal favorito é o gato", "Qual é o meu animal favorito?",
    "Lembre que amanhã tenho prova de matemática.", "lembre-se de comprar pão",
    "O que você lembra de mim?", "Me chamo João e moro no Rio de Janeiro", "Quem sou eu?",
    "Você gosta de futebol?", "O que é um vulcão?", "Do que eu gosto?",
    "Esqueça tudo", "O que você sabe sobre mim?", "Qual é o meu nome?",
    "Meu nome é", "Eu moro em", "Lembre que", "eu não gosto de", "Eu tenho", "Lembre-se:", "Meu nome é Bia.",
    "Escreva um poema usando o meu nome.", "Faça uma frase com o seu nome.", "Quantas letras tem o meu nome?",
    "Meu nome é bonito?", "Use o teu nome numa frase.", "Qual é o seu nome?",
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


def referencias_rope(pt, out):
    """Modelo com RoPE: pesos no formato LAIKA002, o .pt (para o ConversorPt) e logits/geração gulosa."""
    import shutil
    sys.path.insert(0, str(ROOT / "android"))
    from exportar_modelo import export_weights
    pasta = out / "rope"
    pasta.mkdir(parents=True, exist_ok=True)
    export_weights(Path(pt), pasta / "rope.bin")
    shutil.copy(pt, pasta / "modelo.pt")
    model = modelo_fp16(pt)
    block, vocab = model.block_size, model.tok_emb.num_embeddings
    rng = random.Random(3)
    casos = []
    for n in (1, 7, 60, 200, 250):
        ids = [rng.randrange(6, vocab) for _ in range(n)]
        with torch.no_grad():
            logits = model(torch.tensor([ids]))[0, -1].float()
            seq = list(ids)
            for _ in range(20):  # gulosa sem cache; com 250 tokens passa da janela de 256
                seq.append(int(model(torch.tensor([seq[-block:]]))[0, -1].argmax()))
        casos.append({"ids": ids, "logits": logits.numpy().round(5).tolist(), "guloso": seq[n:]})
    with open(pasta / "rope.jsonl", "w", encoding="utf-8") as f:
        for c in casos:
            f.write(json.dumps(c) + "\n")
    print(f"rope.jsonl: {len(casos)} casos (bloco {block})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints", default="checkpoints")
    parser.add_argument("--livro", default=None, help="um livro .txt para testar o tokenizer")
    parser.add_argument("--rag-db", default=str(ROOT / "android/app/src/main/assets/laika_rag_mini.db"))
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "build/referencias"))
    parser.add_argument("--rope", default=None, help="checkpoint .pt de um modelo com RoPE (preset tiny_rope)")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ck = Path(args.checkpoints)
    if args.rope:
        referencias_rope(args.rope, out)
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
        contextos = {str(k): [[h["title"], h["text"]] for h in rag.contexts(p, k)] for k in (1, 2, 3, 6)}
        linhas.append({"pergunta": p, "palavras": content_words(p), "radicais": [_stem(w) for w in content_words(p)], "quer_rag": wants_rag(p), "top": top,
                       "melhor": best["title"] if best else None, "nome": question_name(p), "segue": follows_up(p),
                       "sem_gatilho": without_trigger(p), "longa": wants_long(p),
                       "consultas": rag_queries(p), "contextos": contextos})
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
        # Com histórico, janelas e tamanhos de resposta diferentes.
        rng = random.Random(2)
        for i, p in enumerate(PERGUNTAS):
            for bloco, max_novos in ((256, 80), (256, 120), (512, 80), (512, 120)):
                n = rng.randint(0, len(HISTORICO))
                hist = HISTORICO[:n] if i % 2 else HISTORICO[len(HISTORICO) - n:]
                prompt, fonte = build_prompt(p, tok, bloco, rag, mem if i % 3 == 0 else None, max_novos, hist)
                linhas.append({"pergunta": p, "memoria": i % 3 == 0, "bloco": bloco, "max_novos": max_novos,
                               "historico": [list(t) for t in hist], "prompt": prompt, "fonte": fonte})
        gravar("prompt.jsonl", linhas)

    gravar("penalidade.jsonl", [{"max_novos": m, "minimo": min_answer_tokens(m),
                                 "valores": [end_penalty(k, min_answer_tokens(m)) for k in range(70)]}
                                for m in (16, 40, 60, 61, 80, 100, 120)])


if __name__ == "__main__":
    main()
