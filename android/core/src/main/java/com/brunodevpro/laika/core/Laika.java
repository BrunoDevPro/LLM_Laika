package com.brunodevpro.laika.core;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.function.BooleanSupplier;

/**
 * Monta o prompt (como o build_prompt do chat.py) e gera a resposta (como o generate),
 * usando o cache de atenção do Modelo.
 */
public final class Laika {
    /** Recebe o texto gerado até agora, para mostrar a resposta aparecendo aos poucos. */
    public interface AoGerar {
        void parcial(String texto);
    }

    /** Parâmetros de amostragem (padrões do chat.py). */
    public static final class Opcoes {
        public double temperatura = 0.7;
        public int topK = 40;
        public double topP = 0.9;
        public double penalidade = 1.15;
        public int maxNovos = 80;
        /** Saída: quantos tokens a última chamada de gerar() produziu. */
        public int gerados;
    }

    /** Prompt pronto, o título do artigo usado pelo RAG e o trecho encontrado (ou null). */
    public static final class Prompt {
        public final String texto, fonte, trecho;

        Prompt(String texto, String fonte, String trecho) {
            this.texto = texto;
            this.fonte = fonte;
            this.trecho = trecho;
        }
    }

    public final Modelo modelo;
    public final Tokenizador tok;
    private final int endId;
    private final int[] proibidos;

    public Laika(Modelo modelo, Tokenizador tok) {
        this.modelo = modelo;
        this.tok = tok;
        endId = tok.id(Texto.END);
        proibidos = new int[]{tok.id(Texto.USER), tok.id(Texto.ASSISTANT), tok.id(Texto.PAD), tok.id(Texto.EOT)};
    }

    public Prompt montarPrompt(String pergunta, IndiceRag rag, Memoria memoria, int maxNovos) {
        return montarPrompt(pergunta, rag, memoria, maxNovos, null, modelo.block);
    }

    public Prompt montarPrompt(String pergunta, IndiceRag rag, Memoria memoria, int maxNovos,
                               List<String[]> historico) {
        return montarPrompt(pergunta, rag, memoria, maxNovos, historico, modelo.block);
    }

    /**
     * Como o build_prompt do chat.py. historico: trocas anteriores {pergunta, resposta}, da mais antiga
     * para a mais nova ("memória de IA"); entram as mais recentes (até MAX_HISTORY) que couberem, e só se a
     * pergunta depender da conversa (Texto.segueConversa).
     * bloco: a janela do modelo (parâmetro só para os testes compararem janelas diferentes).
     */
    public Prompt montarPrompt(String pergunta, IndiceRag rag, Memoria memoria, int maxNovos,
                               List<String[]> historico, int bloco) {
        int orcamento = bloco - maxNovos;
        List<String> partes = new ArrayList<>();
        String fonte = null, trecho = null;
        if (memoria != null) {
            String nota = memoria.contextoPara(pergunta);
            if (!nota.isEmpty()) partes.add(nota);
        }
        List<IndiceRag.Trecho> achados = rag != null && Texto.querRag(pergunta)
                ? rag.contextos(pergunta, Texto.trechosRag(bloco)) : new ArrayList<>();
        if (!achados.isEmpty()) {
            List<String> textos = new ArrayList<>();
            for (IndiceRag.Trecho t : achados) {
                partes.add(t.texto);
                textos.add(t.texto);
            }
            fonte = achados.get(0).titulo;
            trecho = String.join("\n\n", textos);
        }
        String atual = Texto.USER + " " + pergunta + " " + Texto.ASSISTANT;
        if (!partes.isEmpty()) {
            String comContexto = Texto.ajustarContexto(
                    t -> tok.codificar(Texto.USER + " " + t + " " + Texto.ASSISTANT).length,
                    pergunta, String.join(" ", partes), orcamento,
                    Texto.MAX_CONTEXT_WORDS * Math.max(1, achados.size()));
            if (comContexto == null) {
                fonte = null;
                trecho = null;
            } else {
                atual = Texto.USER + " " + comContexto + " " + Texto.ASSISTANT;
            }
        }
        List<String> turnos = new ArrayList<>();
        if (historico != null && Texto.segueConversa(pergunta)) {
            int ini = Math.max(0, historico.size() - Texto.MAX_HISTORY);
            for (int i = historico.size() - 1; i >= ini; i--) {
                List<String> candidato = new ArrayList<>();
                candidato.add(Texto.turno(historico.get(i)[0], historico.get(i)[1]));
                candidato.addAll(turnos);
                candidato.add(atual);
                if (tok.codificar(String.join(" ", candidato)).length > orcamento) break;
                candidato.remove(candidato.size() - 1);
                turnos = candidato;
            }
        }
        turnos.add(atual);
        return new Prompt(String.join(" ", turnos), fonte, trecho);
    }

    /** Com um tamanho máximo grande, a resposta tende a ser mais longa (min_answer_tokens do chat.py). */
    public static int minimoResposta(int maxNovos) {
        return Math.max(0, (maxNovos - 60) / 2);
    }

    /** Quanto tirar do logit do <|end|> no passo `passo` (end_penalty do chat.py). */
    public static double penalidadeFim(int passo, int minimo) {
        return passo >= minimo ? 0.0 : 3.0 * (1 - (double) passo / minimo);
    }

    public static String comCitacao(String resposta, String fonte) {
        return fonte != null ? resposta + " *" + fonte : resposta;
    }

    /**
     * Gera a continuação do prompt. pararNoFim=false é o modo "completar texto" (--base).
     * Devolve só o texto gerado (sem o prompt), como o chat.py.
     */
    public String gerar(String prompt, Opcoes op, boolean pararNoFim, Random rng, AoGerar aoGerar,
                        BooleanSupplier cancelado) {
        int[] promptIds = tok.codificar(prompt);
        int[] ids = Arrays.copyOf(promptIds, promptIds.length + op.maxNovos);
        int n = promptIds.length, promptLen = n;
        Modelo.Cache cache = modelo.novoCache();
        int bloco = modelo.block;
        int minimo = pararNoFim ? minimoResposta(op.maxNovos) : 0;

        for (int passo = 0; passo < op.maxNovos; passo++) {
            if (cancelado != null && cancelado.getAsBoolean()) break;
            float[] logits;
            if (n <= bloco) {
                // Com cache: só os tokens que ainda não passaram pelo modelo.
                logits = modelo.avancar(cache, ids, cache.tamanho(), n);
            } else {
                // Passou da janela: as posições mudam, então recalcula a janela inteira (igual ao chat.py).
                cache.limpar();
                logits = modelo.avancar(cache, ids, n - bloco, n);
            }

            for (int t : proibidos) if (t >= 0) logits[t] = Float.NEGATIVE_INFINITY;
            if (!pararNoFim && endId >= 0) logits[endId] = Float.NEGATIVE_INFINITY;
            if (minimo > 0 && endId >= 0) logits[endId] = (float) (logits[endId] - penalidadeFim(n - promptLen, minimo));

            // Penaliza só tokens que o próprio modelo já gerou (os últimos 60).
            Set<Integer> gerados = new LinkedHashSet<>();
            for (int k = Math.max(promptLen, n - 60); k < n; k++) gerados.add(ids[k]);
            for (int t : gerados) {
                float l = logits[t];
                logits[t] = l > 0 ? (float) (l / op.penalidade) : (float) (l * op.penalidade);
            }

            int proximo = amostrar(logits, op, rng);
            if (pararNoFim && proximo == endId) break;
            ids[n++] = proximo;
            if (aoGerar != null) aoGerar.parcial(semPedacoIncompleto(tok.decodificar(ids, promptLen, n)));
        }
        op.gerados = n - promptLen;
        return Texto.aparar(tok.decodificar(ids, promptLen, n));
    }

    /** Um caractere acentuado pode vir em dois tokens: esconde o pedaço incompleto no fim. */
    private static String semPedacoIncompleto(String s) {
        int b = s.length();
        while (b > 0 && s.charAt(b - 1) == '�') b--;
        return Texto.aparar(s.substring(0, b));
    }

    /** Temperatura, top-k e top-p (dentro do top-k), como no chat.py. */
    static int amostrar(float[] logits, Opcoes op, Random rng) {
        int k = Math.min(op.topK, logits.length);
        int[] idx = new int[k];
        float[] val = new float[k];
        int cheio = 0;
        for (int t = 0; t < logits.length; t++) {
            float v = (float) (logits[t] / op.temperatura);
            if (cheio < k) {
                int p = cheio++;
                while (p > 0 && val[p - 1] < v) {
                    val[p] = val[p - 1];
                    idx[p] = idx[p - 1];
                    p--;
                }
                val[p] = v;
                idx[p] = t;
            } else if (v > val[k - 1]) {
                int p = k - 1;
                while (p > 0 && val[p - 1] < v) {
                    val[p] = val[p - 1];
                    idx[p] = idx[p - 1];
                    p--;
                }
                val[p] = v;
                idx[p] = t;
            }
        }
        double[] prob = new double[k];
        double soma = 0;
        for (int i = 0; i < k; i++) {
            prob[i] = Math.exp(val[i] - val[0]);
            soma += prob[i];
        }
        double acumulado = 0, total = 0;
        for (int i = 0; i < k; i++) {
            prob[i] /= soma;
            boolean fica = acumulado < op.topP;  // cumulative - p < top_p
            acumulado += prob[i];
            if (!fica) prob[i] = 0;
            total += prob[i];
        }
        double r = rng.nextDouble() * total;
        for (int i = 0; i < k; i++) {
            r -= prob[i];
            if (r < 0 && prob[i] > 0) return idx[i];
        }
        return idx[0];
    }
}
