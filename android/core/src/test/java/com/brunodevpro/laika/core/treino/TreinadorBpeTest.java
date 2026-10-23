package com.brunodevpro.laika.core.treino;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import com.brunodevpro.laika.core.Tokenizador;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.jupiter.api.Test;

/** O TreinadorBpe contra o BpeTrainer da biblioteca tokenizers (mesmos arquivos, vocabulário 3000). */
class TreinadorBpeTest {
    static File refs = new File(System.getProperty("laika.referencias", "build/referencias"));

    @Test
    void igualAoTokenizersDoPython() throws Exception {
        assumeTrue(new File(refs, "bpe_ref.txt").exists(), "rode referencias_treino.py");
        List<File> arquivos = new ArrayList<>();
        for (String l : Files.readAllLines(new File(refs, "bpe_arquivos.txt").toPath())) arquivos.add(new File(l));
        long t0 = System.currentTimeMillis();
        String meu = TreinadorBpe.treinar(arquivos, 3000,
                Arrays.asList("[PAD]", "[UNK]", "<|user|>", "<|assistant|>", "<|end|>", "<|endoftext|>"), Long.MAX_VALUE,
                Registro.CONSOLE);
        System.out.println("treino do tokenizer: " + (System.currentTimeMillis() - t0) + " ms");
        String ref = Files.readString(new File(refs, "bpe_ref.txt").toPath());
        String[] a = ref.split("\n"), b = meu.split("\n");
        int iguais = 0;
        for (int i = 0; i < Math.min(a.length, b.length); i++) {
            if (!a[i].equals(b[i])) {
                System.out.println("primeira diferença na linha " + i + ": python '" + a[i] + "' x java '" + b[i] + "'");
                break;
            }
            iguais++;
        }
        assertEquals(a.length, b.length);
        assertEquals(a.length, iguais, "o tokenizer treinado difere do Python");
        // E ele funciona no Tokenizador do app.
        Tokenizador t = new Tokenizador(new ByteArrayInputStream(meu.getBytes(StandardCharsets.UTF_8)));
        int[] ids = t.codificar("<|user|> Quem foi Santos Dumont? <|assistant|>");
        assertEquals("<|user|> Quem foi Santos Dumont? <|assistant|>".replace("<|user|>", "").replace("<|assistant|>", ""),
                t.decodificar(ids));
        assertTrue(ids.length > 3);
    }
}
