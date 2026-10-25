# Laika no Android

App de conversa com a Laika rodando **inteira no celular**, sem internet: o mesmo modelo do
`finetuned.pt`, o tokenizer, a busca nos textos (RAG) com citação `*Título` e a memória do usuário.
Pela tela **Treinar**, o app também liga as células do treino no Google Colab, sem você deixar o Colab
aberto, e traz o modelo novo de volta para o celular.

## Instalar

1. Copie o `Laika.apk` para o celular e abra o arquivo.
2. O Android vai pedir para permitir "instalar apps desta fonte" (o app não vem da Play Store). Permita.
3. Abra a Laika. Ela carrega em poucos segundos e já responde.

Requer Android 8.0 ou mais novo. O APK tem ~36 MB. A conversa não usa a internet; só a tela Treinar usa.

## O índice completo do RAG (opcional, recomendado)

O app já vem com um índice pequeno (textos de `data/modern` e um livro). Para a Laika buscar na
Wikipédia e nos 495 livros, importe o `laika_rag.db` (~640 MB):

1. No celular, abra o Google Drive e baixe `Meu Drive/LLM_Laika/rag/laika_rag.db`.
2. Na Laika: botão de versões (no topo) → **Escolher arquivos** → escolha o arquivo.
3. O app copia o índice para a pasta dele (precisa de ~1,3 GB livres durante a cópia) e guarda a
   versão anterior como backup. Depois, pode apagar o arquivo baixado.

## Atualizar depois de um treino no Colab

**Pela tela Treinar (mais fácil):** depois que a célula 6 rodar pelo app, o modelo aparece em
**Modelos prontos**: toque em **Baixar e usar**.

**Pelo Google Drive:** no Colab, rode a célula *6) EXPORTAR PARA O CELULAR*; ela grava
`Meu Drive/LLM_Laika/laika_pacote.zip`. No celular, baixe o arquivo pelo app do Drive e, na Laika:
botão de versões (no topo) → **Escolher arquivos** → o zip.

O zip pode ter o modelo (`finetuned.pt`, `pretrain_best.pt`, `tokenizer.json`), o índice
(`laika_rag.db`, se marcar `INDICE`) e/ou os livros e artigos (se marcar `TEXTOS`: o celular monta o
índice do RAG com eles, junto com os textos próprios que já vêm no app). Também dá para escolher os
arquivos soltos de `Meu Drive/LLM_Laika/checkpoints` de uma vez. O app converte os `.pt` sozinho,
confere se combinam e guarda a versão anterior como backup. Importações longas continuam com a tela
apagada (fica uma notificação com o progresso e o botão Cancelar).

## Versões e backups

Cada versão guarda tudo: modelos, tokenizer, índice do RAG, memória e conversa. O botão do topo (o nome
da versão) abre um painel com todos os modelos do celular: um toque troca de modelo. Em **Versões e
backups**: fazer backup (com nome editável), usar um backup, renomear, exportar como `.zip` (para guardar no
Drive) e importar de volta. Os backups compartilham os arquivos iguais, então guardar várias versões
não repete os 640 MB do índice.

## Colab pelo app (treinar na nuvem)

Menu ⋮ → **Treinar**. O app pede ao GitHub Actions do repositório para ligar uma
máquina do Colab (com o [Colab CLI](https://github.com/googlecolab/google-colab-cli)), rodar as células
escolhidas com os parâmetros da tela (os mesmos campos do `colab.ipynb`: `MODO`, `EPOCAS`...) e
desligar a máquina no fim. Tudo continua sendo salvo no seu Google Drive, como no navegador.

Uma vez só:

1. No GitHub, junte este branch ao `main` (o workflow `.github/workflows/colab.yml` precisa estar no
   branch principal).
2. Crie um token em <https://github.com/settings/personal-access-tokens/new> ("fine-grained"), só
   para o repositório LLM_Laika, com as permissões **Actions** (leitura e escrita), **Secrets**
   (leitura e escrita) e **Contents** (leitura).
3. No Colab (navegador), rode a célula **0** do `colab.ipynb`: ela faz o login do Google com as
   permissões do Colab CLI e guarda essa permissão no GitHub (segredo `COLAB_ADC`), usando o token.
4. No app, tela Treinar: cole o repositório e o token.

Depois: marque as células (a 1 sempre roda antes; há atalhos como "Só fine-tuning", "1 milhão de artigos"
e "Modelo de 50M"), escolha a GPU e toque em **Rodar no Colab**. A tela mostra cada célula (✓, ⏳, ✗)
e as últimas linhas da saída; dá para cancelar. Pode fechar o app: ele avisa por notificação quando o
Colab terminar e quando precisar de você. Na primeira vez, o Colab pode pedir **autorização para usar o
Google Drive**: toque em **Autorizar**, permita o acesso e depois em **Já autorizei**.

Cuidados: o repositório é público, então os registros do GitHub Actions e o zip do modelo (guardado
por 14 dias como artefato) também ficam visíveis para quem entrar no repositório. O app tira e-mails
e tokens do que publica. A máquina do Colab gasta unidades de computação enquanto está ligada (uma
execução para sozinha no fim ou em até 6 horas). A ponte pelo Colab CLI foi testada só com um Colab
de mentira (`colab/teste_laika_colab.py`); na primeira vez, acompanhe pela tela Treinar.

## O que tem no app

- Conversa em bolhas, com pontinhos enquanto a Laika pensa, a resposta aparecendo palavra por palavra e
  um botão para parar. Se você rolar para cima, a tela não puxa para baixo; o botão ↓ volta para o fim.
- O teclado só abre quando você toca no campo de mensagem.
- Toque ou segure uma mensagem: aparece uma barra flutuante com ícones, logo acima da bolha. Nas respostas:
  **Copiar**, **Trecho lido** (o contexto do RAG) e **Gerar outra**. Nas suas mensagens: **Copiar** e
  **Editar** (para enviar de novo).
- RAG igual ao `chat.py`: mesmas regras (`wants_rag`, limite de confiança, busca pelo nome próprio, até
  6 trechos conforme a janela) e a fonte no fim (`*Título`). Na 1.7, a busca foi corrigida: perguntas sobre
  a cadela Laika voltaram a usar o RAG, "Você sabe..." não conta mais como pergunta pessoal, o radical das
  palavras não junta mais "capital" com "capítulo" e os textos próprios precisam da nota mínima.
- Na 1.8, "Faça uma frase com o meu nome" põe o nome guardado no Contexto (e "o seu nome", o da Laika), e
  perguntas curtas como "Mas em que mês foi?" ou "Quem era o líder?" usam a conversa anterior, sem buscar no RAG.
- **Memória de IA:** as últimas 5 trocas da conversa entram no prompt (as que couberem na janela), então
  dá para perguntar "E da Itália?" depois de "Qual é a capital da França?". Só nas mensagens que dependem
  da conversa ("E...", "Por quê?", "isso", "ele"...): numa pergunta nova, o histórico fica de fora para o
  modelo não repetir a resposta anterior. Limpar a conversa zera.
- Memória do usuário igual ao `memory.py` ("meu nome é…", "lembre que…", "o que você lembra de mim?"),
  salva no celular no mesmo formato do `memoria.json`.
- Menu ⋮: **Opções** (um grupo que abre e fecha com as caixinhas: mostrar fontes, buscar nos textos,
  memória do usuário, memória de IA, **respostas longas** e **modo completar texto**, o `--base` com o
  `pretrain_best.pt`),
  barrinhas de **criatividade** (temperatura de 0,10 a 1,50, de 0,01 em 0,01) e de **tamanho das
  respostas** (16 a 120 tokens com os modelos de janela 256; 200 com 512; 400 com o de 100M, que tem 2048;
  quanto maior, mais a Laika tenta escrever), o que a Laika lembra de você, versões e backups, **Treinar** e
  limpar a conversa.
- **Modelo de 100M** (RoPE, contexto 2048): o app guarda as matrizes em float16 (~210 MB de memória) e o
  cache de atenção cresce conforme a conversa. Funciona, mas é bem mais lento que o de 7M. Na tela Treinar,
  os atalhos **Dados para 100M** e **Modelo de 100M** preparam as células (ver `TREINO_100M.md`).
- Cada resposta mostra o tempo, a velocidade (tokens por segundo), os tokens da resposta e o total com o
  prompt; cada pergunta mostra quantos tokens tem.
- **Respostas longas**: com a opção ligada, toda pergunta ganha " Resposta longa." no fim e o tamanho vai ao
  máximo. Sem a opção, escrever "Explique melhor." ou "Resposta longa." na pergunta faz o mesmo.
- Se a versão em uso não abrir, o app oferece voltar para o backup mais recente.
- Modelos grandes (como o de 50M, ~260 MB de memória): o app mantém um carregado por vez. Ao trocar entre
  conversar e completar texto, ele libera o outro; se faltar memória, avisa em vez de fechar.
- Os comandos do `chat.py` também funcionam: `/fontes`, `/rag`, `/memoria`.

## Como funciona

O PyTorch não roda no Android, então o transformer foi reescrito em Java (`core/`):

| Arquivo | Equivale a |
|---|---|
| `Modelo.java` | `model.py` (posições aprendidas ou RoPE), com **cache de atenção (KV cache)**, pesos em float16 nos modelos grandes e as contas divididas entre os núcleos |
| `Tokenizador.java` | o `tokenizer.json` (BPE byte-level da biblioteca tokenizers) |
| `Laika.java` | `build_prompt` e `generate` do `chat.py` (top-k, top-p, penalidade de repetição) |
| `IndiceRag.java` | `RagIndex` do `rag.py` (SQLite FTS5, mesma pontuação) |
| `Memoria.java` | `memory.py` |
| `Texto.java` | as funções de RAG do `data_utils.py` |

Os pesos vão no APK em float16 (13,7 MB por modelo); a conta é feita em float32.

**Conversa no processador:** para responder, um token por vez, o modelo de ~7 milhões de parâmetros é
mais rápido no processador (com o cache de atenção, poucos milissegundos por token). O treino fica no
Colab (tela Treinar).

### Conferido contra o Python

`core/referencias.py` gera as respostas do código original e `gradle :core:test` compara:
666 textos tokenizados iguais, logits com diferença máxima de ~1e-5 para o PyTorch,
geração gulosa idêntica (com cache e passando da janela de 256), busca do RAG (nome próprio e vários
trechos, quando usar o histórico; também com um índice de artigos reais, `LAIKA_RAG_DB=<índice>` com o mesmo
índice no `referencias.py --rag-db`), memória, prompt (com histórico, janelas de 256 e 512) e a penalidade do
fim iguais. O modelo com RoPE (`RopeTest`, um checkpoint `tiny_rope`) dá os mesmos logits do PyTorch
(diferença ~7e-6), também com os pesos em float16, e o `.bin` convertido no celular é igual ao do exportador.
Também: o índice montado no celular igual ao do `rag.py build`, o zip do Colab virando uma versão nova,
o leitor do `colab.ipynb` igual ao do `colab/laika_colab.py` e o cliente do GitHub contra um servidor falso.

## Gerar o APK de novo (depois de um novo treino)

Precisa de JDK 17+ e do Android SDK (ou do Android Studio).

```bash
# 1) Converte os checkpoints (finetuned.pt, pretrain_best.pt, tokenizer.json) para o app
python android/exportar_modelo.py --checkpoints checkpoints --livros data/books
#    (--livros entra no índice pequeno que vai dentro do APK; use uma pasta com poucos livros)

# 2) Opcional: confere o Java contra o Python
python android/core/referencias.py --checkpoints checkpoints
cd android && LAIKA_CHECKPOINTS=../checkpoints LAIKA_LIVROS=<pasta com um livro e titulos.tsv> ./gradlew :core:test

# 3) Monta o APK
./gradlew :app:assembleRelease
#    -> android/app/build/outputs/apk/release/app-release.apk
```

Os arquivos gerados no passo 1 (`app/src/main/assets/`) não vão para o Git, como os checkpoints.
O APK é assinado com a chave de depuração da máquina que o montou: para atualizar o app por cima,
monte sempre na mesma máquina (ou desinstale antes; a memória e o índice importado se perdem).
