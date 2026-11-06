"""A mini-LLM da HP 50g em PyTorch: decoder-only com pré-normalização (RMSNorm), sem bias, RoPE, atenção
multi-query (1 cabeça de K/V), feed-forward SwiGLU ou ReLU² e embedding compartilhado com a saída.

Com `modelo.qat = True`, o forward simula a quantização da calculadora (treino preparado para a quantização, com
straight-through estimator): pesos int4 em grupos ou int8 por canal, com escala = mantissa × 2^-E; entradas das
matrizes, Q, K e V em int8 com escala em potência de 2 por vetor. As tabelas (exp, SiLU, RoPE) e os arredondamentos
do ponto fixo não são simulados aqui: o simulador.py faz a conta exata, só com inteiros.
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from configs import PONTO_FIXO


def escalas_pesos(w, bits, grupo, mbits, pot2):
    """Escalas dos pesos por grupo: (q, m, E) com w ≈ q × m × 2^-E. q inteiro em ±(2^(bits-1) - 1), m inteiro em
    [1, 2^mbits - 1] (uma por grupo), E inteiro por tensor. Mesma conta do simulador (exportação)."""
    qmax = 2 ** (bits - 1) - 1
    mmax = 2 ** mbits - 1
    linhas, colunas = w.shape
    g = grupo or colunas
    wg = w.reshape(linhas, colunas // g, g)
    esc = (wg.abs().amax(-1) / qmax).clamp_min(1e-10)
    E = torch.floor(torch.log2(mmax / esc.max()))
    m = torch.round(esc * torch.exp2(E)).clamp(1, mmax)
    if pot2:
        m = torch.exp2(torch.round(torch.log2(m))).clamp(max=2 ** (mbits - 1))
    s = (m * torch.exp2(-E)).unsqueeze(-1)
    q = torch.round(wg / s).clamp(-qmax, qmax)
    return q, m, E, s


def quant_peso(w, c):
    """Peso como a calculadora o vê (fake-quant com STE)."""
    q, _, _, s = escalas_pesos(w.float(), c["bits"], c["grupo"], c["mbits"], c["pot2"])
    wq = (q * s).reshape(w.shape).to(w.dtype)
    return w + (wq - w).detach()


def quant_ativacao(x):
    """int8 com escala em potência de 2 por vetor (última dimensão), como o simulador: nunca menor que 2^-frac."""
    amax = x.detach().float().abs().amax(-1, keepdim=True).clamp_min(1e-12)
    s = torch.exp2(torch.ceil(torch.log2(amax / 127))).clamp_min(2.0 ** -PONTO_FIXO["frac"])
    q = torch.round(x.float() / s).clamp(-127, 127) * s
    return x + (q.to(x.dtype) - x).detach()


class RMSNorm(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))

    def forward(self, x):
        xf = x.float()
        return (xf * torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + PONTO_FIXO["eps"]) * self.weight).to(x.dtype)


class Linear(nn.Module):
    """Linear sem bias; com qat, pesos e entrada quantizados."""

    def __init__(self, entrada, saida, cfg, dono):
        super().__init__()
        self.weight = nn.Parameter(torch.empty(saida, entrada))
        self.cfg, self.dono = cfg, [dono]  # dono em lista: não vira submódulo

    def forward(self, x):
        if self.dono[0].qat:
            return F.linear(quant_ativacao(x), quant_peso(self.weight, self.cfg))
        return F.linear(x, self.weight)


def tabelas_rope(n, hd, theta=10000.0):
    inv = 1.0 / (theta ** (torch.arange(0, hd // 2, dtype=torch.float32) * 2 / hd))
    ang = torch.arange(n, dtype=torch.float32)[:, None] * inv[None, :]
    return torch.cos(ang), torch.sin(ang)


def girar(x, cos, sin):
    """RoPE: gira a primeira metade de cada cabeça com a segunda (como no model.py da Laika)."""
    m = x.shape[-1] // 2
    x1, x2 = x[..., :m], x[..., m:]
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], -1)


class Bloco(nn.Module):
    def __init__(self, c, dono):
        super().__init__()
        d, hd = c["d"], c["dim_cabeca"]
        self.c = c
        self.n1 = RMSNorm(d)
        self.wq = Linear(d, c["cabecas_q"] * hd, c, dono)
        self.wk = Linear(d, c["cabecas_kv"] * hd, c, dono)
        self.wv = Linear(d, c["cabecas_kv"] * hd, c, dono)
        self.wo = Linear(c["cabecas_q"] * hd, d, c, dono)
        self.n2 = RMSNorm(d)
        self.w1 = Linear(d, c["ff_dim"], c, dono)
        self.w3 = Linear(d, c["ff_dim"], c, dono) if c["ff"] == "swiglu" else None
        self.w2 = Linear(c["ff_dim"], d, c, dono)
        self.dono = [dono]

    def forward(self, x, cos, sin):
        c, B, T = self.c, x.shape[0], x.shape[1]
        hq, hkv, hd = c["cabecas_q"], c["cabecas_kv"], c["dim_cabeca"]
        h = self.n1(x)
        q = girar(self.wq(h).view(B, T, hq, hd).transpose(1, 2), cos, sin)
        k = girar(self.wk(h).view(B, T, hkv, hd).transpose(1, 2), cos, sin)
        v = self.wv(h).view(B, T, hkv, hd).transpose(1, 2)
        if self.dono[0].qat:  # Q e o cache de K/V em int8 na calculadora
            q, k, v = quant_ativacao(q), quant_ativacao(k), quant_ativacao(v)
        if hkv != hq:
            k = k.repeat_interleave(hq // hkv, dim=1)
            v = v.repeat_interleave(hq // hkv, dim=1)
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        x = x + self.wo(a.transpose(1, 2).reshape(B, T, hq * hd))
        h = self.n2(x)
        if c["ff"] == "swiglu":
            f = F.silu(self.w1(h)) * self.w3(h)
        else:
            f = F.relu(self.w1(h)).square()
        return x + self.w2(f)


class MiniLLM(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.qat = False
        self.emb = nn.Parameter(torch.empty(c["vocab"], c["d"]))
        self.blocos = nn.ModuleList([Bloco(c, self) for _ in range(c["camadas"])])
        self.nf = RMSNorm(c["d"])
        cos, sin = tabelas_rope(c["contexto"], c["dim_cabeca"])
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        # Normal(0; 0,02); as projeções que somam no resíduo (wo e w2) divididas por √(2 × camadas).
        for n, p in self.named_parameters():
            if p.dim() == 2:
                std = 0.02 / math.sqrt(2 * c["camadas"]) if n.endswith(("wo.weight", "w2.weight")) else 0.02
                nn.init.normal_(p, 0.0, std)

    def pesos_emb(self):
        return quant_peso(self.emb, self.c) if self.qat else self.emb

    def forward(self, idx):
        T = idx.shape[1]
        emb = self.pesos_emb()
        x = F.embedding(idx, emb)
        cos, sin = self.rope_cos[:T], self.rope_sin[:T]
        for b in self.blocos:
            x = b(x, cos, sin)
        x = self.nf(x)
        if self.qat:
            x = quant_ativacao(x)
        return F.linear(x, emb)

    def num_params(self):
        return sum(p.numel() for p in self.parameters())

    @torch.no_grad()
    def gerar(self, ids, n, temperatura=0.0, fim=None):
        """Geração simples (sem cache), para amostras durante o treino."""
        ids = list(ids)
        for _ in range(n):
            x = torch.tensor([ids[-self.c["contexto"]:]], device=self.emb.device)
            logits = self(x)[0, -1].float()
            if temperatura <= 0:
                t = int(logits.argmax())
            else:
                t = int(torch.multinomial(torch.softmax(logits / temperatura, -1), 1))
            ids.append(t)
            if fim is not None and t == fim:
                break
        return ids
