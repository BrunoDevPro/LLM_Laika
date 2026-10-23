# LLM Laika — guia do projeto para o Claude Code

Este arquivo é lido automaticamente pelo Claude Code. Ele resume o que o projeto é, como está
organizado, por que as decisões foram tomadas, os números medidos e os próximos passos planejados.
Escrito em 22/10/2026; atualizado em 23/10/2026 (app 1.2: Colab pelo app, zip único, sem treino no celular;
app 1.3: preset de 50M, Wikipédia com até 1 milhão de artigos, +3.300 perguntas genéricas;
app 1.4: memória de IA (histórico no prompt), RAG com vários trechos e busca pelo nome próprio, ~20 mil perguntas
da Wikipédia com contexto, taxa de aprendizado automática, menu novo no app).

## 1. O que é

A **Laika** é um modelo de linguagem pequeno (transformer estilo GPT), **treinado do zero em PyTorch,
em português**, com:
- pré-treino em livros do Project Gutenberg, artigos da Wikipédia em português e textos escritos para o projeto;
- fine-tuning de perguntas e respostas (formato de chat);
- **RAG** (busca em artigos e livros com SQLite FTS5) que coloca um trecho como "Contexto:" no prompt e
  cita a fonte no fim da resposta (`... *Nome do artigo`);
- **memória do usuário** (nome, cidade, gostos, "lembre que...") fora do modelo, em JSON;
- **memória de IA**: as últimas trocas da conversa (até 5) entram no prompt, quantas couberem na janela;
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
| Exemplos de fine-tuning escritos | `pergeresp.txt` 7025 + `identidade.txt` 110 + `leitura.txt` 512 = **7647** (3333 deles são as perguntas genéricas de `tools/genericas_*.py`) + `conversas.jsonl` com **1061** conversas de 2 a 3 trocas |
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
| `model.py` | `TinyLLM`: atenção causal (`F.scaled_dot_product_attention`, `is_causal=True`), pré-LayerNorm, GELU, pesos compartilhados entre embedding e saída, **posições aprendidas** (`pos_emb`, tamanho = `block_size`). `build_model(config)` cria a partir do dict salvo no checkpoint. |
| `config.py` | Presets: `tiny` (CPU, ~1,3M), `colab` (~7M, o atual), `colab_big` (~14M) e `colab_50m` (~52M: 512 dim, 14 camadas, 8 cabeças, contexto 512, vocabulário 16 mil, lote 32 × acumulação 2; pede MODO `do_zero` e muitos dados, como a Wikipédia com 1 milhão de artigos). `accum` (acumulação de gradiente) é opcional no preset. |
| `train.py` | Pré-treino. Lê `data/books`, `data/wiki` e `data/modern` (esta 3×). Treina o tokenizer BPE (byte-level) se não for `--resume`. Validação = últimos 5% de **cada** arquivo. Os tokens vão para `data/tokens/` (uint16, lidos com `np.memmap`, reaproveitados enquanto os textos e o tokenizer não mudam), então a RAM não limita o tamanho dos dados. Acumulação de gradiente (`accum`), bf16 na A100/L4 (fp16 + GradScaler na T4), TF32, early stopping, cosine com warmup. Salva o melhor em `checkpoints/pretrain_best.pt` (`model`, `config`, `step`, `val_loss`) e, a cada validação, `pretrain_last.pt` (pesos, otimizador, scaler, step, geradores aleatórios): `--resume` continua dele do ponto exato (ex.: depois do limite de 6 h do GitHub Actions); se o treino já tinha acabado, parte do melhor com um agendamento novo. O `last` é apagado no fim. |
| `finetune.py` | Parte do `pretrain_best.pt` e grava `checkpoints/finetuned.pt` (**sobrescreve** a cada melhora, sem backup). Loss só nos tokens da **última** resposta. Taxa de aprendizado automática (`--lr`): 5e-5 até 20M de parâmetros, 1e-4 acima. Memória de IA: as conversas de `data/qa/conversas.jsonl` e ~30% dos outros exemplos (`--history-share`) ganham de 1 a 4 trocas curtas anteriores (só se couber no bloco). Leitura da Wikipédia: `--wiki-leitura 20000` perguntas tiradas dos trechos (`--wiki-mb 40` de artigos; "Onde X nasceu?", "Quando X foi fundada?", "O que X inventou?", "Quantos habitantes tem X?"...) com o trecho como Contexto; 10% com o trecho de outro artigo e resposta "não sei"; com janela ≥ 512, metade ganha um segundo trecho do mesmo artigo. Mistura em cada lote: exemplos escritos (`data/qa/`, pelo menos ~25%; com os 7,6 mil atuais cada um aparece 1× por época, ~37%; identidade com peso extra), sintéticos (`--synthetic 10000`: continue/complete/frase com palavra/resumo extrativo dos livros + "O que é X?" da Wikipédia em `data/qa_auto/`) e replay de texto puro. Com o índice RAG, ~50% das perguntas que pedem informação ganham "Contexto:" (buscado com `rag.contexts`, igual ao chat). **2 épocas** por padrão. Mostra 8 respostas de teste por época. |
| `chat.py` | Conversa. `build_prompt(question, tokenizer, block, rag, memory, max_new, history)` (usado também pelo finetune) junta memória + RAG (`rag.contexts`, `rag_chunks(block)` trechos: 1 com 256, 2 com 512, 3 com 768+) e corta o contexto para caber na janela; depois põe antes as trocas do histórico, da mais nova para a mais antiga, enquanto couberem (até `MAX_HISTORY = 5`). A busca do RAG usa `rag_queries()`: em "Faça um texto sobre planárias", procura só "planárias"; senão, a pergunta e, se ela não achar nada com confiança, o nome próprio ("Santos Dumont"). Com `max_new_tokens` > 60, o `<|end|>` é penalizado no começo (`min_answer_tokens`, `end_penalty`), para respostas mais longas. `/limpar` esquece o histórico; `--no-history` desliga. `generate()` com top-k, top-p, penalidade de repetição (só nos tokens gerados). **Sem cache de atenção** (recalcula tudo a cada token). `with_citation()` adiciona ` *Título`. Comandos: `/fontes`, `/rag`, `/memoria`, `sair`. `--base` = completar texto com o pré-treino. |
| `rag.py` | `python rag.py build` monta o índice FTS5 (`title, text, kind, pos`; tokenizer `unicode61 remove_diacritics 2`) a partir de wiki/textos/livros, no disco local e depois copia; `RagIndex.best()` só devolve contexto com confiança (nota ≥ 1,8 ou fonte `texto`); `RagIndex.contexts(pergunta, k)` tenta cada consulta de `rag_queries` e devolve até k trechos (os extras do mesmo artigo, ordenados por quantas palavras da pergunta têm). Busca: título contendo todas as palavras + OR de palavras/prefixos; pontuação por cobertura, título igual, penalidade de parênteses/palavras extras/acentos diferentes ("Pele" × "Pelé"), proximidade, primeiro trecho do artigo. `python rag.py search "pergunta"` para testar. No Colab, copia o índice do Drive para o disco local antes de abrir. |
| `memory.py` | Memória por expressões regulares; salva em `checkpoints/memoria.json`. Responde direto "qual é o meu nome", "o que você lembra de mim", "esqueça tudo" e frases incompletas ("Meu nome é", "Eu moro em", "Lembre que" → pede o resto, sem gravar nada); anotações relacionadas entram no Contexto. Não muda o prompt de perguntas normais. |
| `data_utils.py` | Tokens especiais, limpeza do Gutenberg, leitura dos arquivos de QA, exemplos sintéticos, resumo extrativo, limpeza da Wikipédia e geração de "O que é X?", as perguntas de leitura da Wikipédia (`reading_examples`), o formato de conversa (`chat_turn`, `split_conversation`, `MAX_HISTORY`) e as funções do RAG: `content_words`, `wants_rag`, `request_topic` (assunto depois de "sobre", "a respeito de", "acerca de"), `question_name` (nome próprio mais longo), `rag_queries`, `rag_chunks`, `rag_question`, `fit_context`, `split_example`. |
| `prepare_data.py` | Baixa livros pt do catálogo CSV do Gutenberg (`--max-books 500`, grava `data/books/titulos.tsv`) e artigos da Wikipédia via Hugging Face `wikimedia/wikipedia` `20231101.pt` em streaming (`--wiki 100000`; `--wiki 1000000` ou `--wiki -1` = todos, ~1,1 milhão). O download continua de onde parou: cada `wiki_NNN.txt` completo fica registrado num `.pronto` (JSON), e aumentar o número só baixa o que falta. Mostra velocidade e tempo estimado. |
| `colab.ipynb` | 7 células: (0) ligar o app ao Colab (**só no navegador**, uma vez: login `gcloud` com os escopos do Colab CLI e grava o segredo `COLAB_ADC` no GitHub), (1) preparar/Drive (define `rodar()`, que para a célula se o comando falhar), (2) dados + índice RAG (`ARTIGOS`: 10 mil a 1 milhão ou todos), (3) pré-treino (`MODO = "pular" / "continuar" / "do_zero"`, `PRESET` com `colab_50m`; "continuar" retoma o `pretrain_last.pt`), (4) fine-tuning (`PERGUNTAS_WIKIPEDIA`), (5) conversar (**só no navegador**), (6) exportar para o celular (`laika_pacote.zip`: modelo e, opcionalmente, índice e textos). Os campos são formulários do Colab (`#@param`), que o app preenche. A primeira linha de cada célula é `# N) TÍTULO` (e `[só no navegador]` quando for o caso): o app e o `laika_colab.py` dependem disso. |
| `colab/laika_colab.py` | Orquestrador do **Colab CLI** (`google-colab-cli`), rodado pelo GitHub Actions: lê as células do notebook, aplica os parâmetros, liga a máquina (`colab new --gpu`), monta o Drive (repassando ao app o link de autorização, se vier), roda cada célula com `colab exec` (marca de fim + arquivo de estado na máquina, para sobreviver à queda da conexão), baixa o zip da célula 6 e desliga a máquina. Publica o andamento na verificação "Laika no Colab" (check run) que o app lê. Só biblioteca padrão. `python colab/laika_colab.py celulas` mostra as células em JSON. |
| `colab/teste_laika_colab.py` | Testes do orquestrador com um `colab` falso (kernel Python persistente de verdade, queda de conexão, kernel que reinicia, autorização do Drive, GPU recusada, cancelamento) e uma API do GitHub falsa. `python colab/teste_laika_colab.py`. |
| `.github/workflows/colab.yml` | Workflow disparado pelo app (`workflow_dispatch`: `celulas`, `gpu`, `parametros` em JSON, `pedido`). Uma execução por vez (`concurrency`), limite de 355 min, guarda o zip como artefato `laika_pacote` (14 dias) e sempre roda `colab stop` no fim. `sinal.yml`: o app avisa "Drive autorizado" disparando-o com `run-name = drive-ok-<id>`. |
| `SUGESTOES.md` | Ideias de melhoria da LLM que **não** estão no plano da seção 9 (arquitetura, dados, fine-tuning, celular, processo). |
| `tools/gerar_pergeresp.py` | **Gera** `data/qa/pergeresp.txt`, `identidade.txt`, `leitura.txt`, `conversas.jsonl` (`conversas()`: capitais e temas em sequência, "E X?", "Do que estávamos falando?", nome lembrado, "Pode repetir?") e `data/modern/simples_*.txt` a partir das tabelas em `tools/dados_extra*.py`, `tools/leitura.py`, `tools/textos_simples*.py` e `tools/genericas_*.py`. |
| `tools/genericas_*.py` | Perguntas **genéricas** (3333 exemplos). `genericas_temas1..5`: ~460 assuntos `(assunto com artigo, resposta curta, parágrafo)`, de onde saem "O que é X?", "Faça um texto sobre X." (e outras 11 formas), texto curto, "E X?", "Você sabe algo sobre X?", "Resuma em uma frase: <parágrafo>" e leitura com Contexto. `genericas_perguntas1..3` e `genericas_extra`: por quê, como fazer, o que fazer, diferenças, para que serve, como funciona, verdade ou mito, listas, pessoas, datas, opiniões (neutras em política e religião), conversa livre, curiosidades. `genericas_conversa`: mensagens incompletas, pedidos que dependem da mensagem anterior ("Por quê?", "Continue.": a Laika vê uma mensagem por vez e pergunta o assunto), identidade (vai para `identidade.txt`), limites, apoio (CVV 188, SAMU 192, 180, Disque 100) e escrita (poemas, histórias, mensagens). O gerador pula perguntas que já existem (mesmo texto, sem pontuação) e cria variações ("Me ensine a...", "Verdade ou mito:"...). |
| `android/` | **App Android** (APK) que roda a Laika no celular, sem PyTorch: o transformer com KV cache, o tokenizer, o RAG e a memória reescritos em Java (`android/core`), conferidos contra o Python por `core/referencias.py` + `gradle :core:test`. Também liga as células do Colab pela tela **Treinar** (`ColabActivity`, seção 6c) e importa o `laika_pacote.zip`. `exportar_modelo.py` converte os checkpoints (pesos em float16) para `app/src/main/assets/` (fora do Git). Ver seção 6b e `android/LEIA-ME.md`. |
| `windows/` | Scripts do pacote para Windows (`instalar.bat`, `conversar.bat`, `completar_texto.bat`, `instalar_indice.bat`, `rodar.py`, `LEIA-ME.txt`). Ver seção 6. |

## 4. Formatos

- Tokens especiais: `[PAD] [UNK] <|user|> <|assistant|> <|end|> <|endoftext|>`.
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
- Conversa no processador (com 7M parâmetros é mais rápido, ~5 ms/token no PC). O de 50M foi conferido no PC
  (logits iguais ao PyTorch, diferença 1,6e-6; ~35–40 ms/token; ~260 MB de memória com pesos em float32). O `Motor`
  mantém um modelo grande por vez (`grande()`: > 20 M de parâmetros nas camadas): ao trocar entre conversar e
  completar texto, libera o outro, e avisa se faltar memória. A importação pede espaço livre de ~1,3× o zip.
- **Versões e backups** (`core/Armazem`): versão = modelos + tokenizer + índice + memória + conversa; arquivos
  grandes em `blobs/`, compartilhados entre backups. `ConversorPt` lê os `.pt` (pickle mínimo) no celular, com
  saída idêntica ao `exportar_modelo.py` (que agora grava um rodapé `INFO` com val loss, step e se é de chat).
- **Zip único** (`core/Pacote`): o `laika_pacote.zip` da célula 6 (ou o artefato baixado pela tela Colab, ou o
  `laika_dados.zip` antigo) é lido direto do fluxo; `Pacote.tipo()` olha só a primeira entrada (backup do app,
  checkpoint do PyTorch ou pacote). Modelos, tokenizer, índice e memória viram entradas do `Importador`
  (reconhecidas pelo conteúdo); os textos de `books/`, `wiki/` e `modern/` vão para um `Corpus` temporário e o
  celular monta o índice (`core/dados/ConstrutorIndice`, igual ao `rag.py build`, mais os `data/modern` que vão
  no APK). Tudo vira uma versão nova; a anterior vai para os backups. Importações longas rodam no
  `TrabalhoService` (primeiro plano, `dataSync`) e podem ser canceladas.
- **Tela de conversa (1.4)**: o chip do topo (nome da versão) abre o `SeletorModelos` (painel que sobe do rodapé com
  a versão em uso e os backups; um toque troca). O menu ⋮ é o `MenuOpcoes` (`PopupWindow`): grupo "Opções" que
  abre e fecha com as caixinhas (fontes, RAG, memória do usuário, **memória de IA** = pref `historico`, modo completar),
  barrinhas de temperatura (0,10–1,50, passo 0,01, com − e +) e tamanho (16–120 tokens), e os itens memória, versões,
  **Treinar** e limpar. Sem leitura em voz alta, sem "Sobre" e sem compartilhar a conversa. O teclado não abre ao
  entrar (`stateHidden`). Pontinhos de "digitando", a tela só acompanha a resposta se estiver no fim (botão ↓).
  O `Motor.historicoAte()` monta as trocas (pula avisos, erros, respostas interrompidas e o modo completar, que fica
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

## 8. Limitações conhecidas

- **Sem cache de atenção** no `generate()`: aceitável com 7M/256 (alguns segundos por resposta), inviável para modelos maiores.
- O `--resume` continua do `pretrain_last.pt` só se o preset e o tokenizer forem os mesmos; trocar de preset exige `do_zero`.
- **Posições aprendidas** limitadas a `block_size`: mudar o contexto exige refazer o pré-treino.
- Sem `torch.compile` (a acumulação de gradiente, o bf16 e o TF32 já existem).
- O tokenizer foi treinado com muito português antigo do Gutenberg ("chronica", "portuguez").
- O resumo sintético é **extrativo** (escolhe a frase mais representativa), não um resumo de verdade.
- Com 1 milhão de artigos, o índice RAG passa de ~4 GB (o de 100 mil tem 636 MB): o celular importa se houver
  espaço (~1,3× o arquivo), mas demora; para o app, o índice de 100 mil artigos costuma bastar.
- O `finetuned.pt` é sobrescrito sem backup.
- Memória baseada em expressões regulares (frases fora dos padrões não são guardadas).
- Memória de IA limitada pela janela: com 256 tokens, uma pergunta com RAG quase não deixa espaço para o histórico.
  Os checkpoints treinados antes da 1.4 nunca viram históricos: é preciso refazer o fine-tuning (célula 4).
- Busca sem stemming real (só prefixo de 5 letras) e sem embeddings.
- Não há testes automatizados do treino em Python nem script de avaliação (só os do app e do orquestrador do Colab).
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
- [ ] Cache de atenção (KV cache) no modelo e no `generate()`; manter a saída idêntica à versão sem cache.
- [x] Retomada completa: `pretrain_last.pt` com otimizador, scaler, step e geradores aleatórios; `--resume` continua de onde parou.
- [x] Acumulação de gradiente (`accum` no preset).
- [x] bf16 na A100 (`torch.cuda.is_bf16_supported()`) e TF32. Falta o `torch.compile` opcional.
- [x] Tokens pré-processados em disco (`uint16` com `np.memmap`, em `data/tokens/`).
- [ ] Backup automático do `finetuned.pt` com data e hora.
- [ ] Script de avaliação: perplexidade em um conjunto fixo e um banco de ~50 perguntas com respostas esperadas (identidade, fatos, resumo, leitura, conversa), para comparar versões.

### Fase 1 — Dados
- [~] Wikipédia inteira (~1,1 milhão de artigos; ~200–400 M tokens): o `prepare_data.py --wiki -1` já baixa tudo,
  continuando de onde parou (célula 2: `ARTIGOS = "todos"`, sem GPU). Falta medir o tempo e o tamanho reais.
- [ ] Wikisource em português (dumps) e os livros do Gutenberg (só ~650 em português existem lá).
- [ ] **GigaVerbo-v2** (`Polygl0t/gigaverbo-v2` no Hugging Face, ~318 bilhões de tokens em português, licença permissiva, com anotações de qualidade educacional e toxicidade): usar só um subconjunto filtrado (~2 bilhões de tokens), em streaming.
- [ ] Retreinar o tokenizer (~24 mil) com uma amostra equilibrada (português moderno majoritário).
- [ ] Remover duplicatas e textos curtos demais.

### Fase 2 — Pré-treino
- [ ] Preset `colab_100m` (e `colab_30m`), RoPE, contexto 2048. Já existe o `colab_50m` (posições aprendidas,
  contexto 512), que roda no app sem mudar o `Modelo.java`.
- [ ] Estimativa na A100: ~8,5 h para 2 bilhões de tokens com contexto 2048 (~45 a 125 unidades, pois o consumo da A100 varia de 5,4 a 15 unidades por hora conforme a fonte). Com 1024: ~7 h.
- [ ] Opcional: fase curta de extensão para 8k (~5% dos tokens, ~1 h), só como experimento. 16k/32k não compensam para este tamanho (custo de 4 a 7 vezes e o modelo não aproveita).

### Fase 3 — Fine-tuning
- [~] Exemplos com vários trechos de RAG por pergunta (até 3, conforme a janela) e conversas com várias mensagens
  (`conversas.jsonl` e `--history-share`, até 5 trocas). Falta aproveitar a janela de 2048 (mais trechos e trocas).
- [ ] Considerar o `Polygl0t/gigaverbo-v2-sft` como dados de instrução adicionais (conferir a licença antes).
- [ ] Manter os exemplos escritos em `tools/` e a identidade da Laika.

### Fase 4 — RAG
- [ ] Índice com a Wikipédia inteira + Wikisource + livros (~4–5 GB). **Não** indexar o GigaVerbo.
- [ ] Vários trechos por pergunta quando a janela permitir; manter o limite de confiança.
- [ ] Opcional: busca por embeddings como segunda etapa de ordenação.

### Fase 5 — Windows
- [ ] KV cache obrigatório; opcional salvar pesos em fp16 para o arquivo ficar menor.
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
