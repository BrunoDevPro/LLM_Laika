"""Baixa livros em português (domínio público) do Project Gutenberg para data/books/.

Rode no Colab (que tem internet livre). Você também pode simplesmente colocar seus
próprios .txt em data/books/ e pular este script.
"""

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from data_utils import clean_gutenberg

API = "https://gutendex.com/books/"
MIN_CHARS = 30_000


def fetch(url, timeout=60):
    request = urllib.request.Request(url, headers={"User-Agent": "LLM_Laika/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def text_url(book):
    formats = book.get("formats", {})
    candidates = [u for k, u in formats.items() if k.startswith("text/plain") and not u.endswith(".zip")]
    utf8 = [u for u in candidates if "utf-8" in u.lower() or u.endswith(".txt.utf-8")]
    return (utf8 or candidates or [None])[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/books")
    parser.add_argument("--max-books", type=int, default=80)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    saved = len(list(out.glob("*.txt")))
    print(f"{saved} livros já em {out}")
    url = API + "?" + urllib.parse.urlencode({"languages": "pt", "copyright": "false"})

    while url and saved < args.max_books:
        try:
            page = json.loads(fetch(url))
        except Exception as error:  # rede/API fora do ar
            print("Falha ao consultar o Gutenberg:", error)
            print("Alternativa: coloque seus .txt em", out)
            break

        for book in page["results"]:
            if saved >= args.max_books:
                break
            target = out / f"gutenberg_{book['id']}.txt"
            link = text_url(book)
            if target.exists() or not link:
                continue
            try:
                raw = fetch(link).decode("utf-8", errors="ignore")
            except Exception as error:
                print(f"  pulando {book['id']}: {error}")
                continue
            text = clean_gutenberg(raw)
            if len(text) < MIN_CHARS:
                continue
            target.write_text(text, encoding="utf-8")
            saved += 1
            print(f"  [{saved}] {book['title'][:60]} ({len(text) // 1000}k caracteres)")
            time.sleep(0.5)

        url = page.get("next")

    total = sum(p.stat().st_size for p in out.glob("*.txt"))
    print(f"Pronto: {saved} livros, {total / 1e6:.1f} MB em {out}")


if __name__ == "__main__":
    main()
