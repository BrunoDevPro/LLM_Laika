"""Utilitários de dados que não dependem de torch (fáceis de testar)."""

import re
from pathlib import Path

USER_TOKEN = "<|user|>"
ASSISTANT_TOKEN = "<|assistant|>"
END_TOKEN = "<|end|>"
EOT_TOKEN = "<|endoftext|>"
PAD_TOKEN = "[PAD]"
UNK_TOKEN = "[UNK]"
SPECIAL_TOKENS = [PAD_TOKEN, UNK_TOKEN, USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN, EOT_TOKEN]

_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.S | re.I)
_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.I)


def clean_gutenberg(text):
    """Remove cabeçalho/rodapé do Project Gutenberg e normaliza quebras de linha."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")

    start = _START.search(text)
    if start:
        text = text[start.end():]
    end = _END.search(text)
    if end:
        text = text[:end.start()]

    # Gutenberg quebra linhas em ~70 colunas: junta linhas soltas dentro do
    # parágrafo e mantém só as linhas em branco como separador.
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_qa_text(text):
    """Lê '<|user|> pergunta <|assistant|> resposta <|end|>' e devolve exemplos prontos."""
    examples = []
    for block in text.split(END_TOKEN):
        block = block.strip()
        if not block or USER_TOKEN not in block or ASSISTANT_TOKEN not in block:
            continue
        user_part, answer = block.split(ASSISTANT_TOKEN, 1)
        question = user_part.replace(USER_TOKEN, "").strip()
        answer = answer.strip()
        if not question or not answer:
            continue
        examples.append(f"{USER_TOKEN} {question} {ASSISTANT_TOKEN} {answer} {END_TOKEN}")
    return examples


def load_qa_examples(qa_dir):
    examples = []
    for path in sorted(Path(qa_dir).glob("*.txt")):
        found = parse_qa_text(path.read_text(encoding="utf-8"))
        print(f"  {path.name}: {len(found)} exemplos")
        examples.extend(found)
    return examples
