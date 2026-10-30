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
    /** O painel que desliza (null com a gaveta fechada) e a largura dele. */
    private View painel;
    private int largura;
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

    /** Fecha na hora (ao escolher um chat). */
    void fechar() {
        if (janela != null) janela.dismiss();
        painel = null;
    }

    void mostrar() {
        if (aberta()) return;
        criar();
        painel.setTranslationX(-largura);
        abrirAnimado();
    }

    /** Começa a abrir com o dedo, arrastando da tela do chat para a direita: o painel acompanha o dedo. */
    void comecarArrasto() {
        if (aberta()) return;
        criar();
        painel.setTranslationX(-largura);
        escurecer(0);
    }

    /** dx: quanto o dedo andou para a direita desde que o arrasto começou. */
    void arrastar(float dx) {
        if (painel == null) return;
        float t = Math.max(-largura, Math.min(0, dx - largura));
        painel.setTranslationX(t);
        escurecer(1 + t / largura);
    }

    /** Soltou o dedo: abre se passou de ~40% ou se o gesto foi rápido para a direita; senão volta. */
    void soltar(float velocidadeX) {
        if (painel == null) return;
        float t = painel.getTranslationX();
        if (velocidadeX > dp(600) || (velocidadeX > -dp(600) && t > -largura * 0.6f)) abrirAnimado();
        else fecharAnimado();
    }

    private void criar() {
        largura = Math.min(dp(280), (int) (tela.getResources().getDisplayMetrics().widthPixels * 0.72));
        LinearLayout raiz = new LinearLayout(tela);
        painel = raiz;
        raiz.setOrientation(LinearLayout.VERTICAL);
        raiz.setBackgroundColor(tela.getColor(R.color.fundo));
        raiz.setPadding(dp(14), dp(40), dp(14), dp(16));
        raiz.setClickable(true);  // toques no painel não fecham (só fora dele)
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
        rolagem.setVerticalScrollBarEnabled(true);
        rolagem.addView(lista);
        raiz.addView(rolagem, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));
        atualizar();

        // A janela ocupa a tela toda: o painel fica à esquerda e o resto (escurecido) também responde ao dedo
        // (tocar fecha; arrastar para a esquerda, de qualquer ponto, fecha).
        FrameLayout tudo = new Arrastavel(tela, this);
        tudo.addView(raiz, new FrameLayout.LayoutParams(largura, ViewGroup.LayoutParams.MATCH_PARENT, Gravity.START));
        janela = new Dialog(tela);
        janela.requestWindowFeature(Window.FEATURE_NO_TITLE);
        janela.setContentView(tudo);
        janela.setOnDismissListener(d -> painel = null);
        Window w = janela.getWindow();
        if (w != null) {
            w.setBackgroundDrawable(new ColorDrawable(0));
            w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
            w.setGravity(Gravity.START);
            w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            w.setDimAmount(0f);
            w.setWindowAnimations(0);
        }
        janela.show();
    }

    private void abrirAnimado() {
        if (painel == null) return;
        View p = painel;
        p.animate().translationX(0).setDuration(170)
                .setUpdateListener(a -> escurecer(1 + p.getTranslationX() / largura)).start();
    }

    private void fecharAnimado() {
        if (painel == null) return;
        View p = painel;
        p.animate().translationX(-largura).setDuration(150)
                .setUpdateListener(a -> escurecer(1 + p.getTranslationX() / largura))
                .withEndAction(this::fechar).start();
    }

    /** O fundo escurece junto com o painel (0 = fechado, 1 = aberto). */
    private void escurecer(float f) {
        Window w = janela == null ? null : janela.getWindow();
        if (w != null) w.setDimAmount(0.4f * Math.max(0f, Math.min(1f, f)));
    }

    /** Arrastar para a esquerda de qualquer ponto (no painel ou fora dele) leva o painel junto; tocar fora fecha. */
    private static final class Arrastavel extends FrameLayout {
        private final int folga;
        private final ListaChats lista;
        private float x0, y0;
        private boolean arrastou;
        private android.view.VelocityTracker vt;

        Arrastavel(android.content.Context c, ListaChats lista) {
            super(c);
            folga = android.view.ViewConfiguration.get(c).getScaledTouchSlop();
            this.lista = lista;
        }

        @Override
        public boolean onInterceptTouchEvent(android.view.MotionEvent e) {
            if (e.getActionMasked() == android.view.MotionEvent.ACTION_DOWN) {
                x0 = e.getRawX();
                y0 = e.getRawY();
                arrastou = false;
            } else if (e.getActionMasked() == android.view.MotionEvent.ACTION_MOVE) {
                float dx = e.getRawX() - x0, dy = e.getRawY() - y0;
                return dx < -folga && Math.abs(dx) > Math.abs(dy);  // arrasto para a esquerda: o painel vai junto
            }
            return false;
        }

        @Override
        public boolean onTouchEvent(android.view.MotionEvent e) {
            if (vt == null) vt = android.view.VelocityTracker.obtain();
            vt.addMovement(e);
            View p = lista.painel;
            switch (e.getActionMasked()) {
                case android.view.MotionEvent.ACTION_DOWN:
                    x0 = e.getRawX();
                    y0 = e.getRawY();
                    arrastou = false;
                    return true;
                case android.view.MotionEvent.ACTION_MOVE: {
                    float dx = e.getRawX() - x0;
                    if (Math.abs(dx) > folga || Math.abs(e.getRawY() - y0) > folga) arrastou = true;
                    if (p != null) {
                        p.setTranslationX(Math.max(-lista.largura, Math.min(0, dx)));
                        lista.escurecer(1 + p.getTranslationX() / lista.largura);
                    }
                    return true;
                }
                case android.view.MotionEvent.ACTION_UP:
                case android.view.MotionEvent.ACTION_CANCEL: {
                    vt.computeCurrentVelocity(1000);
                    float vx = vt.getXVelocity();
                    vt.recycle();
                    vt = null;
                    if (p == null) return true;
                    if (!arrastou) {
                        lista.fecharAnimado();  // um toque fora do painel
                    } else if (vx < -lista.dp(600) || (vx < lista.dp(600) && p.getTranslationX() < -lista.largura / 3f)) {
                        lista.fecharAnimado();
                    } else {
                        lista.abrirAnimado();
                    }
                    return true;
                }
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
