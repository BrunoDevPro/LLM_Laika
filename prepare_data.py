"""Baixa livros em português (domínio público) do Project Gutenberg para data/books/.

Rode no Colab (que tem internet livre). Você também pode simplesmente colocar seus
próprios .txt em data/books/ e pular este script.
"""

import argparse
import csv
import io
import time
import urllib.request
from pathlib import Path

from data_utils import clean_gutenberg

CATALOG = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
MIN_CHARS = 30_000


def fetch(url, timeout=90, tries=3):
    last_error = None
    for attempt in range(tries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "LLM_Laika/1.0"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as error:
            last_error = error
            time.sleep(2 * (attempt + 1))
    raise last_error


def candidate_urls(book_id):
    return [
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
        f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8",
    ]


def portuguese_books():
    raw = fetch(CATALOG, timeout=120).decode("utf-8-sig", errors="ignore")
    rows = csv.DictReader(io.StringIO(raw))
    books = []
    for row in rows:
        if row.get("Type") == "Text" and (row.get("Language") or "").strip() == "pt":
            books.append((row["Text#"], " ".join(row.get("Title", "").split())))
    return books


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/books")
    parser.add_argument("--max-books", type=int, default=400)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    saved = len(list(out.glob("*.txt")))
    print(f"{saved} livros já em {out}")

    try:
        books = portuguese_books()
    except Exception as error:
        print("Falha ao baixar o catálogo do Gutenberg:", error)
        print("Alternativa: coloque seus .txt em", out)
        return
    print(f"{len(books)} livros em português no catálogo; baixando até {args.max_books}...")

    for book_id, title in books:
        if saved >= args.max_books:
            break
        target = out / f"gutenberg_{book_id}.txt"
        if target.exists():
            continue

        raw = None
        for url in candidate_urls(book_id):
            try:
                raw = fetch(url, tries=2).decode("utf-8", errors="ignore")
                break
            except Exception:
                continue
        if raw is None:
            print(f"  pulando {book_id}: não consegui baixar")
            continue

        text = clean_gutenberg(raw)
        if len(text) < MIN_CHARS:
            continue
        target.write_text(text, encoding="utf-8")
        saved += 1
        print(f"  [{saved}] {title[:60]} ({len(text) // 1000}k caracteres)", flush=True)
        time.sleep(0.3)

    total = sum(p.stat().st_size for p in out.glob("*.txt"))
    print(f"Pronto: {saved} livros, {total / 1e6:.1f} MB em {out}")
    if saved == 0:
        print("Nenhum livro baixado. Coloque seus .txt em", out)


if __name__ == "__main__":
    main()
