"""Fine-tuning: ensina o formato pergunta -> resposta.

Para o modelo não decorar o pergeresp (e responder tudo com ele), cada lote mistura:
  1) exemplos escritos à mão do data/qa/*.txt (pelo menos ~25% dos exemplos de chat; com
     ~7,5 mil exemplos, cada um aparece uma vez por época, ~37%); o identidade.txt (nome da
     Laika) tem peso extra;
  2) exemplos sintéticos: "continue o texto", "frase com a palavra X", "complete a frase"
     (de todos os textos) e "resuma o texto" (trechos dos livros do Gutenberg), as perguntas
     "O que é X?" tiradas da Wikipédia (data/qa_auto/) e ~20 mil perguntas com Contexto tiradas
     dos trechos da Wikipédia ("Onde X nasceu?", "O que X inventou?"; 10% com o trecho errado e a
     resposta "não sei");
  3) trechos de texto puros (replay), para não esquecer o português do pré-treino.

Com o índice do RAG pronto (python rag.py build), parte das perguntas ganha um
"Contexto:" achado nos textos, igual ao que o chat faz. Assim o modelo aprende a usar
o contexto quando ele ajuda e a ignorá-lo quando não ajuda.

Memória de IA: as conversas de data/qa/conversas.jsonl e ~30% dos outros exemplos vêm com
trocas anteriores no prompt, como o chat manda; a loss fica só na última resposta.

Parte de checkpoints/pretrain_best.pt e grava em checkpoints/finetuned.pt, então o
pré-treino nunca é sobrescrito: dá para repetir só este script à vontade.
"""

import argparse
import json
import math
import random
import shutil
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

from chat import build_prompt, generate, with_citation
from data_utils import (load_qa_examples, parse_qa_text, synthetic_examples, fit_context, split_conversation,
                        reading_examples, chat_turn, rag_chunks, wants_rag, MAX_CONTEXT_WORDS,
                        ASSISTANT_TOKEN, END_TOKEN, EOT_TOKEN, PAD_TOKEN, USER_TOKEN)
from model import build_model
from rag import open_index, wiki_passages

parser = argparse.ArgumentParser()
parser.add_argument("--books", nargs="+", default=["data/books", "data/wiki", "data/modern"])
parser.add_argument("--summary-books", default="data/books",
                    help="de onde saem os trechos dos 'Resuma o texto' sintéticos")
parser.add_argument("--qa", default="data/qa")
parser.add_argument("--qa-auto", default="data/qa_auto", help="perguntas geradas da Wikipédia")
parser.add_argument("--wiki-qa", type=int, default=3000, help="máximo de perguntas da Wikipédia usadas")
parser.add_argument("--wiki-dir", default="data/wiki")
parser.add_argument("--wiki-leitura", type=int, default=20000,
                    help="perguntas com Contexto tiradas dos trechos da Wikipédia (\"Onde X nasceu?\"...)")
parser.add_argument("--wiki-mb", type=float, default=40, help="MB de artigos lidos para essas perguntas")
parser.add_argument("--history-share", type=float, default=0.3,
                    help="fração dos exemplos que ganham 1 a 4 trocas anteriores (memória de IA)")
parser.add_argument("--identity-boost", type=int, default=2,
                    help="peso extra do identidade.txt (quem é a Laika)")
parser.add_argument("--out", default="checkpoints")
parser.add_argument("--epochs", type=int, default=2, help="era 4; com muito mais exemplos, 2 bastam")
parser.add_argument("--max-qa-repeat", type=int, default=2, help="máximo de vezes que cada exemplo escrito à mão aparece por época")
parser.add_argument("--max-text-mb", type=float, default=40,
                    help="MB de texto (amostrados) usados para exemplos sintéticos e replay")
parser.add_argument("--max-summary-books", type=int, default=80)
parser.add_argument("--rag-db", default="data/rag/laika_rag.db")
parser.add_argument("--rag-share", type=float, default=0.5,
                    help="fração das perguntas (que pedem informação) que ganham Contexto do RAG")
parser.add_argument("--no-rag", action="store_true")
parser.add_argument("--lr", type=float, default=None,
                    help="taxa de aprendizado (o tamanho do passo de cada ajuste dos pesos); "
                         "padrão: 5e-5 até 20M de parâmetros e 1e-4 nos modelos maiores")
parser.add_argument("--batch-size", type=int, default=16)
parser.add_argument("--no-backup", action="store_true", help="não guarda o finetuned.pt anterior em checkpoints/backups")
parser.add_argument("--synthetic", type=int, default=10000,
                    help="nº de exemplos gerados dos livros (era 4000; subiu junto com os ~7,5 mil escritos à mão)")
parser.add_argument("--qa-share", type=float, default=0.25, help="fração dos exemplos de chat vinda do pergeresp")
parser.add_argument("--replay", type=float, default=0.25, help="fração de cada lote com texto puro dos livros")
parser.add_argument("--val-fraction", type=float, default=0.1)
parser.add_argument("--patience", type=int, default=2)
parser.add_argument("--dropout", type=float, default=0.1)
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()

random.seed(args.seed)
torch.manual_seed(args.seed)
out_dir = Path(args.out)
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = Tokenizer.from_file(str(out_dir / "tokenizer.json"))
ckpt = torch.load(out_dir / "pretrain_best.pt", map_location=device)
cfg = ckpt["config"]
block = cfg["block_size"]

model = build_model(cfg, dropout=args.dropout).to(device)
model.load_state_dict(ckpt["model"])
n_params = sum(p.numel() for p in model.parameters())
# Modelos maiores com a taxa do de 7M quase não aprendiam os exemplos escritos (nem o próprio nome).
lr = args.lr if args.lr is not None else (1e-4 if n_params > 20e6 else 5e-5)
print(f"Pré-treino carregado (val loss {ckpt['val_loss']:.4f}, step {ckpt['step']}, "
      f"{n_params / 1e6:.1f}M parâmetros, taxa de aprendizado {lr:g})")

assistant_id = tokenizer.token_to_id(ASSISTANT_TOKEN)
end_id = tokenizer.token_to_id(END_TOKEN)
pad_id = tokenizer.token_to_id(PAD_TOKEN)
eot_id = tokenizer.token_to_id(EOT_TOKEN)


# ---------- Dados ----------
def sample_texts(files, max_bytes):
    """Lê arquivos em ordem aleatória até max_bytes (com 100 mil artigos, ler tudo não cabe na RAM).
    Os textos de data/modern entram sempre."""
    files = list(files)
    random.shuffle(files)
    files.sort(key=lambda f: f.parent.name != "modern")
    texts, total = [], 0
    for f in files:
        if total >= max_bytes and f.parent.name != "modern":
            break
        texts.append(f.read_text(encoding="utf-8"))
        total += f.stat().st_size
    return texts


book_files = [f for folder in args.books for f in sorted(Path(folder).glob("*.txt"))]
if not book_files:
    raise SystemExit(f"Nenhum texto em {args.books}: o fine-tuning usa os textos para gerar exemplos.")
book_texts = sample_texts(book_files, args.max_text_mb * 1e6)
summary_files = sorted(Path(args.summary_books).glob("*.txt"))
random.shuffle(summary_files)
summary_texts = [p.read_text(encoding="utf-8") for p in summary_files[:args.max_summary_books]]
print(f"Textos usados: {len(book_texts)} de {len(book_files)} arquivos "
      f"(~{sum(map(len, book_texts)) / 1e6:.0f} M caracteres)")

print("Lendo perguntas/respostas:")
qa_texts = load_qa_examples(args.qa)
# Conversas de várias trocas (gerar_pergeresp.py): "Qual é a capital da França?" ... "E da Itália?".
conversas_path = Path(args.qa) / "conversas.jsonl"
if conversas_path.exists():
    conversas = [" ".join(chat_turn(q, a) for q, a in json.loads(line))
                 for line in conversas_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"  conversas.jsonl: {len(conversas)} conversas")
    qa_texts += conversas
identity_texts = set(parse_qa_text((Path(args.qa) / "identidade.txt").read_text(encoding="utf-8"))) \
    if (Path(args.qa) / "identidade.txt").exists() else set()

syn_texts = synthetic_examples(book_texts, args.synthetic, seed=args.seed,
                               summary_texts=summary_texts or None)
print(f"Exemplos sintéticos gerados dos textos: {len(syn_texts)} "
      f"(resumos de {len(summary_texts)} livros do Gutenberg incluídos)")
if Path(args.qa_auto).exists():
    print("Perguntas automáticas (Wikipédia):")
    auto = load_qa_examples(args.qa_auto)
    random.shuffle(auto)
    syn_texts += auto[:args.wiki_qa]

# Perguntas com Contexto tiradas dos trechos da Wikipédia (os mesmos trechos que o RAG usa).
wiki_files = sorted(Path(args.wiki_dir).glob("*.txt"))
random.shuffle(wiki_files)
passages, size = [], 0
for f in wiki_files:
    if size >= args.wiki_mb * 1e6:
        break
    passages += list(wiki_passages(f.read_text(encoding="utf-8")))
    size += f.stat().st_size
reading = reading_examples(passages, args.wiki_leitura, chunks=rag_chunks(block), seed=args.seed)
print(f"Leitura da Wikipédia: {len(reading)} perguntas com Contexto (de {len(passages)} trechos)")
syn_texts += reading

# ---------- Contexto do RAG em parte das perguntas ----------
rag = None if args.no_rag else open_index(args.rag_db)


def add_context(examples, share):
    """Põe o Contexto do RAG na última pergunta, como o chat faz (1 a 3 trechos, conforme a janela)."""
    if rag is None or share <= 0:
        return examples, 0
    out, n = [], 0
    k = rag_chunks(block)
    for example in examples:
        history, question, answer = split_conversation(example)
        if random.random() < share and wants_rag(question):
            hits = rag.contexts(question, k)
            if hits:
                prefix = history + " " if history else ""

                def count(user_text):
                    return len(tokenizer.encode(prefix + chat_turn(user_text, answer)).ids)
                user_text = fit_context(count, question, " ".join(h["text"] for h in hits), block,
                                        max_words=MAX_CONTEXT_WORDS * len(hits))
                if user_text:
                    out.append(prefix + chat_turn(user_text, answer))
                    n += 1
                    continue
        out.append(example)
    return out, n


def add_history(examples, pool, share, skip=frozenset()):
    """Põe 1 a 4 trocas anteriores (sem relação) em parte dos exemplos: o modelo se acostuma a ver o
    histórico no prompt (memória de IA) e a usá-lo só quando ele importa, como nas conversas."""
    if not pool or share <= 0:
        return examples, 0
    out, n = [], 0
    for example in examples:
        if example not in skip and random.random() < share:
            for k in range(random.randint(1, 4), 0, -1):
                joined = " ".join(chat_turn(q, a) for q, a in random.sample(pool, k)) + " " + example
                if len(tokenizer.encode(joined).ids) <= block:
                    out.append(joined)
                    n += 1
                    break
            else:
                out.append(example)
        else:
            out.append(example)
    return out, n


if rag is not None:
    qa_texts, n_qa_ctx = add_context(qa_texts, args.rag_share)
    syn_texts, n_syn_ctx = add_context(syn_texts, args.rag_share)
    print(f"RAG: {n_qa_ctx} perguntas escritas à mão e {n_syn_ctx} automáticas ganharam Contexto")
else:
    print("RAG desligado: o fine-tuning segue sem exemplos com Contexto do RAG "
          "(os de data/qa/leitura.txt e da Wikipédia continuam).")

# Trocas curtas, sem contexto, para servir de histórico.
pool = [split_conversation(e)[1:] for e in qa_texts if e.count(USER_TOKEN) == 1 and "Contexto:" not in e]
pool = [(q, a) for q, a in pool if len(q.split()) <= 15 and len(a.split()) <= 25]
qa_texts, n_qa_hist = add_history(qa_texts, pool, args.history_share, skip=identity_texts)
syn_texts, n_syn_hist = add_history(syn_texts, pool, args.history_share)
print(f"Memória de IA: {n_qa_hist + n_syn_hist} exemplos ganharam mensagens anteriores")

for sample in random.sample(syn_texts, min(4, len(syn_texts))):
    print("   ", sample[:160].replace("\n", " "))


def encode_chat(texts, identity=frozenset()):
    items, too_long = [], 0
    for text in texts:
        if text in identity:
            continue  # tratado à parte
        ids = tokenizer.encode(text).ids
        if len(ids) > block:
            too_long += 1
            continue
        if assistant_id not in ids or end_id not in ids:
            continue
        # Numa conversa, só a ÚLTIMA resposta é treinada (as anteriores são o histórico).
        answer_start = len(ids) - ids[::-1].index(assistant_id)
        inputs = ids[:-1]
        # Loss só na RESPOSTA (e no <|end|>); a pergunta vira -100.
        labels = [tok if pos + 1 >= answer_start else -100 for pos, tok in enumerate(ids[1:])]
        items.append((inputs, labels))
    return items, too_long


qa_data, qa_long = encode_chat(qa_texts, identity_texts)
id_data, _ = encode_chat(list(identity_texts))
syn_data, _ = encode_chat(syn_texts)
if qa_long:
    print(f"ATENÇÃO: {qa_long} exemplos do pergeresp passam de {block} tokens e foram descartados.")
if not syn_data:
    raise SystemExit("Não consegui gerar exemplos dos livros. Confira os .txt em data/books.")


def split(items):
    random.shuffle(items)
    n_val = max(1, int(len(items) * args.val_fraction)) if len(items) >= 10 else 0
    return items[n_val:], items[:n_val]


qa_train, qa_val = split(qa_data)
id_train, id_val = split(id_data)
qa_val += id_val
syn_train, syn_val = split(syn_data)

# Repete o pergeresp só o suficiente para ele ser ~qa_share dos exemplos de chat.
qa_repeat = 0
if qa_train:
    wanted = args.qa_share / (1 - args.qa_share) * len(syn_train)
    qa_repeat = min(args.max_qa_repeat, max(1, round(wanted / len(qa_train))))
id_repeat = qa_repeat * args.identity_boost if id_train else 0
print(f"Treino: {len(syn_train)} sintéticos + {len(qa_train)} do pergeresp (x{qa_repeat}) + "
      f"{len(id_train)} de identidade (x{id_repeat}) | "
      f"validação: {len(syn_val)} sintéticos + {len(qa_val)} escritos à mão")

# Texto contínuo dos livros para o replay (numpy para economizar memória).
parts = [np.array(enc.ids + [eot_id], dtype=np.int32) for enc in tokenizer.encode_batch(book_texts)]
stream = torch.from_numpy(np.concatenate(parts)).long()
del parts
n_replay = round(args.batch_size * args.replay / (1 - args.replay)) if args.replay > 0 else 0


# Trechos de até 512 tokens: com o contexto de 2048 (100M), trechos da janela inteira só gastariam memória.
replay_len = min(block, 512)


def replay_items(n):
    if n == 0:
        return []
    starts = torch.randint(0, len(stream) - replay_len - 1, (n,)).tolist()
    return [(stream[s:s + replay_len].tolist(), stream[s + 1:s + replay_len + 1].tolist()) for s in starts]


def make_batch(items):
    longest = max(len(inp) for inp, _ in items)
    xs, ys = [], []
    for inp, lab in items:
        pad = longest - len(inp)
        # Padding à direita: com máscara causal, as posições reais nunca enxergam o padding.
        xs.append(inp + [pad_id] * pad)
        ys.append(lab + [-100] * pad)
    return torch.tensor(xs, device=device), torch.tensor(ys, device=device)


# bf16 na A100/L4 (metade da memória; o de 100M não caberia em float32 com o lote inteiro). Na T4, float32.
amp = device == "cuda" and torch.cuda.is_bf16_supported()


def batch_loss(items):
    x, y = make_batch(items)
    with torch.autocast(device_type=device, dtype=torch.bfloat16, enabled=amp):
        logits = model(x)
    return F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)


@torch.no_grad()
def validate(items):
    if not items:
        return float("nan")
    model.eval()
    losses = [batch_loss(items[i:i + args.batch_size]).item()
              for i in range(0, len(items), args.batch_size)]
    model.train()
    return sum(losses) / len(losses)


SAMPLE_HISTORY = [("Qual é a capital da França?", "A capital da França é Paris.")]
SAMPLE_PROMPTS = [
    "Qual é o seu nome?", "Oi", "O que é um vulcão?", "Quem foi Santos Dumont?", "Qual é a capital da França?",
    "Complete a frase: Quem espera", "Escreva uma frase com a palavra noite.",
    "Resuma o texto: O menino acordou cedo, tomou café e foi para a escola de bicicleta. "
    "No caminho, viu um cachorro perdido e parou para ajudar. Por isso, chegou atrasado, "
    "mas a professora entendeu quando ele contou o que tinha acontecido.",
]


@torch.no_grad()
def show_samples():
    model.eval()
    for question in SAMPLE_PROMPTS:
        prompt, source = build_prompt(question, tokenizer, block, rag, None, max_new_tokens=60)
        answer = generate(model, tokenizer, prompt, device, max_new_tokens=60)
        print(f"   Você: {question}\n   LLM:  {with_citation(answer, source)}")
    # Memória de IA: a pergunta só faz sentido com a anterior.
    prompt, source = build_prompt("E da Itália?", tokenizer, block, rag, None, 60, SAMPLE_HISTORY)
    answer = generate(model, tokenizer, prompt, device, max_new_tokens=60)
    print(f"   (depois de \"{SAMPLE_HISTORY[0][0]}\") Você: E da Itália?\n   LLM:  {with_citation(answer, source)}")
    model.train()


# ---------- Treino ----------
optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
items_per_epoch = len(syn_train) + len(qa_train) * qa_repeat + len(id_train) * id_repeat
steps_per_epoch = math.ceil(items_per_epoch / args.batch_size)
total_steps = steps_per_epoch * args.epochs
warmup = min(100, total_steps // 10)
print(f"{steps_per_epoch} steps por época, até {total_steps} no total "
      f"(lote = {args.batch_size} de chat + {n_replay} de livro)")


def lr_at(step):
    if step < warmup:
        return lr * (step + 1) / warmup
    progress = (step - warmup) / max(1, total_steps - warmup)
    return lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0))))


print("\nAntes do fine-tuning:")
show_samples()

best_val, bad_epochs, step = float("inf"), 0, 0
best_path = out_dir / "finetuned.pt"
# O finetuned.pt é sobrescrito a cada melhora: antes, guarda o anterior em checkpoints/backups/ (os 3 últimos).
if best_path.exists() and not args.no_backup:
    backups = out_dir / "backups"
    backups.mkdir(exist_ok=True)
    quando = time.strftime("%Y-%m-%d_%H%M", time.localtime(best_path.stat().st_mtime))
    shutil.copy2(best_path, backups / f"finetuned_{quando}.pt")
    for velho in sorted(backups.glob("finetuned_*.pt"))[:-3]:
        velho.unlink()
    print(f"Backup do finetuned.pt anterior: {backups / f'finetuned_{quando}.pt'}")
model.train()

for epoch in range(1, args.epochs + 1):
    train_items = syn_train + qa_train * qa_repeat + id_train * id_repeat
    random.shuffle(train_items)
    running = 0.0
    for i in range(0, len(train_items), args.batch_size):
        for group in optimizer.param_groups:
            group["lr"] = lr_at(step)
        loss = batch_loss(train_items[i:i + args.batch_size] + replay_items(n_replay))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        running += loss.item()
        step += 1

    syn_v, qa_v = validate(syn_val), validate(qa_val)
    # Critério de parada: os dois tipos de pergunta contam igual.
    combined = syn_v if math.isnan(qa_v) else 0.5 * (syn_v + qa_v)
    note = ""
    if combined < best_val:
        best_val, bad_epochs, note = combined, 0, "  <- melhor, salvo"
        torch.save({"model": model.state_dict(), "config": cfg, "val_loss": combined,
                    "finetuned": True}, best_path)
    else:
        bad_epochs += 1
    print(f"\népoca {epoch} | treino {running / steps_per_epoch:.4f} | val livros {syn_v:.4f} | "
          f"val pergeresp {qa_v:.4f}{note}", flush=True)
    show_samples()
    if bad_epochs >= args.patience:
        print("Early stopping.")
        break

print("=" * 40)
print(f"Fine-tuning concluído. Melhor val: {best_val:.4f} -> {best_path}")
print("Se ainda repetir o pergeresp: rode de novo com mais sintéticos (--synthetic 20000) ou --lr menor.")
print("Converse com: python chat.py")
