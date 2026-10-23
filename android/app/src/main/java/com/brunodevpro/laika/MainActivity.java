package com.brunodevpro.laika;

import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.SpannableStringBuilder;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.text.style.RelativeSizeSpan;
import android.text.style.StyleSpan;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/** Tela de conversa com a Laika. */
public class MainActivity extends ComponentActivity implements Motor.Ouvinte {
    /** Sugestões da tela inicial; as que terminam em "…" só preenchem o campo. */
    private static final String[] SUGESTOES = {
            "Quem foi a Laika?", "O que é um vulcão?", "Meu nome é …", "Complete a frase: Quem espera",
            "O que você lembra de mim?",
    };

    private Motor motor;
    private LinearLayout mensagens;
    private ScrollView rolagem;
    private View vazio, tarefa;
    private TextView estado, versaoNome, tarefaTexto;
    private ProgressBar tarefaBarra;
    private EditText entrada;
    private ImageButton enviar;
    private final Map<Motor.Mensagem, TextView> bolhas = new HashMap<>();
    private boolean estavaGerando;

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_main);
        motor = Motor.get(this);

        mensagens = findViewById(R.id.mensagens);
        rolagem = findViewById(R.id.rolagem);
        vazio = findViewById(R.id.vazio);
        tarefa = findViewById(R.id.tarefa);
        tarefaTexto = findViewById(R.id.tarefa_texto);
        tarefaBarra = findViewById(R.id.tarefa_barra);
        entrada = findViewById(R.id.entrada);
        enviar = findViewById(R.id.enviar);
        estado = findViewById(R.id.estado);
        versaoNome = findViewById(R.id.versao_nome);

        // Barras do sistema e teclado: o topo desce abaixo da barra de status, a barra de texto sobe com o teclado.
        View topo = findViewById(R.id.topo), barra = findViewById(R.id.barra);
        int topoPad = topo.getPaddingTop(), barraPad = barra.getPaddingBottom();
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.raiz), (v, insets) -> {
            Insets sys = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            Insets ime = insets.getInsets(WindowInsetsCompat.Type.ime());
            v.setPadding(sys.left, 0, sys.right, 0);
            topo.setPadding(topo.getPaddingLeft(), topoPad + sys.top, topo.getPaddingRight(), topo.getPaddingBottom());
            barra.setPadding(barra.getPaddingLeft(), barra.getPaddingTop(), barra.getPaddingRight(),
                    barraPad + Math.max(sys.bottom, ime.bottom));
            rolarParaFim();
            return WindowInsetsCompat.CONSUMED;
        });

        // O campo quebra a linha sozinho, mas o Enter envia.
        entrada.setHorizontallyScrolling(false);
        entrada.setMaxLines(5);
        entrada.setOnEditorActionListener((v, acao, ev) -> {
            boolean enter = ev != null && ev.getKeyCode() == KeyEvent.KEYCODE_ENTER && ev.getAction() == KeyEvent.ACTION_DOWN;
            if (acao == EditorInfo.IME_ACTION_SEND || enter) {
                enviarTexto();
                return true;
            }
            return false;
        });
        enviar.setOnClickListener(v -> {
            if (motor.gerando) motor.pararGeracao();
            else enviarTexto();
        });
        findViewById(R.id.menu).setOnClickListener(this::abrirMenu);
        findViewById(R.id.versao).setOnClickListener(v -> startActivity(new Intent(this, VersoesActivity.class)));

        LinearLayout sugestoes = findViewById(R.id.sugestoes);
        for (String s : SUGESTOES) {
            TextView chip = new TextView(this);
            chip.setText(s);
            chip.setTextSize(15);
            chip.setTextColor(getColor(R.color.chip_texto));
            chip.setBackgroundResource(R.drawable.chip);
            chip.setPadding(dp(16), dp(9), dp(16), dp(9));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            lp.topMargin = dp(8);
            lp.gravity = Gravity.CENTER_HORIZONTAL;
            chip.setOnClickListener(v -> {
                if (s.endsWith("…")) {
                    entrada.setText(s.substring(0, s.length() - 1));
                    entrada.setSelection(entrada.length());
                    focarCampo();
                } else {
                    enviar(s);
                }
            });
            sugestoes.addView(chip, lp);
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        motor.adicionarOuvinte(this);
        conversaTrocada();
        estadoMudou();
    }

    @Override
    protected void onStop() {
        motor.removerOuvinte(this);
        super.onStop();
    }

    @Override
    public void onWindowFocusChanged(boolean temFoco) {
        super.onWindowFocusChanged(temFoco);
        // Ao abrir o app e ao voltar de um diálogo/outra tela, o campo já fica pronto para digitar.
        if (temFoco) focarCampo();
    }

    private void focarCampo() {
        entrada.requestFocus();
        entrada.post(() -> WindowCompat.getInsetsController(getWindow(), entrada).show(WindowInsetsCompat.Type.ime()));
    }

    // ---------- enviar ----------

    private void enviarTexto() {
        String texto = entrada.getText().toString().trim();
        if (texto.isEmpty()) return;
        if (motor.gerando) {
            Toast.makeText(this, "Espere a resposta terminar (ou toque em ■ para parar).", Toast.LENGTH_SHORT).show();
            return;
        }
        enviar(texto);
    }

    private void enviar(String texto) {
        if (motor.ocupado() || !motor.pronto) {
            Toast.makeText(this, motor.tarefa != null ? motor.tarefa : "A Laika ainda não está pronta.",
                    Toast.LENGTH_SHORT).show();
            return;
        }
        entrada.setText("");
        focarCampo();
        // Os mesmos comandos do chat.py.
        switch (texto) {
            case "/fontes":
                motor.mostrarFontes = !motor.mostrarFontes;
                motor.salvarOpcoes();
                motor.aviso("Fontes " + (motor.mostrarFontes ? "visíveis" : "escondidas") + ".");
                return;
            case "/rag":
                motor.usarRag = !motor.usarRag;
                motor.salvarOpcoes();
                motor.aviso("Busca nos textos " + (motor.usarRag ? "ligada" : "desligada") + ".");
                return;
            case "/memoria":
                motor.aviso(motor.usarMemoria ? motor.resumoMemoria() : "A memória está desligada.");
                return;
            default:
                motor.enviar(texto);
        }
    }

    // ---------- bolhas ----------

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private CharSequence conteudo(Motor.Mensagem m) {
        if (m.fonte == null && m.detalhe == null) return m.texto;
        SpannableStringBuilder sb = new SpannableStringBuilder(m.texto);
        if (m.fonte != null) {
            int ini = sb.length();
            sb.append("  *").append(m.fonte);
            sb.setSpan(new StyleSpan(Typeface.ITALIC), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new ForegroundColorSpan(getColor(R.color.fonte)), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new RelativeSizeSpan(0.85f), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        if (m.detalhe != null && !m.usuario) {
            int ini = sb.length();
            sb.append("\n").append(m.detalhe);
            sb.setSpan(new ForegroundColorSpan(getColor(R.color.detalhe)), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new RelativeSizeSpan(0.72f), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        return sb;
    }

    @Override
    public void mensagemNova(Motor.Mensagem m) {
        TextView t = new TextView(this);
        t.setTextIsSelectable(true);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(4);
        lp.bottomMargin = dp(4);
        if (m.aviso) {
            lp.gravity = Gravity.CENTER_HORIZONTAL;
            t.setTextSize(13);
            t.setTextColor(getColor(R.color.aviso));
            t.setGravity(Gravity.CENTER);
            t.setPadding(dp(16), dp(2), dp(16), dp(2));
        } else {
            lp.gravity = m.usuario ? Gravity.END : Gravity.START;
            if (m.usuario) lp.leftMargin = dp(48);
            else lp.rightMargin = dp(48);
            t.setTextSize(16);
            t.setLineSpacing(0, 1.1f);
            t.setTextColor(getColor(m.usuario ? R.color.texto_usuario : R.color.texto_laika));
            t.setBackgroundResource(m.usuario ? R.drawable.bolha_usuario : R.drawable.bolha_laika);
            t.setPadding(dp(14), dp(9), dp(14), dp(9));
        }
        t.setText(conteudo(m));
        mensagens.addView(t, lp);
        bolhas.put(m, t);
        atualizarVazio();
        rolarParaFim();
    }

    @Override
    public void mensagemMudou(Motor.Mensagem m) {
        TextView t = bolhas.get(m);
        if (t == null) return;
        t.setText(conteudo(m));
        rolarParaFim();
    }

    @Override
    public void conversaTrocada() {
        mensagens.removeAllViews();
        bolhas.clear();
        for (Motor.Mensagem m : motor.conversa) mensagemNova(m);
        atualizarVazio();
    }

    /** Sem mensagens do usuário: mostra as boas-vindas com sugestões. */
    private void atualizarVazio() {
        boolean temConversa = false;
        for (Motor.Mensagem m : motor.conversa) {
            if (!m.aviso) {
                temConversa = true;
                break;
            }
        }
        vazio.setVisibility(temConversa ? View.GONE : View.VISIBLE);
        rolagem.setVisibility(temConversa ? View.VISIBLE : View.INVISIBLE);
    }

    private void rolarParaFim() {
        // scrollTo em vez de fullScroll: fullScroll passaria o foco para a última bolha e o campo
        // de texto deixaria de estar ativo.
        rolagem.post(() -> rolagem.scrollTo(0, Math.max(0, mensagens.getBottom() - rolagem.getHeight()
                + rolagem.getPaddingBottom())));
    }

    @Override
    public void estadoMudou() {
        String s;
        if (motor.erro != null) s = motor.erro;
        else if (!motor.pronto) s = "carregando…";
        else if (motor.modoCompletar) s = "modo completar texto (modelo só pré-treinado)";
        else s = "RAG: " + (motor.usarRag ? motor.descricaoIndice : "desligado")
                    + " · memória " + (motor.usarMemoria ? "ligada" : "desligada");
        estado.setText(s);
        versaoNome.setText(motor.nomeVersao.isEmpty() ? getString(R.string.versoes_curto) : motor.nomeVersao);

        String t = motor.tarefa;
        tarefa.setVisibility(t != null ? View.VISIBLE : View.GONE);
        if (t != null) {
            int p = motor.progresso;
            tarefaTexto.setText(p >= 0 ? String.format(Locale.getDefault(), "%s %d%%", t, p) : t);
            tarefaBarra.setIndeterminate(p < 0);
            if (p >= 0) tarefaBarra.setProgress(p);
        }
        enviar.setImageResource(motor.gerando ? R.drawable.ic_parar : R.drawable.ic_enviar);
        enviar.setContentDescription(getString(motor.gerando ? R.string.parar : R.string.enviar));
        entrada.setHint(motor.modoCompletar ? "Comece um texto…" : getString(R.string.dica));
        if (estavaGerando && !motor.gerando) focarCampo();
        estavaGerando = motor.gerando;
    }

    @Override
    public void aviso(String titulo, String texto) {
        if (titulo == null) {
            Toast.makeText(this, texto, Toast.LENGTH_LONG).show();
        } else {
            new AlertDialog.Builder(this).setTitle(titulo).setMessage(texto).setPositiveButton("OK", null).show();
        }
    }

    // ---------- menu ----------

    private void abrirMenu(View ancora) {
        PopupMenu pm = new PopupMenu(this, ancora);
        Menu m = pm.getMenu();
        m.add(0, 1, 0, "Mostrar fontes (*Título)").setCheckable(true).setChecked(motor.mostrarFontes);
        m.add(0, 2, 0, "Buscar nos textos (RAG)").setCheckable(true).setChecked(motor.usarRag);
        m.add(0, 3, 0, "Usar memória").setCheckable(true).setChecked(motor.usarMemoria);
        if (motor.temBase) m.add(0, 4, 0, "Modo completar texto").setCheckable(true).setChecked(motor.modoCompletar);
        m.add(0, 5, 0, String.format(Locale.getDefault(), "Criatividade (temperatura %.1f)…", motor.temperatura));
        m.add(0, 6, 0, "O que a Laika lembra de mim");
        m.add(0, 7, 0, "Versões e backups…");
        m.add(0, 8, 0, "Limpar conversa");
        m.add(0, 9, 0, "Sobre");
        pm.setOnMenuItemClickListener(this::itemDoMenu);
        pm.show();
    }

    private boolean itemDoMenu(MenuItem item) {
        switch (item.getItemId()) {
            case 1: motor.mostrarFontes = !motor.mostrarFontes; motor.salvarOpcoes(); break;
            case 2: motor.usarRag = !motor.usarRag; motor.salvarOpcoes(); break;
            case 3: motor.usarMemoria = !motor.usarMemoria; motor.salvarOpcoes(); break;
            case 4:
                motor.modoCompletar = !motor.modoCompletar;
                motor.aviso(motor.modoCompletar
                        ? "Modo completar texto: escreva o começo de um texto e a Laika continua (sem RAG nem memória)."
                        : "Modo conversa.");
                estadoMudou();
                break;
            case 5: escolherTemperatura(); break;
            case 6: mostrarMemoria(); break;
            case 7: startActivity(new Intent(this, VersoesActivity.class)); break;
            case 8:
                new AlertDialog.Builder(this).setMessage("Apagar a conversa da tela? (A memória continua.)")
                        .setPositiveButton("Apagar", (d, w) -> motor.limparConversa())
                        .setNegativeButton("Cancelar", null).show();
                break;
            case 9: sobre(); break;
            default: return false;
        }
        return true;
    }

    private void escolherTemperatura() {
        String[] nomes = {"0,3 — mais previsível", "0,5", "0,7 — padrão", "0,9", "1,1 — mais criativa"};
        double[] valores = {0.3, 0.5, 0.7, 0.9, 1.1};
        int atual = 2;
        for (int i = 0; i < valores.length; i++) if (Math.abs(valores[i] - motor.temperatura) < 0.01) atual = i;
        new AlertDialog.Builder(this).setTitle("Criatividade")
                .setSingleChoiceItems(nomes, atual, (d, i) -> {
                    motor.temperatura = valores[i];
                    motor.salvarOpcoes();
                    d.dismiss();
                }).show();
    }

    private void mostrarMemoria() {
        new AlertDialog.Builder(this).setTitle("Memória")
                .setMessage(motor.resumoMemoria() + "\n\nDica: diga \"meu nome é…\", \"eu moro em…\", "
                        + "\"eu gosto de…\" ou \"lembre que…\".")
                .setPositiveButton("OK", null)
                .setNegativeButton("Apagar tudo", (d, w) -> motor.apagarMemoria()).show();
    }

    private void sobre() {
        new AlertDialog.Builder(this).setTitle("Sobre a Laika")
                .setMessage("A Laika é um modelo de linguagem pequeno, treinado do zero em português. "
                        + "Ela roda inteira no celular, sem internet.\n\n"
                        + "A busca nos textos (RAG) põe um trecho da Wikipédia ou dos livros na pergunta e mostra "
                        + "a fonte no fim da resposta (*Título). A memória guarda o que você conta sobre você "
                        + "e fica só neste aparelho.\n\n"
                        + "No botão de versões (no topo) você importa um treino novo, faz backups e volta para "
                        + "qualquer versão.\n\n"
                        + "Comandos: /fontes, /rag, /memoria.\n\n"
                        + "O nome é uma homenagem à cadela Laika (Sputnik 2, 1957).")
                .setPositiveButton("OK", null).show();
    }
}
