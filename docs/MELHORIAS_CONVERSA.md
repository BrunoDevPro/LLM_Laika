# Como fazer a Laika conversar de verdade (e o plano para ≥ 200M)

Anotado em 16/11/2026, a pedido do usuário. **Nada disto está implementado ainda.** É o plano dos itens 1 a 4
(os que mais ajudam) para uma Laika de **200M de parâmetros ou mais** que mantenha conversas simples, com memória
que funciona e respostas coerentes, mesmo quando não são verdadeiras ("minha cor favorita é azul" só precisa ser
a mesma resposta da próxima vez e valer para o resto da conversa).

O que limita hoje não é o tamanho do modelo: é **como o fine-tuning ensina a conversar**. Um modelo maior ajuda
(vê histórico mais longo, imita melhor o estilo), mas aprende os vícios dos dados mais depressa. Por isso os dados e
a perda vêm antes.

| # | Mudança | Onde mexe | Custo | Como medir |
|---|---|---|---|---|
| 1 | Perda em **todas** as respostas da conversa | `finetune.py` (`encode_chat`) | só código, sem dados novos | `val conversa` nova |
| 2 | Histórico **sempre** no prompt (janela 2048) | `data_utils.py`, `chat.py`, `finetune.py`, `Texto.java`, `Laika.java` | só código + regenerar as referências do app | categorias novas no `avaliar.py` |
| 3 | 50–100 mil conversas de 4–12 trocas | geradores em `tools/` + conversas geradas por modelo aberto | algumas horas de GPU + filtros | `avaliar.py` + distinct-2 |
| 4 | Menos molde, mais variedade | mistura do `finetune.py` | só código e configuração | repetição entre respostas |

---

## 1. Perda em todas as respostas da conversa

**Como é hoje.** O `finetune.py` só treina a **última** resposta de cada exemplo (`encode_chat`: `answer_start` é
a posição depois do último `<|assistant|>`; o resto vira `-100`). Numa conversa de 4 trocas, as 3 primeiras respostas
entram só como prompt.

```
<|user|> Tenho um gato chamado Tom. <|assistant|> Que nome bonito! <|end|>      <- hoje: ignorada
<|user|> Qual o nome do meu gato? <|assistant|> O nome do seu gato é Tom. <|end|> <- hoje: a única treinada
```

**Por que atrapalha.**
- O modelo lê a conversa inteira de qualquer jeito, mas só aprende com 1 resposta de k. Desperdiça (k − 1)/k do sinal.
- As respostas do meio são justamente onde se aprende o tom de bate-papo: reagir ao que o usuário contou,
  acompanhar, não repetir. Hoje isso quase não é ensinado.
- É também o que ensina a **usar o histórico**: da 2ª resposta em diante, ela depende do que veio antes.

**O que mudar.**
- Rotular todos os trechos `<|assistant|> … <|end|>` (o `<|end|>` inclusive), não só o último.
- Atenção: o `add_history` do `finetune.py` insere trocas **emprestadas de outros exemplos** como histórico falso.
  Essas trocas devem continuar mascaradas (senão as respostas curtas do `pool` seriam treinadas centenas de vezes). Para isso,
  o `add_history` passa a devolver quantas trocas emprestou, e o `encode_chat` mascara só essas.
- Nas conversas reais (`conversas.jsonl` e as novas do item 3), todas as respostas são treinadas.
- Validação: manter `val escritos` como está (comparável com os modelos antigos) e acrescentar **`val conversa`**
  (todas as respostas de ~2 mil conversas separadas por **conversa**, nunca por troca, senão vaza).
- Normalizar a perda por token de resposta, como hoje. Limitar a 8 respostas treinadas por conversa, para as
  longas não dominarem.

**Ganho esperado.** Uma conversa de 6 trocas passa de 1 para 6 respostas treinadas com o mesmo custo de computação
(o prompt já era calculado). Não está medido; é a mudança mais barata do plano.

**Com 200M.** O mesmo. Um modelo maior aproveita mais o sinal extra, porque aprende estilo com poucos exemplos.

---

## 2. Histórico sempre no prompt, com a janela de 2048

**Como é hoje.** O histórico (até `MAX_HISTORY = 5` trocas) **só entra se a mensagem parecer seguimento**
(`follows_up` em Python e `Texto.segueConversa` em Java): começa com "e/mas/então/também", tem "isso/ele/ela/o mesmo",
é uma frase como "explique melhor", tem até 2 palavras, ou até 6 palavras só com palavras genéricas. Foi uma
decisão de 1.5 (lição 17): com o histórico em toda pergunta, o modelo de 7M repetia a resposta anterior.

**Por que atrapalha a memória.** A regra é uma lista de expressões regulares. Estas mensagens **dependem** da
conversa e **não** passam:

```
Meu cachorro se chama Rex.  ... (3 mensagens depois) ...  Qual o nome do meu cachorro?
Você lembra o que eu falei da viagem?
Pode me dar uma receita com aquilo que eu tenho em casa?
```

Sem o histórico no prompt, o modelo não tem como acertar, não importa o tamanho dele. A memória do usuário
(`memory.py`/`Memoria.java`, que guarda "meu nome é…", "moro em…", "lembre que…") cobre só os padrões que ela conhece.

**O que mudar.**
1. **Modo sempre**: com janela ≥ 1024 (100M, 200M), o histórico entra em **toda** pergunta, as trocas mais recentes
   que couberem (até ~8). Com janela 256 ou 512 (7M, 50M), continua o `follows_up`, porque lá a janela é pequena
   e a lição 17 vale. A opção "memória de IA" do app continua, e o modo vem do tamanho da janela.
2. **Orçamento da janela** de 2048: resposta (até 400), RAG (até ~900 tokens) e **pelo menos ~500 para o histórico**
   (sem RAG, que é o caso do bate-papo, o histórico pode usar ~1200). Hoje o histórico fica com o que sobra depois do RAG.
3. **O treino precisa ver o que o app vai mandar.** Hoje só ~30% dos exemplos ganham histórico, e quase todo sem relação
   (`--history-share`). No novo treino:
   - conversas reais do item 3: **sempre** com todas as trocas anteriores;
   - exemplos de uma troca só (escritos, SFT): **~40–50%** com 1–6 trocas **sem relação**, para ensinar a ignorar histórico irrelevante,
     que é a defesa contra a repetição da lição 17;
   - junto com o item 1 (as respostas do meio treinadas), o modelo vê muitos casos de "mesmo assunto" e "outro assunto".
4. **O RAG continua só na última pergunta** e o gatilho de resposta longa segue fora do histórico (formatos da seção 4 do CLAUDE.md).

**Paridade com o app.** O prompt tem de ser idêntico em `chat.py`/`data_utils.py`, no `finetune.py` e em
`Laika.montarPrompt`/`Texto.java`. Depois, regenerar as referências (`python android/core/referencias.py`) e rodar
`./gradlew :core:test`.

**Medir.** Categorias novas no `avaliar.py` (o campo `historico` já existe nas perguntas):
- *memória* (~30 perguntas): o histórico traz um fato, a pergunta depende dele (`esperado` = o fato);
- *distrator* (~20): o histórico não tem relação, e a resposta **não** pode repetir a anterior (`proibido` = palavras da resposta anterior);
- *volta ao assunto* (~10).

**Com 200M.** O 100M já tem janela 2048; o 200M também (RoPE). A janela de 2048 comporta de 10 a 20 trocas curtas.
O custo está no celular: prompt mais longo = mais tempo de leitura (ver a seção 5).

---

## 3. Conversas de verdade (o maior ganho)

**Como é hoje.**
- `data/qa/conversas.jsonl`: **2.299** conversas de 2–3 trocas, quase todas de molde: "Qual a capital de X?" → "E de Y?", "Do que
  estávamos falando?", "Pode repetir?".
- O GigaVerbo-v2-SFT (até 1 milhão de conversas baixadas) é de pedidos de uma troca só, com respostas longas.
- Praticamente não existe: contar algo e perguntar depois, mudar de assunto e voltar, corrigir o modelo, bate-papo
  do dia a dia, "não entendi", opinião coerente.

**O que criar.** Algo como **50–100 mil conversas de 4 a 12 trocas**, respostas curtas e simples (até ~40 palavras).
Proposta de composição (números a ajustar):

| Família | O que ensina | Conversas |
|---|---|---|
| Contar e perguntar depois | nome, pet, cidade, comida, hobby, idade, profissão; 1–3 mensagens de distração no meio | 12 mil |
| Mudar de assunto e voltar | "voltando ao que falávamos…", "e aquele outro assunto?" | 6 mil |
| **Ficha da Laika** | gostos e fatos **inventados mas fixos** (cor favorita, comida, idade, "onde você mora") repetidos com muitas paráfrases, e "por quê?" coerente com o que ela disse antes | 6 mil |
| Correções e mal-entendidos | "não entendi", "como assim?", "não, eu disse X", "pode repetir?" | 6 mil |
| Bate-papo do dia a dia | cansaço, dia ruim, planos, comida, tempo; respostas curtas e gentis | 8 mil |
| Pedidos encadeados | "explica", "mais simples", "dá um exemplo", "resume" | 6 mil |
| Perguntas factuais curtas com seguimento | as que já existem, com mais variedade | 4 mil |
| Limites e "não sei" | coerentes com o que ela pode e não pode fazer | 4 mil |

**A ficha da Laika** é o que garante a coerência que você pediu. Uma lista de ~50 fatos canônicos inventados
(cor, comida, bichos, medo, "o que faço quando estou sozinha"…) vai nos dados com muitas formas de perguntar. Sem uma ficha fixa, a Laika
responde cores diferentes em cada conversa. As respostas podem ser falsas, desde que sempre as mesmas.

**De onde vêm.**
- **(A) Geradores em `tools/`** (no estilo dos `tools/pessoas*.py`): famílias 1, 2, 4 e 7. Têm a vantagem de que o resultado
  se confere sozinho (o fato plantado precisa aparecer na resposta). O risco é virar molde, então cada geradora usa
  vários bancos de paráfrases e nomes, e a mistura do item 4 limita o peso delas.
- **(B) Um modelo aberto no Colab** (vLLM, ex.: Qwen3 em torno de 8B, licença Apache 2.0; conferir os termos de qualquer
  outro): dois papéis simulados, "usuário" com um objetivo escondido e "Laika" com a ficha e regras de estilo, 4–12 trocas.
  Para as famílias 3, 5 e 6, onde variedade importa. Uma estimativa grosseira: 60 mil conversas × ~350 tokens ≈ 20 milhões de tokens
  gerados, algumas horas de A100 (não medido).
- **(C) Filtrar o SFT** que já está no Drive: conversas com 2 ou mais trocas e respostas curtas. Falta medir quantas passam.

**Filtros obrigatórios** (iguais aos do `converter_sft`, mais alguns):
- português do Brasil, sem emoji, sem menção a outras IAs, nem "como modelo de linguagem…";
- resposta de até ~40 palavras; nenhuma troca com mais de 120 palavras;
- fato plantado presente nas respostas posteriores (verificação por texto);
- deduplicar por n-gramas (conversas quase iguais saem);
- identidade: nada de "sou humana" nem de outro nome.

**Tamanho do que entra no fine-tuning.** 60 mil conversas × ~250 tokens ≈ 15 milhões de tokens: pequeno perto do SFT, e é o que faz diferença.

**Com 200M.** Um modelo maior imita melhor o estilo das conversas geradas, mas também o decora mais depressa:
as 8 famílias precisam de bastante variedade, e o item 4 controla o peso delas.

---

## 4. Menos molde, mais naturalidade

**Como é hoje.** O fine-tuning mistura, por época: os **26.645 exemplos escritos** (`pergeresp`, identidade, leitura,
biografias; cada um aparece em toda época), o **conhecimento sem contexto** (`--conhecimento automático` = 20 mil artigos ×
vários fatos × 4 formas × 2 repetições, ou seja, centenas de milhares de perguntas "Quando X foi fundada?"), as 40 mil
perguntas de leitura da Wikipédia e o SFT (até 300 mil). Quase tudo é pergunta curta → resposta de enciclopédia
na mesma frase de molde ("A capital de X é Y.", "X nasceu em Y em Z.").

**Por que atrapalha a conversa.** O modelo aprende que **toda mensagem é uma pergunta factual** e responde nesse
molde, também a "tô cansado hoje". Com 200M isso piora, porque o modelo decora o molde mais depressa.

**O que mudar.**
1. **Reduzir o conhecimento.** `CONHECIMENTO` de "automático" (20 mil artigos) para **5 mil** (ou `nenhum` numa rodada
   focada em conversa). Como o objetivo é coerência e não verdade, o custo é aceitável.
2. **Limitar cada família de molde** a ~5% dos escritos (a contas explicadas, os sim/não, os "por quê", as pessoas/datas):
   agrupar por primeiras 3 palavras do molde e amostrar. Reduz também `--max-qa-repeat`.
3. **Mistura por percentual** em vez de "tudo, uma vez por época" (como já foi feito no `hp50g/treino.py`:
   `--mistura nome:fração`). Ponto de partida para um fine-tuning focado em conversa, por exemplos:

   | Fonte | Fração |
   |---|---|
   | Conversas do item 3 | 45% |
   | SFT (parte curta e simples; retrieval e resumo em pequena proporção) | 20% |
   | Escritos reduzidos e sem molde repetido (identidade ~2%) | 12% |
   | Leitura com Contexto (Wikipédia e retrieval) | 10% |
   | Conhecimento sem Contexto | 8% |
   | Sintéticos e replay de texto | 5% |

4. **Respostas curtas e simples** como estilo padrão. Respostas longas só com o gatilho "Resposta longa." (lição 21).
5. **Medir.** Em ~100 respostas a ~50 mensagens variadas (bate-papo, perguntas, pedidos), registrar:
   *distinct-2* (variedade de pares de palavras), % de respostas que começam com as mesmas 3 palavras, comprimento médio e a **taxa de cópia do treino**
   (parte das respostas com ≥ 80% dos n-gramas iguais a uma resposta do treino). O objetivo é ver essas medidas melhorarem a cada
   mudança da mistura.

**Com 200M.** O item 4 pesa mais com um modelo maior. Se o 200M parecer pior em variedade que o 100M, a causa é a mistura.

---

## 5. Com 200M ou mais: preset, custo e celular

**Proposta de preset `colab_200m`** (não criado ainda):

| Campo | Valor |
|---|---|
| dimensão / camadas / cabeças | 1024 / 14 / 16 (dimensão da cabeça: 64) |
| contexto, posições | 2048, RoPE |
| vocabulário | 24 mil (o mesmo tokenizador do 100M, assim os tokens calculados no Drive valem) |
| parâmetros | ~**200,7M** (176,2M nas camadas + 24,6M no embedding) |
| lote | 16 × 2048 × acumulação 16 = ~524 mil tokens por passo; ~7.600 passos para ~4 bilhões de tokens |
| taxa | 3e-4 a 4e-4 (o 100M usa 5e-4), aquecimento de 400 passos, cosseno |

**Custo do pré-treino.** A conta é 6·N·D: ~4,8·10¹⁸ FLOPs para 200M × 4 bilhões de tokens, **4× o do 100M** (1,2·10¹⁸ para
100M × 2 bilhões). Se o `docs/TREINO_100M.md` estiver certo (~8,5 h na A100 para o 100M, estimativa nunca medida),
são ~34 h de A100, ou **~190 a 510 unidades** (a A100 gasta de 5,4 a 15 por hora conforme a fonte). **É um mês inteiro do plano
de 200 unidades, ou mais.** Alternativas:
- começar com ~2 bilhões de tokens (10 tokens/parâmetro; fica subtreinado, mas funciona) e **estender depois** com o atalho "Estender", que já existe;
- usar a placa de vídeo própria que você pretende comprar para os 4 bilhões;
- na A100, ligar `--compile` (~20% mais rápido) e conferir os tokens/s na primeira execução, antes de decidir.

**Fine-tuning de 200M.** Cada época é maior que a do 100M, mas o fine-tuning com os itens 1–4 é pequeno perto do pré-treino
(dezenas de milhões de tokens de conversas + o resto da mistura).

**Celular.** 200M em int8 = ~200 MB de pesos (o de 100M tem ~105 MB). No PC, o 100M leva ~35 ms por token e o 200M deve levar **~70 ms**
(uma estimativa por proporção). O prompt longo do item 2 (histórico sempre) pesa: com 1500 tokens de prompt, ler o prompt vai de
alguns segundos a dezenas deles. Para isso existem o "Respostas rápidas" (2 trechos do RAG) e o modo "histórico curto" (as 4 últimas
trocas), que valem a pena ter de volta como opção no app.

---

## 6. Ordem de trabalho sugerida

1. **Itens 1 e 2** (só código): `finetune.py`, `data_utils.py`/`chat.py`, `Texto.java`/`Laika.java`, referências do app e as categorias novas do
   `avaliar.py`. Dá para testar em CPU com o preset `tiny`.
2. **Item 3, parte A** (geradores de `tools/`, ficha da Laika): começar por esta, que se confere sozinha.
3. **Item 4** (mistura por percentual e as medidas de variedade).
4. **Item 3, parte B** (conversas geradas por modelo aberto, com filtros).
5. Pré-treino de 200M (em paralelo, quando houver unidades) e depois o fine-tuning com tudo isto; comparar com o 100M em **Testar respostas**.

## 7. Outros itens citados na mesma conversa (sem detalhe aqui)

- Frase fixa de identidade no começo de toda conversa (~20 tokens).
- Mais pré-treino (extensão por mais tokens).
- Geração mais conservadora no chat: temperatura ~0,5–0,6 e penalidade de repetição só nos últimos ~64 tokens.
- RAG só quando a pergunta pede informação (bate-papo sem trecho da Wikipédia).
- Medir a coerência com perguntas de conversa de várias trocas no `avaliar.py` (parte do item 2 acima).
