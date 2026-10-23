package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.Texto;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/** As funções de exemplos de chat do data_utils.py (perguntas escritas, sintéticas e resumos). */
public final class DadosChat {
    private DadosChat() {
    }

    static final Pattern FRASES = Pattern.compile("(?<=[.!?…])\\s+", Texto.UNICODE);
    static final String STRIP = ".,;:!?…—–-\"'«»()[]“”‘’";

    public static String chat(String pergunta, String resposta) {
        return Texto.USER + " " + pergunta + " " + Texto.ASSISTANT + " " + resposta + " " + Texto.END;
    }

    /** parse_qa_text: "<|user|> pergunta <|assistant|> resposta <|end|>" (comentários com # antes do <|user|>). */
    public static List<String> lerPerguntas(String texto) {
        List<String> r = new ArrayList<>();
        for (String bloco : texto.split(Pattern.quote(Texto.END), -1)) {
            bloco = Texto.aparar(bloco);
            if (bloco.isEmpty() || !bloco.contains(Texto.USER) || !bloco.contains(Texto.ASSISTANT)) continue;
            int a = bloco.indexOf(Texto.ASSISTANT);
            String parteUsuario = bloco.substring(0, a), resposta = Texto.aparar(bloco.substring(a + Texto.ASSISTANT.length()));
            String pergunta = Texto.aparar(parteUsuario.substring(parteUsuario.lastIndexOf(Texto.USER) + Texto.USER.length()));
            if (pergunta.isEmpty() || resposta.isEmpty()) continue;
            r.add(chat(pergunta, resposta));
        }
        return r;
    }

    public static List<String> lerPerguntas(List<File> arquivos, Registro reg) throws IOException {
        List<String> r = new ArrayList<>();
        for (File f : arquivos) {
            List<String> e = lerPerguntas(Corpus.lerTexto(f));
            reg.log("  " + f.getName() + ": " + e.size() + " exemplos");
            r.addAll(e);
        }
        return r;
    }

    /** split_example: (pergunta, resposta). */
    public static String[] separar(String exemplo) {
        int a = exemplo.indexOf(Texto.ASSISTANT);
        String q = Texto.aparar(exemplo.substring(0, a).replace(Texto.USER, ""));
        String r = Texto.aparar(exemplo.substring(a + Texto.ASSISTANT.length()).replace(Texto.END, ""));
        return new String[]{q, r};
    }

    // ---------- frases dos livros ----------

    private static boolean letra(char c) {
        return Character.isLetter(c);
    }

    static boolean fraseBoa(String s) {
        String[] palavras = Texto.separar(s);
        if (palavras.length < 5 || palavras.length > 40) return false;
        String chars = s.replace(" ", "");
        int letras = 0;
        for (int i = 0; i < chars.length(); i++) if (letra(chars.charAt(i))) letras++;
        if (letras < 0.75 * chars.length()) return false;
        if (maiuscula(s)) return false;
        char ult = s.charAt(s.length() - 1);
        return ult == '.' || ult == '!' || ult == '?' || ult == '…';
    }

    /** str.isupper() do Python. */
    private static boolean maiuscula(String s) {
        boolean temCaixa = false;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isLowerCase(c)) return false;
            if (Character.isUpperCase(c)) temCaixa = true;
        }
        return temCaixa;
    }

    private static boolean minuscula(String s) {
        boolean temCaixa = false;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isUpperCase(c) || Character.isTitleCase(c)) return false;
            if (Character.isLowerCase(c)) temCaixa = true;
        }
        return temCaixa;
    }

    private static boolean soLetras(String s) {
        if (s.isEmpty()) return false;
        for (int i = 0; i < s.length(); i++) if (!letra(s.charAt(i))) return false;
        return true;
    }

    static String tirar(String s, String chars) {
        int a = 0, b = s.length();
        while (a < b && chars.indexOf(s.charAt(a)) >= 0) a++;
        while (b > a && chars.indexOf(s.charAt(b - 1)) >= 0) b--;
        return s.substring(a, b);
    }

    /** book_paragraphs: parágrafos como listas de frases "boas". */
    public static List<List<String>> paragrafos(String texto) {
        List<List<String>> r = new ArrayList<>();
        for (String bloco : texto.split("\n\n", -1)) {
            List<String> frases = new ArrayList<>();
            for (String s : FRASES.split(Texto.aparar(bloco), -1)) {
                s = Texto.aparar(s);
                if (!s.isEmpty() && fraseBoa(s)) frases.add(s);
            }
            if (!frases.isEmpty()) r.add(frases);
        }
        return r;
    }

    static List<String> palavrasDeConteudo(String frase) {
        List<String> r = new ArrayList<>();
        String[] ws = Texto.separar(frase);
        for (int i = 1; i < ws.length; i++) {
            String w = tirar(ws[i], STRIP);
            if (w.length() >= 5 && soLetras(w) && minuscula(w)) r.add(w);
        }
        return r;
    }

    static final String[] PEDIDOS_RESUMO = {"Resuma o texto: %s", "Resuma: %s", "Faça um resumo do texto: %s",
            "Qual é a ideia principal deste texto? %s", "Resuma em uma frase: %s"};

    /** extractive_summary: a(s) frase(s) que mais compartilham palavras com o resto do parágrafo. */
    public static String resumoExtrativo(List<String> frases) {
        List<Set<String>> sacos = new ArrayList<>();
        Map<String, Integer> freq = new HashMap<>();
        for (String s : frases) {
            Set<String> saco = new LinkedHashSet<>();
            for (String w : Texto.separar(s)) {
                String t = tirar(w, STRIP);
                if (t.length() >= 4) saco.add(tirar(w.toLowerCase(Locale.ROOT), STRIP));
            }
            sacos.add(saco);
            for (String w : saco) freq.merge(w, 1, Integer::sum);
        }
        List<double[]> notas = new ArrayList<>();
        for (int i = 0; i < sacos.size(); i++) {
            int compartilhadas = 0;
            for (String w : sacos.get(i)) compartilhadas += freq.get(w) - 1;
            notas.add(new double[]{(double) compartilhadas / (sacos.get(i).size() + 3) + (i == 0 ? 0.3 : 0.0), i});
        }
        notas.sort((a, b) -> a[0] != b[0] ? Double.compare(b[0], a[0]) : Double.compare(b[1], a[1]));
        int manter = frases.size() >= 5 ? 2 : 1;
        List<Integer> escolhidas = new ArrayList<>();
        for (int i = 0; i < Math.min(manter, notas.size()); i++) escolhidas.add((int) notas.get(i)[1]);
        Collections.sort(escolhidas);
        List<String> r = new ArrayList<>();
        for (int i : escolhidas) r.add(frases.get(i));
        return String.join(" ", r);
    }

    /** summary_examples: "Resuma o texto: <parágrafo>" -> resumo extrativo. */
    public static List<String> resumos(List<String> textos, int n, Aleatorio rng) {
        List<List<String>> cand = new ArrayList<>();
        for (String t : textos) {
            for (List<String> p : paragrafos(t)) {
                int palavras = 0;
                for (String s : p) palavras += Texto.separar(s).length;
                if (p.size() >= 3 && p.size() <= 6 && palavras >= 40 && palavras <= 90) cand.add(p);
            }
        }
        rng.embaralhar(cand);
        List<String> r = new ArrayList<>();
        for (int i = 0; i < Math.min(n, cand.size()); i++) {
            List<String> p = cand.get(i);
            r.add(chat(String.format(PEDIDOS_RESUMO[rng.inteiro(PEDIDOS_RESUMO.length)], String.join(" ", p)), resumoExtrativo(p)));
        }
        return r;
    }

    private static <T> T escolher(List<T> l, Aleatorio rng) {
        return l.get(rng.inteiro(l.size()));
    }

    /** synthetic_examples: continue / frase com a palavra / complete, mais os resumos. */
    public static List<String> sinteticos(List<String> textos, int n, Aleatorio rng, List<String> textosResumo) {
        int nResumo = (int) (n * 0.2);
        List<String> exemplos = new ArrayList<>(resumos(textosResumo != null ? textosResumo : textos, nResumo, rng));
        n -= exemplos.size();
        List<List<String>> paragrafos = new ArrayList<>();
        for (String t : textos) paragrafos.addAll(paragrafos(t));
        List<List<String>> multi = new ArrayList<>();
        for (List<String> p : paragrafos) if (p.size() >= 2) multi.add(p);
        if (paragrafos.isEmpty()) return exemplos;
        Set<String> vistos = new HashSet<>(exemplos);
        int alvo = exemplos.size() + n, tentativas = 0;
        String[] continuar = {"Continue o texto: %s", "Continue: %s", "O que vem depois de: %s", "Escreva a continuação: %s"};
        String[] palavra = {"Escreva uma frase com a palavra %s.", "Use a palavra \"%s\" em uma frase.", "Crie uma frase com %s.",
                "Me dê um exemplo de frase com a palavra %s."};
        String[] completar = {"Complete a frase: %s", "Termine a frase: %s", "Complete: %s"};
        while (exemplos.size() < alvo && tentativas < n * 10) {
            tentativas++;
            double tipo = rng.real();
            String q, a;
            if (tipo < 0.4 && !multi.isEmpty()) {
                List<String> p = escolher(multi, rng);
                int i = rng.inteiro(p.size() - 1);
                a = p.get(i + 1);
                if (i + 2 < p.size() && rng.real() < 0.4) a += " " + p.get(i + 2);
                q = String.format(continuar[rng.inteiro(continuar.length)], p.get(i));
            } else if (tipo < 0.75) {
                String frase = escolher(escolher(paragrafos, rng), rng);
                List<String> ws = palavrasDeConteudo(frase);
                if (ws.isEmpty()) continue;
                a = frase;
                q = String.format(palavra[rng.inteiro(palavra.length)], escolher(ws, rng));
            } else {
                String frase = escolher(escolher(paragrafos, rng), rng);
                String[] ws = Texto.separar(frase);
                int hi = Math.max(3, ws.length - 3);
                int corte = 3 + rng.inteiro(hi - 3 + 1);
                a = String.join(" ", java.util.Arrays.asList(ws).subList(Math.min(corte, ws.length), ws.length));
                q = String.format(completar[rng.inteiro(completar.length)],
                        String.join(" ", java.util.Arrays.asList(ws).subList(0, Math.min(corte, ws.length))));
            }
            String ex = chat(q, a);
            if (vistos.add(ex)) exemplos.add(ex);
        }
        return exemplos;
    }
}
