package com.brunodevpro.laika.core;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Tokenizer BPE byte-level, igual ao da biblioteca tokenizers (Hugging Face) usado no train.py:
 * pré-tokenizador ByteLevel (add_prefix_space=False, regex do GPT-2) e tokens especiais
 * reconhecidos antes de tudo. Lê o tokenizer.txt gerado por android/exportar_modelo.py.
 */
public final class Tokenizador {
    // Mesma regex do GPT-2 que o ByteLevel usa.
    private static final Pattern PRE = Pattern.compile(
            "'s|'t|'re|'ve|'m|'ll|'d| ?\\p{L}+| ?\\p{N}+| ?[^\\s\\p{L}\\p{N}]+|\\s+(?!\\S)|\\s+",
            Texto.UNICODE);

    private final String[] vocab;
    private final Map<String, Integer> ids = new HashMap<>();
    private final Map<String, Integer> mergeRank = new HashMap<>();
    private final String[] especiais;
    private final boolean[] ehEspecial;
    private final char[] byteParaChar = new char[256];
    private final int[] charParaByte = new int[512];
    private final Map<String, int[]> cache = new HashMap<>();

    public Tokenizador(InputStream in) throws IOException {
        BufferedReader r = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
        int n = cabecalho(r.readLine(), "vocab");
        vocab = new String[n];
        for (int i = 0; i < n; i++) {
            vocab[i] = r.readLine();
            ids.put(vocab[i], i);
        }
        int ne = cabecalho(r.readLine(), "special");
        especiais = new String[ne];
        ehEspecial = new boolean[n];
        for (int i = 0; i < ne; i++) {
            especiais[i] = r.readLine();
            ehEspecial[ids.get(especiais[i])] = true;
        }
        int nm = cabecalho(r.readLine(), "merges");
        for (int i = 0; i < nm; i++) {
            mergeRank.put(r.readLine(), i);
        }
        montarTabelaDeBytes();
    }

    private static int cabecalho(String linha, String nome) throws IOException {
        if (linha == null || !linha.startsWith(nome + " ")) {
            throw new IOException("tokenizer.txt inválido: esperava '" + nome + "'");
        }
        return Integer.parseInt(linha.substring(nome.length() + 1).trim());
    }

    /** Tabela bytes -> caracteres visíveis do GPT-2 (o espaço vira 'Ġ', a quebra de linha 'Ċ'). */
    private void montarTabelaDeBytes() {
        boolean[] direto = new boolean[256];
        for (int b = '!'; b <= '~'; b++) direto[b] = true;
        for (int b = 0xA1; b <= 0xAC; b++) direto[b] = true;
        for (int b = 0xAE; b <= 0xFF; b++) direto[b] = true;
        int extra = 0;
        for (int b = 0; b < 256; b++) {
            char c = direto[b] ? (char) b : (char) (256 + extra++);
            byteParaChar[b] = c;
            charParaByte[c] = b;
        }
    }

    public int tamanhoVocab() {
        return vocab.length;
    }

    /** Id do token, ou -1 se não existir. */
    public int id(String token) {
        Integer i = ids.get(token);
        return i == null ? -1 : i;
    }

    public int[] codificar(String texto) {
        List<Integer> saida = new ArrayList<>();
        int i = 0;
        while (i < texto.length()) {
            // Próximo token especial (o mais longo, se dois começarem no mesmo lugar).
            int melhorPos = -1;
            String melhor = null;
            for (String esp : especiais) {
                int p = texto.indexOf(esp, i);
                if (p >= 0 && (melhorPos < 0 || p < melhorPos || (p == melhorPos && esp.length() > melhor.length()))) {
                    melhorPos = p;
                    melhor = esp;
                }
            }
            int fim = melhorPos < 0 ? texto.length() : melhorPos;
            if (fim > i) codificarTrecho(texto.substring(i, fim), saida);
            if (melhor == null) break;
            saida.add(ids.get(melhor));
            i = melhorPos + melhor.length();
        }
        int[] r = new int[saida.size()];
        for (int k = 0; k < r.length; k++) r[k] = saida.get(k);
        return r;
    }

    private void codificarTrecho(String trecho, List<Integer> saida) {
        Matcher m = PRE.matcher(trecho);
        while (m.find()) {
            byte[] bytes = m.group().getBytes(StandardCharsets.UTF_8);
            StringBuilder sb = new StringBuilder(bytes.length);
            for (byte b : bytes) sb.append(byteParaChar[b & 0xFF]);
            for (int t : bpe(sb.toString())) saida.add(t);
        }
    }

    private int[] bpe(String palavra) {
        int[] emCache = cache.get(palavra);
        if (emCache != null) return emCache;
        List<String> partes = new ArrayList<>();
        for (int k = 0; k < palavra.length(); k++) partes.add(String.valueOf(palavra.charAt(k)));
        while (partes.size() > 1) {
            int melhorRank = Integer.MAX_VALUE, melhorK = -1;
            for (int k = 0; k + 1 < partes.size(); k++) {
                Integer rank = mergeRank.get(partes.get(k) + " " + partes.get(k + 1));
                if (rank != null && rank < melhorRank) {
                    melhorRank = rank;
                    melhorK = k;
                }
            }
            if (melhorK < 0) break;
            String a = partes.get(melhorK), b = partes.get(melhorK + 1);
            List<String> nova = new ArrayList<>(partes.size());
            for (int k = 0; k < partes.size(); k++) {
                if (k + 1 < partes.size() && partes.get(k).equals(a) && partes.get(k + 1).equals(b)) {
                    nova.add(a + b);
                    k++;
                } else {
                    nova.add(partes.get(k));
                }
            }
            partes = nova;
        }
        int unk = id("[UNK]");
        int[] r = new int[partes.size()];
        for (int k = 0; k < r.length; k++) {
            Integer t = ids.get(partes.get(k));
            r[k] = t == null ? unk : t;
        }
        if (cache.size() < 50000) cache.put(palavra, r);
        return r;
    }

    /** Texto dos tokens, sem os tokens especiais (igual ao decode do tokenizers). */
    public String decodificar(int[] tokens, int de, int ate) {
        java.io.ByteArrayOutputStream bytes = new java.io.ByteArrayOutputStream();
        for (int k = de; k < ate; k++) {
            int t = tokens[k];
            if (t < 0 || t >= vocab.length || ehEspecial[t]) continue;
            String s = vocab[t];
            for (int c = 0; c < s.length(); c++) {
                char ch = s.charAt(c);
                bytes.write(ch < charParaByte.length ? charParaByte[ch] : '?');
            }
        }
        return new String(bytes.toByteArray(), StandardCharsets.UTF_8);
    }

    public String decodificar(int[] tokens) {
        return decodificar(tokens, 0, tokens.length);
    }
}
