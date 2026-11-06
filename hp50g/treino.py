"""Treino da mini-LLM da HP 50g (A100/L4 no Colab, ou CPU para testes).

- Dados: os .bin do preparar.py (dialogos e texto), lidos com memmap em pedaços de contexto+1 tokens, numa ordem
  embaralhada fixa e sem repetir até acabar a fonte (a posição de cada fonte vai no checkpoint).
- Mistura: --mistura "dialogos:0.5,texto:0.5" no começo e --mistura-final na fase de queda da taxa.
- Taxa WSD: aquecimento (--aquecimento 1%), constante, queda linear até ~0 nos últimos --queda (20%).
- QAT (simula a quantização da calculadora) na fase de queda; as validações mostram a perda em float e quantizada
  e os bits por caractere. O melhor_float.pt é escolhido pela perda float (antes do QAT) e o melhor.pt pela
  perda quantizada.
- Destilação (opcional): --professor <checkpoint> (mesmo tokenizador) e --alfa (peso da KL com temperatura).
- Checkpoint completo (modelo, otimizador, passo, posição nos dados, sorteios) em ultimo.pt a cada --salvar-min;
  rodar de novo com a mesma --saida continua de onde parou (--do-zero apaga e começa outra vez).

    python hp50g/treino.py --variante A --dados data/hp50g --saida runs/A --tokens 1e9
"""

import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from configs import config, parametros, macs_por_token, cache_bytes  # noqa: E402
from modelo import MiniLLM  # noqa: E402


def argumentos(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variante", default="A")
    ap.add_argument("--ff", choices=["swiglu", "relu2"], help="troca o feed-forward da variante")
    ap.add_argument("--ff-dim", type=int)
    ap.add_argument("--camadas", type=int)
    ap.add_argument("--dados", default="data/hp50g")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--tokens", type=float, default=1e9, help="tokens de treino (uma passada só, se houver)")
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--lote-tokens", type=int, default=131072, help="tokens por passo (~128 mil)")
    ap.add_argument("--micro", type=int, default=0, help="sequências por micro-lote (0 = o lote todo de uma vez)")
    ap.add_argument("--aquecimento", type=float, default=0.01)
    ap.add_argument("--queda", type=float, default=0.2, help="fração final com a taxa caindo até ~0 (e QAT)")
    ap.add_argument("--sem-qat", action="store_true", help="não simula a quantização (comparação)")
    ap.add_argument("--qat-desde", type=float, default=None, help="fração em que o QAT liga (padrão: início da queda)")
    ap.add_argument("--mistura", default="dialogos:0.5,texto:0.5")
    ap.add_argument("--mistura-final", default="dialogos:0.8,texto:0.2")
    ap.add_argument("--professor", default=None, help="checkpoint do professor para a destilação")
    ap.add_argument("--alfa", type=float, default=0.5, help="peso da destilação (KL) na perda")
    ap.add_argument("--temp-dest", type=float, default=1.5)
    ap.add_argument("--avaliar-cada", type=float, default=0.02, help="fração do treino entre validações")
    ap.add_argument("--val-tokens", type=int, default=2_000_000, help="tokens de cada fonte por validação")
    ap.add_argument("--salvar-min", type=float, default=15)
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--do-zero", action="store_true")
    ap.add_argument("--semente", type=int, default=1234)
    ap.add_argument("--parar-em", type=int, default=0, help="para no passo N deixando o ultimo.pt (testes da retomada)")
    return ap.parse_args(argv)


# ---------- dados ----------

class Fonte:
    """Pedaços de contexto+1 tokens de um .bin, numa ordem embaralhada (i -> (a·i + b) mod n) sem repetição até o
    fim da fonte; depois disso, outra ordem (época seguinte)."""

    def __init__(self, caminho, contexto, semente):
        self.dados = np.memmap(caminho, dtype=np.uint16, mode="r")
        self.L = contexto + 1
        self.n = max(1, (len(self.dados) - 1) // contexto)
        self.semente = semente
        self.contador = 0

    def _ordem(self, epoca):
        r = random.Random(self.semente * 1000003 + epoca)
        while True:
            a = r.randrange(1, self.n) if self.n > 1 else 1
            if math.gcd(a, self.n) == 1:
                return a, r.randrange(self.n)

    def proximo(self):
        epoca, i = divmod(self.contador, self.n)
        a, b = self._ordem(epoca)
        self.contador += 1
        ini = ((a * i + b) % self.n) * (self.L - 1)
        x = np.asarray(self.dados[ini:ini + self.L], dtype=np.int64)
        if len(x) < self.L:
            x = np.concatenate([x, np.asarray(self.dados[:self.L - len(x)], dtype=np.int64)])
        return x

    @property
    def epocas(self):
        return self.contador / self.n


def ler_mistura(texto):
    m = {}
    for item in texto.split(","):
        k, _, v = item.partition(":")
        if k.strip():
            m[k.strip()] = float(v or 1)
    s = sum(m.values())
    return {k: v / s for k, v in m.items()}


def janelas_val(caminho, contexto, max_tokens):
    """A validação: pedaços seguidos do começo do .bin de validação (sempre os mesmos)."""
    d = np.memmap(caminho, dtype=np.uint16, mode="r")
    n = min(len(d) - 1, max_tokens) // contexto
    if n == 0:
        return None
    return np.stack([np.asarray(d[i * contexto:i * contexto + contexto + 1], dtype=np.int64) for i in range(n)])


# ---------- treino ----------

def taxa(passo, total, a):
    aq = max(1, int(total * a.aquecimento))
    ini_queda = int(total * (1 - a.queda))
    if passo < aq:
        return a.lr * (passo + 1) / aq
    if passo < ini_queda:
        return a.lr
    return a.lr * max(0.0, (total - passo) / max(1, total - ini_queda))


@torch.no_grad()
def avaliar(modelo, vals, meta, dispositivo, lote=64, amp=None):
    """Perda (nats/token) e bits por caractere de cada fonte de validação."""
    modelo.eval()
    r = {}
    for nome, janelas in vals.items():
        perdas = []
        for i in range(0, len(janelas), lote):
            b = torch.from_numpy(janelas[i:i + lote]).to(dispositivo)
            with torch.autocast(dispositivo.split(":")[0], dtype=torch.bfloat16, enabled=amp is not None):
                logits = modelo(b[:, :-1])
            perdas.append(F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), b[:, 1:].reshape(-1),
                                          reduction="sum").item())
        n = janelas[:, 1:].size
        perda = sum(perdas) / n
        cpt = meta["fontes"][nome]["caracteres_por_token"]
        r[nome] = {"perda": perda, "bpc": perda / math.log(2) / cpt}
    modelo.train()
    return r


def media(r, mistura):
    return sum(r[k]["perda"] * mistura.get(k, 0) for k in r) / max(1e-9, sum(mistura.get(k, 0) for k in r))


def main(argv=None):
    a = argumentos(argv)
    torch.manual_seed(a.semente)
    np.random.seed(a.semente)
    random.seed(a.semente)
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    bf16 = dispositivo == "cuda" and torch.cuda.is_bf16_supported()
    if dispositivo == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    dados, saida = Path(a.dados), Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    meta = json.loads((dados / "meta.json").read_text(encoding="utf-8"))
    c = config(a.variante, ff=a.ff, ff_dim=a.ff_dim, camadas=a.camadas)
    c["vocab"] = meta["vocab"]
    ctx = c["contexto"]
    seqs = max(1, a.lote_tokens // ctx)
    micro = a.micro or seqs
    total = max(1, int(a.tokens // (seqs * ctx)))
    queda = int(total * (1 - a.queda))
    qat_desde = int(total * a.qat_desde) if a.qat_desde is not None else queda
    if a.sem_qat:
        qat_desde = total + 1  # o melhor_float.pt acompanha o treino inteiro (ex.: o professor)
    mistura, mistura_final = ler_mistura(a.mistura), ler_mistura(a.mistura_final)
    fontes = {k: Fonte(dados / f"{k}_treino.bin", ctx, a.semente + i) for i, k in enumerate(sorted(set(mistura) | set(mistura_final)))}
    vals = {k: v for k in fontes if (v := janelas_val(dados / f"{k}_val.bin", ctx, a.val_tokens)) is not None}

    modelo = MiniLLM(c).to(dispositivo)
    rodar = torch.compile(modelo) if a.compile and dispositivo == "cuda" else modelo
    decai = [p for n, p in modelo.named_parameters() if p.dim() >= 2]
    sem = [p for n, p in modelo.named_parameters() if p.dim() < 2]  # normas: sem decaimento de peso
    opt = torch.optim.AdamW([{"params": decai, "weight_decay": 0.1}, {"params": sem, "weight_decay": 0.0}],
                            lr=a.lr, betas=(0.9, 0.95), fused=dispositivo == "cuda")

    professor = None
    if a.professor:
        ck = torch.load(a.professor, map_location=dispositivo, weights_only=False)
        professor = MiniLLM(ck["config"]).to(dispositivo).eval()
        professor.load_state_dict(ck["modelo"])
        for p in professor.parameters():
            p.requires_grad_(False)
        print(f"Professor: {professor.num_params():,} parâmetros ({a.professor})")

    estado = {"passo": 0, "melhor_q": float("inf"), "melhor_f": float("inf"), "historico": []}
    sorteio = np.random.default_rng(a.semente)  # qual fonte cada sequência do lote usa
    ultimo = saida / "ultimo.pt"
    if a.do_zero:
        for f in saida.glob("*.pt"):
            f.unlink()
    if ultimo.exists():
        ck = torch.load(ultimo, map_location=dispositivo, weights_only=False)
        if ck["config"] != c or ck["total"] != total:
            raise SystemExit(f"{ultimo} é de outra configuração ou outro número de passos. Use outra --saida ou --do-zero.")
        modelo.load_state_dict(ck["modelo"])
        opt.load_state_dict(ck["otimizador"])
        estado = ck["estado"]
        for k, f in fontes.items():
            f.contador = ck["fontes"][k]
        torch.set_rng_state(ck["rng_torch"])
        random.setstate(ck["rng_py"])
        np.random.set_state(ck["rng_np"])
        sorteio.bit_generator.state = ck["sorteio"]
        print(f"Continuando do passo {estado['passo']:,} de {total:,}.")

    n = modelo.num_params()
    print(f"Variante {a.variante}: {n:,} parâmetros (conta: {parametros(c):,}), {macs_por_token(c):,} "
          f"multiplicações-e-somas por token, cache {cache_bytes(c) / 1024:.0f} KB | {total:,} passos de "
          f"{seqs} × {ctx} tokens | QAT {'desligado' if a.sem_qat else f'a partir do passo {qat_desde:,}'} | "
          f"{dispositivo}{' bf16' if bf16 else ''}", flush=True)
    for k, f in fontes.items():
        print(f"  {k}: {f.n * ctx:,} tokens de treino; validação {len(vals.get(k, [])) * ctx:,}")

    def salvar(caminho, extra=None):
        tmp = caminho.with_suffix(".tmp")
        torch.save({"modelo": modelo.state_dict(), "config": c, "passo": estado["passo"], **(extra or {})}, tmp)
        os.replace(tmp, caminho)

    def salvar_ultimo():
        tmp = ultimo.with_suffix(".tmp")
        torch.save({"modelo": modelo.state_dict(), "otimizador": opt.state_dict(), "config": c, "total": total,
                    "estado": estado, "fontes": {k: f.contador for k, f in fontes.items()},
                    "rng_torch": torch.get_rng_state(), "rng_py": random.getstate(), "rng_np": np.random.get_state(),
                    "sorteio": sorteio.bit_generator.state}, tmp)
        os.replace(tmp, ultimo)

    avaliar_cada = max(1, int(total * a.avaliar_cada))
    t_salvo, t0, tokens_janela = time.time(), time.time(), 0
    log = open(saida / "log.jsonl", "a", encoding="utf-8")
    amp = torch.bfloat16 if bf16 else None
    modelo.train()
    while estado["passo"] <= total:
        p = estado["passo"]
        if p % avaliar_cada == 0 or p == total:
            modelo.qat = False
            rf = avaliar(modelo, vals, meta, dispositivo, amp=amp)
            modelo.qat = True
            rq = avaliar(modelo, vals, meta, dispositivo, amp=amp)
            mf, mq = media(rf, mistura_final), media(rq, mistura_final)
            reg = {"passo": p, "tokens": p * seqs * ctx, "float": rf, "quant": rq, "perda_f": mf, "perda_q": mq,
                   "epocas": {k: round(f.epocas, 3) for k, f in fontes.items()}, "seg": round(time.time() - t0)}
            estado["historico"].append(reg)
            log.write(json.dumps(reg) + "\n")
            log.flush()
            marcas = ""
            if p < qat_desde and mf < estado["melhor_f"]:
                estado["melhor_f"] = mf
                salvar(saida / "melhor_float.pt", {"perda": mf})
                marcas += " [melhor float]"
            if mq < estado["melhor_q"]:
                estado["melhor_q"] = mq
                salvar(saida / "melhor.pt", {"perda_quant": mq, "perda_float": mf})
                marcas += " [melhor quantizado]"
            detalhe = " | ".join(f"{k} {rf[k]['perda']:.3f}/{rq[k]['perda']:.3f} ({rq[k]['bpc']:.2f} bpc)" for k in rf)
            print(f"passo {p:>6,}/{total:,} | perda float/quant {mf:.4f}/{mq:.4f} | {detalhe}{marcas}", flush=True)
            if p == total:
                break
        modelo.qat = not a.sem_qat and p >= qat_desde
        lr = taxa(p, total, a)
        for g in opt.param_groups:
            g["lr"] = lr
        m = mistura_final if p >= queda else mistura
        nomes = list(m)
        escolha = sorteio.choice(len(nomes), size=seqs, p=[m[k] for k in nomes])
        lote = torch.from_numpy(np.stack([fontes[nomes[i]].proximo() for i in escolha]))
        if dispositivo == "cuda":
            lote = lote.pin_memory().to(dispositivo, non_blocking=True)
        opt.zero_grad(set_to_none=True)
        perda_passo = 0.0
        for i in range(0, seqs, micro):
            b = lote[i:i + micro]
            x, y = b[:, :-1], b[:, 1:]
            with torch.autocast(dispositivo.split(":")[0], dtype=torch.bfloat16, enabled=bf16):
                logits = rodar(x)
                perda = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), y.reshape(-1))
                if professor is not None:
                    with torch.no_grad():
                        lp = professor(x).float()
                    T = a.temp_dest
                    kl = F.kl_div(F.log_softmax(logits.float() / T, -1), F.log_softmax(lp / T, -1),
                                  log_target=True, reduction="batchmean") * T * T / x.shape[1]
                    perda = (1 - a.alfa) * perda + a.alfa * kl
            (perda * len(b) / seqs).backward()
            perda_passo += perda.item() * len(b) / seqs
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        opt.step()
        estado["passo"] += 1
        tokens_janela += seqs * ctx
        if estado["passo"] % 50 == 0:
            dt = time.time() - t0
            print(f"passo {estado['passo']:>6,} | perda {perda_passo:.4f} | taxa {lr:.2e} | qat {int(modelo.qat)} | "
                  f"{tokens_janela / max(1e-9, dt):,.0f} tokens/s", flush=True)
            t0, tokens_janela = time.time(), 0
        if time.time() - t_salvo > a.salvar_min * 60:
            salvar_ultimo()
            t_salvo = time.time()
        if a.parar_em and estado["passo"] == a.parar_em:
            salvar_ultimo()
            print(f"Parado no passo {estado['passo']} (--parar-em); rode de novo para continuar.")
            return
    modelo.qat = False
    salvar(saida / "final.pt")
    if ultimo.exists():
        ultimo.unlink()
    resumo = {"variante": a.variante, "config": c, "parametros": n, "tokens": total * seqs * ctx,
              "melhor_perda_quant": estado["melhor_q"], "melhor_perda_float": estado["melhor_f"],
              "ultima": estado["historico"][-1] if estado["historico"] else None}
    (saida / "resumo.json").write_text(json.dumps(resumo, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Fim. Melhor perda quantizada {estado['melhor_q']:.4f} (float {estado['melhor_f']:.4f}) -> {saida}/melhor.pt")


if __name__ == "__main__":
    main()
