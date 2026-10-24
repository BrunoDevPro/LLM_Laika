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

    private final SQLiteConnection con;

    public IndiceRag(SQLiteConnection con) {
        this.con = con;
    }

    /** Um trecho achado na busca. */
    public static final class Trecho {
        public final String titulo, texto, tipo;
        public final double cobertura, nota;

        Trecho(String titulo, String texto, String tipo, double cobertura, double nota) {
            this.titulo = titulo;
            this.texto = texto;
            this.tipo = tipo;
            this.cobertura = cobertura;
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

    static String radical(String w) {
        return w.length() >= 6 && soLetras(w) ? w.substring(0, 5) : w;
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
        return buscar(pergunta, 40);
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
        // 2) Qualquer trecho com as palavras: exata OU mesmo começo.
        List<String> termos = new ArrayList<>();
        for (String w : palavras) {
            termos.add("\"" + w + "\"");
            if (w.length() >= 6 && soLetras(w)) termos.add("\"" + w.substring(0, 5) + "\"*");
        }
        linhas.addAll(consulta(String.join(" OR ", termos), k));

        Set<String> radicaisPergunta = radicais(palavras);
        Set<String> letrasPergunta = letras(pergunta);
        Set<String> vistos = new HashSet<>();
        for (int rank = 0; rank < linhas.size(); rank++) {
            Linha l = linhas.get(rank);
            if (!vistos.add(l.titulo + "\u0000" + l.texto)) continue;
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
            } else if (emTitulo > 0 && !palavrasPrincipais.isEmpty()) {
                Set<String> extra = new HashSet<>(palavrasPrincipais);
                extra.removeAll(radicaisPergunta);
                nota -= 0.3 * extra.size() / palavrasPrincipais.size();
            }
            if (l.titulo.contains("(")) {
                Set<String> desamb = radicais(Texto.palavras(l.titulo));
                desamb.removeAll(radicais(Texto.palavras(tituloPrincipal)));
                if (!radicaisPergunta.containsAll(desamb)) nota -= 0.2;  // "Cristo Redentor (Porto Alegre)"
            }
            if (l.pos == 0 && emTitulo > 0) nota += 0.1;  // 1º trecho do artigo costuma ter a definição
            nota += 0.2 * proximidade(tokensTexto, palavras);
            nota -= 0.002 * rank;
            resultados.add(new Trecho(l.titulo, l.texto, l.tipo, cobertura, nota));
        }
        // Ordenação estável, como o sort do Python.
        Collections.sort(resultados, (a, b) -> Double.compare(b.nota, a.nota));
        return resultados;
    }

    /** O trecho mais relevante, ou null se a busca não tiver confiança (igual ao RagIndex.best). */
    public Trecho melhor(String pergunta) {
        return confiavel(buscar(pergunta));
    }

    /** O primeiro resultado, se a busca tiver confiança (_confident do rag.py); senão null. */
    static Trecho confiavel(List<Trecho> r) {
        return confiavel(r, true);
    }

    /** qualquerTexto=false: os textos de data/modern também precisam da nota mínima (busca só pelo nome). */
    static Trecho confiavel(List<Trecho> r, boolean qualquerTexto) {
        if (r.isEmpty() || r.get(0).cobertura < 0.6) return null;
        Trecho top = r.get(0);
        return top.nota >= 1.8 || (qualquerTexto && "texto".equals(top.tipo)) ? top : null;
    }

    /**
     * Até k trechos confiáveis para a pergunta (RagIndex.contexts): tenta cada consulta de
     * Texto.consultasRag; os extras são do mesmo artigo, na ordem de quantas palavras da pergunta têm.
     */
    public List<Trecho> contextos(String pergunta, int k) {
        List<String> consultas = Texto.consultasRag(pergunta);
        for (int c = 0; c < consultas.size(); c++) {
            List<Trecho> r = buscar(consultas.get(c));
            Trecho top = confiavel(r, c == 0);
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
