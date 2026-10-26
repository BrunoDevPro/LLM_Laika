"""Baixa os dados de treino: livros do Project Gutenberg (data/books/), artigos da
Wikipédia em português moderno (data/wiki/ e data/qa_auto/) e, para os modelos grandes,
o Corpus Carolina (data/carolina/) e parte do GigaVerbo-v2 (data/gigaverbo/).

Rode no Colab (que tem internet livre). Você também pode simplesmente colocar seus
próprios .txt em data/books/ e pular este script.
"""

import argparse
import csv
import gzip
import io
import json
import random
import math
import os
import re
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from data_utils import EOT_TOKEN, clean_gutenberg, clean_wiki, rag_question, wiki_definition

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
    titles_path = out / "titulos.tsv"
    print(f"{saved} livros já em {out}")
    if saved >= max_books and titles_path.exists():
        return

    try:
        books = portuguese_books()
    except Exception as error:
        print("Falha ao baixar o catálogo do Gutenberg:", error)
        print("Alternativa: coloque seus .txt em", out)
        return
    # Títulos dos livros (o RAG mostra de onde veio cada trecho).
    titles_path.write_text("\n".join(f"{i}\t{t}" for i, t in books), encoding="utf-8")
    if saved >= max_books:
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


def _estado_wiki(done):
    """Progresso salvo em .pronto: {"artigos": n, "fim": bool} (as versões antigas guardavam só o número)."""
    if not done.exists():
        return {"artigos": 0, "fim": False}
    texto = done.read_text().strip()
    try:
        d = json.loads(texto or "0")
    except ValueError:
        return {"artigos": 0, "fim": False}
    if isinstance(d, int):
        return {"artigos": d, "fim": False}
    return {"artigos": int(d.get("artigos", 0)), "fim": bool(d.get("fim"))}


def download_wikipedia(wiki_dir, qa_auto_dir, n_articles, per_file=2000):
    """Baixa os primeiros parágrafos de artigos da Wikipédia em português (CC BY-SA).

    Gera texto moderno para o pré-treino (data/wiki/) e perguntas 'O que é X?' /
    'Quem foi X?' a partir da 1ª frase de cada artigo (data/qa_auto/).

    Pedir mais artigos do que já tem (ex.: de 100 mil para 1 milhão) ou rodar de novo depois de
    uma queda continua de onde parou: os arquivos já gravados ficam, e o começo da lista é só
    percorrido de novo (para pular esses artigos e refazer as perguntas), sem regravar nada.
    """
    done = wiki_dir / ".pronto"
    estado = _estado_wiki(done)
    if estado["artigos"] >= n_articles or estado["fim"]:
        extra = ", todos os que existem" if estado["fim"] else ""
        print(f"Wikipédia já baixada ({estado['artigos']} artigos{extra}) em {wiki_dir}")
        return
    try:
        from datasets import load_dataset
    except ImportError:
        print("Para baixar a Wikipédia, instale: pip install datasets")
        return

    wiki_dir.mkdir(parents=True, exist_ok=True)
    qa_auto_dir.mkdir(parents=True, exist_ok=True)
    # Só arquivos completos contam (o último pode ter ficado pela metade numa queda).
    pular = (estado["artigos"] // per_file) * per_file
    if any(not (wiki_dir / f"wiki_{i:03d}.txt").exists() for i in range(pular // per_file)):
        pular = 0
    if pular:
        print(f"Continuando: {pular} artigos já estão no Drive; baixando até {n_articles}...")
    else:
        print(f"Baixando {n_articles} artigos da Wikipédia em português...")
    try:
        stream = load_dataset("wikimedia/wikipedia", "20231101.pt", split="train", streaming=True)
    except Exception as error:
        print("Falha ao abrir a Wikipédia:", error)
        return

    kept, file_index, buffer, definitions, fim = 0, pular // per_file, [], [], True
    inicio = time.time()

    def flush():
        nonlocal file_index, buffer
        if buffer:
            (wiki_dir / f"wiki_{file_index:03d}.txt").write_text("\n\n".join(buffer), encoding="utf-8")
            file_index += 1
            buffer = []
            done.write_text(json.dumps({"artigos": kept, "fim": False}))  # para continuar se cair

    try:
        for row in stream:
            paragraphs = clean_wiki(row["text"])
            if not paragraphs or sum(len(p.split()) for p in paragraphs) < 40:
                continue
            definition = wiki_definition(row["title"], paragraphs[0])
            if definition:
                definitions.append(definition)
            kept += 1
            if kept <= pular:
                if kept % 50000 == 0:
                    print(f"  pulando os já baixados: {kept}/{pular}", flush=True)
                continue
            buffer.append(row["title"] + "\n\n" + "\n\n".join(paragraphs))
            if len(buffer) >= per_file:
                flush()
                novos = kept - pular
                vel = novos / max(1.0, time.time() - inicio)
                print(f"  {kept} artigos ({vel:.0f}/s; faltam ~{max(0, n_articles - kept) / max(vel, 1) / 60:.0f} min)",
                      flush=True)
            if kept >= n_articles:
                fim = False
                break
    except Exception as error:
        print("Download da Wikipédia interrompido:", error)
        fim = False
    flush()

    (qa_auto_dir / "wiki_definicoes.txt").write_text("\n\n".join(definitions), encoding="utf-8")
    done.write_text(json.dumps({"artigos": kept, "fim": fim}))
    total = sum(p.stat().st_size for p in wiki_dir.glob("*.txt"))
    extra = " (todos os artigos que existem)" if fim else ""
    print(f"Pronto: {kept} artigos{extra} ({total / 1e6:.1f} MB) e {len(definitions)} perguntas 'O que é X?'")


# ---------- Corpus Carolina e GigaVerbo (modelos grandes) ----------
# Os dois vão só para o pré-treino (não entram no índice do RAG). Cada documento é separado do
# seguinte por uma linha com <|endoftext|>, que o tokenizer lê como o token de fim de texto.
SEPARADOR = f"\n\n{EOT_TOKEN}\n\n"
HF = "https://huggingface.co/datasets/"


def _json_url(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "LLM-Laika"}), timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def _estado(arquivo):
    try:
        return json.loads(arquivo.read_text())
    except (OSError, ValueError):
        return {}


def _gravar_estado(arquivo, estado):
    tmp = arquivo.with_suffix(".tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False))
    os.replace(tmp, arquivo)


def _limpar_doc(texto):
    linhas = [re.sub(r"[ \t\u00a0]+", " ", l).strip() for l in texto.replace("\r", "").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(linhas)).strip().replace(EOT_TOKEN, "")


# Corpus Carolina (carolina-c4ai/corpus-carolina, versão 2): português brasileiro contemporâneo em XML TEI,
# com a licença de cada documento no cabeçalho (CC BY, CC BY-SA, domínio público...).
CAROLINA = HF + "carolina-c4ai/corpus-carolina/resolve/main/corpus/"
CAROLINA_TAXONOMIAS = {"dat": "datasets_and_other_corpora", "jud": "judicial_branch", "leg": "legislative_branch",
                       "pub": "public_domain_works", "soc": "social_media", "uni": "university_domains",
                       "wik": "wikis"}
# Sem os textos de leis e decisões judiciais por padrão: são ~45% do corpus e têm um estilo muito
# próprio. Peça com --carolina dat,jud,leg,pub,soc,uni,wik.
CAROLINA_PADRAO = "dat,pub,soc,uni,wik"
_TEI = "{http://www.tei-c.org/ns/1.0}"
# Páginas de bastidores dos wikis (usuários, discussões, predefinições...).
_WIKI_BASTIDOR = re.compile(r"^(usu[aá]ri[oa]|discuss[aã]o|predefini[cç][aã]o|categoria|wikip[eé]dia|ajuda|portal|"
                            r"mediawiki|ficheiro|arquivo|imagem|m[oó]dulo|especial|wiki[a-z]*|anexo|livro|"
                            r"projeto|tópico|t[oó]pico|user|talk|template|file|help|category)\s*:", re.I)


def _carolina_docs(caminho):
    """(texto, título, fonte) de cada documento de um .xml.gz do Carolina, sem carregar o arquivo todo."""
    with gzip.open(caminho) as g:
        for _, el in ET.iterparse(g, events=("end",)):
            if el.tag != _TEI + "TEI":
                continue
            corpo = el.find(_TEI + "text")  # os <p> do cabeçalho (licença, descrição) ficam de fora
            ps = corpo.iter(_TEI + "p") if corpo is not None else []
            texto = "\n\n".join(p.text.strip() for p in ps if p.text and p.text.strip())
            nome = el.find(f".//{_TEI}titleStmt/{_TEI}title/{_TEI}name")
            media = el.find(f".//{_TEI}titleStmt/{_TEI}title/{_TEI}media")
            yield texto, (nome.text or "") if nome is not None else "", (media.get("source", "") if media is not None else "")
            el.clear()


def download_carolina(pasta, taxonomias, com_wikipedia=False):
    """Baixa o Corpus Carolina (as taxonomias pedidas), um .xml.gz por vez, e grava o texto em
    data/carolina/carolina_<arquivo>.txt. Continua de onde parou (data/carolina/.pronto).

    A Wikipédia que vem dentro do Carolina (os arquivos wikis/pt/, ~1 GB) é pulada: o prepare_data já baixa
    a Wikipédia inteira. Do resto dos wikis, só ficam as páginas de conteúdo (sem usuários e discussões).
    """
    pasta.mkdir(parents=True, exist_ok=True)
    pronto = pasta / ".pronto"
    estado = _estado(pronto)
    feitos = set(estado.get("arquivos", []))
    total_docs = estado.get("docs", 0)
    inicio = time.time()
    for cod in taxonomias:
        tax = CAROLINA_TAXONOMIAS.get(cod)
        if tax is None:
            raise SystemExit(f"Taxonomia do Carolina desconhecida: {cod} (use {', '.join(CAROLINA_TAXONOMIAS)})")
        try:
            lista = fetch(f"{CAROLINA}{tax}/checksum.sha256").decode("utf-8").split()[1::2]
        except Exception as error:
            print(f"Carolina: não consegui listar {tax}: {error}")
            continue
        for rel in lista:
            chave = f"{tax}/{rel}"
            if chave in feitos:
                continue
            if cod == "wik" and rel.startswith("pt/") and not com_wikipedia:
                continue  # os arquivos pt/WIK* do Carolina são a própria Wikipédia: nem baixa
            nome = "carolina_" + re.sub(r"[^A-Za-z0-9]+", "_", f"{cod}_{rel}").strip("_").lower() + ".txt"
            with tempfile.TemporaryDirectory() as tmp:
                gz = Path(tmp) / "a.xml.gz"
                try:
                    gz.write_bytes(fetch(f"{CAROLINA}{tax}/{rel}.gz", timeout=300))
                except Exception as error:
                    print(f"  falhou {chave}: {error} (rode de novo para tentar outra vez)")
                    continue
                docs, pulados = [], 0
                for texto, titulo, fonte in _carolina_docs(gz):
                    if cod == "wik" and ((fonte.startswith("ptwiki") and not com_wikipedia)
                                         or _WIKI_BASTIDOR.match(titulo)):
                        pulados += 1
                        continue
                    texto = _limpar_doc(texto)
                    if len(texto.split()) < 50:
                        pulados += 1
                        continue
                    docs.append(texto)
            if docs:
                destino = pasta / nome
                destino.with_suffix(".tmp").write_text(SEPARADOR.join(docs), encoding="utf-8")
                os.replace(destino.with_suffix(".tmp"), destino)
            feitos.add(chave)
            total_docs += len(docs)
            _gravar_estado(pronto, {"arquivos": sorted(feitos), "docs": total_docs})
            mb = sum(f.stat().st_size for f in pasta.glob("*.txt")) / 1e6
            print(f"  Carolina {chave}: {len(docs)} documentos ({pulados} pulados) | total {total_docs:,} "
                  f"documentos, {mb:,.0f} MB, {time.time() - inicio:.0f}s", flush=True)
    mb = sum(f.stat().st_size for f in pasta.glob("*.txt")) / 1e6
    print(f"Carolina pronto: {total_docs:,} documentos ({mb:,.0f} MB) em {pasta}")


# GigaVerbo-v2 (Polygl0t/gigaverbo-v2): ~320 bilhões de tokens da web em português, com notas de
# qualidade educacional e de toxicidade. Usamos só o subconjunto edu_high (nota educacional ≥ 4) e
# um pedaço de cada um dos 56 arquivos (um "grupo de linhas" do parquet por vez, lido pela internet
# sem baixar o arquivo inteiro), para misturar as fontes: cada arquivo tem um site/crawl diferente.
GIGAVERBO = "Polygl0t/gigaverbo-v2"


def _ordem_espalhada(n):
    """0, n/2, n/4, 3n/4...: posições espalhadas pelo arquivo (sequência de van der Corput)."""
    vistos, ordem, i = set(), [], 1
    while len(ordem) < n:
        f, k, b = 0.0, i, 0.5
        while k:
            f, k, b = f + b * (k & 1), k >> 1, b / 2
        pos = int(f * n) if i > 1 else 0
        i += 1
        if pos not in vistos:
            vistos.add(pos)
            ordem.append(pos)
        if i > 64 * n:
            ordem += [p for p in range(n) if p not in vistos]
    return ordem


def download_gigaverbo(pasta, tokens, subconjunto="edu_high", toxico_max=2):
    """Grava ~`tokens` tokens do GigaVerbo-v2 em data/gigaverbo/gigaverbo_AA_GG.txt (arquivo AA, grupo GG).
    Continua de onde parou (.pronto); pedir mais tokens depois só baixa o que falta.
    `token_count` vem no próprio dataset (tokenizer do Tucano, parecido com o nosso)."""
    try:
        import fsspec
        import pyarrow.parquet as pq
    except ImportError:
        print("Para baixar o GigaVerbo, instale: pip install pyarrow fsspec aiohttp")
        return
    pasta.mkdir(parents=True, exist_ok=True)
    pronto = pasta / ".pronto"
    estado = _estado(pronto)
    feitos = dict(estado.get("grupos", {}))
    total = sum(feitos.values())
    if total >= tokens:
        print(f"GigaVerbo já baixado: {total / 1e9:.2f} bilhão de tokens em {pasta}")
        return
    try:
        arvore = _json_url(f"https://huggingface.co/api/datasets/{GIGAVERBO}/tree/main/{subconjunto}")
    except Exception as error:
        print("GigaVerbo: não consegui listar os arquivos:", error)
        return
    arquivos = sorted(f["path"] for f in arvore if f["path"].endswith(".parquet"))
    print(f"GigaVerbo ({subconjunto}): {len(arquivos)} arquivos; já tem {total / 1e9:.2f} bilhão de tokens, "
          f"meta {tokens / 1e9:.2f} bilhão", flush=True)
    fs = fsspec.filesystem("https")
    abertos, grupos = {}, {}

    def abrir(i):
        if i not in abertos:
            arq = fs.open(f"{HF}{GIGAVERBO}/resolve/main/{arquivos[i]}", "rb", block_size=8 << 20)
            abertos[i] = (arq, pq.ParquetFile(arq))
            grupos[i] = _ordem_espalhada(abertos[i][1].metadata.num_row_groups)
        return abertos[i][1]

    inicio, novos, rodada = time.time(), 0, 0
    try:
        while total < tokens:
            algum = False
            for i in range(len(arquivos)):  # uma rodada = um grupo de cada arquivo
                if total >= tokens:
                    break
                try:
                    pf = abrir(i)
                except Exception as error:
                    print(f"  arquivo {arquivos[i]} não abriu: {error}")
                    continue
                if rodada >= len(grupos[i]):
                    continue
                algum = True
                g = grupos[i][rodada]
                chave = f"{i:02d}_{g:02d}"
                if chave in feitos:
                    continue
                try:
                    t = pf.read_row_group(g, columns=["text", "token_count", "toxic_int_score"])
                except Exception as error:
                    print(f"  grupo {chave} falhou: {error} (rode de novo para tentar outra vez)")
                    continue
                docs, n_tok = [], 0
                for texto, n, tox in zip(t.column("text").to_pylist(), t.column("token_count").to_pylist(),
                                         t.column("toxic_int_score").to_pylist()):
                    if tox is not None and tox > toxico_max:
                        continue
                    texto = _limpar_doc(texto or "")
                    if len(texto) < 300:
                        continue
                    docs.append(texto)
                    n_tok += n or 0
                destino = pasta / f"gigaverbo_{chave}.txt"
                destino.with_suffix(".tmp").write_text(SEPARADOR.join(docs), encoding="utf-8")
                os.replace(destino.with_suffix(".tmp"), destino)
                feitos[chave] = n_tok
                total += n_tok
                novos += n_tok
                _gravar_estado(pronto, {"grupos": feitos, "subconjunto": subconjunto})
                vel = novos / max(1.0, time.time() - inicio)
                print(f"  GigaVerbo {chave}: {len(docs):,} documentos | {total / 1e9:.2f}/{tokens / 1e9:.2f} bilhão "
                      f"de tokens ({vel / 1e6:.1f} M/s; faltam ~{max(0, tokens - total) / max(vel, 1) / 60:.0f} min)",
                      flush=True)
            if not algum:
                break
            rodada += 1
    finally:
        for arq, _ in abertos.values():
            arq.close()
    mb = sum(f.stat().st_size for f in pasta.glob("*.txt")) / 1e6
    print(f"GigaVerbo pronto: {total / 1e9:.2f} bilhão de tokens ({mb:,.0f} MB) em {pasta}")


# ---------- GigaVerbo-v2-SFT (instruções para o fine-tuning) ----------
# Licença Apache 2.0. É gerado por outra IA (Qwen2.5) e filtrado por nota de qualidade; os pesos da Laika
# continuam treinados do zero, isto só entra como exemplo de pergunta e resposta no fine-tuning.
SFT = "Polygl0t/gigaverbo-v2-sft"
# summarization (desde a 1.11): resumos que reescrevem o texto (notícias e artigos; média de ~80 palavras para
# textos de ~200), para o modelo não aprender que resumir é copiar uma frase. Quem já tinha baixado general e
# retrieval só baixa o que falta de summarization.
SFT_PADRAO = "general:0.6,retrieval:0.3,summarization:0.1"
# Exemplos que falam de outra IA ("sou o Qwen, da Alibaba") estragariam a identidade da Laika.
_SFT_OUTRA_IA = re.compile(r"\b(?:qwen|alibaba|openai|chatgpt|gpt-?[345]|anthropic|claude|gemini|llama|deepseek|"
                           r"mistral|tucano|copilot)\b", re.IGNORECASE)
_SFT_FORA = ("```", "<think>", "</think>", "\\[", "$$", "|---", "<tool", "<function")
_CONTEXTO_SFT = re.compile(r"<context>(.*?)</context>", re.DOTALL)


def _limpar_sft(texto):
    """Tira a marcação de Markdown que o app não mostra (negrito, títulos) e espaços sobrando."""
    texto = texto.replace("**", "").replace("__", "")
    texto = re.sub(r"(?m)^#{1,6}\s*", "", texto)
    return _limpar_doc(texto)


def converter_sft(mensagens, max_trocas=5):
    """[{role, content}] -> [[pergunta, resposta], ...] no formato da Laika, ou None se não servir.

    Sem mensagem de sistema; o <context> do subconjunto retrieval vira "Contexto: ... Pergunta: ...",
    o mesmo formato do RAG."""
    msgs = [m for m in mensagens if m.get("role") != "system"]
    if not msgs or len(msgs) % 2 or len(msgs) > 2 * max_trocas:
        return None
    pares = []
    for u, a in zip(msgs[::2], msgs[1::2]):
        if u.get("role") != "user" or a.get("role") != "assistant":
            return None
        q, r = (u.get("content") or "").strip(), (a.get("content") or "").strip()
        if not q or not r or len(q) > 8000 or len(r) > 6000:
            return None
        if any(x in q or x in r for x in _SFT_FORA) or _SFT_OUTRA_IA.search(r):
            return None
        m = _CONTEXTO_SFT.search(q)
        if m:
            contexto = re.sub(r"\s+", " ", m.group(1)).strip()
            pergunta = re.sub(r"\s+", " ", _CONTEXTO_SFT.sub(" ", q)).strip()
            if not contexto or not pergunta:
                return None
            q = rag_question(pergunta, contexto)
        else:
            q = _limpar_sft(q)
        pares.append([q, _limpar_sft(r)])
    return pares


SFT_JUNTAS = "sft_todas.jsonl"


def ler_sft(pasta, gravar=True):
    """As conversas do SFT de `pasta` ([[pergunta, resposta], ...] por conversa).

    O download grava um arquivo por grupo de linhas (milhares de arquivos pequenos, para poder continuar de
    onde parou), e ler milhares de arquivos no Google Drive é muito lento. Por isso eles também ficam juntos em
    sft_todas.jsonl; se ele estiver desatualizado (o .pronto diz quantos grupos já foram juntados), os arquivos
    dos grupos são lidos em paralelo e o junto é gravado de novo (gravar=True)."""
    from concurrent.futures import ThreadPoolExecutor

    pasta = Path(pasta)
    estado = _estado(pasta / ".pronto")
    grupos = estado.get("grupos", {})
    juntas = pasta / SFT_JUNTAS
    if juntas.exists() and estado.get("juntas") == len(grupos):
        inicio = time.time()
        conversas = [json.loads(l) for l in juntas.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"GigaVerbo-SFT: {len(conversas):,} conversas lidas de {juntas} em {time.time() - inicio:.0f} s",
              flush=True)
        return conversas
    arquivos = sorted(pasta.glob("sft_*_*_*.jsonl"))
    if not arquivos:
        return []
    print(f"GigaVerbo-SFT: lendo {len(arquivos):,} arquivos de {pasta} (só desta vez; depois fica tudo em "
          f"{SFT_JUNTAS})...", flush=True)
    inicio, linhas = time.time(), []
    with ThreadPoolExecutor(32) as ex:  # no Drive, o que demora é abrir cada arquivo: em paralelo vai bem mais rápido
        for i, texto in enumerate(ex.map(lambda f: f.read_text(encoding="utf-8"), arquivos), 1):
            linhas += [l for l in texto.splitlines() if l.strip()]
            if i % 300 == 0 or i == len(arquivos):
                print(f"  {i:,}/{len(arquivos):,} arquivos ({time.time() - inicio:.0f} s)", flush=True)
    if gravar:
        try:
            parcial = juntas.with_suffix(".parcial")
            parcial.write_text("\n".join(linhas) + "\n", encoding="utf-8")
            os.replace(parcial, juntas)
            estado["juntas"] = len(grupos)
            _gravar_estado(pasta / ".pronto", estado)
        except OSError as error:
            print("  não consegui gravar o arquivo junto:", error)
    return [json.loads(l) for l in linhas]


def download_sft(pasta, total, subconjuntos=SFT_PADRAO, nota_min=4.0, tokens_max=1500):
    """Grava ~`total` conversas do GigaVerbo-v2-SFT em data/sft/sft_SUB_AA_GG.jsonl (uma conversa por linha,
    lista de [pergunta, resposta], como o data/qa/conversas.jsonl). Pega um grupo de linhas de cada arquivo por
    rodada (espalhado) e continua de onde parou (.pronto).

    subconjuntos: "general:0.6,retrieval:0.3,summarization:0.1" (nome:fração). nota_min: instruct_score mínimo (1 a 5).
    tokens_max: tamanho máximo do exemplo (token_count do dataset); o finetune ainda tira o que não couber."""
    try:
        import fsspec
        import pyarrow.parquet as pq
    except ImportError:
        print("Para baixar o GigaVerbo-SFT, instale: pip install pyarrow fsspec aiohttp")
        return
    pasta.mkdir(parents=True, exist_ok=True)
    pronto = pasta / ".pronto"
    feitos = dict(_estado(pronto).get("grupos", {}))
    partes = []
    for item in subconjuntos.split(","):
        nome, _, frac = item.strip().partition(":")
        if nome:
            partes.append((nome, float(frac or 1)))
    soma = sum(f for _, f in partes) or 1
    fs = fsspec.filesystem("https")
    for nome, frac in partes:
        meta = int(total * frac / soma)
        tem = sum(n for k, n in feitos.items() if k.startswith(nome + "_"))
        if tem >= meta:
            print(f"GigaVerbo-SFT {nome}: já tem {tem:,} de {meta:,}")
            continue
        try:
            arvore = _json_url(f"https://huggingface.co/api/datasets/{SFT}/tree/main/{nome}")
        except Exception as error:
            print(f"GigaVerbo-SFT {nome}: não consegui listar os arquivos:", error)
            continue
        arquivos = sorted(f["path"] for f in arvore if f["path"].endswith(".parquet"))
        print(f"GigaVerbo-SFT {nome}: {len(arquivos)} arquivos; tem {tem:,}, meta {meta:,}", flush=True)
        abertos, grupos, rodada = {}, {}, 0
        try:
            for i, caminho in enumerate(arquivos):
                arq = fs.open(f"{HF}{SFT}/resolve/main/{caminho}", "rb", block_size=8 << 20)
                abertos[i] = (arq, pq.ParquetFile(arq))
                grupos[i] = _ordem_espalhada(abertos[i][1].metadata.num_row_groups)
            # Cada grupo de ~1000 linhas contribui com um pedaço, para a amostra cobrir o subconjunto inteiro.
            por_grupo = max(20, math.ceil(1.2 * meta / max(1, sum(map(len, grupos.values())))))
            while tem < meta:
                algum = False
                for i in range(len(arquivos)):
                    if tem >= meta:
                        break
                    if rodada >= len(grupos[i]):
                        continue
                    algum = True
                    g = grupos[i][rodada]
                    chave = f"{nome}_{i:02d}_{g:03d}"
                    if chave in feitos:
                        continue
                    try:
                        t = abertos[i][1].read_row_group(g, columns=["messages", "token_count", "instruct_score"])
                    except Exception as error:
                        print(f"  grupo {chave} falhou: {error} (rode de novo para tentar outra vez)")
                        continue
                    linhas = []
                    for msgs, n, nota in zip(t.column("messages").to_pylist(), t.column("token_count").to_pylist(),
                                             t.column("instruct_score").to_pylist()):
                        if (nota or 0) < nota_min or (n or 0) > tokens_max:
                            continue
                        pares = converter_sft(msgs or [])
                        if pares:
                            linhas.append(json.dumps(pares, ensure_ascii=False))
                    random.Random(chave).shuffle(linhas)
                    linhas = linhas[:min(por_grupo, meta - tem)]
                    destino = pasta / f"sft_{chave}.jsonl"
                    destino.with_suffix(".tmp").write_text("\n".join(linhas) + "\n", encoding="utf-8")
                    os.replace(destino.with_suffix(".tmp"), destino)
                    feitos[chave] = len(linhas)
                    tem += len(linhas)
                    _gravar_estado(pronto, {"grupos": feitos})
                    print(f"  GigaVerbo-SFT {chave}: {len(linhas):,} conversas | {tem:,}/{meta:,}", flush=True)
                if not algum:
                    break
                rodada += 1
        finally:
            for arq, _ in abertos.values():
                arq.close()
    n = sum(feitos.values())
    print(f"GigaVerbo-SFT pronto: {n:,} conversas em {pasta}")
    ler_sft(pasta)  # junta tudo num arquivo só (o fine-tuning lê bem mais rápido)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/books")
    parser.add_argument("--max-books", type=int, default=500)
    parser.add_argument("--wiki", type=int, default=100000,
                        help="nº de artigos da Wikipédia (0 = não baixar; -1 = todos, ~1,1 milhão)")
    parser.add_argument("--wiki-dir", default="data/wiki")
    parser.add_argument("--qa-auto-dir", default="data/qa_auto")
    parser.add_argument("--carolina", nargs="?", const=CAROLINA_PADRAO, default=None,
                        help=f"baixa o Corpus Carolina (taxonomias separadas por vírgula; sem valor: {CAROLINA_PADRAO})")
    parser.add_argument("--carolina-dir", default="data/carolina")
    parser.add_argument("--gigaverbo", type=float, default=0,
                        help="tokens do GigaVerbo-v2 a baixar (ex.: 1.5e9 = 1,5 bilhão; 0 = não baixar)")
    parser.add_argument("--gigaverbo-dir", default="data/gigaverbo")
    parser.add_argument("--gigaverbo-toxico-max", type=int, default=2,
                        help="nota de toxicidade máxima aceita (1 a 5; o edu_high já vem com no máximo 3)")
    parser.add_argument("--sft", type=int, default=0,
                        help="conversas do GigaVerbo-v2-SFT para o fine-tuning (ex.: 300000; 0 = não baixar)")
    parser.add_argument("--sft-dir", default="data/sft")
    parser.add_argument("--sft-subconjuntos", default=SFT_PADRAO,
                        help=f"subconjuntos e frações (padrão {SFT_PADRAO}; há também rewriting, translation...)")
    parser.add_argument("--sft-nota-min", type=float, default=4.0, help="nota de qualidade mínima (1 a 5)")
    parser.add_argument("--sft-tokens-max", type=int, default=1500,
                        help="tamanho máximo de cada exemplo (o de 100M tem janela de 2048)")
    args = parser.parse_args()

    if args.max_books > 0:
        download_gutenberg(Path(args.out), args.max_books)
    if args.wiki != 0:
        n = args.wiki if args.wiki > 0 else 10 ** 9
        download_wikipedia(Path(args.wiki_dir), Path(args.qa_auto_dir), n)
    if args.carolina:
        download_carolina(Path(args.carolina_dir), [c.strip() for c in args.carolina.split(",") if c.strip()])
    if args.gigaverbo > 0:
        download_gigaverbo(Path(args.gigaverbo_dir), int(args.gigaverbo), toxico_max=args.gigaverbo_toxico_max)
    if args.sft > 0:
        download_sft(Path(args.sft_dir), args.sft, args.sft_subconjuntos, args.sft_nota_min, args.sft_tokens_max)


if __name__ == "__main__":
    main()
