package com.brunodevpro.laika;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Intent;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.brunodevpro.laika.core.Armazem;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Painel flutuante (sobe do rodapé, sem trocar de tela) com todos os modelos do celular: o em uso (uma vez só) e
 * os backups, pelo apelido. Um toque troca de modelo; segurar dá um apelido; "Versões e backups" abre a tela
 * completa (detalhes, importar, exportar...).
 */
final class SeletorModelos {
    private final Activity tela;
    private final Motor motor;

    SeletorModelos(Activity tela, Motor motor) {
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

    static String data(long t) {
        return new SimpleDateFormat("dd/MM/yyyy HH:mm", new Locale("pt", "BR")).format(new Date(t));
    }

    void mostrar() {
        Armazem armazem = motor.armazem;
        if (armazem == null) return;
        Armazem.Versao atual, igual;
        List<Armazem.Versao> backups;
        try {
            atual = armazem.atual();
            backups = armazem.backups();
            igual = armazem.backupComMesmosArquivos();
        } catch (IOException e) {
            new AlertDialog.Builder(tela).setMessage("Erro ao ler os modelos: " + e.getMessage())
                    .setPositiveButton("OK", null).show();
            return;
        }

        Dialog d = new Dialog(tela);
        d.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout raiz = new LinearLayout(tela);
        raiz.setOrientation(LinearLayout.VERTICAL);
        raiz.setBackgroundResource(R.drawable.folha);
        raiz.setPadding(dp(16), dp(10), dp(16), dp(16));

        View alca = new View(tela);
        alca.setBackgroundResource(R.drawable.alca);
        LinearLayout.LayoutParams la = new LinearLayout.LayoutParams(dp(40), dp(4));
        la.gravity = Gravity.CENTER_HORIZONTAL;
        la.bottomMargin = dp(12);
        raiz.addView(alca, la);
        TextView titulo = texto("Modelos", 20, R.color.topo_texto, true);
        titulo.setPadding(0, 0, 0, dp(10));
        raiz.addView(titulo);

        // O modelo em uso aparece uma vez só: o backup com os mesmos arquivos é ele.
        LinearLayout lista = new LinearLayout(tela);
        lista.setOrientation(LinearLayout.VERTICAL);
        cartao(lista, atual, true, null, v -> {
            d.dismiss();
            pedirApelido(tela, motor, null, atual);
            return true;
        });
        for (Armazem.Versao b : backups) {
            if (igual != null && igual.id.equals(b.id)) continue;
            cartao(lista, b, false, v -> {
                d.dismiss();
                confirmarUso(tela, motor, b);
            }, v -> {
                d.dismiss();
                pedirApelido(tela, motor, b.id, b);
                return true;
            });
        }
        ScrollView rolagem = new ScrollView(tela);
        rolagem.addView(lista);
        int maxAltura = (int) (tela.getResources().getDisplayMetrics().heightPixels * 0.55);
        raiz.addView(rolagem, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        rolagem.post(() -> {
            if (rolagem.getHeight() > maxAltura) {
                rolagem.getLayoutParams().height = maxAltura;
                rolagem.requestLayout();
            }
        });

        LinearLayout botoes = new LinearLayout(tela);
        botoes.setOrientation(LinearLayout.HORIZONTAL);
        botoes.setPadding(0, dp(12), 0, 0);
        botao(botoes, "Versões e backups", true, v -> {
            d.dismiss();
            tela.startActivity(new Intent(tela, VersoesActivity.class));
        });
        botao(botoes, "Treinar", false, v -> {
            d.dismiss();
            tela.startActivity(new Intent(tela, ColabActivity.class));
        });
        raiz.addView(botoes);

        d.setContentView(raiz);
        Window w = d.getWindow();
        if (w != null) {
            w.setBackgroundDrawable(new ColorDrawable(0));
            w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            w.setGravity(Gravity.BOTTOM);
            w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            w.setDimAmount(0.4f);
            w.setWindowAnimations(android.R.style.Animation_InputMethod);
        }
        d.show();
    }

    /** O apelido em destaque e, se houver, o nome oficial embaixo, menor e em cinza. Segurar: dar um apelido. */
    private void cartao(LinearLayout pai, Armazem.Versao v, boolean emUso, View.OnClickListener acao,
                        View.OnLongClickListener segurar) {
        LinearLayout c = new LinearLayout(tela);
        c.setOrientation(LinearLayout.HORIZONTAL);
        c.setGravity(Gravity.CENTER_VERTICAL);
        c.setBackgroundResource(emUso ? R.drawable.cartao_atual : R.drawable.cartao);
        c.setPadding(dp(14), dp(12), dp(14), dp(12));
        LinearLayout textos = new LinearLayout(tela);
        textos.setOrientation(LinearLayout.VERTICAL);
        textos.addView(texto(v.nomeExibido(), 16, R.color.topo_texto, true));
        if (!v.nomeExibido().equals(v.nome)) {
            TextView oficial = texto(v.nome, 12, R.color.topo_sub, false);
            oficial.setPadding(0, dp(2), 0, 0);
            textos.addView(oficial);
        }
        c.addView(textos, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        if (emUso) {
            ImageView ok = new ImageView(tela);
            ok.setImageResource(R.drawable.ic_ok);
            c.addView(ok, new LinearLayout.LayoutParams(dp(24), dp(24)));
        }
        c.setForeground(tela.getDrawable(R.drawable.item_menu));
        if (acao != null) c.setOnClickListener(acao);
        c.setOnLongClickListener(segurar);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(8);
        pai.addView(c, lp);
    }

    /** Diálogo do apelido de um modelo (id null = o em uso). Vazio tira o apelido. */
    static void pedirApelido(Activity tela, Motor motor, String id, Armazem.Versao v) {
        android.widget.EditText campo = new android.widget.EditText(tela);
        campo.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        campo.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(40)});
        campo.setText(v.apelido == null ? "" : v.apelido);
        campo.setHint(v.nome);
        campo.setSelectAllOnFocus(true);
        android.widget.FrameLayout moldura = new android.widget.FrameLayout(tela);
        int pad = (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 20, tela.getResources().getDisplayMetrics());
        moldura.setPadding(pad, pad / 2, pad, 0);
        moldura.addView(campo);
        AlertDialog d = new AlertDialog.Builder(tela).setTitle("Apelido do modelo").setView(moldura)
                .setPositiveButton("Guardar", (di, w) -> motor.apelidar(id, campo.getText().toString()))
                .setNeutralButton("Tirar", (di, w) -> motor.apelidar(id, ""))
                .setNegativeButton("Cancelar", null).create();
        if (d.getWindow() != null) d.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE);
        d.show();
        campo.requestFocus();
    }

    private void botao(LinearLayout linha, String rotulo, boolean primario, View.OnClickListener acao) {
        TextView b = texto(rotulo, 14, primario ? R.color.texto_usuario : R.color.chip_texto, true);
        b.setBackgroundResource(primario ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(14), dp(10), dp(14), dp(10));
        b.setOnClickListener(acao);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1);
        if (linha.getChildCount() > 0) lp.leftMargin = dp(8);
        linha.addView(b, lp);
    }

    /**
     * Troca de modelo. A conversa e a memória são do chat aberto (não do modelo), então não há nada para salvar:
     * troca direto.
     */
    static void confirmarUso(Activity tela, Motor motor, Armazem.Versao b) {
        if (motor.ocupado()) {
            new AlertDialog.Builder(tela).setMessage("Espere terminar: " + motor.tarefa).setPositiveButton("OK", null).show();
            return;
        }
        motor.usarBackup(b.id);
    }

    /** Um modelo novo chegou aos backups (NOME ou PROJETO do Colab): oferece usar agora. */
    static void mostrarBackupNovo(Activity tela, Motor motor, String titulo, String texto, String id) {
        new AlertDialog.Builder(tela).setTitle(titulo).setMessage(texto)
                .setPositiveButton("Usar agora", (d, w) -> {
                    try {
                        confirmarUso(tela, motor, motor.armazem.backup(id));
                    } catch (IOException e) {
                        new AlertDialog.Builder(tela).setMessage("Erro ao abrir o backup: " + e.getMessage())
                                .setPositiveButton("OK", null).show();
                    }
                })
                .setNegativeButton("Depois", null).show();
    }
}
