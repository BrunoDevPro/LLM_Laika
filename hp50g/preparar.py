"""Dados da mini-LLM da HP 50g: diálogos curtos + texto simples, tokenizador BPE de 1024 e tokens em binário.

Domínio escolhido pelo usuário: diálogos curtos (perguntas e respostas no estilo da Laika). Um modelo de ~1M de
parâmetros só fica coerente num estilo restrito, então:
  dialogos  os exemplos escritos da Laika (data/qa: .txt e conversas.jsonl, sem os que têm "Contexto:", que não
            cabem na janela de 128 da calculadora) e o GigaVerbo-v2-SFT (data/sft), só as conversas curtas,
            no formato <|user|> pergunta <|assistant|> resposta <|end|>
  texto     frases curtas e simples (4 a 25 palavras) tiradas da Wikipédia, do GigaVerbo, do Carolina e dos textos
            de data/modern, em parágrafos de até 5 frases: ensinam a língua; o treino mistura as duas fontes
Validação: ~1% dos documentos de cada fonte (pelo hash do texto), que nunca entram no treino.

Saída (--saida): tokenizador.json, vocab.bin (bytes de cada token + as fusões do BPE, para a calculadora),
{fonte}_treino.bin e {fonte}_val.bin (uint16) e meta.json (tokens, documentos e caracteres por token).

    python hp50g/preparar.py --saida data/hp50g --texto-mb 2000
"""

import argparse
import json
import random
import re
import struct
import sys
import time
import zlib
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

ESPECIAIS = ["<|endoftext|>", "<|user|>", "<|assistant|>", "<|end|>"]
EOT, USER, ASSISTANT, END = ESPECIAIS
# Pedaços para o BPE: um espaço opcional + uma palavra, ou uma sequência de espaços/quebras. A calculadora
# separa os bytes do mesmo jeito (ver simulador.pedacos) e aplica as fusões dentro de cada pedaço.
PADRAO_PEDACOS = r" ?[^\s]+|\s+"
# Só caracteres comuns do português: o resto (outras escritas, emojis) gastaria tokens de bytes soltos.
_PERMITIDOS = re.compile(r"^[\w\s.,;:!?¿¡'\"()\-–—/%$°ºª+=*&@#…«»“”‘’]*$")
_SO_LATIN = re.compile(r"[^\x00-ɏ\s…«»“”‘’–—]")
_FRASES = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"“])")


def limpo(texto):
    return bool(_PERMITIDOS.match(texto)) and not _SO_LATIN.search(texto)


def val(doc, por_mil):
    return zlib.crc32(doc.encode("utf-8")) % 1000 < por_mil


# ---------- diálogos ----------

def ler_qa_txt(caminho):
    """Exemplos <|user|> ... <|assistant|> ... <|end|> de um .txt da Laika (linhas com # são comentários)."""
    linhas = [l for l in caminho.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#")]
    for bloco in "\n".join(linhas).split(END):
        if USER not in bloco or ASSISTANT not in bloco:
            continue
        p, _, r = bloco.split(USER, 1)[1].partition(ASSISTANT)
        yield [[p.strip(), r.strip()]]


def ler_conversas(caminho):
    for l in caminho.read_text(encoding="utf-8").splitlines():
        if l.strip():
            yield json.loads(l)


def ler_sft(pasta):
    junto = pasta / "sft_todas.jsonl"
    arquivos = [junto] if junto.exists() else sorted(pasta.glob("sft_*_*_*.jsonl"))
    for a in arquivos:
        with open(a, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    yield json.loads(l)


def dialogo(conversa, max_p, max_r, max_total, max_trocas):
    """O documento da conversa (só as primeiras trocas que couberem), ou None se nem a primeira couber."""
    partes, total = [], 0
    for p, r in conversa[:max_trocas]:
        p = " ".join(str(p).split())
        r = " ".join(str(r).replace("**", "").split())
        if (not p or not r or "Contexto:" in p or len(p) > max_p or len(r) > max_r
                or not limpo(p) or not limpo(r)):
            break
        trecho = f"{USER} {p} {ASSISTANT} {r} {END}"
        if total + len(trecho) > max_total:
            break
        partes.append(trecho)
        total += len(trecho)
    return " ".join(partes) if partes else None


def montar_dialogos(a, saida):
    qa, docs = Path(a.qa), []
    fontes = []
    for f in sorted(qa.glob("*.txt")):
        fontes.append(("laika", ler_qa_txt(f)))
    if (qa / "conversas.jsonl").exists():
        fontes.append(("laika", ler_conversas(qa / "conversas.jsonl")))
    if a.sft and Path(a.sft).exists():
        fontes.append(("sft", ler_sft(Path(a.sft))))
    contagem = {}
    tr, va = open(saida / "dialogos_treino.txt", "w", encoding="utf-8"), open(saida / "dialogos_val.txt", "w", encoding="utf-8")
    n_sft = 0
    for nome, it in fontes:
        for conv in it:
            if nome == "sft" and a.sft_max and n_sft >= a.sft_max:
                break
            d = dialogo(conv, a.max_pergunta, a.max_resposta, a.max_dialogo, a.max_trocas)
            if d is None:
                continue
            n_sft += nome == "sft"
            contagem[nome] = contagem.get(nome, 0) + 1
            if val(d, a.val_por_mil):
                va.write(d + "\n" + EOT + "\n")
            else:
                # Os exemplos escritos à mão são poucos e são o estilo que queremos: entram repetidos.
                for _ in range(a.repetir_laika if nome == "laika" else 1):
                    tr.write(d + "\n" + EOT + "\n")
    tr.close()
    va.close()
    print("Diálogos:", contagem, flush=True)
    return contagem


# ---------- texto simples ----------

def paragrafos(caminho):
    """Parágrafos de um arquivo da Wikipédia, do GigaVerbo/Carolina (documentos separados por <|endoftext|>) ou
    de data/modern (título na primeira linha)."""
    texto = caminho.read_text(encoding="utf-8", errors="ignore")
    for doc in texto.split(EOT):
        for bloco in re.split(r"\n\s*\n", doc):
            bloco = " ".join(bloco.split())
            if bloco and bloco[-1] in ".!?\"”":  # sem pontuação final é título
                yield bloco


def frases_simples(paragrafo, min_p, max_p):
    for f in _FRASES.split(paragrafo):
        n = len(f.split())
        if min_p <= n <= max_p and f[-1] in ".!?" and limpo(f) and not re.search(r"\d{5,}|https?:|www\.", f):
            yield f


def montar_texto(a, saida):
    pastas = [Path(p) for p in a.texto]
    arquivos = []
    for p in pastas:
        if p.exists():
            fs = sorted(p.glob("*.txt"))
            random.Random(len(fs)).shuffle(fs)  # várias partes de cada fonte, não só o começo
            arquivos.append(fs)
    # Alterna entre as fontes (um arquivo de cada por vez), para a mistura não depender da ordem das pastas.
    fila = []
    for i in range(max((len(f) for f in arquivos), default=0)):
        fila += [f[i] for f in arquivos if i < len(f)]
    limite = a.texto_mb * 1e6
    escritos, docs, inicio, aviso = 0, 0, time.time(), time.time()
    tr, va = open(saida / "texto_treino.txt", "w", encoding="utf-8"), open(saida / "texto_val.txt", "w", encoding="utf-8")
    for arq in fila:
        if escritos >= limite:
            break
        for par in paragrafos(arq):
            # As frases simples de cada parágrafo, em documentos de até frases_por_doc (sem misturar parágrafos).
            fs = list(frases_simples(par, a.min_palavras, a.max_palavras))
            for i in range(0, len(fs), a.frases_por_doc):
                doc = " ".join(fs[i:i + a.frases_por_doc])
                (va if val(doc, a.val_por_mil) else tr).write(doc + "\n" + EOT + "\n")
                escritos += len(doc) + 1
                docs += 1
        if time.time() - aviso > 60:
            aviso = time.time()
            print(f"  texto: {escritos / 1e6:,.0f} MB, {docs:,} documentos ({time.time() - inicio:.0f}s)", flush=True)
    tr.close()
    va.close()
    print(f"Texto simples: {docs:,} documentos, {escritos / 1e6:,.0f} MB", flush=True)


# ---------- tokenizador ----------

def documentos(caminho):
    buf = []
    with open(caminho, encoding="utf-8") as f:
        for l in f:
            if l.rstrip("\n") == EOT:
                if buf:
                    yield "\n".join(buf)
                buf = []
            else:
                buf.append(l.rstrip("\n"))
    if buf:
        yield "\n".join(buf)


def treinar_tokenizador(saida, vocab, amostra_mb):
    from tokenizers import Regex, Tokenizer, decoders, models, pre_tokenizers, trainers

    # Amostra igual das duas fontes (o vocabulário serve aos dois estilos).
    amostra = saida / "_amostra_tokenizador.txt"
    with open(amostra, "w", encoding="utf-8") as out:
        for fonte in ("dialogos", "texto"):
            n = 0
            for doc in documentos(saida / f"{fonte}_treino.txt"):
                limpo_ = re.sub(r"<\|[a-z]+\|>", " ", doc)
                out.write(limpo_ + "\n")
                n += len(limpo_)
                if n > amostra_mb * 5e5:
                    break
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Split(Regex(PADRAO_PEDACOS), behavior="isolated"),
        pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=False),
    ])
    tok.decoder = decoders.ByteLevel()
    treinador = trainers.BpeTrainer(vocab_size=vocab, special_tokens=ESPECIAIS,
                                    initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), show_progress=False)
    tok.train([str(amostra)], treinador)
    amostra.unlink()
    tok.save(str(saida / "tokenizador.json"))
    exportar_vocab(saida)
    return tok


def bytes_do_token(texto):
    """Os bytes de um token do BPE de bytes (o ByteLevel troca cada byte por um caractere visível)."""
    from tokenizers import pre_tokenizers  # noqa: F401
    tabela = _bytes_unicode()
    inv = {v: k for k, v in tabela.items()}
    return bytes(inv[ch] for ch in texto)


def _bytes_unicode():
    """A tabela byte -> caractere do GPT-2/ByteLevel."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, map(chr, cs)))


def ler_vocab_e_fusoes(caminho_tok):
    """(lista de bytes por id, lista de fusões (id_a, id_b, id_resultado) em ordem de prioridade)."""
    j = json.loads(Path(caminho_tok).read_text(encoding="utf-8"))
    vocab = j["model"]["vocab"]
    n = max(vocab.values()) + 1
    for t in j["added_tokens"]:
        n = max(n, t["id"] + 1)
    tokens = [b""] * n
    especiais = {t["id"]: t["content"] for t in j["added_tokens"]}
    for texto, i in vocab.items():
        tokens[i] = especiais[i].encode() if i in especiais else bytes_do_token(texto)
    for i, t in especiais.items():
        tokens[i] = t.encode()
    fusoes = []
    for f in j["model"]["merges"]:
        a, b = f.split(" ") if isinstance(f, str) else f
        fusoes.append((vocab[a], vocab[b], vocab[a + b]))
    return tokens, fusoes, sorted(especiais)


def exportar_vocab(saida):
    """vocab.bin para a calculadora: 'HPVB', nº de tokens, nº de fusões, nº de especiais; cada token como (tamanho
    uint8, bytes); cada fusão como 3 × uint16 (a, b, resultado), na ordem de prioridade; os ids especiais (uint16)."""
    tokens, fusoes, especiais = ler_vocab_e_fusoes(saida / "tokenizador.json")
    with open(saida / "vocab.bin", "wb") as f:
        f.write(b"HPVB" + struct.pack("<HHH", len(tokens), len(fusoes), len(especiais)))
        for t in tokens:
            f.write(struct.pack("<B", len(t)) + t)
        for a_, b_, r in fusoes:
            f.write(struct.pack("<HHH", a_, b_, r))
        for i in especiais:
            f.write(struct.pack("<H", i))


def tokenizar(saida, tok):
    eot = tok.token_to_id(EOT)
    meta = {"vocab": tok.get_vocab_size(), "especiais": {e: tok.token_to_id(e) for e in ESPECIAIS}, "fontes": {}}
    for fonte in ("dialogos", "texto"):
        info = {}
        for parte in ("treino", "val"):
            txt = saida / f"{fonte}_{parte}.txt"
            n_tok = n_chars = n_docs = 0
            with open(saida / f"{fonte}_{parte}.bin", "wb") as out:
                lote = []

                def gravar():
                    nonlocal n_tok
                    for enc in tok.encode_batch(lote):
                        ids = np.asarray(enc.ids + [eot], dtype=np.uint16)
                        out.write(ids.tobytes())
                        n_tok += len(ids)

                for doc in documentos(txt):
                    lote.append(doc)
                    n_docs += 1
                    n_chars += len(re.sub(r"<\|[a-z]+\|>", "", doc)) + 1
                    if len(lote) >= 20000:
                        gravar()
                        lote = []
                if lote:
                    gravar()
            info[parte] = {"tokens": n_tok, "docs": n_docs, "caracteres": n_chars}
            print(f"  {fonte} {parte}: {n_docs:,} documentos, {n_tok:,} tokens", flush=True)
        info["caracteres_por_token"] = info["val"]["caracteres"] / max(1, info["val"]["tokens"])
        meta["fontes"][fonte] = info
    (saida / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saida", default="data/hp50g")
    ap.add_argument("--qa", default=str(RAIZ / "data/qa"))
    ap.add_argument("--sft", default=str(RAIZ / "data/sft"), help="GigaVerbo-v2-SFT baixado pela Laika (vazio = sem)")
    ap.add_argument("--sft-max", type=int, default=0, help="máximo de conversas do SFT (0 = todas as que passarem)")
    ap.add_argument("--texto", nargs="*", default=[str(RAIZ / p) for p in
                                                   ("data/wiki", "data/gigaverbo", "data/carolina", "data/modern")])
    ap.add_argument("--texto-mb", type=float, default=2000, help="MB de texto simples (~3 caracteres por token)")
    ap.add_argument("--max-pergunta", type=int, default=200)
    ap.add_argument("--max-resposta", type=int, default=400)
    ap.add_argument("--max-dialogo", type=int, default=900, help="caracteres de um diálogo (~128 tokens a menos)")
    ap.add_argument("--max-trocas", type=int, default=3)
    ap.add_argument("--repetir-laika", type=int, default=3)
    ap.add_argument("--min-palavras", type=int, default=4)
    ap.add_argument("--max-palavras", type=int, default=25)
    ap.add_argument("--frases-por-doc", type=int, default=5)
    ap.add_argument("--val-por-mil", type=int, default=10)
    ap.add_argument("--vocab", type=int, default=1024)
    ap.add_argument("--amostra-mb", type=float, default=100, help="MB para treinar o tokenizador")
    ap.add_argument("--so-tokenizar", action="store_true", help="refaz só o tokenizador e os .bin")
    a = ap.parse_args(argv)
    random.seed(0)
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    if not a.so_tokenizar:
        montar_dialogos(a, saida)
        montar_texto(a, saida)
    tok = treinar_tokenizador(saida, a.vocab, a.amostra_mb)
    meta = tokenizar(saida, tok)
    for fonte, info in meta["fontes"].items():
        print(f"{fonte}: {info['treino']['tokens']:,} tokens de treino, {info['val']['tokens']:,} de validação, "
              f"{info['caracteres_por_token']:.2f} caracteres por token")


if __name__ == "__main__":
    main()
