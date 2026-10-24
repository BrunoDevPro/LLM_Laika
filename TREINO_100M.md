# Treino da Laika de 100M de parâmetros

Tudo o que precisa para treinar o modelo de ~100M (preset `colab_100m`) no Colab, pelo app (tela
**Treinar**) ou pelo navegador. As estimativas de tempo e de unidades são contas a partir da velocidade
da A100. Elas não foram medidas: o ambiente onde o código foi escrito não tem GPU.

## 1. O modelo

| Item | Valor |
|---|---|
| Parâmetros | **103,5 M** (18,4 M no embedding + 85 M nas 12 camadas) |
| Arquitetura | 768 dimensões, 12 camadas, 12 cabeças (64 por cabeça), GELU, pré-LayerNorm |
| Posições | **RoPE** (sem tabela de posições aprendidas), theta 10000 |
| Contexto | **2048 tokens** (o de 7M tem 256; o de 50M, 512) |
| Vocabulário | **24.000** tokens BPE byte-level, treinado numa amostra equilibrada de 1,5 GB |
| Dropout | 0 (com 2 bilhões de tokens, o modelo passa menos de 1 vez por cada texto) |

## 2. Dados (célula 2, sem GPU)

| Fonte | Quanto | Tokens (aprox.) | Observação |
|---|---|---|---|
| Wikipédia em português | **todos** os artigos (~1,1 milhão) | ~450 M | também vai para o índice do RAG |
| Livros do Gutenberg | 500 | ~25 M | português antigo; entra só um pouco na amostra do tokenizer |
| Textos próprios (`data/modern`) | 130 | <1 M | entram 3 vezes |
| **Corpus Carolina** | padrão: `dat,pub,soc,uni,wik` | ~330 M | português brasileiro contemporâneo; sem leis e decisões judiciais |
| **GigaVerbo-v2** | **1,5 bilhão de tokens** | ~1,5 B | só o `edu_high` (nota educacional ≥ 4), toxicidade ≤ 2, um pedaço de cada um dos 56 arquivos |
| **Total** | | **~2,3 bilhões** | ~22 tokens por parâmetro (o ideal é ~20) |

Espaço no Google Drive: ~25 GB no total (Wikipédia ~3 GB, Carolina ~1,4 GB, GigaVerbo ~6 GB, cópia dos
tokens ~4,5 GB, índice do RAG ~4–5 GB, checkpoints ~3 GB).

Pelo app: **Treinar → "Dados para 100M"** (célula 2 sem GPU, com `ARTIGOS = todos`, `CAROLINA` ligado e
`GIGAVERBO = 1,5 bilhão de tokens`). Pelo terminal:

```bash
python prepare_data.py --max-books 500 --wiki -1 --carolina --gigaverbo 1.5e9 --sft 300000
python rag.py build
```

`SFT = "300 mil conversas"` (o atalho **Dados para 100M** já põe): conversas do GigaVerbo-v2-SFT (Apache 2.0,
geradas por outra IA e filtradas por qualidade; 70% pedidos variados e 30% perguntas com contexto, ~1 GB) para o
fine-tuning. Os pesos continuam do zero: são só exemplos de pergunta e resposta.

Leva de 1 a 3 horas, a maior parte na Wikipédia e no índice do RAG. Se cair, rode de novo: os três
downloads continuam de onde pararam (`.pronto` em cada pasta). Para incluir também as leis e as decisões
judiciais do Carolina (~800 M tokens a mais, num estilo bem formal), use `--carolina dat,jud,leg,pub,soc,uni,wik`.

## 3. Pré-treino (célula 3, A100)

| Parâmetro | Valor |
|---|---|
| `PRESET` | `colab_100m` |
| `MODO` | `do_zero` na primeira vez (tokenizer e modelo novos); **`continuar`** nas execuções seguintes |
| `PASSOS` | 0 (usa os 8.000 do preset) |
| `COMPILAR` | ligado (torch.compile: ~20% mais rápido, 1–2 min para compilar) |
| GPU | **A100** (na L4 cabe com `--batch-size 8 --accum 16`, mas leva umas 3× mais; na T4, não compensa) |
| Lote | 16 sequências × 2048 tokens × 8 de acumulação = **262 mil tokens por passo** |
| Passos | 8.000 (≈ 2,1 bilhões de tokens) |
| Taxa de aprendizado | 5e-4, aquecimento de 400 passos, cosseno até 10% |
| Otimizador | AdamW (betas 0,9 e 0,95, weight decay 0,1), gradiente cortado em 1,0 |
| Precisão | bf16 + TF32 |
| Validação | a cada 250 passos (40 lotes); para sozinho se não melhorar em 8 validações seguidas |

O que acontece na primeira execução:
1. O tokenizer é treinado numa amostra de 1,5 GB, dividida igualmente entre as pastas.
2. Os ~2,3 bilhões de tokens são calculados e gravados em `data/tokens/`, com uma cópia em
   `Drive/LLM_Laika/tokens/` (~4,5 GB). Isso leva ~15–30 min. Numa máquina nova, a cópia é trazida de volta,
   o que é bem mais rápido do que calcular de novo.
3. O treino roda e grava o `pretrain_last.pt` (pesos + otimizador, ~1,3 GB) a cada validação, e o
   `pretrain_best.pt` (~420 MB) a cada melhora.

**Tempo estimado na A100:** ~4–5 h de treino. Pelo app, a execução do GitHub Actions para em ~6 h. Se
parar antes do fim, rode as células 3, 4 e 6 de novo com **MODO = "continuar"**: o treino retoma do passo
exato em que parou.

Referência de `val loss` (vocabulário de 24 mil): abaixo de ~3,0 as frases já são boas; o de 7M parou em
3,62, com um vocabulário de 8 mil (os números não são diretamente comparáveis).

## 4. Fine-tuning (célula 4, A100)

| Parâmetro | Valor |
|---|---|
| `EPOCAS` | 2 |
| `USAR_RAG` | ligado (o índice da célula 2) |
| `PERGUNTAS_WIKIPEDIA` | **40000** |
| `RAG_FRACAO` | **0,7** (70% das perguntas que pedem informação treinam com o Contexto do RAG) |
| `CONHECIMENTO` | automático = **20 mil artigos** no 100M: perguntas sem contexto, cada fato de 4 jeitos, 2× por época (Madeira e Areia ficam de fora) |
| `USAR_SFT` | ligado (as conversas do GigaVerbo-v2-SFT da célula 2) |
| Taxa de aprendizado | automática: **1e-4** (acima de 20M de parâmetros) |
| Precisão | bf16 na A100 |
| Dados | ~15 mil exemplos escritos (inclui as 627 respostas longas, 438 "por quê", 975 de sim ou não e 5.313 de pessoas, datas, séculos, conceitos e gatilho de resposta longa) + 1.435 conversas + 10 mil sintéticos + 40 mil perguntas de leitura da Wikipédia + ~300 mil perguntas de conhecimento (sem contexto) + até 300 mil conversas do SFT; ~30% com mensagens anteriores (memória de IA); até 6 trechos do RAG por pergunta |

Com o conhecimento e o SFT, leva ~1–2 h (antes, ~30–60 min); a escolha dos artigos lê a Wikipédia inteira uma vez
(alguns minutos, sem GPU). O `finetuned.pt` anterior vai para `checkpoints/backups/` antes de ser sobrescrito
(ficam os 3 últimos).

## 5. Exportar e usar (célula 6)

`MODELO` ligado, `INDICE` como preferir (o índice com a Wikipédia inteira tem ~4–5 GB; para o celular, o
de 100 mil artigos costuma bastar). O zip tem ~420 MB só com os dois modelos (float16). No app:
**Treinar → Modelos prontos → Baixar e usar**.

No celular, o app 1.5 (ou mais novo) já entende o modelo com RoPE: ele guarda as matrizes em float16 (~210 MB de memória)
e o cache de atenção cresce conforme a conversa. Ainda assim, é um modelo grande para celular: espere
respostas bem mais lentas que as do de 7M. No Windows/PC, o `chat.py` agora usa cache de atenção.

## 6. Custo em unidades de computação (Google AI Pro: 200 por mês)

| Etapa | GPU | Tempo | Unidades (aprox.) |
|---|---|---|---|
| Dados (célula 2) | nenhuma | 1–3 h | ~1–3 |
| Pré-treino (célula 3) | A100 | 4–5 h (+ tokenização) | ~55–70 |
| Fine-tuning (célula 4) | A100 | 0,5–1 h | ~6–12 |
| Exportar (célula 6) | junto com a 4 | minutos | — |
| **Total** | | | **~65–85** |

O consumo da A100 varia (cerca de 12 unidades por hora é a referência mais citada); confira no Colab.

## 7. Ordem recomendada

1. App → Treinar → **Dados para 100M** → Rodar (sem GPU). Espere terminar.
2. App → Treinar → **Modelo de 100M** → Rodar (A100). Ele marca as células 3, 4, 6 e 7 com `do_zero`.
   Como o pré-treino já terminou, para só refazer o fine-tuning: células 4, 6 e 7 (a 3 com `MODO = "pular"`).
3. Se o treino parar no limite de tempo: abra de novo, mude a célula 3 para **`continuar`** e rode 3, 4 e 6.
4. Quando terminar: **Modelos prontos → Baixar e usar**. A célula 7 (avaliar) mostra no registro as notas por
   categoria, comparadas com o fine-tuning anterior, e grava tudo em `Drive/LLM_Laika/checkpoints/avaliacao/`.

## 8. Comandos equivalentes (navegador ou terminal)

```bash
python prepare_data.py --max-books 500 --wiki -1 --carolina --gigaverbo 1.5e9
python rag.py build
python train.py --preset colab_100m --compile --tokens-backup /content/drive/MyDrive/LLM_Laika/tokens
#  (parou?)  python train.py --preset colab_100m --resume --compile --tokens-backup ...
python finetune.py --epochs 2 --wiki-leitura 40000 --rag-share 0.7
python avaliar.py --comparar backup
python chat.py
```

## 9. Licenças

- Wikipédia: CC BY-SA. Gutenberg: domínio público.
- Corpus Carolina: cada documento traz a própria licença no cabeçalho (em geral CC BY, CC BY-SA ou domínio
  público); o corpus foi organizado para fins acadêmicos, então confira antes de qualquer uso comercial.
- GigaVerbo-v2: não tem uma licença única; vale a licença de cada fonte original (FineWeb-2, HPLT, Common
  Crawl...). É texto da web, inclusive de sites de notícias, e por isso **não** vai para o índice do RAG.
