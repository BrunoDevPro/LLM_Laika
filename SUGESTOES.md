# Sugestões para melhorar a Laika (além do plano do CLAUDE.md)

O plano da seção 9 do `CLAUDE.md` já cobre KV cache, retomada completa, acumulação de gradiente,
bf16, tokens em disco, avaliação, Wikipédia inteira, GigaVerbo-v2, tokenizer de 24 mil, RoPE,
contexto 2048, o modelo de ~100M e o RAG com vários trechos. As ideias abaixo **não estão lá**.
Estão em ordem de "quanto ajudam" ÷ "quanto custam", dentro de cada grupo. Nenhuma foi implementada.

Legenda de custo: 🟢 poucas horas · 🟡 um ou dois dias · 🔴 projeto maior.
Lembrete: tudo o que muda `model.py`, `train.py` ou o formato do prompt precisa ser repetido em
`android/core` (e conferido com `core/referencias.py` + `gradle :core:test`).

## 1. Arquitetura (entram junto com o preset de 100M e o RoPE)

1. 🟢 **RMSNorm + SwiGLU** no lugar de LayerNorm + GELU. É o padrão dos modelos atuais (Llama,
   Qwen, Tucano): mesma quantidade de contas, perda menor para o mesmo número de tokens. Com SwiGLU, a
   camada do meio fica com ~8/3 × dim (ex.: 2048 para dim 768) para manter o número de parâmetros.
2. 🟢 **Atenção com grupos de cabeças (GQA)**: 12 cabeças de pergunta e 4 de chave/valor. O KV cache
   fica 3× menor, o que importa muito no celular com contexto 2048 (100M, 2048 tokens: ~150 MB de
   cache em fp32 sem GQA, ~50 MB com GQA) e a geração fica mais rápida. A perda quase não muda.
3. 🟢 **QK-norm** (normalizar as perguntas e as chaves antes do produto) e **z-loss** pequeno na saída:
   deixam o treino em bf16 estável com taxa de aprendizado mais alta. Barato e evita "explosões".
4. 🟡 **Taxa de aprendizado WSD** (warmup → estável → decaimento curto no fim) em vez do cosseno.
   Combina com o jeito que o projeto treina (célula 3 com `MODO = "continuar"`): dá para continuar o
   pré-treino quando chegarem dados novos sem refazer o agendamento, e cada "decaimento" gera um
   checkpoint bom para o celular. Também permite comparar tamanhos de dados sem treinar de novo.
5. 🟡 **Achar hiperparâmetros no pequeno e levar para o grande (µP)**: com a parametrização µP, a taxa
   de aprendizado ótima do modelo de 7M vale para o de 100M. Economiza unidades do Colab com testes.

## 2. Dados

6. 🟢 **Fase final com dados melhores ("annealing")**: nos últimos ~10% dos passos do pré-treino,
   aumentar a fração de Wikipédia, textos escritos à mão e trechos do GigaVerbo com nota educacional
   alta, junto com o decaimento da taxa de aprendizado. Em modelos pequenos isso costuma render mais do
   que o mesmo número de tokens espalhados pelo treino todo.
7. 🟢 **Atualizar a ortografia dos livros antigos** ("pharmacia" → "farmácia", "elle" → "ele",
   "portuguez" → "português") com uma lista de regras antes de treinar o tokenizer. O tokenizer deixa de
   gastar vocabulário com grafias de 1900 e o modelo para de misturar as duas no chat. Outra opção:
   dar peso menor aos livros anteriores a 1940.
8. 🟡 **Filtro por perplexidade**: medir cada documento com um modelo pequeno treinado só na
   Wikipédia (ou com a própria Laika) e descartar os 10–20% piores (listas, lixo de OCR, tabelas).
   Complementa as notas de qualidade do GigaVerbo-v2.
9. 🟡 **Duplicatas quase iguais (MinHash/LSH)**, não só as exatas: na Wikipédia e em textos da web há
   muitas páginas quase idênticas (municípios, espécies, "freguesias portuguesas"). Elas fazem o modelo
   repetir modelos de frase — a resposta "freguesia portuguesa do concelho de..." para "Quem foi a
   Laika?" vem daí.
10. 🟢 **Separar o banco de avaliação do treino**: tirar do pré-treino e do fine-tuning as perguntas do
    script de avaliação (e textos quase iguais a elas), para o número medido não ser decoreba.

## 3. Fine-tuning e comportamento

11. 🟢 **Exemplos de "não sei"**: perguntas com um Contexto que não tem a resposta (ou sem contexto,
    sobre fatos raros) com respostas como "Não encontrei isso nos meus textos." Hoje a Laika sempre
    inventa algo; isso reduz as alucinações mais que qualquer outra coisa barata.
12. 🟢 **Contexto errado de propósito**: ~10% dos exemplos com RAG recebem um trecho de outro artigo e a
    resposta certa ignora o trecho. Ensina o modelo a não copiar contexto que não combina (o problema
    que o limite de confiança do `rag.py` hoje só esconde).
13. 🟢 **NEFTune**: ruído pequeno nos embeddings durante o fine-tuning (uma linha no `finetune.py`).
    Costuma melhorar respostas de modelos pequenos sem custo.
14. 🟡 **Avaliação das pessoas pelo app → treino por preferência**: botões 👍/👎 nas respostas e "gerar
    outra resposta" (que o app já tem) geram pares "melhor × pior". Exportados num `feedback.jsonl`
    (pode ir no zip do backup), viram treino por DPO ou, mais simples, "rejection sampling": gerar 4
    respostas no Colab, ficar com as que você aprovaria e treinar nelas.
15. 🟡 **Destilação de um modelo aberto maior**: o modelo continua sendo treinado do zero (pesos
    próprios), mas no fine-tuning aprende também com as probabilidades de um professor em português com
    licença permissiva (ex.: Tucano2). É um meio-termo entre "do zero" e só ajustar um modelo pronto.
    Conferir a licença do professor e dos textos gerados.
16. 🟢 **Tokens especiais para o RAG** (`<|contexto|>`, `<|fonte|>`) em vez das palavras "Contexto:" e
    "Pergunta:", junto com o tokenizer novo da Fase 1. O modelo distingue melhor o que é trecho e o que
    é pergunta, e fica fácil pedir a citação no meio da resposta (`[1]`) quando houver vários trechos.
17. 🟡 **Respostas no tamanho certo**: marcar nos exemplos escritos se a resposta é curta ou longa e
    treinar com um controle no prompt (`<|curta|>`/`<|longa|>`). O app já tem a opção "Tamanho das
    respostas", que hoje só corta a geração.

## 4. No celular e no Windows

18. 🟡 **Pesos em int8** (quantização por canal) no `exportar_modelo.py`, no `ConversorPt` e no
    `Modelo.java`: o arquivo cai à metade do fp16 (o de 100M fica com ~100 MB) e a conta fica mais rápida
    no processador do celular. Conferir a perda/as respostas contra o fp32 antes de adotar.
19. 🟡 **Decodificação especulativa**: a Laika de 7M escreve um rascunho de 4–6 tokens e a de 100M só
    confere; com o mesmo tokenizer, a de 100M responde 2–3× mais rápido no celular e no Windows, sem
    mudar o texto gerado (com amostragem, a distribuição é a mesma).
20. 🟢 **Temperatura por tipo de pergunta**: perguntas com RAG (fatos) com temperatura ~0,3; conversa
    com ~0,8. O `wants_rag` já separa os dois casos.
21. 🟡 **Reordenar os trechos do RAG com o próprio modelo**: para os 5 melhores trechos da busca, medir a
    probabilidade que a Laika dá à pergunta dado o trecho e ficar com o melhor. Sai melhor que só a nota
    da busca e não precisa de um modelo de embeddings.
22. 🟡 **Memória da conversa com resumo** (quando houver contexto de 2048): quando a janela encher,
    trocar as mensagens antigas por um resumo curto (extrativo no começo) em vez de cortá-las.

## 5. Processo

23. 🟢 **Histórico de treinos**: cada execução das células 3 e 4 grava no Drive uma linha num
    `historico.csv` (data, preset, passos, tokens, val loss, nota do banco de perguntas, link do
    checkpoint). O app pode mostrar esse histórico na tela Colab.
24. 🟢 **Só exportar se melhorou**: a célula 6 compara a nota do banco de perguntas do modelo novo com
    a do anterior e avisa (ou não exporta) se piorou — evita levar para o celular um fine-tuning ruim.
25. 🟢 **Sementes fixas** em `train.py`/`finetune.py` (torch, numpy, random) e a semente gravada no
    checkpoint, para comparar versões sabendo que a diferença veio da mudança e não da sorte.
