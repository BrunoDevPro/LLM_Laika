package com.brunodevpro.laika;

import android.app.Activity;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

/**
 * As ações de uma mensagem (tocar ou segurar a bolha): uma barra flutuante com ícones,
 * logo acima da bolha (ou abaixo, se não couber), alinhada ao lado dela.
 */
final class AcoesBolha {
    private static final class Acao {
        final int icone;
        final String rotulo;
        final Runnable rodar;

        Acao(int icone, String rotulo, Runnable rodar) {
            this.icone = icone;
            this.rotulo = rotulo;
            this.rodar = rodar;
        }
    }

    private final Activity tela;
    private final List<Acao> acoes = new ArrayList<>();
    private PopupWindow janela;

    AcoesBolha(Activity tela) {
        this.tela = tela;
    }

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, tela.getResources().getDisplayMetrics());
    }

    AcoesBolha acao(int icone, String rotulo, Runnable rodar) {
        acoes.add(new Acao(icone, rotulo, rodar));
        return this;
    }

    /** direita: a bolha é do usuário (alinhada à direita). */
    void mostrar(View bolha, boolean direita) {
        LinearLayout barra = new LinearLayout(tela);
        barra.setOrientation(LinearLayout.HORIZONTAL);
        barra.setPadding(dp(6), dp(6), dp(6), dp(6));
        for (Acao a : acoes) {
            LinearLayout b = new LinearLayout(tela);
            b.setOrientation(LinearLayout.VERTICAL);
            b.setGravity(Gravity.CENTER);
            b.setBackgroundResource(R.drawable.item_menu);
            b.setPadding(dp(10), dp(8), dp(10), dp(6));
            b.setMinimumWidth(dp(68));
            ImageView i = new ImageView(tela);
            i.setImageResource(a.icone);
            b.addView(i, new LinearLayout.LayoutParams(dp(22), dp(22)));
            TextView t = new TextView(tela);
            t.setText(a.rotulo);
            t.setTextSize(12);
            t.setTextColor(tela.getColor(R.color.texto_laika));
            t.setGravity(Gravity.CENTER);
            t.setPadding(0, dp(4), 0, 0);
            b.addView(t);
            b.setContentDescription(a.rotulo);
            b.setOnClickListener(v -> {
                janela.dismiss();
                a.rodar.run();
            });
            barra.addView(b);
        }
        janela = new PopupWindow(barra, ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, true);
        janela.setBackgroundDrawable(tela.getDrawable(R.drawable.painel));
        janela.setElevation(dp(10));
        janela.setOutsideTouchable(true);
        janela.setAnimationStyle(android.R.style.Animation_Dialog);

        // Destaca a bolha enquanto a barra está aberta.
        bolha.setAlpha(0.75f);
        janela.setOnDismissListener(() -> bolha.setAlpha(1f));

        barra.measure(View.MeasureSpec.UNSPECIFIED, View.MeasureSpec.UNSPECIFIED);
        int largura = barra.getMeasuredWidth(), altura = barra.getMeasuredHeight();
        int[] onde = new int[2];
        bolha.getLocationInWindow(onde);
        View raiz = tela.getWindow().getDecorView();
        int larguraTela = raiz.getWidth();
        int x = direita ? onde[0] + bolha.getWidth() - largura : onde[0];
        x = Math.max(dp(8), Math.min(x, larguraTela - largura - dp(8)));
        int acima = onde[1] - altura - dp(6);
        // Acima da bolha se couber abaixo da barra do topo; senão, logo abaixo dela (sem passar do campo de texto).
        int y = acima > dp(96) ? acima
                : Math.max(dp(96), Math.min(onde[1] + bolha.getHeight() + dp(6), raiz.getHeight() - altura - dp(80)));
        janela.showAtLocation(raiz, Gravity.NO_GRAVITY, x, y);
    }
}
