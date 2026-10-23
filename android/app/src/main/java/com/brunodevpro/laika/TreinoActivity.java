package com.brunodevpro.laika;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.brunodevpro.laika.core.Armazem;
import com.brunodevpro.laika.core.ConversorPt;
import com.brunodevpro.laika.core.treino.Corpus;
import com.brunodevpro.laika.core.treino.PreTreino;
import com.brunodevpro.laika.core.treino.Presets;
import com.brunodevpro.laika.core.treino.Rede;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Treinar no celular: as células do Colab (dados, índice, pré-treino, fine-tuning, usar). */
public class TreinoActivity extends ComponentActivity implements TreinoEstado.Ouvinte, Motor.Ouvinte {
    private Motor motor;
    private TreinoEstado estado;
    private SharedPreferences prefs;
    private LinearLayout conteudo;
    private View tarefa;
    private TextView tarefaTitulo, tarefaTexto, log;
    private ProgressBar tarefaBarra;
    private boolean estavaRodando, motorOcupado;

    // Opções escolhidas na tela
    private RadioGroup modo;
    private Spinner preset;
    private EditText passos, microLote, epocas, textoMb;
    private CheckBox comRag, doResultado;

    private final ActivityResultLauncher<String[]> escolherZip = registerForActivityResult(
            new ActivityResultContracts.OpenDocument(), uri -> {
                if (uri == null) return;
                Intent i = new Intent().putExtra("etapas", new String[]{TreinoService.DADOS}).putExtra("uri", uri.toString());
                TreinoService.iniciar(this, i);
            });

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_treino);
        motor = Motor.get(this);
        estado = TreinoEstado.get();
        prefs = getSharedPreferences("treino", MODE_PRIVATE);
        conteudo = findViewById(R.id.conteudo);
        tarefa = findViewById(R.id.tarefa);
        tarefaTitulo = findViewById(R.id.tarefa_titulo);
        tarefaTexto = findViewById(R.id.tarefa_texto);
        tarefaBarra = findViewById(R.id.tarefa_barra);
        findViewById(R.id.voltar).setOnClickListener(v -> finish());
        findViewById(R.id.parar).setOnClickListener(v -> {
            TreinoService.parar(this);
            tarefaTexto.setText("Parando… (salvando o estado)");
        });
        View topo = findViewById(R.id.topo), rolagem = findViewById(R.id.rolagem);
        int topoPad = topo.getPaddingTop();
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.raiz), (v, insets) -> {
            Insets sys = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            v.setPadding(sys.left, 0, sys.right, 0);
            topo.setPadding(topo.getPaddingLeft(), topoPad + sys.top, topo.getPaddingRight(), topo.getPaddingBottom());
            rolagem.setPadding(0, 0, 0, sys.bottom);
            return WindowInsetsCompat.CONSUMED;
        });
        montar();
    }

    @Override
    protected void onStart() {
        super.onStart();
        estado.adicionar(this);
        motor.adicionarOuvinte(this);
        estavaRodando = estado.rodando;
        mudou();
    }

    @Override
    protected void onStop() {
        salvarOpcoes();
        estado.remover(this);
        motor.removerOuvinte(this);
        super.onStop();
    }

    // ---------- estado do treino ----------

    @Override
    public void mudou() {
        boolean rodando = estado.rodando;
        tarefa.setVisibility(rodando ? View.VISIBLE : View.GONE);
        if (rodando) {
            tarefaTitulo.setText(estado.trabalho);
            double f = estado.fracao;
            tarefaTexto.setText(estado.texto.isEmpty() ? "Rodando…" : estado.texto);
            tarefaBarra.setIndeterminate(f < 0);
            if (f >= 0) tarefaBarra.setProgress((int) (f * 100));
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        } else {
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        }
        if (log != null) {
            List<String> l = estado.log();
            StringBuilder sb = new StringBuilder();
            for (int i = Math.max(0, l.size() - 250); i < l.size(); i++) sb.append(l.get(i)).append('\n');
            log.setText(sb.length() == 0 ? "(o log do treino aparece aqui)" : sb.toString());
        }
        if (estavaRodando != rodando) {
            estavaRodando = rodando;
            montar();
            if (!rodando && estado.fim != null) {
                new AlertDialog.Builder(this).setTitle(estado.trabalho).setMessage(estado.fim).setPositiveButton("OK", null).show();
            }
        }
    }

    @Override
    public void estadoMudou() {
        // Só remonta quando uma tarefa do app termina (ex.: "Usar o resultado"), para não apagar o que se digita.
        boolean ocupado = motor.ocupado();
        if (motorOcupado && !ocupado && !estado.rodando) montar();
        motorOcupado = ocupado;
    }

    @Override
    public void aviso(String titulo, String texto) {
        new AlertDialog.Builder(this).setTitle(titulo == null ? "Laika" : titulo).setMessage(texto).setPositiveButton("OK", null).show();
    }

    // ---------- tela ----------

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private TextView texto(String s, float tamanho, int cor, boolean negrito) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(tamanho);
        t.setTextColor(getColor(cor));
        if (negrito) t.setTypeface(t.getTypeface(), Typeface.BOLD);
        return t;
    }

    private LinearLayout cartao(String titulo, String ajuda) {
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setBackgroundResource(R.drawable.cartao);
        c.setPadding(dp(16), dp(14), dp(16), dp(12));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        conteudo.addView(c, lp);
        c.addView(texto(titulo, 17, R.color.topo_texto, true));
        if (ajuda != null) {
            TextView a = texto(ajuda, 13, R.color.aviso, false);
            a.setPadding(0, dp(4), 0, dp(4));
            c.addView(a);
        }
        return c;
    }

    private TextView botao(LinearLayout pai, String rotulo, boolean primario, View.OnClickListener acao) {
        TextView b = texto(rotulo, 14, primario ? R.color.texto_usuario : R.color.chip_texto, true);
        b.setBackgroundResource(primario ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(14), dp(9), dp(14), dp(9));
        boolean livre = !estado.rodando && !motor.ocupado();
        b.setEnabled(livre);
        b.setAlpha(livre ? 1f : 0.5f);
        b.setOnClickListener(acao);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(8);
        pai.addView(b, lp);
        return b;
    }

    private EditText numero(LinearLayout pai, String rotulo, String valor, boolean decimal) {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        TextView t = texto(rotulo, 14, R.color.texto_laika, false);
        l.addView(t, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        EditText e = new EditText(this);
        e.setInputType(InputType.TYPE_CLASS_NUMBER | (decimal ? InputType.TYPE_NUMBER_FLAG_DECIMAL : 0));
        e.setText(valor);
        e.setTextColor(getColor(R.color.texto_laika));
        e.setGravity(Gravity.END);
        e.setMinWidth(dp(90));
        l.addView(e);
        pai.addView(l);
        return e;
    }

    private static int inteiro(EditText e, int padrao) {
        try {
            return Integer.parseInt(e.getText().toString().trim());
        } catch (RuntimeException x) {
            return padrao;
        }
    }

    private static float real(EditText e, float padrao) {
        try {
            return Float.parseFloat(e.getText().toString().trim().replace(',', '.'));
        } catch (RuntimeException x) {
            return padrao;
        }
    }

    private String descricaoBin(File f) {
        try (InputStream in = new FileInputStream(f)) {
            return ConversorPt.lerBin(in).descricao();
        } catch (Exception e) {
            return "arquivo com erro";
        }
    }

    private void montar() {
        salvarOpcoes();
        conteudo.removeAllViews();
        Corpus corpus = TreinoService.corpus(this);
        File pasta = TreinoService.pastaTreino(this), saida = new File(pasta, "saida");

        TextView intro = texto("Tudo o que o Colab faz, aqui no celular, usando a GPU (OpenGL ES 3.1). O treino continua "
                + "com a tela apagada; deixe o celular carregando. Pré-treinar do zero leva muitas horas; o fine-tuning, "
                + "de minutos a uma hora.", 13, R.color.aviso, false);
        intro.setPadding(dp(4), 0, dp(4), dp(10));
        conteudo.addView(intro);

        // 1) dados
        LinearLayout c1 = cartao("1. Dados", "No Colab, rode a célula \"6) EXPORTAR DADOS PARA O CELULAR\". Ela grava "
                + "laika_dados.zip em Meu Drive/LLM_Laika. Baixe o arquivo no celular (app do Google Drive) e escolha aqui.");
        TextView r = texto(corpus.resumo(), 13, R.color.texto_laika, false);
        r.setPadding(0, dp(4), 0, 0);
        c1.addView(r);
        botao(c1, "Importar laika_dados.zip", true, v -> {
            pedirNotificacoes();
            escolherZip.launch(new String[]{"*/*"});
        });
        botao(c1, "Apagar livros e artigos", false, v -> new AlertDialog.Builder(this)
                .setMessage("Apagar os livros, artigos e perguntas da Wikipédia importados? (Os textos próprios e as perguntas "
                        + "escritas continuam.)")
                .setPositiveButton("Apagar", (d, w) -> {
                    corpus.apagar("books");
                    corpus.apagar("wiki");
                    corpus.apagar("qa_auto");
                    montar();
                }).setNegativeButton("Cancelar", null).show());

        // 2) índice
        File db = new File(saida, "laika_rag.db");
        LinearLayout c2 = cartao("2. Índice do RAG", "Monta a busca nos textos (como \"python rag.py build\"). Com os 100 mil "
                + "artigos e 495 livros, leva alguns minutos e ocupa ~640 MB.");
        c2.addView(texto(db.exists() ? String.format(Locale.getDefault(), "Montado: %d MB", db.length() >> 20)
                : "Ainda não montado aqui (o fine-tuning usa o índice da versão em uso).", 13, R.color.texto_laika, false));
        botao(c2, "Montar índice", true, v -> comecar(new String[]{TreinoService.INDICE}));

        // 3) pré-treino
        String interrompido = PreTreino.interrompido(pasta);
        LinearLayout c3 = cartao("3. Pré-treino", "Ensina português com os livros e artigos. \"Continuar\" parte do modelo "
                + "pré-treinado em uso (mesmo tokenizer); \"Do zero\" treina um tokenizer novo e começa com pesos aleatórios.");
        modo = new RadioGroup(this);
        String modoSalvo = prefs.getString("modo", "CONTINUAR");
        for (String[] m : new String[][]{{"CONTINUAR", "Continuar do modelo em uso"}, {"DO_ZERO", "Do zero (tokenizer novo)"},
                {"RETOMAR", "Retomar o treino parado" + (interrompido != null ? " (" + interrompido + ")" : "")}}) {
            RadioButton b = new RadioButton(this);
            b.setText(m[1]);
            b.setTag(m[0]);
            b.setTextColor(getColor(R.color.texto_laika));
            b.setId(View.generateViewId());
            if (m[0].equals("RETOMAR") && interrompido == null) b.setEnabled(false);
            modo.addView(b);
            if (m[0].equals(interrompido != null ? "RETOMAR" : modoSalvo.equals("RETOMAR") ? "CONTINUAR" : modoSalvo)) b.setChecked(true);
        }
        c3.addView(modo);
        LinearLayout lp = new LinearLayout(this);
        lp.setGravity(Gravity.CENTER_VERTICAL);
        lp.addView(texto("Tamanho", 14, R.color.texto_laika, false), new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
        preset = new Spinner(this);
        List<String> nomes = new ArrayList<>(), rotulos = new ArrayList<>();
        for (Presets.Preset p : Presets.TODOS.values()) {
            nomes.add(p.nome);
            rotulos.add(p.nome + " — " + p.descricao);
        }
        preset.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, rotulos));
        preset.setSelection(Math.max(0, nomes.indexOf(prefs.getString("preset", "colab"))));
        lp.addView(preset);
        c3.addView(lp);
        passos = numero(c3, "Passos (0 = o do preset: 10.000 no colab)", String.valueOf(prefs.getInt("passos", 0)), false);
        microLote = numero(c3, "Micro-lote (sequências por vez na GPU)", String.valueOf(prefs.getInt("micro", 8)), false);
        Presets.Preset ps = Presets.TODOS.get(nomes.get(preset.getSelectedItemPosition()));
        Rede.Config cfg = new Rede.Config(ps.vocab, ps.block, ps.dim, ps.heads, ps.layers, ps.dropout);
        c3.addView(texto(String.format(Locale.getDefault(), "Memória da GPU com micro-lote %d: ~%d MB. Se der erro de memória, "
                + "use 4 ou 2.", inteiro(microLote, 8), Rede.memoriaNecessaria(cfg, Math.max(1, inteiro(microLote, 8))) >> 20),
                12, R.color.aviso, false));
        botao(c3, "Começar pré-treino", true, v -> comecar(new String[]{TreinoService.PRETREINO}));

        // 4) fine-tuning
        File baseAqui = new File(saida, "laika_base.bin");
        LinearLayout c4 = cartao("4. Fine-tuning", "Ensina a responder (perguntas escritas, exemplos dos livros, perguntas da "
                + "Wikipédia, parte com Contexto do RAG). Mostra 8 respostas de teste por época no log.");
        doResultado = new CheckBox(this);
        doResultado.setText(baseAqui.exists() ? "Partir do pré-treino feito aqui (" + descricaoBin(baseAqui) + ")"
                : "Partir do pré-treino feito aqui (ainda não há; usa o modelo em uso)");
        doResultado.setChecked(baseAqui.exists() && prefs.getBoolean("doResultado", true));
        doResultado.setEnabled(baseAqui.exists());
        doResultado.setTextColor(getColor(R.color.texto_laika));
        c4.addView(doResultado);
        comRag = new CheckBox(this);
        comRag.setText("Usar o RAG (Contexto em ~50% das perguntas)");
        comRag.setChecked(prefs.getBoolean("rag", true));
        comRag.setTextColor(getColor(R.color.texto_laika));
        c4.addView(comRag);
        epocas = numero(c4, "Épocas", String.valueOf(prefs.getInt("epocas", 2)), false);
        textoMb = numero(c4, "MB de texto para exemplos e replay", String.valueOf(prefs.getFloat("textoMb", 15)), true);
        botao(c4, "Começar fine-tuning", true, v -> comecar(new String[]{TreinoService.FINETUNING}));

        // tudo
        LinearLayout ct = cartao("Rodar tudo em sequência", "Índice → pré-treino → fine-tuning, com as opções acima "
                + "(como rodar as células 2, 3 e 4 do Colab).");
        botao(ct, "Rodar tudo", false, v -> comecar(new String[]{TreinoService.INDICE, TreinoService.PRETREINO,
                TreinoService.FINETUNING}));

        // 5) usar
        LinearLayout c5 = cartao("5. Usar o resultado", "Vira uma versão nova (a versão em uso é guardada nos backups).");
        String[][] arqs = {{"laika_chat.bin", "Chat"}, {"laika_base.bin", "Pré-treino"}, {"tokenizer.txt", "Tokenizer"},
                {"laika_rag.db", "Índice"}};
        boolean algum = false;
        for (String[] a : arqs) {
            File f = new File(saida, a[0]);
            String d;
            if (!f.exists()) d = "—";
            else if (a[0].endsWith(".bin")) d = descricaoBin(f);
            else if (a[0].endsWith(".txt")) {
                try (InputStream in = new FileInputStream(f)) {
                    d = Armazem.descricaoTokenizer(in);
                } catch (Exception e) {
                    d = "arquivo com erro";
                }
            } else d = (f.length() >> 20) + " MB";
            algum |= f.exists();
            TextView t = texto(a[1] + ": " + d, 13, R.color.texto_laika, false);
            t.setPadding(0, dp(2), 0, 0);
            c5.addView(t);
        }
        if (algum) {
            botao(c5, "Usar o resultado", true, v -> motor.usarResultadoDoTreino(saida));
            TextView apagar = botao(c5, "Apagar o resultado", false, v -> new AlertDialog.Builder(this)
                    .setMessage("Apagar os arquivos do treino (saida/)? A versão em uso não muda.")
                    .setPositiveButton("Apagar", (d, w) -> {
                        File[] fs = saida.listFiles();
                        if (fs != null) for (File f : fs) f.delete();
                        montar();
                    }).setNegativeButton("Cancelar", null).show());
            apagar.setTextColor(getColor(R.color.perigo));
        }

        // log
        LinearLayout cl = cartao("Log", null);
        log = texto("", 11, R.color.texto_laika, false);
        log.setTypeface(Typeface.MONOSPACE);
        log.setTextIsSelectable(true);
        ScrollView sv = new ScrollView(this);
        sv.addView(log);
        cl.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(320)));
        sv.post(() -> sv.fullScroll(View.FOCUS_DOWN));
        mudou();
    }

    private void salvarOpcoes() {
        if (modo == null) return;
        SharedPreferences.Editor e = prefs.edit();
        View m = modo.findViewById(modo.getCheckedRadioButtonId());
        if (m != null) e.putString("modo", (String) m.getTag());
        List<String> nomes = new ArrayList<>(Presets.TODOS.keySet());
        e.putString("preset", nomes.get(preset.getSelectedItemPosition()));
        e.putInt("passos", inteiro(passos, 0));
        e.putInt("micro", Math.max(1, inteiro(microLote, 8)));
        e.putInt("epocas", Math.max(1, inteiro(epocas, 2)));
        e.putFloat("textoMb", Math.max(1, real(textoMb, 15)));
        e.putBoolean("rag", comRag.isChecked());
        e.putBoolean("doResultado", doResultado.isChecked());
        e.apply();
    }

    private void pedirNotificacoes() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
        }
    }

    private void comecar(String[] etapas) {
        salvarOpcoes();
        pedirNotificacoes();
        Intent i = new Intent().putExtra("etapas", etapas)
                .putExtra("modo", prefs.getString("modo", "CONTINUAR"))
                .putExtra("preset", prefs.getString("preset", "colab"))
                .putExtra("maxSteps", prefs.getInt("passos", 0))
                .putExtra("microLote", prefs.getInt("micro", 8))
                .putExtra("epocas", prefs.getInt("epocas", 2))
                .putExtra("maxTextoMb", prefs.getFloat("textoMb", 15))
                .putExtra("rag", prefs.getBoolean("rag", true))
                .putExtra("doResultado", prefs.getBoolean("doResultado", true));
        boolean temPre = false;
        for (String s : etapas) temPre |= s.equals(TreinoService.PRETREINO);
        if (temPre) i.putExtra("doResultado", true);  // em sequência, o fine-tuning parte do pré-treino que acabou de rodar
        if (temPre && "DO_ZERO".equals(prefs.getString("modo", "")) && PreTreino.interrompido(TreinoService.pastaTreino(this)) != null) {
            new AlertDialog.Builder(this).setMessage("Há um pré-treino parado. Começar do zero apaga o progresso dele. Continuar?")
                    .setPositiveButton("Começar do zero", (d, w) -> {
                        PreTreino.estadoJson(TreinoService.pastaTreino(this)).delete();
                        TreinoService.iniciar(this, i);
                    }).setNegativeButton("Cancelar", null).show();
            return;
        }
        TreinoService.iniciar(this, i);
    }
}
