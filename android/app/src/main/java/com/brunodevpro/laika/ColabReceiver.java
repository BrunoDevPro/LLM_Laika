package com.brunodevpro.laika;

import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.widget.Toast;

import android.os.Handler;
import android.os.Looper;

import java.io.IOException;

/** Botão "Já autorizei" da notificação: avisa a execução do Colab que o Google Drive foi liberado. */
public class ColabReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent intent) {
        if (!Colab.DRIVE_OK.equals(intent.getAction())) return;
        long id = intent.getLongExtra("id", 0);
        PendingResult fim = goAsync();
        Context app = c.getApplicationContext();
        new Thread(() -> {
            String msg;
            try {
                Colab.github(app).avisarDriveAutorizado(Colab.ramo(app), id);
                msg = "Aviso enviado: o Colab continua a montagem do Drive.";
                app.getSystemService(NotificationManager.class).cancel(4000 + (int) (id % 1000) * 2);
            } catch (IOException e) {
                msg = "Não consegui avisar o Colab: " + e.getMessage();
            }
            String m = msg;
            new Handler(Looper.getMainLooper()).post(() -> Toast.makeText(app, m, Toast.LENGTH_LONG).show());
            fim.finish();
        }).start();
    }
}
