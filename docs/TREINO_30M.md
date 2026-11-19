# Laika 30M — especialista em conversa

Modelo pequeno (~31M de parâmetros), treinado muito além do Chinchilla e focado em conversa simples e escrita curta,
para rodar rápido no celular. Preparado em 17/11/2026; **ainda não treinado**. Os tempos e as unidades abaixo são
estimativas a partir do 200M (90 unidades e ~16 h para pré-treino e fine-tuning), não medidas.

## Por que assim

- **Tamanho:** ~6 vezes menos contas por token que o 200M, então responde numa fração de segundo no celular, e o
  int8 do app (a partir de 20M de parâmetros) vale para ele.
- **Estreito e fundo** (384 dim, 14 camadas, 6 cabeças): em modelos pequenos, a profundidade rende mais que a
  largura (MobileLLM, 2024). A arquitetura é a mesma do `model.py` (GELU, LayerNorm, RoPE), então o app já roda
  sem mudar nada.
- **Vocabulário de 16 mil:** com 24 mil, 27% dos parâmetros iriam para a tabela de palavras; com 16 mil, 20%.
- **Contexto de 1024:** basta para conversa e liga o histórico em toda mensagem (`history_always`, janela ≥ 1024).
- **Além do Chinchilla:** ~6,3 bilhões de tokens (~200 por parâmetro). A perda continua caindo devagar com mais
  dados, e um modelo pequeno é barato de usar depois. Com os ~4,4 bilhões de tokens que já estão no Drive, os dados
  passam ~1,4 vez, o que perde pouco em relação a dados novos (Muennighoff et al., 2023).
- **Conversas no pré-treino:** `data/conversas` (o GigaVerbo-v2-SFT baixado e os exemplos de `data/qa`, no formato
  do chat) entra 2 vezes no pré-treino. O modelo vê o formato de conversa desde o começo, não só no fine-tuning.
  As conversas por molde (`conversas_coerentes.jsonl`) ficam de fora: tinham só 5% de respostas diferentes.

| Preset `colab_30m` | Valor |
|---|---|
| Parâmetros | 31,0M (20% na tabela de palavras) |
| Arquitetura | 384 dim, 14 camadas, 6 cabeças (64 por cabeça), RoPE, contexto 1024, vocabulário 16 mil |
| Lote | 64 × 1024 × acumulação 4 = 262.144 tokens por passo |
| Passos | 24.000 (≈ 6,3 bilhões de tokens) |
| Taxa de aprendizado | 1,5e-3, aquecimento de 1.000 passos, cosseno até 10% |
| Validação | a cada 500 passos (40 lotes), paciência 8 |
| Tokenizer | amostra de 1,5 GB dividida entre as pastas (`tokenizer_mb`) |
| Conversas | `conversas_repeat = 2` (só este preset lê `data/conversas`) |

## Passo a passo pelo app (tela Treinar)

1. **Dados para 30M** (sem GPU): célula 2 com `CONVERSAS_PRETREINO` ligado. Junta as conversas em
   `Drive/LLM_Laika/conversas`. É rápido; não baixa nada novo se o SFT já estiver no Drive. **Rode uma vez só, antes do
   pré-treino, e depois deixe `CONVERSAS_PRETREINO` desligado.** Rodar de novo com conversas novas em `data/qa` troca os
   arquivos de `conversas/`, e o `train.py` reconhece isso como dados diferentes (a assinatura dos tokens usa o nome e o
   tamanho de cada arquivo): um "continuar" retokenizaria tudo e treinaria o resto com outros dados. As conversas novas
   escritas (30 mil mensagens e 10 mil conversas) pesam pouco no pré-treino perto das ~300 mil do SFT, e fazem diferença
   no fine-tuning, que lê `data/qa` direto do repositório (o branch do RAMO) na hora da célula 4: não precisam estar
   prontas para começar o pré-treino.
2. **Modelo de 30M** (A100): prepara as células 3, 4, 6 e 7.
   - Célula 1: `PROJETO = laika30m` e `NOME = Laika 30M conversa`. As pastas são próprias, então o 100M e o 200M não
     mudam.
   - Célula 3: `MODO = do_zero`, `PRESET = colab_30m`, `PASSOS = 0` e `COMPILAR` ligado.
   - Célula 4, com foco em conversa: `CONHECIMENTO = nenhum` (fatos vêm do RAG; um modelo de 30M que decora fatos só
     inventa), `PERGUNTAS_WIKIPEDIA = 20000` (para saber ler o trecho do RAG), `SFT_MAXIMO = 200 mil` e
     `EPOCAS = 2`.
3. **Continuar o 30M**, se a execução parar no limite de ~5,5 h: retoma do último passo salvo, a cada 500 passos.
   Se o pré-treino já tiver terminado, a célula 3 só avisa e segue para o fine-tuning. Com `PASSOS = 0`, o
   `continuar` num pré-treino terminado não treina mais nada.
4. No fim, o zip vai para "Modelos prontos" e para os backups do app, com o nome. A célula 7 avalia.
5. Para voltar aos outros modelos, apague o `PROJETO` da célula 1, ou ponha o deles.

## Estimativas (não medidas)

| | Valor |
|---|---|
| Pré-treino | ~4 a 9 h de A100, em 1 ou 2 execuções |
| Fine-tuning | ~0,5 a 1 h |
| Unidades | ~20 a 45 no total |
| Drive | cópia dos tokens ~10 GB (`tokens_laika30m`), checkpoints ~0,5 GB, conversas ~1 GB |
| Celular | ~6 vezes menos contas por token que o 200M; com int8, uma fração de segundo por resposta curta |

Como estimei: um modelo de 30M custa ~6 vezes menos contas por token que o de 200M, mas aproveita pior a A100 (lote
grande de contas pequenas), então contei ~3 vezes mais barato por token. Também não sei quanto das 90 unidades do
200M foi do fine-tuning.

## O que esperar

- **Ganha:** respostas curtas e coerentes em poucas trocas, rapidez no celular e memória da conversa (histórico em
  toda mensagem).
- **Perde:** conhecimento e raciocínio caem muito; fatos dependem do RAG. Conversa livre sobre qualquer assunto não
  é realista com 30M. Uma conversa simples do dia a dia, que lembra o que você disse, é.
- **O que mais pesa é a variedade dos dados de conversa.** As 30 mil mensagens e 10 mil conversas escritas
  (`docs/MELHORIAS_CONVERSA.md` e a especificação dos dados) entram no `data/qa` (no repositório, no branch do RAMO) e
  servem para este modelo e para o 200M. O pré-treino pode começar antes delas; o fine-tuning (célula 4) espera por elas.

## Pelo terminal

```bash
python prepare_data.py --max-books 0 --wiki 0 --conversas-pretreino      # data/conversas
python train.py --preset colab_30m --compile --tokens-backup /content/drive/MyDrive/LLM_Laika/tokens_laika30m
python finetune.py --conhecimento 0 --wiki-leitura 20000 --sft-max 200000
```
