package com.brunodevpro.laika.core.treino;

/** O usuário pediu para parar: o trabalho já salvou o que dava para salvar. */
public final class Parado extends RuntimeException {
    public Parado() {
        super("parado pelo usuário");
    }
}
