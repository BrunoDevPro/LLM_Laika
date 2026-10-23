package com.brunodevpro.laika.core.dados;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.SQLiteStatement;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.IndiceRag;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * O índice montado no celular (ConstrutorIndice) é igual ao do "python rag.py build":
 * compara com o laika_rag_mini.db gerado pelo exportar_modelo.py (data/modern + o livro de LAIKA_LIVROS).
 */
class IndiceTest {
    static File assets = new File(System.getProperty("laika.assets", "../app/src/main/assets"));
    static File repo = new File(System.getProperty("laika.repo", "../.."));
    static File livros = new File(System.getProperty("laika.livros", "none"));

    @TempDir
    File tmp;

    Corpus corpus() throws IOException {
        Corpus c = new Corpus(new File(tmp, "dados"));
        for (File f : new File(repo, "data/modern").listFiles()) {
            Files.copy(f.toPath(), new File(c.pasta("modern"), f.getName()).toPath());
        }
        if (livros.isDirectory()) {
            for (File f : livros.listFiles()) Files.copy(f.toPath(), new File(c.pasta("books"), f.getName()).toPath());
        }
        return c;
    }

    @Test
    void indiceIgualAoDoRagPy() throws Exception {
        assumeTrue(livros.isDirectory() && new File(assets, "laika_rag_mini.db").exists());
        Corpus c = corpus();
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

    @Test
    void cancelar() throws Exception {
        Corpus c = corpus();
        SQLiteConnection con = new BundledSQLiteDriver().open(new File(tmp, "parado.db").getPath());
        Registro parar = new Registro() {
            public void log(String l) {
            }

            public void progresso(double f, String t) {
            }

            public boolean parar() {
                return true;
            }
        };
        assertThrows(Parado.class, () -> ConstrutorIndice.construir(c, con, parar));
        con.close();
    }

    @Test
    void destinoDosTextos() {
        Corpus c = new Corpus(new File(tmp, "c"));
        assertEquals(new File(c.pasta("books"), "gutenberg_1.txt"), c.destino("LLM_Laika/data/books/gutenberg_1.txt"));
        assertEquals(new File(c.pasta("books"), "titulos.tsv"), c.destino("books/titulos.tsv"));
        assertEquals(new File(c.pasta("wiki"), "wiki_000.txt"), c.destino("wiki\\wiki_000.txt"));
        assertNull(c.destino("qa/pergeresp.txt"));
        assertNull(c.destino("modern/.oculto.txt"));
        assertNull(c.destino("finetuned.pt"));
        assertNull(c.destino("wiki/titulos.tsv"));
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
}
