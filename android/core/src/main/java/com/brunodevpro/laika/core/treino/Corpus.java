package com.brunodevpro.laika.core.treino;

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
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Os textos de treino no celular, com as mesmas pastas do projeto:
 *   books/ (Gutenberg + titulos.tsv), wiki/, modern/, qa/, qa_auto/
 * Os livros e artigos chegam num .zip montado no Colab (célula "Exportar dados para o celular")
 * e baixado do Google Drive; modern/ e qa/ já vêm dentro do app.
 */
public final class Corpus {
    public static final String[] PASTAS = {"books", "wiki", "modern", "qa", "qa_auto"};

    /** Arquivos que vêm dentro do APK (assets/dados/...). */
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

    /** Arquivos do pré-treino, na ordem do train.py (books, wiki, modern). */
    public List<File> preTreino() {
        List<File> r = new ArrayList<>(txt("books"));
        r.addAll(txt("wiki"));
        r.addAll(txt("modern"));
        return r;
    }

    /** Copia modern/ e qa/ do APK se a pasta estiver vazia (o mínimo para o fine-tuning). */
    public void garantirPadrao(Fabrica fab) throws IOException {
        for (String p : new String[]{"modern", "qa"}) {
            if (!txt(p).isEmpty()) continue;
            for (String n : fab.listar(p)) {
                try (InputStream in = fab.abrir(p + "/" + n)) {
                    Armazem.copiar(in, new File(pasta(p), n), -1, null);
                }
            }
        }
    }

    /** Extrai um .zip de dados (aceita "data/books/x.txt", "LLM_Laika/books/x.txt", "books/x.txt"...). */
    public String importarZip(InputStream zip, long total, Armazem.Progresso p) throws IOException {
        int[] porPasta = new int[PASTAS.length];
        long lidos = 0;
        try (ZipInputStream z = new ZipInputStream(zip)) {
            ZipEntry e;
            while ((e = z.getNextEntry()) != null) {
                if (e.isDirectory()) continue;
                String[] partes = e.getName().replace('\\', '/').split("/");
                if (partes.length < 2) continue;
                String pasta = partes[partes.length - 2], nome = partes[partes.length - 1];
                int i = Arrays.asList(PASTAS).indexOf(pasta);
                if (i < 0 || nome.startsWith(".") || nome.contains("..")) continue;
                if (!nome.endsWith(".txt") && !(pasta.equals("books") && nome.equals("titulos.tsv"))) continue;
                File destino = new File(pasta(pasta), nome);
                final long base = lidos;
                lidos += Armazem.copiar(z, destino, total, p == null ? null : (f, t) -> p.feito(base + f, total));
                if (nome.endsWith(".txt")) porPasta[i]++;
            }
        }
        List<String> r = new ArrayList<>();
        for (int i = 0; i < PASTAS.length; i++) if (porPasta[i] > 0) r.add(porPasta[i] + " em " + PASTAS[i]);
        if (r.isEmpty()) throw new IOException("nenhum .txt de books/, wiki/, modern/, qa/ ou qa_auto/ no arquivo");
        return String.join(", ", r);
    }

    public void apagar(String pasta) {
        File[] fs = pasta(pasta).listFiles();
        if (fs != null) for (File f : fs) f.delete();
    }

    /** "495 livros (98 MB) · 50 arquivos da wiki (190 MB) · ..." */
    public String resumo() {
        List<String> r = new ArrayList<>();
        String[] nomes = {"livros", "arquivos da Wikipédia", "textos próprios", "arquivos de perguntas", "arquivos de perguntas da Wikipédia"};
        for (int i = 0; i < PASTAS.length; i++) {
            List<File> fs = txt(PASTAS[i]);
            long b = 0;
            for (File f : fs) b += f.length();
            r.add(String.format(Locale.getDefault(), "%d %s (%.1f MB)", fs.size(), nomes[i], b / 1e6));
        }
        return String.join("\n", r);
    }

    public long bytes(List<File> fs) {
        long b = 0;
        for (File f : fs) b += f.length();
        return b;
    }

    /** Identifica o conjunto de arquivos (para saber se os tokens já calculados ainda valem). */
    public static String assinatura(List<File> fs) {
        long h = 1125899906842597L;
        for (File f : fs) {
            String s = f.getParentFile().getName() + "/" + f.getName() + ":" + f.length();
            for (int i = 0; i < s.length(); i++) h = 31 * h + s.charAt(i);
        }
        return Long.toHexString(h) + "-" + fs.size();
    }

    /** InputStream.readAllBytes() só existe a partir do Android 13. */
    public static byte[] lerTudo(InputStream in) throws IOException {
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        byte[] b = new byte[1 << 16];
        int n;
        while ((n = in.read(b)) > 0) out.write(b, 0, n);
        return out.toByteArray();
    }

    public static String lerTexto(File f) throws IOException {
        return new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
    }
}
