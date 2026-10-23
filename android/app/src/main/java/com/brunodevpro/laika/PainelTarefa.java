package com.brunodevpro.laika;

import android.app.Activity;
import android.view.View;
import android.view.WindowManager;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.util.Locale;

/** A faixa de progresso das tarefas longas do Motor (importar, baixar, exportar), igual em todas as telas. */
final class PainelTarefa {
    private final Activity tela;
    private final Motor motor;
    private final View painel, cancelar;
    private final TextView texto;
    private final ProgressBar barra;

    PainelTarefa(Activity tela, Motor motor) {
        this.tela = tela;
        this.motor = motor;
        painel = tela.findViewById(R.id.tarefa);
        texto = tela.findViewById(R.id.tarefa_texto);
        barra = tela.findViewById(R.id.tarefa_barra);
        cancelar = tela.findViewById(R.id.tarefa_cancelar);
        cancelar.setOnClickListener(v -> motor.cancelarTarefa());
    }

    void atualizar() {
        String t = motor.tarefa;
        painel.setVisibility(t != null ? View.VISIBLE : View.GONE);
        cancelar.setVisibility(t != null && motor.tarefaCancelavel ? View.VISIBLE : View.GONE);
        if (t != null) {
            int p = motor.progresso;
            texto.setText(p >= 0 ? String.format(Locale.getDefault(), "%s %d%%", t, p) : t);
            barra.setIndeterminate(p < 0);
            if (p >= 0) barra.setProgress(p);
        }
        // Mantém a tela acesa durante as tarefas longas.
        if (motor.ocupado() && motor.tarefaCancelavel) tela.getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else tela.getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
}
