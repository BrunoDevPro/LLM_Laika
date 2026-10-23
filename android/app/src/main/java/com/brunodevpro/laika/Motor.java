package com.brunodevpro.laika;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.os.Process;

import androidx.core.content.pm.PackageInfoCompat;
import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.driver.bundled.BundledSQLite;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.Laika;
import com.brunodevpro.laika.core.Memoria;
import com.brunodevpro.laika.core.Modelo;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Tudo o que não é tela: modelo, tokenizer, índice RAG, memória e a conversa.
 * Vive enquanto o app estiver aberto (girar a tela não recarrega o modelo).
 * Todo o trabalho pesado roda numa única thread de fundo, em ordem.
 */
final class Motor {
    /** Uma mensagem da conversa. */
    static final class Mensagem {
        final boolean usuario, aviso;
        volatile String texto;
        volatile String fonte;

        Mensagem(boolean usuario, boolean aviso, String texto) {
            this.usuario = usuario;
            this.aviso = aviso;
            this.texto = texto;
        }
    }

    /** A tela que está aberta (chamado sempre na thread principal). */
    interface Ouvinte {
        void mensagemNova(Mensagem m);

        void mensagemMudou(Mensagem m);

        void estadoMudou();
    }

    private static Motor instancia;

    static synchronized Motor get(Context ctx) {
        if (instancia == null) instancia = new Motor(ctx.getApplicationContext());
        return instancia;
    }

    private static final String INDICE = "laika_rag.db";
    private static final String INDICE_MINI = "laika_rag_mini.db";

    private final Context ctx;
    private final SharedPreferences prefs;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final ExecutorService fundo = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(() -> {
            Process.setThreadPriority(Process.THREAD_PRIORITY_DEFAULT);
            r.run();
        }, "laika");
        t.setDaemon(true);
        return t;
    });
    private final AtomicBoolean cancelar = new AtomicBoolean();
    private final Random rng = new Random();

    final List<Mensagem> conversa = new ArrayList<>();
    private Ouvinte ouvinte;

    private Tokenizador tok;
    private Laika chat, base;
    private IndiceRag rag;
    private Memoria memoria;
    private final int threads = Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors()));

    volatile boolean pronto, gerando, importando;
    volatile String descricaoIndice = "";
    volatile boolean indiceCompleto;
    volatile String erro;

    // Opções (salvas entre aberturas do app)
    boolean mostrarFontes, usarRag, usarMemoria, modoCompletar;
    double temperatura;

    private Motor(Context ctx) {
        this.ctx = ctx;
        prefs = ctx.getSharedPreferences("opcoes", Context.MODE_PRIVATE);
        mostrarFontes = prefs.getBoolean("fontes", true);
        usarRag = prefs.getBoolean("rag", true);
        usarMemoria = prefs.getBoolean("memoria", true);
        modoCompletar = false;
        temperatura = prefs.getFloat("temperatura", 0.7f);
        aviso("Carregando a Laika…");
        fundo.execute(this::carregar);
    }

    void salvarOpcoes() {
        prefs.edit().putBoolean("fontes", mostrarFontes).putBoolean("rag", usarRag)
                .putBoolean("memoria", usarMemoria).putFloat("temperatura", (float) temperatura).apply();
        avisarEstado();
    }

    void setOuvinte(Ouvinte o) {
        ouvinte = o;
    }

    // ---------- avisos para a tela ----------

    private void naTela(Runnable r) {
        ui.post(r);
    }

    private void avisarEstado() {
        naTela(() -> {
            if (ouvinte != null) ouvinte.estadoMudou();
        });
    }

    private Mensagem adicionar(Mensagem m) {
        naTela(() -> {
            conversa.add(m);
            if (ouvinte != null) ouvinte.mensagemNova(m);
        });
        return m;
    }

    private void mudou(Mensagem m) {
        naTela(() -> {
            if (ouvinte != null) ouvinte.mensagemMudou(m);
        });
    }

    Mensagem aviso(String texto) {
        Mensagem m = new Mensagem(false, true, texto);
        if (Looper.myLooper() == Looper.getMainLooper()) {
            conversa.add(m);
            if (ouvinte != null) ouvinte.mensagemNova(m);
            return m;
        }
        return adicionar(m);
    }

    // ---------- carregamento ----------

    private void carregar() {
        long t0 = System.currentTimeMillis();
        try {
            tok = new Tokenizador(ctx.getAssets().open("tokenizer.txt"));
            chat = new Laika(new Modelo(ctx.getAssets().open("laika_chat.bin"), threads), tok);
            memoria = new Memoria(new File(ctx.getFilesDir(), "memoria.json"));
            abrirIndice();
            pronto = true;
            aviso(String.format("Laika pronta em %.1f s (%d núcleos). Pode perguntar!",
                    (System.currentTimeMillis() - t0) / 1000.0, threads));
        } catch (Throwable e) {
            erro = "Não consegui carregar o modelo: " + e;
            aviso(erro);
        }
        avisarEstado();
    }

    boolean temModoCompletar() {
        try {
            for (String f : ctx.getAssets().list("")) if (f.equals("laika_base.bin")) return true;
        } catch (IOException ignorado) {
            // sem lista de assets
        }
        return false;
    }

    private static SQLiteConnection abrirSomenteLeitura(File f) {
        return new BundledSQLiteDriver().open(f.getPath(), BundledSQLite.SQLITE_OPEN_READONLY);
    }

    /** Usa o índice completo importado, se houver; senão o pequeno que vem no app. */
    private void abrirIndice() throws IOException {
        if (rag != null) {
            rag.close();
            rag = null;
        }
        File completo = new File(ctx.getFilesDir(), INDICE);
        if (completo.exists()) {
            try {
                rag = new IndiceRag(abrirSomenteLeitura(completo));
                indiceCompleto = true;
                descricaoIndice = String.format("índice completo (%,d trechos)", rag.contarTrechos());
                return;
            } catch (RuntimeException e) {
                aviso("O índice importado não abriu (" + e.getMessage() + "). Usando o índice pequeno.");
                rag = null;
            }
        }
        File mini = new File(ctx.getFilesDir(), INDICE_MINI);
        long versao = versaoDoApp();
        if (!mini.exists() || prefs.getLong("versao_mini", -1) != versao) {
            try (InputStream in = ctx.getAssets().open(INDICE_MINI)) {
                copiar(in, mini, -1, null);
            }
            prefs.edit().putLong("versao_mini", versao).apply();
        }
        rag = new IndiceRag(abrirSomenteLeitura(mini));
        indiceCompleto = false;
        descricaoIndice = String.format("índice pequeno (%,d trechos)", rag.contarTrechos());
    }

    private long versaoDoApp() {
        try {
            return PackageInfoCompat.getLongVersionCode(ctx.getPackageManager().getPackageInfo(ctx.getPackageName(), 0));
        } catch (Exception e) {
            return 0;
        }
    }

    interface Progresso {
        void bytes(long copiados);
    }

    private static void copiar(InputStream in, File destino, long total, Progresso p) throws IOException {
        byte[] buf = new byte[1 << 20];
        long feito = 0;
        try (OutputStream out = new FileOutputStream(destino)) {
            int n;
            while ((n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
                feito += n;
                if (p != null) p.bytes(feito);
            }
        }
    }

    // ---------- importar o laika_rag.db completo ----------

    void importarIndice(Uri uri, long tamanho) {
        if (importando) return;
        importando = true;
        avisarEstado();
        Mensagem m = aviso("Importando o índice… 0%");
        fundo.execute(() -> {
            File tmp = new File(ctx.getFilesDir(), INDICE + ".novo");
            try {
                if (tamanho > 0 && ctx.getFilesDir().getUsableSpace() < tamanho + (50L << 20)) {
                    throw new IOException(String.format("falta espaço: o índice tem %d MB", tamanho >> 20));
                }
                long[] ultimo = {-1};
                try (InputStream in = ctx.getContentResolver().openInputStream(uri)) {
                    if (in == null) throw new IOException("não consegui abrir o arquivo");
                    copiar(in, tmp, tamanho, feito -> {
                        long pct = tamanho > 0 ? feito * 100 / tamanho : feito >> 20;
                        if (pct != ultimo[0]) {
                            ultimo[0] = pct;
                            m.texto = tamanho > 0 ? "Importando o índice… " + pct + "%"
                                    : "Importando o índice… " + pct + " MB";
                            mudou(m);
                        }
                    });
                }
                // Confere se é mesmo um índice da Laika (tabela FTS5 "passages").
                long trechos;
                try (IndiceRag teste = new IndiceRag(abrirSomenteLeitura(tmp))) {
                    trechos = teste.contarTrechos();
                    teste.buscar("O que é um vulcão?");
                } catch (RuntimeException e) {
                    throw new IOException("o arquivo não é um laika_rag.db válido (" + e.getMessage() + ")");
                }
                if (rag != null) {
                    rag.close();
                    rag = null;
                }
                File destino = new File(ctx.getFilesDir(), INDICE);
                if (destino.exists() && !destino.delete()) throw new IOException("não consegui trocar o índice");
                if (!tmp.renameTo(destino)) throw new IOException("não consegui salvar o índice");
                abrirIndice();
                m.texto = String.format("Índice importado: %,d trechos. A busca agora usa a Wikipédia e os livros.", trechos);
            } catch (Throwable e) {
                tmp.delete();
                m.texto = "Não deu para importar o índice: " + e.getMessage();
                try {
                    if (rag == null) abrirIndice();
                } catch (Throwable ignorado) {
                    // segue sem RAG
                }
            }
            mudou(m);
            importando = false;
            avisarEstado();
        });
    }

    void voltarIndicePequeno() {
        fundo.execute(() -> {
            try {
                if (rag != null) {
                    rag.close();
                    rag = null;
                }
                new File(ctx.getFilesDir(), INDICE).delete();
                abrirIndice();
                aviso("Índice completo apagado do celular. Usando o índice pequeno.");
            } catch (Throwable e) {
                aviso("Erro ao trocar o índice: " + e.getMessage());
            }
            avisarEstado();
        });
    }

    // ---------- conversa ----------

    String resumoMemoria() {
        return memoria == null ? "" : memoria.resumo();
    }

    void apagarMemoria() {
        fundo.execute(() -> {
            if (memoria != null) memoria.tratar("esqueça tudo");
            aviso("Memória apagada.");
        });
    }

    void pararGeracao() {
        cancelar.set(true);
    }

    void enviar(String texto) {
        Mensagem eu = new Mensagem(true, false, texto);
        conversa.add(eu);
        if (ouvinte != null) ouvinte.mensagemNova(eu);
        gerando = true;
        cancelar.set(false);
        avisarEstado();
        final boolean completar = modoCompletar, fontes = mostrarFontes, comRag = usarRag, comMemoria = usarMemoria;
        final double temp = temperatura;
        fundo.execute(() -> {
            Mensagem resp = adicionar(new Mensagem(false, false, "…"));
            try {
                if (!pronto) throw new IllegalStateException(erro != null ? erro : "o modelo ainda está carregando");
                Laika.Opcoes op = new Laika.Opcoes();
                op.temperatura = temp;
                if (completar) {
                    if (base == null) {
                        resp.texto = "Carregando o modelo de completar texto…";
                        mudou(resp);
                        base = new Laika(new Modelo(ctx.getAssets().open("laika_base.bin"), threads), tok);
                    }
                    op.maxNovos = 160;
                    String r = base.gerar(texto, op, false, rng, parcial -> {
                        resp.texto = texto + " " + parcial;
                        mudou(resp);
                    }, cancelar::get);
                    resp.texto = texto + " " + r;
                } else {
                    String direto = comMemoria ? memoria.tratar(texto) : null;
                    if (direto != null) {
                        resp.texto = direto;
                    } else {
                        Laika.Prompt p = chat.montarPrompt(texto, comRag ? rag : null, comMemoria ? memoria : null,
                                op.maxNovos);
                        String r = chat.gerar(p.texto, op, true, rng, parcial -> {
                            resp.texto = parcial.isEmpty() ? "…" : parcial;
                            mudou(resp);
                        }, cancelar::get);
                        resp.texto = r.isEmpty() ? "…" : r;
                        if (fontes) resp.fonte = p.fonte;
                    }
                }
            } catch (Throwable e) {
                resp.texto = "Erro: " + e.getMessage();
            }
            mudou(resp);
            gerando = false;
            avisarEstado();
        });
    }

    void limparConversa() {
        conversa.clear();
    }
}
