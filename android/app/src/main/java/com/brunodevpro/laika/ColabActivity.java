package com.brunodevpro.laika;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.colab.Caderno;
import com.brunodevpro.laika.core.colab.GitHub;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Liga as células do colab.ipynb pelo celular. O app dispara o workflow "Laika no Colab" do
 * repositório no GitHub, que liga uma máquina do Colab com o Colab CLI, roda as células com os
 * parâmetros escolhidos aqui e desliga a máquina no fim (não precisa deixar o Colab aberto).
 * O zip da célula 6 aparece em "Modelos prontos" e vira uma versão nova com um toque.
 */
public class ColabActivity extends ComponentActivity implements Motor.Ouvinte {
    private static final String[] GPUS = {"T4", "L4", "G4", "A100", "H100", "nenhuma"};
    private static final String[] NOMES_GPU = {"T4", "L4", "G4", "A100", "H100",
            "Sem GPU (só para baixar dados e exportar)"};
    private static final String URL_TOKEN = "https://github.com/settings/personal-access-tokens/new";

    private Motor motor;
    private PainelTarefa painel;
    private LinearLayout caixaConfig, caixaCelulas, caixaExecucoes, caixaModelos, caixaConta;
    private final ExecutorService rede = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());

    private List<Caderno.Celula> celulas;
    private final Set<Integer> marcadas = new TreeSet<>();
    private final Map<String, String> valores = new HashMap<>();
    private String gpu;
    private List<GitHub.Execucao> execucoes = new ArrayList<>();
    private Map<Long, GitHub.Verificacao> verificacoes = new HashMap<>();
    private List<GitHub.Artefato> artefatos = new ArrayList<>();
    private String erroRede;
    private boolean temWorkflow = true, buscando, visivel;
    private long aberta = -1;
    private int rodadas;

    private final Runnable periodico = new Runnable() {
        @Override
        public void run() {
            if (!visivel) return;
            atualizar(false);
        }
    };

    private final ActivityResultLauncher<String> pedirNotificacoes = registerForActivityResult(
            new ActivityResultContracts.RequestPermission(), ok -> {
            });

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_versoes);
        motor = Motor.get(this);
        ((TextView) findViewById(R.id.titulo)).setText(R.string.colab);
        findViewById(R.id.voltar).setOnClickListener(v -> finish());
        painel = new PainelTarefa(this, motor);
        LinearLayout conteudo = findViewById(R.id.conteudo);
        caixaConfig = caixa(conteudo);
        caixaCelulas = caixa(conteudo);
        caixaExecucoes = caixa(conteudo);
        caixaModelos = caixa(conteudo);
        caixaConta = caixa(conteudo);

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

        // Escolhas guardadas da última vez
        android.content.SharedPreferences p = Colab.prefs(this);
        gpu = p.getString("gpu", "T4");
        for (String s : p.getString("marcadas", "4,6").split(",")) {
            if (!s.isEmpty()) marcadas.add(Integer.parseInt(s));
        }
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> v = (Map<String, Object>) Json.ler(p.getString("valores", "{}"));
            for (Map.Entry<String, Object> e : v.entrySet()) valores.put(e.getKey(), String.valueOf(e.getValue()));
        } catch (RuntimeException ignorado) {
            // sem valores guardados
        }
        String cache = p.getString("caderno", null);
        if (cache != null) {
            try {
                celulas = Caderno.ler(cache);
            } catch (RuntimeException ignorado) {
                celulas = null;
            }
        }
    }

    private LinearLayout caixa(LinearLayout pai) {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        pai.addView(l, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
        return l;
    }

    @Override
    protected void onStart() {
        super.onStart();
        visivel = true;
        motor.adicionarOuvinte(this);
        painel.atualizar();
        montarTudo();
        if (Colab.configurado(this)) atualizar(true);
    }

    @Override
    protected void onStop() {
        visivel = false;
        ui.removeCallbacks(periodico);
        motor.removerOuvinte(this);
        guardarEscolhas();
        if (!Colab.vigiadas(this).isEmpty()) Colab.agendar(this, 60_000);
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        rede.shutdownNow();
        super.onDestroy();
    }

    private void guardarEscolhas() {
        StringBuilder m = new StringBuilder();
        for (int n : marcadas) m.append(m.length() > 0 ? "," : "").append(n);
        Colab.prefs(this).edit().putString("gpu", gpu).putString("marcadas", m.toString())
                .putString("valores", Json.escrever(new LinkedHashMap<String, Object>(valores))).apply();
    }

    @Override
    public void estadoMudou() {
        painel.atualizar();
        montarModelos();  // os botões de baixar ficam desligados durante outra tarefa
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

    // ---------- rede ----------

    /** Busca no GitHub o que a tela mostra. tudo: também o notebook (as células). */
    private void atualizar(boolean tudo) {
        if (buscando || !Colab.configurado(this)) return;
        buscando = true;
        ui.removeCallbacks(periodico);
        boolean comArtefatos = tudo || rodadas++ % 4 == 0;
        long abertaAgora = aberta;
        rede.execute(() -> {
            GitHub g = Colab.github(this);
            String erro = null, caderno = null, ramo = null;
            Boolean wf = null;
            List<GitHub.Execucao> ex = null;
            Map<Long, GitHub.Verificacao> vers = new HashMap<>();
            List<GitHub.Artefato> arts = null;
            try {
                if (tudo || celulas == null) {
                    ramo = g.ramoPrincipal();
                    wf = g.temWorkflow();
                    caderno = g.caderno(ramo);
                }
                ex = g.execucoes(8);
                for (GitHub.Execucao e : ex) {
                    if (!e.terminou() || e.id == abertaAgora) {
                        try {
                            GitHub.Verificacao v = g.verificacao(e);
                            if (v != null) vers.put(e.id, v);
                        } catch (IOException semDetalhes) {
                            // a execução aparece sem os detalhes ao vivo
                        }
                    }
                }
                if (comArtefatos) arts = g.artefatos();
            } catch (IOException | RuntimeException e) {
                erro = e.getMessage() == null ? e.toString() : e.getMessage();
            }
            String fErro = erro, fCaderno = caderno, fRamo = ramo;
            Boolean fWf = wf;
            List<GitHub.Execucao> fEx = ex;
            List<GitHub.Artefato> fArts = arts;
            ui.post(() -> {
                buscando = false;
                if (isDestroyed()) return;
                erroRede = fErro;
                if (fRamo != null) Colab.prefs(this).edit().putString("ramo", fRamo).apply();
                if (fWf != null) temWorkflow = fWf;
                if (fCaderno != null) {
                    try {
                        celulas = Caderno.ler(fCaderno);
                        Colab.prefs(this).edit().putString("caderno", fCaderno).apply();
                    } catch (RuntimeException e) {
                        erroRede = "o colab.ipynb do repositório não abriu: " + e.getMessage();
                    }
                    montarCelulas();
                }
                if (fEx != null) {
                    execucoes = fEx;
                    verificacoes = vers;
                }
                if (fArts != null) artefatos = fArts;
                montarConfig();
                montarExecucoes();
                montarModelos();
                boolean ativa = false;
                for (GitHub.Execucao e : execucoes) ativa |= !e.terminou();
                if (visivel) ui.postDelayed(periodico, ativa ? 10_000 : 60_000);
            });
        });
    }

    // ---------- montagem da tela ----------

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

    private void secao(LinearLayout pai, String titulo) {
        TextView t = texto(titulo, 12, R.color.topo_sub, true);
        t.setLetterSpacing(0.08f);
        t.setPadding(dp(4), dp(18), dp(4), dp(8));
        pai.addView(t);
    }

    private LinearLayout cartao(LinearLayout pai) {
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setBackgroundResource(R.drawable.cartao);
        c.setPadding(dp(16), dp(14), dp(16), dp(12));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        pai.addView(c, lp);
        return c;
    }

    private LinearLayout linha(LinearLayout pai) {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.HORIZONTAL);
        pai.addView(l);
        return l;
    }

    private TextView botao(LinearLayout linha, String rotulo, boolean primario, View.OnClickListener acao) {
        TextView b = texto(rotulo, 14, primario ? R.color.texto_usuario : R.color.chip_texto, true);
        b.setBackgroundResource(primario ? R.drawable.botao_primario : R.drawable.botao_secundario);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(14), dp(8), dp(14), dp(8));
        b.setOnClickListener(acao);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(8);
        lp.topMargin = dp(8);
        linha.addView(b, lp);
        return b;
    }

    private static void ligado(View v, boolean ligado) {
        v.setEnabled(ligado);
        v.setAlpha(ligado ? 1f : 0.45f);
    }

    private void abrirLink(String url) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
        } catch (RuntimeException e) {
            Toast.makeText(this, "Nenhum navegador para abrir " + url, Toast.LENGTH_LONG).show();
        }
    }

    private void montarTudo() {
        montarConfig();
        montarCelulas();
        montarExecucoes();
        montarModelos();
        montarConta();
    }

    // --- configuração ---

    private void montarConfig() {
        caixaConfig.removeAllViews();
        if (!Colab.configurado(this)) {
            secao(caixaConfig, "LIGAR AO COLAB");
            LinearLayout c = cartao(caixaConfig);
            c.addView(texto("Treinar na nuvem sem deixar o Colab aberto", 16, R.color.topo_texto, true));
            TextView t = texto("O app pede ao GitHub Actions do seu repositório para ligar uma máquina do Colab "
                    + "(com o Colab CLI), rodar as células que você escolher e desligar no fim. Você pode fechar o "
                    + "app: ele avisa quando terminar.\n\nUma vez só:\n"
                    + "1. No GitHub, junte o branch do app ao main (o arquivo .github/workflows/colab.yml precisa "
                    + "estar no branch principal).\n"
                    + "2. Crie um token \"fine-grained\" só para o repositório LLM_Laika, com as permissões "
                    + "Actions (leitura e escrita), Secrets (leitura e escrita) e Contents (leitura).\n"
                    + "3. No Colab (navegador), rode a célula 0 do colab.ipynb: ela autoriza o Colab CLI com a sua "
                    + "conta Google e guarda essa permissão no GitHub.\n"
                    + "4. Cole aqui o repositório e o token.", 13, R.color.texto_laika, false);
            t.setPadding(0, dp(6), 0, dp(4));
            c.addView(t);
            EditText repo = campo(c, "Repositório (dono/nome)", Colab.repo(this), false);
            EditText token = campo(c, "Token do GitHub", "", true);
            LinearLayout l = linha(c);
            botao(l, "Conectar", true, v -> conectar(repo.getText().toString(), token.getText().toString()));
            botao(l, "Criar token", false, v -> abrirLink(URL_TOKEN));
            LinearLayout l2 = linha(c);
            botao(l2, "Abrir o colab.ipynb no Colab", false, v -> abrirLink(urlColab()));
            return;
        }
        if (erroRede != null || !temWorkflow) {
            LinearLayout c = cartao(caixaConfig);
            String msg = !temWorkflow ? "O workflow do Colab (.github/workflows/colab.yml) ainda não está no branch "
                    + "principal do repositório. No GitHub, junte o branch do app ao main e toque em Tentar de novo."
                    : "Não consegui falar com o GitHub: " + erroRede;
            c.addView(texto(msg, 14, R.color.perigo, false));
            LinearLayout l = linha(c);
            botao(l, "Tentar de novo", true, v -> atualizar(true));
            botao(l, "Trocar o token", false, v -> trocarToken());
        }
    }

    private String urlColab() {
        return "https://colab.research.google.com/github/" + Colab.repo(this) + "/blob/" + Colab.ramo(this) + "/colab.ipynb";
    }

    private EditText campo(LinearLayout pai, String dica, String valor, boolean senha) {
        EditText e = new EditText(this);
        e.setHint(dica);
        e.setText(valor);
        e.setTextSize(15);
        e.setSingleLine(true);
        e.setInputType(senha ? InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD
                : InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        pai.addView(e, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT));
        return e;
    }

    private void conectar(String repo, String token) {
        repo = repo.trim().replaceFirst("^https?://github\\.com/", "").replaceAll("/+$", "");
        if (!repo.matches("[\\w.-]+/[\\w.-]+") || token.trim().length() < 20) {
            Toast.makeText(this, "Confira o repositório (dono/nome) e o token.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Colab.salvar(this, repo, token);
        } catch (IOException e) {
            Toast.makeText(this, "Não consegui guardar o token: " + e.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        celulas = null;
        montarTudo();
        atualizar(true);
    }

    private void trocarToken() {
        new AlertDialog.Builder(this).setTitle("Trocar o token?")
                .setMessage("O token guardado no celular é apagado e você cola outro (o repositório pode mudar também).")
                .setPositiveButton("Trocar", (d, w) -> {
                    Colab.esquecerToken(this);
                    montarTudo();
                })
                .setNegativeButton("Cancelar", null).show();
    }

    // --- células ---

    private void montarCelulas() {
        caixaCelulas.removeAllViews();
        if (!Colab.configurado(this)) return;
        secao(caixaCelulas, "RODAR CÉLULAS NO COLAB");
        if (celulas == null) {
            TextView t = texto(erroRede == null ? "Lendo as células do colab.ipynb…" : "As células aparecem quando o "
                    + "app conseguir ler o colab.ipynb do repositório.", 14, R.color.aviso, false);
            t.setPadding(dp(4), 0, dp(4), 0);
            caixaCelulas.addView(t);
            return;
        }
        LinearLayout atalhos = cartao(caixaCelulas);
        atalhos.addView(texto("Atalhos", 13, R.color.topo_sub, true));
        LinearLayout a1 = linha(atalhos), a2 = linha(atalhos), a3 = linha(atalhos), a4 = linha(atalhos);
        botao(a1, "Só fine-tuning", false, v -> marcar(4, 6));
        botao(a1, "Tudo do zero", false, v -> {
            valores.put("3.MODO", "do_zero");
            marcar(2, 3, 4, 6);
        });
        botao(a2, "Atualizar dados", false, v -> marcar(2));
        botao(a2, "Só exportar", false, v -> marcar(6));
        // Baixar 1 milhão de artigos não precisa de GPU (economiza unidades); o treino vem depois.
        botao(a3, "1 milhão de artigos", false, v -> {
            valores.put("2.ARTIGOS", "1 milhão");
            gpu = "nenhuma";
            marcar(2);
        });
        // ~52M de parâmetros: tokenizer e modelo novos (do_zero), melhor na A100.
        botao(a3, "Modelo de 50M", false, v -> {
            valores.put("3.MODO", "do_zero");
            valores.put("3.PRESET", "colab_50m");
            gpu = "A100";
            marcar(3, 4, 6);
        });
        // 100M (contexto 2048, RoPE): primeiro os dados (Wikipédia inteira, Carolina, GigaVerbo; sem GPU),
        // depois o treino na A100 e a avaliação (célula 7). Se parar no limite de 6 h, rode "Modelo de 100M" de novo
        // com MODO "continuar". Os dados incluem 300 mil conversas do GigaVerbo-v2-SFT para o fine-tuning.
        botao(a4, "Dados para 100M", false, v -> {
            valores.put("2.ARTIGOS", "todos (~1,1 milhão)");
            valores.put("2.CAROLINA", "true");
            valores.put("2.GIGAVERBO", "1,5 bilhão de tokens");
            valores.put("2.SFT", "300 mil conversas");
            gpu = "nenhuma";
            marcar(2);
        });
        botao(a4, "Modelo de 100M", false, v -> {
            valores.put("3.MODO", "do_zero");
            valores.put("3.PRESET", "colab_100m");
            valores.put("4.PERGUNTAS_WIKIPEDIA", "40000");
            gpu = "A100";
            marcar(3, 4, 6, 7);
        });
        TextView g = texto("GPU: " + nomeGpu(gpu) + "  ▾", 15, R.color.topo_texto, true);
        g.setPadding(0, dp(12), 0, dp(4));
        g.setOnClickListener(v -> escolherGpu());
        atalhos.addView(g);

        for (Caderno.Celula c : celulas) montarCelula(c);

        LinearLayout fim = linha(caixaCelulas);
        TextView rodar = botao(fim, "Rodar no Colab", true, v -> confirmarRodar());
        rodar.setPadding(dp(22), dp(11), dp(22), dp(11));
    }

    private void marcar(Integer... ns) {
        marcadas.clear();
        for (int n : ns) marcadas.add(n);
        montarCelulas();
        guardarEscolhas();
    }

    private static String nomeGpu(String g) {
        for (int i = 0; i < GPUS.length; i++) if (GPUS[i].equals(g)) return NOMES_GPU[i];
        return g;
    }

    private void escolherGpu() {
        int atual = 0;
        for (int i = 0; i < GPUS.length; i++) if (GPUS[i].equals(gpu)) atual = i;
        new AlertDialog.Builder(this).setTitle("GPU do Colab")
                .setSingleChoiceItems(NOMES_GPU, atual, (d, i) -> {
                    gpu = GPUS[i];
                    d.dismiss();
                    montarCelulas();
                    guardarEscolhas();
                }).show();
    }

    private void montarCelula(Caderno.Celula c) {
        LinearLayout k = cartao(caixaCelulas);
        boolean sempre = c.numero == 1;
        CheckBox cb = new CheckBox(this);
        cb.setText(c.numero + ") " + c.nome);
        cb.setTextSize(16);
        cb.setTypeface(cb.getTypeface(), Typeface.BOLD);
        cb.setTextColor(getColor(R.color.topo_texto));
        cb.setChecked(sempre || marcadas.contains(c.numero));
        ligado(cb, !sempre && !c.soNavegador);
        k.addView(cb);
        String desc = c.soNavegador ? "Só no navegador (" + (c.numero == 0 ? "rode uma vez para ligar o app ao Colab" : "conversa interativa")
                + ")." : sempre ? "Sempre roda antes das outras (monta o Drive, baixa o código). NOME: o nome do modelo no app (vai "
                + "direto para os backups). PROJETO: um modelo em pastas só dele; PARTIR_DE = \"padrão\" copia para ele o pré-treino de sempre, "
                + "senão comece pela célula 3." : resumo(c);
        TextView d = texto(desc, 12, R.color.aviso, false);
        d.setPadding(dp(32), 0, 0, dp(2));
        k.addView(d);
        if (c.soNavegador) return;
        LinearLayout params = new LinearLayout(this);
        params.setOrientation(LinearLayout.VERTICAL);
        params.setPadding(dp(32), 0, 0, 0);
        k.addView(params);
        // Da célula 1 só aparece o PROJETO: o RAMO vem do GitHub (o laika_colab.py usa o ramo do workflow).
        for (Caderno.Parametro p : c.parametros) if (!(sempre && p.nome.equals("RAMO"))) montarParametro(params, c, p);
        if (sempre) return;
        params.setVisibility(cb.isChecked() ? View.VISIBLE : View.GONE);
        cb.setOnCheckedChangeListener((v, marcada) -> {
            if (marcada) marcadas.add(c.numero);
            else marcadas.remove(c.numero);
            params.setVisibility(marcada ? View.VISIBLE : View.GONE);
            guardarEscolhas();
        });
    }

    /** Descrição curta: o resto do título, ou a primeira linha dos comentários. */
    private static String resumo(Caderno.Celula c) {
        String resto = c.titulo.substring(Math.min(c.titulo.length(), c.nome.length())).replaceFirst("^[\\s:—]+", "");
        String s = resto.isEmpty() ? c.descricao.split("\n")[0] : resto;
        return s.length() > 160 ? s.substring(0, 157) + "…" : s;
    }

    /** O valor escolhido, ou o padrão do notebook se o guardado não vale mais (o parâmetro mudou de tipo). */
    private String valor(Caderno.Celula c, Caderno.Parametro p) {
        String chave = c.numero + "." + p.nome, v = valores.get(chave);
        if (v != null) {
            try {
                Caderno.converter(p, v);
                return v;
            } catch (IllegalArgumentException naoVale) {
                valores.remove(chave);
            }
        }
        return Caderno.textoDoPadrao(p);
    }

    private void montarParametro(LinearLayout pai, Caderno.Celula c, Caderno.Parametro p) {
        String chave = c.numero + "." + p.nome;
        if (p.tipo.equals("boolean")) {
            CheckBox b = new CheckBox(this);
            b.setText(p.nome);
            b.setTextSize(14);
            b.setTextColor(getColor(R.color.texto_laika));
            b.setChecked("true".equals(valor(c, p)));
            b.setOnCheckedChangeListener((v, x) -> valores.put(chave, x ? "true" : "false"));
            pai.addView(b);
            return;
        }
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.HORIZONTAL);
        l.setGravity(Gravity.CENTER_VERTICAL);
        TextView nome = texto(p.nome, 14, R.color.texto_laika, false);
        nome.setMinWidth(dp(96));
        l.addView(nome);
        if (p.tipo.equals("opcoes")) {
            TextView o = texto(valor(c, p) + "  ▾", 15, R.color.azul, true);
            o.setPadding(dp(8), dp(10), dp(8), dp(10));
            o.setOnClickListener(v -> {
                String[] ops = p.opcoes.toArray(new String[0]);
                int atual = Math.max(0, p.opcoes.indexOf(valor(c, p)));
                new AlertDialog.Builder(this).setTitle(p.nome).setSingleChoiceItems(ops, atual, (d, i) -> {
                    valores.put(chave, ops[i]);
                    o.setText(ops[i] + "  ▾");
                    d.dismiss();
                }).show();
            });
            l.addView(o);
        } else {
            EditText e = new EditText(this);
            e.setText(valor(c, p));
            e.setTextSize(15);
            e.setSingleLine(true);
            e.setMinWidth(dp(120));
            e.setInputType(p.tipo.equals("integer") ? InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_SIGNED
                    : p.tipo.equals("number") ? InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL
                    : InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
            e.addTextChangedListener(new TextWatcher() {
                public void beforeTextChanged(CharSequence s, int a, int b, int d) {
                }

                public void onTextChanged(CharSequence s, int a, int b, int d) {
                }

                public void afterTextChanged(Editable s) {
                    valores.put(chave, s.toString());
                }
            });
            l.addView(e);
        }
        pai.addView(l);
    }

    // --- rodar ---

    private void confirmarRodar() {
        if (celulas == null) return;
        Map<String, Object> params = new LinkedHashMap<>();
        List<String> nomes = new ArrayList<>(), mudados = new ArrayList<>();
        StringBuilder lista = new StringBuilder();
        for (Caderno.Celula c : celulas) {
            if (c.soNavegador || (c.numero != 1 && !marcadas.contains(c.numero))) continue;
            nomes.add(c.numero + ") " + c.nome);
            if (c.numero != 1) lista.append(lista.length() > 0 ? "," : "").append(c.numero);
            Map<String, Object> daCelula = new LinkedHashMap<>();
            for (Caderno.Parametro p : c.parametros) {
                if (c.numero == 1 && p.nome.equals("RAMO")) continue;  // o laika_colab.py usa o ramo do GitHub
                String v = valor(c, p);
                if (v.equals(Caderno.textoDoPadrao(p))) continue;  // só o que mudou
                try {
                    daCelula.put(p.nome, Caderno.converter(p, v));
                } catch (IllegalArgumentException e) {
                    Toast.makeText(this, "Célula " + c.numero + ": " + e.getMessage(), Toast.LENGTH_LONG).show();
                    return;
                }
                mudados.add(p.nome + " = " + v);
            }
            if (!daCelula.isEmpty()) params.put(String.valueOf(c.numero), daCelula);
        }
        if (lista.length() == 0) {
            Toast.makeText(this, "Marque pelo menos uma célula.", Toast.LENGTH_SHORT).show();
            return;
        }
        String celulasPedidas = lista.toString(), json = Json.escrever(params);
        new AlertDialog.Builder(this).setTitle("Rodar no Colab?")
                .setMessage(String.join("\n", nomes) + "\n\nGPU: " + nomeGpu(gpu)
                        + (mudados.isEmpty() ? "" : "\nParâmetros: " + String.join(", ", mudados))
                        + "\n\nO Colab gasta unidades de computação enquanto a máquina estiver ligada (ela desliga "
                        + "sozinha no fim, ou em até 6 horas). Pode fechar o app: ele avisa quando terminar.")
                .setPositiveButton("Rodar", (d, w) -> rodar(celulasPedidas, json))
                .setNegativeButton("Cancelar", null).show();
    }

    private void rodar(String celulasPedidas, String parametros) {
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            pedirNotificacoes.launch(Manifest.permission.POST_NOTIFICATIONS);
        }
        String ramo = Colab.ramo(this), g = gpu;
        Toast.makeText(this, "Enviando o pedido…", Toast.LENGTH_SHORT).show();
        rede.execute(() -> {
            String msg;
            try {
                String pedido = Colab.novoPedido();
                long id = Colab.github(this).disparar(ramo, celulasPedidas, g, parametros, pedido);
                Colab.vigiar(this, id, pedido, celulasPedidas);
                msg = "Pedido enviado. A máquina do Colab liga em um ou dois minutos.";
            } catch (IOException e) {
                msg = "Não consegui pedir: " + e.getMessage();
            }
            String m = msg;
            ui.post(() -> {
                Toast.makeText(this, m, Toast.LENGTH_LONG).show();
                ui.postDelayed(() -> atualizar(false), 4000);
            });
        });
    }

    // --- execuções ---

    private static String situacao(GitHub.Execucao e) {
        if (!e.terminou()) return "in_progress".equals(e.status) ? "rodando" : "na fila";
        if (e.deuCerto()) return "pronta";
        if ("cancelled".equals(e.conclusao)) return "cancelada";
        return "falhou";
    }

    private static String tituloCurto(GitHub.Execucao e) {
        String t = e.titulo == null ? "" : e.titulo;
        return t.replaceFirst("^Colab:\\s*", "").replaceAll("\\s*#\\w+$", "");
    }

    private void montarExecucoes() {
        caixaExecucoes.removeAllViews();
        if (!Colab.configurado(this) || execucoes.isEmpty()) return;
        secao(caixaExecucoes, "EXECUÇÕES");
        for (GitHub.Execucao e : execucoes) {
            LinearLayout c = cartao(caixaExecucoes);
            boolean ativa = !e.terminou(), detalhes = ativa || e.id == aberta;
            String sit = situacao(e);
            TextView t = texto(tituloCurto(e), 15, R.color.topo_texto, true);
            c.addView(t);
            int cor = sit.equals("falhou") ? R.color.perigo : sit.equals("pronta") ? R.color.azul : R.color.topo_sub;
            c.addView(texto(sit + " · " + Colab.ha(e.criada), 12, cor, true));
            c.setOnClickListener(v -> {
                aberta = aberta == e.id ? -1 : e.id;
                if (aberta == e.id && !verificacoes.containsKey(e.id)) atualizar(false);
                montarExecucoes();
            });
            if (!detalhes) continue;
            GitHub.Verificacao v = verificacoes.get(e.id);
            if (v != null) {
                if (!v.titulo.isEmpty()) {
                    TextView vt = texto(v.titulo, 14, R.color.texto_laika, false);
                    vt.setPadding(0, dp(6), 0, dp(2));
                    c.addView(vt);
                }
                for (Map<String, Object> cel : v.celulas()) {
                    String s = String.valueOf(cel.get("situacao"));
                    String icone = s.equals("ok") ? "✓" : s.equals("rodando") ? "⏳" : s.equals("erro") ? "✗"
                            : s.equals("parada") ? "■" : "·";
                    c.addView(texto("  " + icone + "  " + num(cel.get("numero")) + ") " + cel.get("nome"), 13,
                            s.equals("erro") ? R.color.perigo : R.color.texto_laika, s.equals("rodando")));
                }
                String url = v.autorizar();
                if (url != null && ativa) montarAutorizacao(c, e, url);
                if (!v.texto.isEmpty()) {
                    String[] ls = v.texto.split("\n");
                    StringBuilder ult = new StringBuilder();
                    for (int i = Math.max(0, ls.length - 12); i < ls.length; i++) ult.append(ls[i]).append('\n');
                    TextView log = texto(ult.toString().trim(), 11, R.color.texto_laika, false);
                    log.setTypeface(Typeface.MONOSPACE);
                    log.setBackgroundResource(R.drawable.campo);
                    log.setPadding(dp(10), dp(8), dp(10), dp(8));
                    LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                    lp.topMargin = dp(8);
                    c.addView(log, lp);
                }
            } else if (ativa) {
                c.addView(texto(e.status != null && e.status.equals("in_progress")
                        ? "Preparando o GitHub Actions…" : "Esperando a vez (uma máquina do Colab por vez)…", 13, R.color.aviso, false));
            }
            LinearLayout l = linha(c);
            if (ativa) {
                TextView cancelar = botao(l, "Cancelar", false, x -> cancelar(e));
                cancelar.setTextColor(getColor(R.color.perigo));
            } else {
                botao(l, "Ver registro", false, x -> verRegistro(e));
            }
            if (e.url != null) botao(l, "Abrir no GitHub", false, x -> abrirLink(e.url));
        }
    }

    private static String num(Object o) {
        return o instanceof Number ? String.valueOf(((Number) o).intValue()) : String.valueOf(o);
    }

    private void montarAutorizacao(LinearLayout c, GitHub.Execucao e, String url) {
        LinearLayout a = new LinearLayout(this);
        a.setOrientation(LinearLayout.VERTICAL);
        a.setBackgroundResource(R.drawable.cartao_atual);
        a.setPadding(dp(12), dp(10), dp(12), dp(10));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(8);
        c.addView(a, lp);
        a.addView(texto("O Colab precisa da sua autorização para usar o Google Drive", 14, R.color.topo_texto, true));
        a.addView(texto("Toque em Autorizar, entre com a sua conta Google, permita o acesso e volte aqui para tocar "
                + "em Já autorizei. A execução espera alguns minutos.", 13, R.color.texto_laika, false));
        LinearLayout l = linha(a);
        botao(l, "Autorizar", true, v -> abrirLink(url));
        botao(l, "Já autorizei", false, v -> rede.execute(() -> {
            String msg;
            try {
                Colab.github(this).avisarDriveAutorizado(Colab.ramo(this), e.id);
                msg = "Aviso enviado. O Colab continua em alguns segundos.";
            } catch (IOException erro) {
                msg = "Não consegui avisar: " + erro.getMessage();
            }
            String m = msg;
            ui.post(() -> Toast.makeText(this, m, Toast.LENGTH_LONG).show());
        }));
    }

    private void cancelar(GitHub.Execucao e) {
        new AlertDialog.Builder(this).setTitle("Cancelar a execução?")
                .setMessage("A máquina do Colab é desligada. O que já foi salvo no Drive (como o melhor checkpoint) continua lá.")
                .setPositiveButton("Cancelar execução", (d, w) -> rede.execute(() -> {
                    String msg;
                    try {
                        Colab.github(this).cancelar(e.id);
                        msg = "Cancelando… (a máquina desliga em alguns segundos)";
                    } catch (IOException erro) {
                        msg = "Não consegui cancelar: " + erro.getMessage();
                    }
                    String m = msg;
                    ui.post(() -> {
                        Toast.makeText(this, m, Toast.LENGTH_LONG).show();
                        ui.postDelayed(() -> atualizar(false), 3000);
                    });
                }))
                .setNegativeButton("Voltar", null).show();
    }

    private void verRegistro(GitHub.Execucao e) {
        Toast.makeText(this, "Buscando o registro…", Toast.LENGTH_SHORT).show();
        rede.execute(() -> {
            String r;
            try {
                r = Colab.github(this).registro(e.id, 150);
            } catch (IOException erro) {
                r = "Não consegui buscar o registro: " + erro.getMessage();
            }
            String reg = r.isEmpty() ? "(vazio)" : r;
            ui.post(() -> {
                TextView t = texto(reg, 11, R.color.texto_laika, false);
                t.setTypeface(Typeface.MONOSPACE);
                t.setTextIsSelectable(true);
                t.setPadding(dp(16), dp(8), dp(16), dp(8));
                ScrollView s = new ScrollView(this);
                s.addView(t);
                FrameLayout f = new FrameLayout(this);
                f.addView(s);
                AlertDialog d = new AlertDialog.Builder(this).setTitle(tituloCurto(e)).setView(f)
                        .setPositiveButton("OK", null).create();
                d.show();
                s.post(() -> s.fullScroll(View.FOCUS_DOWN));
            });
        });
    }

    // --- modelos prontos ---

    private void montarModelos() {
        caixaModelos.removeAllViews();
        if (!Colab.configurado(this)) return;
        secao(caixaModelos, "MODELOS PRONTOS");
        List<GitHub.Artefato> validos = new ArrayList<>();
        for (GitHub.Artefato a : artefatos) if (!a.expirado) validos.add(a);
        if (validos.isEmpty()) {
            TextView t = texto("Quando a célula 6 (exportar) rodar pelo app, o zip com o modelo novo aparece aqui "
                    + "por 14 dias. Ele também fica no Drive (LLM_Laika/laika_pacote.zip).", 13, R.color.aviso, false);
            t.setPadding(dp(4), 0, dp(4), 0);
            caixaModelos.addView(t);
            return;
        }
        SimpleDateFormat f = new SimpleDateFormat("dd/MM HH:mm", new Locale("pt", "BR"));
        for (GitHub.Artefato a : validos) {
            LinearLayout c = cartao(caixaModelos);
            c.addView(texto("Modelo de " + f.format(new Date(a.criado)), 15, R.color.topo_texto, true));
            c.addView(texto(String.format(Locale.getDefault(), "%.0f MB · %s", a.tamanho / 1048576.0, Colab.ha(a.criado)),
                    12, R.color.topo_sub, false));
            LinearLayout l = linha(c);
            TextView b = botao(l, "Baixar e usar", true, v -> baixar(a));
            ligado(b, !motor.ocupado());
        }
    }

    private void baixar(GitHub.Artefato a) {
        new AlertDialog.Builder(this).setTitle("Usar este modelo?")
                .setMessage(String.format(Locale.getDefault(), "O app baixa o zip (%.0f MB), confere os arquivos e cria "
                        + "uma versão nova. A versão em uso fica guardada nos backups.", a.tamanho / 1048576.0))
                .setPositiveButton("Baixar e usar", (d, w) -> motor.baixarDoColab(Colab.github(this), a))
                .setNegativeButton("Cancelar", null).show();
    }

    // --- conta ---

    /** Atalhos da conexão (sem textos de ajuda): abrir o caderno no Colab e trocar o token. */
    private void montarConta() {
        caixaConta.removeAllViews();
        if (!Colab.configurado(this)) return;
        secao(caixaConta, "CONEXÃO");
        LinearLayout c = cartao(caixaConta);
        c.addView(texto("Repositório: " + Colab.repo(this), 13, R.color.texto_laika, false));
        LinearLayout l = linha(c);
        botao(l, "Abrir no Colab", false, v -> abrirLink(urlColab()));
        botao(l, "Trocar o token", false, v -> trocarToken());
    }
}
