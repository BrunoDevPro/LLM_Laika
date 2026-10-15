"""Baixa os dados de treino: livros do Project Gutenberg (data/books/) e artigos da
Wikipédia em português moderno (data/wiki/ e data/qa_auto/).

Rode no Colab (que tem internet livre). Você também pode simplesmente colocar seus
próprios .txt em data/books/ e pular este script.
"""

import argparse
import csv
import io
import time
import urllib.request
from pathlib import Path

from data_utils import clean_gutenberg, clean_wiki, wiki_definition

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


def download_gutenberg(out, max_books):
    out.mkdir(parents=True, exist_ok=True)
    saved = len(list(out.glob("*.txt")))
    print(f"{saved} livros já em {out}")
    if saved >= max_books:
        return

    try:
        books = portuguese_books()
    except Exception as error:
        print("Falha ao baixar o catálogo do Gutenberg:", error)
        print("Alternativa: coloque seus .txt em", out)
        return
    print(f"{len(books)} livros em português no catálogo; baixando até {max_books}...")

    for book_id, title in books:
        if saved >= max_books:
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


def download_wikipedia(wiki_dir, qa_auto_dir, n_articles, per_file=2000):
    """Baixa os primeiros parágrafos de artigos da Wikipédia em português (CC BY-SA).

    Gera texto moderno para o pré-treino (data/wiki/) e perguntas 'O que é X?' /
    'Quem foi X?' a partir da 1ª frase de cada artigo (data/qa_auto/).
    """
    done = wiki_dir / ".pronto"
    if done.exists() and int(done.read_text() or 0) >= n_articles:
        print(f"Wikipédia já baixada ({done.read_text()} artigos) em {wiki_dir}")
        return
    try:
        from datasets import load_dataset
    except ImportError:
        print("Para baixar a Wikipédia, instale: pip install datasets")
        return

    wiki_dir.mkdir(parents=True, exist_ok=True)
    qa_auto_dir.mkdir(parents=True, exist_ok=True)
    print(f"Baixando {n_articles} artigos da Wikipédia em português...")
    try:
        stream = load_dataset("wikimedia/wikipedia", "20231101.pt", split="train", streaming=True)
    except Exception as error:
        print("Falha ao abrir a Wikipédia:", error)
        return

    kept, file_index, buffer, definitions = 0, 0, [], []

    def flush():
        nonlocal file_index, buffer
        if buffer:
            (wiki_dir / f"wiki_{file_index:03d}.txt").write_text("\n\n".join(buffer), encoding="utf-8")
            file_index += 1
            buffer = []

    try:
        for row in stream:
            paragraphs = clean_wiki(row["text"])
            if not paragraphs or sum(len(p.split()) for p in paragraphs) < 40:
                continue
            buffer.append(row["title"] + "\n\n" + "\n\n".join(paragraphs))
            definition = wiki_definition(row["title"], paragraphs[0])
            if definition:
                definitions.append(definition)
            kept += 1
            if len(buffer) >= per_file:
                flush()
                print(f"  {kept} artigos...", flush=True)
            if kept >= n_articles:
                break
    except Exception as error:
        print("Download da Wikipédia interrompido:", error)
    flush()

    (qa_auto_dir / "wiki_definicoes.txt").write_text("\n\n".join(definitions), encoding="utf-8")
    done.write_text(str(kept))
    total = sum(p.stat().st_size for p in wiki_dir.glob("*.txt"))
    print(f"Pronto: {kept} artigos ({total / 1e6:.1f} MB) e {len(definitions)} perguntas 'O que é X?'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/books")
    parser.add_argument("--max-books", type=int, default=400)
    parser.add_argument("--wiki", type=int, default=30000, help="nº de artigos da Wikipédia (0 = não baixar)")
    parser.add_argument("--wiki-dir", default="data/wiki")
    parser.add_argument("--qa-auto-dir", default="data/qa_auto")
    args = parser.parse_args()

    download_gutenberg(Path(args.out), args.max_books)
    if args.wiki > 0:
        download_wikipedia(Path(args.wiki_dir), Path(args.qa_auto_dir), args.wiki)


if __name__ == "__main__":
    main()
