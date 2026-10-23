package com.brunodevpro.laika;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.net.Uri;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;

import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.driver.bundled.BundledSQLite;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.Armazem;
import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.treino.ConstrutorIndice;
import com.brunodevpro.laika.core.treino.Corpus;
import com.brunodevpro.laika.core.treino.FineTuning;
import com.brunodevpro.laika.core.treino.Parado;
import com.brunodevpro.laika.core.treino.PreTreino;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Roda os trabalhos do treino (importar dados, índice, pré-treino, fine-tuning) em primeiro
 * plano, com notificação, para continuar com a tela apagada ou o app em segundo plano.
 * A GPU é usada numa thread própria (contexto OpenGL ES sem tela).
 */
public class TreinoService extends Service {
    static final String DADOS = "dados", INDICE = "indice", PRETREINO = "pretreino", FINETUNING = "finetuning";
    private static final String PARAR = "com.brunodevpro.laika.PARAR";
    private static final String CANAL = "treino";
    private static final int ID = 7;

    private PowerManager.WakeLock trava;
    private long ultimaNotificacao;
    private final TreinoEstado.Ouvinte ouvinte = this::notificar;

    static File pastaTreino(Context c) {
        return new File(c.getFilesDir(), "laika/treino");
    }

    static Corpus corpus(Context c) {
        return new Corpus(new File(c.getFilesDir(), "laika/dados"));
    }

    /** Começa uma sequência de etapas (ex.: índice, pré-treino e fine-tuning). */
    static void iniciar(Context c, Intent opcoes) {
        opcoes.setClass(c, TreinoService.class);
        if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(opcoes);
        else c.startService(opcoes);
    }

    static void parar(Context c) {
        TreinoEstado.get().pararPedido = true;
    }

    @Override
    public IBinder onBind(Intent i) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && PARAR.equals(intent.getAction())) {
            parar(this);
            return START_NOT_STICKY;
        }
        TreinoEstado e = TreinoEstado.get();
        criarCanal();
        Notification n = notificacao("Preparando…", -1);
        if (Build.VERSION.SDK_INT >= 34) startForeground(ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        else startForeground(ID, n);
        if (e.rodando || intent == null) return START_NOT_STICKY;

        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        trava = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "laika:treino");
        trava.acquire(48L * 3600 * 1000);
        e.adicionar(ouvinte);
        String[] etapas = intent.getStringArrayExtra("etapas");
        e.comecar(nomes(etapas), new File(pastaTreino(this), "log.txt"));
        Thread t = new Thread(() -> rodar(intent, etapas), "laika-treino");
        t.setPriority(Thread.MAX_PRIORITY);
        t.start();
        return START_NOT_STICKY;
    }

    private static String nomes(String[] etapas) {
        List<String> n = new ArrayList<>();
        for (String s : etapas) {
            switch (s) {
                case DADOS: n.add("Importar dados"); break;
                case INDICE: n.add("Índice do RAG"); break;
                case PRETREINO: n.add("Pré-treino"); break;
                default: n.add("Fine-tuning");
            }
        }
        return String.join(" → ", n);
    }

    private void rodar(Intent in, String[] etapas) {
        TreinoEstado e = TreinoEstado.get();
        String fim;
        GlAndroid gl = null;
        try {
            Motor motor = esperarMotor();
            Corpus corpus = corpus(this);
            corpus.garantirPadrao(new Corpus.Fabrica() {
                @Override
                public String[] listar(String pasta) throws IOException {
                    String[] r = getAssets().list("dados/" + pasta);
                    return r == null ? new String[0] : r;
                }

                @Override
                public InputStream abrir(String caminho) throws IOException {
                    return getAssets().open("dados/" + caminho);
                }
            });
            File pasta = pastaTreino(this);
            for (String etapa : etapas) {
                if (e.pararPedido) throw new Parado();
                e.log("\n--- " + nomes(new String[]{etapa}) + " ---");
                if ((etapa.equals(PRETREINO) || etapa.equals(FINETUNING)) && gl == null) gl = new GlAndroid();
                switch (etapa) {
                    case DADOS: importarDados(corpus, Uri.parse(in.getStringExtra("uri"))); break;
                    case INDICE: construirIndice(corpus, pasta); break;
                    case PRETREINO: preTreino(gl, corpus, pasta, motor, in); break;
                    default: fineTuning(gl, corpus, pasta, motor, in);
                }
            }
            fim = "Concluído. Toque em \"Usar o resultado\" para conversar com o modelo treinado.";
            if (etapas.length == 1 && etapas[0].equals(DADOS)) fim = "Dados importados.";
            if (etapas.length == 1 && etapas[0].equals(INDICE)) fim = "Índice pronto. Ele entra na versão com \"Usar o resultado\".";
        } catch (Parado p) {
            fim = "Parado.";
        } catch (Throwable t) {
            fim = "Erro: " + (t.getMessage() == null ? t.toString() : t.getMessage());
        } finally {
            if (gl != null) {
                try {
                    gl.fechar();
                } catch (Throwable ignorado) {
                    // nada
                }
            }
        }
        e.terminar(fim);
        e.remover(ouvinte);
        if (trava != null && trava.isHeld()) trava.release();
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.notify(ID + 1, new Notification.Builder(this, CANAL).setSmallIcon(R.drawable.ic_notificacao)
                .setContentTitle("Laika: " + e.trabalho).setContentText(fim)
                .setStyle(new Notification.BigTextStyle().bigText(fim))
                .setContentIntent(abrirTela()).setAutoCancel(true).build());
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    private Motor esperarMotor() throws InterruptedException, IOException {
        Motor m = Motor.get(this);
        for (int i = 0; i < 300 && m.armazem == null; i++) Thread.sleep(100);
        if (m.armazem == null) throw new IOException("o app ainda está carregando");
        return m;
    }

    private void importarDados(Corpus corpus, Uri uri) throws IOException {
        TreinoEstado e = TreinoEstado.get();
        long total = Motor.tamanhoDoArquivo(this, uri);
        e.log("Importando " + Motor.nomeDoArquivo(this, uri) + (total > 0 ? String.format(Locale.getDefault(), " (%d MB)", total >> 20) : ""));
        try (InputStream is = getContentResolver().openInputStream(uri)) {
            if (is == null) throw new IOException("não consegui abrir o arquivo");
            String r = corpus.importarZip(is, total, (f, t) -> e.progresso(t > 0 ? (double) f / t : -1,
                    String.format(Locale.getDefault(), "Importando… %d MB", f >> 20)));
            e.log("Importado: " + r + ".");
        }
        e.log(corpus.resumo());
    }

    private void construirIndice(Corpus corpus, File pasta) throws IOException {
        File saida = new File(pasta, "saida");
        saida.mkdirs();
        File tmp = new File(saida, "laika_rag.db.tmp"), db = new File(saida, "laika_rag.db");
        tmp.delete();
        SQLiteConnection con = new BundledSQLiteDriver().open(tmp.getPath());
        try {
            ConstrutorIndice.construir(corpus, con, TreinoEstado.get());
        } finally {
            con.close();
        }
        db.delete();
        if (!tmp.renameTo(db)) throw new IOException("não consegui salvar o índice");
    }

    private void preTreino(GlAndroid gl, Corpus corpus, File pasta, Motor motor, Intent in) throws IOException {
        PreTreino.Opcoes op = new PreTreino.Opcoes();
        op.modo = PreTreino.Modo.valueOf(in.getStringExtra("modo"));
        op.preset = in.getStringExtra("preset");
        op.maxSteps = in.getIntExtra("maxSteps", 0);
        op.microLote = in.getIntExtra("microLote", 8);
        op.maxBytesTokenizer = 60L << 20;
        if (op.modo == PreTreino.Modo.CONTINUAR) {
            Armazem.Versao v = motor.armazem.atual();
            Armazem.Arquivo base = v.arquivos.get(Armazem.BASE);
            if (base == null) throw new IOException("a versão em uso não tem o modelo pré-treinado; escolha \"do zero\"");
            op.baseAtual = motor.armazem.abrir(base.ref);
            op.tokenizerAtual = motor.armazem.abrir(v.arquivos.get(Armazem.TOKENIZER).ref);
        }
        try {
            PreTreino.rodar(gl, corpus, pasta, op, TreinoEstado.get());
        } finally {
            if (op.baseAtual != null) op.baseAtual.close();
            if (op.tokenizerAtual != null) op.tokenizerAtual.close();
        }
    }

    private void fineTuning(GlAndroid gl, Corpus corpus, File pasta, Motor motor, Intent in) throws IOException {
        TreinoEstado e = TreinoEstado.get();
        FineTuning.Opcoes op = new FineTuning.Opcoes();
        op.epocas = in.getIntExtra("epocas", 2);
        op.microLote = in.getIntExtra("microLote", 8);
        op.maxTextoMb = in.getFloatExtra("maxTextoMb", 15);
        File saida = new File(pasta, "saida");
        File base = new File(saida, "laika_base.bin"), tok = new File(saida, "tokenizer.txt");
        boolean doResultado = in.getBooleanExtra("doResultado", true) && base.exists() && tok.exists();
        saida.mkdirs();
        if (!doResultado) {
            // O resultado precisa ser um conjunto que combina: copia o tokenizer e o modelo base em uso para saida/.
            Armazem.Versao v = motor.armazem.atual();
            Armazem.Arquivo b = v.arquivos.get(Armazem.BASE);
            if (b == null) throw new IOException("não há modelo pré-treinado (nem aqui nem na versão em uso)");
            e.log("Partindo do modelo pré-treinado da versão em uso (copiado para saida/).");
            try (InputStream i = motor.armazem.abrir(b.ref)) {
                Armazem.copiar(i, base, -1, null);
            }
            try (InputStream i = motor.armazem.abrir(v.arquivos.get(Armazem.TOKENIZER).ref)) {
                Armazem.copiar(i, tok, -1, null);
            }
        } else {
            e.log("Partindo do pré-treino feito aqui (saida/laika_base.bin).");
        }
        op.base = new java.io.FileInputStream(base);
        op.tokenizer = Corpus.lerTexto(tok);
        IndiceRag rag = null;
        if (in.getBooleanExtra("rag", true)) {
            File db = new File(saida, "laika_rag.db");
            if (!db.exists()) db = motor.arquivoDoIndiceAtual();
            if (db != null && db.exists()) {
                rag = new IndiceRag(abrirLeitura(db));
                e.log("RAG: usando " + (db.getName().equals("laika_rag.db") && db.getParentFile().equals(saida)
                        ? "o índice montado aqui" : "o índice da versão em uso") + ".");
            }
        }
        op.rag = rag;
        try {
            FineTuning.rodar(gl, corpus, pasta, op, e);
        } finally {
            op.base.close();
            if (rag != null) rag.close();
        }
    }

    private static SQLiteConnection abrirLeitura(File f) {
        return new BundledSQLiteDriver().open(f.getPath(), BundledSQLite.SQLITE_OPEN_READONLY);
    }

    // ---------- notificação ----------

    private void criarCanal() {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm.getNotificationChannel(CANAL) == null) {
            NotificationChannel c = new NotificationChannel(CANAL, "Treino da Laika", NotificationManager.IMPORTANCE_LOW);
            c.setDescription("Progresso do treino no celular");
            nm.createNotificationChannel(c);
        }
    }

    private PendingIntent abrirTela() {
        return PendingIntent.getActivity(this, 0, new Intent(this, TreinoActivity.class),
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    private Notification notificacao(String texto, double fracao) {
        Intent p = new Intent(this, TreinoService.class).setAction(PARAR);
        PendingIntent pp = PendingIntent.getService(this, 1, p, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Notification.Builder b = new Notification.Builder(this, CANAL)
                .setSmallIcon(R.drawable.ic_notificacao)
                .setContentTitle("Laika: " + TreinoEstado.get().trabalho)
                .setContentText(texto)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setContentIntent(abrirTela())
                .addAction(new Notification.Action.Builder(null, "Parar", pp).build());
        if (fracao >= 0) b.setProgress(1000, (int) (fracao * 1000), false);
        else b.setProgress(0, 0, true);
        return b.build();
    }

    private void notificar() {
        long agora = System.currentTimeMillis();
        TreinoEstado e = TreinoEstado.get();
        if (!e.rodando || agora - ultimaNotificacao < 2000) return;
        ultimaNotificacao = agora;
        getSystemService(NotificationManager.class).notify(ID, notificacao(e.texto.isEmpty() ? "Rodando…" : e.texto, e.fracao));
    }
}
