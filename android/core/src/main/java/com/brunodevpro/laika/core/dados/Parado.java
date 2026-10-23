package com.brunodevpro.laika.core.dados;

/** O usuário pediu para parar um trabalho longo (montar o índice, baixar um modelo). */
public final class Parado extends RuntimeException {
    public Parado() {
        super("cancelado");
    }
}
