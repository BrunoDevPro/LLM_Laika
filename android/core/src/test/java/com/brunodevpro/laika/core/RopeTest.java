package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

/**
 * O modelo com RoPE (formato LAIKA002, o preset de 100M) contra o PyTorch, com os pesos em float32 e
 * em float16 (modo compacto). As referências vêm de `referencias.py --rope <checkpoint tiny_rope>`.
 */
class RopeTest {
    static final File PASTA = new File(System.getProperty("laika.referencias", "build/referencias"), "rope");

    @Test
    void logitsEGeracaoIguaisAoPyTorch() throws IOException {
        assumeTrue(new File(PASTA, "rope.jsonl").exists(), "rode referencias.py --rope antes");
        List<String> linhas = Files.readAllLines(new File(PASTA, "rope.jsonl").toPath(), StandardCharsets.UTF_8);
        for (boolean compacto : new boolean[]{false, true}) {
            Modelo m = new Modelo(new FileInputStream(new File(PASTA, "rope.bin")), 4, compacto);
            assertTrue(m.rope);
            double pior = 0;
            for (String linha : linhas) {
                @SuppressWarnings("unchecked") Map<String, Object> c = (Map<String, Object>) Json.ler(linha);
                int[] ids = ComparaComPythonTest.ints(c.get("ids"));
                // Tudo de uma vez e token a token (cache que cresce) dão os mesmos logits do PyTorch.
                float[] juntos = m.avancar(m.novoCache(), ids, 0, ids.length);
                Modelo.Cache cache = m.novoCache();
                float[] passo = null;
                for (int i = 0; i < ids.length; i++) passo = m.avancar(cache, ids, i, i + 1);
                List<?> esperado = (List<?>) c.get("logits");
                for (int v = 0; v < esperado.size(); v++) {
                    double e = (Double) esperado.get(v);
                    pior = Math.max(pior, Math.max(Math.abs(e - juntos[v]), Math.abs(e - passo[v])));
                }
                int[] guloso = ComparaComPythonTest.ints(c.get("guloso"));
                int[] seq = Arrays.copyOf(ids, ids.length + guloso.length);
                int n = ids.length;
                Modelo.Cache k = m.novoCache();
                for (int g = 0; g < guloso.length; g++) {
                    float[] lg;
                    if (n <= m.block) {
                        lg = m.avancar(k, seq, k.tamanho(), n);
                    } else {
                        k.limpar();
                        lg = m.avancar(k, seq, n - m.block, n);
                    }
                    int arg = 0;
                    for (int v = 1; v < lg.length; v++) if (lg[v] > lg[arg]) arg = v;
                    seq[n++] = arg;
                }
                assertEquals(Arrays.toString(guloso), Arrays.toString(Arrays.copyOfRange(seq, ids.length, n)),
                        "guloso (compacto=" + compacto + ", " + ids.length + " tokens)");
            }
            m.fechar();
            System.out.printf("RoPE (compacto=%s): maior diferença de logit para o PyTorch = %.2e%n", compacto, pior);
            assertTrue(pior < 2e-3, "logits diferentes do PyTorch: " + pior);
        }
    }

    @Test
    void conversorIgualAoExportador() throws IOException {
        assumeTrue(new File(PASTA, "modelo.pt").exists(), "rode referencias.py --rope antes");
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ConversorPt.Info info = ConversorPt.converter(new File(PASTA, "modelo.pt"), out);
        assertTrue(info.rope);
        assertArrayEquals(Files.readAllBytes(new File(PASTA, "rope.bin").toPath()), out.toByteArray(),
                "o .bin convertido no celular tem que ser igual ao do exportar_modelo.py");
        ConversorPt.Info lido = ConversorPt.lerBin(new FileInputStream(new File(PASTA, "rope.bin")));
        assertTrue(lido.rope);
        assertEquals(info.parametros, lido.parametros);
        assertTrue(lido.descricao().contains("RoPE"));
    }
}
