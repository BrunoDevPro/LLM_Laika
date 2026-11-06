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
    # Só para testar o código em CPU.
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
    c.update({k: v for k, v in trocas.items() if v is not None})
    assert c["cabecas_q"] * c["dim_cabeca"] == c["d"], "cabecas_q × dim_cabeca precisa ser d"
    assert c["cabecas_q"] % c["cabecas_kv"] == 0
    assert c["grupo"] == 0 or c["d"] % c["grupo"] == 0 and c["ff_dim"] % c["grupo"] == 0, "o grupo precisa dividir d e ff_dim"
    return c


def parametros(c):
    d, hd = c["d"], c["dim_cabeca"]
    att = d * c["cabecas_q"] * hd * 2 + d * c["cabecas_kv"] * hd * 2
    ff = d * c["ff_dim"] * (3 if c["ff"] == "swiglu" else 2)
    return c["camadas"] * (att + ff + 2 * d) + c["vocab"] * d + d


def macs_por_token(c, posicoes=None):
    """Multiplicações-e-somas para gerar um token com `posicoes` no cache (padrão: a janela da calculadora)."""
    n = posicoes or c["contexto_calc"]
    lin = parametros(c) - c["camadas"] * 2 * c["d"] - c["d"]
    att = c["camadas"] * c["cabecas_q"] * c["dim_cabeca"] * n * 2
    return lin + att


def cache_bytes(c, posicoes=None):
    """RAM do cache de atenção em int8 (mais um expoente por vetor)."""
    n = posicoes or c["contexto_calc"]
    return c["camadas"] * n * 2 * c["cabecas_kv"] * (c["dim_cabeca"] + 1)
