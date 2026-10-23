package com.brunodevpro.laika.core;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.function.ToIntFunction;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** As funções do data_utils.py usadas no chat (formato do prompt e escolha das palavras do RAG). */
public final class Texto {
    private Texto() {
    }

    public static final String USER = "<|user|>";
    public static final String ASSISTANT = "<|assistant|>";
    public static final String END = "<|end|>";
    public static final String EOT = "<|endoftext|>";
    public static final String PAD = "[PAD]";
    public static final int MAX_CONTEXT_WORDS = 80;

    private static Set<String> conjunto(String palavras) {
        return new HashSet<>(Arrays.asList(palavras.trim().split("\\s+")));
    }

    static final Set<String> STOPWORDS = conjunto(
            "a o os as um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas para pra pro com sem sob "
            + "sobre ate e ou mas nem que quem qual quais quanto quantos quanta quantas como onde aonde quando porque se nao sim "
            + "ja tambem muito muita muitos muitas mais menos tao tanto ser foi era sao eram sera estar esta estao estava ter tem "
            + "tinha ha haver fazer faz fez isso isto esse essa este aquele aquela aquilo ele ela eles elas eu tu voce voces vos "
            + "me te lhe meu minha meus minhas seu sua seus suas teu tua nosso nossa dele dela algum alguma alguns algumas todo "
            + "toda todos todas outro outra cada seja sejam pode podem posso sabe saber diga fale explique defina significa "
            + "significado conte fala diz dizer existe existem coisa coisas entao assim aqui ali favor obrigado obrigada ola oi "
            + "tipo vez vezes ano anos dia dias hoje ontem amanha agora sempre nunca qualquer cujo cuja onde "
            + "fica ficam ficou funciona funcionam acontece aconteceu chama chamado chamada");
    static final Set<String> PERSONAL = conjunto(
            "voce voces seu sua seus suas teu tua te laika eu meu minha meus minhas mim comigo contigo");
    static final Set<String> INSTRUCTIONS = conjunto(
            "corrija complete termine resuma continue escreva crie use cite conjugue passe transforme separe traduza "
            + "classifique calcule conte faca leia vamos apresente");

    /**
     * Flag para \s, \b e \d entenderem Unicode como no Python. No Android a regex (ICU) já é Unicode
     * e não aceita essa flag (dá erro), então ela só é usada fora do Android.
     */
    public static final int UNICODE = "Dalvik".equals(System.getProperty("java.vm.name"))
            ? 0 : Pattern.UNICODE_CHARACTER_CLASS;

    private static final Pattern PALAVRA = Pattern.compile("[a-z0-9]+");

    /** Minúsculas e sem acentos (para comparar palavras). */
    public static String normalizar(String texto) {
        String d = Normalizer.normalize(texto.toLowerCase(Locale.ROOT), Normalizer.Form.NFKD);
        StringBuilder sb = new StringBuilder(d.length());
        for (int i = 0; i < d.length(); i++) {
            char c = d.charAt(i);
            int tipo = Character.getType(c);
            if (tipo != Character.NON_SPACING_MARK && tipo != Character.ENCLOSING_MARK
                    && tipo != Character.COMBINING_SPACING_MARK) {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    public static List<String> palavras(String texto) {
        List<String> r = new ArrayList<>();
        Matcher m = PALAVRA.matcher(normalizar(texto));
        while (m.find()) r.add(m.group());
        return r;
    }

    private static boolean soLetras(String w) {
        for (int i = 0; i < w.length(); i++) if (!Character.isLetter(w.charAt(i))) return false;
        return !w.isEmpty();
    }

    private static boolean soDigitos(String w) {
        for (int i = 0; i < w.length(); i++) if (!Character.isDigit(w.charAt(i))) return false;
        return !w.isEmpty();
    }

    /** Palavras que valem para a busca: sem stopwords, com 3+ letras (ou números longos). */
    public static List<String> palavrasDeConteudo(String texto) {
        Set<String> vistas = new LinkedHashSet<>();
        for (String w : palavras(texto)) {
            if (STOPWORDS.contains(w) || vistas.contains(w)) continue;
            if ((soLetras(w) && w.length() >= 3) || (soDigitos(w) && w.length() >= 3)) vistas.add(w);
        }
        return new ArrayList<>(vistas);
    }

    /** str.split() do Python: separa por qualquer espaço em branco e ignora vazios. */
    public static String[] separar(String s) {
        String t = aparar(s);
        return t.isEmpty() ? new String[0] : ESPACOS.split(t);
    }

    private static final Pattern ESPACOS = Pattern.compile("\\s+", UNICODE);

    /** str.strip() do Python (String.strip() só existe a partir do Android 13). */
    public static String aparar(String s) {
        int a = 0, b = s.length();
        while (a < b && espaco(s.charAt(a))) a++;
        while (b > a && espaco(s.charAt(b - 1))) b--;
        return s.substring(a, b);
    }

    static boolean espaco(char c) {
        return Character.isWhitespace(c) || Character.isSpaceChar(c);
    }

    private static String tirarPontas(String s, String chars) {
        int a = 0, b = s.length();
        while (a < b && chars.indexOf(s.charAt(a)) >= 0) a++;
        while (b > a && chars.indexOf(s.charAt(b - 1)) >= 0) b--;
        return s.substring(a, b);
    }

    /** Decide se vale procurar contexto nos textos (mesma regra do wants_rag). */
    public static boolean querRag(String pergunta) {
        String[] todas = separar(pergunta);
        if (pergunta.contains("Contexto:") || todas.length > 40) return false;
        List<String> primeiras = new ArrayList<>();
        for (int i = 0; i < Math.min(2, todas.length); i++) {
            primeiras.add(tirarPontas(todas[i].toLowerCase(Locale.ROOT), ",.!?:;"));
        }
        if (!primeiras.isEmpty() && primeiras.get(0).equals("me")) primeiras.remove(0);
        if (!primeiras.isEmpty() && (primeiras.get(0).equals("dê") || INSTRUCTIONS.contains(normalizar(primeiras.get(0))))) {
            return false;
        }
        for (String w : palavras(pergunta)) if (PERSONAL.contains(w)) return false;
        return !palavrasDeConteudo(pergunta).isEmpty();
    }

    public static String perguntaComContexto(String pergunta, String contexto) {
        return "Contexto: " + contexto + "\nPergunta: " + pergunta;
    }

    /**
     * Corta o contexto (em palavras) até a pergunta com contexto caber em `orcamento` tokens.
     * Devolve o texto da pergunta com contexto, ou null se nem um contexto curto couber.
     */
    public static String ajustarContexto(ToIntFunction<String> contarTokens, String pergunta, String contexto,
                                         int orcamento) {
        String[] palavras = separar(contexto);
        int n = Math.min(palavras.length, MAX_CONTEXT_WORDS);
        while (n >= 12) {
            String trecho = String.join(" ", Arrays.asList(palavras).subList(0, n)) + (n < palavras.length ? "..." : "");
            String texto = perguntaComContexto(pergunta, trecho);
            if (contarTokens.applyAsInt(texto) <= orcamento) return texto;
            n -= 10;
        }
        return null;
    }
}
