package com.brunodevpro.laika;

import android.app.Activity;
import android.content.res.ColorStateList;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

/**
 * O botão + no canto do campo de mensagem: resposta longa, modo completar texto e memória de IA, como os
 * "anexos e ferramentas" dos assistentes de conversa. O + fica azul quando resposta longa ou completar está ligado.
 */
final class MaisOpcoes {
    private final Activity tela;
    private final Motor motor;
    private final Runnable mudou;
    private PopupWindow janela;

    MaisOpcoes(Activity tela, Motor motor, Runnable mudou) {
        this.tela = tela;
        this.motor = motor;
        this.mudou = mudou;
    }

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, tela.getResources().getDisplayMetrics());
    }

    void mostrar(View ancora) {
        if (janela != null && janela.isShowing()) {
            janela.dismiss();
            return;
        }
        LinearLayout lista = new LinearLayout(tela);
        lista.setOrientation(LinearLayout.VERTICAL);
        lista.setPadding(dp(6), dp(6), dp(6), dp(6));
        caixa(lista, "Resposta longa", motor.respostasLongas, v -> motor.respostasLongas = v);
        if (motor.temBase) {
            caixa(lista, "Completar texto", motor.modoCompletar, v -> {
                motor.modoCompletar = v;
                motor.aviso(v ? "Modo completar texto: escreva o começo de um texto e a Laika continua "
                        + "(sem RAG nem memória)." : "Modo conversa.");
            });
        }
        caixa(lista, "Memória de IA", motor.usarHistorico, v -> motor.usarHistorico = v);

        janela = new PopupWindow(lista, dp(230), ViewGroup.LayoutParams.WRAP_CONTENT, true);
        janela.setBackgroundDrawable(tela.getDrawable(R.drawable.painel));
        janela.setElevation(dp(12));
        janela.setOutsideTouchable(true);
        lista.measure(View.MeasureSpec.makeMeasureSpec(dp(230), View.MeasureSpec.EXACTLY), View.MeasureSpec.UNSPECIFIED);
        // Abre logo acima do botão (o campo fica no rodapé, e o teclado pode estar aberto).
        int[] pos = new int[2];
        ancora.getLocationOnScreen(pos);
        janela.showAtLocation(ancora, Gravity.NO_GRAVITY, pos[0], Math.max(0, pos[1] - lista.getMeasuredHeight() - dp(8)));
    }

    void fechar() {
        if (janela != null) janela.dismiss();
    }

    /** Resposta longa ou completar texto ligados mudam a resposta: o + fica azul para lembrar. */
    boolean algoLigado() {
        return motor.respostasLongas || motor.modoCompletar;
    }

    private void caixa(LinearLayout pai, String rotulo, boolean marcada, java.util.function.Consumer<Boolean> aoMudar) {
        CheckBox cb = new CheckBox(tela);
        cb.setChecked(marcada);
        cb.setButtonTintList(ColorStateList.valueOf(tela.getColor(R.color.azul)));
        TextView t = new TextView(tela);
        t.setText(rotulo);
        t.setTextSize(15);
        t.setTextColor(tela.getColor(R.color.texto_laika));
        LinearLayout l = new LinearLayout(tela);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        l.setMinimumHeight(dp(44));
        l.setPadding(dp(4), 0, dp(10), 0);
        l.setBackgroundResource(R.drawable.item_menu);
        l.addView(cb);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1);
        lp.leftMargin = dp(4);
        l.addView(t, lp);
        l.setOnClickListener(v -> cb.toggle());
        cb.setOnCheckedChangeListener((b, v) -> {
            aoMudar.accept(v);
            motor.salvarOpcoes();
            mudou.run();
        });
        pai.addView(l);
    }
}
