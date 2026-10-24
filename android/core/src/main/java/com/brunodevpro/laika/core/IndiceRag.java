package com.brunodevpro.laika.core;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.SQLiteStatement;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Busca no laika_rag.db (SQLite FTS5), com a mesma pontuação do RagIndex do rag.py.
 * Recebe a conexão já aberta: no Android, o BundledSQLiteDriver traz um SQLite com FTS5
 * (o SQLite do sistema nem sempre tem).
 */
public final class IndiceRag implements AutoCloseable {
    private static final Map<String, Double> KIND_BONUS = new HashMap<>();

    static {
        KIND_BONUS.put("texto", 0.2);
        KIND_BONUS.put("wiki", 0.15);
        KIND_BONUS.put("livro", 0.0);
    }
    private static final Pattern PARENTESES = Pattern.compile("\\s*\\(.*?\\)");
    private static final Pattern LETRAS = Pattern.compile("[\\p{L}]+");
    /** Números curtos e algarismos romanos da pergunta, que desempatam títulos ("Sputnik 2", "Pedro II"). */
    private static final Pattern NUMEROS_CURTOS = Pattern.compile(
            "(?<![\\d.,])\\d{1,2}(?![\\d.,])|\\b[IVXLC]{1,5}\\b", Texto.UNICODE);
    private static final Pattern NUMEROS_TITULO = Pattern.compile("\\d+|\\b[IVXLC]{1,5}\\b", Texto.UNICODE);

    private final SQLiteConnection con;

    public IndiceRag(SQLiteConnection con) {
        this.con = con;
    }

    /** Um trecho achado na busca. */
    public static final class Trecho {
        public final String titulo, texto, tipo;
        public final double cobertura, emTitulo, nota;

        Trecho(String titulo, String texto, String tipo, double cobertura, double emTitulo, double nota) {
            this.titulo = titulo;
            this.texto = texto;
            this.tipo = tipo;
            this.cobertura = cobertura;
            this.emTitulo = emTitulo;
            this.nota = nota;
        }
    }

    private static final class Linha {
        final String titulo, texto, tipo;
        final long pos;

        Linha(String titulo, String texto, String tipo, long pos) {
            this.titulo = titulo;
            this.texto = texto;
            this.tipo = tipo;
            this.pos = pos;
        }
    }

    /** Número de trechos no índice (para mostrar no app). */
    public long contarTrechos() {
        try (SQLiteStatement st = con.prepare("SELECT count(*) FROM passages")) {
            return st.step() ? st.getLong(0) : 0;
        }
    }

    private List<Linha> consulta(String match, int k) {
        List<Linha> r = new ArrayList<>();
        try (SQLiteStatement st = con.prepare("SELECT title, text, kind, pos FROM passages WHERE passages MATCH ? "
                + "ORDER BY bm25(passages, 4.0, 1.0) LIMIT ?")) {
            st.bindText(1, match);
            st.bindLong(2, k);
            while (st.step()) {
                r.add(new Linha(st.getText(0), st.getText(1), st.getText(2), st.isNull(3) ? 0 : st.getLong(3)));
            }
        } catch (RuntimeException e) {
            return new ArrayList<>();  // consulta inválida para o FTS5: sem resultados
        }
        return r;
    }

    private static final String[][] PLURAIS = {{"oes", "ao"}, {"aes", "ao"}, {"ais", "al"}, {"eis", "el"}, {"ns", "m"},
            {"res", "r"}, {"zes", "z"}, {"ses", "s"}, {"s", ""}};
    private static final String[] VERBOS = {"ando", "endo", "indo", "aram", "eram", "iram", "ava", "ou", "ar", "er", "ir", "or"};

    /**
     * Radical leve (_stem do rag.py): tira o plural e algumas terminações de verbo (palavras com 7+ letras).
     * "cadelas" = "cadela", "inventou" = "inventor"; "capital" não é mais "capítulo".
     */
    static String radical(String palavra) {
        if (!soLetras(palavra) || palavra.length() < 4) return palavra;
        String w = palavra;
        for (String[] p : PLURAIS) {
            if (w.endsWith(p[0]) && w.length() - p[0].length() + p[1].length() >= 3
                    && (!p[0].equals("eis") || w.length() >= 6)) {
                w = w.substring(0, w.length() - p[0].length()) + p[1];
                break;
            }
        }
        if (w.length() >= 7) {
            for (String fim : VERBOS) {
                if (w.endsWith(fim)) {
                    w = w.substring(0, w.length() - fim.length());
                    break;
                }
            }
        }
        return w;
    }

    private static boolean soLetras(String w) {
        for (int i = 0; i < w.length(); i++) if (!Character.isLetter(w.charAt(i))) return false;
        return !w.isEmpty();
    }

    private static Set<String> radicais(Iterable<String> palavras) {
        Set<String> r = new HashSet<>();
        for (String w : palavras) r.add(radical(w));
        return r;
    }

    private static Set<String> letras(String s) {
        Set<String> r = new HashSet<>();
        Matcher m = LETRAS.matcher(s.toLowerCase(Locale.ROOT));
        while (m.find()) r.add(m.group());
        return r;
    }

    /** 1.0 se as palavras da pergunta aparecem juntas (janela de até 12 palavras), 0 se espalhadas. */
    static double proximidade(List<String> tokens, List<String> palavras) {
        List<String> stems = new ArrayList<>();
        for (String t : tokens) stems.add(radical(t));
        List<List<Integer>> posicoes = new ArrayList<>();
        for (String w : palavras) {
            String alvo = radical(w);
            List<Integer> p = new ArrayList<>();
            for (int i = 0; i < stems.size(); i++) if (stems.get(i).equals(alvo)) p.add(i);
            if (!p.isEmpty()) posicoes.add(p);
        }
        if (posicoes.size() < 2) return 0.0;
        int melhor = Integer.MAX_VALUE;
        for (int i : posicoes.get(0)) {
            int pior = 0;
            for (List<Integer> p : posicoes) {
                int maisPerto = Integer.MAX_VALUE;
                for (int j : p) maisPerto = Math.min(maisPerto, Math.abs(j - i));
                pior = Math.max(pior, maisPerto);
            }
            melhor = Math.min(melhor, pior);
        }
        return melhor <= 6 ? 1.0 : melhor <= 12 ? 0.5 : 0.0;
    }

    public List<Trecho> buscar(String pergunta) {
        return buscar(pergunta, 200);
    }

    public List<Trecho> buscar(String pergunta, int k) {
        List<String> palavras = Texto.palavrasDeConteudo(pergunta);
        if (palavras.size() > 12) palavras = palavras.subList(0, 12);
        List<Trecho> resultados = new ArrayList<>();
        if (palavras.isEmpty()) return resultados;

        // 1) Artigos cujo TÍTULO tem todas as palavras da pergunta.
        List<String> partes = new ArrayList<>();
        for (String w : palavras) partes.add("title:\"" + w + "\"");
        List<Linha> linhas = new ArrayList<>(consulta(String.join(" AND ", partes), 15));
        // 1b) ... ou todas as palavras do nome próprio ("Laika" em "a cadela Laika").
        String nome = Texto.nomeDaPergunta(pergunta);
        List<String> doNome = Texto.palavrasDeConteudo(nome == null ? "" : nome);
        if (!doNome.isEmpty() && !doNome.equals(palavras)) {
            List<String> p2 = new ArrayList<>();
            for (String w : doNome) p2.add("title:\"" + w + "\"");
            linhas.addAll(consulta(String.join(" AND ", p2), 15));
        }
        // 2) Qualquer trecho com as palavras: exata OU com o mesmo radical.
        List<String> termos = new ArrayList<>();
        for (String w : palavras) {
            termos.add("\"" + w + "\"");
            String r = radical(w);
            if (r.length() >= 4 && !r.equals(w)) termos.add("\"" + r + "\"*");
        }
        linhas.addAll(consulta(String.join(" OR ", termos), k));

        Set<String> radicaisPergunta = radicais(palavras);
        Set<String> letrasPergunta = letras(pergunta);
        Set<String> numerosPergunta = achados(NUMEROS_CURTOS, pergunta);
        Set<String> vistos = new HashSet<>();
        for (int rank = 0; rank < linhas.size(); rank++) {
            Linha l = linhas.get(rank);
            if (!vistos.add(l.titulo + "\u0000" + l.texto)) continue;
            // O texto em que a IA se apresenta só confundiria as perguntas sobre a cadela.
            if ("texto".equals(l.tipo) && Texto.normalizar(l.titulo).equals("laika")) continue;
            String tituloPrincipal = PARENTESES.matcher(l.titulo).replaceAll("");
            Set<String> palavrasTitulo = radicais(Texto.palavras(l.titulo));
            List<String> conteudoPrincipal = Texto.palavrasDeConteudo(tituloPrincipal);
            List<String> principais = new ArrayList<>();
            for (String w : Texto.palavras(tituloPrincipal)) if (conteudoPrincipal.contains(w)) principais.add(w);
            Set<String> palavrasPrincipais = radicais(principais);
            List<String> tokensTexto = Texto.palavras(l.texto);
            Set<String> todas = new HashSet<>(palavrasTitulo);
            todas.addAll(radicais(tokensTexto));
            int naCobertura = 0, noTitulo = 0;
            for (String w : palavras) {
                if (todas.contains(radical(w))) naCobertura++;
                if (palavrasTitulo.contains(radical(w))) noTitulo++;
            }
            double cobertura = (double) naCobertura / palavras.size();
            double emTitulo = (double) noTitulo / palavras.size();

            double nota = cobertura + 0.3 * emTitulo + KIND_BONUS.getOrDefault(l.tipo, 0.0);
            Set<String> desamb = radicais(Texto.palavras(l.titulo));
            desamb.removeAll(radicais(Texto.palavras(tituloPrincipal)));
            // Mesmas letras mas acentos diferentes ("Pele" x "Pelé") não contam como título igual.
            boolean choqueAcento = false;
            for (String a : letras(tituloPrincipal)) {
                for (String b : letrasPergunta) {
                    if (!a.equals(b) && Texto.normalizar(a).equals(Texto.normalizar(b))) choqueAcento = true;
                }
            }
            if (choqueAcento) {
                nota -= 0.5;
            } else if (!palavrasPrincipais.isEmpty() && palavrasPrincipais.equals(radicaisPergunta)) {
                nota += 0.6;  // título exatamente igual ao assunto
            } else if (!palavrasPrincipais.isEmpty() && radicaisPergunta.containsAll(palavrasPrincipais)
                    && radicaisPergunta.size() > palavrasPrincipais.size()) {
                // Título contido na pergunta ("Laika" em "a cadela Laika"): vale mais quanto mais da pergunta
                // ele cobre, e mais ainda se o resto está no trecho.
                nota += 0.5 * palavrasPrincipais.size() / radicaisPergunta.size();
                Set<String> resto = new HashSet<>(radicaisPergunta);
                resto.removeAll(palavrasPrincipais);
                resto.removeAll(desamb);
                if (radicais(tokensTexto).containsAll(resto)) nota += 0.15;
            } else if (emTitulo > 0 && !palavrasPrincipais.isEmpty()) {
                Set<String> extra = new HashSet<>(palavrasPrincipais);
                extra.removeAll(radicaisPergunta);
                nota -= 0.3 * extra.size() / palavrasPrincipais.size();
            }
            if (l.titulo.contains("(")) {
                if (!desamb.isEmpty() && radicaisPergunta.containsAll(desamb)) {
                    nota += 0.3;  // "Marte (planeta)" em "o planeta Marte tem água?"
                } else if (!radicaisPergunta.containsAll(desamb)) {
                    nota -= 0.2;  // "Cristo Redentor (Porto Alegre)"
                }
            }
            if (l.pos == 0 && emTitulo > 0) nota += 0.1;  // 1º trecho do artigo costuma ter a definição
            Set<String> numerosTitulo = achados(NUMEROS_TITULO, l.titulo);
            numerosTitulo.retainAll(numerosPergunta);
            if (!numerosTitulo.isEmpty()) nota += 0.1;
            nota += 0.2 * proximidade(tokensTexto, palavras);
            nota -= 0.002 * rank;
            resultados.add(new Trecho(l.titulo, l.texto, l.tipo, cobertura, emTitulo, nota));
        }
        // Ordenação estável, como o sort do Python.
        Collections.sort(resultados, (a, b) -> Double.compare(b.nota, a.nota));
        return resultados;
    }

    private static Set<String> achados(Pattern p, String s) {
        Set<String> r = new HashSet<>();
        Matcher m = p.matcher(s);
        while (m.find()) r.add(m.group());
        return r;
    }

    /** O trecho mais relevante, ou null se a busca não tiver confiança (igual ao RagIndex.best). */
    public Trecho melhor(String pergunta) {
        return confiavel(buscar(pergunta));
    }

    /** O primeiro resultado, se a busca tiver confiança (_confident do rag.py); senão null. */
    static Trecho confiavel(List<Trecho> r) {
        return confiavel(r, true);
    }

    /**
     * qualquerTexto=true (primeira busca): textos de data/modern com alguma palavra da pergunta no título passam
     * sem a nota mínima; false (busca só pelo nome): também precisam dela.
     */
    static Trecho confiavel(List<Trecho> r, boolean qualquerTexto) {
        if (r.isEmpty() || r.get(0).cobertura < 0.6) return null;
        Trecho top = r.get(0);
        return top.nota >= 1.8 || (qualquerTexto && "texto".equals(top.tipo) && top.emTitulo > 0) ? top : null;
    }

    /**
     * Até k trechos confiáveis para a pergunta (RagIndex.contexts): tenta cada consulta de
     * Texto.consultasRag; os extras são do mesmo artigo, na ordem de quantas palavras da pergunta têm.
     */
    public List<Trecho> contextos(String pergunta, int k) {
        List<String> consultas = Texto.consultasRag(pergunta);
        List<Trecho> primeira = new ArrayList<>();
        for (int c = 0; c < consultas.size(); c++) {
            List<Trecho> r = buscar(consultas.get(c));
            Trecho top = confiavel(r, c == 0);
            if (c == 0) {
                primeira = r;
            } else if (!primeira.isEmpty() && primeira.get(0).cobertura >= 0.6 && "wiki".equals(primeira.get(0).tipo)
                    && radicais(Texto.palavras(primeira.get(0).titulo)).containsAll(
                            radicais(Texto.palavrasDeConteudo(consultas.get(c))))) {
                // Na busca só pelo nome, o 1º resultado da pergunta inteira ganha se o título dele tem o nome
                // ("o tamanho do rio Amazonas" fica com "Rio Amazonas", e não com o estado "Amazonas").
                top = primeira.get(0);
                r = primeira;
            }
            if (top == null) continue;
            List<Trecho> achados = new ArrayList<>();
            achados.add(top);
            if (k > 1) {
                Set<String> queridas = radicais(Texto.palavrasDeConteudo(pergunta));
                List<Trecho> mesmos = new ArrayList<>();
                List<Integer> pontos = new ArrayList<>();
                for (Trecho t : r) {
                    if (!t.titulo.equals(top.titulo) || t.texto.equals(top.texto)) continue;
                    Set<String> tem = radicais(Texto.palavras(t.texto));
                    tem.retainAll(queridas);
                    mesmos.add(t);
                    pontos.add(tem.size());
                }
                // Ordenação estável pelo número de palavras (empate: ordem da busca), como o sort do Python.
                List<Integer> ordem = new ArrayList<>();
                for (int i = 0; i < mesmos.size(); i++) ordem.add(i);
                Collections.sort(ordem, (a, b) -> Integer.compare(pontos.get(b), pontos.get(a)));
                for (int i = 0; i < Math.min(k - 1, ordem.size()); i++) achados.add(mesmos.get(ordem.get(i)));
            }
            return achados;
        }
        return new ArrayList<>();
    }

    @Override
    public void close() {
        con.close();
    }
}
