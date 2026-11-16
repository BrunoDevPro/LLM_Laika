"""Teste ponta a ponta da mini-LLM da HP 50g em CPU (variante "teste", dados de data/qa e data/modern):
preparar -> treinar (com uma interrupção e retomada) -> exportar -> simulador.

    python hp50g/teste_hp50g.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))

import simulador as S  # noqa: E402
from configs import config, parametros  # noqa: E402
from modelo import MiniLLM  # noqa: E402


def rodar(*args):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=RAIZ)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-3000:] + r.stderr[-3000:])
    return r.stdout


class TesteHP50g(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="hp50g_"))
        cls.dados = cls.dir / "dados"
        rodar(AQUI / "preparar.py", "--saida", cls.dados, "--sft", "", "--texto", RAIZ / "data/modern",
              "--amostra-mb", "10")
        comum = ["--variante", "teste", "--dados", cls.dados, "--tokens", "6e5", "--lote-tokens", "4096",
                 "--avaliar-cada", "0.25", "--val-tokens", "8000"]
        cls.saida_corrido = rodar(AQUI / "treino.py", *comum, "--saida", cls.dir / "corrido")
        cls.parte1 = rodar(AQUI / "treino.py", *comum, "--saida", cls.dir / "retomado", "--parar-em", "70")
        cls.parte2 = rodar(AQUI / "treino.py", *comum, "--saida", cls.dir / "retomado")
        cls.export = rodar(AQUI / "simulador.py", "exportar", "--ckpt", cls.dir / "corrido/melhor.pt", "--dados",
                           cls.dados, "--saida", cls.dir / "export", "--janelas", "6")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_contas_dos_tamanhos(self):
        for v in ("A", "B", "A_relu2", "B_relu2", "teste"):
            c = config(v)
            self.assertEqual(MiniLLM(c).num_params(), parametros(c), v)
        self.assertLess(parametros(config("A")) / 2 * 1.07, 700_000)  # int4 + mantissas cabe em ~700 KB

    def test_dados(self):
        meta = json.loads((self.dados / "meta.json").read_text())
        self.assertEqual(meta["vocab"], 1024)
        self.assertGreater(meta["fontes"]["dialogos"]["treino"]["tokens"], 100_000)
        self.assertGreater(meta["fontes"]["dialogos"]["caracteres_por_token"], 1.5)

    def test_retomada_igual_ao_treino_sem_parar(self):
        self.assertIn("Parado no passo 70", self.parte1)
        self.assertIn("Continuando do passo 70", self.parte2)
        a = json.loads((self.dir / "corrido/resumo.json").read_text())
        b = json.loads((self.dir / "retomado/resumo.json").read_text())
        self.assertAlmostEqual(a["melhor_perda_quant"], b["melhor_perda_quant"], places=5)
        self.assertFalse((self.dir / "retomado/ultimo.pt").exists())

    def test_qat_e_simulador(self):
        rel = json.loads((self.dir / "export/relatorio.json").read_text())
        d = rel["perdas"]["dialogos"]
        # O simulador (só inteiros) fica perto da perda quantizada do PyTorch.
        self.assertLess(abs(d["simulador"] - d["quant"]), 0.05, d)
        self.assertEqual(rel["tokenizador_igual"].split("/")[0], rel["tokenizador_igual"].split("/")[1])

    def test_binario_e_deterministico(self):
        pasta = self.dir / "export"
        pac = S.ler(pasta / "hplm.bin")
        self.assertEqual(pasta.joinpath("hplm.bin").stat().st_size, json.loads((pasta / "quant.json").read_text())["bytes_total"])
        sim, tok = S.Simulador(pac), S.Tokenizador(pasta / "vocab.bin")
        r1 = S.responder(sim, tok, "Qual é o seu nome?", 20, 0.8, semente=3)
        r2 = S.responder(sim, tok, "Qual é o seu nome?", 20, 0.8, semente=3)
        self.assertEqual(r1, r2)
        self.assertEqual(S.responder(sim, tok, "Oi", 20), S.responder(sim, tok, "Oi", 20))
        # Os logits do simulador são inteiros e acompanham os do PyTorch quantizado.
        ck = torch.load(self.dir / "corrido/melhor.pt", weights_only=False)
        m = MiniLLM(ck["config"])
        m.load_state_dict(ck["modelo"])
        m.qat = True
        ids = tok.prompt("O que é a Lua?")
        with torch.no_grad():
            ref = m(torch.tensor([ids]))[0].numpy()
        cache = sim.novo_cache()
        for i, t in enumerate(ids):
            lg = sim.passo(t, cache)
            self.assertEqual(lg.dtype, np.int64)
            corr = np.corrcoef(lg / 4096, ref[i])[0, 1]
            self.assertGreater(corr, 0.98, f"posição {i}: correlação {corr:.3f}")

    def test_aritmetica(self):
        self.assertEqual(int(S.desloca(5, -1)), 3)      # 2,5 -> 3
        self.assertEqual(int(S.desloca(-5, -1)), -2)    # -2,5 -> -2 (soma metade e desloca, como em C)
        self.assertEqual(int(S.desloca(3, 2)), 12)
        self.assertEqual(list(S.div_trunc(np.array([-7, 7]), 2)), [-3, 3])
        q, sh = S.quant_vetor(np.array([4096 * 3, -4096]), 12)
        self.assertLessEqual(int(np.abs(q).max()), 127)
        self.assertAlmostEqual(float(q[0]) * 2 ** (sh - 12), 3.0, delta=0.05)


class TesteMoE(unittest.TestCase):
    """O MoE (variante teste_moe): dados normalizados com o tokenizador reaproveitado, perda só nas respostas na queda,
    hplm.bin versão 2, simulador perto do QAT e os vetores de teste para o C."""

    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="hp50g_moe_"))
        base, cls.dados = cls.dir / "base", cls.dir / "dados_moe"
        rodar(AQUI / "preparar.py", "--saida", base, "--sft", "", "--texto", RAIZ / "data/modern", "--amostra-mb", "10")
        (cls.dir / "fatos.txt").write_text("Qual é a cor do céu?|O céu é azul.\n", encoding="utf-8")
        rodar(AQUI / "preparar.py", "--saida", cls.dados, "--sft", "", "--texto-de", base, "--usar-tokenizador",
              base / "tokenizador.json", "--normalizar", "0.7", "--resposta-curta", "60", "--max-trocas", "1",
              "--decorar", cls.dir / "fatos.txt")
        cls.base = base
        cls.treino = rodar(AQUI / "treino.py", "--variante", "teste_moe", "--dados", cls.dados, "--saida", cls.dir / "r",
                           "--tokens", "6e5", "--lote-tokens", "4096", "--avaliar-cada", "0.25", "--val-tokens", "8000")
        rodar(AQUI / "simulador.py", "exportar", "--ckpt", cls.dir / "r/melhor.pt", "--dados", cls.dados, "--saida",
              cls.dir / "export", "--janelas", "6", "--vetores", "12")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_dados(self):
        from preparar import como_na_calculadora
        self.assertEqual(como_na_calculadora("Qual é a capital do Brasil? Ação!"), "Qual e a capital do brasil? acao!")
        self.assertEqual((self.base / "vocab.bin").read_bytes(), (self.dados / "vocab.bin").read_bytes())
        ids = np.fromfile(self.dados / "dialogos_val.bin", np.uint16)
        m = np.fromfile(self.dados / "dialogos_val.mask", np.uint8)
        self.assertEqual(len(ids), len(m))
        self.assertTrue(0 < m.sum() < len(m))
        self.assertIn("Qual e a cor do ceu?", (self.dados / "dialogos_treino.txt").read_text(encoding="utf-8"))

    def test_treino(self):
        self.assertIn("especialistas (%) por camada", self.treino)
        log = [json.loads(l) for l in (self.dir / "r/log.jsonl").read_text().splitlines()]
        self.assertEqual(len(log[-1]["especialistas"]), 2)

    def test_binario_v2(self):
        pasta = self.dir / "export"
        b = (pasta / "hplm.bin").read_bytes()
        self.assertEqual(b[:4], b"HPLM")
        self.assertEqual(int.from_bytes(b[4:8], "little"), 2)
        pac = S.ler(pasta / "hplm.bin")
        self.assertEqual(pac["camadas"][0]["router"]["bits"], 8)
        self.assertEqual(pac["camadas"][0]["router"]["grupo"], pac["config"]["d"])
        nomes = [t["nome"] for t in json.loads((pasta / "quant.json").read_text())["tensores"]]
        self.assertLess(nomes.index("nf"), nomes.index("0.e0.w1"))  # sempre ativos primeiro, especialistas no fim
        self.assertIn("1.router", nomes)

    def test_simulador_e_vetores(self):
        pasta = self.dir / "export"
        rel = json.loads((pasta / "relatorio.json").read_text())
        d = rel["perdas"]["dialogos"]
        self.assertLess(abs(d["simulador"] - d["quant"]), 0.05, d)
        self.assertEqual(len(rel["uso_especialistas_simulador"]), 2)
        vet = json.loads((pasta / "vetores_teste.json").read_text())["casos"]
        self.assertEqual(len(vet), 12)
        sim, tok = S.Simulador(S.ler(pasta / "hplm.bin")), S.Tokenizador(pasta / "vocab.bin")
        caso = vet[3]
        self.assertEqual(caso["prompt"], tok.prompt(caso["pergunta"]))
        cache = sim.novo_cache()
        for t in caso["prompt"]:
            lg = sim.passo(t, cache)
        self.assertEqual([int(v) for v in lg], caso["logits"])  # determinístico, bit a bit
        self.assertEqual(len(caso["rotas"]), len(caso["prompt"]))
        self.assertEqual(len(caso["rotas"][0]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
