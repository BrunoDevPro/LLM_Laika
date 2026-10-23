package com.brunodevpro.laika.core;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.zip.Deflater;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

/**
 * Guarda a versão em uso e os backups.
 *
 * Uma versão = os arquivos do modelo (chat, base, tokenizer, índice do RAG) + a memória do
 * usuário + a conversa. Os arquivos grandes ficam uma vez só em blobs/ e as versões só
 * apontam para eles: um backup não duplica os 640 MB do índice. Os arquivos que vêm dentro
 * do APK são referenciados como "fabrica:nome".
 *
 *   raiz/atual/versao.json, memoria.json, conversa.json
 *   raiz/backups/<id>/versao.json, memoria.json, conversa.json
 *   raiz/blobs/<uuid>.<ext>
 */
public final class Armazem {
    /** Acesso aos arquivos que vêm dentro do APK (assets). */
    public interface Fabrica {
        InputStream abrir(String nome) throws IOException;

        boolean existe(String nome);
    }

    public interface Progresso {
        void feito(long bytes, long total);
    }

    public static final String CHAT = "chat", BASE = "base", TOKENIZER = "tokenizer", INDICE = "indice";
    public static final String[] PAPEIS = {CHAT, BASE, TOKENIZER, INDICE};
    public static final String FABRICA = "fabrica:", BLOB = "blob:";
    public static final String INDICE_FABRICA = FABRICA + "laika_rag_mini.db";
    static final String MARCA_BACKUP = "laika-backup.json";

    /** Um arquivo de uma versão. */
    public static final class Arquivo {
        public final String ref, origem, descricao;
        public final long tamanho;

        public Arquivo(String ref, String origem, String descricao, long tamanho) {
            this.ref = ref;
            this.origem = origem;
            this.descricao = descricao;
            this.tamanho = tamanho;
        }

        Map<String, Object> json() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("ref", ref);
            m.put("origem", origem);
            m.put("descricao", descricao);
            m.put("tamanho", tamanho);
            return m;
        }

        static Arquivo de(Object o) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) o;
            Object t = m.get("tamanho");
            return new Arquivo((String) m.get("ref"), (String) m.get("origem"), (String) m.get("descricao"),
                    t instanceof Number ? ((Number) t).longValue() : 0);
        }

        public boolean daFabrica() {
            return ref.startsWith(FABRICA);
        }
    }

    /** A versão em uso (id null) ou um backup. */
    public static final class Versao {
        public final String id;
        public String nome;
        public long criado, alterado;
        public final Map<String, Arquivo> arquivos = new LinkedHashMap<>();
        final File pasta;

        Versao(String id, File pasta) {
            this.id = id;
            this.pasta = pasta;
        }

        public File memoria() {
            return new File(pasta, "memoria.json");
        }

        public File conversa() {
            return new File(pasta, "conversa.json");
        }

        /** Número de mensagens guardadas na conversa. */
        public int mensagens() {
            try {
                Object o = Json.ler(new String(Files.readAllBytes(conversa().toPath()), StandardCharsets.UTF_8));
                return o instanceof List ? ((List<?>) o).size() : 0;
            } catch (IOException | RuntimeException e) {
                return 0;
            }
        }

        public String resumoMemoria() {
            return new Memoria(memoria()).descricaoCurta();
        }
    }

    private final File raiz, atualDir, backupsDir, blobsDir, tmpDir;
    private final Fabrica fabrica;

    public Armazem(File raiz, Fabrica fabrica) throws IOException {
        this.raiz = raiz;
        this.fabrica = fabrica;
        atualDir = new File(raiz, "atual");
        backupsDir = new File(raiz, "backups");
        blobsDir = new File(raiz, "blobs");
        tmpDir = new File(raiz, "tmp");
        for (File d : new File[]{atualDir, backupsDir, blobsDir, tmpDir}) d.mkdirs();
        if (!new File(atualDir, "versao.json").exists()) criarDeFabrica();
    }

    // ---------- versão de fábrica ----------

    private void criarDeFabrica() throws IOException {
        Versao v = new Versao(null, atualDir);
        v.nome = "Versão de fábrica";
        v.criado = v.alterado = System.currentTimeMillis();
        v.arquivos.putAll(arquivosDeFabrica());
        gravar(v);
    }

    /** Os arquivos que vêm no APK, com a descrição lida do próprio arquivo. */
    public Map<String, Arquivo> arquivosDeFabrica() throws IOException {
        Map<String, Arquivo> m = new LinkedHashMap<>();
        m.put(CHAT, arquivoFabrica("laika_chat.bin", descricaoBin("laika_chat.bin")));
        if (fabrica.existe("laika_base.bin")) m.put(BASE, arquivoFabrica("laika_base.bin", descricaoBin("laika_base.bin")));
        m.put(TOKENIZER, arquivoFabrica("tokenizer.txt", descricaoTokenizer(fabrica.abrir("tokenizer.txt"))));
        m.put(INDICE, arquivoFabrica("laika_rag_mini.db", "índice pequeno (textos próprios e um livro)"));
        return m;
    }

    private Arquivo arquivoFabrica(String nome, String descricao) {
        return new Arquivo(FABRICA + nome, "dentro do app", descricao, 0);
    }

    private String descricaoBin(String nome) throws IOException {
        try (InputStream in = fabrica.abrir(nome)) {
            return ConversorPt.lerBin(in).descricao();
        }
    }

    public static String descricaoTokenizer(InputStream in) throws IOException {
        try (InputStream i = in) {
            return "vocabulário de " + vocabDoTokenizer(i) + " tokens";
        }
    }

    /** Lê só a 1ª linha do tokenizer.txt ("vocab N"). */
    public static int vocabDoTokenizer(InputStream in) throws IOException {
        StringBuilder sb = new StringBuilder();
        int c;
        while ((c = in.read()) >= 0 && c != '\n') sb.append((char) c);
        String l = sb.toString();
        if (!l.startsWith("vocab ")) throw new IOException("tokenizer.txt inválido");
        return Integer.parseInt(l.substring(6).trim());
    }

    // ---------- leitura ----------

    public Versao atual() throws IOException {
        return ler(null, atualDir);
    }

    public List<Versao> backups() {
        List<Versao> r = new ArrayList<>();
        File[] pastas = backupsDir.listFiles(File::isDirectory);
        if (pastas != null) {
            for (File p : pastas) {
                try {
                    r.add(ler(p.getName(), p));
                } catch (IOException | RuntimeException e) {
                    // backup corrompido: não aparece na lista
                }
            }
        }
        r.sort((a, b) -> Long.compare(b.criado, a.criado));
        return r;
    }

    public Versao backup(String id) throws IOException {
        return ler(id, new File(backupsDir, id));
    }

    @SuppressWarnings("unchecked")
    private static Versao ler(String id, File pasta) throws IOException {
        Map<String, Object> m = (Map<String, Object>) Json.ler(lerTexto(new File(pasta, "versao.json")));
        Versao v = new Versao(id, pasta);
        v.nome = (String) m.get("nome");
        v.criado = ((Number) m.get("criado")).longValue();
        v.alterado = m.get("alterado") instanceof Number ? ((Number) m.get("alterado")).longValue() : v.criado;
        Map<String, Object> arqs = (Map<String, Object>) m.get("arquivos");
        for (String papel : PAPEIS) if (arqs.get(papel) != null) v.arquivos.put(papel, Arquivo.de(arqs.get(papel)));
        return v;
    }

    private static void gravar(Versao v) throws IOException {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("formato", 1);
        m.put("nome", v.nome);
        m.put("criado", v.criado);
        m.put("alterado", v.alterado);
        Map<String, Object> arqs = new LinkedHashMap<>();
        for (Map.Entry<String, Arquivo> e : v.arquivos.entrySet()) arqs.put(e.getKey(), e.getValue().json());
        m.put("arquivos", arqs);
        escreverAtomico(new File(v.pasta, "versao.json"), Json.escrever(m).getBytes(StandardCharsets.UTF_8));
    }

    static String lerTexto(File f) throws IOException {
        return new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
    }

    static void escreverAtomico(File f, byte[] dados) throws IOException {
        File tmp = new File(f.getPath() + ".tmp");
        Files.write(tmp.toPath(), dados);
        if (!tmp.renameTo(f)) {
            f.delete();
            if (!tmp.renameTo(f)) throw new IOException("não consegui gravar " + f.getName());
        }
    }

    /** Abre um arquivo de uma versão (do APK ou dos blobs). */
    public InputStream abrir(String ref) throws IOException {
        if (ref.startsWith(FABRICA)) return fabrica.abrir(ref.substring(FABRICA.length()));
        return new FileInputStream(arquivo(ref));
    }

    /** Caminho de um blob (null para arquivos do APK). */
    public File arquivo(String ref) {
        if (!ref.startsWith(BLOB)) return null;
        return new File(blobsDir, ref.substring(BLOB.length()));
    }

    public File memoriaAtual() {
        return new File(atualDir, "memoria.json");
    }

    public File conversaAtual() {
        return new File(atualDir, "conversa.json");
    }

    // ---------- arquivos novos ----------

    /** Arquivo temporário (no mesmo disco dos blobs, para mover sem copiar). */
    public File temporario(String ext) {
        return new File(tmpDir, UUID.randomUUID() + "." + ext);
    }

    /** Move um arquivo pronto para os blobs e devolve o Arquivo para a versão. */
    public Arquivo guardar(File pronto, String ext, String origem, String descricao) throws IOException {
        String nome = UUID.randomUUID() + "." + ext;
        File destino = new File(blobsDir, nome);
        if (!pronto.renameTo(destino)) {
            try (InputStream in = new FileInputStream(pronto)) {
                copiar(in, destino, -1, null);
            }
            pronto.delete();
        }
        return new Arquivo(BLOB + nome, origem, descricao, destino.length());
    }

    public static long copiar(InputStream in, File destino, long total, Progresso p) throws IOException {
        try (OutputStream out = new FileOutputStream(destino)) {
            return copiar(in, out, total, p);
        }
    }

    static long copiar(InputStream in, OutputStream out, long total, Progresso p) throws IOException {
        byte[] buf = new byte[1 << 20];
        long feito = 0;
        int n;
        while ((n = in.read(buf)) > 0) {
            out.write(buf, 0, n);
            feito += n;
            if (p != null) p.feito(feito, total);
        }
        return feito;
    }

    // ---------- backups ----------

    private static byte[] lerOuVazio(File f) {
        try {
            return f.exists() ? Files.readAllBytes(f.toPath()) : new byte[0];
        } catch (IOException e) {
            return new byte[0];
        }
    }

    private static Map<String, String> refs(Versao v) {
        Map<String, String> r = new HashMap<>();
        for (Map.Entry<String, Arquivo> e : v.arquivos.entrySet()) r.put(e.getKey(), e.getValue().ref);
        return r;
    }

    /** O backup idêntico à versão em uso (mesmos arquivos, memória e conversa), ou null. */
    public Versao backupIgualAoAtual() throws IOException {
        Versao a = atual();
        byte[] mem = lerOuVazio(a.memoria()), conv = lerOuVazio(a.conversa());
        for (Versao b : backups()) {
            if (refs(b).equals(refs(a)) && Arrays.equals(mem, lerOuVazio(b.memoria()))
                    && Arrays.equals(conv, lerOuVazio(b.conversa()))) {
                return b;
            }
        }
        return null;
    }

    private static void copiarPasta(Versao de, File para) throws IOException {
        para.mkdirs();
        for (String n : new String[]{"memoria.json", "conversa.json"}) {
            File f = new File(de.pasta, n), d = new File(para, n);
            if (f.exists()) escreverAtomico(d, Files.readAllBytes(f.toPath()));
            else d.delete();
        }
    }

    /** Guarda uma cópia da versão em uso com o nome dado. */
    public Versao fazerBackup(String nome) throws IOException {
        Versao a = atual();
        String id = "b" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6);
        File pasta = new File(backupsDir, id);
        copiarPasta(a, pasta);
        Versao b = new Versao(id, pasta);
        b.nome = nome;
        b.criado = b.alterado = System.currentTimeMillis();
        b.arquivos.putAll(a.arquivos);
        gravar(b);
        return b;
    }

    /** Passa a usar o backup (a versão em uso vira uma cópia dele; o backup não muda). */
    public void usarBackup(String id) throws IOException {
        Versao b = backup(id);
        copiarPasta(b, atualDir);
        Versao a = new Versao(null, atualDir);
        a.nome = b.nome;
        a.criado = b.criado;
        a.alterado = System.currentTimeMillis();
        a.arquivos.putAll(b.arquivos);
        gravar(a);
        limparBlobs();
    }

    /** Renomeia um backup (id) ou a versão em uso (id null). */
    public void renomear(String id, String nome) throws IOException {
        Versao v = id == null ? atual() : backup(id);
        v.nome = nome;
        gravar(v);
    }

    public void apagar(String id) throws IOException {
        File pasta = new File(backupsDir, id);
        File[] fs = pasta.listFiles();
        if (fs != null) for (File f : fs) f.delete();
        if (!pasta.delete() && pasta.exists()) throw new IOException("não consegui apagar o backup");
        limparBlobs();
    }

    /**
     * Troca arquivos da versão em uso (uma atualização). papel -> null remove o arquivo
     * (ex.: o modelo base que não combina com o tokenizer novo). memoria != null substitui a memória.
     */
    public void aplicar(Map<String, Arquivo> trocas, String nome, byte[] memoria) throws IOException {
        Versao a = atual();
        for (Map.Entry<String, Arquivo> e : trocas.entrySet()) {
            if (e.getValue() == null) a.arquivos.remove(e.getKey());
            else a.arquivos.put(e.getKey(), e.getValue());
        }
        if (nome != null) a.nome = nome;
        a.alterado = System.currentTimeMillis();
        if (memoria != null) escreverAtomico(a.memoria(), memoria);
        gravar(a);
        limparBlobs();
    }

    /** Apaga blobs que nenhuma versão usa e temporários esquecidos. */
    public void limparBlobs() throws IOException {
        Set<String> usados = new HashSet<>();
        List<Versao> todas = new ArrayList<>(backups());
        todas.add(atual());
        for (Versao v : todas) for (Arquivo f : v.arquivos.values()) usados.add(f.ref);
        File[] blobs = blobsDir.listFiles();
        if (blobs != null) for (File f : blobs) if (!usados.contains(BLOB + f.getName())) f.delete();
        File[] tmps = tmpDir.listFiles();
        if (tmps != null) for (File f : tmps) f.delete();
    }

    /** Espaço ocupado no celular (blobs + versões). */
    public long espacoUsado() {
        long t = 0;
        for (File d : new File[]{blobsDir, atualDir}) {
            File[] fs = d.listFiles();
            if (fs != null) for (File f : fs) t += f.length();
        }
        File[] bs = backupsDir.listFiles();
        if (bs != null) {
            for (File b : bs) {
                File[] fs = b.listFiles();
                if (fs != null) for (File f : fs) t += f.length();
            }
        }
        return t;
    }

    // ---------- exportar / importar backup (.zip) ----------

    private static String extensao(String ref) {
        int p = ref.lastIndexOf('.');
        return p < 0 ? "bin" : ref.substring(p + 1);
    }

    /** Tamanho do arquivo (blobs) ou -1 se for do APK. */
    public long tamanho(Arquivo a) {
        File f = arquivo(a.ref);
        return f == null ? -1 : f.length();
    }

    /**
     * Grava a versão (id null = em uso) num .zip com tudo: modelos, tokenizer, índice (se
     * incluirIndice), memória e conversa. Dá para importar de volta em qualquer celular.
     */
    public void exportar(String id, OutputStream saida, boolean incluirIndice, Progresso p) throws IOException {
        Versao v = id == null ? atual() : backup(id);
        long total = 0;
        for (Map.Entry<String, Arquivo> e : v.arquivos.entrySet()) {
            if (INDICE.equals(e.getKey()) && !incluirIndice) continue;
            total += Math.max(0, tamanho(e.getValue()));
        }
        ZipOutputStream zip = new ZipOutputStream(saida);
        zip.setLevel(Deflater.BEST_SPEED);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("formato", 1);
        m.put("nome", v.nome);
        m.put("criado", v.criado);
        m.put("alterado", v.alterado);
        Map<String, Object> arqs = new LinkedHashMap<>();
        for (Map.Entry<String, Arquivo> e : v.arquivos.entrySet()) {
            Arquivo a = e.getValue();
            boolean fora = INDICE.equals(e.getKey()) && !incluirIndice && !a.ref.equals(INDICE_FABRICA);
            String ref = fora ? INDICE_FABRICA : "zip:arquivos/" + e.getKey() + "." + extensao(a.ref);
            String desc = fora ? "índice pequeno (o completo não foi incluído no backup)" : a.descricao;
            arqs.put(e.getKey(), new Arquivo(ref, a.origem, desc, a.tamanho).json());
        }
        m.put("arquivos", arqs);
        zip.putNextEntry(new ZipEntry(MARCA_BACKUP));
        zip.write(Json.escrever(m).getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
        for (File f : new File[]{v.memoria(), v.conversa()}) {
            if (!f.exists()) continue;
            zip.putNextEntry(new ZipEntry(f.getName()));
            zip.write(Files.readAllBytes(f.toPath()));
            zip.closeEntry();
        }
        long[] base = {0};
        for (Map.Entry<String, Arquivo> e : v.arquivos.entrySet()) {
            Arquivo a = e.getValue();
            if (INDICE.equals(e.getKey()) && !incluirIndice && !a.ref.equals(INDICE_FABRICA)) continue;
            zip.putNextEntry(new ZipEntry("arquivos/" + e.getKey() + "." + extensao(a.ref)));
            final long inicio = base[0];
            final long tot = total;
            try (InputStream in = abrir(a.ref)) {
                base[0] += copiar(in, zip, tot, p == null ? null : (feito, t) -> p.feito(inicio + feito, tot));
            }
            zip.closeEntry();
        }
        zip.finish();
        zip.flush();
    }

    /**
     * Um backup novo com estes arquivos (papel -> arquivo já guardado nos blobs), sem trocar a versão em
     * uso. Sem índice, usa o pequeno do app.
     */
    public Versao backupDeArquivos(String nome, Map<String, Arquivo> arquivos) throws IOException {
        if (!arquivos.containsKey(CHAT) || !arquivos.containsKey(TOKENIZER)) {
            throw new IOException("um backup precisa do modelo de chat e do tokenizer");
        }
        String id = "b" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6);
        File pasta = new File(backupsDir, id);
        pasta.mkdirs();
        Versao b = new Versao(id, pasta);
        b.nome = nome;
        b.criado = b.alterado = System.currentTimeMillis();
        b.arquivos.putAll(arquivos);
        if (!b.arquivos.containsKey(INDICE)) b.arquivos.put(INDICE, arquivosDeFabrica().get(INDICE));
        gravar(b);
        return b;
    }

    /** Lê um .zip exportado e o guarda como um backup novo (não troca a versão em uso). */
    @SuppressWarnings("unchecked")
    public Versao importarBackup(InputStream entrada, long total, Progresso p) throws IOException {
        Map<String, File> extraidos = new HashMap<>();
        byte[] manifesto = null, memoria = null, conversa = null;
        long[] lidos = {0};
        File pasta = null;
        try (ZipInputStream zip = new ZipInputStream(entrada)) {
            ZipEntry e;
            while ((e = zip.getNextEntry()) != null) {
                String n = e.getName();
                if (n.equals(MARCA_BACKUP)) manifesto = lerTudo(zip);
                else if (n.equals("memoria.json")) memoria = lerTudo(zip);
                else if (n.equals("conversa.json")) conversa = lerTudo(zip);
                else if (n.startsWith("arquivos/") && !n.contains("..")) {
                    String arq = n.substring("arquivos/".length());
                    File tmp = temporario(extensao(arq));
                    final long inicio = lidos[0];
                    lidos[0] += copiar(zip, tmp, total,
                            p == null ? null : (feito, t) -> p.feito(inicio + feito, total));
                    extraidos.put("zip:" + n, tmp);
                }
            }
            if (manifesto == null) throw new IOException("este .zip não é um backup da Laika");
            Map<String, Object> m = (Map<String, Object>) Json.ler(new String(manifesto, StandardCharsets.UTF_8));
            String id = "b" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6);
            pasta = new File(backupsDir, id);
            pasta.mkdirs();
            Versao b = new Versao(id, pasta);
            b.nome = String.valueOf(m.get("nome"));
            b.criado = m.get("criado") instanceof Number ? ((Number) m.get("criado")).longValue() : System.currentTimeMillis();
            b.alterado = System.currentTimeMillis();
            Map<String, Object> arqs = (Map<String, Object>) m.get("arquivos");
            for (String papel : PAPEIS) {
                if (arqs.get(papel) == null) continue;
                Arquivo a = Arquivo.de(arqs.get(papel));
                if (a.ref.startsWith("zip:")) {
                    File f = extraidos.remove(a.ref);
                    if (f == null) throw new IOException("o backup está incompleto (falta " + a.ref.substring(4) + ")");
                    Arquivo g = guardar(f, extensao(a.ref), a.origem, a.descricao);
                    b.arquivos.put(papel, g);
                } else if (a.daFabrica() && fabrica.existe(a.ref.substring(FABRICA.length()))) {
                    b.arquivos.put(papel, a);
                }
            }
            if (!b.arquivos.containsKey(CHAT) || !b.arquivos.containsKey(TOKENIZER)) {
                throw new IOException("o backup não tem o modelo de chat e o tokenizer");
            }
            if (!b.arquivos.containsKey(INDICE)) b.arquivos.put(INDICE, arquivosDeFabrica().get(INDICE));
            if (memoria != null) escreverAtomico(b.memoria(), memoria);
            if (conversa != null) escreverAtomico(b.conversa(), conversa);
            gravar(b);
            pasta = null;
            return b;
        } catch (RuntimeException e) {
            throw new IOException("backup inválido: " + e.getMessage(), e);
        } finally {
            for (File f : extraidos.values()) f.delete();
            if (pasta != null) {  // deu erro no meio: não deixa um backup pela metade
                File[] fs = pasta.listFiles();
                if (fs != null) for (File f : fs) f.delete();
                pasta.delete();
            }
        }
    }

    private static byte[] lerTudo(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        copiar(in, out, -1, null);
        return out.toByteArray();
    }
}
