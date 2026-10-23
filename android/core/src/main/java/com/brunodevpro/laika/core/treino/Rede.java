package com.brunodevpro.laika.core.treino;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * O TinyLLM do model.py na GPU, para treinar: forward, backward feito à mão (como o llm.c)
 * e AdamW. Parâmetros, gradientes e os momentos do Adam ficam num buffer cada, na mesma
 * ordem do arquivo laika_*.bin.
 *
 * Um "micro-lote" tem até microLote sequências de até block tokens; o lote do treino é
 * a soma de vários micro-lotes (acumulação de gradiente), como se fosse um lote só.
 */
public final class Rede implements AutoCloseable {
    /** Tamanho do modelo (o "config" do checkpoint). */
    public static final class Config {
        public final int vocab, block, dim, heads, layers;
        public final float dropout;

        public Config(int vocab, int block, int dim, int heads, int layers, float dropout) {
            if (dim % heads != 0) throw new IllegalArgumentException("dim precisa ser divisível por heads");
            if (dim / heads > 64) throw new IllegalArgumentException("cabeças de até 64 dimensões");
            this.vocab = vocab;
            this.block = block;
            this.dim = dim;
            this.heads = heads;
            this.layers = layers;
            this.dropout = dropout;
        }

        public Config comDropout(float d) {
            return new Config(vocab, block, dim, heads, layers, d);
        }
    }

    /** Um tensor de parâmetros dentro do buffer grande. */
    public static final class Pedaco {
        public final String nome;
        public final int inicio, tamanho;
        public final boolean matriz;

        Pedaco(String nome, int inicio, int tamanho, boolean matriz) {
            this.nome = nome;
            this.inicio = inicio;
            this.tamanho = tamanho;
            this.matriz = matriz;
        }
    }

    public final Config cfg;
    public final int microLote;
    public final List<Pedaco> pedacos = new ArrayList<>();
    public final int nParametros;

    private final Gl gl;
    private final Kernels k;
    private final int D, V, L, Tm, Mmax;
    private final int offTok, offPos, offLnfW, offLnfB;
    private final int[] offLn1W, offLn1B, offQkv, offProj, offLn2W, offLn2B, offW1, offB1, offW2, offB2;

    // buffers
    private final int par, grad, adamM, adamV;
    private final int[] X, ln1, qkv, att, atto, mid, ln2, h, hg;
    private final int lnf, logits, perda, stats, tok, alvo, csr;
    private final int dx, dtmp, dln, dqkv, datt, datto, dh, parcial;
    private final int gruposNorma;
    private final List<Integer> todos = new ArrayList<>();

    public Rede(Gl gl, Config cfg, int microLote) {
        this.gl = gl;
        this.cfg = cfg;
        this.microLote = microLote;
        D = cfg.dim;
        V = cfg.vocab;
        L = cfg.layers;
        Tm = cfg.block;
        Mmax = microLote * Tm;
        k = new Kernels(gl);

        int o = 0;
        offTok = o; o = pedaco("tok_emb.weight", o, V * D, true);
        offPos = o; o = pedaco("pos_emb.weight", o, Tm * D, true);
        offLn1W = new int[L]; offLn1B = new int[L]; offQkv = new int[L]; offProj = new int[L];
        offLn2W = new int[L]; offLn2B = new int[L]; offW1 = new int[L]; offB1 = new int[L];
        offW2 = new int[L]; offB2 = new int[L];
        for (int l = 0; l < L; l++) {
            String p = "blocks." + l + ".";
            offLn1W[l] = o; o = pedaco(p + "ln1.weight", o, D, false);
            offLn1B[l] = o; o = pedaco(p + "ln1.bias", o, D, false);
            offQkv[l] = o; o = pedaco(p + "attn.qkv.weight", o, 3 * D * D, true);
            offProj[l] = o; o = pedaco(p + "attn.proj.weight", o, D * D, true);
            offLn2W[l] = o; o = pedaco(p + "ln2.weight", o, D, false);
            offLn2B[l] = o; o = pedaco(p + "ln2.bias", o, D, false);
            offW1[l] = o; o = pedaco(p + "ff.net.0.weight", o, 4 * D * D, true);
            offB1[l] = o; o = pedaco(p + "ff.net.0.bias", o, 4 * D, false);
            offW2[l] = o; o = pedaco(p + "ff.net.2.weight", o, 4 * D * D, true);
            offB2[l] = o; o = pedaco(p + "ff.net.2.bias", o, D, false);
        }
        offLnfW = o; o = pedaco("ln_f.weight", o, D, false);
        offLnfB = o; o = pedaco("ln_f.bias", o, D, false);
        nParametros = o;

        long maior = Math.max((long) Mmax * V, (long) microLote * cfg.heads * Tm * Tm) * 4;
        if (maior > gl.maiorBuffer()) {
            throw new IllegalStateException(String.format("a GPU só aceita buffers de %d MB e o treino precisa de %d MB; "
                    + "use um micro-lote menor", gl.maiorBuffer() >> 20, maior >> 20));
        }

        par = buf(nParametros);
        grad = buf(nParametros);
        adamM = buf(nParametros);
        adamV = buf(nParametros);
        X = new int[L + 1];
        ln1 = new int[L]; qkv = new int[L]; att = new int[L]; atto = new int[L]; mid = new int[L];
        ln2 = new int[L]; h = new int[L]; hg = new int[L];
        int attTam = microLote * cfg.heads * Tm * Tm;
        for (int l = 0; l <= L; l++) X[l] = buf(Mmax * D);
        for (int l = 0; l < L; l++) {
            ln1[l] = buf(Mmax * D);
            qkv[l] = buf(Mmax * 3 * D);
            att[l] = buf(attTam);
            atto[l] = buf(Mmax * D);
            mid[l] = buf(Mmax * D);
            ln2[l] = buf(Mmax * D);
            h[l] = buf(Mmax * 4 * D);
            hg[l] = buf(Mmax * 4 * D);
        }
        lnf = buf(Mmax * D);
        logits = buf(Mmax * V);
        perda = buf(Mmax);
        stats = buf((2 * L + 1) * 2 * Mmax);
        tok = buf(Mmax);
        alvo = buf(Mmax);
        csr = buf(4 * Mmax);
        dx = buf(Mmax * D);
        dtmp = buf(Mmax * D);
        dln = buf(Mmax * D);
        dqkv = buf(Mmax * 3 * D);
        datt = buf(attTam);
        datto = buf(Mmax * D);
        dh = buf(Mmax * 4 * D);
        gruposNorma = Math.max(1, Math.min(1024, (nParametros + 127) / 128));
        parcial = buf(gruposNorma + 2);
        for (int b : new int[]{grad, adamM, adamV}) k.preencher(b, 0, nParametros, 0f);
    }

    private int pedaco(String nome, int inicio, int n, boolean matriz) {
        pedacos.add(new Pedaco(nome, inicio, n, matriz));
        return inicio + n;
    }

    private int buf(long floats) {
        int b = gl.buffer(Math.max(4, floats * 4));
        todos.add(b);
        return b;
    }

    /** Memória de GPU usada (aproximada), para mostrar no app. */
    public static long memoriaNecessaria(Config c, int microLote) {
        long M = (long) microLote * c.block, D = c.dim;
        long n = (long) c.vocab * D + (long) c.block * D + c.layers * (12L * D * D + 13L * D) + 2 * D;
        long porCamada = M * D * 16 + (long) microLote * c.heads * c.block * c.block;
        return 4 * (4 * n + c.layers * porCamada + M * D * 2 + M * c.vocab + M * D * 9
                + (long) microLote * c.heads * c.block * c.block + M * 4 * D);
    }

    // ---------- pesos ----------

    /** Inicialização do model.py: normal(0, 0.02), projeções residuais com 0.02/sqrt(2*camadas). */
    public void inicializar(long semente) {
        Random r = new Random(semente);
        float[] p = new float[nParametros];
        for (Pedaco pd : pedacos) {
            if (pd.matriz) {
                double std = pd.nome.endsWith("proj.weight") || pd.nome.endsWith("net.2.weight")
                        ? 0.02 / Math.sqrt(2.0 * L) : 0.02;
                for (int i = 0; i < pd.tamanho; i++) p[pd.inicio + i] = (float) (r.nextGaussian() * std);
            } else if (pd.nome.endsWith("ln1.weight") || pd.nome.endsWith("ln2.weight") || pd.nome.equals("ln_f.weight")) {
                for (int i = 0; i < pd.tamanho; i++) p[pd.inicio + i] = 1f;
            }
        }
        carregar(p);
        for (int b : new int[]{grad, adamM, adamV}) k.preencher(b, 0, nParametros, 0f);
    }

    public void carregar(float[] pesos) {
        escreverFloats(par, pesos);
    }

    public float[] pesos() {
        return lerFloats(par, nParametros);
    }

    /** Momentos do Adam (para salvar e retomar o treino). */
    public float[][] estadoAdam() {
        return new float[][]{lerFloats(adamM, nParametros), lerFloats(adamV, nParametros)};
    }

    public void carregarAdam(float[] m, float[] v) {
        escreverFloats(adamM, m);
        escreverFloats(adamV, v);
    }

    public float[] gradientes() {
        return lerFloats(grad, nParametros);
    }

    private void escreverFloats(int b, float[] dados) {
        int passo = 1 << 20;
        for (int i = 0; i < dados.length; i += passo) {
            int n = Math.min(passo, dados.length - i);
            ByteBuffer bb = ByteBuffer.allocateDirect(n * 4).order(ByteOrder.nativeOrder());
            bb.asFloatBuffer().put(dados, i, n);
            gl.escrever(b, (long) i * 4, bb);
        }
    }

    private float[] lerFloats(int b, int n) {
        gl.barreira();
        float[] r = new float[n];
        int passo = 1 << 20;
        for (int i = 0; i < n; i += passo) {
            int m = Math.min(passo, n - i);
            ByteBuffer bb = ByteBuffer.allocateDirect(m * 4).order(ByteOrder.nativeOrder());
            gl.ler(b, (long) i * 4, bb);
            bb.rewind();
            bb.asFloatBuffer().get(r, i, m);
        }
        return r;
    }

    private void escreverInts(int b, int[] dados, int n) {
        ByteBuffer bb = ByteBuffer.allocateDirect(Math.max(4, n * 4)).order(ByteOrder.nativeOrder());
        bb.asIntBuffer().put(dados, 0, n);
        gl.escrever(b, 0, bb);
    }

    // ---------- forward / backward ----------

    private static int semente(int base, int camada, int lugar) {
        int s = base * 0x9E3779B1 + camada * 0x85EBCA77 + lugar * 0xC2B2AE3D;
        return s ^ (s >>> 15);
    }

    /**
     * Roda um micro-lote: tokens e alvos [B*T] (alvo < 0 = ignorar). Com treinar=true soma
     * os gradientes (escala = 1/número de alvos do lote inteiro) e usa dropout.
     * Devolve a perda de cada posição (0 nas ignoradas).
     */
    public float[] microPasso(int[] tokens, int[] alvos, int B, int T, boolean treinar, float escala, int sementeBase) {
        if (B > microLote || T > Tm) throw new IllegalArgumentException("micro-lote maior que o reservado");
        int M = B * T;
        float p = treinar ? cfg.dropout : 0f;
        escreverInts(tok, tokens, M);
        escreverInts(alvo, alvos, M);
        int sOff = 0;  // stats: [ln1_0, ln2_0, ln1_1, ..., lnf] cada um com 2*M floats

        k.embeddingFrente(tok, par, X[0], M, D, T, offTok, offPos);
        if (p > 0) k.dropout(X[0], 0, M * D, semente(sementeBase, 0, 0), p);
        for (int l = 0; l < L; l++) {
            k.layerNorm(X[l], ln1[l], par, stats, M, D, offLn1W[l], offLn1B[l], (2 * l) * 2 * Mmax);
            k.linear(ln1[l], par, offQkv[l], -1, qkv[l], M, D, 3 * D);
            k.atencao(qkv[l], att[l], atto[l], B, T, cfg.heads, D / cfg.heads, Tm, semente(sementeBase, l, 1), p);
            k.linear(atto[l], par, offProj[l], -1, dtmp, M, D, D);
            if (p > 0) k.dropout(dtmp, 0, M * D, semente(sementeBase, l, 2), p);
            k.somar(X[l], dtmp, mid[l], M * D);
            k.layerNorm(mid[l], ln2[l], par, stats, M, D, offLn2W[l], offLn2B[l], (2 * l + 1) * 2 * Mmax);
            k.linear(ln2[l], par, offW1[l], offB1[l], h[l], M, D, 4 * D);
            k.gelu(h[l], hg[l], M * 4 * D);
            k.linear(hg[l], par, offW2[l], offB2[l], dtmp, M, 4 * D, D);
            if (p > 0) k.dropout(dtmp, 0, M * D, semente(sementeBase, l, 3), p);
            k.somar(mid[l], dtmp, X[l + 1], M * D);
        }
        int sF = (2 * L) * 2 * Mmax;
        k.layerNorm(X[L], lnf, par, stats, M, D, offLnfW, offLnfB, sF);
        k.linear(lnf, par, offTok, -1, logits, M, D, V);
        k.entropia(logits, alvo, perda, M, V, escala);
        gl.barreira();
        ByteBuffer pb = ByteBuffer.allocateDirect(M * 4).order(ByteOrder.nativeOrder());
        gl.ler(perda, 0, pb);
        pb.rewind();
        float[] perdas = new float[M];
        pb.asFloatBuffer().get(perdas);
        if (!treinar) return perdas;

        // ---------- backward ----------
        k.gradEntrada(logits, par, offTok, dln, M, V, D, false);           // dlnf = dlogits · Wtok
        k.gradPesos(logits, lnf, grad, offTok, M, V, D);                   // dWtok += dlogitsᵀ · lnf
        k.preencher(dx, 0, M * D, 0f);
        k.layerNormTras(dln, X[L], par, stats, grad, dx, M, D, offLnfW, offLnfB, sF);
        for (int l = L - 1; l >= 0; l--) {
            // ramo do feed-forward
            k.copiar(dx, dtmp, M * D);
            if (p > 0) k.dropout(dtmp, 0, M * D, semente(sementeBase, l, 3), p);
            k.gradPesos(dtmp, hg[l], grad, offW2[l], M, D, 4 * D);
            k.somaColunas(dtmp, grad, offB2[l], M, D);
            k.gradEntrada(dtmp, par, offW2[l], dh, M, D, 4 * D, false);
            k.geluTras(dh, h[l], M * 4 * D);
            k.gradPesos(dh, ln2[l], grad, offW1[l], M, 4 * D, D);
            k.somaColunas(dh, grad, offB1[l], M, 4 * D);
            k.gradEntrada(dh, par, offW1[l], dln, M, 4 * D, D, false);
            k.layerNormTras(dln, mid[l], par, stats, grad, dx, M, D, offLn2W[l], offLn2B[l], (2 * l + 1) * 2 * Mmax);
            // ramo da atenção
            k.copiar(dx, dtmp, M * D);
            if (p > 0) k.dropout(dtmp, 0, M * D, semente(sementeBase, l, 2), p);
            k.gradPesos(dtmp, atto[l], grad, offProj[l], M, D, D);
            k.gradEntrada(dtmp, par, offProj[l], datto, M, D, D, false);
            k.atencaoTras(qkv[l], att[l], datto, datt, dqkv, B, T, cfg.heads, D / cfg.heads, Tm,
                    semente(sementeBase, l, 1), p);
            k.gradPesos(dqkv, ln1[l], grad, offQkv[l], M, 3 * D, D);
            k.gradEntrada(dqkv, par, offQkv[l], dln, M, 3 * D, D, false);
            k.layerNormTras(dln, X[l], par, stats, grad, dx, M, D, offLn1W[l], offLn1B[l], (2 * l) * 2 * Mmax);
        }
        if (p > 0) k.dropout(dx, 0, M * D, semente(sementeBase, 0, 0), p);
        // embeddings: as linhas de cada token agrupadas na CPU (sem soma atômica na GPU)
        Map<Integer, List<Integer>> porToken = new HashMap<>();
        for (int r = 0; r < M; r++) porToken.computeIfAbsent(tokens[r], x -> new ArrayList<>()).add(r);
        int u = porToken.size();
        int[] c = new int[3 * u + M];
        int pos = 0, i = 0;
        for (Map.Entry<Integer, List<Integer>> e : porToken.entrySet()) {
            c[3 * i] = e.getKey();
            c[3 * i + 1] = pos;
            for (int r : e.getValue()) c[3 * u + pos++] = r;
            c[3 * i + 2] = pos;
            i++;
        }
        escreverInts(csr, c, c.length);
        k.embeddingTrasTok(csr, dx, grad, u, D, offTok, 3 * u);
        k.embeddingTrasPos(dx, grad, B, T, D, offPos);
        return perdas;
    }

    public void zerarGradientes() {
        k.preencher(grad, 0, nParametros, 0f);
    }

    /**
     * Um passo do AdamW (com corte da norma do gradiente em `corte`, 0 = sem corte).
     * wdMatriz vale para os tensores 2D e wdVetor para LayerNorm/viés (como no train.py e no finetune.py).
     * Devolve a norma do gradiente.
     */
    public float otimizar(float lr, float wdMatriz, float wdVetor, float b1, float b2, float eps, float corte, int passo) {
        k.norma(grad, parcial, nParametros, gruposNorma, corte);
        float c1 = (float) (1 - Math.pow(b1, passo)), c2 = (float) (1 - Math.pow(b2, passo));
        for (Pedaco pd : pedacos) {
            k.adamw(par, grad, adamM, adamV, parcial, pd.inicio, pd.tamanho, gruposNorma + 1, lr, b1, b2, eps,
                    pd.matriz ? wdMatriz : wdVetor, c1, c2);
        }
        gl.barreira();
        ByteBuffer nb = ByteBuffer.allocateDirect(4).order(ByteOrder.nativeOrder());
        gl.ler(parcial, (long) gruposNorma * 4, nb);
        nb.rewind();
        return nb.getFloat();
    }

    @Override
    public void close() {
        for (int b : todos) gl.apagarBuffer(b);
        todos.clear();
        k.fechar();
    }
}
