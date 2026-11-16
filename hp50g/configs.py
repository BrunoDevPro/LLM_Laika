"""Tamanhos da mini-LLM da HP 50g. Tudo é parametrizado: depois das medições na calculadora, ajuste aqui.

Campos:
  d, camadas            dimensão do modelo e número de blocos
  cabecas_q, cabecas_kv cabeças de Q e de K/V (1 em K/V = multi-query: é o que faz o cache caber na RAM)
  dim_cabeca            dimensão de cada cabeça (cabecas_q × dim_cabeca = d)
  ff, ff_dim            "swiglu" (silu(W1 x) · W3 x, depois W2) ou "relu2" (relu(W1 x)², depois W2)
  vocab                 tamanho do vocabulário (BPE de bytes)
  contexto              janela no treino; contexto_calc: janela na calculadora (tabela de RoPE e cache)
  bits, grupo           pesos: int4 em grupos de 32 (escala por grupo) ou int8 com grupo 0 = uma escala por linha
                        (canal de saída)
  mbits                 bits da mantissa de cada escala (escala = mantissa × 2^-E, E por tensor)
  pot2                  escalas dos pesos em potências de 2 (viram deslocamentos no ARM)
  n_esp, top_k          mistura de especialistas (MoE): n_esp especialistas roteados por camada, top_k = 1
                        (0 = modelo denso, com o feed-forward ff/ff_dim)
  ff_comp, ff_esp       no MoE: oculto do especialista compartilhado (sempre ativo) e de cada roteado (SwiGLU)
  treino                padrões do treino.py para a variante (o que for passado na linha de comando vale mais)
"""

VARIANTES = {
    # Principal: ~1,19M de parâmetros, pesos int4 em grupos de 32 (~630 KB com as escalas).
    "A": dict(d=128, camadas=6, cabecas_q=4, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=352, vocab=1024,
              contexto=256, contexto_calc=128, bits=4, grupo=32, mbits=8, pot2=False),
    "A_relu2": dict(d=128, camadas=6, cabecas_q=4, cabecas_kv=1, dim_cabeca=32, ff="relu2", ff_dim=512, vocab=1024,
                    contexto=256, contexto_calc=128, bits=4, grupo=32, mbits=8, pot2=False),
    # Mais segura: ~590k parâmetros, pesos int8 por canal de saída (~600 KB).
    "B": dict(d=96, camadas=5, cabecas_q=3, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=256, vocab=1024,
              contexto=256, contexto_calc=128, bits=8, grupo=0, mbits=8, pot2=False),
    "B_relu2": dict(d=96, camadas=5, cabecas_q=3, cabecas_kv=1, dim_cabeca=32, ff="relu2", ff_dim=384, vocab=1024,
                    contexto=256, contexto_calc=128, bits=8, grupo=0, mbits=8, pot2=False),
    # Professor para a destilação (~23M): mesmo tokenizador; nunca vai para a calculadora.
    "professor": dict(d=512, camadas=8, cabecas_q=8, cabecas_kv=2, dim_cabeca=64, ff="swiglu", ff_dim=1408, vocab=1024,
                      contexto=256, contexto_calc=256, bits=8, grupo=0, mbits=8, pot2=False),
    # Mistura de especialistas (MoE, especificação "Laika MoE para a HP 50g"): ~9,7M de parâmetros no total e ~2,5M
    # ativos por token. Por camada: atenção multi-query, roteador d → 8 (int8, uma escala por linha), um especialista
    # compartilhado (SwiGLU 128) e 8 roteados (SwiGLU 224), top-1. ~5 MB em int4; ~1,3 MB lidos por token.
    "MoE": dict(d=192, camadas=8, cabecas_q=6, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=224, vocab=1024,
                contexto=256, contexto_calc=128, bits=4, grupo=32, mbits=8, pot2=False,
                n_esp=8, top_k=1, ff_comp=128, ff_esp=224,
                treino=dict(lr=2e-3, lote_tokens=262144, queda=0.15, mistura="texto:0.95,dialogos:0.05",
                            mistura_final="dialogos:0.5,texto:0.5", so_assistente_na_queda=True)),
    # Denso com o mesmo custo por token do MoE (~2,5M): a base de comparação.
    "denso_2.5M": dict(d=192, camadas=8, cabecas_q=6, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=352, vocab=1024,
                       contexto=256, contexto_calc=128, bits=4, grupo=32, mbits=8, pot2=False,
                       treino=dict(lr=3e-3, lote_tokens=262144, queda=0.15, mistura="texto:0.95,dialogos:0.05",
                                   mistura_final="dialogos:0.5,texto:0.5", so_assistente_na_queda=True)),
    # Só para testar o código em CPU.
    "teste_moe": dict(d=64, camadas=2, cabecas_q=2, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=64, vocab=1024,
                      contexto=64, contexto_calc=64, bits=4, grupo=32, mbits=8, pot2=False,
                      n_esp=4, top_k=1, ff_comp=32, ff_esp=64,
                      treino=dict(queda=0.15, mistura="texto:0.5,dialogos:0.5", mistura_final="dialogos:0.5,texto:0.5",
                                  so_assistente_na_queda=True)),
    "teste": dict(d=64, camadas=2, cabecas_q=2, cabecas_kv=1, dim_cabeca=32, ff="swiglu", ff_dim=128, vocab=1024,
                  contexto=64, contexto_calc=64, bits=4, grupo=32, mbits=8, pot2=False),
}

# Ponto fixo do simulador (e da calculadora): bits de fração das ativações largas (int32), da tabela de exp, etc.
PONTO_FIXO = dict(
    frac=12,          # ativações largas (resíduo, saídas das matrizes): int32 com 12 bits de fração (Q12)
    frac_rope=14,     # seno e cosseno do RoPE: int16 Q14
    frac_prob=15,     # probabilidades da atenção: Q15
    exp_passo=5,      # tabela de exp(-x): passo de 1/32
    exp_n=512,        # 512 entradas: x de 0 a 16 (depois disso, exp = 0)
    silu_passo=5,     # tabela de SiLU: passo de 1/32
    silu_lim=8,       # de -8 a 8; fora disso, silu(x) = 0 (x < -8) ou x (x > 8)
    guarda=8,         # bits a mais na soma ponderada dos valores da atenção
    eps=1e-5,         # da RMSNorm
)


def config(nome, **trocas):
    """A variante com campos trocados (ex.: config("A", ff="relu2", ff_dim=512))."""
    c = dict(VARIANTES[nome])
    c.pop("treino", None)
    c.setdefault("n_esp", 0)
    c.update({k: v for k, v in trocas.items() if v is not None})
    assert c["cabecas_q"] * c["dim_cabeca"] == c["d"], "cabecas_q × dim_cabeca precisa ser d"
    assert c["cabecas_q"] % c["cabecas_kv"] == 0
    ocultos = [c["ff_comp"], c["ff_esp"]] if moe(c) else [c["ff_dim"]]
    assert c["grupo"] == 0 or all(x % c["grupo"] == 0 for x in [c["d"]] + ocultos), "o grupo precisa dividir d e os ocultos"
    return c


def padroes_treino(nome):
    """Os padrões de treino da variante (taxa, lote, mistura...)."""
    return dict(VARIANTES[nome].get("treino", {}))


def moe(c):
    return c.get("n_esp", 0) > 0


def _att(c):
    d, hd = c["d"], c["dim_cabeca"]
    return d * c["cabecas_q"] * hd * 2 + d * c["cabecas_kv"] * hd * 2


def parametros(c):
    """Todos os parâmetros (com as normas)."""
    d = c["d"]
    if moe(c):
        ff = d * c["n_esp"] + 3 * d * c["ff_comp"] + c["n_esp"] * 3 * d * c["ff_esp"]
    else:
        ff = d * c["ff_dim"] * (3 if c["ff"] == "swiglu" else 2)
    return c["camadas"] * (_att(c) + ff + 2 * d) + c["vocab"] * d + d


def ativos(c):
    """Parâmetros usados por token, sem as normas (no MoE: um especialista roteado por camada)."""
    d = c["d"]
    if moe(c):
        ff = d * c["n_esp"] + 3 * d * c["ff_comp"] + c["top_k"] * 3 * d * c["ff_esp"]
    else:
        ff = d * c["ff_dim"] * (3 if c["ff"] == "swiglu" else 2)
    return c["camadas"] * (_att(c) + ff) + c["vocab"] * d


def macs_por_token(c, posicoes=None):
    """Multiplicações-e-somas para gerar um token com `posicoes` no cache (padrão: a janela da calculadora)."""
    n = posicoes or c["contexto_calc"]
    lin = ativos(c)
    att = c["camadas"] * c["cabecas_q"] * c["dim_cabeca"] * n * 2
    return lin + att


def cache_bytes(c, posicoes=None):
    """RAM do cache de atenção em int8 (mais um expoente por vetor)."""
    n = posicoes or c["contexto_calc"]
    return c["camadas"] * n * 2 * c["cabecas_kv"] * (c["dim_cabeca"] + 1)
