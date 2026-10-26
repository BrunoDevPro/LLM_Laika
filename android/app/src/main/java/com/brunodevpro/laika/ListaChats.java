package com.brunodevpro.laika;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.text.InputFilter;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.brunodevpro.laika.core.Chats;

import java.util.ArrayList;
import java.util.List;

/**
 * A lista de chats, num painel que abre pela esquerda (como nos assistentes de conversa): "Novo chat", os chats
 * do mais recente para o mais antigo e, embaixo, os arquivados. Um toque abre; segurar renomeia, arquiva ou apaga.
 * Arrastar para a esquerda (ou tocar fora) fecha.
 */
final class ListaChats {
    private final Activity tela;
    private final Motor motor;
    private Dialog janela;
    private LinearLayout lista;
    private boolean verArquivados;

    ListaChats(Activity tela, Motor motor) {
        this.tela = tela;
        this.motor = motor;
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

    boolean aberta() {
        return janela != null && janela.isShowing();
    }

    void fechar() {
        if (janela != null) janela.dismiss();
    }

    void mostrar() {
        LinearLayout raiz = new Arrastavel(tela, this::fechar);
        raiz.setOrientation(LinearLayout.VERTICAL);
        raiz.setBackgroundColor(tela.getColor(R.color.fundo));
        raiz.setPadding(dp(14), dp(40), dp(14), dp(16));
        raiz.addView(texto("Chats", 22, R.color.topo_texto, true));

        LinearLayout novo = new LinearLayout(tela);
        novo.setOrientation(LinearLayout.HORIZONTAL);
        novo.setGravity(Gravity.CENTER_VERTICAL);
        novo.setBackgroundResource(R.drawable.botao_primario);
        novo.setPadding(dp(14), dp(10), dp(14), dp(10));
        ImageView ic = new ImageView(tela);
        ic.setImageResource(R.drawable.ic_novo_chat);
        novo.addView(ic, new LinearLayout.LayoutParams(dp(20), dp(20)));
        TextView tn = texto("Novo chat", 15, R.color.texto_usuario, true);
        LinearLayout.LayoutParams lpt = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lpt.leftMargin = dp(10);
        novo.addView(tn, lpt);
        novo.setOnClickListener(v -> {
            fechar();
            motor.novoChat();
        });
        LinearLayout.LayoutParams lpn = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lpn.topMargin = dp(14);
        lpn.bottomMargin = dp(10);
        raiz.addView(novo, lpn);

        lista = new LinearLayout(tela);
        lista.setOrientation(LinearLayout.VERTICAL);
        ScrollView rolagem = new ScrollView(tela);
        rolagem.addView(lista);
        raiz.addView(rolagem, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));
        atualizar();

        janela = new Dialog(tela);
        janela.requestWindowFeature(Window.FEATURE_NO_TITLE);
        janela.setContentView(raiz);
        Window w = janela.getWindow();
        if (w != null) {
            w.setBackgroundDrawable(new ColorDrawable(0));
            int largura = Math.min(dp(280), (int) (tela.getResources().getDisplayMetrics().widthPixels * 0.72));
            w.setLayout(largura, ViewGroup.LayoutParams.MATCH_PARENT);
            w.setGravity(Gravity.START);
            w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            w.setDimAmount(0.4f);
        }
        janela.show();
        // Entra deslizando pela esquerda.
        raiz.setTranslationX(-dp(280));
        raiz.animate().translationX(0).setDuration(180).start();
    }

    /** O painel acompanha o dedo para a esquerda; soltando depois de um terço da largura, fecha. */
    private static final class Arrastavel extends LinearLayout {
        private final int folga;
        private final Runnable fechar;
        private float x0, y0;

        Arrastavel(android.content.Context c, Runnable fechar) {
            super(c);
            folga = android.view.ViewConfiguration.get(c).getScaledTouchSlop();
            this.fechar = fechar;
        }

        @Override
        public boolean onInterceptTouchEvent(android.view.MotionEvent e) {
            if (e.getActionMasked() == android.view.MotionEvent.ACTION_DOWN) {
                x0 = e.getRawX();
                y0 = e.getRawY();
            } else if (e.getActionMasked() == android.view.MotionEvent.ACTION_MOVE) {
                float dx = e.getRawX() - x0, dy = e.getRawY() - y0;
                return dx < -folga && Math.abs(dx) > Math.abs(dy);  // arrasto para a esquerda: o painel assume
            }
            return false;
        }

        @Override
        public boolean onTouchEvent(android.view.MotionEvent e) {
            switch (e.getActionMasked()) {
                case android.view.MotionEvent.ACTION_DOWN:
                    x0 = e.getRawX();
                    return true;
                case android.view.MotionEvent.ACTION_MOVE:
                    setTranslationX(Math.min(0, e.getRawX() - x0));
                    return true;
                case android.view.MotionEvent.ACTION_UP:
                case android.view.MotionEvent.ACTION_CANCEL:
                    if (getTranslationX() < -getWidth() / 3f) {
                        animate().translationX(-getWidth()).setDuration(120).withEndAction(fechar).start();
                    } else {
                        animate().translationX(0).setDuration(120).start();
                    }
                    return true;
                default:
                    return super.onTouchEvent(e);
            }
        }
    }

    /** Remonta a lista (chamado também quando um título chega ou um chat some). */
    void atualizar() {
        if (lista == null) return;
        lista.removeAllViews();
        List<Chats.Chat> ativos = new ArrayList<>(), arquivados = new ArrayList<>();
        for (Chats.Chat c : motor.listaChats()) (c.arquivado ? arquivados : ativos).add(c);
        String atual = motor.idChatAtual();
        for (Chats.Chat c : ativos) linha(c, c.id.equals(atual));
        if (arquivados.isEmpty()) return;
        TextView cab = texto((verArquivados ? "▾ " : "▸ ") + "Arquivados (" + arquivados.size() + ")", 14,
                R.color.topo_sub, true);
        cab.setPadding(dp(8), dp(16), dp(8), dp(8));
        cab.setOnClickListener(v -> {
            verArquivados = !verArquivados;
            atualizar();
        });
        lista.addView(cab);
        if (verArquivados) for (Chats.Chat c : arquivados) linha(c, c.id.equals(atual));
    }

    private void linha(Chats.Chat c, boolean aberto) {
        TextView t = texto(c.titulo, 15, aberto ? R.color.azul : R.color.texto_laika, aberto);
        t.setMaxLines(1);
        t.setEllipsize(android.text.TextUtils.TruncateAt.END);
        t.setPadding(dp(12), dp(12), dp(12), dp(12));
        t.setBackgroundResource(aberto ? R.drawable.cartao_atual : R.drawable.item_menu);
        if (c.arquivado) t.setAlpha(0.7f);
        t.setOnClickListener(v -> {
            fechar();
            if (!aberto) motor.usarChat(c.id);
        });
        t.setOnLongClickListener(v -> {
            opcoes(c);
            return true;
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(2);
        lista.addView(t, lp);
    }

    private void opcoes(Chats.Chat c) {
        String[] itens = {"Renomear", c.arquivado ? "Desarquivar" : "Arquivar", "Apagar"};
        new AlertDialog.Builder(tela).setTitle(c.titulo).setItems(itens, (d, i) -> {
            if (i == 0) renomear(c);
            else if (i == 1) motor.arquivarChat(c.id, !c.arquivado);
            else apagar(c);
        }).show();
    }

    private void renomear(Chats.Chat c) {
        EditText campo = new EditText(tela);
        campo.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        campo.setFilters(new InputFilter[]{new InputFilter.LengthFilter(60)});
        campo.setText(c.titulo);
        campo.setSelectAllOnFocus(true);
        FrameLayout moldura = new FrameLayout(tela);
        moldura.setPadding(dp(20), dp(8), dp(20), 0);
        moldura.addView(campo);
        AlertDialog d = new AlertDialog.Builder(tela).setTitle("Renomear o chat").setView(moldura)
                .setPositiveButton("Renomear", (di, w) -> {
                    String t = campo.getText().toString().trim();
                    if (!t.isEmpty()) motor.renomearChat(c.id, t);
                })
                .setNegativeButton("Cancelar", null).create();
        if (d.getWindow() != null) d.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE);
        d.show();
        campo.requestFocus();
    }

    private void apagar(Chats.Chat c) {
        new AlertDialog.Builder(tela).setTitle("Apagar \"" + c.titulo + "\"?")
                .setMessage("A conversa e a memória deste chat somem do celular.")
                .setPositiveButton("Apagar", (d, w) -> motor.apagarChat(c.id))
                .setNegativeButton("Cancelar", null).show();
    }
}
