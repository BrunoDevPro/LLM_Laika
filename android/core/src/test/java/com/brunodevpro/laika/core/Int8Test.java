package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Random;

import org.junit.jupiter.api.Test;

/**
 * Os pesos em int8 (uma escala por linha) contra o mesmo modelo em float32, com pesos sorteados (não precisa de
 * checkpoint). LAIKA_BENCH=1 mede também a velocidade num modelo do tamanho do de 100M.
 */
class Int8Test {
    /** float32 -> float16 (os valores sorteados são normais, sem subnormais nem infinitos). */
    static short meia(float v) {
        int b = Float.floatToIntBits(v), sinal = (b >>> 16) & 0x8000, exp = ((b >>> 23) & 0xFF) - 127 + 15;
        if (exp <= 0) return (short) sinal;
        return (short) (sinal | (exp << 10) | ((b >>> 13) & 0x3FF));
    }

    /** Um laika_*.bin (LAIKA001) com pesos ~N(0, desvio) e LayerNorm perto de 1. */
    static byte[] modeloSorteado(int vocab, int block, int dim, int heads, int layers, long semente) throws IOException {
        Random r = new Random(semente);
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        out.write("LAIKA001".getBytes("US-ASCII"));
        ByteBuffer cab = ByteBuffer.allocate(20).order(ByteOrder.LITTLE_ENDIAN);
        cab.putInt(vocab).putInt(block).putInt(dim).putInt(heads).putInt(layers);
        out.write(cab.array());
        float desvio = (float) (1 / Math.sqrt(dim));
        Escritor w = (n, base, ruido) -> {
            ByteBuffer b = ByteBuffer.allocate(n * 2).order(ByteOrder.LITTLE_ENDIAN);
            for (int i = 0; i < n; i++) b.putShort(meia(base + ruido * (float) r.nextGaussian()));
            out.write(b.array());
        };
        w.escrever(vocab * dim, 0, 0.5f);
        w.escrever(block * dim, 0, 0.1f);
        for (int l = 0; l < layers; l++) {
            w.escrever(dim, 1, 0.05f);
            w.escrever(dim, 0, 0.05f);
            w.escrever(3 * dim * dim, 0, desvio);
            w.escrever(dim * dim, 0, desvio);
            w.escrever(dim, 1, 0.05f);
            w.escrever(dim, 0, 0.05f);
            w.escrever(4 * dim * dim, 0, desvio);
            w.escrever(4 * dim, 0, 0.02f);
            w.escrever(4 * dim * dim, 0, desvio / 2);
            w.escrever(dim, 0, 0.02f);
        }
        w.escrever(dim, 1, 0.05f);
        w.escrever(dim, 0, 0.05f);
        return out.toByteArray();
    }

    private interface Escritor {
        void escrever(int n, float base, float ruido) throws IOException;
    }

    static int maior(float[] v) {
        int m = 0;
        for (int i = 1; i < v.length; i++) if (v[i] > v[m]) m = i;
        return m;
    }

    @Test
    void int8PertoDoFloat32() throws IOException {
        byte[] bin = modeloSorteado(500, 64, 128, 4, 3, 7);
        Modelo f32 = new Modelo(new ByteArrayInputStream(bin), 2, false);
        Modelo q8 = new Modelo(new ByteArrayInputStream(bin), 2, false, true, true);
        assertTrue(q8.int8 && !q8.compacto && !f32.int8);
        // Pedido sem forçar: um modelo pequeno (abaixo de LIMITE_INT8) continua em float.
        assertFalse(new Modelo(new ByteArrayInputStream(bin), 2, false, true).int8);

        Random r = new Random(3);
        int[] ids = new int[40];
        for (int i = 0; i < ids.length; i++) ids[i] = r.nextInt(500);
        float[] a = f32.avancar(f32.novoCache(), ids, 0, ids.length);
        float[] b = q8.avancar(q8.novoCache(), ids, 0, ids.length);
        double erro = 0, escala = 0;
        for (int i = 0; i < a.length; i++) {
            erro = Math.max(erro, Math.abs(a[i] - b[i]));
            escala = Math.max(escala, Math.abs(a[i]));
        }
        System.out.printf("int8: maior diferença de logit %.4f (maior logit %.2f)%n", erro, escala);
        assertTrue(erro < 0.05 * escala, "int8 longe demais do float32: " + erro);
        assertTrue(maior(a) == maior(b), "o token mais provável mudou");

        // Token a token (cache, uma linha por vez com dotInt8) = tudo de uma vez (linha convertida para float).
        Modelo.Cache c = q8.novoCache();
        float[] passo = null;
        for (int i = 0; i < ids.length; i++) passo = q8.avancar(c, ids, i, i + 1);
        for (int i = 0; i < b.length; i++) {
            assertTrue(Math.abs(passo[i] - b[i]) < 1e-3, "cache diferente na posição " + i);
        }
        f32.fechar();
        q8.fechar();
    }

    @Test
    void velocidadeDo100M() throws IOException {
        assumeTrue(System.getenv("LAIKA_BENCH") != null, "LAIKA_BENCH=1 para medir");
        byte[] bin = modeloSorteado(24000, 256, 768, 12, 12, 11);
        int threads = Integer.parseInt(System.getenv().getOrDefault("LAIKA_BENCH_THREADS", "4"));
        for (boolean usarInt8 : new boolean[]{false, true}) {
            Modelo m = new Modelo(new ByteArrayInputStream(bin), threads, true, usarInt8);
            int[] ids = new int[200];
            for (int i = 0; i < ids.length; i++) ids[i] = (i * 37) % 24000;
            Modelo.Cache c = m.novoCache();
            long t0 = System.nanoTime();
            float[] l = m.avancar(c, ids, 0, ids.length);
            long t1 = System.nanoTime();
            int gerados = 50;
            for (int i = 0; i < gerados; i++) {
                ids[0] = maior(l);
                l = m.avancar(c, ids, 0, 1);
            }
            long t2 = System.nanoTime();
            System.out.printf("%s (%d núcleos): prompt de 200 tokens %.2f s, %.1f ms por token gerado%n",
                    usarInt8 ? "int8" : "float16", threads, (t1 - t0) / 1e9, (t2 - t1) / 1e6 / gerados);
            m.fechar();
        }
        assertArrayEquals(new int[0], new int[0]);
    }
}
