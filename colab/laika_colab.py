#!/usr/bin/env python3
"""Roda células do colab.ipynb num Colab de verdade, sem navegador, com o Colab CLI.

Quem chama é o workflow .github/workflows/colab.yml, que o app Laika dispara pela API do GitHub:

    app --(workflow_dispatch)--> GitHub Actions --(colab CLI)--> máquina do Colab (GPU + Google Drive)

Para cada célula pedida (a 1 sempre roda antes das outras), o código do notebook recebe os
parâmetros (#@param) escolhidos no app e vai para o Colab com "colab exec". O andamento aparece
no app por uma verificação do GitHub ("check run") chamada "Laika no Colab". No fim, o zip da
célula 6 (se ela rodou) é baixado para virar um artefato, e a máquina do Colab é desligada.

    python colab/laika_colab.py celulas                  # células e parâmetros do notebook (JSON)
    python colab/laika_colab.py rodar --celulas 3,4,6 --gpu T4 --parametros '{"3": {"MODO": "continuar"}}'
    python colab/laika_colab.py desligar --sessao laika-123

Só usa a biblioteca padrão (roda no Python do próprio runner do GitHub).
"""
import argparse
import ast
import base64
import codecs
import collections
import json
import os
import queue
import re
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Pasta de trabalho da máquina do Colab (os testes trocam por uma pasta local).
CONTENT = os.environ.get("LAIKA_CONTENT", "/content")
MARCA_NAVEGADOR = "[só no navegador]"
GPUS = ["T4", "L4", "G4", "A100", "H100"]
NOME_VERIFICACAO = "Laika no Colab"
WORKFLOW_SINAL = "sinal.yml"
# Os testes encurtam as esperas (colab/teste_laika_colab.py).
ESPERA_AUTORIZACAO = float(os.environ.get("LAIKA_ESPERA_AUTORIZACAO", 8 * 60))  # o drivemount desiste em 10 min
ESPERA = float(os.environ.get("LAIKA_ESPERA_SEG", 30))  # entre consultas, quando a conexão com o Colab cai
SONDA = float(os.environ.get("LAIKA_SONDA_SEG", 600))  # entre testes de "o kernel caiu?"

TITULO = re.compile(r"^#\s*(\d+)\)\s*(.+?)\s*$")
PARAM = re.compile(r"^(?P<nome>[A-Za-z_]\w*)\s*=\s*(?P<valor>.+?)\s*#\s*@param\s*(?P<spec>.*?)\s*$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
SEGREDOS = re.compile(r"(colab-runtime-proxy-token=|access_token=|refresh_token=|ya29\.)[\w.~%/+-]+")


class Falha(Exception):
    """Erro já explicado para o usuário (vai para o app e para o log)."""


def limpar(texto):
    """Tira e-mails e tokens do que vai para o log público do GitHub e para o app."""
    return SEGREDOS.sub(lambda m: m.group(1) + "<oculto>", EMAIL.sub("<e-mail>", texto))


def log(msg):
    print("[laika] " + msg, flush=True)


# ---------------------------------------------------------------------------
# O notebook: células numeradas e parâmetros no formato dos formulários do Colab
# ---------------------------------------------------------------------------

class Parametro:
    def __init__(self, nome, tipo, padrao, opcoes, linha):
        self.nome, self.tipo, self.padrao, self.opcoes, self.linha = nome, tipo, padrao, opcoes, linha

    def json(self):
        d = {"nome": self.nome, "tipo": self.tipo, "padrao": self.padrao}
        if self.opcoes:
            d["opcoes"] = self.opcoes
        return d


class Celula:
    def __init__(self, numero, titulo, descricao, codigo, so_navegador, parametros):
        self.numero, self.titulo, self.descricao = numero, titulo, descricao
        self.codigo, self.so_navegador, self.parametros = codigo, so_navegador, parametros
        # "PRÉ-TREINO (ensina português)..." -> "PRÉ-TREINO"
        self.nome = re.split(r"[:(.\[—]", titulo, maxsplit=1)[0].strip()

    def json(self):
        return {"numero": self.numero, "nome": self.nome, "titulo": self.titulo, "descricao": self.descricao,
                "so_navegador": self.so_navegador, "parametros": [p.json() for p in self.parametros]}


def ler_parametro(m, linha):
    nome, spec = m.group("nome"), m.group("spec")
    padrao = ast.literal_eval(m.group("valor"))
    if spec.startswith("["):
        return Parametro(nome, "opcoes", padrao, list(ast.literal_eval(spec)), linha)
    t = re.search(r'type\s*:\s*"(\w+)"', spec)
    tipo = t.group(1) if t else type(padrao).__name__
    tipo = {"bool": "boolean", "int": "integer", "float": "number", "slider": "number"}.get(tipo, tipo)
    if tipo not in ("string", "integer", "number", "boolean"):
        tipo = "string"
    return Parametro(nome, tipo, padrao, [], linha)


def ler_caderno(caminho):
    """Células de código que começam com "# N) TÍTULO" (as outras são ignoradas)."""
    with open(caminho, encoding="utf-8") as f:
        nb = json.load(f)
    celulas = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        fonte = c.get("source", "")
        codigo = "".join(fonte) if isinstance(fonte, list) else fonte
        linhas = codigo.split("\n")
        m = TITULO.match(linhas[0])
        if not m:
            continue
        titulo = m.group(2)
        so_navegador = MARCA_NAVEGADOR in titulo
        titulo = re.sub(r"\s+", " ", titulo.replace(MARCA_NAVEGADOR, "")).strip()
        descricao = []
        for l in linhas[1:]:
            if not l.startswith("#"):
                break
            descricao.append(re.sub(r"^#\s?", "", l).rstrip())
        params = [ler_parametro(p, i) for i, l in enumerate(linhas) for p in [PARAM.match(l)] if p]
        celulas.append(Celula(int(m.group(1)), titulo, "\n".join(descricao), codigo, so_navegador, params))
    return celulas


def converter(celula, p, valor):
    erro = Falha(f"célula {celula.numero}: valor inválido para {p.nome}: {valor!r}")
    if p.tipo == "boolean":
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str) and valor.strip().lower() in ("true", "false", "sim", "não", "nao", "1", "0"):
            return valor.strip().lower() in ("true", "sim", "1")
        raise erro
    if p.tipo == "integer":
        if isinstance(valor, bool):
            raise erro
        if isinstance(valor, int):
            return valor
        if isinstance(valor, float) and valor.is_integer():
            return int(valor)
        if isinstance(valor, str) and re.fullmatch(r"\s*-?\d+\s*", valor):
            return int(valor)
        raise erro
    if p.tipo == "number":
        if isinstance(valor, bool):
            raise erro
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise erro from None
    if p.tipo == "opcoes":
        for o in p.opcoes:
            if valor == o or str(valor) == str(o):
                return o
        raise Falha(f"célula {celula.numero}: {p.nome} precisa ser um de {p.opcoes}, não {valor!r}")
    if not isinstance(valor, (str, int, float)) or isinstance(valor, bool) or "\n" in str(valor) \
            or "\r" in str(valor):
        raise erro
    return str(valor)


def aplicar_parametros(celula, valores):
    """O código da célula com os valores pedidos no lugar dos padrões (mesma linha do #@param)."""
    linhas = celula.codigo.split("\n")
    por_nome = {p.nome: p for p in celula.parametros}
    for nome, valor in (valores or {}).items():
        p = por_nome.get(nome)
        if p is None:
            raise Falha(f"a célula {celula.numero} não tem o parâmetro {nome}")
        m = PARAM.match(linhas[p.linha])
        linhas[p.linha] = f"{nome} = {converter(celula, p, valor)!r}  #@param {m.group('spec')}"
    codigo = "\n".join(linhas)
    try:
        ast.parse("\n".join("pass" if l.lstrip().startswith(("!", "%")) else l for l in linhas))
    except SyntaxError as e:
        raise Falha(f"célula {celula.numero}: o código ficou inválido ({e})") from None
    return codigo


def escolher_celulas(celulas, pedido, parametros, ramo):
    """Lista de (célula, código) na ordem do notebook. A célula 1 (preparar) sempre vai primeiro."""
    por_numero = {c.numero: c for c in celulas}
    try:
        numeros = {int(x) for x in re.split(r"[,\s]+", pedido.strip()) if x}
    except ValueError:
        raise Falha(f"lista de células inválida: {pedido!r} (use números separados por vírgula)") from None
    if 1 in por_numero:
        numeros.add(1)
    for n in sorted(numeros):
        if n not in por_numero:
            raise Falha(f"o notebook não tem a célula {n}")
        if por_numero[n].so_navegador:
            raise Falha(f"a célula {n} ({por_numero[n].titulo}) só funciona no navegador")
    if not isinstance(parametros, dict):
        raise Falha("os parâmetros precisam ser um objeto JSON, ex.: {\"3\": {\"MODO\": \"continuar\"}}")
    for chave in parametros:
        if not str(chave).isdigit() or int(chave) not in numeros:
            raise Falha(f"parâmetros para a célula {chave}, que não foi pedida")
    escolhidas = []
    for c in celulas:
        if c.numero not in numeros:
            continue
        valores = dict(parametros.get(str(c.numero)) or {})
        if c.numero == 1 and ramo and "RAMO" not in valores and any(p.nome == "RAMO" for p in c.parametros):
            valores["RAMO"] = ramo  # a máquina do Colab usa o mesmo código que o GitHub Actions
        escolhidas.append((c, aplicar_parametros(c, valores)))
    return escolhidas


def montar_execucao(numero, codigo, nonce):
    """Código enviado ao Colab: roda a célula e grava o estado num arquivo da máquina.

    O arquivo (rodando/ok/erro) permite saber como a célula terminou mesmo se a conexão do
    "colab exec" cair no meio de um treino de horas: o kernel continua rodando no Colab.
    """
    nome = f"<célula {numero}>"
    return "\n".join([
        "import os, linecache, base64 as _b64",
        f"os.makedirs({CONTENT + '/.laika'!r}, exist_ok=True)",
        f"if os.path.isdir({CONTENT + '/LLM_Laika'!r}):",
        f"    os.chdir({CONTENT + '/LLM_Laika'!r})",
        "def _laika_estado(estado):",
        f"    with open({CONTENT + f'/.laika/celula_{numero}.txt'!r}, 'w') as _f:",
        f"        _f.write(estado + ' ' + {nonce!r})",
        "_laika_estado('rodando')",
        f"_laika_codigo = get_ipython().transform_cell(_b64.b64decode({base64.b64encode(codigo.encode()).decode()!r}).decode('utf-8'))",
        f"linecache.cache[{nome!r}] = (len(_laika_codigo), None, _laika_codigo.splitlines(True), {nome!r})",
        "try:",
        f"    exec(compile(_laika_codigo, {nome!r}, 'exec'), globals())",
        "except BaseException:",
        "    _laika_estado('erro')",
        "    raise",
        "_laika_estado('ok')",
        f"print('@@LAIKA_OK {numero} {nonce}@@', flush=True)",
        "",
    ])


def remoto(caminho):
    """Caminho para "colab download" (relativo à raiz da máquina do Colab)."""
    return caminho.lstrip("/")


# ---------------------------------------------------------------------------
# O que aparece no app: estado da execução numa verificação ("check run") do GitHub
# ---------------------------------------------------------------------------

class Estado:
    def __init__(self, escolhidas, gpu, ramo):
        self.gpu, self.ramo = gpu, ramo
        self.inicio = time.time()
        self.fase = "ligando"
        self.mensagem = "Ligando a máquina do Colab…"
        self.autorizar = None
        self.pacote = False
        self.celulas = [{"numero": c.numero, "nome": c.nome, "situacao": "na_fila", "inicio": None, "fim": None}
                        for c, _ in escolhidas]
        self.linhas = collections.deque(maxlen=80)

    def celula(self, numero):
        return next(c for c in self.celulas if c["numero"] == numero)

    def titulo(self):
        return self.mensagem[:200]

    def resumo(self):
        icones = {"na_fila": "⏸ na fila", "rodando": "⏳ rodando", "ok": "✅ pronta", "erro": "❌ falhou",
                  "parada": "⏹ parada"}
        agora = time.time()
        md = [f"**{self.mensagem}**", "",
              f"GPU: {self.gpu or 'nenhuma'} · código do ramo `{self.ramo}`", "",
              "| Célula | Situação | Tempo |", "|---|---|---|"]
        for c in self.celulas:
            seg = ((c["fim"] or agora) - c["inicio"]) if c["inicio"] else None
            md.append(f"| {c['numero']}) {c['nome']} | {icones[c['situacao']]} | "
                      f"{'' if seg is None else f'{seg / 60:.0f} min'} |")
        if self.autorizar:
            md += ["", "### O Colab precisa da sua autorização para usar o Google Drive",
                   f"Abra [este link]({self.autorizar}), autorize com a sua conta e toque em "
                   "**Já autorizei** no app (a execução espera alguns minutos)."]
        dados = {"fase": self.fase, "mensagem": self.mensagem, "gpu": self.gpu, "inicio": int(self.inicio),
                 "celulas": self.celulas, "autorizar": self.autorizar, "pacote": self.pacote}
        md += ["", "<!-- laika " + json.dumps(dados, ensure_ascii=False).replace("-->", "--\\u003e") + " -->"]
        return "\n".join(md)

    def texto(self):
        return "```\n" + "\n".join(self.linhas) + "\n```" if self.linhas else ""


class GitHub:
    """Verificação "Laika no Colab" (o app lê) e os avisos do app (workflow sinal.yml)."""

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.repo = os.environ.get("GITHUB_REPOSITORY")
        self.sha = os.environ.get("GITHUB_SHA")
        self.run_id = os.environ.get("GITHUB_RUN_ID")
        self.api = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        self.ativo = all([self.token, self.repo, self.sha, self.run_id])
        self.id = None
        self.ultimo = 0.0
        self.avisou = False

    def _api(self, metodo, caminho, dados=None):
        req = urllib.request.Request(
            self.api + "/repos/" + self.repo + caminho, method=metodo,
            data=None if dados is None else json.dumps(dados).encode(),
            headers={"Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "laika-colab"})
        with urllib.request.urlopen(req, timeout=30) as r:
            corpo = r.read()
            return json.loads(corpo) if corpo else {}

    def _tentar(self, metodo, caminho, dados=None):
        try:
            return self._api(metodo, caminho, dados)
        except (urllib.error.URLError, OSError, ValueError) as e:
            if not self.avisou:
                self.avisou = True
                log(f"aviso: não consegui falar com a API do GitHub ({e}); o app vai ver menos detalhes.")
            return None

    def _saida(self, estado):
        return {"title": estado.titulo(), "summary": estado.resumo()[:65000], "text": estado.texto()[-65000:]}

    def iniciar(self, estado):
        if not self.ativo:
            return
        r = self._tentar("POST", "/check-runs", {
            "name": NOME_VERIFICACAO, "head_sha": self.sha, "status": "in_progress",
            "external_id": str(self.run_id), "output": self._saida(estado)})
        self.id = r.get("id") if r else None
        self.ultimo = time.monotonic()

    def atualizar(self, estado, forcar=False):
        if not self.id or (not forcar and time.monotonic() - self.ultimo < 20):
            return
        self.ultimo = time.monotonic()
        self._tentar("PATCH", f"/check-runs/{self.id}", {"output": self._saida(estado)})

    def terminar(self, estado, conclusao):
        if not self.id:
            return
        self._tentar("PATCH", f"/check-runs/{self.id}", {
            "status": "completed", "conclusion": conclusao, "output": self._saida(estado)})

    def recebeu_sinal(self, nome):
        """O app avisa disparando o workflow sinal.yml com run-name = nome."""
        if not self.ativo:
            return False
        r = self._tentar("GET", f"/actions/workflows/{WORKFLOW_SINAL}/runs?event=workflow_dispatch&per_page=30")
        return bool(r) and any(x.get("display_title") == nome for x in r.get("workflow_runs", []))


# ---------------------------------------------------------------------------
# O Colab CLI
# ---------------------------------------------------------------------------

class Colab:
    def __init__(self, sessao, comando=None):
        self.sessao = sessao
        self.comando = comando or shlex.split(os.environ.get("LAIKA_COLAB_CLI", "colab --auth=adc"))
        self.atual = None  # processo em andamento (para parar se o job for cancelado)

    def _abrir(self, args, entrada=False):
        env = dict(os.environ, PYTHONUNBUFFERED="1", NO_COLOR="1", TERM="dumb")
        self.atual = subprocess.Popen(self.comando + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      stdin=subprocess.PIPE if entrada else subprocess.DEVNULL,
                                      start_new_session=True, env=env)
        return self.atual

    def rodar(self, args, ao_ler=None, ao_esperar=None, entrada=False, limite=None):
        """Roda um comando do CLI entregando as linhas da saída; devolve (código, saída)."""
        p = self._abrir(args, entrada)
        saida = []

        def linha(l):
            saida.append(l)
            if ao_ler:
                ao_ler(l)

        acompanhar(p, linha, ao_esperar, limite)
        self.atual = None
        return p.returncode, saida

    def interromper(self):
        p, self.atual = self.atual, None
        if p and p.poll() is None:
            for sinal_, espera in [(signal.SIGINT, 5), (signal.SIGTERM, 5), (signal.SIGKILL, 5)]:
                try:
                    os.killpg(p.pid, sinal_)
                    p.wait(espera)
                    return
                except subprocess.TimeoutExpired:
                    continue
                except OSError:
                    return

    def executar(self, codigo, limite_seg, ao_ler=None, ao_esperar=None):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(codigo)
        try:
            return self.rodar(["exec", "-s", self.sessao, "-f", f.name, "--timeout", str(int(limite_seg))],
                              ao_ler, ao_esperar, limite=limite_seg + 120)
        finally:
            os.unlink(f.name)

    def ler_arquivo(self, caminho):
        """Conteúdo de um arquivo pequeno da máquina do Colab, ou None se não existir."""
        with tempfile.TemporaryDirectory() as d:
            local = os.path.join(d, "x")
            codigo, _ = self.rodar(["download", "-s", self.sessao, remoto(caminho), local], limite=120)
            if codigo != 0 or not os.path.exists(local):
                return None
            with open(local, encoding="utf-8", errors="replace") as f:
                return f.read()

    def kernel_livre(self):
        """True se o kernel responde na hora (não está ocupado com uma célula)."""
        codigo, saida = self.executar("print('@@LAIKA_LIVRE@@')", 60)
        return any("@@LAIKA_LIVRE@@" in l for l in saida)


def acompanhar(p, ao_ler, ao_esperar=None, limite=None):
    """Lê a saída do processo aos poucos (linhas com \\r viram só o último pedaço, como num terminal)."""
    fila = queue.Queue()

    def ler():
        fd = p.stdout.fileno()
        while True:
            try:
                b = os.read(fd, 65536)
            except OSError:
                b = b""
            fila.put(b)
            if not b:
                return

    threading.Thread(target=ler, daemon=True).start()
    resto = ""
    fim = None if limite is None else time.monotonic() + limite
    decod = codecs.getincrementaldecoder("utf-8")("replace")
    while True:
        try:
            b = fila.get(timeout=1)
        except queue.Empty:
            b = None
        if b:
            resto += decod.decode(b)
            *completas, resto = resto.split("\n")
            for l in completas:
                l = l.rstrip("\r")
                ao_ler(l.rsplit("\r", 1)[-1])
        elif b == b"":
            break
        if ao_esperar:
            ao_esperar()
        if fim is not None and time.monotonic() > fim and p.poll() is None:
            ao_ler("[laika] o comando passou do tempo e foi interrompido")
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
    if resto.strip():
        ao_ler(resto.rsplit("\r", 1)[-1])
    p.wait()


# ---------------------------------------------------------------------------
# A execução
# ---------------------------------------------------------------------------

class Execucao:
    def __init__(self, args, escolhidas):
        self.args = args
        self.escolhidas = escolhidas
        self.gpu = None if args.gpu.lower() in ("", "nenhuma", "cpu", "none") else args.gpu.upper()
        self.estado = Estado(escolhidas, self.gpu, args.ramo)
        self.github = GitHub()
        self.colab = Colab(args.sessao)
        self.prazo = time.monotonic() + args.prazo_min * 60

    # --- saída: log do GitHub Actions + últimas linhas no app ---

    def mostrar(self, linha):
        if linha.startswith("@@LAIKA_"):  # marcas internas (fim da célula, Drive montado)
            return
        linha = limpar(linha)[:400]
        print(linha, flush=True)
        self.estado.linhas.append(linha)
        self.github.atualizar(self.estado)

    def anunciar(self, mensagem, fase=None):
        if fase:
            self.estado.fase = fase
        self.estado.mensagem = mensagem
        log(mensagem)
        self.estado.linhas.append("[laika] " + mensagem)
        self.github.atualizar(self.estado, forcar=True)

    def restante(self):
        return self.prazo - time.monotonic()

    # --- etapas ---

    def ligar(self):
        self.anunciar(f"Ligando a máquina do Colab ({self.gpu or 'sem GPU'})…", "ligando")
        args = ["new", "-s", self.args.sessao] + (["--gpu", self.gpu] if self.gpu else [])
        codigo, saida = self.colab.rodar(args, self.mostrar, limite=15 * 60)
        if codigo != 0 or not any("READY" in l for l in saida):
            texto = " ".join(saida)
            if "rejected accelerator" in texto or "entitlement" in texto:
                raise Falha(f"a sua conta não conseguiu a GPU {self.gpu} pelo Colab CLI. "
                            "Tente outra GPU (ex.: T4) ou sem GPU.")
            if "Allocation refused" in texto or "precondition" in texto:
                raise Falha("o Colab recusou a máquina agora (limite de uso ou de sessões abertas). "
                            "Espere um pouco e tente de novo.")
            if "401" in texto or "403" in texto or "credentials" in texto.lower():
                raise Falha("o Colab não aceitou a permissão guardada no GitHub. Rode a célula 0 do "
                            "colab.ipynb no navegador de novo.")
            raise Falha("não consegui ligar a máquina do Colab (veja o registro)")

    def montar_drive(self):
        """'colab drivemount', repassando ao app o pedido de autorização do Google Drive, se vier.

        O CLI mostra um link e espera um Enter. O link vai para a verificação que o app lê; quando
        o usuário toca em "Já autorizei", o app dispara o workflow sinal.yml e aqui o Enter é enviado
        (ou depois de alguns minutos, de qualquer jeito).
        """
        self.anunciar("Montando o Google Drive…", "drive")
        sinal = f"drive-ok-{self.github.run_id}"
        s = {"pediu": False, "url": None, "desde": None, "consulta": 0.0, "enviado": False}

        def ao_ler(l):
            if "Authorization needed" in l:
                s["pediu"] = True
            if s["pediu"] and s["url"] is None and l.strip().startswith("http"):
                s["url"] = sem_dados_pessoais(l.strip())
                l = "(link de autorização do Google Drive: veja no app)"
            self.mostrar(l)

        def ao_esperar():
            p = self.colab.atual
            if s["url"] and s["desde"] is None:
                s["desde"] = time.monotonic()
                self.estado.autorizar = s["url"]
                self.anunciar("O Colab precisa da sua autorização para usar o Google Drive", "autorizar")
                if not self.github.id:  # sem a verificação no app, o link fica só no registro
                    print("Link para autorizar o Google Drive:", s["url"], flush=True)
            if s["desde"] is None or s["enviado"] or p is None:
                return
            agora = time.monotonic()
            pronto = agora - s["desde"] > ESPERA_AUTORIZACAO
            if not pronto and agora - s["consulta"] >= 10:
                s["consulta"] = agora
                pronto = self.github.recebeu_sinal(sinal)
            if pronto:
                s["enviado"] = True
                self.estado.autorizar = None
                self.anunciar("Continuando a montagem do Google Drive…", "drive")
                try:
                    p.stdin.write(b"\n")
                    p.stdin.flush()
                except OSError:
                    pass

        self.colab.rodar(["drivemount", "-s", self.args.sessao], ao_ler, ao_esperar, entrada=True, limite=12 * 60)
        self.estado.autorizar = None
        # O CLI pode desistir antes do Drive terminar de montar: confere direto na máquina.
        for tentativa in range(4):
            codigo, saida = self.colab.executar(
                f"import os; print('@@LAIKA_DRIVE', os.path.isdir({CONTENT + '/drive/MyDrive'!r}))", 60)
            if any("@@LAIKA_DRIVE True" in l for l in saida):
                self.anunciar("Google Drive montado.")
                return
            time.sleep(min(15, ESPERA))
        raise Falha("o Google Drive não montou. Se apareceu o pedido de autorização, autorize e rode de novo.")

    def rodar_celula(self, celula, codigo):
        info = self.estado.celula(celula.numero)
        info["situacao"], info["inicio"] = "rodando", int(time.time())
        total = len(self.escolhidas)
        pos = next(i for i, (c, _) in enumerate(self.escolhidas) if c is celula) + 1
        self.anunciar(f"Célula {celula.numero} ({pos}/{total}): {celula.nome}", "celula")
        nonce = secrets.token_hex(4)
        limite = self.restante() - 30
        if limite < 30:
            raise Falha("acabou o tempo desta execução (o GitHub Actions para em 6 horas)")
        _, saida = self.colab.executar(montar_execucao(celula.numero, codigo, nonce), limite, self.mostrar,
                                       lambda: self.github.atualizar(self.estado))
        ok = any(f"@@LAIKA_OK {celula.numero} {nonce}@@" in l for l in saida) or self.conferir(celula, nonce)
        info["situacao"], info["fim"] = ("ok" if ok else "erro"), int(time.time())
        if not ok:
            raise Falha(f"a célula {celula.numero} ({celula.nome}) deu erro (veja o registro)")

    def conferir(self, celula, nonce):
        """Sem a marca de "pronto" na saída: vê no arquivo de estado como a célula terminou."""
        arquivo = f"{CONTENT}/.laika/celula_{celula.numero}.txt"
        estado = (self.colab.ler_arquivo(arquivo) or "").strip()
        if estado == f"ok {nonce}":
            return True
        if estado != f"rodando {nonce}":
            return False  # deu erro, ou o código nem chegou a rodar
        self.anunciar(f"A conexão com o Colab caiu; a célula {celula.numero} continua rodando lá. Esperando…")
        ultima_sonda = time.monotonic()
        while self.restante() > 90:
            time.sleep(ESPERA)
            self.github.atualizar(self.estado)
            estado = (self.colab.ler_arquivo(arquivo) or "").strip()
            if estado == f"ok {nonce}":
                return True
            if estado != f"rodando {nonce}":
                return False
            if time.monotonic() - ultima_sonda > SONDA:
                ultima_sonda = time.monotonic()
                if self.colab.kernel_livre():
                    # o kernel está livre mas a célula não terminou: ele caiu (ex.: falta de memória)
                    estado = (self.colab.ler_arquivo(arquivo) or "").strip()
                    return estado == f"ok {nonce}"
        return False

    def baixar_pacote(self):
        self.anunciar("Baixando o zip para o app…", "baixando")
        os.makedirs(self.args.saida, exist_ok=True)
        local = os.path.join(self.args.saida, "laika_pacote.zip")
        codigo, _ = self.colab.rodar(["download", "-s", self.args.sessao, remoto(CONTENT + "/laika_pacote.zip"),
                                      local], self.mostrar, limite=60 * 60)
        if codigo != 0 or not os.path.exists(local):
            log("aviso: não consegui baixar o zip; ele continua no Google Drive (LLM_Laika/laika_pacote.zip).")
            return
        destino = os.path.join(self.args.saida, "pacote")
        shutil.rmtree(destino, ignore_errors=True)
        with zipfile.ZipFile(local) as z:
            for nome in z.namelist():
                partes = nome.replace("\\", "/").split("/")
                if nome.endswith("/") or nome.startswith("/") or ".." in partes:
                    continue
                alvo = os.path.join(destino, *partes)
                os.makedirs(os.path.dirname(alvo), exist_ok=True)
                with z.open(nome) as de, open(alvo, "wb") as para:
                    shutil.copyfileobj(de, para, 1 << 20)
        os.unlink(local)
        tamanho = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(destino) for f in fs)
        self.estado.pacote = True
        self.anunciar(f"Zip pronto para o app ({tamanho / 2**20:.0f} MB).")

    def desligar(self):
        self.colab.interromper()
        self.colab.rodar(["stop", "-s", self.args.sessao], self.mostrar, limite=180)

    def rodar(self):
        self.github.iniciar(self.estado)
        conclusao, erro = "failure", None
        try:
            self.ligar()
            self.montar_drive()
            for celula, codigo in self.escolhidas:
                self.rodar_celula(celula, codigo)
            if any(c.numero == 6 for c, _ in self.escolhidas):
                self.baixar_pacote()
            conclusao = "success"
            self.estado.mensagem = "Pronto: todas as células rodaram." + (
                " O zip está em Modelos prontos no app." if self.estado.pacote else "")
        except Falha as e:
            erro = str(e)
        except KeyboardInterrupt:
            conclusao, erro = "cancelled", "execução cancelada"
        except Exception as e:  # erro inesperado: aparece no app em vez de sumir
            erro = f"erro inesperado: {e!r}"
        finally:
            for c in self.estado.celulas:
                if c["situacao"] in ("na_fila", "rodando"):
                    c["situacao"] = "parada"
                    c["fim"] = c["fim"] or (int(time.time()) if c["inicio"] else None)
            if erro:
                self.estado.mensagem = ("Cancelado" if conclusao == "cancelled" else "Falhou: ") + (
                    "" if conclusao == "cancelled" else erro)
            self.estado.fase = "fim"
            log(self.estado.mensagem)
            try:
                self.desligar()
            except BaseException:
                pass
            self.github.terminar(self.estado, conclusao)
            resumo = os.environ.get("GITHUB_STEP_SUMMARY")
            if resumo:
                with open(resumo, "a", encoding="utf-8") as f:
                    f.write(self.estado.resumo() + "\n")
        return 0 if conclusao == "success" else 1


def sem_dados_pessoais(url):
    """O link de autorização sem o e-mail da conta (o usuário escolhe a conta na hora)."""
    try:
        u = urllib.parse.urlsplit(url)
        q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True)
             if k not in ("login_hint", "user", "email", "authuser")]
        return urllib.parse.urlunsplit(u._replace(query=urllib.parse.urlencode(q)))
    except ValueError:
        return limpar(url)


def principal(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("comando", choices=["celulas", "rodar", "desligar"])
    ap.add_argument("--caderno", default=os.path.join(RAIZ, "colab.ipynb"))
    ap.add_argument("--celulas", default="")
    ap.add_argument("--gpu", default="T4", help="T4, L4, G4, A100, H100 ou nenhuma")
    ap.add_argument("--parametros", default="{}", help='JSON: {"3": {"MODO": "continuar"}}')
    ap.add_argument("--sessao", default="laika")
    ap.add_argument("--ramo", default=os.environ.get("GITHUB_REF_NAME", "main"))
    ap.add_argument("--saida", default="saida")
    ap.add_argument("--prazo-min", type=float, default=340)
    args = ap.parse_args(argv)

    if args.comando == "celulas":
        print(json.dumps([c.json() for c in ler_caderno(args.caderno)], ensure_ascii=False, indent=1))
        return 0
    if args.comando == "desligar":
        Colab(args.sessao).rodar(["stop", "-s", args.sessao], lambda l: print(limpar(l), flush=True), limite=180)
        return 0

    try:
        if args.gpu.upper() not in GPUS and args.gpu.lower() not in ("", "nenhuma", "cpu", "none"):
            raise Falha(f"GPU desconhecida: {args.gpu} (use {', '.join(GPUS)} ou nenhuma)")
        try:
            parametros = json.loads(args.parametros or "{}")
        except ValueError:
            raise Falha("os parâmetros não são um JSON válido") from None
        escolhidas = escolher_celulas(ler_caderno(args.caderno), args.celulas, parametros, args.ramo)
    except Falha as e:
        log(f"Pedido inválido: {e}")  # antes de ligar qualquer máquina
        g = GitHub()
        estado = Estado([], args.gpu, args.ramo)
        estado.mensagem, estado.fase = f"Pedido inválido: {e}", "fim"
        g.iniciar(estado)
        g.terminar(estado, "failure")
        return 2
    log("Células: " + ", ".join(f"{c.numero}) {c.nome}" for c, _ in escolhidas))
    # O GitHub manda SIGINT e depois SIGTERM ao cancelar: os dois desligam o Colab antes de sair.
    signal.signal(signal.SIGTERM, cancelar)
    return Execucao(args, escolhidas).rodar()


def cancelar(*_):
    raise KeyboardInterrupt


if __name__ == "__main__":
    sys.exit(principal())
