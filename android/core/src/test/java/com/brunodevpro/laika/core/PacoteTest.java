package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.dados.ConstrutorIndice;
import com.brunodevpro.laika.core.dados.Corpus;
import com.brunodevpro.laika.core.dados.Registro;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * O zip único (laika_pacote.zip da célula 6 / artefato da tela Colab): modelos, tokenizer,
 * memória e textos viram uma versão nova, com o índice do RAG montado no celular.
 */
class PacoteTest {
    static File assets = new File(System.getProperty("laika.assets", "../app/src/main/assets"));
    static File ck = new File(System.getProperty("laika.checkpoints", "none"));
    static File repo = new File(System.getProperty("laika.repo", "../.."));

    static final String WIKI = "Laika (cadela)\n\nLaika foi uma cadela soviética, o primeiro animal a orbitar a Terra, "
            + "a bordo do Sputnik 2, em novembro de 1957. Ela era uma vira-lata das ruas de Moscou.\n\n"
            + "Vulcão\n\nUm vulcão é uma abertura na superfície da Terra por onde sai magma, cinzas e gases "
            + "do interior do planeta durante uma erupção.\n\n"
            + "Zarabatana\n\nUma zarabatana é um tubo longo e estreito usado para soprar pequenos dardos, "
            + "comum entre povos indígenas da Amazônia para caçar.\n";

    @TempDir
    File tmp;
    Armazem armazem;

    @BeforeEach
    void preparar() throws IOException {
        assumeTrue(new File(ck, "finetuned.pt").exists() && new File(assets, "laika_chat.bin").exists(),
                "defina LAIKA_CHECKPOINTS e rode exportar_modelo.py");
        armazem = new Armazem(new File(tmp, "laika"), new Armazem.Fabrica() {
            public InputStream abrir(String nome) throws IOException {
                return new FileInputStream(new File(assets, nome));
            }

            public boolean existe(String nome) {
                return new File(assets, nome).exists();
            }
        });
    }

    static byte[] zip(Object... nomesEConteudos) throws IOException {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        try (ZipOutputStream z = new ZipOutputStream(b)) {
            for (int i = 0; i < nomesEConteudos.length; i += 2) {
                z.putNextEntry(new ZipEntry((String) nomesEConteudos[i]));
                Object c = nomesEConteudos[i + 1];
                z.write(c instanceof byte[] ? (byte[]) c : ((String) c).getBytes(StandardCharsets.UTF_8));
                z.closeEntry();
            }
        }
        return b.toByteArray();
    }

    static byte[] ler(File f) throws IOException {
        return Files.readAllBytes(f.toPath());
    }

    static BufferedInputStream fluxo(byte[] b) {
        return new BufferedInputStream(new ByteArrayInputStream(b), 1 << 16);
    }

    /** Monta o índice com os textos do corpus, como o app faz depois de extrair o zip. */
    Importador.Entrada indice(Corpus corpus) throws IOException {
        File db = armazem.temporario("db");
        SQLiteConnection con = new BundledSQLiteDriver().open(db.getPath());
        try {
            ConstrutorIndice.construir(corpus, con, Registro.CONSOLE);
        } finally {
            con.close();
        }
        return new Importador.Entrada(db, "índice montado no celular");
    }

    static long trechos(File db) {
        try (IndiceRag r = new IndiceRag(new BundledSQLiteDriver().open(db.getPath()))) {
            return r.contarTrechos();
        }
    }

    @Test
    void tipos() throws IOException {
        File ex = new File(tmp, "backup.zip");
        try (java.io.OutputStream out = new java.io.FileOutputStream(ex)) {
            armazem.exportar(null, out, false, null);
        }
        assertEquals(Pacote.BACKUP, Pacote.tipo(fluxo(ler(ex))));
        assertEquals(Pacote.CHECKPOINT, Pacote.tipo(fluxo(ler(new File(ck, "finetuned.pt")))));
        assertEquals(Pacote.PACOTE, Pacote.tipo(fluxo(zip("finetuned.pt", "x"))));
        assertNull(Pacote.tipo(fluxo("vocab 8000".getBytes(StandardCharsets.UTF_8))));
        // o fluxo continua inteiro depois de olhar o começo
        BufferedInputStream in = fluxo(zip("a/b.txt", "conteúdo"));
        Pacote.tipo(in);
        assertEquals('P', in.read());
    }

    @Test
    void pacoteCompletoViraUmaVersaoNova() throws Exception {
        byte[] z = zip(
                "finetuned.pt", ler(new File(ck, "finetuned.pt")),
                "pretrain_best.pt", ler(new File(ck, "pretrain_best.pt")),
                "tokenizer.json", ler(new File(ck, "tokenizer.json")),
                "memoria.json", "{\"nome\": \"Ana\", \"cidade\": null, \"gostos\": [], \"notas\": []}",
                "wiki/wiki_000.txt", WIKI,
                "qa/pergeresp.txt", "<|user|> oi\n<|assistant|> olá <|end|>\n",
                "__MACOSX/._finetuned.pt", "lixo",
                "LEIA-ME.md", "texto qualquer");
        Corpus corpus = new Corpus(new File(tmp, "corpus"));
        List<long[]> progresso = new ArrayList<>();
        Pacote p = Pacote.extrair(fluxo(z), z.length, armazem, corpus, (feito, total) -> progresso.add(new long[]{feito, total}));
        assertEquals(4, p.entradas.size());
        assertEquals(1, p.textos);
        assertEquals(List.of("qa/pergeresp.txt", "LEIA-ME.md"), p.ignorados);
        assertFalse(p.temIndice());
        assertFalse(progresso.isEmpty());

        // o app junta os textos próprios do APK (aqui, data/modern do repositório) e monta o índice
        corpus.garantirModerno(new Corpus.Fabrica() {
            public String[] listar(String pasta) {
                return new File(repo, "data/" + pasta).list();
            }

            public InputStream abrir(String caminho) throws IOException {
                return new FileInputStream(new File(repo, "data/" + caminho));
            }
        });
        assertTrue(corpus.txt("modern").size() > 100);
        assertTrue(corpus.resumo().startsWith("1 arquivo da Wikipédia e "), corpus.resumo());
        List<Importador.Entrada> entradas = new ArrayList<>(p.entradas);
        entradas.add(indice(corpus));
        Importador.Resultado r = new Importador(armazem, PacoteTest::trechos).importar(entradas);
        assertEquals(List.of(Armazem.CHAT, Armazem.BASE, Armazem.TOKENIZER, Armazem.INDICE),
                new ArrayList<>(r.trocas.keySet()));
        assertNotNull(r.memoria);
        assertTrue(r.avisos.isEmpty(), r.avisos.toString());

        armazem.aplicar(r.trocas, "Colab de hoje", r.memoria);
        Armazem.Versao v = armazem.atual();
        assertEquals("Colab de hoje", v.nome);
        assertTrue(v.resumoMemoria().contains("Ana"), v.resumoMemoria());
        File db = armazem.arquivo(v.arquivos.get(Armazem.INDICE).ref);
        try (IndiceRag rag = new IndiceRag(new BundledSQLiteDriver().open(db.getPath()))) {
            IndiceRag.Trecho t = rag.melhor("O que é uma zarabatana?");
            assertNotNull(t);
            assertEquals("Zarabatana", t.titulo);
        }
        corpus.apagar();
        assertFalse(corpus.raiz.exists());
    }

    /** Um pacote com laika_nome.txt (PROJETO do Colab) vira um backup com esse nome; a versão em uso não muda. */
    @Test
    void pacoteComNomeVaiParaOsBackups() throws Exception {
        Files.writeString(armazem.memoriaAtual().toPath(), "{\"nome\": \"Bruno\", \"notas\": []}");
        Files.writeString(armazem.conversaAtual().toPath(), "[{\"u\": true, \"t\": \"oi\"}]");
        byte[] z = zip(
                "finetuned.pt", ler(new File(ck, "finetuned.pt")),
                "tokenizer.json", ler(new File(ck, "tokenizer.json")),
                "laika_nome.txt", "  Laika pequena\n7M ");
        Pacote p = Pacote.extrair(fluxo(z), z.length, armazem, null, null);
        assertEquals("Laika pequena 7M", p.nome);
        assertEquals(2, p.entradas.size());
        assertTrue(p.ignorados.isEmpty(), p.ignorados.toString());
        Importador.Resultado r = new Importador(armazem, PacoteTest::trechos).importar(p.entradas);
        String antes = armazem.atual().nome;
        Armazem.Versao b = armazem.backupComTrocas(p.nome, r.trocas, r.memoria);
        assertEquals(antes, armazem.atual().nome);
        assertEquals("Laika pequena 7M", b.nome);
        assertEquals(0, b.mensagens());
        assertTrue(b.resumoMemoria().contains("Bruno"), b.resumoMemoria());
        assertEquals(armazem.atual().arquivos.get(Armazem.INDICE).ref, b.arquivos.get(Armazem.INDICE).ref);
        // O mesmo nome de novo: ganha a data, não substitui o anterior.
        Armazem.Versao b2 = armazem.backupComTrocas(p.nome, r.trocas, null);
        assertTrue(b2.nome.startsWith("Laika pequena 7M ("), b2.nome);
        assertEquals(2, armazem.backups().size());
    }

    /** O modelo em uso e o backup com os mesmos arquivos são o mesmo modelo; o apelido vale para os dois. */
    @Test
    void mesmosArquivosEApelido() throws Exception {
        assertNull(armazem.backupComMesmosArquivos());
        Armazem.Versao b = armazem.fazerBackup("Meu modelo");
        assertEquals(b.id, armazem.atual().origem);
        assertEquals(b.id, armazem.backupComMesmosArquivos().id);
        Files.writeString(armazem.conversaAtual().toPath(), "[{\"u\": true, \"t\": \"oi\"}]");
        assertEquals(b.id, armazem.backupComMesmosArquivos().id);  // a conversa não conta mais
        armazem.apelidar(null, "  Laika esperta ");
        assertEquals("Laika esperta", armazem.atual().nomeExibido());
        assertEquals("Laika esperta", armazem.backup(b.id).apelido);
        assertEquals("Meu modelo", armazem.backup(b.id).nome);
        armazem.apelidar(b.id, "");
        assertNull(armazem.atual().apelido);
        assertEquals("Meu modelo", armazem.backup(b.id).nomeExibido());
        // Outro modelo na versão em uso: nenhum backup tem os mesmos arquivos.
        File tok = armazem.temporario("txt");
        Files.copy(new File(assets, "tokenizer.txt").toPath(), tok.toPath());
        java.util.Map<String, Armazem.Arquivo> trocas = new java.util.LinkedHashMap<>();
        trocas.put(Armazem.TOKENIZER, armazem.guardar(tok, "txt", "tokenizer.txt", "outro"));
        armazem.aplicar(trocas, null, null);
        assertNull(armazem.atual().origem);
        assertNull(armazem.backupComMesmosArquivos());
        armazem.apelidar(b.id, "Antigo");
        armazem.usarBackup(b.id);
        assertEquals("Antigo", armazem.atual().nomeExibido());
        assertEquals(b.id, armazem.backupComMesmosArquivos().id);
    }

    /** O resultado do treino no celular do app 1.1 vira um backup, sem trocar a versão em uso. */
    @Test
    void backupDeArquivosNaoTrocaAVersao() throws IOException {
        File chat = armazem.temporario("bin"), tok = armazem.temporario("txt");
        Files.copy(new File(assets, "laika_chat.bin").toPath(), chat.toPath());
        Files.copy(new File(assets, "tokenizer.txt").toPath(), tok.toPath());
        java.util.Map<String, Armazem.Arquivo> a = new java.util.LinkedHashMap<>();
        a.put(Armazem.CHAT, armazem.guardar(chat, "bin", "laika_chat.bin", "chat"));
        a.put(Armazem.TOKENIZER, armazem.guardar(tok, "txt", "tokenizer.txt", "tokenizer"));
        String antes = armazem.atual().nome;
        Armazem.Versao b = armazem.backupDeArquivos("Treino no celular (app 1.1)", a);
        assertEquals(antes, armazem.atual().nome);
        List<Armazem.Versao> bs = armazem.backups();
        assertEquals(1, bs.size());
        assertEquals("Treino no celular (app 1.1)", bs.get(0).nome);
        assertEquals(Armazem.INDICE_FABRICA, bs.get(0).arquivos.get(Armazem.INDICE).ref);
        armazem.usarBackup(b.id);
        assertEquals("Treino no celular (app 1.1)", armazem.atual().nome);
    }

    @Test
    void zipSoComTextosTrocaSoOIndice() throws Exception {
        byte[] z = zip("LLM_Laika/data/wiki/wiki_000.txt", WIKI, "LLM_Laika/data/books/titulos.tsv", "1\tLivro\n");
        Corpus corpus = new Corpus(new File(tmp, "corpus"));
        Pacote p = Pacote.extrair(fluxo(z), z.length, armazem, corpus, null);
        assertTrue(p.entradas.isEmpty());
        assertEquals(1, p.textos);
        assertTrue(new File(corpus.pasta("books"), "titulos.tsv").exists());
        Importador.Resultado r = new Importador(armazem, PacoteTest::trechos).importar(List.of(indice(corpus)));
        assertEquals(List.of(Armazem.INDICE), new ArrayList<>(r.trocas.keySet()));
    }
}
