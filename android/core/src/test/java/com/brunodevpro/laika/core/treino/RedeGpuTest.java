package com.brunodevpro.laika.core.treino;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import com.brunodevpro.laika.core.Json;

import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Os shaders do treino contra o PyTorch (referencias_treino.py): perda, gradientes de todos
 * os parâmetros, norma do gradiente e o passo do AdamW. Roda no Mesa (GPU por software).
 */
class RedeGpuTest {
    static File refs = new File(System.getProperty("laika.referencias", "build/referencias"));
    static Gl gl;

    @BeforeAll
    static void abrir() {
        assumeTrue(new File(refs, "treino_pequeno.json").exists(), "rode referencias_treino.py");
        try {
            gl = new GlMesa();
        } catch (Throwable e) {
            e.printStackTrace();
            assumeTrue(false, "sem OpenGL ES no PC (instale o Mesa): " + e);
        }
        System.out.println("GPU de teste: " + gl.descricao());
    }

    @AfterAll
    static void fechar() {
        if (gl != null) gl.fechar();
    }

    static float[] f32(String nome) throws IOException {
        ByteBuffer b = ByteBuffer.wrap(Files.readAllBytes(new File(refs, nome).toPath())).order(ByteOrder.LITTLE_ENDIAN);
        float[] r = new float[b.remaining() / 4];
        b.asFloatBuffer().get(r);
        return r;
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> meta(String caso) throws IOException {
        return (Map<String, Object>) Json.ler(Files.readString(new File(refs, "treino_" + caso + ".json").toPath()));
    }

    static int[] ints(Object o) {
        List<?> l = (List<?>) o;
        int[] r = new int[l.size()];
        for (int i = 0; i < r.length; i++) r[i] = ((Number) l.get(i)).intValue();
        return r;
    }

    static int n(Map<String, Object> m, String k) {
        return ((Number) m.get(k)).intValue();
    }

    @SuppressWarnings("unchecked")
    static Rede.Config config(Map<String, Object> meta, float dropout) {
        Map<String, Object> c = (Map<String, Object>) meta.get("cfg");
        return new Rede.Config(n(c, "vocab_size"), n(c, "block_size"), n(c, "embed_size"), n(c, "heads"), n(c, "layers"), dropout);
    }

    /** Maior diferença relativa ao maior valor absoluto (as contas na GPU somam em outra ordem). */
    static double diferenca(float[] a, float[] b) {
        double max = 1e-12, d = 0;
        for (int i = 0; i < a.length; i++) {
            max = Math.max(max, Math.abs(a[i]));
            d = Math.max(d, Math.abs(a[i] - b[i]));
        }
        return d / max;
    }

    void conferir(String caso, int microLotes) throws IOException {
        Map<String, Object> m = meta(caso);
        int B = n(m, "B"), T = n(m, "T");
        int[] tok = ints(m.get("tokens")), alvo = ints(m.get("alvos"));
        int validos = 0;
        for (int a : alvo) if (a >= 0) validos++;
        float escala = 1f / validos;
        int porMicro = B / microLotes;
        try (Rede r = new Rede(gl, config(m, 0f), porMicro)) {
            r.carregar(f32("treino_" + caso + "_pesos0.f32"));
            r.zerarGradientes();
            double perda = 0;
            for (int u = 0; u < microLotes; u++) {
                int[] t = java.util.Arrays.copyOfRange(tok, u * porMicro * T, (u + 1) * porMicro * T);
                int[] a = java.util.Arrays.copyOfRange(alvo, u * porMicro * T, (u + 1) * porMicro * T);
                for (float p : r.microPasso(t, a, porMicro, T, true, escala, 7)) perda += p;
            }
            perda /= validos;
            double esperada = ((Number) m.get("perda")).doubleValue();
            System.out.printf("%s (%d micro-lotes): perda %.6f (PyTorch %.6f)%n", caso, microLotes, perda, esperada);
            assertEquals(esperada, perda, 1e-4);

            float[] g = r.gradientes(), ge = f32("treino_" + caso + "_grads.f32");
            for (Rede.Pedaco pd : r.pedacos) {
                float[] a = java.util.Arrays.copyOfRange(g, pd.inicio, pd.inicio + pd.tamanho);
                float[] e = java.util.Arrays.copyOfRange(ge, pd.inicio, pd.inicio + pd.tamanho);
                double d = diferenca(e, a);
                assertTrue(d < 2e-4, pd.nome + ": gradiente difere " + d);
            }
            float norma = r.otimizar(((Number) m.get("lr")).floatValue(), ((Number) m.get("wd_matriz")).floatValue(),
                    ((Number) m.get("wd_vetor")).floatValue(), ((Number) m.get("b1")).floatValue(),
                    ((Number) m.get("b2")).floatValue(), 1e-8f, ((Number) m.get("clip")).floatValue(), 1);
            assertEquals(((Number) m.get("norma")).doubleValue(), norma, 1e-3 * norma);
            float[] p1 = r.pesos(), e1 = f32("treino_" + caso + "_pesos1.f32"), p0 = f32("treino_" + caso + "_pesos0.f32");
            // Compara o quanto cada peso andou (o passo é pequeno perto do peso).
            float[] passoA = new float[p1.length], passoE = new float[p1.length];
            for (int i = 0; i < p1.length; i++) {
                passoA[i] = p1[i] - p0[i];
                passoE[i] = e1[i] - p0[i];
            }
            double d = diferenca(passoE, passoA);
            System.out.printf("   norma %.5f, passo do AdamW difere %.2e%n", norma, d);
            assertTrue(d < 5e-3, "passo do AdamW difere " + d);
        }
    }

    @Test
    void gradientesIguaisAoPyTorch() throws IOException {
        conferir("pequeno", 1);
        conferir("cabeca64", 1);
    }

    @Test
    void acumulacaoDeGradiente() throws IOException {
        conferir("pequeno", 3);  // 3 micro-lotes de 1 sequência = 1 lote de 3
        conferir("cabeca64", 2);
    }

    /** Com dropout não dá para comparar com o PyTorch (outra máscara): confere o gradiente por diferenças finitas. */
    @Test
    void dropoutGradienteNumerico() throws IOException {
        Map<String, Object> m = meta("pequeno");
        int B = n(m, "B"), T = n(m, "T");
        int[] tok = ints(m.get("tokens")), alvo = ints(m.get("alvos"));
        int validos = 0;
        for (int a : alvo) if (a >= 0) validos++;
        float escala = 1f / validos;
        try (Rede r = new Rede(gl, config(m, 0.3f), B)) {
            float[] p0 = f32("treino_pequeno_pesos0.f32");
            r.carregar(p0);
            r.zerarGradientes();
            r.microPasso(tok, alvo, B, T, true, escala, 11);
            float[] g = r.gradientes();
            int[] testar = {5, 1700, 2000, 2100, 3000, 6000, 9000, 15000, p0.length - 40, p0.length - 3};
            double eps = 3e-3;
            int bons = 0;
            for (int i : testar) {
                float[] p = p0.clone();
                p[i] += eps;
                r.carregar(p);
                double mais = soma(r.microPasso(tok, alvo, B, T, true, escala, 11)) * escala;
                p[i] -= 2 * eps;
                r.carregar(p);
                double menos = soma(r.microPasso(tok, alvo, B, T, true, escala, 11)) * escala;
                double num = (mais - menos) / (2 * eps);
                boolean ok = Math.abs(num - g[i]) <= 0.05 * Math.max(Math.abs(num), Math.abs(g[i])) + 2e-4;
                System.out.printf("   dropout: parâmetro %d: analítico %.6f, numérico %.6f%s%n", i, g[i], num, ok ? "" : "  <-- !");
                if (ok) bons++;
            }
            assertTrue(bons >= testar.length - 1, "gradiente com dropout não bate");
            // Sem treino (validação) não há dropout: a perda é a mesma de sempre.
            r.carregar(p0);
            float[] a = r.microPasso(tok, alvo, B, T, false, escala, 11), b = r.microPasso(tok, alvo, B, T, false, escala, 99);
            assertArrayEquals(a, b);
        }
    }

    static double soma(float[] v) {
        double s = 0;
        for (float x : v) s += x;
        return s;
    }
}
