# LLM Laika

Um pequeno modelo de linguagem (transformer estilo GPT) treinado do zero em PyTorch, em português.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BrunoDevPro/LLM_Laika/blob/main/colab.ipynb)

## Como rodar (Google Colab)

1. Clique no botão acima.
2. **Ambiente de execução → Alterar tipo de ambiente de execução → GPU (T4)**.
3. Execute as 3 células: (1) clona o repositório e baixa os dados, (2) pré-treina e faz o fine-tuning, (3) conversa.

> O repositório precisa ser **público** para o Colab conseguir clonar sem token.

**Salvamento:** o notebook liga o seu Google Drive (autorize na primeira célula) e guarda livros,
tokenizer e checkpoints em `Meu Drive/LLM_Laika/`. Se a sessão cair, rode as células de novo: ele
reaproveita os livros e o pré-treino que já estão lá. O `train.py` salva o melhor checkpoint a cada
avaliação, então mesmo uma queda no meio do treino não perde tudo (continue com `--resume`).

## Estrutura

| Arquivo | Para quê |
|---|---|
| `prepare_data.py` | Baixa 400 livros do Project Gutenberg (`data/books/`) e 30 mil artigos da Wikipédia em português (`data/wiki/`, com perguntas "O que é X?" em `data/qa_auto/`) |
| `train.py` | Pré-treino com validação, early stopping e salvamento do melhor checkpoint |
| `finetune.py` | Fine-tuning pergunta→resposta (loss só na resposta); não sobrescreve o pré-treino |
| `chat.py` | Conversa; `--base` completa texto com o modelo só pré-treinado |
| `model.py` / `config.py` | Arquitetura e presets (`tiny` para CPU, `colab` para GPU) |
| `data/modern/` | Textos curtos em português moderno, escritos para o projeto (entram 3x no pré-treino) |
| `data/qa/pergeresp.txt` | ~740 perguntas e respostas escritas à mão (gerado por `tools/gerar_pergeresp.py`) |
| `data/qa/identidade.txt` | Perguntas sobre quem é a Laika (peso extra no fine-tuning) |

Também funciona localmente: `pip install torch tokenizers`, coloque `.txt` em `data/books/` e rode
`python train.py --preset tiny`, `python finetune.py`, `python chat.py`.

## O que esperar

- O **pré-treino** ensina português. Acompanhe o `val loss`: acima de ~4.5 o modelo ainda não aprendeu
  gramática; abaixo de ~3.5 as frases começam a fazer sentido. Teste com `python chat.py --base`.
- O **fine-tuning** ensina o *formato* (pergunta → resposta curta → fim). Conhecimento vem do pré-treino
  e do próprio `pergeresp.txt`; um modelo desse tamanho não "sabe" o que não está nos dados.
- Mais livros ajudam mais do que mais épocas: o `train.py` mostra os *tokens por parâmetro*
  (ideal ≈ 20). Se o `val loss` parar de cair, mais passos só pioram (overfitting).

## Como o fine-tuning evita "decorar" o pergeresp

Cada lote mistura três coisas:
1. Exemplos escritos à mão do `data/qa/` (~25% dos exemplos de chat, `--qa-share`); o `identidade.txt`
   tem peso extra (`--identity-boost`).
2. Milhares de exemplos gerados automaticamente (`--synthetic`): "Continue o texto: …", "Escreva uma frase
   com a palavra X", "Complete a frase: …", "Resuma o texto: …" (trechos dos livros do Gutenberg, com um
   resumo extrativo: a frase que melhor representa o trecho) e até 3000 "O que é X?" da Wikipédia.
3. Trechos de texto puros (`--replay`), para o modelo não esquecer o português.

A cada época o script mostra respostas para 7 perguntas de teste, então dá para ver na hora se ele
voltou a responder tudo com o pergeresp. Se isso acontecer: `python finetune.py --qa-share 0.12 --lr 3e-5`.
Não precisa refazer o pré-treino para repetir o fine-tuning.

## Melhorando o fine-tuning

- Prefira **muitas perguntas variadas e curtas** a poucas perguntas repetidas com paráfrases.
- Escreva respostas sobre assuntos que **aparecem nos livros** ou no próprio arquivo.
- Cada exemplo tem que caber no `block_size` (128 no `tiny`, 256 no `colab`); o `finetune.py` avisa se
  descartar exemplos.
- Formato: `<|user|> pergunta` + quebra de linha + `<|assistant|> resposta <|end|>`, exemplos separados por
  linha em branco; linhas com `#` são comentários. Pode criar quantos `.txt` quiser em `data/qa/`.
- `pergeresp.txt` e `identidade.txt` são gerados por `python tools/gerar_pergeresp.py` (que os sobrescreve).
  Para os seus próprios exemplos, use outro arquivo, por exemplo `data/qa/meus_exemplos.txt`.
