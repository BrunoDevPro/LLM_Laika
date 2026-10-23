package com.brunodevpro.laika.core.treino;

/** Para onde vão as mensagens e o progresso de um trabalho de treino (a tela, a notificação, o teste). */
public interface Registro {
    /** Uma linha de log, como a saída das células do Colab. */
    void log(String linha);

    /** Progresso de 0 a 1 (ou -1 se não dá para medir) e um texto curto. */
    void progresso(double fracao, String texto);

    /** true quando o usuário pediu para parar: o trabalho salva o que tem e termina. */
    boolean parar();

    /** Registro que só imprime (testes). */
    Registro CONSOLE = new Registro() {
        @Override
        public void log(String linha) {
            System.out.println(linha);
        }

        @Override
        public void progresso(double fracao, String texto) {
        }

        @Override
        public boolean parar() {
            return false;
        }
    };
}
