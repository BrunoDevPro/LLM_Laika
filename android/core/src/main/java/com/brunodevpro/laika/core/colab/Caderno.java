package com.brunodevpro.laika.core.colab;

import com.brunodevpro.laika.core.Json;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * As células do colab.ipynb, lidas como o colab/laika_colab.py lê: células de código que começam
 * com "# N) TÍTULO", com os parâmetros dos formulários do Colab (linhas com #@param).
 * A tela Colab do app mostra cada célula com os seus campos.
 */
public final class Caderno {
    public static final String MARCA_NAVEGADOR = "[só no navegador]";
    private static final Pattern TITULO = Pattern.compile("^#\\s*(\\d+)\\)\\s*(.+?)\\s*$");
    private static final Pattern PARAM = Pattern.compile("^([A-Za-z_]\\w*)\\s*=\\s*(.+?)\\s*#\\s*@param\\s*(.*?)\\s*$");
    private static final Pattern TIPO = Pattern.compile("type\\s*:\\s*\"(\\w+)\"");

    public static final class Parametro {
        /** "string", "integer", "number", "boolean" ou "opcoes". */
        public final String nome, tipo;
        /** String, Long, Double ou Boolean. */
        public final Object padrao;
        public final List<String> opcoes;

        Parametro(String nome, String tipo, Object padrao, List<String> opcoes) {
            this.nome = nome;
            this.tipo = tipo;
            this.padrao = padrao;
            this.opcoes = opcoes;
        }
    }

    public static final class Celula {
        public final int numero;
        /** nome: "PRÉ-TREINO"; titulo: a linha inteira; descricao: os comentários logo abaixo. */
        public final String nome, titulo, descricao;
        public final boolean soNavegador;
        public final List<Parametro> parametros;

        Celula(int numero, String titulo, String descricao, boolean soNavegador, List<Parametro> parametros) {
            this.numero = numero;
            this.titulo = titulo;
            this.nome = titulo.split("[:(.\\[—]", 2)[0].trim();
            this.descricao = descricao;
            this.soNavegador = soNavegador;
            this.parametros = parametros;
        }

        public Parametro parametro(String nome) {
            for (Parametro p : parametros) if (p.nome.equals(nome)) return p;
            return null;
        }
    }

    private Caderno() {
    }

    /** Lê o .ipynb (JSON). */
    @SuppressWarnings("unchecked")
    public static List<Celula> ler(String ipynb) {
        Map<String, Object> nb = (Map<String, Object>) Json.ler(ipynb);
        List<Celula> r = new ArrayList<>();
        for (Object o : (List<Object>) nb.get("cells")) {
            Map<String, Object> c = (Map<String, Object>) o;
            if (!"code".equals(c.get("cell_type"))) continue;
            Object fonte = c.get("source");
            String codigo;
            if (fonte instanceof List) {
                StringBuilder sb = new StringBuilder();
                for (Object l : (List<Object>) fonte) sb.append(l);
                codigo = sb.toString();
            } else {
                codigo = String.valueOf(fonte);
            }
            Celula cel = celula(codigo);
            if (cel != null) r.add(cel);
        }
        return r;
    }

    static Celula celula(String codigo) {
        String[] linhas = codigo.split("\n", -1);
        Matcher m = TITULO.matcher(linhas[0]);
        if (!m.matches()) return null;
        String titulo = m.group(2);
        boolean soNavegador = titulo.contains(MARCA_NAVEGADOR);
        titulo = titulo.replace(MARCA_NAVEGADOR, "").replaceAll("\\s+", " ").trim();
        List<String> descricao = new ArrayList<>();
        for (int i = 1; i < linhas.length && linhas[i].startsWith("#"); i++) {
            descricao.add(linhas[i].replaceFirst("^#\\s?", "").replaceAll("\\s+$", ""));
        }
        List<Parametro> params = new ArrayList<>();
        for (String l : linhas) {
            Matcher p = PARAM.matcher(l);
            if (p.matches()) params.add(parametro(p.group(1), p.group(2), p.group(3)));
        }
        return new Celula(Integer.parseInt(m.group(1)), titulo, String.join("\n", descricao), soNavegador,
                Collections.unmodifiableList(params));
    }

    @SuppressWarnings("unchecked")
    static Parametro parametro(String nome, String valor, String spec) {
        Object padrao = literal(valor);
        if (spec.startsWith("[")) {
            List<String> opcoes = new ArrayList<>();
            for (Object o : (List<Object>) Json.ler(spec.replace('\'', '"'))) opcoes.add(String.valueOf(o));
            return new Parametro(nome, "opcoes", padrao, Collections.unmodifiableList(opcoes));
        }
        Matcher t = TIPO.matcher(spec);
        String tipo = t.find() ? t.group(1)
                : padrao instanceof Boolean ? "boolean" : padrao instanceof Long ? "integer"
                : padrao instanceof Double ? "number" : "string";
        if (tipo.equals("slider")) tipo = "number";
        if (!tipo.equals("integer") && !tipo.equals("number") && !tipo.equals("boolean")) tipo = "string";
        return new Parametro(nome, tipo, padrao, Collections.emptyList());
    }

    /** O valor de um literal do Python: "texto", 'texto', 12, 0.5, True, False. */
    static Object literal(String s) {
        s = s.trim();
        if (s.equals("True")) return Boolean.TRUE;
        if (s.equals("False")) return Boolean.FALSE;
        if (s.length() >= 2 && (s.charAt(0) == '"' || s.charAt(0) == '\'') && s.charAt(s.length() - 1) == s.charAt(0)) {
            StringBuilder sb = new StringBuilder();
            for (int i = 1; i < s.length() - 1; i++) {
                char c = s.charAt(i);
                if (c == '\\' && i + 1 < s.length() - 1) {
                    char n = s.charAt(++i);
                    sb.append(n == 'n' ? '\n' : n == 't' ? '\t' : n);
                } else {
                    sb.append(c);
                }
            }
            return sb.toString();
        }
        try {
            return Long.parseLong(s.replace("_", ""));
        } catch (NumberFormatException e) {
            try {
                return Double.parseDouble(s.replace("_", ""));
            } catch (NumberFormatException e2) {
                return s;
            }
        }
    }

    /**
     * O valor digitado na tela, já no tipo certo para o JSON dos parâmetros do workflow.
     * Lança IllegalArgumentException com uma mensagem para o usuário se não servir.
     */
    public static Object converter(Parametro p, String texto) {
        String t = texto == null ? "" : texto.trim();
        switch (p.tipo) {
            case "boolean":
                String b = t.toLowerCase(Locale.ROOT);
                if (b.equals("true") || b.equals("sim")) return Boolean.TRUE;
                if (b.equals("false") || b.equals("não") || b.equals("nao")) return Boolean.FALSE;
                throw new IllegalArgumentException(p.nome + " precisa ser sim ou não");
            case "integer":
                try {
                    return Long.parseLong(t);
                } catch (NumberFormatException e) {
                    throw new IllegalArgumentException(p.nome + " precisa ser um número inteiro");
                }
            case "number":
                try {
                    return Double.parseDouble(t.replace(',', '.'));
                } catch (NumberFormatException e) {
                    throw new IllegalArgumentException(p.nome + " precisa ser um número");
                }
            case "opcoes":
                if (p.opcoes.contains(t)) return t;
                throw new IllegalArgumentException(p.nome + " precisa ser um de " + p.opcoes);
            default:
                if (t.contains("\n")) throw new IllegalArgumentException(p.nome + " não pode ter mais de uma linha");
                return t;
        }
    }

    /** O padrão como texto para a tela (True -> "true"). */
    public static String textoDoPadrao(Parametro p) {
        if (p.padrao instanceof Boolean) return ((Boolean) p.padrao) ? "true" : "false";
        if (p.padrao instanceof Double) {
            double d = (Double) p.padrao;
            return d == Math.rint(d) ? String.valueOf((long) d) : String.valueOf(d);
        }
        return String.valueOf(p.padrao);
    }
}
