package com.brunodevpro.laika.core.dados;

import com.brunodevpro.laika.core.Armazem;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/**
 * Os textos de onde o celular monta o índice do RAG, com as pastas do projeto:
 *   books/ (Gutenberg + titulos.tsv), wiki/ e modern/
 * Chegam dentro de um zip (célula 6 do Colab com TEXTOS marcado, ou o laika_dados.zip antigo).
 */
public final class Corpus {
    public static final String[] PASTAS = {"books", "wiki", "modern"};

    /** Os textos que vêm dentro do APK (assets/dados/modern). */
    public interface Fabrica {
        String[] listar(String pasta) throws IOException;

        InputStream abrir(String caminho) throws IOException;
    }

    public final File raiz;

    public Corpus(File raiz) {
        this.raiz = raiz;
        for (String p : PASTAS) new File(raiz, p).mkdirs();
    }

    public File pasta(String nome) {
        return new File(raiz, nome);
    }

    public List<File> txt(String pasta) {
        File[] fs = pasta(pasta).listFiles((d, n) -> n.endsWith(".txt"));
        List<File> r = new ArrayList<>();
        if (fs != null) r.addAll(Arrays.asList(fs));
        r.sort((a, b) -> a.getName().compareTo(b.getName()));  // sorted() do Python
        return r;
    }

    /** Quantos .txt há em books/, wiki/ e modern/. */
    public int arquivos() {
        int n = 0;
        for (String p : PASTAS) n += txt(p).size();
        return n;
    }

    /**
     * Onde guardar uma entrada de zip, se ela for um texto do corpus ("data/books/x.txt",
     * "LLM_Laika/wiki/wiki_000.txt", "books/titulos.tsv"...), ou null se não for.
     */
    public File destino(String nomeNoZip) {
        String[] partes = nomeNoZip.replace('\\', '/').split("/");
        if (partes.length < 2) return null;
        String pasta = partes[partes.length - 2], nome = partes[partes.length - 1];
        if (!Arrays.asList(PASTAS).contains(pasta) || nome.startsWith(".") || nome.contains("..")) return null;
        if (!nome.endsWith(".txt") && !(pasta.equals("books") && nome.equals("titulos.tsv"))) return null;
        return new File(pasta(pasta), nome);
    }

    /** Copia os textos próprios do APK se o zip não trouxe modern/ (o rag.py sempre os indexa). */
    public void garantirModerno(Fabrica fab) throws IOException {
        if (!txt("modern").isEmpty()) return;
        for (String n : fab.listar("modern")) {
            try (InputStream in = fab.abrir("modern/" + n)) {
                Armazem.copiar(in, new File(pasta("modern"), n), -1, null);
            }
        }
    }

    /** "495 livros, 1000 arquivos da Wikipédia e 130 textos próprios" */
    public String resumo() {
        String[][] nomes = {{"livro", "livros"}, {"arquivo da Wikipédia", "arquivos da Wikipédia"},
                {"texto próprio", "textos próprios"}};
        List<String> r = new ArrayList<>();
        for (int i = 0; i < PASTAS.length; i++) {
            int n = txt(PASTAS[i]).size();
            if (n > 0) r.add(String.format(Locale.getDefault(), "%d %s", n, nomes[i][n == 1 ? 0 : 1]));
        }
        if (r.isEmpty()) return "nenhum texto";
        if (r.size() == 1) return r.get(0);
        return String.join(", ", r.subList(0, r.size() - 1)) + " e " + r.get(r.size() - 1);
    }

    /** Apaga os textos (a pasta é temporária). */
    public void apagar() {
        for (String p : PASTAS) {
            File[] fs = pasta(p).listFiles();
            if (fs != null) for (File f : fs) f.delete();
            pasta(p).delete();
        }
        raiz.delete();
    }

    public static String lerTexto(File f) throws IOException {
        return new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
    }
}
