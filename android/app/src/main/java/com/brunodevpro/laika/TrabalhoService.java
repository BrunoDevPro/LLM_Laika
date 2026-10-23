package com.brunodevpro.laika;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;

import java.util.Locale;

/**
 * Mantém o app vivo (serviço em primeiro plano, com notificação) enquanto o Motor faz uma tarefa
 * longa: importar o zip do Colab, montar o índice do RAG, baixar um modelo, exportar um backup.
 * Assim a tarefa continua com a tela apagada ou com outro app aberto. Para sozinho no fim.
 */
public class TrabalhoService extends Service implements Motor.Ouvinte {
    private static final String CANAL = "trabalho", CANCELAR = "com.brunodevpro.laika.CANCELAR_TAREFA";
    private static final int ID = 21;

    private Motor motor;
    private PowerManager.WakeLock trava;
    private long inicio, ultimaNotificacao;
    private String ultimoAviso, ultimoTitulo;

    static void iniciar(Context c) {
        Intent i = new Intent(c, TrabalhoService.class);
        try {
            c.startForegroundService(i);
        } catch (RuntimeException proibido) {
            // app em segundo plano (Android 12+): a tarefa roda assim mesmo, só sem a notificação
        }
    }

    @Override
    public IBinder onBind(Intent i) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        motor = Motor.get(this);
        inicio = System.currentTimeMillis();
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm.getNotificationChannel(CANAL) == null) {
            NotificationChannel c = new NotificationChannel(CANAL, "Importações e downloads", NotificationManager.IMPORTANCE_LOW);
            c.setDescription("Progresso das tarefas longas da Laika");
            nm.createNotificationChannel(c);
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && CANCELAR.equals(intent.getAction())) {
            motor.cancelarTarefa();
            return START_NOT_STICKY;
        }
        Notification n = notificacao();
        if (Build.VERSION.SDK_INT >= 29) startForeground(ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
        else startForeground(ID, n);
        if (trava == null) {
            trava = getSystemService(PowerManager.class).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "laika:trabalho");
            trava.acquire(6L * 3600 * 1000);
        }
        motor.adicionarOuvinte(this);
        if (!motor.ocupado()) terminar();
        return START_NOT_STICKY;
    }

    private Notification notificacao() {
        String t = motor.tarefa == null ? "Terminando…" : motor.tarefa;
        int p = motor.progresso;
        Notification.Builder b = new Notification.Builder(this, CANAL)
                .setSmallIcon(R.drawable.ic_notificacao)
                .setContentTitle("Laika")
                .setContentText(p >= 0 ? String.format(Locale.getDefault(), "%s %d%%", t, p) : t)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setContentIntent(PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class),
                        PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT));
        if (p >= 0) b.setProgress(100, p, false);
        else b.setProgress(0, 0, true);
        if (motor.tarefaCancelavel) {
            PendingIntent pc = PendingIntent.getService(this, 1, new Intent(this, TrabalhoService.class).setAction(CANCELAR),
                    PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
            b.addAction(new Notification.Action.Builder(null, "Cancelar", pc).build());
        }
        return b.build();
    }

    @Override
    public void estadoMudou() {
        if (!motor.ocupado()) {
            terminar();
            return;
        }
        long agora = System.currentTimeMillis();
        if (agora - ultimaNotificacao < 1000) return;
        ultimaNotificacao = agora;
        getSystemService(NotificationManager.class).notify(ID, notificacao());
    }

    @Override
    public void aviso(String titulo, String texto) {
        ultimoTitulo = titulo;
        ultimoAviso = texto;
    }

    private void terminar() {
        motor.removerOuvinte(this);
        if (trava != null && trava.isHeld()) trava.release();
        trava = null;
        stopForeground(STOP_FOREGROUND_REMOVE);
        // Tarefa longa: talvez o usuário tenha saído do app; deixa o resultado numa notificação.
        if (ultimoAviso != null && System.currentTimeMillis() - inicio > 20_000) {
            getSystemService(NotificationManager.class).notify(ID + 1, new Notification.Builder(this, CANAL)
                    .setSmallIcon(R.drawable.ic_notificacao)
                    .setContentTitle(ultimoTitulo != null ? ultimoTitulo : "Laika")
                    .setContentText(ultimoAviso)
                    .setStyle(new Notification.BigTextStyle().bigText(ultimoAviso))
                    .setAutoCancel(true)
                    .setContentIntent(PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class),
                            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT))
                    .build());
        }
        stopSelf();
    }

    @Override
    public void onTimeout(int startId, int tipo) {
        // Android 15: limite de horas para serviços de transferência de dados.
        terminar();
    }

    @Override
    public void onDestroy() {
        motor.removerOuvinte(this);
        if (trava != null && trava.isHeld()) trava.release();
        super.onDestroy();
    }
}
