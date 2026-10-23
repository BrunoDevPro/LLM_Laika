package com.brunodevpro.laika.core.treino;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.SQLiteStatement;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.ConversorPt;
import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.Laika;
import com.brunodevpro.laika.core.Modelo;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * O caminho do Colab inteiro no "celular" (Mesa no lugar da GPU): índice do RAG (comparado
 * com o do rag.py), tokenizer do zero, pré-treino com parada e retomada, e fine-tuning.
 */
class PipelineTest {
    static File assets = new File(System.getProperty("laika.assets", "../app/src/main/assets"));
    static File repo = new File(System.getProperty("laika.repo", "../.."));
    static File livros = new File(System.getProperty("laika.livros", "none"));
    static Gl gl;

    @TempDir
    File tmp;

    @BeforeAll
    static void abrir() {
        try {
            gl = new GlMesa();
        } catch (Throwable e) {
            assumeTrue(false, "sem OpenGL ES no PC: " + e);
        }
    }

    @AfterAll
    static void fechar() {
        if (gl != null) gl.fechar();
    }

    /** Corpus de teste: data/modern + data/qa do repositório e o livro do índice pequeno. */
    Corpus corpus(boolean poucasPerguntas) throws IOException {
        Corpus c = new Corpus(new File(tmp, "dados"));
        for (File f : new File(repo, "data/modern").listFiles()) Files.copy(f.toPath(), new File(c.pasta("modern"), f.getName()).toPath());
        for (File f : new File(repo, "data/qa").listFiles()) {
            if (poucasPerguntas && f.getName().equals("pergeresp.txt")) continue;  // deixa o teste rápido no Mesa
            Files.copy(f.toPath(), new File(c.pasta("qa"), f.getName()).toPath());
        }
        if (livros.isDirectory()) {
            for (File f : livros.listFiles()) Files.copy(f.toPath(), new File(c.pasta("books"), f.getName()).toPath());
        }
        return c;
    }

    @Test
    void indiceIgualAoDoRagPy() throws Exception {
        assumeTrue(livros.isDirectory() && new File(assets, "laika_rag_mini.db").exists());
        Corpus c = corpus(false);
        File db = new File(tmp, "indice.db");
        BundledSQLiteDriver drv = new BundledSQLiteDriver();
        SQLiteConnection con = drv.open(db.getPath());
        long n = ConstrutorIndice.construir(c, con, Registro.CONSOLE);
        con.close();
        List<String> meu = linhas(drv, db), py = linhas(drv, new File(assets, "laika_rag_mini.db"));
        assertEquals(py.size(), meu.size());
        for (int i = 0; i < py.size(); i++) assertEquals(py.get(i), meu.get(i), "trecho " + i);
        assertEquals(n, meu.size());
        try (IndiceRag r = new IndiceRag(drv.open(db.getPath()))) {
            assertNotNull(r.melhor("O que são os dinossauros?"));
        }
    }

    static List<String> linhas(BundledSQLiteDriver drv, File db) {
        List<String> r = new ArrayList<>();
        SQLiteConnection c = drv.open(db.getPath());
        try (SQLiteStatement st = c.prepare("SELECT title, text, kind, pos FROM passages ORDER BY rowid")) {
            while (st.step()) r.add(st.getText(0) + "\u0001" + st.getText(1) + "\u0001" + st.getText(2) + "\u0001" + st.getLong(3));
        }
        c.close();
        return r;
    }

    /** Registro que pede para parar depois de n chamadas de parar() no pré-treino. */
    static Registro pararDepois(int n, List<String> log) {
        AtomicInteger c = new AtomicInteger();
        return new Registro() {
            public void log(String l) {
                System.out.println(l);
                log.add(l);
            }

            public void progresso(double f, String t) {
            }

            public boolean parar() {
                return n > 0 && c.incrementAndGet() > n;
            }
        };
    }

    @Test
    void doZeroAteOChat() throws Exception {
        Corpus c = corpus(true);
        File pasta = new File(tmp, "treino");
        PreTreino.Opcoes op = new PreTreino.Opcoes();
        op.modo = PreTreino.Modo.DO_ZERO;
        op.preset = "tiny";
        op.maxSteps = 12;
        op.evalEvery = 4;
        op.evalIters = 2;
        op.microLote = 8;
        op.repetirModern = 3;

        // Para no meio...
        List<String> log1 = new ArrayList<>();
        assertThrows(Parado.class, () -> PreTreino.rodar(gl, c, pasta, op, pararDepois(290, log1)));
        String interrompido = PreTreino.interrompido(pasta);
        assertNotNull(interrompido, "deveria ter salvo o estado");
        System.out.println("interrompido: " + interrompido);
        // ...e retoma de onde parou.
        PreTreino.Opcoes op2 = new PreTreino.Opcoes();
        op2.modo = PreTreino.Modo.RETOMAR;
        op2.evalEvery = 4;
        op2.evalIters = 2;
        List<String> log2 = new ArrayList<>();
        PreTreino.rodar(gl, c, pasta, op2, pararDepois(0, log2));
        assertNull(PreTreino.interrompido(pasta));
        assertTrue(log2.stream().anyMatch(l -> l.startsWith("Retomando do passo")));
        double primeira = valLoss(log1.stream().filter(l -> l.contains("val loss")).findFirst().get());
        String ultimaLinha = log2.stream().filter(l -> l.contains("val loss") && l.startsWith("step")).reduce((a, b) -> b).get();
        double ultima = valLoss(ultimaLinha);
        System.out.printf("val loss: %.3f -> %.3f%n", primeira, ultima);
        assertTrue(ultima < primeira - 0.1, "o pré-treino não aprendeu");

        File base = new File(pasta, "saida/laika_base.bin");
        ConversorPt.Info info;
        try (FileInputStream in = new FileInputStream(base)) {
            info = ConversorPt.lerBin(in);
        }
        assertEquals(false, info.finetuned);
        assertEquals(4000, info.vocab);

        // Fine-tuning a partir do pré-treino, com o índice do RAG.
        FineTuning.Opcoes f = new FineTuning.Opcoes();
        f.epocas = 1;
        f.sinteticos = 120;
        f.batch = 16;
        f.microLote = 8;
        f.maxTextoMb = 1;
        f.base = new FileInputStream(base);
        f.tokenizer = Files.readString(new File(pasta, "saida/tokenizer.txt").toPath());
        File db = new File(tmp, "mini.db");
        Files.copy(new File(assets, "laika_rag_mini.db").toPath(), db.toPath(), StandardCopyOption.REPLACE_EXISTING);
        f.rag = new IndiceRag(new BundledSQLiteDriver().open(db.getPath()));
        List<String> log3 = new ArrayList<>();
        FineTuning.rodar(gl, c, pasta, f, pararDepois(0, log3));
        assertTrue(log3.stream().anyMatch(l -> l.contains("<- melhor, salvo")));
        File chat = new File(pasta, "saida/laika_chat.bin");
        try (FileInputStream in = new FileInputStream(chat)) {
            assertTrue(ConversorPt.lerBin(in).finetuned);
        }
        // O resultado roda no motor de conversa do app.
        Tokenizador tok = new Tokenizador(new FileInputStream(new File(pasta, "saida/tokenizer.txt")));
        Modelo m = new Modelo(new FileInputStream(chat), 2);
        String r = new Laika(m, tok).gerar("<|user|> Oi <|assistant|>", new Laika.Opcoes(), true, new Random(1), null, null);
        System.out.println("Resposta do modelo treinado no 'celular': " + r);
        m.fechar();
    }

    static double valLoss(String linha) {
        int i = linha.indexOf("val loss ") + 9;
        return Double.parseDouble(linha.substring(i, linha.indexOf(' ', i)));
    }
}
