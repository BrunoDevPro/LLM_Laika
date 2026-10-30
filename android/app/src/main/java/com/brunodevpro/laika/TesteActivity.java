package com.brunodevpro.laika;

import android.app.AlertDialog;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
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

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Testar respostas: o usuário escreve uma pergunta, escolhe quantas respostas a Laika vai dar (e a temperatura, o
 * tamanho, RAG, memória, resposta longa) e avalia cada uma (acertou, em parte ou errou, e uma nota de 0 a 5). O
 * relatório soma tudo e pode ser exportado (Markdown ou CSV). As respostas ficam fora dos chats; o teste fica salvo
 * em teste.json até "Excluir" no relatório.
 */
public class TesteActivity extends ComponentActivity implements Motor.Ouvinte {
    private static final String[] VEREDITOS = {"acertou", "parcial", "errou"};
    private static final String[] ROTULOS = {"Acertou", "Em parte", "Errou"};

    private Motor motor;
    private LinearLayout conteudo;
    private PainelTarefa painel;
    private File arquivo;
    private JSONObject teste;

    // Campos da pergunta nova (sobrevivem ao montar())
    private EditText campoPergunta;
    private String rascunho = "";
    private int quantas = 3, tamanho = 80;
    private double temperatura = 0.7;
    private boolean comRag = true, comMemoria = false, longas = false, rapidas;
    /** O relatório começa reduzido (só a linha do resumo); o estado fica guardado. */
    private boolean relatorioAberto;
    /** O modelo que a tela mostra: muda pelo seletor, e a tela se refaz quando a troca termina. */
    private String modeloMostrado;
    private boolean prontoMostrado;

    // Geração em andamento: o caso, quantas faltam e a bolha que mostra o texto parcial.
    private JSONObject casoGerando;
    private int faltam;
    private boolean parar;
    private TextView aoVivo;

    private boolean exportarCsv;
    private final ActivityResultLauncher<String> criarArquivo = registerForActivityResult(
            new ActivityResultContracts.CreateDocument("*/*"), this::exportar);

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_versoes);
        motor = Motor.get(this);
        ((TextView) findViewById(R.id.titulo)).setText("Testar respostas");
        findViewById(R.id.voltar).setOnClickListener(v -> finish());
        painel = new PainelTarefa(this, motor);
        conteudo = findViewById(R.id.conteudo);
        arquivo = new File(getFilesDir(), "teste.json");
        teste = ler();
        temperatura = motor.temperatura;
        tamanho = Math.min(motor.tamanhoResposta, motor.tamanhoMaximo());
        comRag = motor.usarRag;
        rapidas = motor.respostasRapidas;
        relatorioAberto = getSharedPreferences("tela", MODE_PRIVATE).getBoolean("teste_relatorio_aberto", false);
        if (salvo != null) {
            rascunho = salvo.getString("rascunho", "");
            exportarCsv = salvo.getBoolean("csv");
        }

        View topo = findViewById(R.id.topo), rolagem = findViewById(R.id.rolagem);
        int topoPad = topo.getPaddingTop();
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.raiz), (v, insets) -> {
            Insets sys = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            Insets ime = insets.getInsets(WindowInsetsCompat.Type.ime());
            v.setPadding(sys.left, 0, sys.right, 0);
            topo.setPadding(topo.getPaddingLeft(), topoPad + sys.top, topo.getPaddingRight(), topo.getPaddingBottom());
            rolagem.setPadding(0, 0, 0, Math.max(sys.bottom, ime.bottom));
            return WindowInsetsCompat.CONSUMED;
        });
        montar();
    }

    @Override
    protected void onSaveInstanceState(Bundle s) {
        super.onSaveInstanceState(s);
        s.putString("rascunho", campoPergunta != null ? campoPergunta.getText().toString() : rascunho);
        s.putBoolean("csv", exportarCsv);
    }

    @Override
    protected void onStart() {
        super.onStart();
        motor.adicionarOuvinte(this);
        painel.atualizar();
    }

    @Override
    protected void onStop() {
        motor.removerOuvinte(this);
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        // Saiu da tela no meio: para a geração (as respostas prontas já foram salvas).
        if (casoGerando != null) {
            parar = true;
            motor.pararGeracao();
        }
        super.onDestroy();
    }

    @Override
    public void estadoMudou() {
        painel.atualizar();
        boolean pronto = motor.pronto && !motor.ocupado();
        if (pronto != prontoMostrado || !java.util.Objects.equals(motor.nomeExibido, modeloMostrado)) montar();
    }

    @Override
    public void backupNovo(String titulo, String texto, String id) {
        SeletorModelos.mostrarBackupNovo(this, motor, titulo, texto, id);
    }

    @Override
    public void aviso(String titulo, String texto) {
        if (titulo == null) Toast.makeText(this, texto, Toast.LENGTH_LONG).show();
        else new AlertDialog.Builder(this).setTitle(titulo).setMessage(texto).setPositiveButton("OK", null).show();
    }

    // ---------- arquivo ----------

    private JSONObject ler() {
        try {
            if (arquivo.exists()) {
                return new JSONObject(new String(Files.readAllBytes(arquivo.toPath()), StandardCharsets.UTF_8));
            }
        } catch (IOException | JSONException ignorado) {
            // arquivo estragado: começa um teste novo
        }
        return novoTeste();
    }

    private static JSONObject novoTeste() {
        JSONObject t = new JSONObject();
        try {
            t.put("nome", "Teste de " + new SimpleDateFormat("dd/MM/yyyy HH:mm", new Locale("pt", "BR")).format(new Date()));
            t.put("casos", new JSONArray());
        } catch (JSONException e) {
            throw new IllegalStateException(e);
        }
        return t;
    }

    private void salvar() {
        File tmp = new File(arquivo.getPath() + ".tmp");
        try (FileOutputStream out = new FileOutputStream(tmp)) {
            out.write(teste.toString().getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            Toast.makeText(this, "Não foi possível salvar o teste: " + e.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        if (!tmp.renameTo(arquivo)) tmp.delete();
    }

    private JSONArray casos() {
        return teste.optJSONArray("casos");
    }

    // ---------- tela ----------

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private TextView texto(String s, float tam, int cor, boolean negrito) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(tam);
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

    private LinearLayout cartao() {
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setBackgroundResource(R.drawable.cartao);
        c.setPadding(dp(16), dp(14), dp(16), dp(12));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        conteudo.addView(c, lp);
        return c;
    }

    private LinearLayout linha(LinearLayout pai) {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        pai.addView(l);
        return l;
    }

    private TextView botao(LinearLayout l, String rotulo, boolean primario, View.OnClickListener acao) {
        TextView b = texto(rotulo, 14, primario ? R.color.texto_usuario : R.color.chip_texto, true);
        b.setBackgroundResource(primario ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(14), dp(8), dp(14), dp(8));
        b.setOnClickListener(acao);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(8);
        // Margens iguais em cima e embaixo: na linha centralizada, só a de cima empurrava o botão para fora (cortado).
        lp.topMargin = lp.bottomMargin = dp(4);
        l.addView(b, lp);
        return b;
    }

    /** Um botãozinho de escolha (veredito ou nota): azul quando escolhido. */
    private TextView escolha(LinearLayout l, String rotulo, boolean marcado, View.OnClickListener acao) {
        TextView b = texto(rotulo, 13, marcado ? R.color.texto_usuario : R.color.chip_texto, marcado);
        b.setBackgroundResource(marcado ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(10), dp(5), dp(10), dp(5));
        b.setMinWidth(dp(34));
        b.setOnClickListener(acao);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(6);
        lp.topMargin = lp.bottomMargin = dp(3);
        l.addView(b, lp);
        return b;
    }

    /** Um valor com − e + (quantas respostas, temperatura, tamanho). */
    private void ajuste(LinearLayout pai, String rotulo, String valor, Runnable menos, Runnable mais) {
        LinearLayout l = linha(pai);
        l.setPadding(0, dp(2), 0, 0);
        TextView r = texto(rotulo, 14, R.color.texto_laika, false);
        l.addView(r, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        escolha(l, "−", false, v -> {
            menos.run();
            lembrarRascunho();
            montar();
        });
        TextView t = texto(valor, 14, R.color.topo_texto, true);
        t.setGravity(Gravity.CENTER);
        t.setMinWidth(dp(56));
        l.addView(t);
        escolha(l, "+", false, v -> {
            mais.run();
            lembrarRascunho();
            montar();
        });
    }

    private CheckBox caixa(LinearLayout pai, String rotulo, boolean marcado, java.util.function.Consumer<Boolean> mudou) {
        CheckBox c = new CheckBox(this);
        c.setText(rotulo);
        c.setTextSize(14);
        c.setTextColor(getColor(R.color.texto_laika));
        c.setButtonTintList(android.content.res.ColorStateList.valueOf(getColor(R.color.azul)));
        c.setChecked(marcado);
        c.setOnCheckedChangeListener((b, v) -> mudou.accept(v));
        pai.addView(c);
        return c;
    }

    private void lembrarRascunho() {
        if (campoPergunta != null) rascunho = campoPergunta.getText().toString();
    }

    private void montar() {
        lembrarRascunho();
        conteudo.removeAllViews();
        aoVivo = null;
        JSONArray casos = casos();
        modeloMostrado = motor.nomeExibido;
        prontoMostrado = motor.pronto && !motor.ocupado();

        // Modelo: o em uso; "Trocar" abre o mesmo seletor do chat (a versão em uso muda no app todo).
        secao("MODELO");
        LinearLayout cm = cartao();
        LinearLayout lm = linha(cm);
        LinearLayout nomes = new LinearLayout(this);
        nomes.setOrientation(LinearLayout.VERTICAL);
        nomes.addView(texto(modeloMostrado == null ? "—" : modeloMostrado, 16, R.color.topo_texto, true));
        String sit = motor.erro != null ? motor.erro : !prontoMostrado ? "carregando…" : motor.descricaoModelo;
        if (sit != null && !sit.isEmpty()) nomes.addView(texto(sit, 12, R.color.topo_sub, false));
        lm.addView(nomes, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        botao(lm, "Trocar", false, v -> {
            if (casoGerando != null) {
                Toast.makeText(this, "Pare a geração antes de trocar de modelo.", Toast.LENGTH_SHORT).show();
                return;
            }
            new SeletorModelos(this, motor).mostrar();
        });

        // Pergunta nova
        secao("PERGUNTA");
        LinearLayout c = cartao();
        campoPergunta = new EditText(this);
        campoPergunta.setHint("Escreva a pergunta para testar");
        campoPergunta.setText(rascunho);
        campoPergunta.setTextSize(15);
        campoPergunta.setTextColor(getColor(R.color.texto_laika));
        campoPergunta.setHintTextColor(getColor(R.color.detalhe));
        campoPergunta.setBackgroundResource(R.drawable.campo);
        campoPergunta.setPadding(dp(14), dp(10), dp(14), dp(10));
        campoPergunta.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE
                | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        campoPergunta.setMaxLines(6);
        c.addView(campoPergunta);
        ajuste(c, "Respostas", String.valueOf(quantas),
                () -> quantas = Math.max(1, quantas - 1), () -> quantas = Math.min(20, quantas + 1));
        ajuste(c, "Temperatura", String.format(Locale.getDefault(), "%.2f", temperatura),
                () -> temperatura = Math.max(Motor.TEMP_MIN, Math.round((temperatura - 0.1) * 100) / 100.0),
                () -> temperatura = Math.min(Motor.TEMP_MAX, Math.round((temperatura + 0.1) * 100) / 100.0));
        int max = motor.tamanhoMaximo();
        ajuste(c, "Tamanho", "até " + tamanho,
                () -> tamanho = Math.max(Motor.TAMANHO_MIN, tamanho - 16), () -> tamanho = Math.min(max, tamanho + 16));
        caixa(c, "Busca (RAG)", comRag, v -> comRag = v);
        caixa(c, "Memória do usuário no Contexto", comMemoria, v -> comMemoria = v);
        caixa(c, "Resposta longa", longas, v -> longas = v);
        caixa(c, "Respostas rápidas (até 2 trechos do RAG)", rapidas, v -> rapidas = v);
        TextView dica = texto("Com temperatura acima de zero, cada resposta sai diferente: gere várias para ver "
                + "quantas acertam. Nada disso entra nos chats.", 12, R.color.aviso, false);
        dica.setPadding(0, dp(4), 0, 0);
        c.addView(dica);
        LinearLayout lb = linha(c);
        if (casoGerando != null) {
            botao(lb, "Parar", true, v -> {
                parar = true;
                motor.pararGeracao();
            });
        } else {
            botao(lb, quantas == 1 ? "Gerar 1 resposta" : "Gerar " + quantas + " respostas", true, v -> comecar());
        }

        // Casos, do mais novo para o mais antigo
        if (casos.length() > 0) secao("PERGUNTAS TESTADAS (" + casos.length() + ")");
        for (int i = casos.length() - 1; i >= 0; i--) mostrarCaso(casos.optJSONObject(i), i);

        // Relatório: reduzido (nome e uma linha); tocar no topo estende ou reduz.
        secao("RELATÓRIO");
        LinearLayout r = cartao();
        LinearLayout topo = linha(r);
        topo.setOnClickListener(v -> {
            relatorioAberto = !relatorioAberto;
            getSharedPreferences("tela", MODE_PRIVATE).edit().putBoolean("teste_relatorio_aberto", relatorioAberto).apply();
            montar();
        });
        LinearLayout cab = new LinearLayout(this);
        cab.setOrientation(LinearLayout.VERTICAL);
        cab.addView(texto(teste.optString("nome"), 16, R.color.topo_texto, true));
        cab.addView(texto(resumoCurto(), 13, R.color.topo_sub, false));
        topo.addView(cab, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        TextView seta = texto(relatorioAberto ? "▴" : "▾", 22, R.color.topo_sub, false);
        seta.setPadding(dp(12), 0, dp(4), 0);
        topo.addView(seta);
        if (relatorioAberto) {
            TextView resumo = texto(resumo() + porPergunta(), 14, R.color.texto_laika, false);
            resumo.setPadding(0, dp(8), 0, 0);
            resumo.setLineSpacing(0, 1.15f);
            r.addView(resumo);
            LinearLayout l1 = linha(r);
            l1.setPadding(0, dp(6), 0, 0);
            botao(l1, "Exportar", true, v -> escolherFormato());
            botao(l1, "Renomear", false, v -> renomear());
            botao(l1, "Excluir", false, v -> excluir());
        }
    }

    private void mostrarCaso(JSONObject caso, int indice) {
        LinearLayout c = cartao();
        c.addView(texto(caso.optString("pergunta"), 16, R.color.topo_texto, true));
        TextView op = texto(opcoes(caso), 12, R.color.topo_sub, false);
        op.setPadding(0, dp(2), 0, dp(4));
        c.addView(op);
        JSONArray rs = caso.optJSONArray("respostas");
        for (int k = 0; rs != null && k < rs.length(); k++) mostrarResposta(c, rs.optJSONObject(k), k);
        if (caso == casoGerando) {
            aoVivo = texto("…", 15, R.color.texto_laika, false);
            aoVivo.setBackgroundResource(R.drawable.bolha_laika);
            aoVivo.setPadding(dp(12), dp(8), dp(12), dp(8));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            lp.topMargin = dp(10);
            c.addView(aoVivo, lp);
            TextView f = texto("gerando… faltam " + faltam, 12, R.color.aviso, false);
            c.addView(f);
            return;
        }
        LinearLayout l = linha(c);
        botao(l, "Mais 1", false, v -> gerarMais(caso, 1));
        botao(l, "Repetir", false, v -> {
            rascunho = caso.optString("pergunta");
            JSONObject o = caso.optJSONObject("opcoes");
            if (o != null) {
                temperatura = o.optDouble("temperatura", temperatura);
                tamanho = o.optInt("tamanho", tamanho);
                comRag = o.optBoolean("rag", comRag);
                comMemoria = o.optBoolean("memoria", comMemoria);
                longas = o.optBoolean("longa", longas);
                rapidas = o.optBoolean("rapidas", rapidas);
            }
            campoPergunta = null;
            montar();
            findViewById(R.id.rolagem).scrollTo(0, 0);
        });
        botao(l, "Apagar", false, v -> new AlertDialog.Builder(this).setTitle("Apagar esta pergunta?")
                .setMessage("As respostas e as notas dela saem do relatório.")
                .setPositiveButton("Apagar", (d, w) -> {
                    casos().remove(indice);
                    salvar();
                    montar();
                }).setNegativeButton("Cancelar", null).show());
    }

    private void mostrarResposta(LinearLayout c, JSONObject r, int k) {
        TextView t = texto((k + 1) + ". " + r.optString("texto")
                + (r.optString("fonte").isEmpty() ? "" : "  *" + r.optString("fonte")), 15, R.color.texto_laika, false);
        t.setBackgroundResource(R.drawable.bolha_laika);
        t.setPadding(dp(12), dp(8), dp(12), dp(8));
        t.setLineSpacing(0, 1.1f);
        t.setTextIsSelectable(true);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(10);
        c.addView(t, lp);
        String det = r.optString("detalhe") + (r.optString("modelo").isEmpty() ? "" : " · " + r.optString("modelo"));
        TextView d = texto(det, 11, R.color.detalhe, false);
        d.setPadding(dp(4), dp(2), 0, 0);
        c.addView(d);

        String veredito = r.optString("veredito");
        LinearLayout lv = linha(c);
        for (int i = 0; i < VEREDITOS.length; i++) {
            String v = VEREDITOS[i];
            escolha(lv, ROTULOS[i], v.equals(veredito), x -> {
                poe(r, "veredito", v.equals(r.optString("veredito")) ? null : v);
                salvar();
                montar();
            });
        }
        int nota = r.optInt("nota", -1);
        LinearLayout ln = linha(c);
        TextView rot = texto("Nota", 12, R.color.topo_sub, false);
        rot.setPadding(0, dp(6), dp(6), 0);
        ln.addView(rot);
        for (int n = 0; n <= 5; n++) {
            int esta = n;
            escolha(ln, String.valueOf(n), n == nota, x -> {
                poe(r, "nota", esta == r.optInt("nota", -1) ? null : esta);
                // Sem veredito ainda: a nota sugere um (5 = acertou, 0 = errou, o resto = em parte).
                if (r.optString("veredito").isEmpty() && r.has("nota")) {
                    poe(r, "veredito", esta == 5 ? "acertou" : esta == 0 ? "errou" : "parcial");
                }
                salvar();
                montar();
            });
        }
        String com = r.optString("comentario");
        TextView cm = texto(com.isEmpty() ? "+ comentário" : "Comentário: " + com, 12,
                com.isEmpty() ? R.color.azul : R.color.texto_laika, false);
        cm.setPadding(0, dp(8), 0, dp(2));
        cm.setOnClickListener(v -> comentar(r));
        c.addView(cm);
    }

    private static void poe(JSONObject o, String chave, Object valor) {
        try {
            if (valor == null) o.remove(chave);
            else o.put(chave, valor);
        } catch (JSONException e) {
            throw new IllegalStateException(e);
        }
    }

    private void comentar(JSONObject r) {
        EditText e = new EditText(this);
        e.setText(r.optString("comentario"));
        e.setSelection(e.length());
        e.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        e.setHint("O que estava certo ou errado");
        LinearLayout box = new LinearLayout(this);
        box.setPadding(dp(20), dp(8), dp(20), 0);
        box.addView(e, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        new AlertDialog.Builder(this).setTitle("Comentário").setView(box)
                .setPositiveButton("Salvar", (d, w) -> {
                    String s = e.getText().toString().trim();
                    poe(r, "comentario", s.isEmpty() ? null : s);
                    salvar();
                    montar();
                }).setNegativeButton("Cancelar", null).show();
    }

    private void renomear() {
        EditText e = new EditText(this);
        e.setText(teste.optString("nome"));
        e.setSelection(e.length());
        e.setSingleLine(true);
        LinearLayout box = new LinearLayout(this);
        box.setPadding(dp(20), dp(8), dp(20), 0);
        box.addView(e, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        new AlertDialog.Builder(this).setTitle("Nome do teste").setView(box)
                .setPositiveButton("Salvar", (d, w) -> {
                    String s = e.getText().toString().trim();
                    if (!s.isEmpty()) poe(teste, "nome", s);
                    salvar();
                    montar();
                }).setNegativeButton("Cancelar", null).show();
    }

    private void excluir() {
        if (casoGerando != null) {
            Toast.makeText(this, "Pare a geração antes.", Toast.LENGTH_SHORT).show();
            return;
        }
        new AlertDialog.Builder(this).setTitle("Excluir o relatório?")
                .setMessage("As perguntas, respostas e notas deste teste serão apagadas e começa um teste novo. "
                        + "Exporte antes, se quiser guardar.")
                .setPositiveButton("Excluir", (d, w) -> {
                    teste = novoTeste();
                    salvar();
                    montar();
                }).setNegativeButton("Cancelar", null).show();
    }

    // ---------- geração ----------

    private void comecar() {
        String p = campoPergunta.getText().toString().trim();
        if (p.isEmpty()) {
            Toast.makeText(this, "Escreva a pergunta.", Toast.LENGTH_SHORT).show();
            return;
        }
        JSONObject caso = new JSONObject();
        JSONObject op = new JSONObject();
        poe(op, "temperatura", temperatura);
        poe(op, "tamanho", tamanho);
        poe(op, "rag", comRag);
        poe(op, "memoria", comMemoria);
        poe(op, "longa", longas);
        poe(op, "rapidas", rapidas);
        poe(caso, "pergunta", p);
        poe(caso, "opcoes", op);
        poe(caso, "respostas", new JSONArray());
        poe(caso, "data", System.currentTimeMillis());
        casos().put(caso);
        salvar();
        rascunho = "";
        campoPergunta.setText("");
        gerarMais(caso, quantas);
    }

    private void gerarMais(JSONObject caso, int n) {
        if (casoGerando != null) return;
        if (motor.gerando) {
            Toast.makeText(this, "Espere a resposta do chat terminar.", Toast.LENGTH_SHORT).show();
            return;
        }
        casoGerando = caso;
        faltam = n;
        parar = false;
        montar();
        proxima();
    }

    private void proxima() {
        JSONObject caso = casoGerando;
        if (caso == null) return;
        if (parar || faltam <= 0) {
            casoGerando = null;
            if (!isDestroyed()) montar();
            return;
        }
        JSONObject o = caso.optJSONObject("opcoes");
        motor.testar(caso.optString("pergunta"), o.optDouble("temperatura", 0.7), o.optInt("tamanho", 80),
                o.optBoolean("rag"), o.optBoolean("memoria"), o.optBoolean("longa"), o.optBoolean("rapidas"),
                parcial -> {
                    if (aoVivo != null) aoVivo.setText(parcial.isEmpty() ? "…" : parcial);
                },
                (r, erro) -> {
                    if (erro != null) {
                        casoGerando = null;
                        if (!isDestroyed()) {
                            Toast.makeText(this, erro, Toast.LENGTH_LONG).show();
                            montar();
                        }
                        return;
                    }
                    JSONObject j = new JSONObject();
                    poe(j, "texto", r.texto);
                    poe(j, "detalhe", r.detalhe);
                    poe(j, "fonte", r.fonte);
                    poe(j, "modelo", r.modelo);
                    caso.optJSONArray("respostas").put(j);
                    salvar();
                    faltam--;
                    if (isDestroyed()) {
                        casoGerando = null;
                        return;
                    }
                    montar();
                    proxima();
                });
    }

    // ---------- relatório ----------

    private static String opcoes(JSONObject caso) {
        JSONObject o = caso.optJSONObject("opcoes");
        if (o == null) return "";
        List<String> l = new ArrayList<>();
        l.add(String.format(Locale.getDefault(), "temperatura %.2f", o.optDouble("temperatura")));
        l.add("até " + o.optInt("tamanho") + " tokens");
        l.add(o.optBoolean("rag") ? "com RAG" : "sem RAG");
        if (o.optBoolean("memoria")) l.add("com memória");
        if (o.optBoolean("longa")) l.add("resposta longa");
        if (o.optBoolean("rapidas")) l.add("rápidas");
        return String.join(" · ", l);
    }

    /** Contagens de um caso ou do teste: [respostas, acertos, parciais, erros, com nota, soma das notas]. */
    private static int[] contar(JSONArray rs, int[] t) {
        for (int k = 0; rs != null && k < rs.length(); k++) {
            JSONObject r = rs.optJSONObject(k);
            t[0]++;
            String v = r.optString("veredito");
            if (v.equals("acertou")) t[1]++;
            else if (v.equals("parcial")) t[2]++;
            else if (v.equals("errou")) t[3]++;
            if (r.has("nota")) {
                t[4]++;
                t[5] += r.optInt("nota");
            }
        }
        return t;
    }

    private static String pct(int a, int b) {
        return b == 0 ? "–" : Math.round(100.0 * a / b) + "%";
    }

    private static String media(int soma, int n) {
        return n == 0 ? "–" : String.format(Locale.getDefault(), "%.1f", (double) soma / n);
    }

    /** Uma linha para o relatório reduzido. */
    private String resumoCurto() {
        JSONArray casos = casos();
        int[] t = new int[6];
        for (int i = 0; i < casos.length(); i++) contar(casos.optJSONObject(i).optJSONArray("respostas"), t);
        if (t[0] == 0) return "Nenhuma resposta ainda";
        int avaliadas = t[1] + t[2] + t[3];
        return t[0] + " respostas · acertou " + pct(t[1], avaliadas) + " · nota " + media(t[5], t[4]);
    }

    /** No relatório estendido: uma linha por pergunta. */
    private String porPergunta() {
        JSONArray casos = casos();
        if (casos.length() < 2) return "";
        StringBuilder sb = new StringBuilder("\n");
        for (int i = 0; i < casos.length(); i++) {
            JSONObject caso = casos.optJSONObject(i);
            int[] t = contar(caso.optJSONArray("respostas"), new int[6]);
            String p = caso.optString("pergunta");
            if (p.length() > 40) p = p.substring(0, 39) + "…";
            sb.append("\n").append(i + 1).append(". ").append(p).append(": ").append(t[1]).append("/").append(t[0])
                    .append(" certas · nota ").append(media(t[5], t[4]));
        }
        return sb.toString();
    }

    private String resumo() {
        JSONArray casos = casos();
        int[] t = new int[6];
        for (int i = 0; i < casos.length(); i++) contar(casos.optJSONObject(i).optJSONArray("respostas"), t);
        if (t[0] == 0) return "Nenhuma resposta ainda.";
        int avaliadas = t[1] + t[2] + t[3];
        return casos.length() + (casos.length() == 1 ? " pergunta, " : " perguntas, ") + t[0] + " respostas ("
                + avaliadas + " avaliadas)\n"
                + "Acertou: " + t[1] + " (" + pct(t[1], avaliadas) + ") · Em parte: " + t[2] + " (" + pct(t[2], avaliadas)
                + ") · Errou: " + t[3] + " (" + pct(t[3], avaliadas) + ")\n"
                + "Nota média: " + media(t[5], t[4]) + " de 5" + (t[4] < t[0] ? " (" + t[4] + " com nota)" : "");
    }

    private void escolherFormato() {
        if (casos().length() == 0) {
            Toast.makeText(this, "Ainda não há respostas para exportar.", Toast.LENGTH_SHORT).show();
            return;
        }
        String base = teste.optString("nome").replaceAll("[\\\\/:*?\"<>|]", "-");
        new AlertDialog.Builder(this).setTitle("Exportar relatório")
                .setItems(new String[]{"Texto (.md): fácil de ler", "Planilha (.csv): uma linha por resposta"}, (d, w) -> {
                    exportarCsv = w == 1;
                    criarArquivo.launch(base + (exportarCsv ? ".csv" : ".md"));
                }).show();
    }

    private void exportar(Uri uri) {
        if (uri == null) return;
        try (OutputStream out = getContentResolver().openOutputStream(uri)) {
            if (out == null) throw new IOException("não foi possível abrir o arquivo");
            out.write((exportarCsv ? csv() : markdown()).getBytes(StandardCharsets.UTF_8));
            Toast.makeText(this, "Relatório exportado.", Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            new AlertDialog.Builder(this).setTitle("Erro ao exportar").setMessage(e.getMessage())
                    .setPositiveButton("OK", null).show();
        }
    }

    private String markdown() {
        StringBuilder sb = new StringBuilder();
        sb.append("# ").append(teste.optString("nome")).append("\n\n");
        sb.append("Modelo em uso: ").append(motor.nomeExibido).append("\n\n");
        sb.append("## Resumo\n\n").append(resumo().replace("\n", "  \n")).append("\n\n");
        JSONArray casos = casos();
        for (int i = 0; i < casos.length(); i++) {
            JSONObject caso = casos.optJSONObject(i);
            JSONArray rs = caso.optJSONArray("respostas");
            int[] t = contar(rs, new int[6]);
            sb.append("## ").append(i + 1).append(". ").append(caso.optString("pergunta")).append("\n\n");
            sb.append("_").append(opcoes(caso)).append("_  \n");
            sb.append("Acertou ").append(t[1]).append(" · em parte ").append(t[2]).append(" · errou ").append(t[3])
                    .append(" · nota média ").append(media(t[5], t[4])).append("\n\n");
            for (int k = 0; rs != null && k < rs.length(); k++) {
                JSONObject r = rs.optJSONObject(k);
                sb.append(k + 1).append(". ");
                String v = r.optString("veredito");
                if (!v.isEmpty()) sb.append("**").append(rotulo(v)).append("**");
                if (r.has("nota")) sb.append(v.isEmpty() ? "" : ", ").append("nota ").append(r.optInt("nota"));
                if (!v.isEmpty() || r.has("nota")) sb.append(": ");
                sb.append(r.optString("texto").replace("\n", " "));
                if (!r.optString("fonte").isEmpty()) sb.append(" *").append(r.optString("fonte"));
                sb.append("  \n   _").append(r.optString("detalhe"));
                if (!r.optString("modelo").isEmpty()) sb.append(" · ").append(r.optString("modelo"));
                sb.append("_");
                if (!r.optString("comentario").isEmpty()) sb.append("  \n   Comentário: ").append(r.optString("comentario"));
                sb.append("\n");
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    private static String rotulo(String v) {
        for (int i = 0; i < VEREDITOS.length; i++) if (VEREDITOS[i].equals(v)) return ROTULOS[i];
        return v;
    }

    private static String celula(String s) {
        return "\"" + (s == null ? "" : s.replace("\"", "\"\"")) + "\"";
    }

    private String csv() {
        StringBuilder sb = new StringBuilder("﻿pergunta;opcoes;resposta;fonte;veredito;nota;comentario;detalhe;modelo\n");
        JSONArray casos = casos();
        for (int i = 0; i < casos.length(); i++) {
            JSONObject caso = casos.optJSONObject(i);
            JSONArray rs = caso.optJSONArray("respostas");
            for (int k = 0; rs != null && k < rs.length(); k++) {
                JSONObject r = rs.optJSONObject(k);
                sb.append(celula(caso.optString("pergunta"))).append(';')
                        .append(celula(opcoes(caso))).append(';')
                        .append(celula(r.optString("texto"))).append(';')
                        .append(celula(r.optString("fonte"))).append(';')
                        .append(celula(r.optString("veredito").isEmpty() ? "" : rotulo(r.optString("veredito")))).append(';')
                        .append(r.has("nota") ? String.valueOf(r.optInt("nota")) : "").append(';')
                        .append(celula(r.optString("comentario"))).append(';')
                        .append(celula(r.optString("detalhe"))).append(';')
                        .append(celula(r.optString("modelo"))).append('\n');
            }
        }
        return sb.toString();
    }
}
