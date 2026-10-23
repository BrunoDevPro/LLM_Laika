package com.brunodevpro.laika.core;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * O TinyLLM do model.py refeito em Java puro, com cache de atenção (KV cache).
 *
 * Mesma conta do PyTorch: embedding de token + posição aprendida, blocos com pré-LayerNorm,
 * atenção causal (8 cabeças), feed-forward com GELU exato, LayerNorm final e saída com os
 * pesos do embedding. Com o cache, cada token novo custa só a parte dele, em vez de
 * recalcular a frase inteira como o chat.py faz.
 *
 * As multiplicações de matriz são divididas entre os núcleos do processador.
 */
public final class Modelo {
    private static final float LN_EPS = 1e-5f;

    public final int vocab, block, dim, heads, layers, headDim;
    private final float[] tokEmb, posEmb, lnfW, lnfB;
    private final float[][] ln1W, ln1B, qkvW, projW, ln2W, ln2B, ff1W, ff1B, ff2W, ff2B;
    private final ExecutorService pool;
    private final int threads;

    /** Lê o laika_*.bin gerado por android/exportar_modelo.py. */
    public Modelo(InputStream in, int threads) throws IOException {
        DataInputStream d = new DataInputStream(new java.io.BufferedInputStream(in, 1 << 16));
        byte[] magic = new byte[8];
        d.readFully(magic);
        if (!new String(magic, "US-ASCII").equals("LAIKA001")) throw new IOException("arquivo de pesos inválido");
        byte[] cab = new byte[20];
        d.readFully(cab);
        ByteBuffer c = ByteBuffer.wrap(cab).order(ByteOrder.LITTLE_ENDIAN);
        vocab = c.getInt();
        block = c.getInt();
        dim = c.getInt();
        heads = c.getInt();
        layers = c.getInt();
        headDim = dim / heads;

        tokEmb = ler(d, vocab * dim);
        posEmb = ler(d, block * dim);
        ln1W = new float[layers][]; ln1B = new float[layers][]; qkvW = new float[layers][]; projW = new float[layers][];
        ln2W = new float[layers][]; ln2B = new float[layers][]; ff1W = new float[layers][]; ff1B = new float[layers][];
        ff2W = new float[layers][]; ff2B = new float[layers][];
        for (int l = 0; l < layers; l++) {
            ln1W[l] = ler(d, dim);
            ln1B[l] = ler(d, dim);
            qkvW[l] = ler(d, 3 * dim * dim);
            projW[l] = ler(d, dim * dim);
            ln2W[l] = ler(d, dim);
            ln2B[l] = ler(d, dim);
            ff1W[l] = ler(d, 4 * dim * dim);
            ff1B[l] = ler(d, 4 * dim);
            ff2W[l] = ler(d, 4 * dim * dim);
            ff2B[l] = ler(d, dim);
        }
        lnfW = ler(d, dim);
        lnfB = ler(d, dim);

        this.threads = Math.max(1, threads);
        pool = this.threads > 1 ? Executors.newFixedThreadPool(this.threads - 1, r -> {
            Thread t = new Thread(r, "laika-calculo");
            t.setDaemon(true);
            return t;
        }) : null;
    }

    /** Pesos em float16 (little-endian) -> float32. */
    private static float[] ler(DataInputStream d, int n) throws IOException {
        byte[] raw = new byte[n * 2];
        d.readFully(raw);
        ByteBuffer b = ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN);
        float[] out = new float[n];
        for (int i = 0; i < n; i++) out[i] = meiaParaFloat(b.getShort());
        return out;
    }

    public static float meiaParaFloat(short h) {
        int bits = h & 0xFFFF;
        int sinal = (bits >>> 15) << 31;
        int exp = (bits >>> 10) & 0x1F;
        int mant = bits & 0x3FF;
        if (exp == 0) {
            if (mant == 0) return Float.intBitsToFloat(sinal);
            float v = mant / 1024f * (float) Math.pow(2, -14);  // subnormal
            return sinal != 0 ? -v : v;
        }
        if (exp == 31) return Float.intBitsToFloat(sinal | 0x7F800000 | (mant << 13));
        return Float.intBitsToFloat(sinal | ((exp - 15 + 127) << 23) | (mant << 13));
    }

    public void fechar() {
        if (pool != null) pool.shutdownNow();
    }

    /** Cache de atenção de uma conversa: chaves e valores das posições já processadas. */
    public final class Cache {
        final float[][] k = new float[layers][block * dim];
        final float[][] v = new float[layers][block * dim];
        int tamanho = 0;

        public int tamanho() {
            return tamanho;
        }

        public void limpar() {
            tamanho = 0;
        }
    }

    public Cache novoCache() {
        return new Cache();
    }

    /**
     * Processa tokens[de..ate) a partir da posição cache.tamanho e devolve os logits do
     * último token (o próximo token mais provável). As chaves/valores ficam no cache.
     */
    public float[] avancar(Cache cache, int[] tokens, int de, int ate) {
        int t = ate - de, p0 = cache.tamanho;
        if (t <= 0) throw new IllegalArgumentException("nenhum token");
        if (p0 + t > block) throw new IllegalArgumentException("passou do block_size (" + block + ")");

        float[] x = new float[t * dim];
        for (int i = 0; i < t; i++) {
            int tok = tokens[de + i], pos = p0 + i;
            for (int j = 0; j < dim; j++) x[i * dim + j] = tokEmb[tok * dim + j] + posEmb[pos * dim + j];
        }
        float[] h = new float[t * dim];
        float[] qkv = new float[t * 3 * dim];
        float[] att = new float[t * dim];
        float[] tmp = new float[t * dim];
        float[] ff = new float[t * 4 * dim];

        for (int l = 0; l < layers; l++) {
            layerNorm(x, h, t, ln1W[l], ln1B[l]);
            matmul(h, t, dim, qkvW[l], null, 3 * dim, qkv);
            float[] kc = cache.k[l], vc = cache.v[l];
            for (int i = 0; i < t; i++) {
                System.arraycopy(qkv, i * 3 * dim + dim, kc, (p0 + i) * dim, dim);
                System.arraycopy(qkv, i * 3 * dim + 2 * dim, vc, (p0 + i) * dim, dim);
            }
            atencao(qkv, kc, vc, t, p0, att);
            matmul(att, t, dim, projW[l], null, dim, tmp);
            for (int i = 0; i < t * dim; i++) x[i] += tmp[i];

            layerNorm(x, h, t, ln2W[l], ln2B[l]);
            matmul(h, t, dim, ff1W[l], ff1B[l], 4 * dim, ff);
            for (int i = 0; i < ff.length; i++) ff[i] = gelu(ff[i]);
            matmul(ff, t, 4 * dim, ff2W[l], ff2B[l], dim, tmp);
            for (int i = 0; i < t * dim; i++) x[i] += tmp[i];
        }
        cache.tamanho = p0 + t;

        float[] ultimo = new float[dim];
        layerNorm(x, (t - 1) * dim, ultimo, 0, lnfW, lnfB);
        float[] logits = new float[vocab];
        matmul(ultimo, 1, dim, tokEmb, null, vocab, logits);
        return logits;
    }

    private void layerNorm(float[] x, float[] out, int t, float[] w, float[] b) {
        for (int i = 0; i < t; i++) layerNorm(x, i * dim, out, i * dim, w, b);
    }

    private void layerNorm(float[] x, int xo, float[] out, int oo, float[] w, float[] b) {
        float media = 0;
        for (int j = 0; j < dim; j++) media += x[xo + j];
        media /= dim;
        float var = 0;
        for (int j = 0; j < dim; j++) {
            float d = x[xo + j] - media;
            var += d * d;
        }
        float inv = (float) (1.0 / Math.sqrt(var / dim + LN_EPS));
        for (int j = 0; j < dim; j++) out[oo + j] = (x[xo + j] - media) * inv * w[j] + b[j];
    }

    /** Atenção causal: cada token novo olha para todas as posições até ele (no cache). */
    private void atencao(float[] qkv, float[] kc, float[] vc, int t, int p0, float[] out) {
        float escala = (float) (1.0 / Math.sqrt(headDim));
        paralelo(t * heads, t * heads * (p0 + t) * headDim >= 32768, (ini, fim) -> {
            float[] pesos = new float[p0 + t];
            for (int tarefa = ini; tarefa < fim; tarefa++) {
                int i = tarefa / heads, hd = tarefa % heads;
                int qo = i * 3 * dim + hd * headDim;
                int n = p0 + i + 1;  // posições visíveis (máscara causal)
                float max = Float.NEGATIVE_INFINITY;
                for (int s = 0; s < n; s++) {
                    float sc = escala * dot(qkv, qo, kc, s * dim + hd * headDim, headDim);
                    pesos[s] = sc;
                    if (sc > max) max = sc;
                }
                float soma = 0;
                for (int s = 0; s < n; s++) {
                    pesos[s] = (float) Math.exp(pesos[s] - max);
                    soma += pesos[s];
                }
                int oo = i * dim + hd * headDim;
                for (int j = 0; j < headDim; j++) out[oo + j] = 0;
                for (int s = 0; s < n; s++) {
                    float p = pesos[s] / soma;
                    int vo = s * dim + hd * headDim;
                    for (int j = 0; j < headDim; j++) out[oo + j] += p * vc[vo + j];
                }
            }
        });
    }

    /** out[t][o] = x[t] · W[o] (+ bias[o]); W no formato do PyTorch: [saída][entrada]. */
    private void matmul(float[] x, int t, int in, float[] w, float[] bias, int outDim, float[] out) {
        paralelo(outDim, (long) t * in * outDim >= 65536, (ini, fim) -> {
            for (int o = ini; o < fim; o++) {
                int wo = o * in;
                float b = bias == null ? 0f : bias[o];
                for (int i = 0; i < t; i++) out[i * outDim + o] = dot(x, i * in, w, wo, in) + b;
            }
        });
    }

    private static float dot(float[] a, int ao, float[] b, int bo, int n) {
        float s0 = 0, s1 = 0, s2 = 0, s3 = 0;
        int j = 0;
        for (; j + 3 < n; j += 4) {
            s0 += a[ao + j] * b[bo + j];
            s1 += a[ao + j + 1] * b[bo + j + 1];
            s2 += a[ao + j + 2] * b[bo + j + 2];
            s3 += a[ao + j + 3] * b[bo + j + 3];
        }
        for (; j < n; j++) s0 += a[ao + j] * b[bo + j];
        return (s0 + s1) + (s2 + s3);
    }

    /** GELU exato (nn.GELU() usa a função erro, não a aproximação com tanh). */
    static float gelu(float x) {
        return (float) (0.5 * x * (1.0 + erf(x / Math.sqrt(2.0))));
    }

    /** Função erro com erro < 1,2e-7 (Numerical Recipes, erfc de Chebyshev). */
    static double erf(double x) {
        double z = Math.abs(x);
        double t = 1.0 / (1.0 + 0.5 * z);
        double r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418
                + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587
                + t * (-0.82215223 + t * 0.17087277)))))))));
        return x >= 0 ? 1.0 - r : r - 1.0;
    }

    private interface Faixa {
        void rodar(int ini, int fim);
    }

    /** Divide [0, n) entre os núcleos; trabalho pequeno roda direto, sem trocar de thread. */
    private void paralelo(int n, boolean vale, Faixa f) {
        if (pool == null || !vale || n < threads) {
            f.rodar(0, n);
            return;
        }
        int partes = threads;
        CountDownLatch pronto = new CountDownLatch(partes - 1);
        Throwable[] erro = new Throwable[1];
        for (int p = 1; p < partes; p++) {
            int ini = (int) ((long) n * p / partes), fim = (int) ((long) n * (p + 1) / partes);
            pool.execute(() -> {
                try {
                    f.rodar(ini, fim);
                } catch (Throwable e) {
                    erro[0] = e;
                } finally {
                    pronto.countDown();
                }
            });
        }
        f.rodar(0, (int) ((long) n / partes));
        try {
            pronto.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }
        if (erro[0] != null) throw new RuntimeException(erro[0]);
    }
}
