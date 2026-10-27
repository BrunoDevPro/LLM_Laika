"""RAG: busca trechos dos livros e artigos para dar contexto ao modelo.

O modelo é pequeno e não consegue guardar tudo o que leu. Com o RAG, antes de
responder, o chat procura nos textos (Wikipédia, data/modern e livros do Gutenberg)
o trecho mais parecido com a pergunta e o coloca no prompt:

    <|user|> Contexto: <trecho encontrado>
    Pergunta: <pergunta> <|assistant|>

O fine-tuning ensina o modelo a usar esse formato (data/qa/leitura.txt e exemplos
com contexto gerados automaticamente).

A busca usa o SQLite FTS5 (BM25), que já vem com o Python: não precisa de GPU nem de
bibliotecas extras. Montar o índice:  python rag.py build
Testar uma busca:                   python rag.py search "O que é um vulcão?"
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

from data_utils import _SENTENCE_SPLIT, content_words, normalize, question_name, rag_queries, word_tokens

DEFAULT_DB = "data/rag/laika_rag.db"
# Mude quando a busca mudar: o cache de contextos do finetune.py (contextos_cache.json) é refeito.
RAG_VERSAO = "1.12"
SOURCES = [("data/wiki", "wiki"), ("data/modern", "texto"), ("data/books", "livro")]
PASSAGE_WORDS = 80
KIND_BONUS = {"texto": 0.2, "wiki": 0.15, "livro": 0.0}


# ---------- Montagem do índice ----------

def chunk_sentences(text, size=PASSAGE_WORDS):
    """Junta frases até ~size palavras, sem cortar frases no meio."""
    chunk, count = [], 0
    for sentence in _SENTENCE_SPLIT.split(text):
        n = len(sentence.split())
        if chunk and count + n > size:
            yield " ".join(chunk)
            chunk, count = [], 0
        chunk.append(sentence)
        count += n
    if chunk:
        yield " ".join(chunk)


def wiki_passages(text):
    """Arquivos da Wikipédia: 'Título' numa linha curta sem ponto final, depois os parágrafos."""
    title, pos = "", 0
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block[-1] not in ".!?…" and len(block) < 120:
            title, pos = block, 0
            continue
        for chunk in chunk_sentences(block):
            if len(chunk.split()) >= 8:
                yield title, chunk, pos
                pos += 1


def modern_passages(text):
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    title = blocks[0] if blocks else ""
    pos = 0
    for block in blocks[1:]:
        for chunk in chunk_sentences(block):
            yield title, chunk, pos
            pos += 1


def book_passages(text, title):
    for block in text.split("\n\n"):
        block = block.strip()
        if len(block.split()) < 15:
            continue
        for chunk in chunk_sentences(block):
            if len(chunk.split()) >= 15:
                yield title, chunk, 99


def book_titles(folder):
    titles = {}
    path = Path(folder) / "titulos.tsv"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                book_id, title = line.split("\t", 1)
                titles[book_id] = title
    return titles


def iter_passages():
    for folder, kind in SOURCES:
        titles = book_titles(folder) if kind == "livro" else {}
        for path in sorted(Path(folder).glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            if kind == "wiki":
                passages = wiki_passages(text)
            elif kind == "texto":
                passages = modern_passages(text)
            else:
                book_id = path.stem.replace("gutenberg_", "")
                passages = book_passages(text, titles.get(book_id, f"Livro {book_id} do Project Gutenberg"))
            for title, passage, pos in passages:
                yield title, passage, kind, pos


def data_signature():
    sig = {}
    for folder, _ in SOURCES:
        files = list(Path(folder).glob("*.txt"))
        sig[folder] = [len(files), sum(f.stat().st_size for f in files)]
    return sig


def build(db_path=DEFAULT_DB, force=False):
    db_path = Path(db_path)
    meta_path = db_path.with_suffix(".json")
    signature = data_signature()
    if not force and db_path.exists() and meta_path.exists():
        if json.loads(meta_path.read_text()).get("signature") == signature:
            print(f"Índice RAG já está atualizado: {db_path}")
            return
    if not any(n for n, _ in signature.values()):
        print("Nenhum texto encontrado para indexar. Rode prepare_data.py antes.")
        return

    # Monta no disco local (o Google Drive é lento para o SQLite) e copia no final.
    tmp = Path(tempfile.gettempdir()) / "laika_rag_build.db"
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("CREATE VIRTUAL TABLE passages USING fts5("
                "title, text, kind UNINDEXED, pos UNINDEXED, tokenize='unicode61 remove_diacritics 2')")

    counts, batch = {}, []
    for title, text, kind, pos in iter_passages():
        batch.append((title, text, kind, pos))
        counts[kind] = counts.get(kind, 0) + 1
        if len(batch) >= 5000:
            con.executemany("INSERT INTO passages VALUES (?, ?, ?, ?)", batch)
            batch = []
            total = sum(counts.values())
            if total % 50000 == 0:
                print(f"  {total} trechos...", flush=True)
    if batch:
        con.executemany("INSERT INTO passages VALUES (?, ?, ?, ?)", batch)
    con.execute("INSERT INTO passages(passages) VALUES('optimize')")
    con.commit()
    con.close()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(tmp, db_path)
    tmp.unlink()
    meta_path.write_text(json.dumps({"signature": signature, "counts": counts}))
    size = db_path.stat().st_size / 1e6
    print(f"Índice RAG pronto: {sum(counts.values())} trechos {counts} ({size:.0f} MB) -> {db_path}")


# ---------- Busca ----------

# Plural -> singular (já sem acentos): "vulcoes" -> "vulcao", "capitais" -> "capital", "flores" -> "flor".
_PLURAIS = (("oes", "ao"), ("aes", "ao"), ("ais", "al"), ("eis", "el"), ("ns", "m"), ("res", "r"), ("zes", "z"),
            ("ses", "s"), ("s", ""))
_VERBOS = ("ando", "endo", "indo", "aram", "eram", "iram", "ava", "ou", "ar", "er", "ir", "or")


def _stem(word):
    """Radical leve: tira o plural e algumas terminações de verbo (palavras com 7+ letras).

    "cadelas" = "cadela", "inventou" = "inventor" = "invent". Antes eram as 5 primeiras letras, o que
    juntava "capital" com "capítulo", "Portugal" com "português" e "planeta" com "planejamento". A vogal
    final fica ("pedra" não é "Pedro").
    """
    if not word.isalpha() or len(word) < 4:
        return word
    w = word
    for fim, troca in _PLURAIS:
        if w.endswith(fim) and len(w) - len(fim) + len(troca) >= 3 and (fim != "eis" or len(w) >= 6):
            w = w[:-len(fim)] + troca
            break
    if len(w) >= 7:
        for fim in _VERBOS:
            if w.endswith(fim):
                w = w[:-len(fim)]
                break
    return w


def _with_stems(words):
    return {_stem(w) for w in words}


def _proximity(tokens, words):
    """1.0 se as palavras da pergunta aparecem juntas (janela de até 12 palavras), 0 se espalhadas."""
    stems = [_stem(t) for t in tokens]
    positions = [[i for i, t in enumerate(stems) if t == _stem(w)] for w in words]
    positions = [p for p in positions if p]
    if len(positions) < 2:
        return 0.0
    best = min(max(abs(min(p, key=lambda j: abs(j - i)) - i) for p in positions) for i in positions[0])
    return 1.0 if best <= 6 else 0.5 if best <= 12 else 0.0


class RagIndex:
    def __init__(self, db_path=DEFAULT_DB):
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"{path} não existe. Rode: python rag.py build")
        real = os.path.realpath(path)
        info = path.stat()
        # Identifica esta versão do índice (o cache de contextos do finetune.py depende dela).
        self.assinatura = f"{info.st_size}-{int(info.st_mtime)}"
        if real.startswith("/content/drive"):
            # Leitura aleatória no Drive é muito lenta: usa uma cópia local.
            local = Path(tempfile.gettempdir()) / f"laika_rag_{info.st_size}.db"
            if not local.exists():
                print(f"Copiando o índice RAG do Drive para o disco local ({info.st_size / 1e9:.1f} GB, só na "
                      "primeira vez)...", flush=True)
                inicio = time.time()
                parcial = local.with_suffix(".parcial")  # se cair no meio, não fica uma cópia pela metade
                shutil.copy(real, parcial)
                os.replace(parcial, local)
                print(f"  índice copiado em {time.time() - inicio:.0f} s", flush=True)
            real = str(local)
        self.arquivo = real
        self.con = sqlite3.connect(f"file:{real}?mode=ro", uri=True, check_same_thread=False)

    def _query(self, match, k):
        try:
            return self.con.execute(
                "SELECT title, text, kind, pos, rowid FROM passages WHERE passages MATCH ? "
                "ORDER BY bm25(passages, 4.0, 1.0) LIMIT ?", (match, k)).fetchall()
        except sqlite3.OperationalError:
            return []

    def search(self, question, k=200):
        words = content_words(question)[:12]
        if not words:
            return []
        # 1) Artigos cujo TÍTULO tem todas as palavras da pergunta ("Vulcão", "Machado de Assis").
        title_rows = self._query(" AND ".join(f'title:"{w}"' for w in words), 15)
        # 1b) ... ou todas as palavras do nome próprio ("Laika" em "a cadela Laika").
        name_words = content_words(question_name(question) or "")
        if name_words and name_words != words:
            title_rows += self._query(" AND ".join(f'title:"{w}"' for w in name_words), 15)
        # 1c) Títulos que COMEÇAM pelas palavras ("Pantanal", "Pelé"): com muitos artigos, os 15 de 1) podiam ser
        # só homônimos ("TV Pantanal", "Isto É Pelé"), e o artigo principal nem entrava na disputa.
        title_rows += self._query('title: ^"' + " ".join(words) + '"', 15)
        # 2) Qualquer trecho com as palavras: exata OU com o mesmo radical ("cadelas" acha "cadela").
        terms = []
        for w in words:
            terms.append(f'"{w}"')
            if len(_stem(w)) >= 4 and _stem(w) != w:
                terms.append(f'"{_stem(w)}"*')
        rows = title_rows + self._query(" OR ".join(terms), k)

        query_stems = {_stem(w) for w in words}
        raw_question = set(re.findall(r"[^\W\d_]+", question.lower()))
        # Números curtos e algarismos romanos não são palavras de busca, mas desempatam títulos:
        # "Sputnik 2" x "Sputnik-1", "Pedro II" x "Pedro I".
        short_numbers = set(re.findall(r"(?<![\d.,])\d{1,2}(?![\d.,])|\b[IVXLC]{1,5}\b", question))
        results, seen = [], set()
        for rank, (title, text, kind, pos, rowid) in enumerate(rows):
            if (title, text) in seen or (kind == "texto" and normalize(title) == "laika"):
                continue  # o texto em que a IA se apresenta só confundiria as perguntas sobre a cadela
            seen.add((title, text))
            main_title = re.sub(r"\s*\(.*?\)", "", title)
            title_words = _with_stems(word_tokens(title))
            main_words = _with_stems(w for w in word_tokens(main_title) if w in content_words(main_title))
            text_tokens = word_tokens(text)
            all_words = title_words | _with_stems(text_tokens)
            coverage = sum(_stem(w) in all_words for w in words) / len(words)
            in_title = sum(_stem(w) in title_words for w in words) / len(words)

            score = coverage + 0.3 * in_title + KIND_BONUS.get(kind, 0)
            # Mesmas letras mas acentos diferentes ("Pele" x "Pelé") não contam como título igual.
            raw_title = set(re.findall(r"[^\W\d_]+", main_title.lower()))
            accent_clash = any(normalize(a) == normalize(b) and a != b for a in raw_title for b in raw_question)
            desamb = _with_stems(word_tokens(title)) - _with_stems(word_tokens(main_title))
            if accent_clash:
                score -= 0.5
            elif main_words and main_words == query_stems:
                score += 0.6                      # título exatamente igual ao assunto
            elif main_words and main_words < query_stems:
                # Título contido na pergunta: "Laika" em "a cadela Laika", "Rio Amazonas" em "o tamanho do rio
                # Amazonas" (quanto mais da pergunta o título cobre, mais vale), e mais se o resto está no trecho.
                score += 0.5 * len(main_words) / len(query_stems)
                if query_stems - main_words - desamb <= _with_stems(text_tokens):
                    score += 0.15
            elif in_title > 0 and main_words:
                extra = len(main_words - query_stems) / len(main_words)
                score -= 0.5 * extra              # "Prêmio Machado de Assis" < "Machado de Assis"
            if "(" in title:
                if desamb and desamb <= query_stems:
                    score += 0.3                  # "Marte (planeta)" em "o planeta Marte tem água?"
                elif not desamb <= query_stems:
                    score -= 0.2                  # desambiguação: "Cristo Redentor (Porto Alegre)"
            if pos == 0 and in_title > 0:
                score += 0.1                      # 1º trecho do artigo costuma ter a definição
            if short_numbers & set(re.findall(r"\d+|\b[IVXLC]{1,5}\b", title)):
                score += 0.1                      # "Sputnik 2", "Pedro II do Brasil"
            score += 0.2 * _proximity(text_tokens, words)
            score -= 0.002 * rank
            results.append({"title": title, "text": text, "kind": kind,
                            "coverage": coverage, "in_title": in_title, "score": score, "rowid": rowid})
        # Homônimos ("Java", a ilha, e "Java (linguagem de programação)"): sem pista na pergunta, ganha um pouco o
        # artigo mais antigo da Wikipédia (o índice segue a ordem de criação), que costuma ser o sentido mais
        # conhecido (a linguagem é o artigo 545; a ilha, o 15.980). Pistas ("a ilha de Java") pesam mais.
        grupos = {}
        for r in results:
            if r["kind"] == "wiki":
                grupos.setdefault(normalize(re.sub(r"\s*\(.*?\)", "", r["title"])), []).append((r["rowid"], r["title"]))
        antigos = {min(g)[1] for g in grupos.values() if len({t for _, t in g}) > 1}
        for r in results:
            if r["kind"] == "wiki" and r["title"] in antigos:
                r["score"] += 0.3
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def best(self, question):
        """O trecho mais relevante, ou None se a busca não tiver confiança."""
        return _confident(self.search(question))

    def contexts(self, question, k=1):
        """Até k trechos confiáveis para a pergunta (lista vazia se nenhum).

        Tenta cada consulta de rag_queries (a pergunta inteira e, se ela não achar nada com
        confiança, só o nome próprio). Os trechos extras são do mesmo artigo do primeiro, na
        ordem de quantas palavras da pergunta eles têm (empate: a nota da busca).
        Na busca só pelo nome, os textos de data/modern também precisam da nota mínima: qualquer
        texto que cite "França" cobre 100% da consulta "França"; e, se o 1º resultado da pergunta inteira
        é um artigo cujo título tem o nome, ele é o escolhido.
        """
        first = []
        for i, query in enumerate(rag_queries(question)):
            results = self.search(query)
            top = _confident(results, any_text=i == 0)
            if i == 0:
                first = results
            elif first and first[0]["coverage"] >= 0.6 and first[0]["kind"] == "wiki" \
                    and {_stem(w) for w in content_words(query)} <= _with_stems(word_tokens(first[0]["title"])):
                # Na busca só pelo nome, o 1º resultado da pergunta inteira ganha se o título dele tem o nome:
                # "o tamanho do rio Amazonas" fica com "Rio Amazonas", e não com o estado "Amazonas".
                top, results = first[0], first
            if top is None:
                continue
            hits = [top]
            if k > 1:
                wanted = {_stem(w) for w in content_words(question)}
                same = [r for r in results if r["title"] == top["title"] and r["text"] != top["text"]]
                same.sort(key=lambda r: -len(wanted & {_stem(t) for t in word_tokens(r["text"])}))
                hits += same[:k - 1]
            return hits
        return []


def _confident(results, min_coverage=0.6, min_score=1.8, any_text=True):
    """O primeiro resultado, se a busca tiver confiança; senão None.

    Contexto errado atrapalha mais do que nenhum contexto, então só aceita resultados
    com nota alta (em geral, quando o assunto da pergunta é o título do artigo) ou, na
    primeira busca (any_text), textos de data/modern com alguma palavra da pergunta no título.
    Antes qualquer texto de data/modern passava: "O que é pedra?" usava "As pirâmides do Egito".
    """
    if not results or results[0]["coverage"] < min_coverage:
        return None
    top = results[0]
    if top["score"] >= min_score or (any_text and top["kind"] == "texto" and top.get("in_title", 0) > 0):
        return top
    return None


def open_index(db_path=DEFAULT_DB, quiet=False):
    """Abre o índice se existir; senão devolve None (o chat funciona sem RAG)."""
    try:
        return RagIndex(db_path)
    except FileNotFoundError as error:
        if not quiet:
            print(f"RAG desligado: {error}")
        return None


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="monta o índice de busca")
    b.add_argument("--db", default=DEFAULT_DB)
    b.add_argument("--force", action="store_true")
    s = sub.add_parser("search", help="testa uma busca")
    s.add_argument("question")
    s.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args()

    if args.cmd == "build":
        build(args.db, args.force)
    else:
        index = RagIndex(args.db)
        for r in index.search(args.question)[:5]:
            print(f"[{r['kind']}] {r['title']} (cobertura {r['coverage']:.2f}, nota {r['score']:.2f})")
            print("   ", r["text"][:300])


if __name__ == "__main__":
    main()
