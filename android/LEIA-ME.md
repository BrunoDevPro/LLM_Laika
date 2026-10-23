# Laika no Android

App de conversa com a Laika rodando **inteira no celular**, sem internet: o mesmo modelo do
`finetuned.pt`, o tokenizer, a busca nos textos (RAG) com citação `*Título` e a memória do usuário.

## Instalar

1. Copie o `Laika.apk` para o celular e abra o arquivo.
2. O Android vai pedir para permitir "instalar apps desta fonte" (o app não vem da Play Store). Permita.
3. Abra a Laika. Ela carrega em poucos segundos e já responde.

Requer Android 8.0 ou mais novo. O APK tem ~36 MB.

## O índice completo do RAG (opcional, recomendado)

O app já vem com um índice pequeno (textos de `data/modern` e um livro). Para a Laika buscar na
Wikipédia e nos 495 livros, importe o `laika_rag.db` (~640 MB):

1. No celular, abra o Google Drive e baixe `Meu Drive/LLM_Laika/rag/laika_rag.db`.
2. Na Laika: botão de versões (no topo) → **Escolher arquivos** → escolha o arquivo.
3. O app copia o índice para a pasta dele (precisa de ~1,3 GB livres durante a cópia) e guarda a
   versão anterior como backup. Depois, pode apagar o arquivo baixado.

## Atualizar depois de um treino no Colab

Não precisa de computador: no celular, baixe do Drive (`Meu Drive/LLM_Laika/checkpoints`) o
`finetuned.pt`, o `pretrain_best.pt` e o `tokenizer.json` (e, se quiser, `rag/laika_rag.db`).
No app: botão de versões (no topo) → **Escolher arquivos** → selecione todos de uma vez.
O app converte os `.pt` sozinho, confere se combinam e guarda a versão anterior como backup.

## Versões e backups

Cada versão guarda tudo: modelos, tokenizer, índice do RAG, memória e conversa. No botão do topo:
fazer backup (com nome editável), usar um backup, renomear, exportar como `.zip` (para guardar no
Drive) e importar de volta. Os backups compartilham os arquivos iguais, então guardar várias versões
não repete os 640 MB do índice.

## Treinar no celular

Menu ⋮ → **Treinar no celular**. As mesmas etapas do Colab, rodando na GPU do celular
(OpenGL ES 3.1, compute shaders) com a tela apagada (fica uma notificação com o progresso e o botão Parar):

1. **Dados**: no Colab, rode a célula *6) EXPORTAR DADOS PARA O CELULAR*; ela grava
   `Meu Drive/LLM_Laika/laika_dados.zip`. Baixe no celular e importe. (Os textos próprios e as
   perguntas escritas já vêm no app.)
2. **Índice do RAG**: o `rag.py build`.
3. **Pré-treino**: continuar do modelo em uso, do zero (treina um tokenizer novo) ou retomar um
   treino parado (o estado completo é salvo a cada validação e ao parar).
4. **Fine-tuning**: o `finetune.py` (exemplos escritos, sintéticos, Wikipédia, RAG, 8 respostas de teste por época).
5. **Usar o resultado**: vira uma versão nova (a anterior vai para os backups).

Tempo: o pré-treino completo do preset `colab` (10.000 passos, ~164 M tokens) são ~7,5 PFLOP; numa
GPU de celular isso leva muitas horas (o app mostra tokens/s e o tempo que falta). O fine-tuning leva
de minutos a uma hora. Deixe o celular carregando; ele esquenta.

Conferido no PC com o Mesa (a mesma GPU "de mentira" roda os mesmos shaders): perda, gradientes de
todos os parâmetros e o passo do AdamW iguais ao PyTorch; tokenizer treinado igual ao da biblioteca
tokenizers; índice igual ao do `rag.py`; pré-treino com parada e retomada e fine-tuning de ponta a ponta.

## O que tem no app

- Conversa em bolhas, com a resposta aparecendo palavra por palavra e um botão para parar.
- RAG igual ao `chat.py`: mesmas regras (`wants_rag`, limite de confiança) e a fonte no fim (`*Título`).
- Memória igual ao `memory.py` ("meu nome é…", "lembre que…", "o que você lembra de mim?"),
  salva no celular no mesmo formato do `memoria.json`.
- Menu: fontes, RAG, memória, **modo completar texto** (o `--base`, com o `pretrain_best.pt`),
  criatividade (temperatura), versões e backups, treinar no celular, limpar a conversa.
- Os comandos do `chat.py` também funcionam: `/fontes`, `/rag`, `/memoria`.

## Como funciona

O PyTorch não roda no Android, então o transformer foi reescrito em Java (`core/`):

| Arquivo | Equivale a |
|---|---|
| `Modelo.java` | `model.py`, com **cache de atenção (KV cache)** e as contas divididas entre os núcleos |
| `Tokenizador.java` | o `tokenizer.json` (BPE byte-level da biblioteca tokenizers) |
| `Laika.java` | `build_prompt` e `generate` do `chat.py` (top-k, top-p, penalidade de repetição) |
| `IndiceRag.java` | `RagIndex` do `rag.py` (SQLite FTS5, mesma pontuação) |
| `Memoria.java` | `memory.py` |
| `Texto.java` | as funções de RAG do `data_utils.py` |

Os pesos vão no APK em float16 (13,7 MB por modelo); a conta é feita em float32.

**Conversa no processador, treino na GPU:** para responder, um token por vez, o modelo de ~7 milhões
de parâmetros é mais rápido no processador (com o cache de atenção, poucos milissegundos por token).
Para treinar, as contas são em lotes grandes e a GPU vale a pena (`core/treino`).

### Conferido contra o Python

`core/referencias.py` gera as respostas do código original e `gradle :core:test` compara:
612 textos tokenizados iguais, logits com diferença máxima de ~1e-5 para o PyTorch,
geração gulosa idêntica (com cache e passando da janela de 256), busca do RAG, memória e prompt iguais.

## Gerar o APK de novo (depois de um novo treino)

Precisa de JDK 17+ e do Android SDK (ou do Android Studio).

```bash
# 1) Converte os checkpoints (finetuned.pt, pretrain_best.pt, tokenizer.json) para o app
python android/exportar_modelo.py --checkpoints checkpoints --livros data/books
#    (--livros entra no índice pequeno que vai dentro do APK; use uma pasta com poucos livros)

# 2) Opcional: confere o Java contra o Python (treino na GPU precisa do Mesa: apt install libegl-mesa0 libgles2)
python android/core/referencias.py --checkpoints checkpoints
python android/core/referencias_treino.py data/books/gutenberg_24455.txt
cd android && LAIKA_CHECKPOINTS=../checkpoints LAIKA_LIVROS=<pasta com um livro e titulos.tsv> ./gradlew :core:test

# 3) Monta o APK
./gradlew :app:assembleRelease
#    -> android/app/build/outputs/apk/release/app-release.apk
```

Os arquivos gerados no passo 1 (`app/src/main/assets/`) não vão para o Git, como os checkpoints.
O APK é assinado com a chave de depuração da máquina que o montou: para atualizar o app por cima,
monte sempre na mesma máquina (ou desinstale antes; a memória e o índice importado se perdem).
