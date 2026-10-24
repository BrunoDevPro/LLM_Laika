package com.brunodevpro.laika;

import android.app.AlertDialog;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputFilter;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.brunodevpro.laika.core.Armazem;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Versões e backups: a versão em uso, importar uma atualização (o zip do Colab ou os arquivos de um
 * treino novo), fazer/usar/renomear/exportar/apagar backups.
 */
public class VersoesActivity extends ComponentActivity implements Motor.Ouvinte {
    private static final long INDICE_GRANDE = 50L << 20;

    private Motor motor;
    private LinearLayout conteudo;
    private PainelTarefa painel;
    private boolean estavaOcupado;

    // Exportação pendente (enquanto o usuário escolhe onde salvar)
    private String exportarId;
    private boolean exportarIndice;

    private final ActivityResultLauncher<String[]> escolherArquivos = registerForActivityResult(
            new ActivityResultContracts.OpenMultipleDocuments(), uris -> {
                if (uris != null && !uris.isEmpty()) motor.importar(uris);
            });

    private final ActivityResultLauncher<String> criarZip = registerForActivityResult(
            new ActivityResultContracts.CreateDocument("application/zip"), uri -> {
                if (uri != null) motor.exportar(exportarId, uri, exportarIndice);
            });

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_versoes);
        motor = Motor.get(this);
        conteudo = findViewById(R.id.conteudo);
        painel = new PainelTarefa(this, motor);
        findViewById(R.id.voltar).setOnClickListener(v -> finish());
        if (salvo != null) {
            exportarId = salvo.getString("exportarId");
            exportarIndice = salvo.getBoolean("exportarIndice");
        }

        View topo = findViewById(R.id.topo), rolagem = findViewById(R.id.rolagem);
        int topoPad = topo.getPaddingTop();
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.raiz), (v, insets) -> {
            Insets sys = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            v.setPadding(sys.left, 0, sys.right, 0);
            topo.setPadding(topo.getPaddingLeft(), topoPad + sys.top, topo.getPaddingRight(), topo.getPaddingBottom());
            rolagem.setPadding(0, 0, 0, sys.bottom);
            return WindowInsetsCompat.CONSUMED;
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle s) {
        super.onSaveInstanceState(s);
        s.putString("exportarId", exportarId);
        s.putBoolean("exportarIndice", exportarIndice);
    }

    @Override
    protected void onStart() {
        super.onStart();
        motor.adicionarOuvinte(this);
        estadoMudou();
        montar();
    }

    @Override
    protected void onStop() {
        motor.removerOuvinte(this);
        super.onStop();
    }

    @Override
    public void estadoMudou() {
        painel.atualizar();
        boolean ocupado = motor.ocupado();
        if (estavaOcupado != ocupado) montar();
        estavaOcupado = ocupado;
    }

    @Override
    public void aviso(String titulo, String texto) {
        if (titulo == null) {
            Toast.makeText(this, texto, Toast.LENGTH_LONG).show();
        } else {
            new AlertDialog.Builder(this).setTitle(titulo).setMessage(texto).setPositiveButton("OK", null).show();
        }
        montar();
    }

    // ---------- montagem da tela ----------

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private static String data(long t) {
        return new SimpleDateFormat("dd/MM/yyyy HH:mm", new Locale("pt", "BR")).format(new Date(t));
    }

    private TextView texto(String s, float tamanho, int cor, boolean negrito) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(tamanho);
        t.setTextColor(getColor(cor));
        if (negrito) t.setTypeface(t.getTypeface(), android.graphics.Typeface.BOLD);
        return t;
    }

    private void secao(String titulo) {
        TextView t = texto(titulo, 12, R.color.topo_sub, true);
        t.setLetterSpacing(0.08f);
        t.setPadding(dp(4), dp(18), dp(4), dp(8));
        conteudo.addView(t);
    }

    private LinearLayout cartao(boolean destaque) {
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setBackgroundResource(destaque ? R.drawable.cartao_atual : R.drawable.cartao);
        c.setPadding(dp(16), dp(14), dp(16), dp(12));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        conteudo.addView(c, lp);
        return c;
    }

    private TextView botao(LinearLayout linha, String rotulo, boolean primario, View.OnClickListener acao) {
        TextView b = texto(rotulo, 14, primario ? R.color.texto_usuario : R.color.chip_texto, true);
        b.setBackgroundResource(primario ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(14), dp(8), dp(14), dp(8));
        b.setOnClickListener(acao);
        b.setEnabled(!motor.ocupado());
        b.setAlpha(motor.ocupado() ? 0.5f : 1f);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(8);
        lp.topMargin = dp(8);
        linha.addView(b, lp);
        return b;
    }

    private LinearLayout linhaDeBotoes(LinearLayout cartao) {
        // Quebra em mais de uma linha se não couber (telas estreitas).
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.HORIZONTAL);
        cartao.addView(l);
        return l;
    }

    private void detalhe(LinearLayout c, String rotulo, String valor) {
        TextView t = texto(rotulo + ": " + valor, 13, R.color.texto_laika, false);
        t.setPadding(0, dp(2), 0, 0);
        c.addView(t);
    }

    private String descricao(Armazem.Versao v, String papel) {
        Armazem.Arquivo a = v.arquivos.get(papel);
        if (a == null) return "não tem";
        String d = a.descricao == null ? "" : a.descricao;
        if (Armazem.INDICE.equals(papel) && a.tamanho > 0) d += String.format(Locale.getDefault(), " · %d MB", a.tamanho >> 20);
        return a.daFabrica() ? d + " · do app" : d + (a.origem != null ? " · " + a.origem : "");
    }

    private void montar() {
        conteudo.removeAllViews();
        Armazem armazem = motor.armazem;
        if (armazem == null) {
            conteudo.addView(texto("Carregando…", 15, R.color.aviso, false));
            return;
        }
        Armazem.Versao atual;
        List<Armazem.Versao> backups;
        Armazem.Versao igual;
        try {
            atual = armazem.atual();
            backups = armazem.backups();
            igual = armazem.backupIgualAoAtual();
        } catch (IOException e) {
            conteudo.addView(texto("Erro ao ler as versões: " + e.getMessage(), 15, R.color.perigo, false));
            return;
        }

        // Versão em uso
        secao("EM USO");
        LinearLayout c = cartao(true);
        c.addView(texto(atual.nome, 18, R.color.topo_texto, true));
        c.addView(texto("desde " + data(atual.alterado) + (igual != null ? " · salva no backup \"" + igual.nome + "\""
                : " · com mudanças que não estão em nenhum backup"), 12, R.color.topo_sub, false));
        detalhe(c, "Chat", descricao(atual, Armazem.CHAT));
        detalhe(c, "Completar texto", descricao(atual, Armazem.BASE));
        detalhe(c, "Tokenizer", descricao(atual, Armazem.TOKENIZER));
        detalhe(c, "Busca (RAG)", descricao(atual, Armazem.INDICE));
        detalhe(c, "Memória", atual.resumoMemoria());
        detalhe(c, "Conversa", plural(atual.mensagens(), "mensagem", "mensagens"));
        LinearLayout l = linhaDeBotoes(c);
        botao(l, "Fazer backup", true, v -> pedirNomeDoBackup());
        botao(l, "Renomear", false, v -> renomear(null, atual.nome));
        botao(l, "Exportar", false, v -> exportar(atual));

        // Atualização
        secao("ATUALIZAR");
        LinearLayout u = cartao(false);
        u.addView(texto("Usar um modelo novo", 16, R.color.topo_texto, true));
        TextView ajuda = texto("laika_pacote.zip do Colab, os .pt e o tokenizer.json, ou um backup .zip do app. "
                + "A versão em uso vai para os backups antes da troca.", 13, R.color.texto_laika, false);
        ajuda.setPadding(0, dp(4), 0, 0);
        u.addView(ajuda);
        LinearLayout lu = linhaDeBotoes(u);
        botao(lu, "Escolher arquivos", true, v -> escolherArquivos.launch(new String[]{"*/*"}));
        botao(lu, "Treinar", false, v -> startActivity(new android.content.Intent(this, ColabActivity.class)));

        // Backups
        secao("BACKUPS (" + backups.size() + ")");
        if (backups.isEmpty()) {
            TextView t = texto("Nenhum backup ainda. Toque em \"Fazer backup\" para guardar a versão em uso.",
                    14, R.color.aviso, false);
            t.setPadding(dp(4), 0, dp(4), 0);
            conteudo.addView(t);
        }
        for (Armazem.Versao b : backups) {
            boolean ehIgual = igual != null && igual.id.equals(b.id);
            LinearLayout cb = cartao(false);
            cb.addView(texto(b.nome, 16, R.color.topo_texto, true));
            cb.addView(texto(data(b.criado) + (ehIgual ? " · igual à versão em uso" : ""), 12, R.color.topo_sub, false));
            detalhe(cb, "Chat", descricao(b, Armazem.CHAT));
            detalhe(cb, "Busca (RAG)", descricao(b, Armazem.INDICE));
            detalhe(cb, "Memória", b.resumoMemoria() + " · conversa: " + plural(b.mensagens(), "mensagem", "mensagens"));
            LinearLayout lb = linhaDeBotoes(cb);
            botao(lb, "Usar", true, v -> usar(b, igual != null));
            botao(lb, "Renomear", false, v -> renomear(b.id, b.nome));
            LinearLayout lb2 = linhaDeBotoes(cb);
            botao(lb2, "Exportar", false, v -> exportar(b));
            TextView apagar = botao(lb2, "Apagar", false, v -> apagar(b));
            apagar.setTextColor(getColor(R.color.perigo));
        }

        TextView rodape = texto(String.format(Locale.getDefault(),
                "Espaço usado pela Laika no celular: %d MB (os backups compartilham os arquivos iguais).",
                armazem.espacoUsado() >> 20), 12, R.color.aviso, false);
        rodape.setPadding(dp(4), dp(14), dp(4), dp(8));
        conteudo.addView(rodape);
    }

    private static String plural(int n, String um, String varios) {
        return n + " " + (n == 1 ? um : varios);
    }

    // ---------- ações ----------

    /** Diálogo com um campo de texto (nome do backup). */
    private void pedirTexto(String titulo, String valor, String botaoOk, java.util.function.Consumer<String> ok) {
        EditText campo = new EditText(this);
        campo.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        campo.setFilters(new InputFilter[]{new InputFilter.LengthFilter(60)});
        campo.setText(valor);
        campo.setSelectAllOnFocus(true);
        FrameLayout moldura = new FrameLayout(this);
        moldura.setPadding(dp(20), dp(8), dp(20), 0);
        moldura.addView(campo);
        AlertDialog d = new AlertDialog.Builder(this).setTitle(titulo).setView(moldura)
                .setPositiveButton(botaoOk, (di, w) -> {
                    String nome = campo.getText().toString().trim();
                    if (nome.isEmpty()) Toast.makeText(this, "O nome não pode ficar vazio.", Toast.LENGTH_SHORT).show();
                    else ok.accept(nome);
                })
                .setNegativeButton("Cancelar", null).create();
        d.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE);
        d.show();
        campo.requestFocus();
    }

    private void pedirNomeDoBackup() {
        pedirTexto("Fazer backup", "Backup de " + data(System.currentTimeMillis()), "Guardar",
                nome -> motor.fazerBackup(nome));
    }

    private void renomear(String id, String nomeAtual) {
        pedirTexto(id == null ? "Renomear a versão em uso" : "Renomear o backup", nomeAtual, "Renomear",
                nome -> motor.renomear(id, nome));
    }

    private void usar(Armazem.Versao b, boolean atualJaSalva) {
        SeletorModelos.confirmarUso(this, motor, b, atualJaSalva);
    }

    private void apagar(Armazem.Versao b) {
        new AlertDialog.Builder(this).setTitle("Apagar \"" + b.nome + "\"?")
                .setMessage("O backup some deste celular. Os arquivos que outras versões usam continuam.")
                .setPositiveButton("Apagar", (d, w) -> motor.apagarBackup(b.id))
                .setNegativeButton("Cancelar", null).show();
    }

    private void exportar(Armazem.Versao v) {
        exportarId = v.id;
        Armazem.Arquivo indice = v.arquivos.get(Armazem.INDICE);
        long tam = indice == null ? -1 : motor.armazem.tamanho(indice);
        String nomeArquivo = "Laika - " + v.nome.replaceAll("[\\\\/:*?\"<>|]", "-") + ".zip";
        if (tam > INDICE_GRANDE) {
            new AlertDialog.Builder(this).setTitle("Incluir o índice completo?")
                    .setMessage(String.format(Locale.getDefault(), "O índice do RAG tem %d MB. Sem ele o arquivo fica "
                            + "bem menor (~30 MB) e, ao importar, a versão usa o índice pequeno do app.", tam >> 20))
                    .setPositiveButton("Com o índice", (d, w) -> {
                        exportarIndice = true;
                        criarZip.launch(nomeArquivo);
                    })
                    .setNegativeButton("Sem o índice", (d, w) -> {
                        exportarIndice = false;
                        criarZip.launch(nomeArquivo);
                    }).show();
        } else {
            exportarIndice = true;
            criarZip.launch(nomeArquivo);
        }
    }
}
