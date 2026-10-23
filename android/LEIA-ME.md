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
2. Na Laika: menu **⋮ → Importar índice completo** → escolha o arquivo.
3. O app copia o índice para a pasta dele (precisa de ~1,3 GB livres durante a cópia). Depois,
   pode apagar o arquivo baixado.

## O que tem no app

- Conversa em bolhas, com a resposta aparecendo palavra por palavra e um botão para parar.
- RAG igual ao `chat.py`: mesmas regras (`wants_rag`, limite de confiança) e a fonte no fim (`*Título`).
- Memória igual ao `memory.py` ("meu nome é…", "lembre que…", "o que você lembra de mim?"),
  salva no celular no mesmo formato do `memoria.json`.
- Menu: fontes, RAG, memória, **modo completar texto** (o `--base`, com o `pretrain_best.pt`),
  criatividade (temperatura), importar/remover o índice, limpar a conversa.
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

**Por que não usa a GPU:** o modelo tem ~7 milhões de parâmetros. Para um modelo desse tamanho,
mandar o trabalho para a GPU do celular custa mais (cópia de dados e disparo de cada operação) do que
a própria conta; no processador, com o cache de atenção, cada token sai em poucos milissegundos.
A GPU passa a valer a pena com o modelo de ~100M parâmetros do plano (Fase 5).

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

# 2) Opcional: confere o Java contra o Python
python android/core/referencias.py --checkpoints checkpoints
cd android && ./gradlew :core:test

# 3) Monta o APK
./gradlew :app:assembleRelease
#    -> android/app/build/outputs/apk/release/app-release.apk
```

Os arquivos gerados no passo 1 (`app/src/main/assets/`) não vão para o Git, como os checkpoints.
O APK é assinado com a chave de depuração da máquina que o montou: para atualizar o app por cima,
monte sempre na mesma máquina (ou desinstale antes; a memória e o índice importado se perdem).
