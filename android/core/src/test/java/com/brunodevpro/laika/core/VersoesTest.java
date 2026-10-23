package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * Conversão dos .pt/tokenizer.json no próprio app (comparada com o exportar_modelo.py),
 * versões, backups, exportação/importação e a checagem de compatibilidade.
 * Precisa dos checkpoints (propriedade laika.checkpoints) e dos assets exportados.
 */
class VersoesTest {
    static File assets = new File(System.getProperty("laika.assets", "../app/src/main/assets"));
    static File ck = new File(System.getProperty("laika.checkpoints", "none"));

    @TempDir
    File tmp;
    Armazem armazem;

    final Armazem.Fabrica fabrica = new Armazem.Fabrica() {
        public InputStream abrir(String nome) throws IOException {
            return new FileInputStream(new File(assets, nome));
        }

        public boolean existe(String nome) {
            return new File(assets, nome).exists();
        }
    };

    static long trechos(File db) {
        SQLiteConnection c = new BundledSQLiteDriver().open(db.getPath());
        try (IndiceRag r = new IndiceRag(c)) {
            return r.contarTrechos();
        }
    }

    @BeforeEach
    void preparar() throws IOException {
        assumeTrue(new File(ck, "finetuned.pt").exists() && new File(assets, "laika_chat.bin").exists(),
                "defina LAIKA_CHECKPOINTS e rode exportar_modelo.py");
        armazem = new Armazem(new File(tmp, "laika"), fabrica);
    }

    /** Copia um arquivo para a pasta temporária do armazém, como o app faz com o que vem do seletor. */
    Importador.Entrada entrada(File origem, String nome) throws IOException {
        File t = armazem.temporario("x");
        Files.copy(origem.toPath(), t.toPath());
        return new Importador.Entrada(t, nome);
    }

    byte[] bytes(Armazem.Arquivo a) throws IOException {
        try (InputStream in = armazem.abrir(a.ref)) {
            return in.readAllBytes();
        }
    }

    @Test
    void conversoresIguaisAoPython() throws IOException {
        for (String[] par : new String[][]{{"finetuned.pt", "laika_chat.bin"}, {"pretrain_best.pt", "laika_base.bin"}}) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            ConversorPt.Info info = ConversorPt.converter(new File(ck, par[0]), out);
            assertArrayEquals(Files.readAllBytes(new File(assets, par[1]).toPath()), out.toByteArray(), par[0]);
            ConversorPt.Info lido = ConversorPt.lerBin(new ByteArrayInputStream(out.toByteArray()));
            assertEquals(info.parametros, lido.parametros);
            assertEquals(info.valLoss, lido.valLoss);
            assertEquals(info.finetuned, lido.finetuned);
            System.out.println(par[0] + ": " + info.descricao() + (info.finetuned ? " (chat)" : " (base)"));
        }
        try (InputStream in = new FileInputStream(new File(ck, "tokenizer.json"))) {
            assertEquals(Files.readString(new File(assets, "tokenizer.txt").toPath()), ConversorTokenizer.converter(in));
        }
        // float16: casos de arredondamento (par mais próximo, subnormais, infinito)
        for (float f : new float[]{0f, -0f, 1f, 65504f, 65520f, 1e-8f, 5.96e-8f, 2.98e-8f, 6.1e-5f, 0.1f, 1.0009765f, 1.00146484375f}) {
            float volta = Modelo.meiaParaFloat(ConversorPt.paraMeia(f));
            assertTrue(Math.abs(volta - f) <= Math.max(Math.abs(f) * 1e-3, 6e-8) || Float.isInfinite(volta), "meia " + f);
        }
    }

    @Test
    void atualizacaoBackupsEExportacao() throws Exception {
        Armazem.Versao fab = armazem.atual();
        assertEquals("Versão de fábrica", fab.nome);
        assertTrue(fab.arquivos.get(Armazem.CHAT).descricao.contains("val loss 2,115")
                || fab.arquivos.get(Armazem.CHAT).descricao.contains("val loss 2.115"), fab.arquivos.get(Armazem.CHAT).descricao);
        Files.writeString(armazem.memoriaAtual().toPath(), "{\"nome\": \"Bruno\", \"notas\": [\"x\"]}");

        // Atualização com os arquivos do Drive (pt + tokenizer.json + índice + memória).
        File mem = new File(tmp, "memoria.json");
        Files.writeString(mem.toPath(), "{\"nome\": \"Ana\", \"gostos\": [\"de futebol\"], \"notas\": []}");
        List<Importador.Entrada> es = new ArrayList<>(Arrays.asList(
                entrada(new File(ck, "finetuned.pt"), "finetuned.pt"),
                entrada(new File(ck, "pretrain_best.pt"), "pretrain_best (1).pt"),
                entrada(new File(ck, "tokenizer.json"), "tokenizer.json"),
                entrada(new File(assets, "laika_rag_mini.db"), "laika_rag.db"),
                entrada(mem, "memoria.json")));
        Importador imp = new Importador(armazem, VersoesTest::trechos);
        Importador.Resultado r = imp.importar(es);
        assertEquals(4, r.trocas.size(), r.feitos.toString());
        assertTrue(r.mudaVersao());
        assertTrue(r.avisos.isEmpty(), r.avisos.toString());
        assertTrue(r.trocas.get(Armazem.INDICE).descricao.contains("2"), r.trocas.get(Armazem.INDICE).descricao);
        for (Importador.Entrada e : es) assertFalse(e.arquivo.exists(), "temporário apagado");

        Armazem.Versao antes = armazem.fazerBackup("Antes da atualização");
        assertNotNull(armazem.backupIgualAoAtual());
        armazem.aplicar(r.trocas, "Atualização de teste", r.memoria);
        assertNull(armazem.backupIgualAoAtual());
        Armazem.Versao nova = armazem.atual();
        assertEquals("Atualização de teste", nova.nome);
        assertEquals("Ana · 1 fato", nova.resumoMemoria());
        assertEquals("Bruno · 1 anotação", armazem.backup(antes.id).resumoMemoria());
        // Os arquivos convertidos no "celular" são idênticos aos do exportar_modelo.py.
        assertArrayEquals(Files.readAllBytes(new File(assets, "laika_chat.bin").toPath()), bytes(nova.arquivos.get(Armazem.CHAT)));
        assertArrayEquals(Files.readAllBytes(new File(assets, "laika_base.bin").toPath()), bytes(nova.arquivos.get(Armazem.BASE)));
        assertArrayEquals(Files.readAllBytes(new File(assets, "tokenizer.txt").toPath()), bytes(nova.arquivos.get(Armazem.TOKENIZER)));

        // Renomear, backup da nova, exportar e importar de volta.
        armazem.renomear(antes.id, "Fábrica (Bruno)");
        assertEquals("Fábrica (Bruno)", armazem.backup(antes.id).nome);
        Files.writeString(armazem.conversaAtual().toPath(), "[{\"u\": true, \"t\": \"oi\"}]");
        Armazem.Versao b2 = armazem.fazerBackup("Com conversa");
        assertEquals(1, b2.mensagens());
        ByteArrayOutputStream zip = new ByteArrayOutputStream();
        long[] ultimo = {0};
        armazem.exportar(b2.id, zip, true, (feito, total) -> ultimo[0] = feito);
        assertTrue(ultimo[0] > 27_000_000L, "progresso " + ultimo[0]);
        armazem.apagar(b2.id);
        Armazem.Versao volta = armazem.importarBackup(new ByteArrayInputStream(zip.toByteArray()), zip.size(), null);
        assertEquals("Com conversa", volta.nome);
        assertEquals(1, volta.mensagens());
        assertEquals("Ana · 1 fato", volta.resumoMemoria());
        for (String papel : Armazem.PAPEIS) {
            assertArrayEquals(bytes(nova.arquivos.get(papel)), bytes(volta.arquivos.get(papel)), papel);
        }
        // O mesmo .zip também entra pelo Importador (reconhecido pelo conteúdo).
        File z = new File(tmp, "backup.zip");
        Files.write(z.toPath(), zip.toByteArray());
        Importador.Resultado rz = imp.importar(List.of(entrada(z, "Laika backup.zip")));
        assertEquals(1, rz.backupsImportados.size());
        assertFalse(rz.mudaVersao());

        // Voltar para o backup da fábrica: o modelo volta a ser o do APK.
        armazem.usarBackup(antes.id);
        assertEquals("fabrica:laika_chat.bin", armazem.atual().arquivos.get(Armazem.CHAT).ref);
        assertEquals("Bruno · 1 anotação", armazem.atual().resumoMemoria());
        assertNotNull(armazem.backupIgualAoAtual());

        // Limpeza: só ficam os blobs que algum backup usa.
        for (Armazem.Versao b : armazem.backups()) if (!b.id.equals(antes.id)) armazem.apagar(b.id);
        File[] blobs = new File(tmp, "laika/blobs").listFiles();
        assertEquals(0, blobs.length, Arrays.toString(blobs));
        assertEquals(1, armazem.backups().size());
    }

    @Test
    void recusaArquivosQueNaoCombinam() throws Exception {
        Importador imp = new Importador(armazem, VersoesTest::trechos);
        // Tokenizer de outro tamanho sem o modelo novo.
        File tok = new File(tmp, "tokenizer.txt");
        Files.writeString(tok.toPath(), "vocab 3\na\nb\nc\nspecial 0\nmerges 0\n");
        IOException e = assertThrows(IOException.class, () -> imp.importar(List.of(entrada(tok, "tokenizer.txt"))));
        assertTrue(e.getMessage().contains("não combina"), e.getMessage());
        assertEquals("Versão de fábrica", armazem.atual().nome);
        assertEquals(0, new File(tmp, "laika/blobs").listFiles().length);

        File lixo = new File(tmp, "foto.jpg");
        Files.write(lixo.toPath(), new byte[]{(byte) 0xFF, (byte) 0xD8, 1, 2, 3});
        e = assertThrows(IOException.class, () -> imp.importar(List.of(entrada(lixo, "foto.jpg"))));
        assertTrue(e.getMessage().contains("não reconhecido"), e.getMessage());

        File db = new File(tmp, "outro.db");
        SQLiteConnection c = new BundledSQLiteDriver().open(db.getPath());
        try (var st = c.prepare("CREATE TABLE x(a)")) {
            st.step();
        }
        c.close();
        e = assertThrows(IOException.class, () -> imp.importar(List.of(entrada(db, "outro.db"))));
        assertTrue(e.getMessage().contains("não é um índice"), e.getMessage());
    }
}
