package com.brunodevpro.laika.core.treino;

/** Gerador SplitMix64: o estado é um long só, fácil de salvar para retomar o treino do mesmo ponto. */
public final class Aleatorio {
    public long estado;

    public Aleatorio(long semente) {
        estado = semente;
    }

    public long proximo() {
        long z = (estado += 0x9E3779B97F4A7C15L);
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
        return z ^ (z >>> 31);
    }

    /** Inteiro em [0, n). */
    public int inteiro(int n) {
        return (int) Math.floorMod(proximo(), (long) n);
    }

    public double real() {
        return (proximo() >>> 11) * 0x1.0p-53;
    }

    public <T> void embaralhar(java.util.List<T> l) {
        for (int i = l.size() - 1; i > 0; i--) {
            int j = inteiro(i + 1);
            T t = l.get(i);
            l.set(i, l.get(j));
            l.set(j, t);
        }
    }
}
