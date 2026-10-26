"""Avaliação fixa da Laika: para comparar versões com números, e não só no olho.

  python avaliar.py                          # mede checkpoints/finetuned.pt
  python avaliar.py --comparar backup        # e o backup mais recente (checkpoints/backups/), lado a lado
  python avaliar.py --comparar outro.pt      # ou qualquer outro checkpoint de chat
  python avaliar.py --sem-rag                # tudo sem a busca nos textos

Mede três coisas:
  1) perplexidade num texto fixo que nunca entra no treino (data/avaliacao/textos.txt): quanto o modelo
     "se surpreende" com português comum (menor é melhor);
  2) ~100 perguntas fixas (data/avaliacao/perguntas.jsonl), por categoria (identidade, fatos sem e com
     RAG, leitura, seguimento, resposta longa, contas, sim ou não, datas, generalização, "não sei", resumo...).
     Cada uma tem as palavras esperadas na resposta; as respostas são geradas sem sorteio (sempre o token
     mais provável), então a mesma versão dá sempre o mesmo resultado. Nos resumos, a resposta também
     não pode ser longa demais (max_palavras) nem copiada do texto (max_copia: fração de sequências de
     4 palavras iguais às do texto);
  3) a busca do RAG (data/avaliacao/rag.jsonl): para cada pergunta, o artigo que deveria vir (ou nenhum).
     Conta acertos, perguntas sem contexto e contextos errados. Só roda com o índice (data/rag/laika_rag.db).

O resultado vai para checkpoints/avaliacao/avaliacao_<data>.json (com todas as respostas).
"""

import argparse
import json
import math
import time
from pathlib import Path

import torch

from chat import build_prompt, generate
from data_utils import normalize, rag_question, wants_long
from model import build_model

PASTA = Path("data/avaliacao")


def carregar(caminho, device):
    ckpt = torch.load(caminho, map_location=device)
    model = build_model(ckpt["config"], dropout=0.0).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model


def ler_jsonl(caminho):
    if not caminho.exists():
        return []
    return [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()]


@torch.no_grad()
def perplexidade(model, tokenizer, texto, device):
    """exp(loss média por token) em janelas do tamanho do contexto do modelo."""
    ids = tokenizer.encode(texto).ids
    janela = model.block_size
    total, n = 0.0, 0
    for i in range(0, max(1, len(ids) - 1), janela):
        pedaco = ids[i:i + janela + 1]
        if len(pedaco) < 2:
            break
        x = torch.tensor([pedaco[:-1]], device=device)
        y = torch.tensor([pedaco[1:]], device=device)
        logits = model(x)
        total += torch.nn.functional.cross_entropy(logits[0].float(), y[0], reduction="sum").item()
        n += len(pedaco) - 1
    return math.exp(total / max(1, n))


def contem(resposta, alternativas):
    """Alguma das alternativas aparece na resposta? (sem acentos e sem maiúsculas)."""
    alvo = " " + " ".join(normalize(resposta).replace("-", " ").split()) + " "
    if isinstance(alternativas, str):
        alternativas = [alternativas]
    return any(" " + " ".join(normalize(a).replace("-", " ").split()) in alvo for a in alternativas)


def copia(resposta, texto, n=4):
    """Fração das sequências de n palavras da resposta que aparecem iguais no texto (0 = escreveu com as próprias
    palavras, 1 = copiou tudo). Um resumo que só repete frases do texto passa nas palavras esperadas, mas não resume."""
    def grupos(s):
        w = normalize(s).split()
        return [tuple(w[i:i + n]) for i in range(len(w) - n + 1)]
    r, t = grupos(resposta), set(grupos(texto))
    return sum(g in t for g in r) / len(r) if r else 0.0


def nota(item, resposta):
    """(acertou?, fração das palavras esperadas encontradas)."""
    grupos = item.get("esperado", [])
    achados = sum(contem(resposta, g) for g in grupos)
    parcial = achados / len(grupos) if grupos else 1.0
    ok = achados == len(grupos)
    if any(contem(resposta, p) for p in item.get("proibido", [])):
        ok, parcial = False, 0.0
    if item.get("min_palavras") and len(resposta.split()) < item["min_palavras"]:
        ok = False
    if item.get("max_palavras") and len(resposta.split()) > item["max_palavras"]:
        ok = False
    # Resumos: reprovado se a resposta for quase toda copiada da pergunta (o texto a resumir está nela).
    if "max_copia" in item and copia(resposta, item["pergunta"]) > item["max_copia"]:
        ok = False
    return ok, parcial


def responder(model, tokenizer, item, rag, device, max_padrao):
    pergunta = item["pergunta"]
    max_novos = item.get("max_tokens") or (max(max_padrao, model.block_size // 4) if wants_long(pergunta)
                                            else max_padrao)
    if item.get("contexto"):
        pergunta, usar_rag = rag_question(pergunta, item["contexto"]), None
    else:
        usar_rag = rag if item.get("rag", True) else None
    historico = [tuple(t) for t in item.get("historico", [])]
    prompt, fonte = build_prompt(pergunta, tokenizer, model.block_size, usar_rag, None, max_novos, historico)
    # Sem sorteio: top_k=1 escolhe sempre o token mais provável (mesmo resultado em toda execução).
    resposta = generate(model, tokenizer, prompt, device, max_novos, temperature=1.0, top_k=1)
    return resposta, fonte


def avaliar_perguntas(model, tokenizer, itens, rag, device, max_padrao):
    resultados = []
    for item in itens:
        resposta, fonte = responder(model, tokenizer, item, rag, device, max_padrao)
        ok, parcial = nota(item, resposta)
        r = {"categoria": item["categoria"], "pergunta": item["pergunta"], "resposta": resposta,
             "fonte": fonte, "acertou": ok, "parcial": round(parcial, 3)}
        if "max_copia" in item:
            r["copia"] = round(copia(resposta, item["pergunta"]), 3)
        resultados.append(r)
    return resultados


def _sem_artigo(titulo):
    palavras = normalize(titulo).split()
    return " ".join(palavras[1:] if len(palavras) > 1 and palavras[0] in ("o", "a", "os", "as") else palavras)


def avaliar_rag(rag, itens):
    """acerto: o 1º trecho é do artigo esperado; nenhum: não veio contexto; errado: veio de outro artigo.
    "titulo" é um título ou uma lista de títulos aceitos; null = não deve vir contexto (conversa, pergunta
    pessoal, conta)."""
    from data_utils import wants_rag

    linhas, conta = [], {"acerto": 0, "nenhum": 0, "errado": 0}
    for item in itens:
        pergunta, esperado = item["pergunta"], item.get("titulo")
        hits = rag.contexts(pergunta, 1) if wants_rag(pergunta) else []
        veio = hits[0]["title"] if hits else None
        if esperado is None:
            situacao = "acerto" if veio is None else "errado"
        elif veio is None:
            situacao = "nenhum"
        else:
            aceitos = [esperado] if isinstance(esperado, str) else esperado
            # "O coração" (texto de data/modern) vale como "Coração" (artigo da Wikipédia).
            situacao = "acerto" if _sem_artigo(veio) in {_sem_artigo(t) for t in aceitos} else "errado"
        conta[situacao] += 1
        linhas.append({"pergunta": pergunta, "esperado": esperado, "veio": veio, "situacao": situacao})
    return conta, linhas


def resumo_por_categoria(resultados):
    cats = {}
    for r in resultados:
        c = cats.setdefault(r["categoria"], [0, 0, 0.0])
        c[0] += r["acertou"]
        c[1] += 1
        c[2] += r["parcial"]
    return {k: {"acertos": a, "total": t, "parcial": round(p / t, 3)} for k, (a, t, p) in cats.items()}


def ultimo_backup(pasta):
    backups = sorted(Path(pasta, "backups").glob("finetuned_*.pt"))
    return backups[-1] if backups else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="checkpoints", help="pasta com o tokenizer.json e os checkpoints")
    parser.add_argument("--modelo", default=None, help="checkpoint a avaliar (padrão: <out>/finetuned.pt)")
    parser.add_argument("--comparar", default=None, help='outro checkpoint, ou "backup" para o mais recente')
    parser.add_argument("--rag-db", default="data/rag/laika_rag.db")
    parser.add_argument("--sem-rag", action="store_true")
    parser.add_argument("--perguntas", default=str(PASTA / "perguntas.jsonl"))
    parser.add_argument("--max-tokens", type=int, default=80, help="tamanho máximo das respostas curtas")
    parser.add_argument("--saida", default=None, help="pasta do resultado (padrão: <out>/avaliacao)")
    args = parser.parse_args()

    from tokenizers import Tokenizer
    from rag import open_index

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = Path(args.out)
    tokenizer = Tokenizer.from_file(str(out / "tokenizer.json"))
    modelos = [("atual", Path(args.modelo) if args.modelo else out / "finetuned.pt")]
    if args.comparar:
        outro = ultimo_backup(out) if args.comparar == "backup" else Path(args.comparar)
        if outro is None or not outro.exists():
            print(f"Nada para comparar ({args.comparar}): avaliando só o modelo atual.")
        else:
            modelos.append(("anterior", outro))
    rag = None if args.sem_rag else open_index(args.rag_db)
    itens = ler_jsonl(Path(args.perguntas))
    textos = (PASTA / "textos.txt").read_text(encoding="utf-8") if (PASTA / "textos.txt").exists() else ""

    relatorio = {"data": time.strftime("%Y-%m-%d %H:%M"), "rag": rag is not None, "modelos": {}}
    itens_rag = ler_jsonl(PASTA / "rag.jsonl")
    if rag is not None and itens_rag:
        conta, linhas = avaliar_rag(rag, itens_rag)
        relatorio["busca"] = {"resumo": conta, "itens": linhas}
        total = sum(conta.values()) or 1
        print(f"\nBusca do RAG ({total} perguntas): {conta['acerto']} certas ({100 * conta['acerto'] / total:.0f}%), "
              f"{conta['nenhum']} sem contexto, {conta['errado']} com o artigo errado")
        for l in linhas:
            if l["situacao"] != "acerto":
                print(f"   [{l['situacao']}] {l['pergunta']}  -> veio {l['veio']!r}, esperado {l['esperado']!r}")

    for nome, caminho in modelos:
        if not caminho.exists():
            raise SystemExit(f"{caminho} não existe. Rode o fine-tuning antes.")
        print(f"\nAvaliando {nome}: {caminho}")
        model = carregar(caminho, device)
        ppl = perplexidade(model, tokenizer, textos, device) if textos else float("nan")
        resultados = avaliar_perguntas(model, tokenizer, itens, rag, device, args.max_tokens)
        relatorio["modelos"][nome] = {"arquivo": str(caminho), "perplexidade": round(ppl, 3),
                                      "categorias": resumo_por_categoria(resultados), "respostas": resultados}
        del model

    nomes = list(relatorio["modelos"])
    cats = sorted({c for m in relatorio["modelos"].values() for c in m["categorias"]})
    print("\n" + "categoria".ljust(22) + "".join(n.rjust(16) for n in nomes))
    for c in cats:
        linha = c.ljust(22)
        for n in nomes:
            r = relatorio["modelos"][n]["categorias"].get(c)
            linha += (f"{r['acertos']}/{r['total']} ({r['parcial']:.2f})" if r else "-").rjust(16)
        print(linha)
    linha_total, linha_ppl = "TOTAL".ljust(22), "perplexidade".ljust(22)
    for n in nomes:
        m = relatorio["modelos"][n]
        a = sum(r["acertou"] for r in m["respostas"])
        linha_total += f"{a}/{len(m['respostas'])}".rjust(16)
        linha_ppl += f"{m['perplexidade']:.2f}".rjust(16)
    print(linha_total)
    print(linha_ppl)
    # Quanto dos resumos é cópia do texto (menor é melhor; acima de ~0,5 o modelo está copiando, não resumindo).
    linha_copia, tem = "cópia nos resumos".ljust(22), False
    for n in nomes:
        c = [r["copia"] for r in relatorio["modelos"][n]["respostas"] if "copia" in r]
        tem |= bool(c)
        linha_copia += (f"{sum(c) / len(c):.2f}" if c else "-").rjust(16)
    if tem:
        print(linha_copia)
    if len(nomes) == 2:
        a, b = (relatorio["modelos"][n]["respostas"] for n in nomes)
        mudou = [(x, y) for x, y in zip(a, b) if x["acertou"] != y["acertou"]]
        if mudou:
            print(f"\nMudaram ({len(mudou)}):")
            for x, y in mudou:
                print(f"   {'+' if x['acertou'] else '-'} [{x['categoria']}] {x['pergunta']}\n"
                      f"       atual:    {x['resposta'][:150]}\n       anterior: {y['resposta'][:150]}")

    saida = Path(args.saida) if args.saida else out / "avaliacao"
    saida.mkdir(parents=True, exist_ok=True)
    arquivo = saida / f"avaliacao_{time.strftime('%Y-%m-%d_%H%M')}.json"
    arquivo.write_text(json.dumps(relatorio, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nResultado completo (com todas as respostas): {arquivo}")


if __name__ == "__main__":
    main()
