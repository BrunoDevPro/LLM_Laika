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
    /** Trocas anteriores que podem entrar no prompt ("memória de IA"), como o MAX_HISTORY do Python. */
    public static final int MAX_HISTORY = 5;

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

    /** "Faça um texto sobre X", "Me conte sobre X": o assunto é X (o _TOPIC do data_utils.py). */
    private static final Pattern TOPICO = Pattern.compile(
            "(?:^|\\s)(?:sobre|a respeito d[eoa]s?|acerca d[eoa]s?)\\s+(.+)$",
            Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE | UNICODE);

    /** O assunto de um pedido como "Faça um texto sobre planárias." ("planárias"), ou null (request_topic). */
    public static String assuntoDoPedido(String pergunta) {
        java.util.regex.Matcher m = TOPICO.matcher(aparar(pergunta));
        if (!m.find()) return null;
        String assunto = tirarPontas(m.group(1), " .!?;:");
        return palavrasDeConteudo(assunto).isEmpty() ? null : assunto;
    }

    private static final String NOME_PONTAS = ".,;:!?¿¡\"'()[]«»“”‘’";
    private static final Set<String> LIGACOES_NOME = conjunto("de da do dos das e");

    /**
     * O nome próprio mais longo da pergunta ("Santos Dumont" em "O que Santos Dumont inventou?"), ou null
     * (question_name). A primeira palavra só conta se a seguinte também for nome.
     */
    public static String nomeDaPergunta(String pergunta) {
        String[] brutas = separar(pergunta);
        boolean[] nome = new boolean[brutas.length];
        for (int i = 0; i < brutas.length; i++) {
            String w = tirarPontas(brutas[i], NOME_PONTAS);
            nome[i] = !w.isEmpty() && Character.isUpperCase(w.charAt(0)) && !STOPWORDS.contains(normalizar(w));
        }
        if (brutas.length == 1 || (brutas.length > 1 && !nome[1])) nome[0] = false;
        List<List<String>> trechos = new ArrayList<>();
        List<String> atual = new ArrayList<>(), ligacoes = new ArrayList<>();
        for (int i = 0; i < brutas.length; i++) {
            String bruta = brutas[i], w = tirarPontas(bruta, NOME_PONTAS);
            if (nome[i]) {
                atual.addAll(ligacoes);
                atual.add(w);
                ligacoes.clear();
            } else if (!atual.isEmpty() && LIGACOES_NOME.contains(w)) {
                ligacoes.add(w);
            } else {
                if (!atual.isEmpty()) trechos.add(atual);
                atual = new ArrayList<>();
                ligacoes.clear();
            }
            // Pontuação depois da palavra fecha o nome.
            if (!atual.isEmpty() && NOME_PONTAS.indexOf(bruta.charAt(bruta.length() - 1)) >= 0) {
                trechos.add(atual);
                atual = new ArrayList<>();
                ligacoes.clear();
            }
        }
        if (!atual.isEmpty()) trechos.add(atual);
        List<String> maior = null;
        for (List<String> t : trechos) if (maior == null || t.size() > maior.size()) maior = t;
        if (maior == null) return null;
        String r = String.join(" ", maior);
        return palavrasDeConteudo(r).isEmpty() ? null : r;
    }

    /** Gatilho de resposta longa (LONG_TRIGGER do data_utils.py), que a opção "Respostas longas" do app acrescenta. */
    public static final String GATILHO_LONGO = "Resposta longa.";
    private static final Pattern GATILHOS = Pattern.compile(
            "\\b(?:explique melhor|explica melhor|resposta longa|responda com detalhes)\\b[.:!,]?",
            Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE | UNICODE);

    /** A pergunta sem o gatilho de resposta longa, para a busca e a memória (without_trigger). */
    public static String semGatilho(String pergunta) {
        String resto = tirarPontas(aparar(ESPACOS.matcher(GATILHOS.matcher(pergunta).replaceAll(" ")).replaceAll(" ")), " ,");
        return !palavrasDeConteudo(resto).isEmpty() || resto.length() > 3 ? resto : pergunta;
    }

    /** A mensagem pede uma resposta longa? (wants_long) */
    public static boolean querLonga(String pergunta) {
        return GATILHOS.matcher(pergunta).find();
    }

    private static final Set<String> SEGUE_PALAVRAS = conjunto(
            "isso isto disso disto nisso nisto esse essa esses essas desse dessa desses dessas nesse nessa nesses nessas "
            + "aquilo aquele aquela aqueles aquelas daquilo daquele daquela naquilo naquele naquela "
            + "ele ela eles elas dele dela deles delas nele nela neles nelas "
            + "mesmo mesma anterior disse falou falamos falando mencionou perguntei respondeu "
            + "continue continua continuar prossiga repita repete repetir novamente");
    private static final Set<String> SEGUE_INICIOS = conjunto("e mas entao tambem");
    private static final String[] SEGUE_FRASES = {"explique melhor", "explica melhor", "fale mais", "conte mais",
            "diga mais", "mais detalhes", "outro exemplo", "outra vez", "de novo", "nao entendi", "o que voce quis dizer",
            "resposta longa", "responda com detalhes"}; // o gatilho sozinho ("Resposta longa.") pede mais da anterior
    private static final Set<String> SOCIAIS = conjunto(
            "oi ola ei opa obrigado obrigada valeu tchau ate logo bom boa dia tarde noite tudo bem beleza ok certo legal "
            + "show otimo sim nao kkk kkkk haha blz");

    /**
     * A mensagem depende da conversa anterior? (follows_up do data_utils.py). A memória de IA só põe o
     * histórico no prompt nesses casos ("E da Itália?", "Por quê?", "Quem foi ele?").
     */
    public static boolean segueConversa(String pergunta) {
        List<String> ws = new ArrayList<>();
        for (String w : separar(normalizar(pergunta))) {
            String limpa = tirarPontas(w, NOME_PONTAS);
            if (!limpa.isEmpty()) ws.add(limpa);
        }
        if (ws.isEmpty()) return false;
        if (SEGUE_INICIOS.contains(ws.get(0)) && !(ws.size() > 1 && ws.get(1).equals("ai"))) return true;
        for (String w : ws) if (SEGUE_PALAVRAS.contains(w)) return true;
        String junto = " " + String.join(" ", ws) + " ";
        for (String f : SEGUE_FRASES) if (junto.contains(" " + f + " ")) return true;
        if (ws.size() > 2 || !palavrasDeConteudo(pergunta).isEmpty()) return false;
        for (String w : ws) if (!SOCIAIS.contains(w)) return true;
        return false;
    }

    /** O que procurar no RAG, em ordem (rag_queries): o assunto do pedido; senão a pergunta e o nome próprio. */
    public static List<String> consultasRag(String pergunta) {
        List<String> r = new ArrayList<>();
        String assunto = assuntoDoPedido(pergunta);
        if (assunto != null) {
            r.add(assunto);
            return r;
        }
        r.add(pergunta);
        String nome = nomeDaPergunta(pergunta);
        if (nome != null && !palavrasDeConteudo(nome).equals(palavrasDeConteudo(pergunta))) r.add(nome);
        return r;
    }

    /** Quantos trechos do RAG cabem no prompt (rag_chunks): 1 com janela de 256, 2 com 512, 3 com 768+. */
    public static int trechosRag(int bloco) {
        return Math.min(3, Math.max(1, bloco / 256));
    }

    /** Uma troca no formato do chat (chat_turn). */
    public static String turno(String pergunta, String resposta) {
        return USER + " " + pergunta + " " + ASSISTANT + " " + resposta + " " + END;
    }

    /** Decide se vale procurar contexto nos textos (mesma regra do wants_rag). */
    public static boolean querRag(String pergunta) {
        String[] todas = separar(pergunta);
        if (pergunta.contains("Contexto:") || todas.length > 40) return false;
        String assunto = assuntoDoPedido(pergunta);
        if (assunto != null) {
            for (String w : palavras(assunto)) if (PERSONAL.contains(w)) return false;
            return true;
        }
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
        return ajustarContexto(contarTokens, pergunta, contexto, orcamento, MAX_CONTEXT_WORDS);
    }

    /** Igual, com outro limite de palavras (MAX_CONTEXT_WORDS por trecho, quando há vários). */
    public static String ajustarContexto(ToIntFunction<String> contarTokens, String pergunta, String contexto,
                                         int orcamento, int maxPalavras) {
        String[] palavras = separar(contexto);
        int n = Math.min(palavras.length, maxPalavras);
        while (n >= 12) {
            String trecho = String.join(" ", Arrays.asList(palavras).subList(0, n)) + (n < palavras.length ? "..." : "");
            String texto = perguntaComContexto(pergunta, trecho);
            if (contarTokens.applyAsInt(texto) <= orcamento) return texto;
            n -= 10;
        }
        return null;
    }
}
