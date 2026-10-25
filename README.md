# LLM Laika

Um pequeno modelo de linguagem (transformer estilo GPT) treinado do zero em PyTorch, em português,
com busca nos textos (RAG) e memória do usuário.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BrunoDevPro/LLM_Laika/blob/main/colab.ipynb)

## No celular (Android)

A pasta `android/` tem um app que roda a Laika no celular, sem internet (RAG e memória incluídos).
Pela tela **Treinar** do app dá para ligar as células do treino no Colab sem deixar o Colab aberto
(GitHub Actions + [Colab CLI](https://github.com/googlecolab/google-colab-cli)) e baixar o modelo novo.
Veja `android/LEIA-ME.md` para instalar o APK, configurar a tela Treinar e gerar o APK de novo.

## Como rodar (Google Colab)

1. Clique no botão acima.
2. **Ambiente de execução → Alterar tipo de ambiente de execução → GPU (T4)**.
3. Rode as células conforme o que você quer fazer:

| Quero... | Células |
|---|---|
| Fazer tudo do zero | 1, 2, 3, 4, 5 |
| **Só refazer o fine-tuning** (usando o pré-treino que já está no Drive) | 1, 4, 5 |
| Atualizar livros/artigos e o índice de busca | 1, 2 |
| Só conversar | 1, 5 |
| Levar o modelo para o celular | 1, 6 |
| Medir o modelo e comparar com o anterior (`avaliar.py`) | 1, 7 |
| Modelo maior (~50M; precisa de mais dados) | 1; 2 com `ARTIGOS = "1 milhão"`; 3 com `PRESET = "colab_50m"` e `MODO = "do_zero"`; 4 |
| **Modelo de 100M** (contexto 2048, A100) | 1; 2 com `ARTIGOS = "todos"`, `CAROLINA`, `GIGAVERBO = 1,5 bilhão` e `SFT = 300 mil`; 3 com `PRESET = "colab_100m"`; 4; 6; 7. Ver **`TREINO_100M.md`** |
| Ligar as células pelo app, sem deixar o Colab aberto | 0 (uma vez só) |

As células são: (0) ligar o app ao Colab, (1) preparar, (2) dados, (3) pré-treino, (4) fine-tuning,
(5) conversa, (6) exportar para o celular (`laika_pacote.zip`) e (7) avaliar.

> O repositório precisa ser **público** para o Colab conseguir clonar sem token.

**Salvamento:** tudo fica em `Meu Drive/LLM_Laika/` (livros, artigos, índice do RAG, tokenizer,
checkpoints e memória). Se a sessão cair, rode a célula 1 e continue de onde parou. A célula 3 tem
`MODO = "pular"` (usa o pré-treino do Drive), `"continuar"` (retoma um pré-treino interrompido do ponto em que
parou, ou continua o terminado com os dados atuais) ou `"do_zero"`. A célula 2 baixa de 10 mil a todos os
~1,1 milhão de artigos da Wikipédia e, se cair, continua de onde parou.

## Estrutura

| Arquivo | Para quê |
|---|---|
| `prepare_data.py` | Baixa 500 livros do Project Gutenberg (`data/books/`) e artigos da Wikipédia em português (`--wiki 100000`, `1000000` ou `-1` para todos; continua de onde parou) em `data/wiki/`, com perguntas "O que é X?" em `data/qa_auto/`. Para os modelos grandes: Corpus Carolina (`--carolina`, em `data/carolina/`) e GigaVerbo-v2 (`--gigaverbo 1.5e9` tokens, em `data/gigaverbo/`), só para o pré-treino; e conversas do GigaVerbo-v2-SFT para o fine-tuning (`--sft 300000`, em `data/sft/`) |
| `rag.py` | Índice de busca (SQLite FTS5) nos artigos, livros e textos modernos: `python rag.py build` |
| `memory.py` | Memória do usuário (nome, cidade, gostos, "lembre que...") em `checkpoints/memoria.json` |
| `train.py` | Pré-treino com validação, early stopping, tokens em disco (`data/tokens/`, com cópia opcional no Drive: `--tokens-backup`), tokenizer treinado numa amostra (`--tokenizer-mb`), acumulação de gradiente (`--accum`), bf16, `--compile` e retomada (`--resume`) |
| `finetune.py` | Fine-tuning pergunta→resposta (loss só na resposta); não sobrescreve o pré-treino. Também é **fonte de conhecimento**: os artigos mais importantes da Wikipédia viram perguntas sem contexto, cada fato de 4 jeitos (`--conhecimento`) |
| `avaliar.py` | Avaliação fixa: perplexidade, 108 perguntas por categoria e a busca do RAG (`data/avaliacao/`); `--comparar backup` compara com o fine-tuning anterior |
| `chat.py` | Conversa com RAG, memória e cache de atenção; `--base` completa texto com o modelo só pré-treinado |
| `model.py` / `config.py` | Arquitetura (posições aprendidas ou RoPE) e presets (`tiny` e `tiny_rope` para CPU; `colab` ~7M, `colab_big` ~14M, `colab_50m` ~52M e `colab_100m` ~104M com contexto 2048 para GPU) |
| `TREINO_100M.md` | Todas as configurações do treino de 100M: dados, células, tempo, unidades e ordem |
| `windows/` | Scripts do pacote para rodar no Windows (CPU): `instalar.bat`, `conversar.bat`, `rodar.py`... |
| `CLAUDE.md` | Guia do projeto para o Claude Code: arquitetura, decisões, limitações e plano futuro |
| `SUGESTOES.md` | Ideias para melhorar a LLM além do plano do `CLAUDE.md` |
| `colab/laika_colab.py` | Roda células do `colab.ipynb` pelo Colab CLI (usado pelo workflow `.github/workflows/colab.yml`, que o app dispara) |
| `data/modern/` | 130 textos em português moderno escritos para o projeto: 20 maiores e 110 simples (`simples_*.txt`); entram 3x no pré-treino |
| `data/qa/pergeresp.txt` | ~14 mil perguntas e respostas: ~3000 genéricas ("Faça um texto sobre X", "E X?", por quê, como, diferenças, conversa, poemas...), 627 com respostas longas (2 parágrafos, passo a passo, histórias, contas explicadas), 438 de "por quê", 975 de sim ou não e 5313 de pessoas ("Quem foi X?", "O que X fez?"), datas por extenso, séculos em algarismos romanos, conceitos (pedra, rocha, água...) e o gatilho de resposta longa (gerado por `tools/gerar_pergeresp.py`) |
| `data/qa/leitura.txt` | ~510 perguntas de interpretação com "Contexto:", o mesmo formato do RAG |
| `data/qa/identidade.txt` | ~110 perguntas sobre quem é a Laika e a origem do nome (peso extra no fine-tuning) |

Também funciona localmente: `pip install torch tokenizers`, coloque `.txt` em `data/books/` e rode
`python train.py --preset tiny`, `python rag.py build`, `python finetune.py`, `python chat.py`.

## RAG: busca nos livros e artigos

Um modelo de ~7M de parâmetros não consegue guardar o que leu em 100 mil artigos. Com o RAG, antes de
responder, o chat procura os trechos mais parecidos com a pergunta e os coloca no prompt:

```
<|user|> Contexto: Um vulcão é uma estrutura geológica criada quando o magma...
Pergunta: O que é um vulcão? <|assistant|>
```

- O RAG só entra em perguntas que pedem informação. Conversa, perguntas sobre a Laika ou sobre você,
  contas e pedidos como "Corrija...", "Resuma..." vão sem contexto.
- Com janela de 256 tokens entra 1 trecho; com 512 (preset `colab_50m`), até 2; com 1024, até 4; com 2048
  (preset `colab_100m`), até 6.
  Os trechos extras são do mesmo artigo, os que têm mais palavras da pergunta.
- Se a pergunta inteira não acha nada com confiança, a busca tenta só o **nome próprio** dela
  ("O que Santos Dumont inventou?" → "Santos Dumont"; "Pesquise sobre a cadela Laika" → "Laika").
- "Laika" sozinha é a IA (sem busca); com cadela, Sputnik, espaço, soviética..., é a cadela e a busca vale.
- O fine-tuning ensina o modelo a usar esse formato: `leitura.txt`, ~70% das perguntas que pedem
  informação, treinadas com os trechos achados pela busca (`--rag-share`), e ~20 mil perguntas tiradas
  dos próprios artigos da Wikipédia ("Onde X nasceu?", "Quando X foi fundada?", "O que X inventou?",
  "Quantos habitantes tem X?"), com o trecho como Contexto (`--wiki-leitura`). Em 10% delas o trecho é
  de outro artigo e a resposta é "não sei", para o modelo não inventar a partir de um contexto errado.
- Quando o RAG é usado, a resposta termina com `*Nome do artigo`, por exemplo: `Um vulcão é ... *Vulcão`.
  `/fontes` liga ou desliga esse asterisco e `/rag` liga ou desliga a busca.
- Testar a busca sem o modelo: `python rag.py search "Quem foi Santos Dumont?"`.

## Memória

A Laika guarda o que você conta: "meu nome é Ana", "eu moro em Recife", "eu gosto de futebol",
"minha cor favorita é azul", "lembre que amanhã tenho prova". Depois responde "qual é o meu nome?",
"o que você lembra de mim?" e usa as anotações como contexto. "Esqueça tudo" apaga a memória.

Essa memória fica **fora do modelo**, num arquivo no Drive, e vale entre conversas.

**Resposta longa:** termine a pergunta com "Explique melhor." ou "Resposta longa." (ou ligue a opção
**Respostas longas** no app, ou `/longa` no `chat.py`) para uma resposta mais longa e detalhada. Depois de
cada mensagem, o app e o `chat.py` mostram quantos tokens ela teve e o total com o prompt.

**Memória de IA (histórico da conversa):** as últimas trocas da conversa (até 5) entram no prompt antes
da pergunta, quantas couberem na janela depois do contexto do RAG e do espaço da resposta:

```
<|user|> Qual é a capital da França? <|assistant|> A capital da França é Paris. <|end|> <|user|> E da Itália? <|assistant|>
```

Assim a Laika entende "E da Itália?", "Por quê?" ou "Resuma o que você disse". O fine-tuning treina
isso com `data/qa/conversas.jsonl` (~1.000 conversas escritas pelo gerador) e com ~30% dos exemplos
ganhando de 1 a 4 trocas anteriores (`--history-share`). No `chat.py`, `/limpar` esquece o histórico e
`--no-history` desliga. Com a janela de 256 tokens cabem poucas trocas; com 512, umas 5.

O histórico só entra quando a mensagem depende da conversa (`data_utils.follows_up`): começa com "E",
"Mas" ou "Então", tem palavras como "isso", "ele", "ela", "o mesmo", "continue", ou é bem curta e sem assunto
próprio ("Por quê?", "Como assim?", "Explique melhor."). Numa pergunta que se basta, como "O que é um
vulcão?", o histórico fica de fora: com ele, o modelo pequeno às vezes repetia a resposta anterior.

## O que esperar

- O **pré-treino** ensina português. Acompanhe o `val loss`: acima de ~4.5 o modelo ainda não aprendeu
  gramática; abaixo de ~3.5 as frases começam a fazer sentido. Teste com `python chat.py --base`.
- O **fine-tuning** ensina o *formato* (pergunta → resposta curta → fim) e a usar o contexto do RAG.
  A **taxa de aprendizado** (o tamanho do passo de cada ajuste dos pesos) é escolhida sozinha: 5e-5 até
  20M de parâmetros e 1e-4 nos modelos maiores (`--lr` troca).
- **Tamanho das respostas:** com `--max-new-tokens` (ou a barrinha do app) acima de 60, o `<|end|>` é
  penalizado no começo da resposta, então a Laika tende a escrever mais (até 120 tokens no app).
- Mais livros ajudam mais do que mais épocas: o `train.py` mostra os *tokens por parâmetro* (ideal ≈ 20).

## Como o fine-tuning evita "decorar" o pergeresp

Em 2 épocas (`--epochs`), cada lote mistura três coisas:
1. Exemplos escritos à mão do `data/qa/` (pelo menos ~25% dos exemplos de chat, `--qa-share`, cada um no
   máximo 2 vezes por época, `--max-qa-repeat`; com os ~7.600 atuais, cada um entra uma vez por época, ~37%);
   o `identidade.txt` tem peso extra (`--identity-boost`).
2. Milhares de exemplos gerados automaticamente (`--synthetic`, 10 mil): "Continue o texto: …", "Escreva uma frase
   com a palavra X", "Complete a frase: …", "Resuma o texto: …" (trechos dos livros do Gutenberg, com um
   resumo extrativo: a frase que melhor representa o trecho) e até 3000 "O que é X?" da Wikipédia.
3. Trechos de texto puros (`--replay`), para o modelo não esquecer o português.

A cada época o script mostra respostas para 8 perguntas de teste. Se ele voltar a responder tudo com o
pergeresp: `python finetune.py --synthetic 20000 --lr 3e-5` (mais exemplos dos livros e um passo menor). Não precisa
refazer o pré-treino.

## Adicionando perguntas

- Formato: `<|user|> pergunta` + quebra de linha + `<|assistant|> resposta <|end|>`, exemplos separados por
  linha em branco; linhas com `#` são comentários. A resposta pode ter quebras de linha (poemas). Pode criar quantos `.txt` quiser em `data/qa/`.
- `pergeresp.txt`, `leitura.txt` e `identidade.txt` são gerados por `python tools/gerar_pergeresp.py` (que os
  sobrescreve). As tabelas ficam em `tools/dados_extra*.py`, `tools/leitura.py`, `tools/textos_simples*.py` e
  `tools/genericas_*.py` (temas com resposta curta e parágrafo, perguntas genéricas, conversa e escrita).
  Para os seus próprios exemplos, use outro arquivo, por exemplo `data/qa/meus_exemplos.txt`.
- Cada exemplo tem que caber no `block_size` (256 no `colab`); o `finetune.py` avisa se descartar exemplos.
