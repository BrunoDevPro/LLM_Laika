package com.brunodevpro.laika.core.treino;

import java.util.HashMap;
import java.util.Map;

/** Chamadas dos shaders com os uniformes certos (uma função por operação). */
final class Kernels {
    private final Gl gl;
    private final int matmul, elementos, lnFrente, lnTras, lnTrasPesos, somaColunas, atFrente, atTras1, atTras2,
            embFrente, embTrasTok, embTrasPos, entropia, norma1, norma2, adamw;
    private final Map<Integer, Map<String, Integer>> locais = new HashMap<>();
    private int atual = -1;

    Kernels(Gl gl) {
        this.gl = gl;
        matmul = gl.programa(Shaders.MATMUL);
        elementos = gl.programa(Shaders.ELEMENTOS);
        lnFrente = gl.programa(Shaders.LN_FRENTE);
        lnTras = gl.programa(Shaders.LN_TRAS);
        lnTrasPesos = gl.programa(Shaders.LN_TRAS_PESOS);
        somaColunas = gl.programa(Shaders.SOMA_COLUNAS);
        atFrente = gl.programa(Shaders.ATENCAO_FRENTE);
        atTras1 = gl.programa(Shaders.ATENCAO_TRAS1);
        atTras2 = gl.programa(Shaders.ATENCAO_TRAS2);
        embFrente = gl.programa(Shaders.EMBED_FRENTE);
        embTrasTok = gl.programa(Shaders.EMBED_TRAS_TOK);
        embTrasPos = gl.programa(Shaders.EMBED_TRAS_POS);
        entropia = gl.programa(Shaders.ENTROPIA);
        norma1 = gl.programa(Shaders.NORMA1);
        norma2 = gl.programa(Shaders.NORMA2);
        adamw = gl.programa(Shaders.ADAMW);
    }

    void fechar() {
        locais.clear();
    }

    private void usar(int prog) {
        if (prog != atual) {
            gl.usar(prog);
            atual = prog;
        }
    }

    private int loc(String nome) {
        return locais.computeIfAbsent(atual, x -> new HashMap<>()).computeIfAbsent(nome, n -> gl.local(atual, n));
    }

    private void i(String nome, int v) {
        int l = loc(nome);
        if (l >= 0) gl.uniformI(l, v);
    }

    private void f(String nome, float v) {
        int l = loc(nome);
        if (l >= 0) gl.uniformF(l, v);
    }

    private static int grupos(long n, int porGrupo) {
        return (int) ((n + porGrupo - 1) / porGrupo);
    }

    /** Despacho 2D para mais de 65535 grupos de 128 (o shader usa indice()). */
    private void despachar128(long n) {
        int g = grupos(n, 128);
        int gx = Math.min(g, 65535), gy = (g + gx - 1) / gx;
        gl.despachar(Math.max(1, gx), Math.max(1, gy), 1);
        gl.barreira();
    }

    // ---------- matmul ----------

    private void mm(int A, int offA, int sAi, int sAk, int B, int offB, int sBk, int sBj, int C, int offC, int sCi, int sCj,
                    int M, int N, int K, int vies, int offVies, boolean acumular) {
        usar(matmul);
        gl.ligar(0, A);
        gl.ligar(1, B);
        gl.ligar(2, C);
        gl.ligar(3, vies >= 0 ? vies : B);
        i("M", M); i("N", N); i("K", K);
        i("offA", offA); i("sAi", sAi); i("sAk", sAk);
        i("offB", offB); i("sBk", sBk); i("sBj", sBj);
        i("offC", offC); i("sCi", sCi); i("sCj", sCj);
        i("offVies", Math.max(0, offVies)); i("temVies", offVies >= 0 ? 1 : 0);
        i("acumular", acumular ? 1 : 0); f("alpha", 1f);
        gl.despachar(grupos(N, 64), grupos(M, 64), 1);
        gl.barreira();
    }

    /** out[M,N] = inp[M,K] · W[N,K]ᵀ (+ b) — o nn.Linear do PyTorch. W e b estão no buffer de parâmetros. */
    void linear(int inp, int par, int offW, int offB, int out, int M, int K, int N) {
        mm(inp, 0, K, 1, par, offW, 1, K, out, 0, N, 1, M, N, K, offB >= 0 ? par : -1, offB, false);
    }

    /** dinp[M,K] (+)= dout[M,N] · W[N,K]. */
    void gradEntrada(int dout, int par, int offW, int dinp, int M, int N, int K, boolean acumular) {
        mm(dout, 0, N, 1, par, offW, K, 1, dinp, 0, K, 1, M, K, N, -1, -1, acumular);
    }

    /** dW[N,K] += dout[M,N]ᵀ · inp[M,K]. */
    void gradPesos(int dout, int inp, int grad, int offW, int M, int N, int K) {
        mm(dout, 0, 1, N, inp, 0, K, 1, grad, offW, K, 1, N, K, M, -1, -1, true);
    }

    // ---------- elemento a elemento ----------

    private void elem(int op, int X, int offX, int Y, int offY, int Z, int offZ, int n, float valor, int semente, float p) {
        usar(elementos);
        gl.ligar(0, X);
        gl.ligar(1, Y);
        gl.ligar(2, Z);
        i("n", n); i("op", op); i("offX", offX); i("offY", offY); i("offZ", offZ);
        f("valor", valor); i("semente", semente); f("p", p);
        despachar128(n);
    }

    void preencher(int buf, int off, int n, float v) {
        elem(0, buf, 0, buf, 0, buf, off, n, v, 0, 0);
    }

    void copiar(int de, int para, int n) {
        elem(1, de, 0, de, 0, para, 0, n, 0, 0, 0);
    }

    void somar(int a, int b, int out, int n) {
        elem(2, a, 0, b, 0, out, 0, n, 0, 0, 0);
    }

    void gelu(int x, int out, int n) {
        elem(4, x, 0, x, 0, out, 0, n, 0, 0, 0);
    }

    /** d (in-place) *= GELU'(x) */
    void geluTras(int d, int x, int n) {
        elem(5, d, 0, x, 0, d, 0, n, 0, 0, 0);
    }

    void dropout(int buf, int off, int n, int semente, float p) {
        elem(6, buf, 0, buf, 0, buf, off, n, 0, semente, p);
    }

    // ---------- LayerNorm ----------

    void layerNorm(int inp, int out, int par, int stats, int M, int D, int offW, int offB, int offS) {
        usar(lnFrente);
        gl.ligar(0, inp);
        gl.ligar(1, out);
        gl.ligar(2, par);
        gl.ligar(3, stats);
        i("D", D); i("offI", 0); i("offO", 0); i("offW", offW); i("offB", offB); i("offS", offS); i("linhas", M);
        gl.despachar(M, 1, 1);
        gl.barreira();
    }

    /** dinp += gradiente da entrada; grad[offW], grad[offB] += gradientes do peso e do viés. */
    void layerNormTras(int dout, int inp, int par, int stats, int grad, int dinp, int M, int D, int offW, int offB, int offS) {
        usar(lnTras);
        gl.ligar(0, dout);
        gl.ligar(1, inp);
        gl.ligar(2, par);
        gl.ligar(3, stats);
        gl.ligar(4, dinp);
        i("D", D); i("offD", 0); i("offI", 0); i("offW", offW); i("offS", offS); i("offG", 0); i("linhas", M);
        gl.despachar(M, 1, 1);
        gl.barreira();
        usar(lnTrasPesos);
        gl.ligar(0, dout);
        gl.ligar(1, inp);
        gl.ligar(3, stats);
        gl.ligar(4, grad);
        i("D", D); i("offD", 0); i("offI", 0); i("offS", offS); i("linhas", M); i("offGW", offW); i("offGB", offB);
        gl.despachar(grupos(D, 64), 1, 1);
        gl.barreira();
    }

    void somaColunas(int dout, int grad, int offG, int M, int N) {
        usar(somaColunas);
        gl.ligar(0, dout);
        gl.ligar(1, grad);
        i("N", N); i("linhas", M); i("offD", 0); i("offG", offG);
        gl.despachar(grupos(N, 64), 1, 1);
        gl.barreira();
    }

    // ---------- atenção ----------

    private void atUniformes(int B, int T, int H, int hd, int Tm, int semente, float p) {
        i("B", B); i("T", T); i("H", H); i("hd", hd); i("TMAX", Tm); i("semente", semente); f("p", p);
    }

    void atencao(int qkv, int att, int out, int B, int T, int H, int hd, int Tm, int semente, float p) {
        usar(atFrente);
        gl.ligar(0, qkv);
        gl.ligar(1, att);
        gl.ligar(2, out);
        atUniformes(B, T, H, hd, Tm, semente, p);
        gl.despachar(grupos((long) B * H * T, 64), 1, 1);
        gl.barreira();
    }

    void atencaoTras(int qkv, int att, int dout, int datt, int dqkv, int B, int T, int H, int hd, int Tm, int semente, float p) {
        usar(atTras1);
        gl.ligar(0, qkv);
        gl.ligar(1, att);
        gl.ligar(2, dout);
        gl.ligar(3, datt);
        gl.ligar(4, dqkv);
        atUniformes(B, T, H, hd, Tm, semente, p);
        gl.despachar(grupos((long) B * H * T, 64), 1, 1);
        gl.barreira();
        usar(atTras2);
        gl.ligar(0, qkv);
        gl.ligar(1, att);
        gl.ligar(2, dout);
        gl.ligar(3, datt);
        gl.ligar(4, dqkv);
        atUniformes(B, T, H, hd, Tm, semente, p);
        gl.despachar(grupos((long) B * H * T, 64), 1, 1);
        gl.barreira();
    }

    // ---------- embeddings e perda ----------

    void embeddingFrente(int tok, int par, int out, int M, int D, int T, int offTok, int offPos) {
        usar(embFrente);
        gl.ligar(0, tok);
        gl.ligar(1, par);
        gl.ligar(2, out);
        i("n", M * D); i("D", D); i("T", T); i("offTok", offTok); i("offPos", offPos);
        despachar128((long) M * D);
    }

    void embeddingTrasTok(int csr, int dx, int grad, int unicos, int D, int offTok, int offLista) {
        usar(embTrasTok);
        gl.ligar(0, csr);
        gl.ligar(1, dx);
        gl.ligar(2, grad);
        i("unicos", unicos); i("D", D); i("offTok", offTok); i("offLista", offLista);
        despachar128((long) unicos * D);
    }

    void embeddingTrasPos(int dx, int grad, int B, int T, int D, int offPos) {
        usar(embTrasPos);
        gl.ligar(0, dx);
        gl.ligar(1, grad);
        i("B", B); i("T", T); i("D", D); i("offPos", offPos);
        despachar128((long) T * D);
    }

    void entropia(int logits, int alvo, int perda, int M, int V, float escala) {
        usar(entropia);
        gl.ligar(0, logits);
        gl.ligar(1, alvo);
        gl.ligar(2, perda);
        i("V", V); f("escala", escala);
        int gx = Math.min(M, 65535), gy = (M + gx - 1) / gx;
        gl.despachar(gx, gy, 1);
        gl.barreira();
    }

    // ---------- otimizador ----------

    void norma(int grad, int parcial, int n, int grupos, float maximo) {
        usar(norma1);
        gl.ligar(0, grad);
        gl.ligar(1, parcial);
        i("n", n);
        gl.despachar(grupos, 1, 1);
        gl.barreira();
        usar(norma2);
        gl.ligar(1, parcial);
        i("grupos", grupos); f("maximo", maximo);
        gl.despachar(1, 1, 1);
        gl.barreira();
    }

    void adamw(int par, int grad, int m, int v, int corte, int off, int n, int idxCorte, float lr, float b1, float b2,
               float eps, float wd, float c1, float c2) {
        usar(adamw);
        gl.ligar(0, par);
        gl.ligar(1, grad);
        gl.ligar(2, m);
        gl.ligar(3, v);
        gl.ligar(4, corte);
        i("n", n); i("off", off); i("idxCorte", idxCorte);
        f("lr", lr); f("b1", b1); f("b2", b2); f("eps", eps); f("wd", wd); f("c1", c1); f("c2", c2);
        despachar128(n);
    }
}
