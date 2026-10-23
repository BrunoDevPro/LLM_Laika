package com.brunodevpro.laika.core.treino;

import java.util.LinkedHashMap;
import java.util.Map;

/** Os presets do config.py (mesmos números). */
public final class Presets {
    private Presets() {
    }

    public static final class Preset {
        public final String nome, descricao;
        public final int block, dim, heads, layers, vocab, batch, maxSteps, warmup, evalEvery, evalIters, patience;
        public final float dropout, lr;

        Preset(String nome, String descricao, int block, int dim, int heads, int layers, float dropout, int vocab, int batch,
               float lr, int maxSteps, int warmup, int evalEvery, int evalIters, int patience) {
            this.nome = nome;
            this.descricao = descricao;
            this.block = block;
            this.dim = dim;
            this.heads = heads;
            this.layers = layers;
            this.dropout = dropout;
            this.vocab = vocab;
            this.batch = batch;
            this.lr = lr;
            this.maxSteps = maxSteps;
            this.warmup = warmup;
            this.evalEvery = evalEvery;
            this.evalIters = evalIters;
            this.patience = patience;
        }
    }

    public static final Map<String, Preset> TODOS = new LinkedHashMap<>();

    static {
        put(new Preset("tiny", "~1 M parâmetros, para testar rápido", 128, 128, 4, 4, 0.1f, 4000, 32, 1e-3f, 3000, 100, 250, 20, 8));
        put(new Preset("colab", "~7 M parâmetros (o modelo atual)", 256, 256, 8, 6, 0.2f, 8000, 64, 8e-4f, 10000, 300, 500, 40, 6));
        put(new Preset("colab_big", "~14 M parâmetros", 256, 384, 6, 6, 0.15f, 8000, 64, 6e-4f, 15000, 500, 500, 40, 6));
    }

    private static void put(Preset p) {
        TODOS.put(p.nome, p);
    }

    /** O lr_at do train.py: aquecimento linear e cosseno até 10% da taxa. */
    public static float taxa(int passo, float lr, int warmup, int total) {
        if (passo < warmup) return lr * (passo + 1) / warmup;
        double progresso = (passo - warmup) / (double) Math.max(1, total - warmup);
        return (float) (lr * (0.1 + 0.9 * 0.5 * (1 + Math.cos(Math.PI * Math.min(progresso, 1.0)))));
    }
}
