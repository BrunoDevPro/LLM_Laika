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
 * Mesma conta do PyTorch: embedding de token + posição (aprendida, LAIKA001, ou RoPE, LAIKA002),
 * blocos com pré-LayerNorm, atenção causal, feed-forward com GELU exato, LayerNorm final e saída
 * com os pesos do embedding. Com o cache, cada token novo custa só a parte dele.
 *
 * Modelos grandes (o de 100M) guardam as matrizes em float16 (metade da memória; a conta continua
 * em float32, com os mesmos valores), e o cache cresce conforme a conversa em vez de reservar a
 * janela inteira (2048 posições) de uma vez.
 *
 * As multiplicações de matriz são divididas entre os núcleos do processador.
 */
public final class Modelo {
    private static final float LN_EPS = 1e-5f;

    /** Acima disto (parâmetros), as matrizes ficam em float16 na memória. */
    public static final long LIMITE_COMPACTO = 60_000_000L;

    public final int vocab, block, dim, heads, layers, headDim;
    /** RoPE (LAIKA002) em vez da tabela de posições aprendidas. */
    public final boolean rope;
    /** Matrizes em float16 (short[]) em vez de float32. */
    public final boolean compacto;
    private final float[] posEmb, lnfW, lnfB, ropeCos, ropeSin;
    private final Matriz tokEmb;
    private final float[][] ln1W, ln1B, ln2W, ln2B, ff1B, ff2B;
    private final Matriz[] qkvW, projW, ff1W, ff2W;
    private final ExecutorService pool;
    private final int threads;

    /** Uma matriz de pesos: float32 (f) ou float16 (h, convertido na hora pela tabela MEIAS). */
    private static final class Matriz {
        final float[] f;
        final short[] h;

        Matriz(float[] f, short[] h) {
            this.f = f;
            this.h = h;
        }
    }

    private static float[] meias;

    /** float16 -> float32 para todos os 65536 valores (os mesmos de meiaParaFloat). */
    private static synchronized float[] tabelaMeias() {
        if (meias == null) {
            float[] t = new float[65536];
            for (int i = 0; i < t.length; i++) t[i] = meiaParaFloat((short) i);
            meias = t;
        }
        return meias;
    }

    /** Lê o laika_*.bin gerado por android/exportar_modelo.py. */
    public Modelo(InputStream in, int threads) throws IOException {
        this(in, threads, null);
    }

    /** compacto: null = decide pelo tamanho (LIMITE_COMPACTO); true/false força (testes). */
    public Modelo(InputStream in, int threads, Boolean compacto) throws IOException {
        DataInputStream d = new DataInputStream(new java.io.BufferedInputStream(in, 1 << 16));
        byte[] magic = new byte[8];
        d.readFully(magic);
        String m = new String(magic, "US-ASCII");
        if (!m.equals("LAIKA001") && !m.equals("LAIKA002")) throw new IOException("arquivo de pesos inválido");
        rope = m.equals("LAIKA002");
        byte[] cab = new byte[rope ? 24 : 20];
        d.readFully(cab);
        ByteBuffer c = ByteBuffer.wrap(cab).order(ByteOrder.LITTLE_ENDIAN);
        vocab = c.getInt();
        block = c.getInt();
        dim = c.getInt();
        heads = c.getInt();
        layers = c.getInt();
        headDim = dim / heads;
        float theta = rope ? c.getFloat() : 0f;
        long parametros = ConversorPt.parametros(vocab, rope ? 0 : block, dim, layers);
        this.compacto = compacto != null ? compacto : parametros > LIMITE_COMPACTO;

        tokEmb = matriz(d, vocab * dim);
        posEmb = rope ? null : ler(d, block * dim);
        ln1W = new float[layers][]; ln1B = new float[layers][]; qkvW = new Matriz[layers]; projW = new Matriz[layers];
        ln2W = new float[layers][]; ln2B = new float[layers][]; ff1W = new Matriz[layers]; ff1B = new float[layers][];
        ff2W = new Matriz[layers]; ff2B = new float[layers][];
        for (int l = 0; l < layers; l++) {
            ln1W[l] = ler(d, dim);
            ln1B[l] = ler(d, dim);
            qkvW[l] = matriz(d, 3 * dim * dim);
            projW[l] = matriz(d, dim * dim);
            ln2W[l] = ler(d, dim);
            ln2B[l] = ler(d, dim);
            ff1W[l] = matriz(d, 4 * dim * dim);
            ff1B[l] = ler(d, 4 * dim);
            ff2W[l] = matriz(d, 4 * dim * dim);
            ff2B[l] = ler(d, dim);
        }
        lnfW = ler(d, dim);
        lnfB = ler(d, dim);

        if (rope) {
            // Igual ao rope_tables do model.py (float32): ângulo = posição × theta^(-2j/headDim).
            int metade = headDim / 2;
            float[] inv = new float[metade];
            for (int j = 0; j < metade; j++) inv[j] = (float) (1.0 / Math.pow(theta, (2.0 * j) / headDim));
            ropeCos = new float[block * metade];
            ropeSin = new float[block * metade];
            for (int pos = 0; pos < block; pos++) {
                for (int j = 0; j < metade; j++) {
                    float ang = (float) pos * inv[j];
                    ropeCos[pos * metade + j] = (float) Math.cos(ang);
                    ropeSin[pos * metade + j] = (float) Math.sin(ang);
                }
            }
        } else {
            ropeCos = ropeSin = null;
        }

        this.threads = Math.max(1, threads);
        pool = this.threads > 1 ? Executors.newFixedThreadPool(this.threads - 1, r -> {
            Thread t = new Thread(r, "laika-calculo");
            t.setDaemon(true);
            return t;
        }) : null;
    }

    private Matriz matriz(DataInputStream d, int n) throws IOException {
        if (!compacto) return new Matriz(ler(d, n), null);
        tabelaMeias();
        byte[] raw = new byte[n * 2];
        d.readFully(raw);
        short[] h = new short[n];
        ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(h);
        return new Matriz(null, h);
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

    /**
     * Cache de atenção de uma conversa: chaves e valores das posições já processadas. Começa pequeno
     * e dobra quando precisa (com contexto 2048, reservar tudo de cara gastaria ~150 MB).
     */
    public final class Cache {
        float[][] k = new float[layers][], v = new float[layers][];
        int tamanho = 0, capacidade = 0;

        public int tamanho() {
            return tamanho;
        }

        public void limpar() {
            tamanho = 0;
        }

        void garantir(int posicoes) {
            if (posicoes <= capacidade) return;
            int nova = Math.min(block, Math.max(posicoes, Math.max(64, capacidade * 2)));
            for (int l = 0; l < layers; l++) {
                k[l] = k[l] == null ? new float[nova * dim] : java.util.Arrays.copyOf(k[l], nova * dim);
                v[l] = v[l] == null ? new float[nova * dim] : java.util.Arrays.copyOf(v[l], nova * dim);
            }
            capacidade = nova;
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

        cache.garantir(p0 + t);

        float[] x = new float[t * dim];
        float[] tabela = compacto ? tabelaMeias() : null;
        for (int i = 0; i < t; i++) {
            int tok = tokens[de + i], pos = p0 + i;
            for (int j = 0; j < dim; j++) {
                float e = compacto ? tabela[tokEmb.h[tok * dim + j] & 0xFFFF] : tokEmb.f[tok * dim + j];
                x[i * dim + j] = rope ? e : e + posEmb[pos * dim + j];
            }
        }
        float[] h = new float[t * dim];
        float[] qkv = new float[t * 3 * dim];
        float[] att = new float[t * dim];
        float[] tmp = new float[t * dim];
        float[] ff = new float[t * 4 * dim];

        for (int l = 0; l < layers; l++) {
            layerNorm(x, h, t, ln1W[l], ln1B[l]);
            matmul(h, t, dim, qkvW[l], null, 3 * dim, qkv);
            if (rope) girar(qkv, t, p0);
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

    /** RoPE em q e k de cada cabeça (apply_rope do model.py: gira a 1ª metade com a 2ª). */
    private void girar(float[] qkv, int t, int p0) {
        int metade = headDim / 2;
        for (int i = 0; i < t; i++) {
            int base = (p0 + i) * metade;
            for (int parte = 0; parte < 2; parte++) {  // 0 = q, 1 = k
                for (int hd = 0; hd < heads; hd++) {
                    int o = i * 3 * dim + parte * dim + hd * headDim;
                    for (int j = 0; j < metade; j++) {
                        float x1 = qkv[o + j], x2 = qkv[o + metade + j];
                        float c = ropeCos[base + j], s = ropeSin[base + j];
                        qkv[o + j] = x1 * c - x2 * s;
                        qkv[o + metade + j] = x1 * s + x2 * c;
                    }
                }
            }
        }
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
    private void matmul(float[] x, int t, int in, Matriz w, float[] bias, int outDim, float[] out) {
        float[] tabela = w.h != null ? tabelaMeias() : null;
        paralelo(outDim, (long) t * in * outDim >= 65536, (ini, fim) -> {
            // Pesos em float16 com vários tokens (o prompt): converte a linha uma vez só, e não uma vez por token
            // (com 500 tokens de prompt, a conversão se repetia 500 vezes). Mesmos valores, mesma soma.
            float[] linha = w.h != null && t > 1 ? new float[in] : null;
            for (int o = ini; o < fim; o++) {
                int wo = o * in;
                float b = bias == null ? 0f : bias[o];
                if (linha != null) for (int j = 0; j < in; j++) linha[j] = tabela[w.h[wo + j] & 0xFFFF];
                for (int i = 0; i < t; i++) {
                    float d = w.f != null ? dot(x, i * in, w.f, wo, in)
                            : linha != null ? dot(x, i * in, linha, 0, in) : dotMeia(x, i * in, w.h, wo, in, tabela);
                    out[i * outDim + o] = d + b;
                }
            }
        });
    }

    /** Igual ao dot, com os pesos em float16 (mesma ordem de soma, então o mesmo resultado). */
    private static float dotMeia(float[] a, int ao, short[] b, int bo, int n, float[] tab) {
        float s0 = 0, s1 = 0, s2 = 0, s3 = 0;
        int j = 0;
        for (; j + 3 < n; j += 4) {
            s0 += a[ao + j] * tab[b[bo + j] & 0xFFFF];
            s1 += a[ao + j + 1] * tab[b[bo + j + 1] & 0xFFFF];
            s2 += a[ao + j + 2] * tab[b[bo + j + 2] & 0xFFFF];
            s3 += a[ao + j + 3] * tab[b[bo + j + 3] & 0xFFFF];
        }
        for (; j < n; j++) s0 += a[ao + j] * tab[b[bo + j] & 0xFFFF];
        return (s0 + s1) + (s2 + s3);
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
        // Pedaços pequenos distribuídos sob demanda: nos celulares, metade dos núcleos é bem mais lenta, e com
        // partes iguais todos esperavam o mais lento. Cada linha da saída continua calculada do mesmo jeito.
        int bloco = Math.max(1, n / (threads * 8));
        java.util.concurrent.atomic.AtomicInteger proximo = new java.util.concurrent.atomic.AtomicInteger();
        Runnable trabalho = () -> {
            for (int ini; (ini = proximo.getAndAdd(bloco)) < n; ) f.rodar(ini, Math.min(n, ini + bloco));
        };
        int partes = threads;
        CountDownLatch pronto = new CountDownLatch(partes - 1);
        Throwable[] erro = new Throwable[1];
        for (int p = 1; p < partes; p++) {
            pool.execute(() -> {
                try {
                    trabalho.run();
                } catch (Throwable e) {
                    erro[0] = e;
                } finally {
                    pronto.countDown();
                }
            });
        }
        trabalho.run();
        try {
            pronto.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }
        if (erro[0] != null) throw new RuntimeException(erro[0]);
    }
}
