"""Inicia a Laika no computador (Windows, Linux ou Mac).

Confere se os arquivos necessários estão no lugar e, se o índice completo do RAG
(data/rag/laika_rag.db) não estiver aqui, monta um índice pequeno com os textos de
data/modern para a busca funcionar mesmo assim.
"""

import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
base_mode = "--base" in sys.argv

needed = ["checkpoints/tokenizer.json", "checkpoints/pretrain_best.pt" if base_mode else "checkpoints/finetuned.pt"]
missing = [f for f in needed if not Path(f).exists()]
if missing:
    print("Faltam arquivos:")
    for f in missing:
        print("  -", f)
    print("\nBaixe-os do Google Drive (pasta Meu Drive/LLM_Laika/checkpoints) e coloque na pasta checkpoints.")
    sys.exit(1)

def fts5_ok():
    import sqlite3
    try:
        sqlite3.connect(":memory:").execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        return True
    except sqlite3.OperationalError:
        return False


if not base_mode and "--no-rag" not in sys.argv and not fts5_ok():
    print("Aviso: o SQLite deste Python não tem FTS5; a busca nos textos (RAG) fica desligada.")
    print("Instalar o Python mais recente de python.org costuma resolver.")
    sys.argv.append("--no-rag")

if not base_mode and "--no-rag" not in sys.argv and "--rag-db" not in sys.argv:
    # Procura o índice completo: na pasta data/rag, na pasta da Laika ou em Downloads.
    candidates = [Path("data/rag/laika_rag.db"), Path("laika_rag.db")]
    for folder in [Path.home() / "Downloads", Path.home() / "Transferências"]:
        if folder.is_dir():  # o navegador pode ter renomeado: "laika_rag (1).db"
            candidates += sorted(folder.glob("laika_rag*.db"))
    full = next((c for c in candidates if c.exists() and c.stat().st_size > 1_000_000), None)
    if full:
        print("Usando o índice RAG completo:", full.resolve())
        sys.argv += ["--rag-db", str(full)]
    else:
        mini = Path("data/rag/laika_rag_mini.db")
        import rag
        rag.SOURCES = [("data/modern", "texto")]
        if not mini.exists():
            print("Índice completo não encontrado (data/rag/laika_rag.db).")
            print("Montando um índice pequeno só com os textos de data/modern...")
            rag.build(str(mini))
        sys.argv += ["--rag-db", str(mini)]

import chat  # noqa: E402

chat.main()
