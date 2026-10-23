# LLM Laika

Um pequeno modelo de linguagem (transformer estilo GPT) treinado do zero em PyTorch, em português,
com busca nos textos (RAG) e memória do usuário.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BrunoDevPro/LLM_Laika/blob/main/colab.ipynb)

## No celular (Android)

A pasta `android/` tem um app que roda a Laika no celular, sem internet (RAG e memória incluídos).
Pela tela **Colab** do app dá para ligar as células do treino no Colab sem deixar o Colab aberto
(GitHub Actions + [Colab CLI](https://github.com/googlecolab/google-colab-cli)) e baixar o modelo novo.
Veja `android/LEIA-ME.md` para instalar o APK, configurar a tela Colab e gerar o APK de novo.

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
| Modelo maior (~50M; precisa de mais dados) | 1; 2 com `ARTIGOS = "1 milhão"`; 3 com `PRESET = "colab_50m"` e `MODO = "do_zero"`; 4 |
| Ligar as células pelo app, sem deixar o Colab aberto | 0 (uma vez só) |

As células são: (0) ligar o app ao Colab, (1) preparar, (2) dados, (3) pré-treino, (4) fine-tuning,
(5) conversa e (6) exportar para o celular (`laika_pacote.zip`).

> O repositório precisa ser **público** para o Colab conseguir clonar sem token.

**Salvamento:** tudo fica em `Meu Drive/LLM_Laika/` (livros, artigos, índice do RAG, tokenizer,
checkpoints e memória). Se a sessão cair, rode a célula 1 e continue de onde parou. A célula 3 tem
`MODO = "pular"` (usa o pré-treino do Drive), `"continuar"` (retoma um pré-treino interrompido do ponto em que
parou, ou continua o terminado com os dados atuais) ou `"do_zero"`. A célula 2 baixa de 10 mil a todos os
~1,1 milhão de artigos da Wikipédia e, se cair, continua de onde parou.

## Estrutura

| Arquivo | Para quê |
|---|---|
| `prepare_data.py` | Baixa 500 livros do Project Gutenberg (`data/books/`) e artigos da Wikipédia em português (`--wiki 100000`, `1000000` ou `-1` para todos; continua de onde parou) em `data/wiki/`, com perguntas "O que é X?" em `data/qa_auto/` |
| `rag.py` | Índice de busca (SQLite FTS5) nos artigos, livros e textos modernos: `python rag.py build` |
| `memory.py` | Memória do usuário (nome, cidade, gostos, "lembre que...") em `checkpoints/memoria.json` |
| `train.py` | Pré-treino com validação, early stopping, tokens em disco (`data/tokens/`), acumulação de gradiente, bf16 e retomada (`--resume`) |
| `finetune.py` | Fine-tuning pergunta→resposta (loss só na resposta); não sobrescreve o pré-treino |
| `chat.py` | Conversa com RAG e memória; `--base` completa texto com o modelo só pré-treinado |
| `model.py` / `config.py` | Arquitetura e presets (`tiny` para CPU; `colab` ~7M, `colab_big` ~14M e `colab_50m` ~52M para GPU) |
| `windows/` | Scripts do pacote para rodar no Windows (CPU): `instalar.bat`, `conversar.bat`, `rodar.py`... |
| `CLAUDE.md` | Guia do projeto para o Claude Code: arquitetura, decisões, limitações e plano futuro |
| `SUGESTOES.md` | Ideias para melhorar a LLM além do plano do `CLAUDE.md` |
| `colab/laika_colab.py` | Roda células do `colab.ipynb` pelo Colab CLI (usado pelo workflow `.github/workflows/colab.yml`, que o app dispara) |
| `data/modern/` | 130 textos em português moderno escritos para o projeto: 20 maiores e 110 simples (`simples_*.txt`); entram 3x no pré-treino |
| `data/qa/pergeresp.txt` | ~7000 perguntas e respostas, ~3000 delas genéricas ("Faça um texto sobre X", "E X?", por quê, como, diferenças, conversa, poemas...) (gerado por `tools/gerar_pergeresp.py`) |
| `data/qa/leitura.txt` | ~510 perguntas de interpretação com "Contexto:", o mesmo formato do RAG |
| `data/qa/identidade.txt` | ~110 perguntas sobre quem é a Laika e a origem do nome (peso extra no fine-tuning) |

Também funciona localmente: `pip install torch tokenizers`, coloque `.txt` em `data/books/` e rode
`python train.py --preset tiny`, `python rag.py build`, `python finetune.py`, `python chat.py`.

## RAG: busca nos livros e artigos

Um modelo de ~7M de parâmetros não consegue guardar o que leu em 100 mil artigos. Com o RAG, antes de
responder, o chat procura o trecho mais parecido com a pergunta e o coloca no prompt:

```
<|user|> Contexto: Um vulcão é uma estrutura geológica criada quando o magma...
Pergunta: O que é um vulcão? <|assistant|>
```

- O RAG só entra em perguntas que pedem informação. Conversa, perguntas sobre a Laika ou sobre você,
  contas e pedidos como "Corrija...", "Resuma..." vão sem contexto.
- O fine-tuning ensina o modelo a usar esse formato: `leitura.txt` mais ~50% das perguntas que pedem
  informação, treinadas com o trecho achado pela busca (`--rag-share`).
- Quando o RAG é usado, a resposta termina com `*Nome do artigo`, por exemplo: `Um vulcão é ... *Vulcão`.
  `/fontes` liga ou desliga esse asterisco e `/rag` liga ou desliga a busca.
- Testar a busca sem o modelo: `python rag.py search "Quem foi Santos Dumont?"`.

## Memória

A Laika guarda o que você conta: "meu nome é Ana", "eu moro em Recife", "eu gosto de futebol",
"minha cor favorita é azul", "lembre que amanhã tenho prova". Depois responde "qual é o meu nome?",
"o que você lembra de mim?" e usa as anotações como contexto. "Esqueça tudo" apaga a memória.

A memória fica **fora do modelo**, num arquivo no Drive, e não entra nas perguntas normais. A janela do
modelo tem só 256 tokens e ele foi treinado com uma pergunta por vez, então colocar o histórico da conversa
no prompt atrapalharia as respostas.

## O que esperar

- O **pré-treino** ensina português. Acompanhe o `val loss`: acima de ~4.5 o modelo ainda não aprendeu
  gramática; abaixo de ~3.5 as frases começam a fazer sentido. Teste com `python chat.py --base`.
- O **fine-tuning** ensina o *formato* (pergunta → resposta curta → fim) e a usar o contexto do RAG.
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
pergeresp: `python finetune.py --synthetic 20000 --lr 3e-5` (mais exemplos dos livros na mistura). Não precisa
refazer o pré-treino.

## Adicionando perguntas

- Formato: `<|user|> pergunta` + quebra de linha + `<|assistant|> resposta <|end|>`, exemplos separados por
  linha em branco; linhas com `#` são comentários. A resposta pode ter quebras de linha (poemas). Pode criar quantos `.txt` quiser em `data/qa/`.
- `pergeresp.txt`, `leitura.txt` e `identidade.txt` são gerados por `python tools/gerar_pergeresp.py` (que os
  sobrescreve). As tabelas ficam em `tools/dados_extra*.py`, `tools/leitura.py`, `tools/textos_simples*.py` e
  `tools/genericas_*.py` (temas com resposta curta e parágrafo, perguntas genéricas, conversa e escrita).
  Para os seus próprios exemplos, use outro arquivo, por exemplo `data/qa/meus_exemplos.txt`.
- Cada exemplo tem que caber no `block_size` (256 no `colab`); o `finetune.py` avisa se descartar exemplos.
