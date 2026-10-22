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
from pathlib import Path

from data_utils import _SENTENCE_SPLIT, content_words, word_tokens

DEFAULT_DB = "data/rag/laika_rag.db"
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

def _stem(word):
    return word[:5] if len(word) >= 6 and word.isalpha() else word


def _with_stems(words):
    return {_stem(w) for w in words}


class RagIndex:
    def __init__(self, db_path=DEFAULT_DB):
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"{path} não existe. Rode: python rag.py build")
        real = os.path.realpath(path)
        if real.startswith("/content/drive"):
            # Leitura aleatória no Drive é muito lenta: usa uma cópia local.
            local = Path(tempfile.gettempdir()) / f"laika_rag_{path.stat().st_size}.db"
            if not local.exists():
                print("Copiando o índice RAG do Drive para o disco local (só na primeira vez)...")
                shutil.copy(real, local)
            real = str(local)
        self.con = sqlite3.connect(f"file:{real}?mode=ro", uri=True, check_same_thread=False)

    def search(self, question, k=10):
        words = content_words(question)[:12]
        if not words:
            return []
        # Palavra exata OU mesmo começo (radical simples: "pisou" acha "pisar").
        terms = []
        for w in words:
            terms.append(f'"{w}"')
            if len(w) >= 6 and w.isalpha():
                terms.append(f'"{w[:5]}"*')
        query = " OR ".join(terms)
        try:
            rows = self.con.execute(
                "SELECT title, text, kind, pos FROM passages WHERE passages MATCH ? "
                "ORDER BY bm25(passages, 4.0, 1.0) LIMIT ?", (query, k)).fetchall()
        except sqlite3.OperationalError:
            return []
        results = []
        for rank, (title, text, kind, pos) in enumerate(rows):
            title_words = _with_stems(word_tokens(title))
            all_words = title_words | _with_stems(word_tokens(text))
            coverage = sum(_stem(w) in all_words for w in words) / len(words)
            in_title = sum(_stem(w) in title_words for w in words) / len(words)
            # O 1º trecho de um artigo costuma ter a definição ("X é ...").
            lead = 0.1 if pos == 0 and in_title > 0 else 0.0
            score = coverage + 0.3 * in_title + KIND_BONUS.get(kind, 0) + lead - 0.01 * rank
            results.append({"title": title, "text": text, "kind": kind,
                            "coverage": coverage, "score": score})
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def best(self, question, min_coverage=0.6):
        """O trecho mais relevante, ou None se nenhum cobrir a maior parte das palavras da pergunta."""
        results = self.search(question)
        if results and results[0]["coverage"] >= min_coverage:
            return results[0]
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
