package com.brunodevpro.laika.core;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Importa os arquivos de uma atualização, reconhecendo cada um pelo conteúdo:
 *   finetuned.pt / pretrain_best.pt  -> convertidos para o formato do app (chat ou base)
 *   laika_*.bin, tokenizer.json / tokenizer.txt, laika_rag.db, memoria.json
 *   .zip de backup exportado pelo app -> vira um backup novo
 * e confere se o modelo e o tokenizer combinam antes de trocar qualquer coisa.
 * Os arquivos de dentro de um laika_pacote.zip chegam aqui pelo {@link Pacote}.
 */
public final class Importador {
    /** Abre um laika_rag.db para conferir e devolve o número de trechos (lança erro se não servir). */
    public interface ConferirIndice {
        long trechos(File db) throws Exception;
    }

    /** Um arquivo escolhido pelo usuário, já copiado para o celular. */
    public static final class Entrada {
        public final File arquivo;
        public final String nome;

        public Entrada(File arquivo, String nome) {
            this.arquivo = arquivo;
            this.nome = nome;
        }
    }

    public static final class Resultado {
        /** papel -> arquivo novo (null = remover da versão). */
        public final Map<String, Armazem.Arquivo> trocas = new LinkedHashMap<>();
        public byte[] memoria;
        public final List<Armazem.Versao> backupsImportados = new ArrayList<>();
        public final List<String> avisos = new ArrayList<>();
        public final List<String> feitos = new ArrayList<>();

        /** Se a versão em uso vai mudar (senão, só entraram backups). */
        public boolean mudaVersao() {
            return !trocas.isEmpty() || memoria != null;
        }
    }

    private final Armazem armazem;
    private final ConferirIndice conferir;

    public Importador(Armazem armazem, ConferirIndice conferir) {
        this.armazem = armazem;
        this.conferir = conferir;
    }

    private static String inicio(File f, int n) throws IOException {
        byte[] b = new byte[n];
        int lidos = 0;
        try (InputStream in = new FileInputStream(f)) {
            while (lidos < n) {
                int r = in.read(b, lidos, n - lidos);
                if (r < 0) break;
                lidos += r;
            }
        }
        return new String(b, 0, lidos, StandardCharsets.ISO_8859_1);
    }

    public Resultado importar(List<Entrada> entradas) throws IOException {
        Resultado r = new Resultado();
        try {
            for (Entrada e : entradas) identificarEConverter(e, r);
            conferirCompatibilidade(r);
        } catch (IOException | RuntimeException erro) {
            armazem.limparBlobs();  // apaga o que foi convertido e não vai ser usado
            throw erro instanceof IOException ? (IOException) erro : new IOException(erro.getMessage(), erro);
        } finally {
            for (Entrada e : entradas) e.arquivo.delete();
        }
        return r;
    }

    @SuppressWarnings("unchecked")
    private void identificarEConverter(Entrada e, Resultado r) throws IOException {
        String cab = inicio(e.arquivo, 16);
        String nome = e.nome;
        if (cab.startsWith("PK\u0003\u0004")) {
            ConversorPt.Info info;
            try {
                info = ConversorPt.ler(e.arquivo);
            } catch (IOException naoEhCheckpoint) {
                // Talvez seja um backup exportado pelo app.
                try (InputStream in = new FileInputStream(e.arquivo)) {
                    Armazem.Versao b = armazem.importarBackup(in, e.arquivo.length(), null);
                    r.backupsImportados.add(b);
                    r.feitos.add("backup \"" + b.nome + "\" importado");
                    return;
                } catch (IOException naoEhBackup) {
                    throw new IOException(nome + ": não é um checkpoint do PyTorch nem um backup da Laika ("
                            + naoEhCheckpoint.getMessage() + ")");
                }
            }
            File bin = armazem.temporario("bin");
            try (OutputStream out = new FileOutputStream(bin)) {
                info = ConversorPt.converter(e.arquivo, out);
            } catch (IOException erro) {
                bin.delete();
                throw new IOException(nome + ": " + erro.getMessage(), erro);
            }
            String papel = info.finetuned ? Armazem.CHAT : Armazem.BASE;
            colocar(r, papel, armazem.guardar(bin, "bin", nome, info.descricao()), nome);
        } else if (cab.startsWith("LAIKA001") || cab.startsWith("LAIKA002")) {
            ConversorPt.Info info;
            try (InputStream in = new FileInputStream(e.arquivo)) {
                info = ConversorPt.lerBin(in);
            }
            String n = nome.toLowerCase(Locale.ROOT);
            String papel = info.temRodape ? (info.finetuned ? Armazem.CHAT : Armazem.BASE)
                    : (n.contains("base") || n.contains("pretrain") ? Armazem.BASE : Armazem.CHAT);
            colocar(r, papel, armazem.guardar(e.arquivo, "bin", nome, info.descricao()), nome);
        } else if (cab.startsWith("SQLite format 3")) {
            long trechos;
            try {
                trechos = conferir.trechos(e.arquivo);
            } catch (Exception erro) {
                throw new IOException(nome + ": não é um índice do RAG da Laika (" + erro.getMessage() + ")");
            }
            colocar(r, Armazem.INDICE, armazem.guardar(e.arquivo, "db", nome,
                    String.format("índice com %,d trechos", trechos)), nome);
        } else if (cab.startsWith("vocab ")) {
            String desc;
            try (InputStream in = new FileInputStream(e.arquivo)) {
                desc = Armazem.descricaoTokenizer(in);
            }
            colocar(r, Armazem.TOKENIZER, armazem.guardar(e.arquivo, "txt", nome, desc), nome);
        } else if (cab.trim().startsWith("{") || cab.startsWith("﻿")) {
            String texto = new String(Files.readAllBytes(e.arquivo.toPath()), StandardCharsets.UTF_8);
            Object json;
            try {
                json = Json.ler(texto.startsWith("﻿") ? texto.substring(1) : texto);
            } catch (RuntimeException erro) {
                throw new IOException(nome + ": JSON inválido");
            }
            Map<String, Object> m = json instanceof Map ? (Map<String, Object>) json : null;
            if (m != null && m.containsKey("model") && m.containsKey("added_tokens")) {
                String txt;
                try (InputStream in = new FileInputStream(e.arquivo)) {
                    txt = ConversorTokenizer.converter(in);
                }
                File f = armazem.temporario("txt");
                Files.write(f.toPath(), txt.getBytes(StandardCharsets.UTF_8));
                String desc = Armazem.descricaoTokenizer(new FileInputStream(f));
                colocar(r, Armazem.TOKENIZER, armazem.guardar(f, "txt", nome, desc), nome);
            } else if (m != null && (m.containsKey("nome") || m.containsKey("gostos") || m.containsKey("notas"))) {
                r.memoria = texto.getBytes(StandardCharsets.UTF_8);
                r.feitos.add("memória de " + nome);
            } else {
                throw new IOException(nome + ": JSON que não é tokenizer nem memória");
            }
        } else {
            throw new IOException(nome + ": tipo de arquivo não reconhecido. Use finetuned.pt, pretrain_best.pt, "
                    + "tokenizer.json, laika_rag.db, memoria.json, o laika_pacote.zip do Colab ou um backup .zip.");
        }
    }

    private static String nomePapel(String papel) {
        switch (papel) {
            case Armazem.CHAT: return "modelo de chat";
            case Armazem.BASE: return "modelo de completar texto";
            case Armazem.TOKENIZER: return "tokenizer";
            default: return "índice do RAG";
        }
    }

    private static void colocar(Resultado r, String papel, Armazem.Arquivo a, String nome) {
        if (r.trocas.containsKey(papel)) {
            r.avisos.add("dois arquivos para o " + nomePapel(papel) + "; usei " + nome);
        }
        r.trocas.put(papel, a);
        r.feitos.add(nomePapel(papel) + " (" + nome + ")");
    }

    /** O tokenizer e os modelos precisam ter o mesmo vocabulário. */
    private void conferirCompatibilidade(Resultado r) throws IOException {
        if (r.trocas.isEmpty()) return;
        Armazem.Versao atual = armazem.atual();
        int vocabTok = vocabTokenizer(r.trocas.containsKey(Armazem.TOKENIZER)
                ? r.trocas.get(Armazem.TOKENIZER) : atual.arquivos.get(Armazem.TOKENIZER));
        boolean tokNovo = r.trocas.containsKey(Armazem.TOKENIZER);

        Armazem.Arquivo chat = r.trocas.containsKey(Armazem.CHAT) ? r.trocas.get(Armazem.CHAT) : atual.arquivos.get(Armazem.CHAT);
        int vocabChat = vocabModelo(chat);
        if (vocabChat != vocabTok) {
            throw new IOException(String.format("o modelo de chat (vocabulário %d) não combina com o tokenizer "
                    + "(vocabulário %d). %s", vocabChat, vocabTok, tokNovo
                    ? "Importe também o finetuned.pt treinado com este tokenizer."
                    : "Importe também o tokenizer.json do mesmo treino."));
        }
        Armazem.Arquivo base = r.trocas.containsKey(Armazem.BASE) ? r.trocas.get(Armazem.BASE) : atual.arquivos.get(Armazem.BASE);
        if (base != null && vocabModelo(base) != vocabTok) {
            if (r.trocas.containsKey(Armazem.BASE)) {
                throw new IOException("o pretrain_best.pt não combina com o tokenizer. Importe os arquivos do mesmo treino.");
            }
            r.trocas.put(Armazem.BASE, null);
            r.avisos.add("o modelo de completar texto antigo não combina com o tokenizer novo e foi tirado desta "
                    + "versão (importe o pretrain_best.pt novo para tê-lo de volta)");
        }
    }

    private int vocabTokenizer(Armazem.Arquivo a) throws IOException {
        try (InputStream in = armazem.abrir(a.ref)) {
            return Armazem.vocabDoTokenizer(in);
        }
    }

    private int vocabModelo(Armazem.Arquivo a) throws IOException {
        try (InputStream in = armazem.abrir(a.ref)) {
            return ConversorPt.lerBin(in).vocab;
        }
    }
}
