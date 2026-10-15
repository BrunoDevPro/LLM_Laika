# LLM Laika

Um pequeno modelo de linguagem (transformer estilo GPT) treinado do zero em PyTorch, em português.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BrunoDevPro/LLM_Laika/blob/main/colab.ipynb)

## Como rodar (Google Colab)

1. Clique no botão acima.
2. **Ambiente de execução → Alterar tipo de ambiente de execução → GPU (T4)**.
3. Execute as 3 células: (1) clona o repositório e baixa os livros, (2) pré-treina e faz o fine-tuning, (3) conversa.

> O repositório precisa ser **público** para o Colab conseguir clonar sem token.

## Estrutura

| Arquivo | Para quê |
|---|---|
| `prepare_data.py` | Baixa livros em português (domínio público) do Project Gutenberg para `data/books/` |
| `train.py` | Pré-treino com validação, early stopping e salvamento do melhor checkpoint |
| `finetune.py` | Fine-tuning pergunta→resposta (loss só na resposta); não sobrescreve o pré-treino |
| `chat.py` | Conversa; `--base` completa texto com o modelo só pré-treinado |
| `model.py` / `config.py` | Arquitetura e presets (`tiny` para CPU, `colab` para GPU) |
| `data/qa/pergeresp.txt` | Perguntas e respostas do fine-tuning |

Também funciona localmente: `pip install torch tokenizers`, coloque `.txt` em `data/books/` e rode
`python train.py --preset tiny`, `python finetune.py`, `python chat.py`.

## O que esperar

- O **pré-treino** ensina português. Acompanhe o `val loss`: acima de ~4.5 o modelo ainda não aprendeu
  gramática; abaixo de ~3.5 as frases começam a fazer sentido. Teste com `python chat.py --base`.
- O **fine-tuning** ensina o *formato* (pergunta → resposta curta → fim). Conhecimento vem do pré-treino
  e do próprio `pergeresp.txt`; um modelo desse tamanho não "sabe" o que não está nos dados.
- Mais livros ajudam mais do que mais épocas: o `train.py` mostra os *tokens por parâmetro*
  (ideal ≈ 20). Se o `val loss` parar de cair, mais passos só pioram (overfitting).

## Melhorando o fine-tuning

- Prefira **muitas perguntas variadas e curtas** a poucas perguntas repetidas com paráfrases.
- Escreva respostas sobre assuntos que **aparecem nos livros** ou no próprio arquivo.
- Cada exemplo tem que caber no `block_size` (128 no `tiny`, 256 no `colab`); o `finetune.py` avisa se
  descartar exemplos.
- Formato: `<|user|> pergunta` + quebra de linha + `<|assistant|> resposta <|end|>`, exemplos separados por
  linha em branco. Pode criar quantos `.txt` quiser em `data/qa/`.
