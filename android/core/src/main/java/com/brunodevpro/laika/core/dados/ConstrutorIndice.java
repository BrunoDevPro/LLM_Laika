package com.brunodevpro.laika.core.dados;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.SQLiteStatement;

import com.brunodevpro.laika.core.Texto;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * O "python rag.py build" no celular: divide wiki/, modern/ e books/ em trechos de ~80
 * palavras (sem cortar frases) e monta a tabela FTS5 "passages" igual à do rag.py.
 */
public final class ConstrutorIndice {
    /** Fim de frase, como o _SENTENCE_SPLIT do data_utils.py (usado pelo rag.py). */
    static final Pattern FRASES = Pattern.compile("(?<=[.!?…])\\s+", Texto.UNICODE);

    private ConstrutorIndice() {
    }

    public interface Trechos {
        void trecho(String titulo, String texto, String tipo, int pos);
    }

    static List<String> pedacos(String texto) {
        List<String> r = new ArrayList<>();
        List<String> atual = new ArrayList<>();
        int conta = 0;
        for (String frase : FRASES.split(texto, -1)) {
            int n = Texto.separar(frase).length;
            if (!atual.isEmpty() && conta + n > 80) {
                r.add(String.join(" ", atual));
                atual.clear();
                conta = 0;
            }
            atual.add(frase);
            conta += n;
        }
        if (!atual.isEmpty()) r.add(String.join(" ", atual));
        return r;
    }

    private static boolean fimDeFrase(String b) {
        char c = b.charAt(b.length() - 1);
        return c == '.' || c == '!' || c == '?' || c == '…';
    }

    static void wiki(String texto, Trechos t) {
        String titulo = "";
        int pos = 0;
        for (String bloco : texto.split("\n\n", -1)) {
            bloco = Texto.aparar(bloco);
            if (bloco.isEmpty()) continue;
            if (!fimDeFrase(bloco) && bloco.codePointCount(0, bloco.length()) < 120) {
                titulo = bloco;
                pos = 0;
                continue;
            }
            for (String p : pedacos(bloco)) {
                if (Texto.separar(p).length >= 8) t.trecho(titulo, p, "wiki", pos++);
            }
        }
    }

    static void moderno(String texto, Trechos t) {
        List<String> blocos = new ArrayList<>();
        for (String b : texto.split("\n\n", -1)) if (!Texto.aparar(b).isEmpty()) blocos.add(Texto.aparar(b));
        String titulo = blocos.isEmpty() ? "" : blocos.get(0);
        int pos = 0;
        for (int i = 1; i < blocos.size(); i++) for (String p : pedacos(blocos.get(i))) t.trecho(titulo, p, "texto", pos++);
    }

    static void livro(String texto, String titulo, Trechos t) {
        for (String bloco : texto.split("\n\n", -1)) {
            bloco = Texto.aparar(bloco);
            if (Texto.separar(bloco).length < 15) continue;
            for (String p : pedacos(bloco)) if (Texto.separar(p).length >= 15) t.trecho(titulo, p, "livro", 99);
        }
    }

    static Map<String, String> titulos(File pastaLivros) throws IOException {
        Map<String, String> r = new HashMap<>();
        File f = new File(pastaLivros, "titulos.tsv");
        if (f.exists()) {
            for (String l : Files.readAllLines(f.toPath())) {
                int tab = l.indexOf('\t');
                if (tab > 0) r.put(l.substring(0, tab), l.substring(tab + 1));
            }
        }
        return r;
    }

    /** Todos os trechos, na ordem do rag.py (wiki, textos, livros). */
    public static void percorrer(Corpus corpus, Trechos t, Registro reg) throws IOException {
        List<File> wiki = corpus.txt("wiki"), mod = corpus.txt("modern"), livros = corpus.txt("books");
        int total = wiki.size() + mod.size() + livros.size(), i = 0;
        for (File f : wiki) {
            wiki(Corpus.lerTexto(f), t);
            progresso(++i, total, reg);
        }
        for (File f : mod) {
            moderno(Corpus.lerTexto(f), t);
            progresso(++i, total, reg);
        }
        Map<String, String> tit = titulos(corpus.pasta("books"));
        for (File f : livros) {
            String id = f.getName().substring(0, f.getName().length() - 4).replace("gutenberg_", "");
            livro(Corpus.lerTexto(f), tit.getOrDefault(id, "Livro " + id + " do Project Gutenberg"), t);
            progresso(++i, total, reg);
        }
    }

    private static void progresso(int i, int total, Registro reg) {
        if (reg.parar()) throw new Parado();
        if (i % 5 == 0 || i == total) reg.progresso((double) i / total, "Índice: " + i + "/" + total + " arquivos");
    }

    private static void sql(SQLiteConnection c, String s) {
        try (SQLiteStatement st = c.prepare(s)) {
            st.step();
        }
    }

    /** Monta o índice na conexão (um arquivo novo, aberto para escrita). Devolve o número de trechos. */
    public static long construir(Corpus corpus, SQLiteConnection con, Registro reg) throws IOException {
        sql(con, "PRAGMA journal_mode=OFF");
        sql(con, "PRAGMA synchronous=OFF");
        sql(con, "CREATE VIRTUAL TABLE passages USING fts5(title, text, kind UNINDEXED, pos UNINDEXED, "
                + "tokenize='unicode61 remove_diacritics 2')");
        long[] n = {0};
        Map<String, long[]> porTipo = new HashMap<>();
        sql(con, "BEGIN");
        try (SQLiteStatement ins = con.prepare("INSERT INTO passages VALUES (?, ?, ?, ?)")) {
            percorrer(corpus, (titulo, texto, tipo, pos) -> {
                ins.bindText(1, titulo);
                ins.bindText(2, texto);
                ins.bindText(3, tipo);
                ins.bindLong(4, pos);
                ins.step();
                ins.reset();
                porTipo.computeIfAbsent(tipo, x -> new long[1])[0]++;
                if (++n[0] % 50000 == 0) {
                    sql(con, "COMMIT");
                    sql(con, "BEGIN");
                    reg.log(String.format("  %,d trechos...", n[0]));
                }
            }, reg);
        }
        sql(con, "COMMIT");
        reg.progresso(-1, "Índice: otimizando…");
        sql(con, "INSERT INTO passages(passages) VALUES('optimize')");
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, long[]> e : porTipo.entrySet()) sb.append(e.getKey()).append(": ").append(e.getValue()[0]).append("  ");
        reg.log(String.format("Índice RAG pronto: %,d trechos (%s)", n[0], sb.toString().trim()));
        return n[0];
    }
}
