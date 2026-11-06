"""Simulador exato em ponto fixo da mini-LLM da HP 50g (só inteiros, numpy) e exportação dos pesos.

A ideia: o programa em C da calculadora faz exatamente estas contas, então o texto gerado aqui (guloso ou com a
mesma semente) e na 50g tem de ser igual. Tudo em inteiros (int8 nos pesos e entradas, int32/int64 nas somas);
nenhuma conta em ponto flutuante na inferência.

Formato dos números (ver configs.PONTO_FIXO):
  ativações largas   int32 com F = 12 bits de fração (Q12): resíduo, saídas das matrizes, Q/K/V antes do int8
  entradas das matrizes, Q, K, V
                     int8 com um deslocamento sh ≥ 0 por vetor: valor = q × 2^(sh - F)
  pesos              q (int4 ou int8) × m × 2^-E: m é a mantissa do grupo (int4) ou da linha (int8), E é do tensor
  RoPE               cos/sin em int16 Q14 (tabela [posição][dim/2])
  softmax            exp(-x) por tabela (passo 1/32, 512 entradas, Q15); probabilidades em Q15
  SiLU               tabela de -8 a 8 (passo 1/32, Q12); fora disso, 0 ou x
  RMSNorm            soma dos quadrados em int64, raiz quadrada inteira, divisão inteira truncada (como em C)
Deslocamento à direita arredondado: (v + 2^(n-1)) >> n, com >> aritmético (como o GCC no ARM).

Comandos:
  python hp50g/simulador.py exportar --ckpt runs/A/melhor.pt --dados data/hp50g --saida export/A
  python hp50g/simulador.py gerar --pacote export/A --pergunta "Qual é o seu nome?"
  python hp50g/simulador.py relatorio --pacotes export/A export/B
"""

import argparse
import json
import math
import re
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from configs import PONTO_FIXO, cache_bytes, macs_por_token, parametros  # noqa: E402

VERSAO = 1
CAMPOS = ["d", "camadas", "cabecas_q", "cabecas_kv", "dim_cabeca", "ff_dim", "ff_tipo", "vocab", "contexto_calc",
          "bits", "grupo", "mbits", "frac", "frac_rope", "frac_prob", "exp_passo", "exp_n", "silu_passo", "silu_lim",
          "guarda", "eps_q24", "c_inv"]


# ---------- aritmética inteira ----------

def desloca(v, n):
    """v × 2^n com arredondamento (n < 0: (v + 2^(-n-1)) >> -n). v int64; n inteiro ou array de inteiros."""
    v = np.asarray(v, dtype=np.int64)
    n = np.asarray(n, dtype=np.int64)
    if n.ndim == 0:
        n = int(n)
        if n >= 0:
            return v << n
        return (v + (1 << (-n - 1))) >> (-n)
    esq = np.where(n >= 0, n, 0)
    dir_ = np.where(n < 0, -n, 0)
    meio = np.where(dir_ > 0, np.left_shift(np.int64(1), np.maximum(dir_ - 1, 0)), 0)
    return np.where(n >= 0, v << esq, (v + meio) >> dir_)


def div_trunc(a, b):
    """Divisão inteira truncando para zero (como em C)."""
    a = np.asarray(a, dtype=np.int64)
    return np.sign(a) * (np.abs(a) // b)


def quant_vetor(x, F):
    """int32 Q(F) -> (int8, sh): o menor sh ≥ 0 com o maior valor cabendo em ±127."""
    amax = int(np.abs(x).max()) if x.size else 0
    sh = 0
    while ((amax + ((1 << sh) >> 1)) >> sh) > 127:
        sh += 1
    return np.clip(desloca(x, -sh), -127, 127), sh


# ---------- quantização dos pesos (a mesma conta do modelo.escalas_pesos) ----------

def escalas_np(w, bits, grupo, mbits, pot2):
    w = np.asarray(w, dtype=np.float32)
    qmax, mmax = 2 ** (bits - 1) - 1, 2 ** mbits - 1
    linhas, colunas = w.shape
    g = grupo or colunas
    wg = w.reshape(linhas, colunas // g, g)
    esc = np.maximum(np.abs(wg).max(-1) / np.float32(qmax), np.float32(1e-10)).astype(np.float32)
    E = int(np.floor(np.log2(np.float32(mmax) / esc.max())))
    m = np.clip(np.round(esc * np.float32(2.0 ** E)), 1, mmax).astype(np.float32)
    if pot2:
        m = np.minimum(np.exp2(np.round(np.log2(m))), 2 ** (mbits - 1)).astype(np.float32)
    s = (m * np.float32(2.0 ** -E))[..., None]
    q = np.clip(np.round(wg / s), -qmax, qmax).astype(np.int8)
    return {"q": q.reshape(linhas, colunas), "m": m.astype(np.int64), "E": E, "grupo": g}


def tabelas(c, pf):
    F, hd, n = pf["frac"], c["dim_cabeca"], c["contexto_calc"]
    exp = np.array([round(math.exp(-i / 2 ** pf["exp_passo"]) * 2 ** pf["frac_prob"]) for i in range(pf["exp_n"])],
                   dtype=np.int64)
    ns = 2 * pf["silu_lim"] * 2 ** pf["silu_passo"]
    xs = [-pf["silu_lim"] + (i + 0.5) / 2 ** pf["silu_passo"] for i in range(ns)]
    silu = np.array([round(x / (1 + math.exp(-x)) * 2 ** F) for x in xs], dtype=np.int64)
    inv = [1.0 / (10000.0 ** (2 * j / hd)) for j in range(hd // 2)]
    cos = np.array([[round(math.cos(np.float32(p * inv[j])) * 2 ** pf["frac_rope"]) for j in range(hd // 2)]
                    for p in range(n)], dtype=np.int64)
    sin = np.array([[round(math.sin(np.float32(p * inv[j])) * 2 ** pf["frac_rope"]) for j in range(hd // 2)]
                    for p in range(n)], dtype=np.int64)
    return {"exp": exp, "silu": silu, "cos": cos, "sin": sin}


def quantizar(estado, c, pf=PONTO_FIXO):
    """Checkpoint (state_dict) -> pacote inteiro: tensores quantizados, normas em Q12 e tabelas."""
    def np_(t):
        return t.detach().float().cpu().numpy()

    def peso(nome):
        return escalas_np(np_(estado[nome]), c["bits"], c["grupo"], c["mbits"], c["pot2"])

    def norma(nome):
        return np.round(np_(estado[nome]) * 2 ** pf["frac"]).astype(np.int64)

    camadas = []
    for l in range(c["camadas"]):
        p = f"blocos.{l}."
        cam = {"n1": norma(p + "n1.weight"), "wq": peso(p + "wq.weight"), "wk": peso(p + "wk.weight"),
               "wv": peso(p + "wv.weight"), "wo": peso(p + "wo.weight"), "n2": norma(p + "n2.weight"),
               "w1": peso(p + "w1.weight"), "w2": peso(p + "w2.weight")}
        if c["ff"] == "swiglu":
            cam["w3"] = peso(p + "w3.weight")
        camadas.append(cam)
    return {"config": dict(c), "pf": dict(pf), "emb": peso("emb"), "camadas": camadas, "nf": norma("nf.weight"),
            "tabelas": tabelas(c, pf)}


# ---------- arquivo binário (HPLM) ----------

def _campos(pac):
    c, pf = pac["config"], pac["pf"]
    v = dict(c)
    v.update(pf)
    v["ff_tipo"] = 0 if c["ff"] == "swiglu" else 1
    v["eps_q24"] = round(pf["eps"] * 2 ** (2 * pf["frac"]))
    v["c_inv"] = round(2 ** pf["frac"] / math.sqrt(c["dim_cabeca"]))
    return [int(v[k]) for k in CAMPOS]


def _alinhar(f):
    while f.tell() % 4:
        f.write(b"\0")


def _gravar_matriz(f, t, bits, mbits, mapa, nome):
    ini = f.tell()
    linhas, colunas = t["q"].shape
    f.write(struct.pack("<iiii", t["E"], linhas, colunas, t["grupo"]))
    f.write(t["m"].astype("<u1" if mbits <= 8 else "<u2").tobytes())
    _alinhar(f)
    q = t["q"].astype(np.int8).reshape(-1)
    if bits == 4:  # dois por byte: o primeiro no nibble de baixo (complemento de 2 com 4 bits)
        n = (q.astype(np.uint8) & 0x0F)
        if len(n) % 2:
            n = np.append(n, 0)
        f.write((n[0::2] | (n[1::2] << 4)).astype(np.uint8).tobytes())
    else:
        f.write(q.tobytes())
    _alinhar(f)
    mapa.append({"nome": nome, "offset": ini, "bytes": f.tell() - ini, "E": t["E"], "linhas": linhas,
                 "colunas": colunas, "grupo": t["grupo"]})


def _gravar_norma(f, v, mapa, nome):
    ini = f.tell()
    f.write(struct.pack("<i", len(v)) + v.astype("<i4").tobytes())
    mapa.append({"nome": nome, "offset": ini, "bytes": f.tell() - ini})


def gravar(pac, caminho):
    """hplm.bin: 'HPLM', versão, nº de campos, os campos (int32, ordem de CAMPOS); tabelas exp (uint16), SiLU (int32),
    cos e sin (int16); embedding; por camada n1, wq, wk, wv, wo, n2, w1, (w3), w2; nf. Matriz: E, linhas, colunas,
    grupo (int32), mantissas (uint8, ou uint16 com mbits > 8), pesos (int8, ou int4 dois por byte); tudo alinhado a 4.
    Norma: n (int32) e os ganhos em Q12 (int32)."""
    c, mapa = pac["config"], []
    with open(caminho, "wb") as f:
        campos = _campos(pac)
        f.write(b"HPLM" + struct.pack("<ii", VERSAO, len(campos)) + struct.pack(f"<{len(campos)}i", *campos))
        t = pac["tabelas"]
        for nome, dt in (("exp", "<u2"), ("silu", "<i4"), ("cos", "<i2"), ("sin", "<i2")):
            ini = f.tell()
            f.write(t[nome].astype(dt).tobytes())
            _alinhar(f)
            mapa.append({"nome": "tabela_" + nome, "offset": ini, "bytes": f.tell() - ini})
        _gravar_matriz(f, pac["emb"], c["bits"], c["mbits"], mapa, "emb")
        for l, cam in enumerate(pac["camadas"]):
            for k in ("n1", "wq", "wk", "wv", "wo", "n2", "w1", "w3", "w2"):
                if k not in cam:
                    continue
                if k in ("n1", "n2"):
                    _gravar_norma(f, cam[k], mapa, f"{l}.{k}")
                else:
                    _gravar_matriz(f, cam[k], c["bits"], c["mbits"], mapa, f"{l}.{k}")
        _gravar_norma(f, pac["nf"], mapa, "nf")
        total = f.tell()
    return mapa, total


def ler(caminho):
    """hplm.bin -> pacote (o mesmo que gravar recebeu)."""
    b = Path(caminho).read_bytes()
    assert b[:4] == b"HPLM", "não é um arquivo HPLM"
    versao, n = struct.unpack_from("<ii", b, 4)
    assert versao == VERSAO
    v = dict(zip(CAMPOS, struct.unpack_from(f"<{n}i", b, 12)))
    pos = 12 + 4 * n
    c = {k: v[k] for k in ("d", "camadas", "cabecas_q", "cabecas_kv", "dim_cabeca", "ff_dim", "vocab",
                           "contexto_calc", "bits", "grupo", "mbits")}
    c["ff"] = "swiglu" if v["ff_tipo"] == 0 else "relu2"
    c["pot2"] = False
    c["contexto"] = c["contexto_calc"]
    pf = {k: v[k] for k in ("frac", "frac_rope", "frac_prob", "exp_passo", "exp_n", "silu_passo", "silu_lim", "guarda")}
    pf["eps"] = v["eps_q24"] / 2 ** (2 * pf["frac"])

    def tirar(dt, cont):
        nonlocal pos
        a = np.frombuffer(b, dtype=dt, count=cont, offset=pos).astype(np.int64)
        pos += np.dtype(dt).itemsize * cont
        pos += (-pos) % 4
        return a

    ns = 2 * pf["silu_lim"] * 2 ** pf["silu_passo"]
    hd2 = c["dim_cabeca"] // 2
    tab = {"exp": tirar("<u2", pf["exp_n"]), "silu": tirar("<i4", ns),
           "cos": tirar("<i2", c["contexto_calc"] * hd2).reshape(-1, hd2),
           "sin": tirar("<i2", c["contexto_calc"] * hd2).reshape(-1, hd2)}

    def matriz():
        nonlocal pos
        E, linhas, colunas, g = struct.unpack_from("<iiii", b, pos)
        pos += 16
        m = tirar("<u1" if c["mbits"] <= 8 else "<u2", linhas * (colunas // g))
        if c["bits"] == 4:
            nb = (linhas * colunas + 1) // 2
            raw = np.frombuffer(b, dtype=np.uint8, count=nb, offset=pos)
            pos += nb
            pos += (-pos) % 4
            nib = np.empty(nb * 2, dtype=np.int64)
            nib[0::2], nib[1::2] = raw & 0x0F, raw >> 4
            q = np.where(nib >= 8, nib - 16, nib)[:linhas * colunas]
        else:
            q = tirar("<i1", linhas * colunas)
        return {"q": q.reshape(linhas, colunas).astype(np.int8), "m": m.reshape(linhas, colunas // g), "E": E, "grupo": g}

    def norma():
        nonlocal pos
        (k,) = struct.unpack_from("<i", b, pos)
        pos += 4
        return tirar("<i4", k)

    emb = matriz()
    camadas = []
    for _ in range(c["camadas"]):
        cam = {"n1": norma(), "wq": matriz(), "wk": matriz(), "wv": matriz(), "wo": matriz(), "n2": norma(),
               "w1": matriz()}
        if c["ff"] == "swiglu":
            cam["w3"] = matriz()
        cam["w2"] = matriz()
        camadas.append(cam)
    return {"config": c, "pf": pf, "emb": emb, "camadas": camadas, "nf": norma(), "tabelas": tab}


# ---------- inferência só com inteiros ----------

class Simulador:
    def __init__(self, pac):
        self.p = pac
        self.c, self.pf = pac["config"], pac["pf"]
        self.F = self.pf["frac"]
        c = self.c
        self.c_inv = round(2 ** self.F / math.sqrt(c["dim_cabeca"]))
        self.eps = round(self.pf["eps"] * 2 ** (2 * self.F))
        # Pesos em int64 já no formato [linhas][grupos][tamanho do grupo] (só para a conta ser rápida no numpy).
        for t in [pac["emb"]] + [cam[k] for cam in pac["camadas"] for k in cam if k not in ("n1", "n2")]:
            linhas, colunas = t["q"].shape
            t["_q"] = t["q"].astype(np.int64).reshape(linhas, colunas // t["grupo"], t["grupo"])

    def novo_cache(self):
        c = self.c
        n, hkv, hd = c["contexto_calc"], c["cabecas_kv"], c["dim_cabeca"]
        return {"pos": 0, "k": np.zeros((c["camadas"], n, hkv, hd), np.int64), "kx": np.zeros((c["camadas"], n, hkv), np.int64),
                "v": np.zeros((c["camadas"], n, hkv, hd), np.int64), "vx": np.zeros((c["camadas"], n, hkv), np.int64)}

    def matvec(self, t, x8, sh):
        """y (Q12) = W · x, com x = x8 × 2^(sh - F): soma em int64 por grupo, vezes a mantissa, deslocada."""
        inner = (t["_q"] * x8.reshape(t["_q"].shape[1], t["grupo"])).sum(-1)
        return desloca((inner * t["m"]).sum(-1), sh - t["E"])

    def linear(self, t, x):
        x8, sh = quant_vetor(x, self.F)
        return self.matvec(t, x8, sh)

    def rmsnorm(self, x, g):
        ss = int((x * x).sum())
        r = max(1, math.isqrt(ss // len(x) + self.eps))
        return div_trunc(x * g, r)

    def rope(self, x, pos):
        """x: [cabeças][dim] em Q12; gira a primeira metade de cada cabeça com a segunda (tabela Q14)."""
        m = x.shape[-1] // 2
        cos, sin = self.p["tabelas"]["cos"][pos], self.p["tabelas"]["sin"][pos]
        x1, x2 = x[:, :m], x[:, m:]
        fr = -self.pf["frac_rope"]
        return np.concatenate([desloca(x1 * cos - x2 * sin, fr), desloca(x1 * sin + x2 * cos, fr)], -1)

    def silu(self, x):
        F, pf, tab = self.F, self.pf, self.p["tabelas"]["silu"]
        lim = pf["silu_lim"] << F
        idx = np.clip((x + lim) >> (F - pf["silu_passo"]), 0, len(tab) - 1)
        return np.where(x >= lim, x, np.where(x < -lim, 0, tab[idx]))

    def passo(self, token, cache):
        """Processa um token na posição cache['pos'] e devolve os logits (Q12, int64)."""
        c, F, pf, p = self.c, self.F, self.pf, self.p
        pos = cache["pos"]
        if pos >= c["contexto_calc"]:
            raise ValueError("passou do contexto da calculadora")
        hq, hkv, hd = c["cabecas_q"], c["cabecas_kv"], c["dim_cabeca"]
        e = p["emb"]
        x = desloca(e["q"][token].astype(np.int64) * np.repeat(e["m"][token], e["grupo"]), F - e["E"])
        G, tab_exp = pf["guarda"], p["tabelas"]["exp"]
        for l, cam in enumerate(p["camadas"]):
            h = self.rmsnorm(x, cam["n1"])
            h8, shh = quant_vetor(h, F)
            q = self.rope(self.matvec(cam["wq"], h8, shh).reshape(hq, hd), pos)
            k = self.rope(self.matvec(cam["wk"], h8, shh).reshape(hkv, hd), pos)
            v = self.matvec(cam["wv"], h8, shh).reshape(hkv, hd)
            for j in range(hkv):
                cache["k"][l, pos, j], cache["kx"][l, pos, j] = quant_vetor(k[j], F)
                cache["v"][l, pos, j], cache["vx"][l, pos, j] = quant_vetor(v[j], F)
            saida = []
            for i in range(hq):
                j = i // (hq // hkv)
                q8, shq = quant_vetor(q[i], F)
                kc, kx = cache["k"][l, :pos + 1, j], cache["kx"][l, :pos + 1, j]
                s = desloca((kc @ q8) * self.c_inv, shq + kx - 2 * F)
                d = s.max() - s
                idx = d >> (F - pf["exp_passo"])
                ex = np.where(idx < pf["exp_n"], tab_exp[np.minimum(idx, pf["exp_n"] - 1)], 0)
                prob = (ex << pf["frac_prob"]) // ex.sum()
                vc, vx = cache["v"][l, :pos + 1, j], cache["vx"][l, :pos + 1, j]
                termos = desloca(prob[:, None] * vc, (vx - pf["frac_prob"] + G)[:, None])
                saida.append(desloca(termos.sum(0), -G))
            x = x + self.linear(cam["wo"], np.concatenate(saida))
            h = self.rmsnorm(x, cam["n2"])
            h8, shh = quant_vetor(h, F)
            a = self.matvec(cam["w1"], h8, shh)
            if c["ff"] == "swiglu":
                f = desloca(self.silu(a) * self.matvec(cam["w3"], h8, shh), -F)
            else:
                r = np.maximum(a, 0)
                f = desloca(r * r, -F)
            x = x + self.linear(cam["w2"], f)
        cache["pos"] = pos + 1
        return self.linear(p["emb"], self.rmsnorm(x, p["nf"]))


class Aleatorio:
    """Gerador congruencial de 32 bits (o mesmo em C): estado = estado × 1664525 + 1013904223."""

    def __init__(self, semente):
        self.s = semente & 0xFFFFFFFF

    def __call__(self):
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.s >> 8


def escolher(sim, logits, temperatura_q8, topk, rng):
    """Guloso com temperatura 0; senão, amostra entre os topk maiores com exp por tabela (só inteiros)."""
    if temperatura_q8 <= 0:
        return int(np.argmax(logits))
    F, pf, tab = sim.F, sim.pf, sim.p["tabelas"]["exp"]
    ordem = np.argsort(-logits, kind="stable")[:topk]
    d = ((logits[ordem[0]] - logits[ordem]) << 8) // temperatura_q8
    idx = d >> (F - pf["exp_passo"])
    ex = np.where(idx < pf["exp_n"], tab[np.minimum(idx, pf["exp_n"] - 1)], 0)
    r = rng() % int(ex.sum())
    return int(ordem[np.searchsorted(np.cumsum(ex), r, side="right")])


# ---------- tokenizador da calculadora (BPE só com as fusões) ----------

class Tokenizador:
    def __init__(self, caminho_vocab):
        b = Path(caminho_vocab).read_bytes()
        assert b[:4] == b"HPVB"
        nt, nf, ne = struct.unpack_from("<HHH", b, 4)
        pos, self.tokens = 10, []
        for _ in range(nt):
            n = b[pos]
            self.tokens.append(b[pos + 1:pos + 1 + n])
            pos += 1 + n
        self.fusoes = {}
        for r in range(nf):
            a, b2, res = struct.unpack_from("<HHH", b, pos)
            self.fusoes[(a, b2)] = (r, res)
            pos += 6
        self.especiais = list(struct.unpack_from(f"<{ne}H", b, pos))
        nomes = {self.tokens[i].decode(): i for i in self.especiais}
        self.eot, self.user, self.assistant, self.end = (nomes["<|endoftext|>"], nomes["<|user|>"],
                                                        nomes["<|assistant|>"], nomes["<|end|>"])
        self.byte = {t[0]: i for i, t in enumerate(self.tokens) if len(t) == 1 and i not in self.especiais}

    def codificar(self, texto):
        """Pedaços ' ?[^espaço]+' ou '[espaço]+' (bytes); em cada um, junta o par de menor prioridade até não dar mais."""
        ids = []
        for pedaco in re.findall(rb" ?[^\s]+|\s+", texto.encode("utf-8")):
            p = [self.byte[x] for x in pedaco]
            while len(p) > 1:
                melhor = min(((self.fusoes[(p[i], p[i + 1])][0], i) for i in range(len(p) - 1)
                              if (p[i], p[i + 1]) in self.fusoes), default=None)
                if melhor is None:
                    break
                r, i = melhor
                p[i:i + 2] = [self.fusoes[(p[i], p[i + 1])][1]]
            ids += p
        return ids

    def decodificar(self, ids):
        return b"".join(self.tokens[i] for i in ids if i not in self.especiais).decode("utf-8", "replace")

    def prompt(self, pergunta):
        return [self.user] + self.codificar(" " + pergunta.strip() + " ") + [self.assistant]


def responder(sim, tok, pergunta, max_tokens=80, temperatura=0.0, semente=1, topk=40):
    cache, ids = sim.novo_cache(), tok.prompt(pergunta)
    logits = None
    for t in ids:
        logits = sim.passo(t, cache)
    rng, saida = Aleatorio(semente), []
    for _ in range(max_tokens):
        t = escolher(sim, logits, round(temperatura * 256), topk, rng)
        if t in (tok.end, tok.eot) or cache["pos"] >= sim.c["contexto_calc"]:
            break
        saida.append(t)
        logits = sim.passo(t, cache)
    return tok.decodificar(saida)


def perda_simulador(sim, janelas):
    """Perda média (nats/token) dos logits inteiros, convertidos para float só para medir."""
    total, n = 0.0, 0
    for jan in janelas:
        cache = sim.novo_cache()
        for i in range(len(jan) - 1):
            l = sim.passo(int(jan[i]), cache).astype(np.float64) / 2 ** sim.F
            m = l.max()
            total += m + math.log(np.exp(l - m).sum()) - l[int(jan[i + 1])]
            n += 1
    return total / max(1, n)


# ---------- comandos ----------

PERGUNTAS = ["Oi", "Qual é o seu nome?", "Quem é você?", "O que é a Lua?", "Qual é a capital do Brasil?",
             "Me conte uma curiosidade.", "Por que o céu é azul?", "Tchau!"]


def exportar(a):
    import torch
    from modelo import MiniLLM

    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    c = ck["config"]
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    pac = quantizar(ck["modelo"], c)
    mapa, total = gravar(pac, saida / "hplm.bin")
    pac2 = ler(saida / "hplm.bin")
    pares = [(pac["emb"], pac2["emb"])] + [(c1[k], c2[k]) for c1, c2 in zip(pac["camadas"], pac2["camadas"])
                                           for k in c1 if k[0] == "w"]
    iguais = all(np.array_equal(t1["q"], t2["q"]) and np.array_equal(t1["m"], t2["m"]) and t1["E"] == t2["E"]
                 for t1, t2 in pares)
    iguais &= all(np.array_equal(c1[k], c2[k]) for c1, c2 in zip(pac["camadas"], pac2["camadas"]) for k in ("n1", "n2"))
    iguais &= all(np.array_equal(pac["tabelas"][k], pac2["tabelas"][k]) for k in pac["tabelas"])
    assert iguais, "o hplm.bin lido não bate com o que foi gravado"
    dados = Path(a.dados)
    for nome in ("vocab.bin", "tokenizador.json"):
        (saida / nome).write_bytes((dados / nome).read_bytes())
    sim, tok = Simulador(pac2), Tokenizador(saida / "vocab.bin")
    meta = json.loads((dados / "meta.json").read_text(encoding="utf-8"))

    # Conferência do tokenizador da calculadora contra o do Hugging Face.
    from tokenizers import Tokenizer
    hf = Tokenizer.from_file(str(dados / "tokenizador.json"))
    amostras = [l for l in (dados / "dialogos_val.txt").read_text(encoding="utf-8").splitlines()
                if l and l != "<|endoftext|>"][:200]
    tok_ok = sum(tok.codificar(re.sub(r"<\|[a-z]+\|>", "", s)) == hf.encode(re.sub(r"<\|[a-z]+\|>", "", s)).ids
                 for s in amostras)

    # Perdas na mesma validação (janelas do contexto da calculadora): float, QAT (PyTorch) e simulador (inteiros).
    n = c["contexto_calc"]
    rel = {"variante": a.nome or Path(a.ckpt).parent.name, "parametros": parametros(c), "bytes": total,
           "macs_por_token": macs_por_token(c), "cache_bytes": cache_bytes(c), "tokenizador_igual": f"{tok_ok}/{len(amostras)}",
           "perdas": {}, "amostras": []}
    modelo = MiniLLM(c)
    modelo.load_state_dict(ck["modelo"])
    modelo.eval()
    for fonte in ("dialogos", "texto"):
        bin_ = dados / f"{fonte}_val.bin"
        if not bin_.exists():
            continue
        d = np.memmap(bin_, dtype=np.uint16, mode="r")
        k = min(a.janelas, (len(d) - 1) // n)
        if k == 0:
            continue
        jan = np.stack([np.asarray(d[i * n:i * n + n + 1], dtype=np.int64) for i in range(k)])
        x = torch.from_numpy(jan)
        r = {}
        with torch.no_grad():
            for qat in (False, True):
                modelo.qat = qat
                lg = modelo(x[:, :-1])
                r["quant" if qat else "float"] = float(torch.nn.functional.cross_entropy(
                    lg.reshape(-1, lg.shape[-1]), x[:, 1:].reshape(-1)))
        r["simulador"] = perda_simulador(sim, jan)
        cpt = meta["fontes"][fonte]["caracteres_por_token"]
        r["bpc_simulador"] = r["simulador"] / math.log(2) / cpt
        rel["perdas"][fonte] = r
        print(f"{fonte}: perda float {r['float']:.4f} | QAT {r['quant']:.4f} | simulador {r['simulador']:.4f} "
              f"({r['bpc_simulador']:.2f} bits/caractere) em {k} janelas de {n}", flush=True)

    # Amostras lado a lado: PyTorch float (guloso) e simulador (guloso e com semente).
    for pergunta in PERGUNTAS:
        ids = tok.prompt(pergunta)
        modelo.qat = False
        g = modelo.gerar(ids, 60, fim=tok.end)[len(ids):]
        flt = tok.decodificar([t for t in g if t != tok.end])
        rel["amostras"].append({"pergunta": pergunta, "float": flt, "simulador": responder(sim, tok, pergunta, 60),
                                "simulador_t0.8": responder(sim, tok, pergunta, 60, 0.8, semente=7)})
    quant = {"formato": "ver simulador.gravar", "config": c, "ponto_fixo": pac["pf"], "campos": dict(zip(CAMPOS, _campos(pac))),
             "tensores": mapa, "bytes_total": total, "especiais": {"eot": tok.eot, "user": tok.user,
                                                                  "assistant": tok.assistant, "end": tok.end}}
    (saida / "quant.json").write_text(json.dumps(quant, indent=1, ensure_ascii=False), encoding="utf-8")
    (saida / "relatorio.json").write_text(json.dumps(rel, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"hplm.bin: {total:,} bytes ({total / 1024:.0f} KB) | {rel['parametros']:,} parâmetros | "
          f"{rel['macs_por_token']:,} multiplicações-e-somas por token | cache {rel['cache_bytes'] / 1024:.0f} KB | "
          f"tokenizador igual ao do treino em {rel['tokenizador_igual']} amostras")
    for s in rel["amostras"]:
        print(f"  {s['pergunta']}\n    float: {s['float']}\n    simulador: {s['simulador']}\n    t=0,8: {s['simulador_t0.8']}")


def gerar(a):
    pasta = Path(a.pacote)
    sim, tok = Simulador(ler(pasta / "hplm.bin")), Tokenizador(pasta / "vocab.bin")
    print(responder(sim, tok, a.pergunta, a.tokens, a.temperatura, a.semente))


def relatorio(a):
    linhas = ["| Variante | Parâmetros | Bytes | MACs/token | Cache | Fonte | Perda float | Perda QAT | Perda simulador | "
              "Bits/caractere |", "|---|---|---|---|---|---|---|---|---|---|"]
    for p in a.pacotes:
        r = json.loads((Path(p) / "relatorio.json").read_text(encoding="utf-8"))
        for fonte, v in r["perdas"].items():
            linhas.append(f"| {r['variante']} | {r['parametros']:,} | {r['bytes']:,} | {r['macs_por_token']:,} | "
                          f"{r['cache_bytes'] / 1024:.0f} KB | {fonte} | {v['float']:.3f} | {v['quant']:.3f} | "
                          f"{v['simulador']:.3f} | {v['bpc_simulador']:.2f} |")
    texto = "\n".join(linhas)
    print(texto)
    if a.saida:
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exportar")
    e.add_argument("--ckpt", required=True)
    e.add_argument("--dados", default="data/hp50g")
    e.add_argument("--saida", required=True)
    e.add_argument("--nome", default=None)
    e.add_argument("--janelas", type=int, default=40, help="janelas de validação de cada fonte no simulador")
    g = sub.add_parser("gerar")
    g.add_argument("--pacote", required=True)
    g.add_argument("--pergunta", required=True)
    g.add_argument("--tokens", type=int, default=80)
    g.add_argument("--temperatura", type=float, default=0.0)
    g.add_argument("--semente", type=int, default=1)
    r = sub.add_parser("relatorio")
    r.add_argument("--pacotes", nargs="+", required=True)
    r.add_argument("--saida", default=None)
    a = ap.parse_args(argv)
    {"exportar": exportar, "gerar": gerar, "relatorio": relatorio}[a.cmd](a)


if __name__ == "__main__":
    main()
