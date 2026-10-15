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


# ---------- Exemplos sintéticos gerados a partir dos livros ----------

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
_STRIP = ".,;:!?…—–-\"'«»()[]“”‘’"


def _good_sentence(sentence):
    words = sentence.split()
    if not 5 <= len(words) <= 40:
        return False
    chars = sentence.replace(" ", "")
    if sum(c.isalpha() for c in chars) < 0.75 * len(chars):
        return False  # números, índices, tabelas
    if sentence.isupper() or sentence[-1] not in ".!?…":
        return False
    return True


def book_paragraphs(text):
    """Divide o livro em parágrafos, cada um como lista de frases 'boas'."""
    paragraphs = []
    for block in text.split("\n\n"):
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(block.strip())]
        sentences = [s for s in sentences if _good_sentence(s)]
        if sentences:
            paragraphs.append(sentences)
    return paragraphs


def _content_words(sentence):
    words = []
    for raw in sentence.split()[1:]:
        word = raw.strip(_STRIP)
        if len(word) >= 5 and word.isalpha() and word.islower():
            words.append(word)
    return words


def _chat(question, answer):
    return f"{USER_TOKEN} {question} {ASSISTANT_TOKEN} {answer} {END_TOKEN}"


def synthetic_examples(book_texts, n, seed=0):
    """Cria pares pergunta/resposta cujas respostas saem dos próprios livros.

    Isso ensina o modelo a responder usando o que aprendeu no pré-treino, em vez
    de devolver sempre alguma resposta decorada do pergeresp.
    """
    import random

    rng = random.Random(seed)
    paragraphs = [p for text in book_texts for p in book_paragraphs(text)]
    multi = [p for p in paragraphs if len(p) >= 2]
    if not paragraphs:
        return []

    examples, seen = [], set()
    attempts = 0
    while len(examples) < n and attempts < n * 10:
        attempts += 1
        kind = rng.random()

        if kind < 0.4 and multi:
            para = rng.choice(multi)
            i = rng.randrange(len(para) - 1)
            answer = para[i + 1]
            if i + 2 < len(para) and rng.random() < 0.4:
                answer += " " + para[i + 2]
            question = rng.choice([
                "Continue o texto: {}", "Continue: {}", "O que vem depois de: {}",
                "Escreva a continuação: {}",
            ]).format(para[i])

        elif kind < 0.75:
            sentence = rng.choice(rng.choice(paragraphs))
            words = _content_words(sentence)
            if not words:
                continue
            word = rng.choice(words)
            answer = sentence
            question = rng.choice([
                "Escreva uma frase com a palavra {}.", "Use a palavra \"{}\" em uma frase.",
                "Crie uma frase com {}.", "Me dê um exemplo de frase com a palavra {}.",
            ]).format(word)

        else:
            sentence = rng.choice(rng.choice(paragraphs))
            words = sentence.split()
            cut = rng.randint(3, max(3, len(words) - 3))
            answer = " ".join(words[cut:])
            question = rng.choice([
                "Complete a frase: {}", "Termine a frase: {}", "Complete: {}",
            ]).format(" ".join(words[:cut]))

        example = _chat(question, answer)
        if example not in seen:
            seen.add(example)
            examples.append(example)
    return examples
