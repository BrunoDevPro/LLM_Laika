"""Testes do laika_colab.py com um Colab CLI falso e uma API do GitHub falsa.

    python colab/teste_laika_colab.py

O "colab" falso guarda um kernel Python de verdade num processo separado (o estado continua entre
um "exec" e outro, como no Colab), simula a queda da conexão, o kernel que reinicia, o pedido de
autorização do Google Drive e a GPU recusada. A API falsa do GitHub faz o papel do app.
"""
import http.server
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import laika_colab as lc  # noqa: E402

KERNEL = r'''
import io, json, os, queue, socket, subprocess, sys, threading, traceback
ns = {"__name__": "__main__"}

class IPythonFalso:
    def transform_cell(self, codigo):
        r = []
        for l in codigo.split("\n"):
            s = l.lstrip()
            r.append(l[:len(l) - len(s)] + f"get_ipython().system({s[1:]!r})" if s.startswith("!") else l)
        return "\n".join(r) + "\n"

    def system(self, comando):
        p = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(p.stdout, end="")

ip = IPythonFalso()
ns["get_ipython"] = lambda: ip

class Saida(io.TextIOBase):
    con = None
    def write(self, s):
        if self.con is not None and s:
            try:
                self.con.sendall(json.dumps({"saida": s}).encode() + b"\n")
            except OSError:
                self.con = None
        return len(s)

saida = Saida()
sys.stdout = sys.stderr = saida
fila = queue.Queue()

def trabalhar():
    while True:
        con, codigo = fila.get()
        saida.con = con
        fim = "ok"
        try:
            exec(compile(codigo, "<kernel>", "exec"), ns)
        except BaseException:
            fim = "erro"
            saida.write(traceback.format_exc())
        if saida.con is not None:
            try:
                con.sendall(json.dumps({"fim": fim}).encode() + b"\n")
            except OSError:
                pass
        saida.con = None
        try:
            con.close()
        except OSError:
            pass

threading.Thread(target=trabalhar, daemon=True).start()
srv = socket.socket(socket.AF_UNIX)
srv.bind(sys.argv[1])
srv.listen()
while True:
    con, _ = srv.accept()
    pedido = json.loads(con.makefile("rb").readline())
    fila.put((con, pedido["codigo"]))
'''

CLI = r'''
import json, os, shutil, signal, socket, subprocess, sys, time
ESTADO, CONTENT = os.environ["FAKE_ESTADO"], os.environ["LAIKA_CONTENT"]
args = [a for a in sys.argv[1:] if not a.startswith("--auth")]
cmd = args[0]
opt = lambda nome, padrao=None: args[args.index(nome) + 1] if nome in args else padrao
sessao = opt("-s")
arq = os.path.join(ESTADO, f"sessao_{sessao}.json")

def registrar(evento):
    with open(os.path.join(ESTADO, "eventos.txt"), "a") as f:
        f.write(evento + "\n")

def novo_kernel():
    sock = os.path.join(ESTADO, f"k_{sessao}_{time.time_ns()}.sock")
    p = subprocess.Popen([sys.executable, os.path.join(ESTADO, "kernel_falso.py"), sock], start_new_session=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if os.path.exists(sock):
            break
        time.sleep(0.05)
    json.dump({"pid": p.pid, "sock": sock}, open(arq, "w"))

def pedir(codigo):
    s = socket.socket(socket.AF_UNIX)
    s.connect(json.load(open(arq))["sock"])
    s.sendall(json.dumps({"codigo": codigo}).encode() + b"\n")
    return s

if cmd == "new":
    registrar(f"new {opt('--gpu')}")
    print(f"[colab] Creating session '{sessao}'...", flush=True)
    if opt("--gpu") and os.environ.get("FAKE_SEM_GPU"):
        print(f"[colab] Backend rejected accelerator '{opt('--gpu')}'. You may not have quota or entitlement "
              "for this accelerator on your account.", file=sys.stderr)
        sys.exit(1)
    novo_kernel()
    print("[colab] Session READY.")
elif cmd == "reiniciar-kernel":  # só do teste: o kernel morre e o Colab sobe outro, vazio
    k = json.load(open(arq))
    os.kill(k["pid"], signal.SIGKILL)
    novo_kernel()
elif cmd == "drivemount":
    registrar("drivemount")
    print(f"[colab] Mounting Google Drive to '/content/drive' on {sessao}...", flush=True)
    queda = os.path.join(ESTADO, "drive_caiu")
    if os.environ.get("FAKE_DRIVE_CAI") and not os.path.exists(queda):  # 1ª vez: o CLI perde a conexão
        open(queda, "w").close()
        print("Traceback (most recent call last):\nRuntimeError: Connection was lost.", file=sys.stderr, flush=True)
        sys.exit(1)
    if os.environ.get("FAKE_DRIVE_AUTH"):
        print("\n[colab] Intercepted Drive Auth Request. Connecting to https://colab.research.google.com...")
        print("\n[colab] REQUIRED: Google Drive Authorization needed.\nPlease visit:\n\n"
              "https://accounts.google.com/o/oauth2/v2/auth?client_id=123&login_hint=ana.silva%40gmail.com"
              "&scope=drive&state=xyz\n", flush=True)
        sys.stdout.write("Press Enter after you have granted access... ")
        sys.stdout.flush()
        registrar("enter" if sys.stdin.readline() == "\n" else "sem-enter")
        print("[colab] Authorizing VM...\n[colab] Credentials propagated. Resuming mount...", flush=True)
    os.makedirs(os.path.join(CONTENT, "drive", "MyDrive"), exist_ok=True)
    print("Mounted at /content/drive", flush=True)
elif cmd == "exec":
    codigo = open(opt("-f"), encoding="utf-8").read()
    limite = float(opt("--timeout", "30"))
    s = pedir(f"import os; os.makedirs({CONTENT!r}, exist_ok=True); os.chdir({CONTENT!r})")
    s.settimeout(3)  # como o CLI de verdade: se o kernel está ocupado, o preâmbulo estoura o tempo
    try:
        while b'"fim"' not in s.recv(65536):
            pass
    except socket.timeout:
        print("TimeoutError: Timeout waiting for output", file=sys.stderr)
        sys.exit(1)
    cair = next((f for n in range(10) for f in [os.path.join(ESTADO, f"cair_{n}")]
                 if f"<célula {n}>" in codigo and os.path.exists(f)), None)
    s = pedir(codigo)
    s.settimeout(0.2)
    inicio, buf = time.time(), b""
    while True:
        if cair and time.time() - inicio > 1.0:
            os.unlink(cair)
            registrar("caiu")
            print("WebSocketConnectionClosedException: Connection to remote host was lost.", file=sys.stderr)
            sys.exit(1)
        if time.time() - inicio > limite:
            print("TimeoutError: Timeout waiting for output", file=sys.stderr)
            sys.exit(1)
        try:
            b = s.recv(65536)
        except socket.timeout:
            continue
        if not b:
            break
        buf += b
        while b"\n" in buf:
            linha, buf = buf.split(b"\n", 1)
            m = json.loads(linha)
            if "saida" in m:
                sys.stdout.write(m["saida"])
                sys.stdout.flush()
            if "fim" in m:
                sys.exit(0)  # como o CLI de verdade: sai com 0 mesmo se a célula deu erro
elif cmd == "download":
    origem, local = "/" + args[-2], args[-1]
    if os.path.isfile(origem):
        shutil.copy(origem, local)
        print(f"[colab] Downloaded '{args[-2]}' to '{local}'")
    else:
        print(f"[colab] Download failed: File or directory not found: {args[-2]}")
        sys.exit(1)
elif cmd == "stop":
    registrar("stop")
    if os.path.exists(arq):
        try:
            os.kill(json.load(open(arq))["pid"], signal.SIGKILL)
        except OSError:
            pass
        os.unlink(arq)
        print("[colab] Session terminated.")
    else:
        print(f"[colab] Session '{sessao}' not found.")
'''


def caderno_de_teste():
    def celula(codigo):
        return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                "source": [l + "\n" for l in codigo.strip("\n").split("\n")]}

    return {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Teste\n"]},
        celula('''
# 1) PREPARAR: atalhos
RAMO = "main"  #@param {type:"string"}
import os, subprocess
CONTENT = os.environ["LAIKA_CONTENT"]
def rodar(c):
    r = subprocess.run(c, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(r.stdout, end="", flush=True)
    if r.returncode:
        raise RuntimeError("falhou: " + c)
DRIVE = CONTENT + "/drive/MyDrive/LLM_Laika"
os.makedirs(CONTENT + "/LLM_Laika", exist_ok=True)
os.chdir(CONTENT + "/LLM_Laika")
print("preparado no ramo", RAMO)
'''),
        celula('''
# 2) DADOS: com parâmetros
# Uma descrição.
N = 2  #@param {type:"integer"}
FALHAR = False  #@param {type:"boolean"}
for i in range(N):
    print(f"baixando {i}%\\r", end="", flush=True)
print("baixado", N, "| contato ana.silva@gmail.com", flush=True)
rodar("echo comando ok")
if FALHAR:
    raise RuntimeError("falhou de propósito")
'''),
        celula('''
# 3) PRÉ-TREINO (longa)
import time
for i in range(6):
    print("passo", i, flush=True)
    time.sleep(0.4)
print("pasta", os.getcwd(), flush=True)
'''),
        celula('''
# 5) CONVERSAR [só no navegador]
%run chat.py
'''),
        celula('''
# 6) EXPORTAR PARA O CELULAR: teste
MODELO = True  #@param {type:"boolean"}
import zipfile
with zipfile.ZipFile(CONTENT + "/laika_pacote.zip", "w") as z:
    z.writestr("finetuned.pt", b"PK falso")
    z.writestr("tokenizer.json", "{}")
    z.writestr("books/livro.txt", "texto")
print("zip pronto")
'''),
    ]}


class GitHubFalso(http.server.BaseHTTPRequestHandler):
    """Verificações (check runs) e o workflow sinal.yml. Com aprovar=True, faz o papel do app."""
    checks, sinais, aprovar = {}, [], False

    def log_message(self, *a):
        pass

    def _responder(self, dados, codigo=200):
        corpo = json.dumps(dados).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _corpo(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")

    def do_POST(self):
        assert self.headers["Authorization"] == "Bearer token-falso"
        if self.path.endswith("/check-runs"):
            dados = self._corpo()
            dados["id"] = len(self.checks) + 1
            dados["historico"] = [dados["output"]]
            self.checks[dados["id"]] = dados
            return self._responder({"id": dados["id"]}, 201)
        self._responder({}, 404)

    def do_PATCH(self):
        m = re.search(r"/check-runs/(\d+)$", self.path)
        c = self.checks[int(m.group(1))]
        dados = self._corpo()
        c.update({k: v for k, v in dados.items() if k != "output"})
        c["output"] = dados["output"]
        c["historico"].append(dados["output"])
        if self.aprovar and '"autorizar": "https' in dados["output"]["summary"]:
            self.sinais.append("drive-ok-77")
        self._responder({"id": c["id"]})

    def do_GET(self):
        if "/actions/workflows/sinal.yml/runs" in self.path:
            return self._responder({"workflow_runs": [{"display_title": s} for s in self.sinais]})
        self._responder({}, 404)


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def dados_da_verificacao(check):
    m = re.search(r"<!-- laika (.*) -->", check["output"]["summary"])
    return json.loads(m.group(1))


class TesteCaderno(unittest.TestCase):
    def test_notebook_de_verdade(self):
        cel = {c.numero: c for c in lc.ler_caderno(os.path.join(lc.RAIZ, "colab.ipynb"))}
        self.assertEqual(sorted(cel), [0, 1, 2, 3, 4, 5, 6, 7])
        self.assertTrue(cel[0].so_navegador and cel[5].so_navegador)
        self.assertFalse(any(cel[n].so_navegador for n in (1, 2, 3, 4, 6, 7)))
        self.assertEqual([c.nome for c in cel.values()][1:5], ["PREPARAR", "DADOS", "PRÉ-TREINO", "FINE-TUNING"])
        modo = next(p for p in cel[3].parametros if p.nome == "MODO")
        self.assertEqual((modo.tipo, modo.padrao, modo.opcoes), ("opcoes", "pular", ["pular", "continuar", "do_zero"]))
        codigo = lc.aplicar_parametros(cel[3], {"MODO": "continuar", "PASSOS": "500"})
        self.assertIn("MODO = 'continuar'  #@param [\"pular\", \"continuar\", \"do_zero\"]", codigo)
        self.assertIn("PASSOS = 500  #@param", codigo)
        codigo = lc.aplicar_parametros(cel[4], {"EPOCAS": 3, "USAR_RAG": False, "RAG_FRACAO": "0.5"})
        self.assertIn("EPOCAS = 3  #@param", codigo)
        self.assertIn("USAR_RAG = False  #@param", codigo)
        self.assertIn("RAG_FRACAO = 0.5  #@param", codigo)
        for errado in [{"MODO": "xyz"}, {"PASSOS": "dois"}, {"NAO_EXISTE": 1}, {"PASSOS": True}]:
            with self.assertRaises(lc.Falha):
                lc.aplicar_parametros(cel[3], errado)
        with self.assertRaises(lc.Falha):
            lc.aplicar_parametros(cel[1], {"RAMO": "main\nimport os"})

    def test_escolher(self):
        cels = lc.ler_caderno(os.path.join(lc.RAIZ, "colab.ipynb"))
        r = lc.escolher_celulas(cels, "6, 3", {"3": {"MODO": "do_zero"}}, "meu-ramo")
        self.assertEqual([c.numero for c, _ in r], [1, 3, 6])
        self.assertIn("RAMO = 'meu-ramo'", r[0][1])
        self.assertIn("MODO = 'do_zero'", r[1][1])
        for pedido, params in [("5", {}), ("0", {}), ("9", {}), ("x", {}), ("4", {"3": {"MODO": "pular"}})]:
            with self.assertRaises(lc.Falha):
                lc.escolher_celulas(cels, pedido, params, "main")

    def test_execucao_local(self):
        """O código enviado ao Colab grava o estado e marca o fim (e repassa o erro)."""
        with tempfile.TemporaryDirectory() as d:
            antigo, lc.CONTENT = lc.CONTENT, d
            try:
                class IP:
                    def transform_cell(self, c):
                        return c
                ns = {"get_ipython": IP}
                exec(lc.montar_execucao(2, "x = 40 + 2\nprint('valor', x)", "abc"), ns)
                self.assertEqual(ns["x"], 42)  # as variáveis ficam no kernel, para as próximas células
                self.assertEqual(ler(f"{d}/.laika/celula_2.txt"), "ok abc")
                with self.assertRaises(ZeroDivisionError):
                    exec(lc.montar_execucao(3, "y = 1 / 0", "def"), ns)
                self.assertEqual(ler(f"{d}/.laika/celula_3.txt"), "erro def")
            finally:
                lc.CONTENT = antigo

    def test_limpar(self):
        self.assertEqual(lc.limpar("de ana.silva@gmail.com ok"), "de <e-mail> ok")
        self.assertNotIn("segredo", lc.limpar("x?colab-runtime-proxy-token=segredo123&a=1"))
        url = lc.sem_dados_pessoais("https://accounts.google.com/a?client_id=1&login_hint=ana%40gmail.com&state=z")
        self.assertNotIn("login_hint", url)
        self.assertIn("state=z", url)


class TesteDePontaAPonta(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="laika_colab_")
        self.estado = os.path.join(self.dir, "estado")
        self.content = os.path.join(self.dir, "vm", "content")
        os.makedirs(self.estado)
        os.makedirs(self.content)
        with open(os.path.join(self.estado, "kernel_falso.py"), "w") as f:
            f.write(KERNEL)
        with open(os.path.join(self.estado, "colab_falso.py"), "w") as f:
            f.write(CLI)
        self.caderno = os.path.join(self.dir, "caderno.ipynb")
        with open(self.caderno, "w", encoding="utf-8") as f:
            json.dump(caderno_de_teste(), f, ensure_ascii=False)
        GitHubFalso.checks, GitHubFalso.sinais, GitHubFalso.aprovar = {}, [], False
        self.servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), GitHubFalso)
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()

    def tearDown(self):
        subprocess.run([sys.executable, os.path.join(self.estado, "colab_falso.py"), "stop", "-s", "teste"],
                       env=self.env(), capture_output=True)
        self.servidor.shutdown()
        self.servidor.server_close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def env(self, **extra):
        e = dict(os.environ, FAKE_ESTADO=self.estado, LAIKA_CONTENT=self.content,
                 LAIKA_COLAB_CLI=f"{sys.executable} {os.path.join(self.estado, 'colab_falso.py')} --auth=adc",
                 GITHUB_TOKEN="token-falso", GITHUB_REPOSITORY="dono/repo", GITHUB_SHA="abc123", GITHUB_RUN_ID="77",
                 GITHUB_API_URL=f"http://127.0.0.1:{self.servidor.server_address[1]}",
                 GITHUB_STEP_SUMMARY=os.path.join(self.dir, "resumo.md"),
                 LAIKA_ESPERA_SEG="0.3", LAIKA_SONDA_SEG="1", LAIKA_ESPERA_AUTORIZACAO="20")
        e.update(extra)
        return e

    def rodar(self, celulas, parametros="{}", gpu="T4", esperar=True, **extra):
        p = subprocess.Popen([sys.executable, os.path.join(AQUI, "laika_colab.py"), "rodar", "--caderno", self.caderno,
                              "--celulas", celulas, "--gpu", gpu, "--parametros", parametros, "--sessao", "teste",
                              "--ramo", "ramo-x", "--saida", os.path.join(self.dir, "saida"), "--prazo-min", "3"],
                             env=self.env(**extra), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if not esperar:
            return p
        saida, _ = p.communicate(timeout=120)
        return p.returncode, saida

    def eventos(self):
        caminho = os.path.join(self.estado, "eventos.txt")
        return ler(caminho).split("\n") if os.path.exists(caminho) else []

    def check(self):
        self.assertEqual(len(GitHubFalso.checks), 1)
        c = GitHubFalso.checks[1]
        self.assertEqual((c["name"], c["head_sha"], c["external_id"]), ("Laika no Colab", "abc123", "77"))
        return c

    def test_tudo_certo(self):
        codigo, saida = self.rodar("6,2,3", '{"2": {"N": 3}}')
        self.assertEqual(codigo, 0, saida)
        self.assertIn("preparado no ramo ramo-x", saida)  # o ramo do GitHub chega à célula 1
        self.assertIn("baixado 3", saida)
        self.assertIn("comando ok", saida)  # rodar() da célula 1 continua no kernel
        self.assertIn("pasta " + self.content + "/LLM_Laika", saida)
        self.assertNotIn("ana.silva@gmail.com", saida)
        self.assertIn("<e-mail>", saida)
        c = self.check()
        self.assertEqual((c["status"], c["conclusion"]), ("completed", "success"))
        d = dados_da_verificacao(c)
        self.assertEqual([(x["numero"], x["situacao"]) for x in d["celulas"]], [(1, "ok"), (2, "ok"), (3, "ok"), (6, "ok")])
        self.assertTrue(d["pacote"])
        self.assertIn("passo 5", c["output"]["text"])
        pacote = os.path.join(self.dir, "saida", "pacote")
        self.assertEqual(sorted(os.listdir(pacote)), ["books", "finetuned.pt", "tokenizer.json"])
        self.assertEqual(self.eventos()[:2], ["new T4", "drivemount"])
        self.assertIn("stop", self.eventos())
        self.assertIn("| 3) PRÉ-TREINO | ✅ pronta |", ler(os.path.join(self.dir, "resumo.md")))

    def test_celula_com_erro(self):
        codigo, saida = self.rodar("2,3", '{"2": {"FALHAR": true}}')
        self.assertEqual(codigo, 1)
        self.assertIn("falhou de propósito", saida)
        self.assertNotIn("passo 0", saida)  # parou na primeira célula com erro
        c = self.check()
        self.assertEqual(c["conclusion"], "failure")
        d = dados_da_verificacao(c)
        self.assertEqual([x["situacao"] for x in d["celulas"]], ["ok", "erro", "parada"])
        self.assertIn("célula 2 (DADOS) deu erro", c["output"]["title"])
        self.assertIn("stop", self.eventos())

    def test_conexao_cai_e_a_celula_termina(self):
        open(os.path.join(self.estado, "cair_3"), "w").close()
        codigo, saida = self.rodar("3")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("caiu", self.eventos())
        self.assertIn("continua rodando lá", saida)
        self.assertEqual([x["situacao"] for x in dados_da_verificacao(self.check())["celulas"]], ["ok", "ok"])

    def test_kernel_reinicia_no_meio(self):
        open(os.path.join(self.estado, "cair_3"), "w").close()
        p = self.rodar("3", esperar=False)
        for _ in range(200):  # espera a conexão cair e mata o kernel (o Colab sobe outro, vazio)
            if "caiu" in self.eventos():
                break
            time.sleep(0.05)
        subprocess.run([sys.executable, os.path.join(self.estado, "colab_falso.py"), "reiniciar-kernel", "-s", "teste"],
                       env=self.env(), check=True)
        saida, _ = p.communicate(timeout=120)
        self.assertEqual(p.returncode, 1, saida)
        self.assertEqual(dados_da_verificacao(self.check())["celulas"][1]["situacao"], "erro")

    def test_autorizacao_do_drive(self):
        GitHubFalso.aprovar = True
        codigo, saida = self.rodar("2", FAKE_DRIVE_AUTH="1")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("enter", self.eventos())
        self.assertNotIn("accounts.google.com", saida)  # o link só vai para o app
        pedido = [h for h in self.check()["historico"] if '"autorizar": "https' in h["summary"]]
        self.assertTrue(pedido)
        url = re.search(r'"autorizar": "([^"]+)"', pedido[0]["summary"]).group(1)
        self.assertTrue(url.startswith("https://accounts.google.com/") and "state=xyz" in url)
        self.assertNotIn("login_hint", url)
        self.assertNotIn("gmail", json.dumps(self.check()))

    def test_drive_perde_a_conexao_e_tenta_de_novo(self):
        codigo, saida = self.rodar("2", FAKE_DRIVE_CAI="1")
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.eventos().count("drivemount"), 2)
        self.assertIn("tentando de novo (2/3)", saida)
        self.assertEqual(self.check()["conclusion"], "success")

    def test_gpu_recusada(self):
        codigo, saida = self.rodar("2", gpu="A100", FAKE_SEM_GPU="1")
        self.assertEqual(codigo, 1)
        c = self.check()
        self.assertIn("não conseguiu a GPU A100", c["output"]["title"])
        self.assertEqual([x["situacao"] for x in dados_da_verificacao(c)["celulas"]], ["parada", "parada"])
        self.assertNotIn("drivemount", self.eventos())

    def test_pedido_invalido_nao_liga_o_colab(self):
        codigo, saida = self.rodar("5")
        self.assertEqual(codigo, 2)
        self.assertIn("só funciona no navegador", saida)
        self.assertEqual(self.eventos(), [])
        self.assertIn("Pedido inválido", self.check()["output"]["title"])

    def test_cancelar(self):
        p = self.rodar("3", esperar=False)
        for _ in range(400):
            c = GitHubFalso.checks.get(1)
            if c and "Célula 3" in c["output"]["title"]:
                break
            time.sleep(0.05)
        time.sleep(0.5)
        p.send_signal(signal.SIGTERM)
        saida, _ = p.communicate(timeout=60)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.check()["conclusion"], "cancelled")
        self.assertIn("stop", self.eventos())


if __name__ == "__main__":
    unittest.main(verbosity=2)
