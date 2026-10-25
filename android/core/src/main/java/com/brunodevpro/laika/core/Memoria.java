package com.brunodevpro.laika.core;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Memória do usuário fora do modelo, igual ao memory.py: guarda nome, cidade, idade, gostos,
 * favoritos e anotações ("lembre que...") num memoria.json (mesmo formato do PC) e responde
 * direto perguntas como "qual é o meu nome?".
 */
public final class Memoria {
    private static final int F = Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE | Texto.UNICODE;
    private static final String STOP = "(?=[.,;!?]|\\s+e\\s+(?:eu|meu|minha|moro|tenho|gosto)\\b|$)";
    private static final String VALUE = "([^.,;!?]+?)" + STOP;
    private static final String VALUE_CONT = VALUE.substring(1);  // _VALUE[1:] do Python

    private static final Pattern SAVE_NAME = Pattern.compile(
            "\\b(?:meu nome (?:é|e)|me chamo|eu me chamo|pode me chamar de)\\s+" + VALUE, F);
    private static final Pattern SAVE_CITY = Pattern.compile("\\b(?:eu )?moro ((?:em|no|na|nos|nas) " + VALUE_CONT, F);
    private static final Pattern SAVE_AGE = Pattern.compile("\\b(?:eu )?tenho (\\d{1,3}) anos\\b", F);
    private static final Pattern SAVE_LIKE = Pattern.compile(
            "\\b(?:eu )?(n[ãa]o )?gosto (?:muito )?((?:de|do|da|dos|das) " + VALUE_CONT, F);
    private static final Pattern SAVE_FAV = Pattern.compile(
            "\\b(?:o |a )?(meu|minha) ([a-zà-ÿ]+(?: [a-zà-ÿ]+)?) favorit[oa] (?:é|e) " + VALUE, F);
    private static final Pattern SAVE_NOTE = Pattern.compile(
            "^(?:por favor,? )?(?:lembre(?:-se)?|lembra|guarde|anote|memorize)(?: de)?(?: que)?[:,]?\\s+(.+)$", F);

    private static final Pattern ASK_NAME = Pattern.compile("\\b(qual (?:é |e )?(?:o )?meu nome|como (?:é que )?eu me chamo|"
            + "voc[eê] sabe (?:qual (?:é )?)?(?:o )?meu nome|quem sou eu|sabe quem eu sou)", F);
    /** "Faça uma frase com o meu nome", "Escreva um poema usando o seu nome": o nome vai no Contexto (NAME_REF_*). */
    private static final Pattern NOME_DO_USUARIO = Pattern.compile(
            "\\b(?:o\\s+)?meu\\s+(?:pr[oó]prio\\s+)?nome\\b(?!\\s+(?:é|e)\\b)", F);
    private static final Pattern NOME_DA_LAIKA = Pattern.compile(
            "\\b(?:o\\s+)?(?:seu|teu)\\s+(?:pr[oó]prio\\s+)?nome\\b(?!\\s+(?:é|e)\\b)", F);
    /** Pedido que usa o nome ("frase", "poema", "letras"...): só aí o nome da Laika entra no Contexto (NAME_USE). */
    private static final Pattern USA_O_NOME = Pattern.compile("\\b(?:frases?|poemas?|poesia|versos?|rimas?|acr[oó]stico|"
            + "letras?|soletr\\w*|contr[aá]rio|mensagem|hist[oó]ria|texto|escrev\\w*|fa[cç]a|use|usando|usar|crie|invente|"
            + "forme|anagrama)\\b", F);
    private static final Pattern ASK_CITY = Pattern.compile("\\bonde (?:é que )?eu moro\\b", F);
    private static final Pattern ASK_AGE = Pattern.compile("\\b(quantos anos eu tenho|qual (?:é )?a minha idade)\\b", F);
    private static final Pattern ASK_LIKES = Pattern.compile("\\b(?:do que|o que) eu (?:n[ãa]o )?gosto\\b", F);
    private static final Pattern ASK_FAV = Pattern.compile(
            "\\bqual (?:é |e )?(?:a |o )?(?:minha|meu) ([a-zà-ÿ]+(?: [a-zà-ÿ]+)?) favorit[oa]", F);
    /** Mensagem enviada pela metade ("Meu nome é"): pergunta o resto (igual ao INCOMPLETE do memory.py). */
    private static final Pattern[] INCOMPLETA = {
            Pattern.compile("^(?:meu nome (?:é|e)|me chamo|eu me chamo|pode me chamar de)\\s*[.!]*$", F),
            Pattern.compile("^(?:eu )?moro(?: (?:em|no|na|nos|nas))?\\s*[.!]*$", F),
            Pattern.compile("^(?:eu )?(?:n[ãa]o )?gosto(?: muito)?(?: (?:de|do|da|dos|das))?\\s*[.!]*$", F),
            Pattern.compile("^(?:eu )?tenho\\s*[.!]*$", F),
            Pattern.compile("^(?:por favor,? )?(?:lembre(?:-se)?|lembra|guarde|anote|memorize)(?: de)?(?: que)?\\s*[.!:]*$", F),
    };
    private static final String[] RESPOSTA_INCOMPLETA = {
            "Acho que a mensagem ficou pela metade. Qual é o seu nome?",
            "Faltou o final da frase. Onde você mora?",
            "Faltou o final da frase. Do que você gosta?",
            "Faltou o final da frase. O que você tem?",
            "Claro! O que você quer que eu lembre?",
    };
    private static final Pattern ASK_ALL = Pattern.compile("\\bo que voc[eê] (?:sabe|lembra|guardou)(?: (?:sobre|de) mim)?\\b", F);
    private static final Pattern FORGET = Pattern.compile(
            "\\b(esque[cç]a|apague|limpe|apaga|esquece) (?:tudo|a (?:sua )?mem[oó]ria|o que eu (?:te )?disse)\\b", F);

    private final File arquivo;
    private String nome, cidade, idade;
    private final List<String> gostos = new ArrayList<>(), naoGosta = new ArrayList<>(), notas = new ArrayList<>();
    /** favoritos: chave -> {valor, fem} */
    private final Map<String, String[]> favoritos = new LinkedHashMap<>();

    public Memoria(File arquivo) {
        this.arquivo = arquivo;
        if (arquivo.exists()) {
            try {
                carregar(new String(Files.readAllBytes(arquivo.toPath()), StandardCharsets.UTF_8));
            } catch (IOException | RuntimeException ignorado) {
                // arquivo corrompido: começa vazia, como o memory.py
            }
        }
    }

    private void apagarTudo() {
        nome = cidade = idade = null;
        gostos.clear();
        naoGosta.clear();
        notas.clear();
        favoritos.clear();
    }

    @SuppressWarnings("unchecked")
    private void carregar(String json) {
        Object o = Json.ler(json);
        if (!(o instanceof Map)) return;
        Map<String, Object> d = (Map<String, Object>) o;
        nome = texto(d.get("nome"));
        cidade = texto(d.get("cidade"));
        idade = texto(d.get("idade"));
        lista(d.get("gostos"), gostos);
        lista(d.get("nao_gosta"), naoGosta);
        lista(d.get("notas"), notas);
        if (d.get("favoritos") instanceof Map) {
            for (Map.Entry<String, Object> e : ((Map<String, Object>) d.get("favoritos")).entrySet()) {
                if (e.getValue() instanceof Map) {
                    Map<String, Object> info = (Map<String, Object>) e.getValue();
                    favoritos.put(e.getKey(), new String[]{texto(info.get("valor")),
                            Boolean.TRUE.equals(info.get("fem")) ? "1" : ""});
                }
            }
        }
    }

    private static String texto(Object o) {
        if (o == null) return null;
        if (o instanceof Double && (Double) o == Math.rint((Double) o)) return String.valueOf(((Double) o).longValue());
        return String.valueOf(o);
    }

    private static void lista(Object o, List<String> destino) {
        if (o instanceof List) for (Object x : (List<?>) o) if (x != null) destino.add(String.valueOf(x));
    }

    public void salvar() {
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("nome", nome);
        d.put("cidade", cidade);
        d.put("idade", idade);
        d.put("gostos", gostos);
        d.put("nao_gosta", naoGosta);
        Map<String, Object> fav = new LinkedHashMap<>();
        for (Map.Entry<String, String[]> e : favoritos.entrySet()) {
            Map<String, Object> info = new LinkedHashMap<>();
            info.put("valor", e.getValue()[0]);
            info.put("fem", !e.getValue()[1].isEmpty());
            fav.put(e.getKey(), info);
        }
        d.put("favoritos", fav);
        d.put("notas", notas);
        try {
            File pasta = arquivo.getParentFile();
            if (pasta != null) pasta.mkdirs();
            Files.write(arquivo.toPath(), Json.escrever(d).getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignorado) {
            // sem espaço/permissão: a conversa continua, só não guarda
        }
    }

    private static String frase(String chave, String[] info) {
        return !info[1].isEmpty() ? "sua " + chave + " favorita é " + info[0] : "seu " + chave + " favorito é " + info[0];
    }

    private static String limpar(String v) {
        String s = Texto.aparar(v);
        int a = 0, b = s.length();
        while (a < b && (s.charAt(a) == '"' || s.charAt(a) == '\'')) a++;
        while (b > a && (s.charAt(b - 1) == '"' || s.charAt(b - 1) == '\'')) b--;
        return Texto.aparar(s.substring(a, b));
    }

    private String lembrar(String msg) {
        if (FORGET.matcher(msg).find()) {
            apagarTudo();
            salvar();
            return "Pronto, apaguei tudo o que eu tinha guardado sobre você.";
        }
        if (ASK_NAME.matcher(msg).find()) {
            return nome != null ? "Seu nome é " + nome + "." : "Você ainda não me disse o seu nome. Como você se chama?";
        }
        if (ASK_CITY.matcher(msg).find()) {
            return cidade != null ? "Você mora " + cidade + "." : "Você ainda não me disse onde mora.";
        }
        if (ASK_AGE.matcher(msg).find()) {
            return idade != null ? "Você tem " + idade + " anos." : "Você ainda não me disse a sua idade.";
        }
        if (ASK_LIKES.matcher(msg).find()) {
            String m = msg.toLowerCase(Locale.ROOT);
            if (m.contains("não") || m.contains("nao")) {
                return naoGosta.isEmpty() ? "Você ainda não me disse do que não gosta."
                        : "Você me disse que não gosta " + String.join(", ", naoGosta) + ".";
            }
            return gostos.isEmpty() ? "Você ainda não me disse do que gosta."
                    : "Você me disse que gosta " + String.join(", ", gostos) + ".";
        }
        Matcher fav = ASK_FAV.matcher(msg);
        if (fav.find()) {
            String chave = fav.group(1).toLowerCase(Locale.ROOT);
            return favoritos.containsKey(chave) ? "Você me disse que " + frase(chave, favoritos.get(chave)) + "."
                    : "Você ainda não me contou isso.";
        }
        if (ASK_ALL.matcher(msg).find()) return resumo();
        return null;
    }

    /** O que a Laika lembra sobre o usuário (comando /memoria). */
    public String resumo() {
        List<String> p = new ArrayList<>();
        if (nome != null) p.add("seu nome é " + nome);
        if (cidade != null) p.add("você mora " + cidade);
        if (idade != null) p.add("você tem " + idade + " anos");
        if (!gostos.isEmpty()) p.add("você gosta " + String.join(", ", gostos));
        if (!naoGosta.isEmpty()) p.add("você não gosta " + String.join(", ", naoGosta));
        for (Map.Entry<String, String[]> e : favoritos.entrySet()) p.add(frase(e.getKey(), e.getValue()));
        for (String n : notas) p.add("você me pediu para lembrar: " + n);
        if (p.isEmpty()) return "Ainda não sei nada sobre você. Você pode me contar, por exemplo: meu nome é Ana.";
        return "Eu lembro que " + String.join("; ", p) + ".";
    }

    /** Resumo curto para a lista de versões: "Bruno · 3 fatos · 2 anotações". */
    public String descricaoCurta() {
        List<String> p = new ArrayList<>();
        if (nome != null) p.add(nome);
        int fatos = (cidade != null ? 1 : 0) + (idade != null ? 1 : 0) + gostos.size() + naoGosta.size() + favoritos.size();
        if (fatos > 0) p.add(fatos + (fatos == 1 ? " fato" : " fatos"));
        if (!notas.isEmpty()) p.add(notas.size() + (notas.size() == 1 ? " anotação" : " anotações"));
        return p.isEmpty() ? "vazia" : String.join(" · ", p);
    }

    private static String capitalizar(String w) {
        if (w.isEmpty()) return w;
        int primeiro = w.codePointAt(0);
        int n = Character.charCount(primeiro);
        return new String(Character.toChars(Character.toTitleCase(primeiro))) + w.substring(n).toLowerCase(Locale.ROOT);
    }

    private List<String> aprender(String msg) {
        List<String> aprendido = new ArrayList<>();
        Matcher note = SAVE_NOTE.matcher(Texto.aparar(msg));
        if (note.find()) {
            String t = limpar(note.group(1));
            int b = t.length();
            while (b > 0 && (t.charAt(b - 1) == '.' || t.charAt(b - 1) == '!')) b--;
            t = t.substring(0, b);
            String tl = t.toLowerCase(Locale.ROOT);
            if (tl.equals("que") || tl.equals("de") || tl.equals("de que")) return aprendido;  // "Lembre que" sem o resto
            if (!t.isEmpty() && !notas.contains(t)) notas.add(t);
            aprendido.add("Certo, vou lembrar: " + t + ".");
            return aprendido;
        }
        boolean pergunta = msg.contains("?");
        Matcher m = SAVE_NAME.matcher(msg);
        if (m.find() && !pergunta) {
            String[] ws = Texto.separar(limpar(m.group(1)));
            List<String> partes = new ArrayList<>();
            for (int i = 0; i < Math.min(3, ws.length); i++) partes.add(capitalizar(ws[i]));
            String n = String.join(" ", partes);
            if (!n.isEmpty()) {
                nome = n;
                aprendido.add("Prazer, " + n + "! Vou lembrar o seu nome.");
            }
        }
        m = SAVE_CITY.matcher(msg);
        if (m.find() && !pergunta) {
            cidade = limpar(m.group(1));
            aprendido.add("Anotado: você mora " + cidade + ".");
        }
        m = SAVE_AGE.matcher(msg);
        if (m.find() && !pergunta) {
            idade = m.group(1);
            aprendido.add("Anotado: você tem " + idade + " anos.");
        }
        m = SAVE_LIKE.matcher(msg);
        if (m.find() && !pergunta) {
            boolean negativo = m.group(1) != null;
            String coisa = limpar(m.group(2));
            List<String> alvo = negativo ? naoGosta : gostos;
            if (!alvo.contains(coisa)) alvo.add(coisa);
            aprendido.add("Anotado: você " + (negativo ? "não " : "") + "gosta " + coisa + ".");
        }
        m = SAVE_FAV.matcher(msg);
        if (m.find() && !pergunta) {
            String[] info = {limpar(m.group(3)), m.group(1).toLowerCase(Locale.ROOT).equals("minha") ? "1" : ""};
            String chave = m.group(2).toLowerCase(Locale.ROOT);
            favoritos.put(chave, info);
            aprendido.add("Anotado: " + frase(chave, info) + ".");
        }
        return aprendido;
    }

    /** Resposta direta da memória, ou null para o modelo responder normalmente. */
    public String tratar(String msg) {
        String r = lembrar(msg);
        if (r != null) return r;
        List<String> aprendido = aprender(msg);
        if (!aprendido.isEmpty()) {
            salvar();
            return String.join(" ", aprendido);
        }
        String aparado = Texto.aparar(msg);
        for (int i = 0; i < INCOMPLETA.length; i++) {
            if (INCOMPLETA[i].matcher(aparado).matches()) return RESPOSTA_INCOMPLETA[i];
        }
        // "Faça uma frase com o meu nome" sem saber o nome: pergunta, em vez de o modelo inventar um.
        if (nome == null && NOME_DO_USUARIO.matcher(msg).find()) {
            return "Você ainda não me disse o seu nome. Como você se chama?";
        }
        return null;
    }

    /**
     * Anotações relacionadas à pergunta, para entrar no Contexto do modelo; e o nome do usuário ou o da Laika
     * quando a mensagem fala em "meu nome" ou "seu nome" (context_for do memory.py).
     */
    public String contextoPara(String pergunta) {
        List<String> partes = new ArrayList<>();
        // O nome do usuário ou o da Laika, quando a mensagem fala em "meu nome" ou "seu nome".
        if (nome != null && NOME_DO_USUARIO.matcher(pergunta).find()) partes.add("O nome do usuário é " + nome + ".");
        if (NOME_DA_LAIKA.matcher(pergunta).find() && USA_O_NOME.matcher(pergunta).find()) partes.add("O nome da assistente é Laika.");
        int antes = partes.size();
        Set<String> palavras = new HashSet<>(Texto.palavrasDeConteudo(pergunta));
        for (String n : notas) {
            if (palavras.isEmpty() || partes.size() - antes >= 2) break;
            for (String w : Texto.palavrasDeConteudo(n)) {
                if (palavras.contains(w)) {
                    partes.add("O usuário pediu para lembrar: " + n + ".");
                    break;
                }
            }
        }
        return String.join(" ", partes);
    }
}
