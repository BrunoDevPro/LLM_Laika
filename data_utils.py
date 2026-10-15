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
        # Só o que vem depois do último <|user|>: ignora comentários (# ...) antes dele.
        question = user_part.rsplit(USER_TOKEN, 1)[-1].strip()
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


SUMMARY_REQUESTS = ["Resuma o texto: {}", "Resuma: {}", "Faça um resumo do texto: {}",
                    "Qual é a ideia principal deste texto? {}", "Resuma em uma frase: {}"]


def extractive_summary(sentences):
    """Escolhe a(s) frase(s) mais representativa(s) do parágrafo (resumo extrativo).

    Cada frase ganha pontos pelas palavras que ela compartilha com o resto do texto;
    a primeira frase ganha um pequeno bônus, porque costuma apresentar o assunto.
    """
    from collections import Counter

    bags = [{w.lower().strip(_STRIP) for w in s.split() if len(w.strip(_STRIP)) >= 4}
            for s in sentences]
    freq = Counter(w for bag in bags for w in bag)
    scores = []
    for i, bag in enumerate(bags):
        shared = sum(freq[w] - 1 for w in bag)  # palavras que aparecem em outras frases
        score = shared / (len(bag) + 3) + (0.3 if i == 0 else 0.0)
        scores.append((score, i))
    keep = 2 if len(sentences) >= 5 else 1
    chosen = sorted(i for _, i in sorted(scores, reverse=True)[:keep])
    return " ".join(sentences[i] for i in chosen)


def summary_examples(texts, n, seed=0, min_words=40, max_words=90):
    """'Resuma o texto: <parágrafo>' -> resumo extrativo, a partir dos livros."""
    import random

    rng = random.Random(seed)
    candidates = []
    for text in texts:
        for para in book_paragraphs(text):
            words = sum(len(s.split()) for s in para)
            if 3 <= len(para) <= 6 and min_words <= words <= max_words:
                candidates.append(para)
    rng.shuffle(candidates)
    return [_chat(rng.choice(SUMMARY_REQUESTS).format(" ".join(p)), extractive_summary(p))
            for p in candidates[:n]]


# ---------- Wikipédia ----------

_PAREN = re.compile(r"\s*\([^()]*\)")
_WIKI_STOP = ("Ver também", "Referências", "Ligações externas", "Bibliografia", "Notas",
              "Fontes", "Leitura adicional")


def clean_wiki(text, max_paragraphs=8):
    """Fica só com os parágrafos de prosa do começo do artigo (sem títulos e listas)."""
    paragraphs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) < 40 and line.startswith(_WIKI_STOP):
            break
        if len(line) < 60 or line[-1] not in ".!?…":
            continue
        paragraphs.append(re.sub(r"\s+", " ", line))
        if len(paragraphs) >= max_paragraphs:
            break
    return paragraphs


def wiki_definition(title, first_paragraph):
    """Transforma a 1ª frase de um artigo em 'O que é X?' / 'Quem foi X?'."""
    title = _PAREN.sub("", title).strip()
    if not title or title.startswith("Lista") or len(title) > 50:
        return None
    first = _SENTENCE_SPLIT.split(first_paragraph, 1)[0]
    has_dates = bool(re.search(r"\([^()]*\d{3,4}[^()]*\)", first))
    sentence = re.sub(r"\s+", " ", _PAREN.sub("", first)).strip()
    sentence = sentence.replace(" ,", ",")
    if "(" in sentence or ")" in sentence or not sentence.endswith("."):
        return None
    if not 5 <= len(sentence.split()) <= 40:
        return None
    match = re.match(r"^(?:(o|a|os|as)\s+)?" + re.escape(title.lower()) + r",?\s+(é|foi|são|foram)\s",
                     sentence.lower())
    if not match:
        return None
    article, verb = match.groups()
    subject = f"{article} {title}" if article else title
    if verb == "é":
        question = f"Quem é {subject}?" if has_dates else f"O que é {subject}?"
    elif verb == "foi":
        question = f"Quem foi {subject}?" if has_dates else f"O que foi {subject}?"
    else:
        question = f"O que são {subject}?" if verb == "são" else f"O que foram {subject}?"
    return _chat(question, sentence)


def synthetic_examples(book_texts, n, seed=0, summary_texts=None, summary_share=0.2):
    """Cria pares pergunta/resposta cujas respostas saem dos próprios livros.

    Isso ensina o modelo a responder usando o que aprendeu no pré-treino, em vez
    de devolver sempre alguma resposta decorada do pergeresp. Uma parte
    (summary_share) são pedidos de resumo com trechos de summary_texts.
    """
    import random

    rng = random.Random(seed)
    n_summary = int(n * summary_share)
    summaries = summary_examples(summary_texts if summary_texts is not None else book_texts,
                                 n_summary, seed=seed)
    n -= len(summaries)

    paragraphs = [p for text in book_texts for p in book_paragraphs(text)]
    multi = [p for p in paragraphs if len(p) >= 2]
    if not paragraphs:
        return summaries

    examples, seen = list(summaries), set(summaries)
    target = len(examples) + n
    attempts = 0
    while len(examples) < target and attempts < n * 10:
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
