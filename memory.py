"""Memória do chatbot: guarda o que o usuário conta sobre si e lembra depois.

As últimas trocas da conversa entram no prompt (a "memória de IA", em chat.build_prompt),
mas só enquanto couberem na janela e só durante a conversa. O que vale entre conversas
fica FORA do modelo, aqui:

- frases como "meu nome é Ana", "eu moro em Recife", "eu gosto de futebol",
  "minha cor favorita é azul" e "lembre que amanhã tenho prova" são guardadas
  num arquivo JSON (no Drive, sobrevive entre sessões);
- perguntas como "qual é o meu nome?" ou "o que você lembra de mim?" são
  respondidas direto da memória, sem passar pelo modelo;
- as anotações ("lembre que...") que tiverem a ver com a pergunta entram no
  Contexto, no mesmo formato que o RAG, para o modelo usar.

Nada disso muda o modelo nem o prompt das perguntas normais.
"""

import json
import re
from pathlib import Path

from data_utils import content_words

_STOP = r"(?=[.,;!?]|\s+e\s+(?:eu|meu|minha|moro|tenho|gosto)\b|$)"
_VALUE = r"([^.,;!?]+?)" + _STOP

SAVE_NAME = re.compile(r"\b(?:meu nome (?:é|e)|me chamo|eu me chamo|pode me chamar de)\s+" + _VALUE, re.I)
SAVE_CITY = re.compile(r"\b(?:eu )?moro ((?:em|no|na|nos|nas) " + _VALUE[1:], re.I)
SAVE_AGE = re.compile(r"\b(?:eu )?tenho (\d{1,3}) anos\b", re.I)
SAVE_LIKE = re.compile(r"\b(?:eu )?(n[ãa]o )?gosto (?:muito )?((?:de|do|da|dos|das) " + _VALUE[1:], re.I)
SAVE_FAV = re.compile(r"\b(?:o |a )?(meu|minha) ([a-zà-ÿ]+(?: [a-zà-ÿ]+)?) favorit[oa] (?:é|e) " + _VALUE, re.I)
SAVE_NOTE = re.compile(r"^(?:por favor,? )?(?:lembre(?:-se)?|lembra|guarde|anote|memorize)(?: de)?(?: que)?[:,]?\s+(.+)$", re.I)

ASK_NAME = re.compile(r"\b(qual (?:é |e )?(?:o )?meu nome|como (?:é que )?eu me chamo|voc[eê] sabe (?:qual (?:é )?)?(?:o )?meu nome|quem sou eu|sabe quem eu sou)", re.I)
ASK_CITY = re.compile(r"\bonde (?:é que )?eu moro\b", re.I)
ASK_AGE = re.compile(r"\b(quantos anos eu tenho|qual (?:é )?a minha idade)\b", re.I)
ASK_LIKES = re.compile(r"\b(?:do que|o que) eu (?:n[ãa]o )?gosto\b", re.I)
ASK_FAV = re.compile(r"\bqual (?:é |e )?(?:a |o )?(?:minha|meu) ([a-zà-ÿ]+(?: [a-zà-ÿ]+)?) favorit[oa]", re.I)


# "Faça uma frase com o meu nome", "Escreva um poema usando o seu nome": o nome vai no Contexto.
NAME_REF_USER = re.compile(r"\b(?:o\s+)?meu\s+(?:pr[oó]prio\s+)?nome\b(?!\s+(?:é|e)\b)", re.I)
NAME_REF_LAIKA = re.compile(r"\b(?:o\s+)?(?:seu|teu)\s+(?:pr[oó]prio\s+)?nome\b(?!\s+(?:é|e)\b)", re.I)


def _fav_phrase(key, info):
    """'sua cor favorita é azul' / 'seu animal favorito é o gato'."""
    if info.get("fem"):
        return f"sua {key} favorita é {info['valor']}"
    return f"seu {key} favorito é {info['valor']}"


# Mensagem enviada pela metade ("Meu nome é", "Eu moro em"): pergunta o resto em vez de o modelo inventar.
INCOMPLETE = [
    (re.compile(r"^(?:meu nome (?:é|e)|me chamo|eu me chamo|pode me chamar de)\s*[.!]*$", re.I),
     "Acho que a mensagem ficou pela metade. Qual é o seu nome?"),
    (re.compile(r"^(?:eu )?moro(?: (?:em|no|na|nos|nas))?\s*[.!]*$", re.I),
     "Faltou o final da frase. Onde você mora?"),
    (re.compile(r"^(?:eu )?(?:n[ãa]o )?gosto(?: muito)?(?: (?:de|do|da|dos|das))?\s*[.!]*$", re.I),
     "Faltou o final da frase. Do que você gosta?"),
    (re.compile(r"^(?:eu )?tenho\s*[.!]*$", re.I),
     "Faltou o final da frase. O que você tem?"),
    (re.compile(r"^(?:por favor,? )?(?:lembre(?:-se)?|lembra|guarde|anote|memorize)(?: de)?(?: que)?\s*[.!:]*$", re.I),
     "Claro! O que você quer que eu lembre?"),
]
ASK_ALL = re.compile(r"\bo que voc[eê] (?:sabe|lembra|guardou)(?: (?:sobre|de) mim)?\b", re.I)
FORGET = re.compile(r"\b(esque[cç]a|apague|limpe|apaga|esquece) (?:tudo|a (?:sua )?mem[oó]ria|o que eu (?:te )?disse)\b", re.I)


def _clean(value):
    return value.strip().strip("\"'").strip()


class Memory:
    def __init__(self, path="checkpoints/memoria.json"):
        self.path = Path(path)
        self.data = {"nome": None, "cidade": None, "idade": None, "gostos": [], "nao_gosta": [],
                     "favoritos": {}, "notas": []}
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as error:
            print("(não consegui salvar a memória:", error, ")")

    # ---------- perguntas respondidas pela memória ----------
    def _recall(self, msg):
        d = self.data
        if FORGET.search(msg):
            self.data = {"nome": None, "cidade": None, "idade": None, "gostos": [], "nao_gosta": [],
                         "favoritos": {}, "notas": []}
            self.save()
            return "Pronto, apaguei tudo o que eu tinha guardado sobre você."
        if ASK_NAME.search(msg):
            return f"Seu nome é {d['nome']}." if d["nome"] else "Você ainda não me disse o seu nome. Como você se chama?"
        if ASK_CITY.search(msg):
            return f"Você mora {d['cidade']}." if d["cidade"] else "Você ainda não me disse onde mora."
        if ASK_AGE.search(msg):
            return f"Você tem {d['idade']} anos." if d["idade"] else "Você ainda não me disse a sua idade."
        if ASK_LIKES.search(msg):
            if "não" in msg.lower() or "nao" in msg.lower():
                items = d["nao_gosta"]
                return ("Você me disse que não gosta " + ", ".join(items) + ".") if items else "Você ainda não me disse do que não gosta."
            return ("Você me disse que gosta " + ", ".join(d["gostos"]) + ".") if d["gostos"] else "Você ainda não me disse do que gosta."
        fav = ASK_FAV.search(msg)
        if fav:
            key = fav.group(1).lower()
            if key in d["favoritos"]:
                return f"Você me disse que {_fav_phrase(key, d['favoritos'][key])}."
            return "Você ainda não me contou isso."
        if ASK_ALL.search(msg):
            return self.summary()
        return None

    def summary(self):
        d, parts = self.data, []
        if d["nome"]:
            parts.append(f"seu nome é {d['nome']}")
        if d["cidade"]:
            parts.append(f"você mora {d['cidade']}")
        if d["idade"]:
            parts.append(f"você tem {d['idade']} anos")
        if d["gostos"]:
            parts.append("você gosta " + ", ".join(d["gostos"]))
        if d["nao_gosta"]:
            parts.append("você não gosta " + ", ".join(d["nao_gosta"]))
        for k, v in d["favoritos"].items():
            parts.append(_fav_phrase(k, v))
        for n in d["notas"]:
            parts.append(f"você me pediu para lembrar: {n}")
        if not parts:
            return "Ainda não sei nada sobre você. Você pode me contar, por exemplo: meu nome é Ana."
        return "Eu lembro que " + "; ".join(parts) + "."

    # ---------- fatos que o usuário conta ----------
    def _learn(self, msg):
        d, learned = self.data, []
        note = SAVE_NOTE.search(msg.strip())
        if note:
            text = _clean(note.group(1)).rstrip(".!")
            if text.lower() in ("que", "de", "de que"):  # "Lembre que" sem o resto
                return []
            if text and text not in d["notas"]:
                d["notas"].append(text)
            return [f"Certo, vou lembrar: {text}."]
        m = SAVE_NAME.search(msg)
        if m and "?" not in msg:
            name = " ".join(w.capitalize() for w in _clean(m.group(1)).split()[:3])
            if name:
                d["nome"] = name
                learned.append(f"Prazer, {name}! Vou lembrar o seu nome.")
        m = SAVE_CITY.search(msg)
        if m and "?" not in msg:
            d["cidade"] = _clean(m.group(1))
            learned.append(f"Anotado: você mora {d['cidade']}.")
        m = SAVE_AGE.search(msg)
        if m and "?" not in msg:
            d["idade"] = m.group(1)
            learned.append(f"Anotado: você tem {d['idade']} anos.")
        m = SAVE_LIKE.search(msg)
        if m and "?" not in msg:
            negative, thing = m.group(1), _clean(m.group(2))
            target = d["nao_gosta"] if negative else d["gostos"]
            if thing not in target:
                target.append(thing)
            learned.append(f"Anotado: você {'não ' if negative else ''}gosta {thing}.")
        m = SAVE_FAV.search(msg)
        if m and "?" not in msg:
            info = {"valor": _clean(m.group(3)), "fem": m.group(1).lower() == "minha"}
            key = m.group(2).lower()
            d["favoritos"][key] = info
            learned.append(f"Anotado: {_fav_phrase(key, info)}.")
        return learned

    def handle(self, msg):
        """Resposta direta da memória, ou None para o modelo responder normalmente."""
        answer = self._recall(msg)
        if answer:
            return answer
        learned = self._learn(msg)
        if learned:
            self.save()
            return " ".join(learned)
        for pattern, reply in INCOMPLETE:
            if pattern.match(msg.strip()):
                return reply
        if NAME_REF_USER.search(msg) and not self.data["nome"]:
            # "Faça uma frase com o meu nome" sem saber o nome: pergunta, em vez de o modelo inventar um.
            return "Você ainda não me disse o seu nome. Como você se chama?"
        return None

    def context_for(self, question):
        """Anotações relacionadas à pergunta, para entrar no Contexto do modelo; e o nome do usuário ou o da Laika
        quando a mensagem fala em "meu nome" ou "seu nome" ("Faça uma frase com o meu nome.")."""
        parts = []
        if NAME_REF_USER.search(question) and self.data["nome"]:
            parts.append(f"O nome do usuário é {self.data['nome']}.")
        if NAME_REF_LAIKA.search(question):
            parts.append("O nome da assistente é Laika.")
        words = set(content_words(question))
        if words:
            related = [n for n in self.data["notas"] if words & set(content_words(n))]
            parts += [f"O usuário pediu para lembrar: {n}." for n in related[:2]]
        return " ".join(parts)
