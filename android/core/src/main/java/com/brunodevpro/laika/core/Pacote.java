package com.brunodevpro.laika.core;

import com.brunodevpro.laika.core.dados.Corpus;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Um zip com tudo de um modelo diferente: o laika_pacote.zip da célula 6 do Colab (também o que a
 * tela Colab baixa), o laika_dados.zip antigo ou um zip montado à mão. Pode ter:
 *   finetuned.pt, pretrain_best.pt (ou laika_*.bin), tokenizer.json (ou .txt), laika_rag.db,
 *   memoria.json, textos em books/, wiki/ e modern/ (o app monta o índice do RAG com eles) e laika_nome.txt
 *   (o nome do modelo: o pacote vira um backup com esse nome, sem trocar a versão em uso).
 * Os arquivos viram entradas do Importador (que reconhece cada um pelo conteúdo); os textos vão
 * para um Corpus. Backups exportados pelo app e checkpoints do PyTorch também são zip: veja {@link #tipo}.
 */
public final class Pacote {
    public final List<Importador.Entrada> entradas = new ArrayList<>();
    /** Arquivos do zip que não servem para nada aqui (ex.: qa/, notebooks). */
    public final List<String> ignorados = new ArrayList<>();
    public int textos;
    /** O nome do modelo (PROJETO da célula 1 do Colab, em laika_nome.txt), ou null. */
    public String nome;
    static final String ARQUIVO_NOME = "laika_nome.txt";

    private Pacote() {
    }

    /** Nome da primeira entrada do zip, sem consumir o fluxo. */
    public static String primeiraEntrada(BufferedInputStream in) throws IOException {
        in.mark(1 << 16);
        try {
            byte[] cab = new byte[30];
            if (lerTudo(in, cab) < 30 || cab[0] != 'P' || cab[1] != 'K' || cab[2] != 3 || cab[3] != 4) return null;
            int tam = (cab[26] & 0xff) | (cab[27] & 0xff) << 8;
            byte[] nome = new byte[tam];
            if (lerTudo(in, nome) < tam) return null;
            return new String(nome, StandardCharsets.UTF_8);
        } finally {
            in.reset();
        }
    }

    private static int lerTudo(InputStream in, byte[] b) throws IOException {
        int n = 0;
        while (n < b.length) {
            int r = in.read(b, n, b.length - n);
            if (r < 0) break;
            n += r;
        }
        return n;
    }

    public static final String BACKUP = "backup", CHECKPOINT = "checkpoint", PACOTE = "pacote";

    /**
     * O que é um arquivo, olhando só a primeira entrada (sem consumir o fluxo): backup exportado
     * pelo app (laika-backup.json vem sempre primeiro), checkpoint do PyTorch ("finetuned/data.pkl"),
     * outro zip (um pacote) ou null se não for zip.
     */
    public static String tipo(BufferedInputStream in) throws IOException {
        String primeira = primeiraEntrada(in);
        if (primeira == null) return null;
        if (primeira.equals(Armazem.MARCA_BACKUP)) return BACKUP;
        if (primeira.equals("data.pkl") || primeira.endsWith("/data.pkl")) return CHECKPOINT;
        return PACOTE;
    }

    /** O tipo de arquivo que interessa ao Importador, pela extensão (o conteúdo é conferido depois). */
    static String extensao(String nome) {
        String n = nome.toLowerCase(Locale.ROOT);
        if (n.endsWith(".pt") || n.endsWith(".pth")) return "pt";
        if (n.endsWith(".bin")) return "bin";
        if (n.endsWith(".db")) return "db";
        if (n.equals("tokenizer.json") || n.equals("memoria.json")) return "json";
        if (n.equals("tokenizer.txt")) return "txt";
        return null;
    }

    /**
     * Lê o zip todo (sem precisar de cópia: vem direto do seletor de arquivos ou do download).
     * corpus recebe os textos; pode ser null quando não se quer textos.
     */
    public static Pacote extrair(InputStream zip, long total, Armazem armazem, Corpus corpus, Armazem.Progresso p)
            throws IOException {
        Pacote r = new Pacote();
        long[] lidos = {0};
        try (ZipInputStream z = new ZipInputStream(zip)) {
            ZipEntry e;
            while ((e = z.getNextEntry()) != null) {
                String caminho = e.getName().replace('\\', '/');
                if (e.isDirectory() || caminho.startsWith("__MACOSX/") || caminho.contains("/.")
                        || caminho.startsWith(".")) {
                    continue;
                }
                String nome = caminho.substring(caminho.lastIndexOf('/') + 1);
                if (caminho.equals(ARQUIVO_NOME)) {
                    byte[] b = new byte[200];
                    int n = lerTudo(z, b);
                    String s = new String(b, 0, n, StandardCharsets.UTF_8).replaceAll("\\s+", " ").trim();
                    if (!s.isEmpty()) r.nome = s.length() > 60 ? s.substring(0, 60) : s;
                    continue;
                }
                File destino = corpus == null ? null : corpus.destino(caminho);
                String ext = destino == null ? extensao(nome) : null;
                if (destino == null && ext == null) {
                    r.ignorados.add(caminho);
                    continue;
                }
                File f = destino != null ? destino : armazem.temporario(ext);
                final long base = lidos[0];
                lidos[0] += Armazem.copiar(z, f, total, p == null ? null : (feito, t) -> p.feito(base + feito, total));
                if (destino != null) {
                    if (nome.endsWith(".txt")) r.textos++;
                } else {
                    r.entradas.add(new Importador.Entrada(f, nome));
                }
            }
        } catch (IOException | RuntimeException erro) {
            for (Importador.Entrada en : r.entradas) en.arquivo.delete();
            throw erro instanceof IOException ? (IOException) erro : new IOException(erro.getMessage(), erro);
        }
        return r;
    }

    /** Se já veio um índice pronto no zip (os textos então não precisam virar outro). */
    public boolean temIndice() {
        for (Importador.Entrada e : entradas) if (e.nome.toLowerCase(Locale.ROOT).endsWith(".db")) return true;
        return false;
    }
}
