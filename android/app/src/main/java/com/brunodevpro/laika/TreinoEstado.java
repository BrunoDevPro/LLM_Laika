package com.brunodevpro.laika;

import android.os.Handler;
import android.os.Looper;

import com.brunodevpro.laika.core.treino.Registro;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/** O que o treino está fazendo agora (para a tela e a notificação): log, progresso, parar. */
final class TreinoEstado implements Registro {
    interface Ouvinte {
        void mudou();
    }

    private static final TreinoEstado INSTANCIA = new TreinoEstado();

    static TreinoEstado get() {
        return INSTANCIA;
    }

    private final Handler ui = new Handler(Looper.getMainLooper());
    private final Set<Ouvinte> ouvintes = new LinkedHashSet<>();
    private final ArrayDeque<String> linhas = new ArrayDeque<>();
    private Writer arquivo;
    private boolean avisoPendente;

    volatile boolean rodando, pararPedido;
    volatile String trabalho = "", texto = "";
    volatile double fracao = -1;
    volatile String fim;  // mensagem final ("concluído", erro...)

    void adicionar(Ouvinte o) {
        ouvintes.add(o);
    }

    void remover(Ouvinte o) {
        ouvintes.remove(o);
    }

    synchronized List<String> log() {
        return new ArrayList<>(linhas);
    }

    void comecar(String nome, File arquivoLog) {
        rodando = true;
        pararPedido = false;
        trabalho = nome;
        texto = "";
        fracao = -1;
        fim = null;
        synchronized (this) {
            linhas.clear();
            try {
                arquivoLog.getParentFile().mkdirs();
                arquivo = new FileWriter(arquivoLog, true);
            } catch (IOException e) {
                arquivo = null;
            }
        }
        log("=== " + nome + " ===");
    }

    void terminar(String mensagem) {
        log(mensagem);
        synchronized (this) {
            try {
                if (arquivo != null) arquivo.close();
            } catch (IOException ignorado) {
                // nada
            }
            arquivo = null;
        }
        fim = mensagem;
        rodando = false;
        avisar();
    }

    private void avisar() {
        synchronized (this) {
            if (avisoPendente) return;
            avisoPendente = true;
        }
        // Junta as atualizações (o treino pode logar muito rápido).
        ui.postDelayed(() -> {
            synchronized (this) {
                avisoPendente = false;
            }
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.mudou();
        }, 150);
    }

    @Override
    public void log(String linha) {
        synchronized (this) {
            for (String l : linha.split("\n", -1)) {
                linhas.add(l);
                if (linhas.size() > 400) linhas.removeFirst();
            }
            try {
                if (arquivo != null) {
                    arquivo.write(linha);
                    arquivo.write('\n');
                    arquivo.flush();
                }
            } catch (IOException ignorado) {
                // sem espaço: o log continua só na tela
            }
        }
        avisar();
    }

    @Override
    public void progresso(double f, String t) {
        fracao = f;
        texto = t;
        avisar();
    }

    @Override
    public boolean parar() {
        return pararPedido;
    }
}
