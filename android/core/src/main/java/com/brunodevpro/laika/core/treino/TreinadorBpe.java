package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.Tokenizador;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.TreeSet;

/**
 * Treina um tokenizer BPE byte-level como o BpeTrainer da biblioteca tokenizers (o que o
 * train.py usa): lê os arquivos linha a linha (com o \n), pré-tokeniza com a regex do GPT-2,
 * começa com os tokens especiais e os 256 caracteres do alfabeto (em ordem de código) e
 * junta o par mais frequente até chegar no tamanho do vocabulário. Empate: o par de ids menores.
 * Gera o tokenizer.txt do app.
 */
public final class TreinadorBpe {
    private TreinadorBpe() {
    }

    /** Lista de ints que cresce (para não criar milhões de Integer). */
    private static final class Ints {
        int[] v = new int[4];
        int n;

        void add(int x) {
            if (n == v.length) v = Arrays.copyOf(v, n * 2);
            v[n++] = x;
        }
    }

    private static final class Juncao {
        final long par;
        long contagem;
        final Ints onde;

        Juncao(long par, long contagem, Ints onde) {
            this.par = par;
            this.contagem = contagem;
            this.onde = onde;
        }
    }

    private static long par(int a, int b) {
        return ((long) a << 32) | (b & 0xFFFFFFFFL);
    }

    /**
     * @param maxBytes lê no máximo isto de texto (o resto dos arquivos é ignorado), para caber na memória do celular
     */
    public static String treinar(List<File> arquivos, int tamanhoVocab, List<String> especiais, long maxBytes, Registro reg)
            throws IOException {
        // 1) contar as palavras (pedaços da pré-tokenização)
        Map<String, long[]> contagem = new HashMap<>();
        long lidos = 0;
        int i = 0;
        for (File f : arquivos) {
            if (lidos >= maxBytes) {
                reg.log(String.format("Tokenizer: usei %d de %d arquivos (limite de %d MB de texto).", i, arquivos.size(),
                        maxBytes >> 20));
                break;
            }
            if (reg.parar()) throw new Parado();
            String texto = Corpus.lerTexto(f);
            lidos += f.length();
            int ini = 0;
            while (ini < texto.length()) {
                int fim = texto.indexOf('\n', ini);
                fim = fim < 0 ? texto.length() : fim + 1;
                Tokenizador.preTokenizar(texto.substring(ini, fim), p -> contagem.computeIfAbsent(p, x -> new long[1])[0]++);
                ini = fim;
            }
            i++;
            if (i % 20 == 0) reg.progresso(0.5 * lidos / Math.max(1, Math.min(maxBytes, total(arquivos))),
                    "Tokenizer: lendo " + i + "/" + arquivos.size());
        }

        // 2) vocabulário inicial: especiais + alfabeto em ordem de código
        List<String> vocab = new ArrayList<>(especiais);
        Map<String, Integer> ids = new HashMap<>();
        for (int k = 0; k < vocab.size(); k++) ids.put(vocab.get(k), k);
        TreeSet<Character> alfabeto = new TreeSet<>();
        for (char c : Tokenizador.alfabeto()) alfabeto.add(c);
        for (String w : contagem.keySet()) for (int k = 0; k < w.length(); k++) alfabeto.add(w.charAt(k));
        for (char c : alfabeto) {
            String s = String.valueOf(c);
            if (!ids.containsKey(s)) {
                ids.put(s, vocab.size());
                vocab.add(s);
            }
        }

        // 3) palavras como listas de ids
        int nPal = contagem.size();
        int[][] palavras = new int[nPal][];
        int[] tamanhos = new int[nPal];
        long[] vezes = new long[nPal];
        int w = 0;
        for (Map.Entry<String, long[]> e : contagem.entrySet()) {
            String s = e.getKey();
            int[] sim = new int[s.length()];
            for (int k = 0; k < s.length(); k++) sim[k] = ids.get(String.valueOf(s.charAt(k)));
            palavras[w] = sim;
            tamanhos[w] = sim.length;
            vezes[w] = e.getValue()[0];
            w++;
        }
        contagem.clear();
        reg.log(String.format("Tokenizer: %,d palavras diferentes em %.0f MB de texto.", nPal, lidos / 1e6));

        // 4) contagem dos pares e onde aparecem
        Map<Long, long[]> pares = new HashMap<>();
        Map<Long, Ints> onde = new HashMap<>();
        for (w = 0; w < nPal; w++) {
            int[] sim = palavras[w];
            for (int k = 0; k + 1 < tamanhos[w]; k++) {
                long p = par(sim[k], sim[k + 1]);
                pares.computeIfAbsent(p, x -> new long[1])[0] += vezes[w];
                onde.computeIfAbsent(p, x -> new Ints()).add(w);
            }
        }
        PriorityQueue<Juncao> fila = new PriorityQueue<>((a, b) -> {
            if (a.contagem != b.contagem) return Long.compare(b.contagem, a.contagem);
            return Long.compare(a.par, b.par);  // empate: par (a, b) menor primeiro
        });
        for (Map.Entry<Long, Ints> e : onde.entrySet()) {
            long c = pares.get(e.getKey())[0];
            if (c > 0) fila.add(new Juncao(e.getKey(), c, e.getValue()));
        }
        onde.clear();

        // 5) juntar até completar o vocabulário
        List<String> juncoes = new ArrayList<>();
        int[] carimbo = new int[nPal];
        int rodada = 0;
        int alvo = tamanhoVocab - vocab.size();
        while (vocab.size() < tamanhoVocab && !fila.isEmpty()) {
            Juncao topo = fila.poll();
            long atual = pares.containsKey(topo.par) ? pares.get(topo.par)[0] : 0;
            if (topo.contagem != atual) {
                topo.contagem = atual;
                fila.add(topo);
                continue;
            }
            if (topo.contagem < 1) break;
            int a = (int) (topo.par >>> 32), b = (int) topo.par;
            String novo = vocab.get(a) + vocab.get(b);
            Integer existente = ids.get(novo);
            int novoId = existente != null ? existente : vocab.size();
            if (existente == null) {
                ids.put(novo, novoId);
                vocab.add(novo);
            }
            juncoes.add(vocab.get(a) + " " + vocab.get(b));

            rodada++;
            Map<Long, Ints> mudou = new HashMap<>();
            for (int q = 0; q < topo.onde.n; q++) {
                int pw = topo.onde.v[q];
                if (carimbo[pw] == rodada) continue;  // a mesma palavra pode aparecer mais de uma vez na lista
                carimbo[pw] = rodada;
                juntar(palavras, tamanhos, pw, a, b, novoId, vezes[pw], pares, mudou);
            }
            for (Map.Entry<Long, Ints> e : mudou.entrySet()) {
                long c = pares.get(e.getKey())[0];
                if (c > 0) fila.add(new Juncao(e.getKey(), c, e.getValue()));
            }
            if (juncoes.size() % 200 == 0) {
                if (reg.parar()) throw new Parado();
                reg.progresso(0.5 + 0.5 * juncoes.size() / Math.max(1, alvo),
                        "Tokenizer: " + vocab.size() + "/" + tamanhoVocab + " tokens");
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append("vocab ").append(vocab.size()).append('\n');
        for (String t : vocab) sb.append(t).append('\n');
        sb.append("special ").append(especiais.size()).append('\n');
        for (String t : especiais) sb.append(t).append('\n');
        sb.append("merges ").append(juncoes.size()).append('\n');
        for (String m : juncoes) sb.append(m).append('\n');
        reg.log(String.format("Tokenizer treinado: %d tokens, %d junções.", vocab.size(), juncoes.size()));
        return sb.toString();
    }

    private static long total(List<File> fs) {
        long t = 0;
        for (File f : fs) t += f.length();
        return t;
    }

    /** Word::merge da biblioteca tokenizers: junta (a, b) -> novo e registra os pares que mudaram. */
    private static void juntar(int[][] palavras, int[] tamanhos, int w, int a, int b, int novo, long vezes,
                               Map<Long, long[]> pares, Map<Long, Ints> mudou) {
        int[] s = palavras[w];
        int n = tamanhos[w];
        int i = 0;
        while (i < n) {
            if (s[i] == a && i + 1 < n && s[i + 1] == b) {
                if (i > 0) {
                    soma(pares, par(s[i - 1], a), -vezes);
                    soma(pares, par(s[i - 1], novo), vezes);
                    mudou.computeIfAbsent(par(s[i - 1], novo), x -> new Ints()).add(w);
                }
                s[i] = novo;
                System.arraycopy(s, i + 2, s, i + 1, n - i - 2);
                n--;
                if (i < n - 1) {
                    soma(pares, par(b, s[i + 1]), -vezes);
                    soma(pares, par(novo, s[i + 1]), vezes);
                    mudou.computeIfAbsent(par(novo, s[i + 1]), x -> new Ints()).add(w);
                }
            }
            i++;
        }
        tamanhos[w] = n;
    }

    private static void soma(Map<Long, long[]> pares, long p, long d) {
        pares.computeIfAbsent(p, x -> new long[1])[0] += d;
    }
}
