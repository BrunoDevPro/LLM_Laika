# LLM Laika — guia do projeto para o Claude Code

Este arquivo é lido automaticamente pelo Claude Code. Ele resume o que o projeto é, como está
organizado, por que as decisões foram tomadas, os números medidos e os próximos passos planejados.
Escrito em 22/10/2026; atualizado em 23/10/2026 (app 1.2: Colab pelo app, zip único, sem treino no celular;
app 1.3: preset de 50M, Wikipédia com até 1 milhão de artigos, +3.300 perguntas genéricas;
app 1.4: memória de IA (histórico no prompt), RAG com vários trechos e busca pelo nome próprio, ~20 mil perguntas
da Wikipédia com contexto, taxa de aprendizado automática, menu novo no app; em 24/10/2026, app 1.5: memória de
IA só em mensagens de seguimento, preset de 100M com RoPE e contexto 2048, cache de atenção no Python, Corpus
Carolina e GigaVerbo, +2.040 perguntas com respostas longas, "por quê" e sim ou não; app 1.6: gatilho de resposta
longa ("Explique melhor.", "Resposta longa.", opção "Respostas longas" no app), tokens por mensagem, +5.313 perguntas
de pessoas, datas por extenso, séculos em algarismos romanos e conceitos; app 1.7: busca do RAG corrigida
(a cadela Laika, radical novo, textos com nota mínima), até 6 trechos com janela 2048, fine-tuning como fonte de
conhecimento, GigaVerbo-v2-SFT e `avaliar.py`; em 25/10/2026, app 1.8: leitura de datas de acontecimentos, respostas
sem datas por extenso, +1.048 perguntas de quem fez, por quê, líder, mês e duas perguntas em uma, seguimentos como
"Mas em que mês foi?", nome do usuário e da Laika no Contexto em "Faça uma frase com o meu nome"; app 1.9: PROJETO
no Colab (cada modelo com as suas pastas e o zip indo direto para os backups do app com o nome), salvar por cima e
limpar backups no app, "Temperatura" no menu, identidade reforçada contra os personagens do SFT).

## 1. O que é

A **Laika** é um modelo de linguagem pequeno (transformer estilo GPT), **treinado do zero em PyTorch,
em português**, com:
- pré-treino em livros do Project Gutenberg, artigos da Wikipédia em português e textos escritos para o projeto;
- fine-tuning de perguntas e respostas (formato de chat);
- **RAG** (busca em artigos e livros com SQLite FTS5) que coloca um trecho como "Contexto:" no prompt e
  cita a fonte no fim da resposta (`... *Nome do artigo`);
- **memória do usuário** (nome, cidade, gostos, "lembre que...") fora do modelo, em JSON;
- **memória de IA**: as últimas trocas da conversa (até 5) entram no prompt, quantas couberem na janela, só quando a
  mensagem depende da anterior (`follows_up`);
- treino no **Google Colab** (arquivos no Google Drive) e um **pacote para rodar no Windows** (CPU).

Repositório: `github.com/BrunoDevPro/LLM_Laika` (público, branch `main`).
O nome é uma homenagem à cadela Laika (Sputnik 2, 1957). A interface e os comentários do código são em português.

## 2. Estado atual (números medidos)

| Item | Valor |
|---|---|
| Modelo em uso (preset `colab`) | ~7M parâmetros: 256 dim, 6 camadas, 8 cabeças, contexto 256, vocabulário BPE 8000 |
| Pré-treino | 10.000 steps (lote 64 × 256); melhor `val loss` **3,62** no step 9.500 (ainda melhorava) |
| Fine-tuning | `val loss` **2,12** (média de "livros" e "escritos à mão") |
| Dados no Drive | 495 livros (~17 M palavras) + ~99 mil artigos aproveitados de 100 mil (~31 M palavras, ~314 palavras/artigo) ≈ **80 M tokens** |
| Índice RAG | `laika_rag.db` 636 MB, **1,09 milhão de trechos** (678 mil wiki, 413 mil livros, 124 textos) |
| Velocidade de treino medida | T4: ~95 mil tokens/s com o modelo de 14M (≈ 9 TFLOPS efetivos) |
| Exemplos de fine-tuning escritos | `pergeresp.txt` 15426 + `identidade.txt` 274 + `leitura.txt` 512 = **16212** (3333 genéricas de `tools/genericas_*.py`; 627 respostas longas, 438 "por quê" e 975 sim ou não de `tools/longas*.py`, `porque*.py`, `simnao*.py`; 5313 de pessoas, datas, séculos, conceitos e gatilho de `tools/pessoas*.py`, `eventos.py`, `conceitos*.py`; 1048 de quem fez, por quê, líder, mês e nomes de `tools/eventos2.py` e `nomes_sections`; 164 de identidade de `tools/identidade4.py`) + `conversas.jsonl` com **2299** conversas de 2 a 3 trocas |
| Preset de 100M (`colab_100m`) | 103,5M parâmetros, RoPE, contexto 2048, vocabulário 24 mil, 8 mil passos de 262 mil tokens (~2,1 bilhões); **ainda não treinado**. Configuração completa em `TREINO_100M.md` |
| Textos próprios (`data/modern/`) | 130 (20 maiores + 110 simples) |

Os checkpoints atuais (`pretrain_best.pt`, `finetuned.pt`, `tokenizer.json`) ficam no Drive em
`Meu Drive/LLM_Laika/checkpoints/` e **não estão no Git**.

**Limitação de ambiente:** o ambiente em que este código foi escrito não tinha acesso ao PyPI, então
**o PyTorch nunca foi executado aqui**. Tudo que depende de torch foi testado só no Colab pelo usuário;
o resto (gerador de dados, RAG, memória, montagem do prompt) foi testado com um torch falso. Se o
Claude Code tiver PyTorch disponível, vale rodar um teste ponta a ponta com `--preset tiny`.
(Em 23/10/2026 o Claude Code rodou com PyTorch 2.14 em CPU: `train → rag build → finetune → chat` com
`--preset tiny` funcionou, e os checkpoints reais foram comparados com o app Android.)

## 3. Estrutura

| Arquivo | Função |
|---|---|
| `model.py` | `TinyLLM`: atenção causal (`F.scaled_dot_product_attention`, `is_causal=True`), pré-LayerNorm, GELU, pesos compartilhados entre embedding e saída, **posições aprendidas** (`pos_emb`, tamanho = `block_size`) ou **RoPE** (`rope=True` no config: gira as metades de q e k, tabelas `rope_cos/sin` fora do state_dict, sem `pos_emb`). `forward(idx)` treina; `forward_cached(idx, past)` gera com cache de atenção (mesma saída, conferida). `build_model(config)` cria a partir do dict salvo no checkpoint. |
| `config.py` | Presets: `tiny` (CPU, ~1,3M), `tiny_rope` (o tiny com RoPE e contexto 256, para testes), `colab` (~7M, o atual), `colab_big` (~14M), `colab_50m` (~52M: 512 dim, 14 camadas, 8 cabeças, contexto 512, vocabulário 16 mil, lote 32 × acumulação 2) e `colab_100m` (~104M: 768 dim, 12 camadas, 12 cabeças, RoPE, contexto 2048, vocabulário 24 mil, dropout 0, lote 16 × 2048 × acumulação 8, lr 5e-4, 8 mil passos, `tokenizer_mb=1500`). Os dois maiores pedem MODO `do_zero` e muitos dados. `accum`, `rope` e `tokenizer_mb` são opcionais no preset. |
| `train.py` | Pré-treino. Lê `data/books`, `data/wiki`, `data/modern` (esta 3×), `data/carolina` e `data/gigaverbo` (as que existirem). Treina o tokenizer BPE (byte-level) se não for `--resume`; com `tokenizer_mb`/`--tokenizer-mb`, numa amostra dividida igualmente entre as pastas (sem os `<|endoftext|>`). Arquivos grandes são tokenizados em pedaços de ~1 MB, em grupos de ~32 milhões de caracteres (a RAM não estoura com 8 GB de texto); `--tokens-backup` guarda/traz uma cópia dos tokens (célula 3: `Drive/LLM_Laika/tokens`). `--accum`, `--compile` (torch.compile; salva os pesos do modelo original). Validação = últimos 5% de **cada** arquivo. Os tokens vão para `data/tokens/` (uint16, lidos com `np.memmap`, reaproveitados enquanto os textos e o tokenizer não mudam), então a RAM não limita o tamanho dos dados. Acumulação de gradiente (`accum`), bf16 na A100/L4 (fp16 + GradScaler na T4), TF32, early stopping, cosine com warmup. Salva o melhor em `checkpoints/pretrain_best.pt` (`model`, `config`, `step`, `val_loss`) e, a cada validação, `pretrain_last.pt` (pesos, otimizador, scaler, step, geradores aleatórios): `--resume` continua dele do ponto exato (ex.: depois do limite de 6 h do GitHub Actions); se o treino já tinha acabado, parte do melhor com um agendamento novo. O `last` é apagado no fim. |
| `finetune.py` | Parte do `pretrain_best.pt` e grava `checkpoints/finetuned.pt` (**sobrescreve** a cada melhora, sem backup). Loss só nos tokens da **última** resposta. Guarda o `finetuned.pt` anterior em `checkpoints/backups/` (os 3 últimos; `--no-backup`). A identidade tem peso extra (`--identity-boost 2`) e, desde a 1.9, pelo menos `--identity-share 0.005` dos exemplos da época (até 16 repetições), senão some no meio do SFT e do conhecimento. bf16 na A100/L4; replay em trechos de até 512 tokens. Taxa de aprendizado automática (`--lr`): 5e-5 até 20M de parâmetros, 1e-4 acima. Memória de IA: as conversas de `data/qa/conversas.jsonl` e ~30% dos outros exemplos (`--history-share`) ganham de 1 a 4 trocas curtas anteriores (só se couber no bloco). Leitura da Wikipédia: `--wiki-leitura 20000` perguntas tiradas dos trechos (`--wiki-mb 40` de artigos; "Onde X nasceu?", "Quando X foi fundada?", "O que X inventou?", "Quantos habitantes tem X?", e na 1.8 "Quando aconteceu X?", "Em que mês foi X?", "Quem liderou X?"...) com o trecho como Contexto; 10% com o trecho de outro artigo e resposta "não sei"; com janela ≥ 512, metade ganha um segundo trecho do mesmo artigo. Mistura em cada lote: exemplos escritos (`data/qa/`, pelo menos ~25%; com os 7,6 mil atuais cada um aparece 1× por época, ~37%; identidade com peso extra), sintéticos (`--synthetic 10000`: continue/complete/frase com palavra/resumo extrativo dos livros + "O que é X?" da Wikipédia em `data/qa_auto/`) e replay de texto puro. Com o índice RAG, ~70% das perguntas que pedem informação ganham "Contexto:" (`--rag-share 0.7`, buscado com `rag.contexts`, igual ao chat). **Conhecimento** (`--conhecimento`, 1.7): os N artigos "mais importantes" da Wikipédia (`select_articles`: os mais longos, com peso a mais para os primeiros arquivos; automático = 5 mil até 20M de parâmetros, 20 mil acima; fora `--conhecimento-excluir "Madeira,Areia"`) viram perguntas **sem** Contexto (`knowledge_examples`: cada fato de `_reading_pairs` em `--conhecimento-formas 4` formas, mais "Fale sobre X." com o começo do artigo), repetidas `--conhecimento-repetir 2` vezes por época, fora do RAG e do histórico. **SFT** (1.7): as conversas de `data/sft/*.jsonl` (`--sft-max 300000`), também fora do RAG e do histórico; o que passa do bloco é descartado. As buscas do RAG rodam em paralelo (`find_contexts`, um processo por núcleo, até 16) com cache em `data/rag/contextos_cache.json` (vale enquanto o índice e `rag.RAG_VERSAO` não mudam; gravado a cada 5 mil buscas); o SFT é lido de `data/sft/sft_todas.jsonl` (`prepare_data.ler_sft`, que junta os arquivos dos grupos em paralelo quando ele falta); a tokenização é em lotes. **Lotes agrupados por tamanho** (`make_batches`): até `--batch-size` exemplos e até `--tokens-por-lote` (padrão batch-size × min(janela, 512)) tokens com o enchimento, ordenados por tamanho dentro de blocos sorteados de 8192; o progresso da época aparece a cada 2 min (lotes, loss, tokens/s, tempo restante); a validação usa até `--val-max 2000` exemplos de cada tipo. A validação mostra também `val conhecimento` e `val SFT` (o critério de parada continua livros + escritos). **2 épocas** por padrão. Mostra 8 respostas de teste por época. |
| `chat.py` | Conversa. `build_prompt(question, tokenizer, block, rag, memory, max_new, history)` (usado também pelo finetune) junta memória + RAG (`rag.contexts`, `rag_chunks(block)` trechos: 1 com 256, 2 com 512, 3 com 768+) e corta o contexto para caber na janela; depois põe antes as trocas do histórico, da mais nova para a mais antiga, enquanto couberem (até `MAX_HISTORY = 5`). A busca do RAG usa `rag_queries()`: em "Faça um texto sobre planárias", procura só "planárias"; senão, a pergunta e, se ela não achar nada com confiança, o nome próprio ("Santos Dumont"). Com `max_new_tokens` > 60, o `<|end|>` é penalizado no começo (`min_answer_tokens`, `end_penalty`), para respostas mais longas. **Gatilho de resposta longa** (`LONG_TRIGGER = "Resposta longa."`, `wants_long`, `without_trigger`; também "Explique melhor", "Responda com detalhes"): fica na pergunta, mas sai da busca do RAG, da memória e do `follows_up`; com ele, o tamanho máximo sobe para `block // 4`; `/longa` acrescenta o gatilho a toda pergunta. Depois de cada resposta mostra `(N tokens na resposta, T no total)`. O histórico só entra se `follows_up(pergunta)`. `/limpar` esquece o histórico; `--no-history` desliga. `generate()` com top-k, top-p, penalidade de repetição (só nos tokens gerados) e **cache de atenção** (`forward_cached`; passou da janela, recalcula a janela inteira como antes; saída gulosa idêntica à versão sem cache). `with_citation()` adiciona ` *Título`. Comandos: `/fontes`, `/rag`, `/memoria`, `sair`. `--base` = completar texto com o pré-treino. |
| `rag.py` | `python rag.py build` monta o índice FTS5 (`title, text, kind, pos`; tokenizer `unicode61 remove_diacritics 2`) a partir de wiki/textos/livros, no disco local e depois copia; `RagIndex.best()` só devolve contexto com confiança (nota ≥ 1,8, ou fonte `texto` com alguma palavra da pergunta no título); `RagIndex.contexts(pergunta, k)` tenta cada consulta de `rag_queries` e devolve até k trechos (os extras do mesmo artigo, ordenados por quantas palavras da pergunta têm). Busca (1.7): título contendo todas as palavras, ou todas as do nome próprio, + OR de palavras/radicais, 200 candidatos; `_stem` tira só plural e terminações de verbo (antes eram 5 letras: "capital" = "capítulo"); o texto `data/modern/laika.txt` (a IA se apresentando) fica fora; pontuação por cobertura, título igual (+0,6) ou título contido na pergunta com o resto no trecho (+0,4, "a cadela Laika"), penalidade de parênteses/palavras extras/acentos diferentes ("Pele" × "Pelé"), proximidade, primeiro trecho do artigo. `python rag.py search "pergunta"` para testar. No Colab, copia o índice do Drive para o disco local antes de abrir. |
| `memory.py` | Memória por expressões regulares; salva em `checkpoints/memoria.json`. Com "meu nome" (sem "é" depois) o Contexto ganha "O nome do usuário é N." e com "seu/teu nome", "O nome da assistente é Laika." (1.8; sem nome guardado, pede o nome). Desde a 1.9, o da Laika só
quando o pedido usa o nome (`NAME_USE`: frase, poema, letras, escreva, use...), não em "Qual é o seu nome?". Responde direto "qual é o meu nome", "o que você lembra de mim", "esqueça tudo" e frases incompletas ("Meu nome é", "Eu moro em", "Lembre que" → pede o resto, sem gravar nada); anotações relacionadas entram no Contexto. Não muda o prompt de perguntas normais. |
| `data_utils.py` | Tokens especiais, limpeza do Gutenberg, leitura dos arquivos de QA, exemplos sintéticos, resumo extrativo, limpeza da Wikipédia e geração de "O que é X?", as perguntas de leitura da Wikipédia (`reading_examples`), o formato de conversa (`chat_turn`, `split_conversation`, `MAX_HISTORY`, `follows_up`: a mensagem começa com "e/mas/então/também", tem "isso/ele/ela/o mesmo/continue...", uma frase como "explique melhor" ou "não entendi", ou tem até 2 palavras sem assunto e não é cumprimento, ou até 6 palavras só com palavras genéricas como mês, ano, líder, motivo, governava: `generic_follow_up`, que também desliga o RAG, senão "Mas em que mês foi?" achava o artigo "Mês") o conhecimento sem contexto (`knowledge_examples`, `KNOWLEDGE_WRAPS`, `KNOWLEDGE_ABOUT`) e as funções do RAG: `content_words`, `personal_words` (pronomes e "laika", menos quando o assunto é a cadela, `_LAIKA_CADELA`, e sem o começo educado "Você sabe...", `_POLITE`), `wants_rag`, `request_topic` (assunto depois de "sobre", "a respeito de", "acerca de"), `question_name` (nome próprio mais longo), `rag_queries` (o assunto ou a pergunta e, depois, o nome próprio), `rag_chunks` (1 com 256, 2 com 512, 4 com 1024, 6 com 2048), `rag_question`, `fit_context`, `split_example`. |
| `prepare_data.py` | `--carolina [taxonomias]` (Corpus Carolina v2, XML TEI de `carolina-c4ai/corpus-carolina`; padrão `dat,pub,soc,uni,wik`, sem `jud`/`leg`; pula os `wikis/pt/*`, que são a Wikipédia, e páginas de bastidores; um `carolina_*.txt` por arquivo) e `--gigaverbo N` (N tokens do `Polygl0t/gigaverbo-v2` `edu_high`, toxicidade ≤ 2, lido por grupos de linhas do parquet via HTTP com `fsspec`+`pyarrow`, um grupo de cada um dos 56 arquivos por rodada; `gigaverbo_AA_GG.txt`). Os dois separam documentos com `<|endoftext|>`, continuam de onde pararam (`.pronto`) e não entram no RAG. `--sft N` (1.7): N conversas do `Polygl0t/gigaverbo-v2-sft` (Apache 2.0; gerado pelo Qwen2.5 e filtrado por qualidade) para o fine-tuning, `--sft-subconjuntos "general:0.7,retrieval:0.3"`, nota ≥ 4, ≤ 1500 tokens, sem sistema, código, `<think>`, LaTeX, tabelas e menções a outras IAs (`converter_sft`); o `<context>` do retrieval vira `Contexto: ... Pergunta: ...`; um pedaço de cada grupo de linhas de todos os arquivos (`data/sft/sft_SUB_AA_GGG.jsonl`, como o `conversas.jsonl`), continuando de onde parou. Baixa livros pt do catálogo CSV do Gutenberg (`--max-books 500`, grava `data/books/titulos.tsv`) e artigos da Wikipédia via Hugging Face `wikimedia/wikipedia` `20231101.pt` em streaming (`--wiki 100000`; `--wiki 1000000` ou `--wiki -1` = todos, ~1,1 milhão). O download continua de onde parou: cada `wiki_NNN.txt` completo fica registrado num `.pronto` (JSON), e aumentar o número só baixa o que falta. Mostra velocidade e tempo estimado. |
| `colab.ipynb` | Célula 1 com **`NOME`** (1.9.1: só o nome do modelo no app; o zip da célula 6 leva `laika_nome.txt` com `NOME` ou, sem ele, o `PROJETO`) e **`PROJETO`** (1.9, só para um modelo novo; pasta nova sem pré-treino: a célula 1 avisa e o `finetune.py` para com uma mensagem clara): vazio = `checkpoints` e `Drive/tokens` de sempre; com um nome, `checkpoints_<nome>` e `tokens_<nome>` (variáveis `CHECKPOINTS`, `TOKENS`, `SUFIXO`; o atalho `checkpoints` é refeito se o projeto mudar na mesma máquina), dados, índice e SFT compartilhados; a célula 6 grava `laika_nome.txt` no fim do zip e o copia como `laika_pacote_<nome>.zip`. 8 células: (0) ligar o app ao Colab (**só no navegador**, uma vez: login `gcloud` com os escopos do Colab CLI e grava o segredo `COLAB_ADC` no GitHub), (1) preparar/Drive (define `rodar()`, que para a célula se o comando falhar; atalhos também para `data/carolina` e `data/gigaverbo`), (2) dados + índice RAG (`ARTIGOS`: 10 mil a 1 milhão ou todos; `CAROLINA`; `GIGAVERBO` de 500 milhões a 2 bilhões de tokens; `SFT` de 100 a 500 mil conversas), (3) pré-treino (`MODO = "pular" / "continuar" / "do_zero"`, `PRESET` até `colab_100m`, `COMPILAR`; "continuar" retoma o `pretrain_last.pt`; sempre com `--tokens-backup {DRIVE}/tokens`), (4) fine-tuning (`PERGUNTAS_WIKIPEDIA` 40000, `RAG_FRACAO` 0,7, `CONHECIMENTO`, `USAR_SFT`), (5) conversar (**só no navegador**), (6) exportar para o celular (`laika_pacote.zip`: modelo e, opcionalmente, índice e textos), (7) avaliar (`avaliar.py`, `COMPARAR_COM_BACKUP`, `USAR_RAG`). Os campos são formulários do Colab (`#@param`), que o app preenche. A primeira linha de cada célula é `# N) TÍTULO` (e `[só no navegador]` quando for o caso): o app e o `laika_colab.py` dependem disso. |
| `colab/laika_colab.py` | Orquestrador do **Colab CLI** (`google-colab-cli`), rodado pelo GitHub Actions: lê as células do notebook, aplica os parâmetros, liga a máquina (`colab new --gpu`), monta o Drive (repassando ao app o link de autorização, se vier), roda cada célula com `colab exec` (marca de fim + arquivo de estado na máquina, para sobreviver à queda da conexão), baixa o zip da célula 6 e desliga a máquina. Publica o andamento na verificação "Laika no Colab" (check run) que o app lê. Só biblioteca padrão. `python colab/laika_colab.py celulas` mostra as células em JSON. |
| `colab/teste_laika_colab.py` | Testes do orquestrador com um `colab` falso (kernel Python persistente de verdade, queda de conexão, kernel que reinicia, autorização do Drive, GPU recusada, cancelamento) e uma API do GitHub falsa. `python colab/teste_laika_colab.py`. |
| `.github/workflows/colab.yml` | Workflow disparado pelo app (`workflow_dispatch`: `celulas`, `gpu`, `parametros` em JSON, `pedido`). Uma execução por vez (`concurrency`), limite de 355 min, guarda o zip como artefato `laika_pacote` (14 dias) e sempre roda `colab stop` no fim. `sinal.yml`: o app avisa "Drive autorizado" disparando-o com `run-name = drive-ok-<id>`. |
| `avaliar.py` | Avaliação fixa (1.7): perplexidade em `data/avaliacao/textos.txt` (nunca entra no treino), 112 perguntas de `data/avaliacao/perguntas.jsonl` por categoria (identidade, conversa, acontecimentos, nomes, fatos sem e com RAG, leitura, "não sei", seguimento, resposta longa, contas, sim ou não, datas, generalização, pedidos) com as palavras esperadas (`esperado`: grupos de alternativas, todos precisam aparecer; `proibido`, `min_palavras`, `contexto`, `historico`, `rag`), geração sem sorteio (`top_k=1`), e a busca do RAG (`data/avaliacao/rag.jsonl`: pergunta → título esperado ou `null`; acerto, sem contexto, errado). `--comparar backup` compara com o backup mais recente e lista as perguntas que mudaram. Grava `checkpoints/avaliacao/avaliacao_<data>.json`. |
| `SUGESTOES.md` | Ideias de melhoria da LLM que **não** estão no plano da seção 9 (arquitetura, dados, fine-tuning, celular, processo). |
| `TREINO_100M.md` | Todas as configurações do treino de 100M (dados, células, lote, passos, lr, tempo, unidades, espaço no Drive, ordem). |
| `tools/gerar_pergeresp.py` | **Gera** `data/qa/pergeresp.txt`, `identidade.txt`, `leitura.txt`, `conversas.jsonl` (`conversas()`: capitais e temas em sequência, "E X?", "Do que estávamos falando?", nome lembrado, "Pode repetir?") e `data/modern/simples_*.txt` a partir das tabelas em `tools/dados_extra*.py`, `tools/leitura.py`, `tools/textos_simples*.py` e `tools/genericas_*.py`. |
| `tools/longas1..7.py`, `porque1..4.py`, `simnao*.py` | **Respostas longas** (176 textos de 2 parágrafos, ~100–150 palavras, até 252 tokens com o tokenizer de 8 mil: explicações, passo a passo, comparações e histórias; `(assunto ou None, pergunta, texto)`, com 2–3 formas de pedir), **"por quê"** (~250, com outra forma de perguntar cada) e **sim ou não** (~300 à mão + `ANIMAIS`, `PLANETAS` e as tabelas de capitais, estados, línguas e livros, com uma pergunta certa e uma errada; primos, pares, tabuada, contas). `gerar_pergeresp.longas_sections` e `contas_explicadas` (150 contas com o passo a passo). |
| `tools/pessoas1..3.py`, `eventos.py`, `conceitos1..2.py` | **Pessoas** (138: `(nome, "m"/"f"/"p", nascimento, morte, quem foi, o que fez)`; Brasil, ciência, exploração, história, artes), **acontecimentos** (102: `(nome, dia, mês, ano, o que aconteceu, mais)`) e **conceitos** (87: `(assunto, curta, longa)`: pedra, rocha, água, minerais, vida, física, espaço; de propósito **sem madeira e areia**, que o usuário quer perguntar depois para ver se a Laika generaliza). `gerar_pergeresp.pessoas_sections`, `datas_sections` (datas em algarismos e por extenso com `ano_extenso`/`data_extenso`, séculos com `romano`, anos e algarismos romanos), `conceitos_sections`, `gatilho_sections` (o gatilho nos temas e nas respostas longas) e `novas_conversas` ("Quem foi X?" → "E o que ele fez?", "O que é X?" → "Explique melhor."). |
| `tools/eventos2.py` | (1.8) Para 96 acontecimentos de `eventos.py`: `(quem fez, por que aconteceu, pergunta do líder ou None, resposta)`. `gerar_pergeresp.detalhes_sections` ("Quem liderou X?", "Por que aconteceu X?", "Quem era o rei de Portugal quando...", "O que foi X e por que aconteceu?", "O que aconteceu na X, quando?", "Em que mês foi X?", "X foi em que mês?") e `detalhes_conversas` (→ "Mas quando?", "Mas quem fez isso?", "Mas em que mês foi?" → "E o dia?", "Quem governava na época?"). `nomes_sections`/`nomes_conversas`: pedidos com o nome do usuário no Contexto, o nome da Laika e "Faça uma frase com o nome dele" depois de "Quem foi X?" ou "Meu irmão se chama Pedro". |
| `tools/identidade4.py` | (1.9) Mais identidade: ~30 formas de perguntar o nome, ~30 de "quem é você", ~55 negações de personagem ("Você é o rei do Reino Unido?", "Você é Napoleão?"), "Você tem um reino?", quem a fez, do zero, o nome; `DEPOIS_DO_ASSUNTO` vira conversas depois de perguntas sobre reis e pessoas (`gerar_pergeresp.identidade_conversas`). |
| `tools/genericas_*.py` | Perguntas **genéricas** (3333 exemplos). `genericas_temas1..5`: ~460 assuntos `(assunto com artigo, resposta curta, parágrafo)`, de onde saem "O que é X?", "Faça um texto sobre X." (e outras 11 formas), texto curto, "E X?", "Você sabe algo sobre X?", "Resuma em uma frase: <parágrafo>" e leitura com Contexto. `genericas_perguntas1..3` e `genericas_extra`: por quê, como fazer, o que fazer, diferenças, para que serve, como funciona, verdade ou mito, listas, pessoas, datas, opiniões (neutras em política e religião), conversa livre, curiosidades. `genericas_conversa`: mensagens incompletas, pedidos que dependem da mensagem anterior ("Por quê?", "Continue.": a Laika vê uma mensagem por vez e pergunta o assunto), identidade (vai para `identidade.txt`), limites, apoio (CVV 188, SAMU 192, 180, Disque 100) e escrita (poemas, histórias, mensagens). O gerador pula perguntas que já existem (mesmo texto, sem pontuação) e cria variações ("Me ensine a...", "Verdade ou mito:"...). |
| `android/` | **App Android** (APK) que roda a Laika no celular, sem PyTorch: o transformer com KV cache, o tokenizer, o RAG e a memória reescritos em Java (`android/core`), conferidos contra o Python por `core/referencias.py` + `gradle :core:test`. Também liga as células do Colab pela tela **Treinar** (`ColabActivity`, seção 6c) e importa o `laika_pacote.zip`. `exportar_modelo.py` converte os checkpoints (pesos em float16) para `app/src/main/assets/` (fora do Git). Ver seção 6b e `android/LEIA-ME.md`. |
| `windows/` | Scripts do pacote para Windows (`instalar.bat`, `conversar.bat`, `completar_texto.bat`, `instalar_indice.bat`, `rodar.py`, `LEIA-ME.txt`). Ver seção 6. |

## 4. Formatos

- Tokens especiais: `[PAD] [UNK] <|user|> <|assistant|> <|end|> <|endoftext|>`.
- Pesos do app: `LAIKA001` (posições aprendidas) ou `LAIKA002` (RoPE: sem `pos_emb`, cabeçalho com o theta em float32);
  o `exportar_modelo.py` e o `ConversorPt` geram os mesmos bytes.
- `data/carolina/*.txt` e `data/gigaverbo/*.txt`: documentos separados por uma linha `<|endoftext|>` (o tokenizer lê
  como o token de fim de texto).
- Exemplo de chat: `<|user|> pergunta <|assistant|> resposta <|end|>`. Nos arquivos `.txt`:
  `<|user|> pergunta` (quebra de linha) `<|assistant|> resposta <|end|>`, linha em branco entre exemplos;
  linhas com `#` antes do `<|user|>` são comentários. A resposta pode ter quebras de linha (poemas, diálogos);
  o que separa os exemplos é o `<|end|>`.
- Com contexto (RAG e `leitura.txt`): a pergunta vira `Contexto: <trecho>\nPergunta: <pergunta>`
  (`data_utils.rag_question`); com vários trechos, eles vão juntos (separados por espaço) no mesmo Contexto.
  Chat e fine-tuning precisam usar exatamente o mesmo formato.
- Conversa com histórico (memória de IA): as trocas anteriores vêm antes, separadas por espaço:
  `<|user|> q1 <|assistant|> r1 <|end|> <|user|> q2 <|assistant|>`. O contexto do RAG e a memória só entram na
  última pergunta. `data/qa/conversas.jsonl`: uma conversa por linha, lista de `[pergunta, resposta]`.
- Arquivos da Wikipédia (`data/wiki/wiki_NNN.txt`): blocos separados por linha em branco; um bloco curto
  sem pontuação final é o título do artigo, os seguintes são parágrafos.
- `data/modern/*.txt`: primeira linha = título, depois parágrafos.
- **Não edite `data/qa/pergeresp.txt` à mão**: ele é sobrescrito pelo gerador. Edite as tabelas em
  `tools/` e rode `python tools/gerar_pergeresp.py`, ou crie outro `.txt` em `data/qa/`.

## 5. Comandos

```bash
# Local (CPU), teste rápido
pip install torch tokenizers numpy
python prepare_data.py --max-books 20 --wiki 2000
python train.py --preset tiny
python rag.py build
python finetune.py --epochs 1
python chat.py

# Regenerar exemplos escritos
python tools/gerar_pergeresp.py

# Modelo de 100M (A100): ver TREINO_100M.md
python prepare_data.py --max-books 500 --wiki -1 --carolina --gigaverbo 1.5e9
python train.py --preset colab_100m --compile --tokens-backup /content/drive/MyDrive/LLM_Laika/tokens

# Modelo de 50M (Colab): muitos dados e tokenizer novo
python prepare_data.py --wiki 1000000        # ou --wiki -1 (todos); se cair, rode de novo que continua
python train.py --preset colab_50m           # parou no limite de tempo? repita com --resume

# Orquestrador do Colab CLI (usado pelo GitHub Actions; os testes usam um CLI falso)
python colab/laika_colab.py celulas
python colab/teste_laika_colab.py
```

Opções úteis: `finetune.py --epochs 4 --max-qa-repeat 3 --patience 3 --qa-share 0.25 --rag-share 0.5 --no-rag`;
`train.py --preset colab --resume --max-steps N`; `chat.py --no-rag --no-memory --temperature 0.7`.

No Colab, as pastas `data/books`, `data/wiki`, `data/qa_auto`, `data/rag` e `checkpoints` são **atalhos
para o Drive** (`/content/drive/MyDrive/LLM_Laika/...`), criados pela célula 1.

## 6. Pacote para Windows (`LaikaLocal`)

Montagem: pasta com `chat.py model.py data_utils.py rag.py memory.py` + tudo de `windows/` na raiz +
`checkpoints/{finetuned.pt, pretrain_best.pt, tokenizer.json}` + `data/modern/*.txt` + opcionalmente
`data/rag/laika_rag.db`. O `instalar.bat` cria `.venv` e instala o torch de CPU
(`--index-url https://download.pytorch.org/whl/cpu`), `tokenizers` e `numpy`. O `rodar.py` confere os
arquivos, verifica se o SQLite tem FTS5, procura o índice (em `data/rag`, na raiz ou em `Downloads`,
aceitando `laika_rag (1).db`) e, se não achar, monta um índice pequeno com `data/modern`.
Os `.bat` são ASCII com CRLF. Nada disso foi testado num Windows real.

## 6b. App Android (`android/`)

- `core/` (Java puro, roda no Android e no PC): `Modelo` (TinyLLM + KV cache + threads), `Tokenizador`
  (BPE byte-level), `Laika` (`build_prompt`/`generate`), `IndiceRag` (FTS5, mesma pontuação do `rag.py`),
  `Memoria` (mesmo `memoria.json`), `Texto` (`content_words`, `wants_rag`, `fit_context`).
  **Qualquer mudança no formato do prompt, no `rag.py`, no `memory.py` ou no `model.py` precisa ser
  repetida aqui**; rode `python android/core/referencias.py --checkpoints checkpoints` e `./gradlew :core:test`.
- `app/`: telas de chat, versões e Colab (Views, sem Compose), `Motor` com uma thread de fundo. SQLite próprio
  (`androidx.sqlite:sqlite-bundled`, tem FTS5). O índice pequeno (`laika_rag_mini.db`) vai no APK; o
  `laika_rag.db` completo é importado pelo menu (não cabe no APK). minSdk 26, targetSdk 35.
- `Modelo` lê `LAIKA001` e `LAIKA002` (RoPE: tabelas cos/sin em float32 como o `rope_tables`); acima de 60M de
  parâmetros (`LIMITE_COMPACTO`) guarda as matrizes em float16 (`short[]` + tabela de 65536 floats, mesma soma, logits
  idênticos) e o `Cache` cresce dobrando até o `block` (2048 × 12 camadas reservado de uma vez seriam ~150 MB).
  `RopeTest` confere com um checkpoint `tiny_rope` (`referencias.py --rope <pt>`). O limite da barrinha de tamanho
  depende da janela (`Motor.tamanhoMaximo`: 120 / 200 / 400).
- Conversa no processador (com 7M parâmetros é mais rápido, ~5 ms/token no PC). O de 50M foi conferido no PC
  (logits iguais ao PyTorch, diferença 1,6e-6; ~35–40 ms/token; ~260 MB de memória com pesos em float32). O `Motor`
  mantém um modelo grande por vez (`grande()`: > 20 M de parâmetros nas camadas): ao trocar entre conversar e
  completar texto, libera o outro, e avisa se faltar memória. A importação pede espaço livre de ~1,3× o zip.
- **Versões e backups** (`core/Armazem`): versão = modelos + tokenizer + índice + memória + conversa; arquivos
  grandes em `blobs/`, compartilhados entre backups. `ConversorPt` lê os `.pt` (pickle mínimo) no celular, com
  saída idêntica ao `exportar_modelo.py` (que agora grava um rodapé `INFO` com val loss, step e se é de chat).
- **Backups (1.9)**: a versão em uso guarda `origem` (o backup de onde veio, apagado quando os arquivos mudam).
  Ao trocar de modelo com mudanças, `SeletorModelos.confirmarUso` oferece "Salvar por cima de <origem>"
  (`Armazem.salvarPorCima`, só se os arquivos forem os mesmos: `origemDoAtual`), "Guardar como backup novo" ou "Trocar sem
  guardar". Na tela de versões, "Limpar" apaga a conversa e/ou a memória de um backup (`Armazem.limpar`). Um pacote com
  `laika_nome.txt` (PROJETO) vira um backup com esse nome (`backupComTrocas`: arquivos da versão em uso + os novos, a
  memória do usuário, sem conversa; nome repetido ganha a data), sem trocar a versão em uso, e o app oferece "Usar agora".
  A tela Treinar mostra o `PROJETO` da célula 1 (o `RAMO` continua vindo do GitHub).
- **Zip único** (`core/Pacote`): o `laika_pacote.zip` da célula 6 (ou o artefato baixado pela tela Colab, ou o
  `laika_dados.zip` antigo) é lido direto do fluxo; `Pacote.tipo()` olha só a primeira entrada (backup do app,
  checkpoint do PyTorch ou pacote). Modelos, tokenizer, índice e memória viram entradas do `Importador`
  (reconhecidas pelo conteúdo); os textos de `books/`, `wiki/` e `modern/` vão para um `Corpus` temporário e o
  celular monta o índice (`core/dados/ConstrutorIndice`, igual ao `rag.py build`, mais os `data/modern` que vão
  no APK). Tudo vira uma versão nova; a anterior vai para os backups. Importações longas rodam no
  `TrabalhoService` (primeiro plano, `dataSync`) e podem ser canceladas.
- **Tela de conversa (1.4)**: o chip do topo (nome da versão) abre o `SeletorModelos` (painel que sobe do rodapé com
  a versão em uso e os backups; um toque troca). O menu ⋮ é o `MenuOpcoes` (`PopupWindow`): grupo "Opções" que
  abre e fecha com as caixinhas (fontes, RAG, memória do usuário, **memória de IA** = pref `historico`, **respostas longas** = pref `longas` (1.6:
  `Motor` acrescenta `Texto.GATILHO_LONGO` e usa o `tamanhoMaximo()`), modo completar),
  barrinhas de **Temperatura** (nome desde a 1.9; antes "Criatividade"; 0,10–1,50, passo 0,01, com − e +) e tamanho (16–120 tokens), e os itens memória, versões,
  **Treinar** e limpar. Sem leitura em voz alta, sem "Sobre" e sem compartilhar a conversa. O teclado não abre ao
  entrar (`stateHidden`). Pontinhos de "digitando", a tela só acompanha a resposta se estiver no fim (botão ↓).
  As ações da bolha (tocar ou segurar) são o `AcoesBolha`: barra flutuante com ícones acima da bolha (Copiar; Editar
  nas do usuário; Trecho lido e Gerar outra nas da Laika), sem compartilhar nem selecionar texto (1.5).
  Cada bolha mostra os tokens (pergunta: os dela; resposta: tempo, tokens/s, tokens da resposta e o total com o prompt, `Opcoes.tokensPrompt`). O `Motor.historicoAte()` monta as trocas (pula avisos, erros, respostas interrompidas e o modo completar, que fica
  marcado na conversa salva como `"x"`); "Gerar outra resposta" usa o histórico de antes da pergunta.
- **O treino no celular (GPU) foi retirado** na versão 1.2 do app, a pedido do usuário; o treino fica no Colab,
  ligado pela tela Colab. O que sobrou dele é só a montagem do índice a partir de textos.
- Testes do núcleo: `ComparaComPythonTest`, `VersoesTest`, `PacoteTest`, `dados/IndiceTest` (índice igual ao do
  `rag.py`), `colab/ColabTest` (leitor do notebook igual ao do `laika_colab.py` e o cliente do GitHub contra um
  servidor falso). Com os checkpoints: `LAIKA_CHECKPOINTS=<pasta> LAIKA_LIVROS=<pasta com um livro> ./gradlew :core:test`.
- Só o modelo em `model.py` (posições aprendidas, GELU exato, pesos compartilhados) é suportado; RoPE
  (Fase 2) exige mudar `Modelo.java` e o formato do `exportar_modelo.py`.

## 6c. Colab pelo app (Colab CLI, sem deixar o Colab aberto)

```
app (tela Colab) --API do GitHub--> workflow colab.yml (runner Linux) --Colab CLI--> máquina do Colab (GPU + Drive)
       ^   verificação "Laika no Colab" (andamento, link do Drive, últimas linhas)  |
       '--- artefato laika_pacote (zip da célula 6) <-------------------------------'
```

- O Colab CLI (`pip install google-colab-cli`, Python ≥ 3.12, Linux/macOS) não roda no Android; por isso o
  runner do GitHub Actions faz a ponte. A permissão do Google vem do segredo `COLAB_ADC` (credencial ADC do
  `gcloud` com os escopos `openid`, `cloud-platform`, `userinfo.email` e `colaboratory`), gravado pela célula 0.
- `core/colab/Caderno` lê as células como o `laika_colab.py` (o teste compara os dois); `core/colab/GitHub` é o
  cliente REST (disparo com `return_run_details`, procura pelo código do pedido no `run-name` como reserva,
  verificação, cancelar, `sinal.yml`, artefatos com redirecionamento sem o token).
- No app: `ColabActivity` (tela **Treinar**: configuração, células com os campos `#@param`, atalhos, GPU, execuções com o andamento
  ao vivo, autorização do Drive, cancelar, registro, "Modelos prontos"; atalhos "1 milhão de artigos" = célula 2
  sem GPU, e "Modelo de 50M" = células 3, 4 e 6 com `colab_50m`, `do_zero` e A100), `Colab` (token em `noBackupFilesDir`,
  execuções acompanhadas), `ColabJob` (JobScheduler, consulta a cada ~3 min e notifica) e `ColabReceiver`
  (botão "Já autorizei" da notificação).
- Antes de funcionar: o branch com `.github/workflows/` precisa estar no `main` (o `workflow_dispatch` só
  aparece para workflows do branch principal); token fine-grained com Actions (leitura e escrita), Secrets
  (leitura e escrita) e Contents (leitura); rodar a célula 0 no navegador uma vez.
- O repositório é público: os registros do Actions, a verificação e os artefatos também são. O orquestrador
  tira e-mails e tokens do que publica e não imprime o link de autorização no registro (só na verificação).
- **Não testado com o Colab de verdade** (o ambiente de desenvolvimento não tem a conta Google): só com o CLI
  falso e a API falsa. Na primeira vez, acompanhe pela tela Colab e pelo registro do Actions.

## 7. Decisões e lições (não desfazer sem motivo)

1. **O chat decodifica só os tokens gerados.** O `decode` remove tokens especiais, então dividir o texto por `<|assistant|>` não funcionava e a pergunta aparecia repetida na resposta.
2. **Loss só na resposta** no fine-tuning (pergunta com label -100).
3. **O fine-tuning decorava o pergeresp** (78 exemplos, treino 0,12 × validação 2,78) e respondia tudo com ele. Solução: misturar sintéticos dos livros, replay e limitar a fração e as repetições dos exemplos escritos.
4. **O modelo de 14M decorava 4M tokens** (treino 3,0 × validação 4,9) → preset de 7M com dropout 0,2.
5. **Validação de cada arquivo**, não só do último (antes media um livro só).
6. **Memória do usuário fora do modelo** (JSON): vale entre conversas e não gasta a janela. O histórico da conversa (memória de IA, item 13) entra no prompt desde a 1.4.
7. **RAG conservador**: contexto errado atrapalha mais do que nenhum. Por isso existe o limite de confiança e o bloqueio para conversa, perguntas pessoais (pronomes), pedidos de tarefa e contas (`wants_rag`).
8. **Dados com numpy** no `train.py` e amostragem de texto (`--max-text-mb 40`) no `finetune.py`, para caber na RAM com 100 mil artigos.
9. **Legal**: só textos de domínio público ou com licença aberta. Traduções modernas têm direito do tradutor. Não raspar sites de notícias.
10. **Pedidos "sobre X" buscam só X no RAG** (`rag_queries`): "Faça um texto sobre planárias" achava o
    artigo errado porque as palavras do pedido (faça, texto) pesavam na busca. O Java faz o mesmo (`Texto.consultasRag`).
11. **Frase incompleta não vai para o modelo**: "Meu nome é" sozinho fazia o modelo repetir a frase; a memória
    responde pedindo o resto e não grava nada (Python e Java).
12. **Perguntas genéricas escritas à mão** (`tools/genericas_*.py`): o modelo pequeno precisa ver muitos tipos de
    pedido (texto sobre X, "E X?", por quê, como, diferenças, conversa) com respostas boas. Cada tema tem resposta
    curta e parágrafo; política e religião ficam neutras. Com 7,6 mil exemplos escritos, o `--synthetic` subiu
    para 10 mil para não mudar muito a mistura (escritos ~37% dos exemplos de chat).
13. **Memória de IA no prompt** (pedido do usuário na 1.4): o modelo só entende "E da Itália?" vendo a troca
    anterior. O contexto do RAG tem prioridade; o histórico usa o que sobra da janela (com 256 tokens e RAG, quase
    nada; com 512, ~5 trocas). O fine-tuning precisa ver históricos (conversas.jsonl e `--history-share`), senão o
    modelo se confunde com o prompt mais longo. As respostas da tabela de seguimento ("Por quê?", "Pode repetir?")
    não dizem mais "não vejo as mensagens anteriores".
14. **RAG pelo nome próprio**: "O que Santos Dumont inventou?" tinha nota 1,75 (< 1,8) com a pergunta inteira; buscar
    só "Santos Dumont" acha o artigo. A pergunta inteira continua sendo tentada primeiro, e na busca só pelo nome
    os textos de `data/modern` também precisam da nota mínima (senão "França" puxava "O Império Romano").
15. **Perguntas da Wikipédia com contexto**: o modelo pequeno não guarda fatos, então o fine-tuning ensina a *ler* o
    trecho (padrões "nasceu em", "fica em", "fundada em", "inventou"...), mais 10% de trechos errados com "não sei".
16. **Tamanho da resposta**: a barrinha vai até 120 (mais que isso tira espaço do histórico na janela de 256); acima de
    60 tokens o `<|end|>` é penalizado no começo (3,0 decaindo até zero na metade do que passa de 60).
17. **Memória de IA só em seguimento** (1.5): com o histórico em toda pergunta, o modelo repetia a resposta anterior
    em perguntas sem relação. `follows_up` decide (Python e Java, `Texto.segueConversa`); o fine-tuning continua
    misturando históricos sem relação (`--history-share`), o que ensina a ignorá-los.
18. **100M com RoPE e contexto 2048** (pedido do usuário): posições aprendidas de 2048 seriam 1,6M de parâmetros que
    aprendem devagar; o RoPE não tem parâmetros. Os presets antigos continuam com `pos_emb` (checkpoints compatíveis).
19. **GigaVerbo por grupos de linhas, de todos os arquivos**: cada parquet do `edu_high` vem de uma fonte (o primeiro é
    todo `mc4_pt`), então pegar os 3 primeiros arquivos inteiros daria só 3 fontes. O Carolina vai sem leis e decisões
    judiciais por padrão (~45% do corpus, estilo muito formal) e sem a Wikipédia que vem dentro dele.
20. **Respostas longas de até ~150 palavras**: cabem na janela de 256 do 7M (a maior tem 252 tokens), então servem a
    todos os modelos; com 2048 tokens, a barrinha do app vai até 400.
21. **Gatilho de resposta longa** (1.6, pedido do usuário): "Explique melhor." / "Resposta longa." no fim da pergunta
    pede o texto longo; no fine-tuning, a mesma pergunta sem gatilho tem a resposta curta. A opção do app só acrescenta
    " Resposta longa." (`Texto.GATILHO_LONGO`) e aumenta o tamanho até o máximo. O gatilho sai da busca (RAG, memória,
    seguimento): senão "Resposta longa" virava palavra de busca; sozinho ("Resposta longa."), conta como seguimento.
22. **Sem "O que é madeira/areia?"** nos exemplos (pedido do usuário, para testar se a Laika monta a resposta). O
    conhecimento da Wikipédia também os deixa de fora (`--conhecimento-excluir`). Os artigos "Madeira" e "Areia"
    existem no índice: para testar a generalização, desligue o RAG.
23. **"Laika" é a IA ou a cadela** (1.7): "laika" na lista de palavras pessoais desligava o RAG em "Pesquise sobre a
    cadela Laika", e o modelo inventava tudo. Com palavras como cadela, Sputnik, espaço, soviética, é a cadela. E
    "Você sabe o que é um vulcão?" não é pergunta pessoal (`_POLITE`).
24. **Radical leve em vez de 5 letras** (1.7): o prefixo juntava capital/capítulo, Portugal/português,
    planeta/planejamento. Tirar a vogal final também foi descartado ("pedra" viraria "Pedro").
25. **Textos de `data/modern` com nota mínima** (1.7): numa pergunta de uma palavra, qualquer texto com a palavra
    passava ("O que é pedra?" → "As pirâmides do Egito"). Agora precisam da nota ou de uma palavra no título.
26. **Fine-tuning como fonte de conhecimento** (1.7): um fato só fica guardado com muitas exposições em frases
    variadas, e o pré-treino viu cada artigo ~1 vez. Por isso os artigos importantes viram perguntas sem contexto,
    4 formas por fato, 2× por época. Só fatos da Wikipédia que o modelo já leu (ensinar fatos novos no
    fine-tuning aumenta a invenção, segundo Gekhman et al., 2024).
27. **GigaVerbo-v2-SFT** (1.7): os pesos continuam do zero; o conjunto (gerado por outra IA, como os exemplos escritos
    em `tools/`, que também foram escritos por uma IA) só entra como pergunta e resposta. Exemplos que citam outra IA
    são descartados, para não estragar a identidade da Laika.

28. **Buscas do fine-tuning em paralelo e com cache** (1.7): com a Wikipédia inteira, ~13 mil buscas em sequência
    levavam mais de 1 h com a A100 parada e sem mensagem. Mude `RAG_VERSAO` quando mexer na busca, senão o cache
    antigo é reaproveitado.

29. **Lotes agrupados por tamanho no fine-tuning** (1.7): com o SFT, quase todo lote sorteado de 16 tinha uma conversa
    longa, e os outros 15 exemplos eram completados com enchimento até ela; cada época do 100M levaria horas sem
    nenhuma mensagem. Continua com até 16 exemplos por lote (o mesmo número de atualizações; com 32 ou 64 por lote a
    perda do teste ficou pior), só sem o enchimento.

30. **Datas de acontecimentos e sem extenso** (1.8): o modelo achava o artigo "Queda de Constantinopla" e errava a data,
    porque a leitura da Wikipédia não tinha o padrão "ocorreu/aconteceu em 29 de maio de 1453"; agora tem (data, ano,
    "liderada por"). As respostas não trazem mais o ano por extenso ("(mil oitocentos...)" aparecia no meio das
    respostas); os séculos em algarismos romanos ficam. O ano por extenso continua só nas perguntas de conversão.
31. **Nome no Contexto** (1.8): "Faça uma frase com o meu nome" não tinha como saber o nome; a memória põe o nome
    no Contexto, como as anotações (Python e Java). "O nome dele" vem do histórico (seguimento).
32. **"Sou o rei do Reino Unido"** (1.9): o GigaVerbo-v2-SFT tem muitos pedidos de faz de conta ("Assuma o papel do
    rei...", "Você é um rei medieval. Qual é o seu nome?"), e o `converter_sft` tira a mensagem de sistema, onde às vezes
    estava o personagem; com 300 mil conversas contra ~400 exposições de identidade, "Qual é o seu nome?" virava um
    personagem, e temperatura baixa não ajuda (só deixa a resposta mais provável mais certa). Correções feitas: o nome da
    Laika não vai mais para o Contexto em perguntas sobre o nome (o 1.8 punha, num formato que o modelo nunca viu com a
    identidade), +164 exemplos de identidade com negações de personagem, conversas sobre reis seguidas de "Quem é você?",
    `--identity-share` e 4 perguntas na avaliação. Filtrar os personagens do SFT (e baixar de novo) ficou de fora, a pedido.
33. **PROJETO** (1.9): o `do_zero` de um modelo pequeno apagava o pré-treino, o tokenizer e a cópia dos tokens do 100M.
    Cada projeto tem as suas pastas; os dados baixados são de todos. **NOME separado** (1.9.1): o usuário pôs um
    PROJETO só para dar nome ao fine-tuning do 100M, a pasta nova estava vazia e a célula 4 falhou (sem tokenizer).

## 8. Limitações conhecidas

- O de 100M nunca foi treinado de verdade (só o `tiny_rope` em CPU); tempo e unidades do `TREINO_100M.md` são estimativas.
- 100M no celular: ~210 MB de pesos em float16 e bem mais lento (prompt longo com RAG e histórico pode levar dezenas de segundos).
- O `--resume` continua do `pretrain_last.pt` só se o preset e o tokenizer forem os mesmos; trocar de preset exige `do_zero`.
- **Posições aprendidas** (presets até 50M) limitadas a `block_size`: mudar o contexto exige refazer o pré-treino. O RoPE
  (100M) também foi treinado só até 2048.
- GigaVerbo e Carolina têm licenças por fonte (texto da web no GigaVerbo, inclusive notícias): só pré-treino, nunca no RAG.
- O tokenizer foi treinado com muito português antigo do Gutenberg ("chronica", "portuguez").
- O resumo sintético é **extrativo** (escolhe a frase mais representativa), não um resumo de verdade.
- Com 1 milhão de artigos, o índice RAG passa de ~4 GB (o de 100 mil tem 636 MB): o celular importa se houver
  espaço (~1,3× o arquivo), mas demora; para o app, o índice de 100 mil artigos costuma bastar.
- O `finetuned.pt` é sobrescrito, mas o anterior vai para `checkpoints/backups/` (os 3 últimos).
- Memória baseada em expressões regulares (frases fora dos padrões não são guardadas).
- Memória de IA limitada pela janela: com 256 tokens, uma pergunta com RAG quase não deixa espaço para o histórico.
  Os checkpoints treinados antes da 1.4 nunca viram históricos: é preciso refazer o fine-tuning (célula 4).
- Busca com radical leve (plural e verbos), sem embeddings. "Laika" sozinha (sem cadela, espaço...) continua sendo
  pergunta sobre a IA, sem RAG.
- Não há testes automatizados do treino em Python (só os do app e do orquestrador do Colab); o `avaliar.py` mede a
  qualidade, mas o banco tem só 112 perguntas e a nota é por palavras-chave.
- O conhecimento sem contexto escolhe os artigos pelo tamanho (o download guarda só 8 parágrafos de cada um, então
  muitos empatam) e pela ordem de criação; não há contagem de visitas nem de links.
- O controle do Colab pelo app depende do Colab CLI (ferramenta nova do Google; a interface pode mudar) e não
  foi testado contra o Colab de verdade.

## 9. Plano futuro (combinado com o usuário, ainda não implementado)

O usuário pretende assinar o **Google AI Pro** (200 unidades de computação do Colab por mês, A100 e,
provavelmente, 2 TB no Drive; o Colab CLI permite rodar scripts sem o navegador). Com isso, o objetivo é:

**Configuração alvo:** ~**100M de parâmetros** (768 dim, 12 camadas, 12 cabeças), **contexto 2048**,
**RoPE** no lugar das posições aprendidas, vocabulário BPE de ~24 mil, ~**2 bilhões de tokens** de treino
(20 tokens por parâmetro; 3 a 4 bilhões também seria bom para um modelo pequeno). Etapa intermediária
opcional: ~30M, contexto 1024, ~600M tokens.

### Fase 0 — Infraestrutura (fazer antes de gastar unidades)
- [x] Cache de atenção (KV cache) no modelo e no `generate()`; saída idêntica à versão sem cache (conferido).
- [x] Retomada completa: `pretrain_last.pt` com otimizador, scaler, step e geradores aleatórios; `--resume` continua de onde parou.
- [x] Acumulação de gradiente (`accum` no preset).
- [x] bf16 na A100 (`torch.cuda.is_bf16_supported()`), TF32 e `--compile`.
- [x] Tokens pré-processados em disco (`uint16` com `np.memmap`, em `data/tokens/`).
- [x] Backup automático do `finetuned.pt` com data e hora (`checkpoints/backups/`).
- [x] Script de avaliação (`avaliar.py`, célula 7): perplexidade fixa, 112 perguntas por categoria e a busca do RAG.

### Fase 1 — Dados
- [~] Wikipédia inteira (~1,1 milhão de artigos; ~200–400 M tokens): o `prepare_data.py --wiki -1` já baixa tudo,
  continuando de onde parou (célula 2: `ARTIGOS = "todos"`, sem GPU). Falta medir o tempo e o tamanho reais.
- [ ] Wikisource em português (dumps) e os livros do Gutenberg (só ~650 em português existem lá).
- [x] **GigaVerbo-v2** (`Polygl0t/gigaverbo-v2`, ~320 bilhões de tokens, sem licença única): `prepare_data.py --gigaverbo`, só `edu_high` e toxicidade ≤ 2.
- [x] **Corpus Carolina** (`--carolina`, sem leis/judiciário por padrão).
- [x] Retreinar o tokenizer (~24 mil) com uma amostra equilibrada (`tokenizer_mb`, dividida entre as pastas).
- [ ] Remover duplicatas e textos curtos demais.

### Fase 2 — Pré-treino
- [x] Preset `colab_100m`, RoPE, contexto 2048 (Python, exportador, `ConversorPt` e `Modelo.java`). Falta treinar de
  verdade e, se quiser, um `colab_30m` intermediário.
- [ ] Estimativa na A100: ~8,5 h para 2 bilhões de tokens com contexto 2048 (~45 a 125 unidades, pois o consumo da A100 varia de 5,4 a 15 unidades por hora conforme a fonte). Com 1024: ~7 h.
- [ ] Otimizações para um próximo pré-treino (analisadas, deixadas para depois; no Colab só há uma GPU, então não há
  ganho com várias GPUs, e a parte do processador já é paralela/sobreposta): AdamW `fused=True` (~5%); calcular a perda
  sem converter os logits inteiros para float32 (16 × 2048 × 24 mil ≈ 3 GB por micro-lote), em pedaços, o que libera
  memória para lotes de 32 com metade da acumulação (~10–20%); junto com o `--compile`, ~15–30% a menos de tempo.
- [ ] Opcional: fase curta de extensão para 8k (~5% dos tokens, ~1 h), só como experimento. 16k/32k não compensam para este tamanho (custo de 4 a 7 vezes e o modelo não aproveita).

### Fase 3 — Fine-tuning
- [~] Exemplos com vários trechos de RAG por pergunta (até 3, conforme a janela) e conversas com várias mensagens
  (`conversas.jsonl` e `--history-share`, até 5 trocas). Falta aproveitar a janela de 2048 (mais trechos e trocas).
- [x] `Polygl0t/gigaverbo-v2-sft` (Apache 2.0) como dados de instrução: `prepare_data.py --sft`, célula 2 (`SFT`).
- [x] Fine-tuning como fonte de conhecimento: perguntas sem contexto dos artigos importantes (`--conhecimento`).
- [x] Até 6 trechos do RAG com janela 2048 e `--rag-share 0.7`.

### Fase 3b — Conhecimento, para depois (combinado com o usuário: guardar, ainda não implementar)
Em ordem do que mais ajuda:
1. **Recozimento no fim do pré-treino**: continuar o pré-treino do 100M por ~100–200 milhões de tokens com taxa de
   aprendizado baixa, numa mistura de parágrafos iniciais dos ~20–50 mil artigos mais importantes repetidos ~5×,
   `data/modern` e os exemplos escritos (~1 h na A100). É o jeito mais natural de pôr fatos nos pesos.
2. **A mesma pergunta com e sem contexto**: cada fato do conhecimento também na versão com o trecho do artigo, para o
   modelo aprender a usar o trecho quando ele existe e a memória quando não existe.
3. **Exemplos de "não sei"** para nomes raros sem contexto (~3–5%, para não virar "não sei" para tudo).
Referência de quantidade: mínimo útil ~5 mil assuntos × 3 fatos × 5 formas ≈ 75 mil exemplos; bom para o 100M ~20 mil
assuntos ≈ 300 mil (~18 milhões de tokens por época, ~10–15 min na A100). Mais perguntas de molde não ajudam: o
formato já está coberto pelos ~15 mil escritos + sintéticos + leitura; falta variedade (SFT) e repetição de fatos.
- [ ] Manter os exemplos escritos em `tools/` e a identidade da Laika.

### Fase 4 — RAG
- [ ] Índice com a Wikipédia inteira + Wikisource + livros (~4–5 GB). **Não** indexar o GigaVerbo.
- [ ] Vários trechos por pergunta quando a janela permitir; manter o limite de confiança.
- [ ] Opcional: busca por embeddings como segunda etapa de ordenação.

### Fase 5 — Windows
- [x] KV cache no `chat.py`. Opcional: salvar pesos em fp16 para o arquivo ficar menor.
- [ ] Tempo estimado por mensagem no processador (4–8 núcleos), com cache: 100M ~3–6 s numa pergunta com RAG, ~6–12 s com ~2000 tokens de prompt. Sem cache seria de dezenas de segundos a minutos.
- [ ] Atualizar o pacote e o LEIA-ME.

### Mais ideias
Ver `SUGESTOES.md`: 25 sugestões que não estão neste plano (RMSNorm/SwiGLU, GQA, WSD, annealing com dados
melhores, ortografia antiga, exemplos de "não sei", contexto errado de propósito, 👍/👎 no app → DPO,
int8 e decodificação especulativa no celular, histórico de treinos...).

### Alternativa discutida
Fazer só o fine-tuning de um modelo aberto já treinado em português (ex.: **Tucano2-0.6B**, licença
permissiva) daria um resultado bem melhor, mas o projeto deixaria de ser "do zero". Decisão do usuário.

## 10. Preferências do usuário

- Respostas e interface em **português do Brasil**; comentários do código em português.
- Ele trabalha principalmente no **Colab** (Drive para persistência) e quer rodar a IA no **Windows**.
- Pediu antes: pré-treino com no máximo ~15 mil steps (no preset atual), fine-tuning com menos épocas que antes,
  muitos exemplos escritos à mão, citação `*Título` no RAG.
- Quando pedir "só analise" ou "não implemente", não altere código.
- Commits: o usuário é o autor; mensagens em português explicando o porquê.

## 11. Sugestão de primeiro pedido no Claude Code

> Leia o CLAUDE.md. Implemente a Fase 0 do plano (KV cache, retomada completa, acumulação de gradiente,
> bf16/compile, tokens em disco com memmap, backup do finetuned e script de avaliação), sem mudar o
> comportamento dos presets atuais. Teste com `--preset tiny` em CPU antes de terminar.
