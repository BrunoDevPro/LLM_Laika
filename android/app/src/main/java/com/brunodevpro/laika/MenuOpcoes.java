package com.brunodevpro.laika;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.os.SystemClock;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;

import java.util.Locale;
import java.util.function.IntConsumer;
import java.util.function.IntFunction;

/**
 * O menu da tela de conversa: as opções de marcar (num grupo que abre e fecha), as barrinhas de
 * criatividade e de tamanho das respostas, e os atalhos (memória, versões, treinar, limpar).
 */
final class MenuOpcoes {
    interface Acoes {
        void memoria();

        void versoes();

        void treinar();

        void limpar();

        /** Alguma opção mudou (a tela atualiza a linha de estado). */
        void mudou();
    }

    private final Activity tela;
    private final Motor motor;
    private final Acoes acoes;
    private final SharedPreferences prefs;
    private PopupWindow janela;
    /** Quando o menu fechou: o toque fora que fecha o menu não pode reabri-lo no mesmo botão. */
    private long fechadoEm;

    MenuOpcoes(Activity tela, Motor motor, Acoes acoes) {
        this.tela = tela;
        this.motor = motor;
        this.acoes = acoes;
        prefs = tela.getSharedPreferences("tela", Context.MODE_PRIVATE);
    }

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, tela.getResources().getDisplayMetrics());
    }

    private TextView texto(String s, float tamanho, int cor, boolean negrito) {
        TextView t = new TextView(tela);
        t.setText(s);
        t.setTextSize(tamanho);
        t.setTextColor(tela.getColor(cor));
        if (negrito) t.setTypeface(t.getTypeface(), Typeface.BOLD);
        return t;
    }

    void mostrar(View ancora) {
        if (janela != null && janela.isShowing()) {
            janela.dismiss();
            return;
        }
        if (SystemClock.uptimeMillis() - fechadoEm < 300) return;
        LinearLayout lista = new LinearLayout(tela);
        lista.setOrientation(LinearLayout.VERTICAL);
        lista.setPadding(dp(8), dp(8), dp(8), dp(8));

        montarOpcoes(lista);
        divisoria(lista);
        barra(lista, "Criatividade", "mais previsível", "mais criativa",
                (int) Math.round(Motor.TEMP_MIN * 100), (int) Math.round(Motor.TEMP_MAX * 100),
                (int) Math.round(motor.temperatura * 100),
                v -> String.format(Locale.getDefault(), "%.2f", v / 100.0),
                v -> motor.temperatura = v / 100.0);
        barra(lista, "Tamanho das respostas", "curtas", "longas", Motor.TAMANHO_MIN, motor.tamanhoMaximo(),
                Math.min(motor.tamanhoResposta, motor.tamanhoMaximo()), v -> "até " + v + " tokens",
                v -> motor.tamanhoResposta = v);
        TextView dica = texto("Com mais tokens, a Laika tenta escrever respostas mais longas (e sobra menos "
                + "espaço para lembrar a conversa).", 11, R.color.aviso, false);
        dica.setPadding(dp(12), 0, dp(12), dp(6));
        lista.addView(dica);
        divisoria(lista);
        item(lista, R.drawable.ic_lampada, "O que a Laika lembra de mim", R.color.texto_laika, acoes::memoria);
        item(lista, R.drawable.ic_versoes, "Versões e backups", R.color.texto_laika, acoes::versoes);
        item(lista, R.drawable.ic_treinar, "Treinar", R.color.texto_laika, acoes::treinar);
        item(lista, R.drawable.ic_limpar, "Limpar conversa", R.color.perigo, acoes::limpar);

        ScrollView rolagem = new ScrollView(tela);
        rolagem.addView(lista);
        int largura = Math.min(dp(330), tela.getResources().getDisplayMetrics().widthPixels - dp(24));
        janela = new PopupWindow(rolagem, largura, ViewGroup.LayoutParams.WRAP_CONTENT, true);
        janela.setBackgroundDrawable(tela.getDrawable(R.drawable.painel));
        janela.setElevation(dp(12));
        janela.setOutsideTouchable(true);
        janela.setOnDismissListener(() -> fechadoEm = SystemClock.uptimeMillis());
        janela.showAsDropDown(ancora, -dp(4), 0, Gravity.END);
    }

    void fechar() {
        if (janela != null) janela.dismiss();
    }

    private void divisoria(LinearLayout pai) {
        View v = new View(tela);
        v.setBackgroundColor(tela.getColor(R.color.divisoria));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(1));
        lp.setMargins(dp(8), dp(6), dp(8), dp(6));
        pai.addView(v, lp);
    }

    private LinearLayout linha(LinearLayout pai, int icone, String rotulo, int cor) {
        LinearLayout l = new LinearLayout(tela);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        l.setMinimumHeight(dp(46));
        l.setPadding(dp(12), 0, dp(12), 0);
        l.setBackgroundResource(R.drawable.item_menu);
        ImageView i = new ImageView(tela);
        i.setImageResource(icone);
        l.addView(i, new LinearLayout.LayoutParams(dp(22), dp(22)));
        TextView t = texto(rotulo, 15, cor, false);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1);
        lp.leftMargin = dp(14);
        l.addView(t, lp);
        pai.addView(l, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return l;
    }

    private void item(LinearLayout pai, int icone, String rotulo, int cor, Runnable acao) {
        linha(pai, icone, rotulo, cor).setOnClickListener(v -> {
            fechar();
            acao.run();
        });
    }

    /** "Opções": as caixinhas de marcar, num grupo que abre e fecha (lembra se ficou aberto). */
    private void montarOpcoes(LinearLayout pai) {
        LinearLayout cabeca = linha(pai, R.drawable.ic_ajustes, "Opções", R.color.texto_laika);
        ((TextView) cabeca.getChildAt(1)).setTypeface(null, Typeface.BOLD);
        TextView resumo = texto("", 12, R.color.aviso, false);
        cabeca.addView(resumo);
        ImageView seta = new ImageView(tela);
        seta.setImageResource(R.drawable.ic_expandir);
        LinearLayout.LayoutParams lps = new LinearLayout.LayoutParams(dp(22), dp(22));
        lps.leftMargin = dp(6);
        cabeca.addView(seta, lps);

        LinearLayout grupo = new LinearLayout(tela);
        grupo.setOrientation(LinearLayout.VERTICAL);
        grupo.setPadding(dp(8), 0, 0, dp(4));
        pai.addView(grupo);

        caixa(grupo, "Mostrar fontes", "*Título no fim das respostas", motor.mostrarFontes, v -> motor.mostrarFontes = v);
        caixa(grupo, "Buscar nos textos (RAG)", "Wikipédia, livros e textos do app", motor.usarRag, v -> motor.usarRag = v);
        caixa(grupo, "Memória do usuário", "Seu nome, cidade, gostos e \"lembre que…\"", motor.usarMemoria,
                v -> motor.usarMemoria = v);
        caixa(grupo, "Memória de IA", "Lembra das últimas 5 mensagens da conversa", motor.usarHistorico,
                v -> motor.usarHistorico = v);
        if (motor.temBase) {
            caixa(grupo, "Modo completar texto", "Escreva um começo e a Laika continua", motor.modoCompletar, v -> {
                motor.modoCompletar = v;
                motor.aviso(v ? "Modo completar texto: escreva o começo de um texto e a Laika continua "
                        + "(sem RAG nem memória)." : "Modo conversa.");
            });
        }

        Runnable atualizar = () -> {
            boolean aberto = prefs.getBoolean("opcoes_abertas", false);
            grupo.setVisibility(aberto ? View.VISIBLE : View.GONE);
            seta.setRotation(aberto ? 180 : 0);
            int ligadas = (motor.mostrarFontes ? 1 : 0) + (motor.usarRag ? 1 : 0) + (motor.usarMemoria ? 1 : 0)
                    + (motor.usarHistorico ? 1 : 0) + (motor.modoCompletar ? 1 : 0);
            resumo.setText(aberto ? "" : ligadas + " ligada" + (ligadas == 1 ? "" : "s"));
        };
        atualizar.run();
        cabeca.setOnClickListener(v -> {
            prefs.edit().putBoolean("opcoes_abertas", !prefs.getBoolean("opcoes_abertas", false)).apply();
            atualizar.run();
        });
    }

    private void caixa(LinearLayout pai, String rotulo, String explicacao, boolean marcada,
                       java.util.function.Consumer<Boolean> aoMudar) {
        CheckBox cb = new CheckBox(tela);
        cb.setChecked(marcada);
        cb.setButtonTintList(ColorStateList.valueOf(tela.getColor(R.color.azul)));
        LinearLayout textos = new LinearLayout(tela);
        textos.setOrientation(LinearLayout.VERTICAL);
        textos.addView(texto(rotulo, 15, R.color.texto_laika, false));
        textos.addView(texto(explicacao, 12, R.color.aviso, false));
        LinearLayout l = new LinearLayout(tela);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        l.setPadding(dp(4), dp(4), dp(8), dp(4));
        l.setBackgroundResource(R.drawable.item_menu);
        l.addView(cb);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1);
        lp.leftMargin = dp(4);
        l.addView(textos, lp);
        l.setOnClickListener(v -> cb.toggle());
        cb.setOnCheckedChangeListener((b, v) -> {
            aoMudar.accept(v);
            motor.salvarOpcoes();
            acoes.mudou();
        });
        pai.addView(l);
    }

    /** Uma barrinha deslizante (com − e + para o ajuste fino), de min a max, passo 1. */
    private void barra(LinearLayout pai, String titulo, String esquerda, String direita, int min, int max, int valor,
                       IntFunction<String> mostrar, IntConsumer aoMudar) {
        LinearLayout cab = new LinearLayout(tela);
        cab.setOrientation(LinearLayout.HORIZONTAL);
        cab.setPadding(dp(12), dp(8), dp(12), 0);
        cab.addView(texto(titulo, 15, R.color.texto_laika, false),
                new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        TextView atual = texto(mostrar.apply(valor), 14, R.color.azul, true);
        cab.addView(atual);
        pai.addView(cab);

        SeekBar sb = new SeekBar(tela);
        sb.setMin(min);
        sb.setMax(max);
        sb.setProgress(Math.max(min, Math.min(max, valor)));
        ColorStateList azul = ColorStateList.valueOf(tela.getColor(R.color.azul));
        sb.setProgressTintList(azul);
        sb.setThumbTintList(azul);
        sb.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar s, int v, boolean doUsuario) {
                atual.setText(mostrar.apply(v));
                aoMudar.accept(v);
                if (!doUsuario) motor.salvarOpcoes();  // botões − e +
            }

            @Override
            public void onStartTrackingTouch(SeekBar s) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar s) {
                motor.salvarOpcoes();
            }
        });
        LinearLayout l = new LinearLayout(tela);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        l.setPadding(dp(4), 0, dp(4), 0);
        l.addView(passo(R.drawable.ic_menos, "Diminuir " + titulo.toLowerCase(Locale.ROOT), () -> sb.setProgress(sb.getProgress() - 1)));
        l.addView(sb, new LinearLayout.LayoutParams(0, dp(36), 1));
        l.addView(passo(R.drawable.ic_mais, "Aumentar " + titulo.toLowerCase(Locale.ROOT), () -> sb.setProgress(sb.getProgress() + 1)));
        pai.addView(l);

        LinearLayout pontas = new LinearLayout(tela);
        pontas.setOrientation(LinearLayout.HORIZONTAL);
        pontas.setPadding(dp(44), 0, dp(44), dp(4));
        pontas.addView(texto(esquerda, 11, R.color.aviso, false),
                new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        pontas.addView(texto(direita, 11, R.color.aviso, false));
        pai.addView(pontas);
    }

    private ImageButton passo(int icone, String descricao, Runnable acao) {
        ImageButton b = new ImageButton(tela);
        b.setImageResource(icone);
        b.setBackgroundResource(R.drawable.botao_redondo);
        b.setContentDescription(descricao);
        b.setOnClickListener(v -> acao.run());
        b.setLayoutParams(new LinearLayout.LayoutParams(dp(32), dp(32)));
        return b;
    }
}
