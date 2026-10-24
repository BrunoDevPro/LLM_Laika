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
 * Painel flutuante (sobe do rodapé, sem trocar de tela) com todos os modelos do celular: a versão em uso e
 * os backups. Um toque troca de modelo; "Versões e backups" abre a tela completa (importar, exportar...).
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

    private static String modelo(Armazem.Versao v) {
        Armazem.Arquivo a = v.arquivos.get(Armazem.CHAT);
        return a == null || a.descricao == null ? "" : a.descricao;
    }

    void mostrar() {
        Armazem armazem = motor.armazem;
        if (armazem == null) return;
        Armazem.Versao atual, igual;
        List<Armazem.Versao> backups;
        try {
            atual = armazem.atual();
            backups = armazem.backups();
            igual = armazem.backupIgualAoAtual();
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

        raiz.addView(texto("Modelos", 20, R.color.topo_texto, true));
        TextView sub = texto(backups.isEmpty()
                ? "Só há a versão em uso. Faça um backup ou importe um modelo novo em Versões e backups."
                : "Toque num modelo para usá-lo. A conversa e a memória vão junto com cada versão.",
                13, R.color.aviso, false);
        sub.setPadding(0, dp(2), 0, dp(10));
        raiz.addView(sub);

        LinearLayout lista = new LinearLayout(tela);
        lista.setOrientation(LinearLayout.VERTICAL);
        cartao(lista, atual.nome, "Em uso" + (modelo(atual).isEmpty() ? "" : " · " + modelo(atual)), true, null);
        for (Armazem.Versao b : backups) {
            boolean ehIgual = igual != null && igual.id.equals(b.id);
            String desc = data(b.criado) + (ehIgual ? " · igual à em uso" : "")
                    + (modelo(b).isEmpty() ? "" : "\n" + modelo(b));
            cartao(lista, b.nome, desc, false, ehIgual ? null : v -> {
                d.dismiss();
                confirmarUso(tela, motor, b, igual != null);
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

    private void cartao(LinearLayout pai, String nome, String descricao, boolean emUso, View.OnClickListener acao) {
        LinearLayout c = new LinearLayout(tela);
        c.setOrientation(LinearLayout.HORIZONTAL);
        c.setGravity(Gravity.CENTER_VERTICAL);
        c.setBackgroundResource(emUso ? R.drawable.cartao_atual : R.drawable.cartao);
        c.setPadding(dp(14), dp(12), dp(14), dp(12));
        LinearLayout textos = new LinearLayout(tela);
        textos.setOrientation(LinearLayout.VERTICAL);
        textos.addView(texto(nome, 16, R.color.topo_texto, true));
        TextView d = texto(descricao, 12, R.color.topo_sub, false);
        d.setPadding(0, dp(2), 0, 0);
        textos.addView(d);
        c.addView(textos, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        if (emUso) {
            ImageView ok = new ImageView(tela);
            ok.setImageResource(R.drawable.ic_ok);
            c.addView(ok, new LinearLayout.LayoutParams(dp(24), dp(24)));
        }
        if (acao != null) {
            c.setForeground(tela.getDrawable(R.drawable.item_menu));
            c.setOnClickListener(acao);
        } else if (!emUso) {
            c.setAlpha(0.6f);
        }
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(8);
        pai.addView(c, lp);
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

    /** Troca para um backup, oferecendo guardar a versão em uso se ela tiver mudanças fora dos backups. */
    static void confirmarUso(Activity tela, Motor motor, Armazem.Versao b, boolean atualJaSalva) {
        if (motor.ocupado()) {
            new AlertDialog.Builder(tela).setMessage("Espere terminar: " + motor.tarefa).setPositiveButton("OK", null).show();
            return;
        }
        if (atualJaSalva) {
            new AlertDialog.Builder(tela).setTitle("Usar \"" + b.nome + "\"?")
                    .setMessage("A conversa, a memória e o modelo passam a ser os deste backup.")
                    .setPositiveButton("Usar", (d, w) -> motor.usarBackup(b.id, null))
                    .setNegativeButton("Cancelar", null).show();
            return;
        }
        new AlertDialog.Builder(tela).setTitle("Usar \"" + b.nome + "\"?")
                .setMessage("A versão em uso (\"" + motor.nomeVersao + "\") tem mudanças que não estão em nenhum "
                        + "backup (conversa, memória ou arquivos). Guardar antes de trocar?")
                .setPositiveButton("Guardar e usar", (d, w) ->
                        motor.usarBackup(b.id, motor.nomeVersao + " (" + data(System.currentTimeMillis()) + ")"))
                .setNeutralButton("Usar sem guardar", (d, w) -> motor.usarBackup(b.id, null))
                .setNegativeButton("Cancelar", null).show();
    }
}
