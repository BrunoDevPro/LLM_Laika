# Mini-LLM para a HP 50g

Um modelo de linguagem minúsculo (decoder-only), treinado do zero no Colab, para rodar em C (HPGCC) no ARM da
HP 50g, gerando **diálogos curtos** em português, token a token. Esta pasta não mexe na Laika: só reaproveita
os dados que ela já baixou no Drive e os exemplos escritos de `data/qa/`.

O ambiente onde o código foi escrito não tem GPU nem a calculadora. Tudo foi testado em CPU com a variante
`teste` (`python hp50g/teste_hp50g.py`). Os números da calculadora (RAM, velocidade, flash) são estimativas, e o
formato final dos pesos e o programa em C ficam para a sessão da HP 50g.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `configs.py` | As variantes (A, A_relu2, B, B_relu2, professor, teste), o formato do ponto fixo (`PONTO_FIXO`) e as contas de parâmetros, multiplicações-e-somas por token e RAM do cache |
| `modelo.py` | `MiniLLM` em PyTorch: RMSNorm, RoPE, multi-query, SwiGLU ou ReLU², sem bias, embedding compartilhado, inicialização 0,02 com wo/w2 ÷ √(2 × camadas). Com `qat = True`, simula a quantização (STE) |
| `preparar.py` | Diálogos + texto simples, validação (~1% dos documentos, pelo hash), tokenizador BPE de bytes de 1024, `vocab.bin` e os `.bin` (uint16) |
| `treino.py` | Treino com memmap, mistura de fontes, taxa WSD, QAT na queda, destilação opcional, checkpoint completo e retomada |
| `simulador.py` | Quantização dos pesos, `hplm.bin`, simulador só com inteiros, tokenizador da calculadora (só com as fusões), geração gulosa e com semente, relatório |
| `hp50g.ipynb` | O notebook do Colab: preparar, dados, varreduras, professor, treino final, exportar |
| `teste_hp50g.py` | Teste ponta a ponta em CPU, com interrupção e retomada |

## Variantes

Números medidos aqui: parâmetros e bytes do `hplm.bin`. As multiplicações-e-somas por token contam um contexto de 128.

| Variante | d / camadas | Atenção (Q / K-V) | Feed-forward | Pesos | Parâmetros | `hplm.bin` | Mult.-somas/token | Cache int8 |
|---|---|---|---|---|---|---|---|---|
| **A** | 128 / 6 | 4 × 32 / 1 × 32 | SwiGLU 352 | int4, grupos de 32 | 1.189.504 | 635 KB | 1,38 M | 49,5 KB |
| A_relu2 | 128 / 6 | 4 × 32 / 1 × 32 | ReLU² 512 | int4, grupos de 32 | 1.164.928 | 622 KB | 1,36 M | 49,5 KB |
| **B** | 96 / 5 | 3 × 32 / 1 × 32 | SwiGLU 256 | int8 por linha | 590.880 | 597 KB | 0,71 M | 41 KB |
| B_relu2 | 96 / 5 | 3 × 32 / 1 × 32 | ReLU² 384 | int8 por linha | 590.880 | 596 KB | 0,71 M | 41 KB |
| professor | 512 / 8 | 8 × 64 / 2 × 64 | SwiGLU 1408 | (só para a destilação) | ~23 M | – | – | – |

Todas usam vocabulário de 1024, contexto 256 no treino e 128 na calculadora. Para mudar o tamanho depois das
medições, edite `configs.py` (ou use `--camadas`, `--ff` e `--ff-dim` no `treino.py`).

## Dados (domínio: diálogos curtos)

- **diálogos** (`<|user|> pergunta <|assistant|> resposta <|end|>`, até 3 trocas e ~900 caracteres):
  - os exemplos escritos da Laika (`data/qa/*.txt` e `conversas.jsonl`), repetidos 3×, sem os que têm `Contexto:`;
  - as conversas curtas do GigaVerbo-v2-SFT (`data/sft`), com pergunta de até 200 caracteres e resposta de até 400;
  - só caracteres comuns do português.
- **texto**: frases de 4 a 25 palavras da Wikipédia, do GigaVerbo e do Carolina, em documentos de até 5 frases do
  mesmo parágrafo. Ensinam a língua.
- **Mistura:** `--mistura "dialogos:0.5,texto:0.5"` e, na fase de queda da taxa, `--mistura-final "dialogos:0.8,texto:0.2"`.
  Os diálogos curtos devem ter dezenas de milhões de tokens, então se repetem algumas vezes num treino de 1 bilhão;
  o texto simples não se repete.
- **Validação:** ~1% dos documentos de cada fonte, escolhidos pelo hash do texto, e nunca usados no treino.
- **Medida comum:** bits por caractere (perda ÷ ln 2 ÷ caracteres por token), comparável entre tokenizadores.

**Tokenizador:**
- BPE de bytes com 1024 tokens: 4 especiais, os 256 bytes e as fusões. Nenhum caractere fica sem representação.
- Pedaços ` ?[^espaço]+` ou `[espaço]+`; as fusões só acontecem dentro de cada pedaço.
- Com os dados da Laika, cada token cobre ~2,4 caracteres.

## Treino

- **Precisão e otimizador:** bf16 com `--compile`; AdamW (0,9; 0,95), decaimento 0,1 (sem decaimento nas normas), corte de gradiente em 1,0, dropout 0.
- **Lote:** 512 × 256 = 131 mil tokens por passo.
- **Taxa (WSD):** aquecimento de 1%, constante, queda linear até 0 nos últimos 20%. O pico padrão é 3e-3; a célula 3 compara 1e-3, 3e-3 e 6e-3.
- **QAT:** liga no começo da queda (`--qat-desde` muda).
- **Validações:** a cada 2% do treino, mostram a perda float e a quantizada de cada fonte. O `melhor_float.pt` é escolhido pela perda float antes do QAT e o `melhor.pt` pela perda quantizada.
- **Dados sem repetição:** cada fonte é lida numa ordem embaralhada fixa (i → (a·i + b) mod n), sem repetir até acabar.
- **Retomada:** o `ultimo.pt` (modelo, otimizador, passo, posição de cada fonte e sorteios) é salvo a cada 15 min. Rodar de novo com a mesma `--saida` continua do mesmo ponto, e o teste confere que a perda final sai igual à de um treino sem interrupção.
- **Destilação:** `--professor <ckpt> --alfa 0.5 --temp-dest 1.5`, com KL × T² misturada à perda normal.

## Ponto fixo (o que o C precisa repetir)

Ativações largas em int32 com 12 bits de fração (Q12). Deslocamento à direita arredondado:
`(v + 2^(n-1)) >> n`, com `>>` aritmético.

1. **Embedding:** `x = (q[token][j] × m[grupo]) << (12 - E)` (ou `>>` arredondado se `12 - E < 0`).
2. **RMSNorm:**
   - `ss = Σ x²` (int64);
   - `r = isqrt(ss / d + eps)`, com `eps = round(1e-5 · 2^24)`;
   - `y = trunc((x · g) / r)`, com `g` em Q12 e divisão truncando para zero.
3. **Entrada de cada matriz em int8:** o menor `sh ≥ 0` com `((max|x| + 2^(sh-1)) >> sh) ≤ 127`; `x8 = clamp(desloca(x, -sh), ±127)`.
4. **Matriz:** `acc = Σ_grupo m[o][g] · Σ_{j∈g} q[o][j] · x8[j]` (int64); `y = desloca(acc, sh - E)`.
5. **RoPE** (tabela cos/sin Q14 por posição): `x1' = desloca(x1·c - x2·s, -14)`, `x2' = desloca(x1·s + x2·c, -14)`.
6. **Atenção:**
   - Q, K e V de cada cabeça em int8 com o próprio `sh`; K e V vão para o cache com o `sh`.
   - `score = desloca((k8·q8) · c_inv, sh_q + sh_k - 24)`, com `c_inv = round(2^12/√32)`.
   - `d = max - score`; `e = EXP[d >> 7]` (0 se passar de 511; `EXP[i] = round(2^15 · e^(-i/32))`).
   - `p = (e << 15) / Σe`.
   - `o = desloca(Σ desloca(p · v8, sh_v - 15 + 8), -8)`.
7. **Feed-forward:**
   - SwiGLU: `silu(a)` por tabela (512 entradas de -8 a 8, Q12; fora disso 0 ou `a`) e `f = desloca(silu(a) · b, -12)`;
   - ReLU²: `r = max(a, 0)` e `f = desloca(r · r, -12)`.
8. **Saída:** a norma final, depois a matriz do embedding, que dá os logits em Q12.
   - Guloso: o primeiro índice do maior logit.
   - Amostragem: os 40 maiores (ordem estável), `EXP[((max - l) · 256 / T_q8) >> 7]`, sorteio com o gerador `s = s·1664525 + 1013904223` (32 bits), usando `(s >> 8) % Σ`.
9. **Prompt:** `<|user|>` + BPE(" " + pergunta + " ") + `<|assistant|>`; gera até `<|end|>` ou até o contexto de 128 acabar.

### Arquivos exportados (`simulador.py exportar`)

**`hplm.bin`** (little-endian, alinhado a 4):
- cabeçalho: `HPLM`, a versão, o nº de campos e os campos de `simulador.CAMPOS` em int32;
- tabelas: exp (uint16), SiLU (int32), cos e sin (int16, [128][16]);
- o embedding;
- por camada: n1, wq, wk, wv, wo, n2, w1, (w3), w2;
- a norma final.

Cada matriz tem `E`, linhas, colunas e grupo (int32), as mantissas (uint8, uma por grupo ou linha) e os pesos (int4, dois por byte com o primeiro no nibble de baixo, ou int8). Cada norma tem `n` e os ganhos Q12 (int32).

**`vocab.bin`**:
- `HPVB`;
- o nº de tokens, de fusões e de especiais (uint16);
- cada token como (tamanho uint8, bytes);
- cada fusão como (a, b, resultado) em uint16, em ordem de prioridade;
- os ids especiais.

**`quant.json`:** a configuração, o ponto fixo, os campos e a posição e o tamanho de cada tensor.

**`relatorio.json`:**
- as perdas float, quantizada (PyTorch) e do simulador (inteiros) na mesma validação, com bits por caractere;
- os tamanhos;
- a conferência do tokenizador;
- as amostras lado a lado.

O `relatorio` junta várias exportações numa tabela.

## Laika MoE (versão 2 do hplm.bin)

Especificação "Laika MoE para a HP 50g": uma mistura de especialistas no lugar do modelo denso de 1,19M.

**Arquitetura** (variante `MoE` em `configs.py`):
- d = 192, 8 camadas, atenção multi-query (6 × 32 / 1 × 32), RoPE, RMSNorm, sem bias.
- Roteador d → 8 em int8, com uma escala por linha. Um especialista compartilhado (SwiGLU 128) e 8 roteados (SwiGLU 224), top-1.
- A saída do especialista roteado vai multiplicada pela probabilidade softmax dele. Nenhum token é descartado.
- Perdas auxiliares: balanceamento estilo Switch (0,01 × 8 × Σ f·P) e z-loss (1e-3).
- O treino mostra o uso de cada especialista e a entropia do roteador em cada validação. A meta é que nenhum fique abaixo de ~5% nem acima de ~25%.

**Números medidos no arquivo exportado:**

| Item | Valor |
|---|---|
| Parâmetros no total | 9.744.384 (sem as normas) |
| Ativos por token | 2.519.040 |
| `hplm.bin` | 4,97 MB |
| Sempre ativos (começo do arquivo) | 802 KB |
| Lidos por token | 1,31 MB |
| Cache de atenção | 67,6 KB |

**Dados** (`preparar.py`, célula 2):
- Tokenizador reaproveitado (`--usar-tokenizador`): o `vocab.bin` da calculadora não muda.
- Texto simples reaproveitado de `hp50g/dados` (`--texto-de`).
- 70% das perguntas escritas como no teclado da 50g (`--normalizar 0.7`, `como_na_calculadora`: sem acentos, minúsculas, só a–z 0–9 espaço . ? ! , e a primeira letra maiúscula). As respostas continuam acentuadas.
- Respostas encurtadas para até 60 caracteres, em frases inteiras (`--resposta-curta`).
- Uma troca por diálogo (`--max-trocas 1`), porque cada pergunta é uma conversa nova na calculadora.
- Pares próprios para decorar (`--decorar`, `pergunta|resposta` por linha, `--decorar-rep 8`).
- `dialogos_*.mask` marca os tokens das respostas.
- Tudo vai para `hp50g/dados_moe`.

**Treino** (padrões da variante):
- Lote de 262 mil tokens, taxa de 2e-3, queda nos últimos 15%.
- Mistura de 95% texto e 5% diálogos; na queda, 50/50.
- Na queda, a perda só nas respostas dos diálogos (`--so-assistente queda`) e QAT com o roteador quantizado no forward.
- Base de comparação: a variante `denso_2.5M` (d = 192, 8 camadas, SwiGLU 352), com o mesmo custo por token.

**Simulador:** o bloco MoE exatamente como na especificação:
- roteador `matvec` em int8;
- `e = argmax` (o primeiro máximo);
- `p = (EXP[d_e] << 15) / Σ EXP[d]`, com `d = max - r`;
- `ys` do especialista compartilhado, `ye` do escolhido, `ye = desloca(ye · p, -15)`;
- `x += ys` e depois `x += ye`.

O cache guarda as rotas (especialista, p) de cada token.

**`hplm.bin` versão 2:**
- campos: os 22 de antes, mais `n_esp`, `top_k`, `ff_comp` e `ff_esp`;
- cada matriz com 5 int32: E, linhas, colunas, grupo e **bits** (4, ou 8 no roteador, com grupo = colunas);
- ordem: tabelas, emb; por camada n1, wq, wk, wv, wo, n2, router, s_w1, s_w3, s_w2; nf; depois, para cada camada e especialista, w1, w3, w2.

O `quant.json` lista o offset de cada tensor (`3.router`, `3.s_w1`, `3.e5.w2`…). Os modelos densos continuam na versão 1.

**`vetores_teste.json`** (`simulador.py exportar --vetores 50`): as 8 perguntas de sempre sem acentos e outras do `dialogos_val` normalizadas. Para cada uma:
- os ids do prompt;
- os 1024 logits inteiros depois do último token do prompt;
- as rotas (especialista e p Q15, por camada, de cada token do prompt);
- a resposta gulosa (até `<|end|>`, 80 tokens ou o contexto de 128).

**`relatorio.json`:** além do que já tinha:
- o uso de cada especialista no simulador;
- os bytes sempre ativos e lidos por token;
- as amostras com as perguntas normalizadas;
- com `--comparar export/denso_2.5M`, as perdas do denso, com um aviso se o MoE ficar pior.

A perda do simulador é calculada em paralelo, nos núcleos da máquina.

**Ordem no Colab:** 1 → 2 (sem GPU) → 3 (varredura de 1e-3, 2e-3 e 3e-3 com 150M tokens, A100) → 4 (denso de comparação, A100) → 6 (treino final do MoE, ~2,5 bilhões de tokens, A100) → 7 (exporta o denso e depois o MoE com a comparação, sem GPU).

## Pelo app

Em **Treinar**, toque em **HP 50g**. As células são as do `hp50g.ipynb` e rodam como as da Laika (o workflow
`colab.yml` recebe `caderno = hp50g/hp50g.ipynb`). Atalhos: 1. Dados (sem GPU), 2. Varredura (L4), 3. Treino final
(L4), 4. Exportar (sem GPU). Os resultados ficam no Drive em `LLM_Laika/hp50g`.

## Comandos

```bash
python hp50g/preparar.py --saida data/hp50g --texto-mb 2000
python hp50g/treino.py --variante A --dados data/hp50g --saida runs/A --tokens 1e9 --compile
python hp50g/simulador.py exportar --ckpt runs/A/melhor.pt --dados data/hp50g --saida export/A
python hp50g/simulador.py gerar --pacote export/A --pergunta "Qual é o seu nome?"
python hp50g/teste_hp50g.py   # CPU, ~30 s
```

## Pendências (sessão da HP 50g)

- RAM livre para um programa HPGCC e espaço na porta 2; o ARM consegue ler os pesos direto da flash?
- Velocidade real a 75 e 192 MHz. A variante A faz ~1,4 milhão de multiplicações-e-somas por token, mas desempacotar o int4 custa ciclos; se ficar lento, use a B (int8).
- Programa em C com as contas acima (o simulador é a referência: mesmo texto com a mesma semente), interface na tela de 131 × 80 e entrada de texto.
- Ajustar `d`, camadas ou contexto conforme as medições (`configs.py`). Escalas em potência de 2 (`pot2`) se a multiplicação pela mantissa pesar.
