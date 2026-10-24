package com.brunodevpro.laika;

import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.SpannableStringBuilder;
import android.text.Spanned;
import android.text.TextWatcher;
import android.text.style.ForegroundColorSpan;
import android.text.style.RelativeSizeSpan;
import android.text.style.StyleSpan;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;

import com.brunodevpro.laika.core.Armazem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Tela de conversa com a Laika. */
public class MainActivity extends ComponentActivity implements Motor.Ouvinte {
    /** Sugestões da tela inicial; as que terminam em "…" só preenchem o campo. */
    private static final String[] SUGESTOES = {
            "Quem foi a Laika?", "O que é um vulcão?", "Qual é a capital da França?", "Meu nome é …",
            "Complete a frase: Quem espera",
    };
    /** Pontinhos de "digitando" enquanto a resposta não começa. */
    private static final String[] PONTOS = {"●  ○  ○", "○  ●  ○", "○  ○  ●"};

    private Motor motor;
    private PainelTarefa painel;
    private MenuOpcoes menu;
    private LinearLayout mensagens;
    private ScrollView rolagem;
    private View vazio, descer;
    private TextView estado, versaoNome;
    private EditText entrada;
    private ImageButton enviar;
    private final Map<Motor.Mensagem, TextView> bolhas = new HashMap<>();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private boolean ofereceuBackup;
    /** A conversa está no fim (a tela acompanha a resposta); false se o usuário rolou para cima. */
    private boolean noFim = true;
    private int quadro;

    private final Runnable animarPontos = new Runnable() {
        @Override
        public void run() {
            quadro++;
            boolean algum = false;
            for (Map.Entry<Motor.Mensagem, TextView> e : bolhas.entrySet()) {
                if (Motor.DIGITANDO.equals(e.getKey().texto)) {
                    e.getValue().setText(PONTOS[quadro % PONTOS.length]);
                    algum = true;
                }
            }
            if (algum || motor.gerando) ui.postDelayed(this, 350);
        }
    };

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_main);
        motor = Motor.get(this);
        painel = new PainelTarefa(this, motor);
        menu = new MenuOpcoes(this, motor, new MenuOpcoes.Acoes() {
            @Override
            public void memoria() {
                mostrarMemoria();
            }

            @Override
            public void versoes() {
                startActivity(new Intent(MainActivity.this, VersoesActivity.class));
            }

            @Override
            public void treinar() {
                startActivity(new Intent(MainActivity.this, ColabActivity.class));
            }

            @Override
            public void limpar() {
                limparConversa();
            }

            @Override
            public void mudou() {
                estadoMudou();
            }
        });

        mensagens = findViewById(R.id.mensagens);
        rolagem = findViewById(R.id.rolagem);
        vazio = findViewById(R.id.vazio);
        descer = findViewById(R.id.descer);
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
            rolarParaFim(false);
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
        entrada.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int a, int b, int c) {
            }

            @Override
            public void onTextChanged(CharSequence s, int a, int b, int c) {
            }

            @Override
            public void afterTextChanged(Editable s) {
                atualizarBotaoEnviar();
            }
        });
        enviar.setOnClickListener(v -> {
            if (motor.gerando) motor.pararGeracao();
            else enviarTexto();
        });
        findViewById(R.id.menu).setOnClickListener(v -> menu.mostrar(v));
        findViewById(R.id.versao).setOnClickListener(v -> new SeletorModelos(this, motor).mostrar());

        // Rolar para cima solta a tela do fim (a resposta não puxa mais para baixo) e mostra o botão de descer.
        rolagem.setOnScrollChangeListener((v, x, y, xAntes, yAntes) -> {
            int falta = mensagens.getBottom() - (y + rolagem.getHeight());
            noFim = falta < dp(48);
            descer.setVisibility(noFim ? View.GONE : View.VISIBLE);
        });
        descer.setOnClickListener(v -> rolarParaFim(true));
        // A resposta crescendo (texto chegando) acompanha o fim depois do layout, sem ficar uma linha atrás.
        mensagens.addOnLayoutChangeListener((v, l, t, r, b, lAntes, tAntes, rAntes, bAntes) -> {
            if (b != bAntes && noFim) rolagem.scrollTo(0, Math.max(0, b - rolagem.getHeight() + rolagem.getPaddingBottom()));
        });

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
        atualizarBotaoEnviar();
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
        ui.removeCallbacks(animarPontos);
        menu.fechar();
        super.onStop();
    }

    /** Abre o teclado: só quando o usuário pede para escrever (nunca ao entrar na tela). */
    private void focarCampo() {
        entrada.requestFocus();
        entrada.post(() -> WindowCompat.getInsetsController(getWindow(), entrada).show(WindowInsetsCompat.Type.ime()));
    }

    // ---------- enviar ----------

    private void atualizarBotaoEnviar() {
        boolean ativo = motor.gerando || entrada.getText().toString().trim().length() > 0;
        enviar.setAlpha(ativo ? 1f : 0.45f);
    }

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
        rolarParaFim(true);
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
        if (Motor.DIGITANDO.equals(m.texto)) return PONTOS[quadro % PONTOS.length];
        if (m.fonte == null && m.detalhe == null) return m.texto;
        SpannableStringBuilder sb = new SpannableStringBuilder(m.texto);
        if (m.fonte != null) {
            int ini = sb.length();
            sb.append("  *").append(m.fonte);
            sb.setSpan(new StyleSpan(Typeface.ITALIC), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new ForegroundColorSpan(getColor(R.color.fonte)), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new RelativeSizeSpan(0.85f), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        if (m.detalhe != null) {
            int ini = sb.length();
            sb.append("\n").append(m.detalhe);
            // Na bolha do usuário (azul), o detalhe vai em branco translúcido.
            int cor = m.usuario ? (getColor(R.color.texto_usuario) & 0x00FFFFFF) | 0xB0000000 : getColor(R.color.detalhe);
            sb.setSpan(new ForegroundColorSpan(cor), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.setSpan(new RelativeSizeSpan(0.72f), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        return sb;
    }

    @Override
    public void mensagemNova(Motor.Mensagem m) {
        TextView t = new TextView(this);
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
            // Um toque abre as ações (copiar, gerar de novo...). Sem seleção de texto direta,
            // para a bolha não roubar o foco do campo de mensagem.
            t.setOnClickListener(v -> acoesDaBolha(m, v));
            t.setOnLongClickListener(v -> {
                acoesDaBolha(m, v);
                return true;
            });
        }
        t.setText(conteudo(m));
        mensagens.addView(t, lp);
        bolhas.put(m, t);
        atualizarVazio();
        // A mensagem do próprio usuário sempre leva a tela para o fim.
        rolarParaFim(m.usuario);
        if (Motor.DIGITANDO.equals(m.texto)) iniciarPontos();
    }

    @Override
    public void mensagemMudou(Motor.Mensagem m) {
        TextView t = bolhas.get(m);
        if (t == null) return;
        t.setText(conteudo(m));
        if (Motor.DIGITANDO.equals(m.texto)) iniciarPontos();
        rolarParaFim(false);
    }

    private void iniciarPontos() {
        ui.removeCallbacks(animarPontos);
        ui.postDelayed(animarPontos, 350);
    }

    @Override
    public void conversaTrocada() {
        mensagens.removeAllViews();
        bolhas.clear();
        for (Motor.Mensagem m : new ArrayList<>(motor.conversa)) mensagemNova(m);
        atualizarVazio();
        rolarParaFim(true);
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
        if (!temConversa) descer.setVisibility(View.GONE);
    }

    /** Vai para a última mensagem; sem forcar, só se a tela já estava no fim (o usuário pode estar lendo). */
    private void rolarParaFim(boolean forcar) {
        if (!forcar && !noFim) return;
        noFim = true;
        descer.setVisibility(View.GONE);
        // scrollTo em vez de fullScroll: fullScroll passaria o foco para a última bolha e o campo
        // de texto deixaria de estar ativo.
        rolagem.post(() -> rolagem.scrollTo(0, Math.max(0, mensagens.getBottom() - rolagem.getHeight()
                + rolagem.getPaddingBottom())));
    }

    private void acoesDaBolha(Motor.Mensagem m, View ancora) {
        if (m.texto == null || m.texto.equals(Motor.DIGITANDO)) return;
        String completo = m.texto + (m.fonte != null ? " *" + m.fonte : "");
        AcoesBolha acoes = new AcoesBolha(this).acao(R.drawable.ic_copiar, "Copiar", () -> {
            getSystemService(ClipboardManager.class).setPrimaryClip(ClipData.newPlainText("Laika", completo));
            Toast.makeText(this, "Copiado.", Toast.LENGTH_SHORT).show();
        });
        if (m.usuario) {
            acoes.acao(R.drawable.ic_editar, "Editar", () -> {
                entrada.setText(m.texto);
                entrada.setSelection(entrada.length());
                focarCampo();
            });
        } else {
            if (m.trecho != null) {
                acoes.acao(R.drawable.ic_trecho, "Trecho lido", () ->
                        new AlertDialog.Builder(this).setTitle(m.fonte != null ? "*" + m.fonte : "Trecho encontrado")
                                .setMessage(m.trecho + "\n\n(A busca do RAG achou este trecho e ele entrou na "
                                        + "pergunta como Contexto.)")
                                .setPositiveButton("OK", null).show());
            }
            if (!motor.gerando && motor.perguntaDe(m) != null) {
                acoes.acao(R.drawable.ic_gerar, "Gerar outra", () -> {
                    if (motor.ocupado() || !motor.pronto) {
                        Toast.makeText(this, "Espere a Laika ficar pronta.", Toast.LENGTH_SHORT).show();
                    } else {
                        motor.gerarDeNovo(m);
                    }
                });
            }
        }
        acoes.mostrar(ancora, m.usuario);
    }

    // ---------- estado ----------

    /** A linha embaixo do nome: o que está acontecendo ou o que está ligado, em poucas palavras. */
    private String linhaDeEstado() {
        if (motor.erro != null) return motor.erro;
        if (!motor.pronto) return "carregando…";
        if (motor.gerando) return motor.modoCompletar ? "escrevendo…" : "pensando…";
        if (motor.modoCompletar) return "modo completar texto";
        List<String> ligado = new ArrayList<>();
        if (motor.usarRag) {
            String d = motor.descricaoIndice;
            int p = d.indexOf(" (");
            ligado.add(p > 0 ? d.substring(0, p) : "busca");
        }
        if (motor.usarMemoria) ligado.add("memória");
        if (motor.usarHistorico) ligado.add("memória de IA");
        if (motor.respostasLongas) ligado.add("respostas longas");
        return ligado.isEmpty() ? "sem busca e sem memória" : String.join(" · ", ligado);
    }

    @Override
    public void estadoMudou() {
        estado.setText(linhaDeEstado());
        versaoNome.setText(motor.nomeVersao.isEmpty() ? getString(R.string.versoes_curto) : motor.nomeVersao);
        painel.atualizar();
        enviar.setImageResource(motor.gerando ? R.drawable.ic_parar : R.drawable.ic_enviar);
        enviar.setContentDescription(getString(motor.gerando ? R.string.parar : R.string.enviar));
        atualizarBotaoEnviar();
        entrada.setHint(motor.modoCompletar ? "Comece um texto…" : getString(R.string.dica));
        if (motor.gerando) iniciarPontos();
        if (motor.erro != null && !motor.ocupado()) oferecerBackup();
    }

    /** A versão em uso não abriu: oferece voltar para o backup mais recente. */
    private void oferecerBackup() {
        if (ofereceuBackup || motor.armazem == null) return;
        List<Armazem.Versao> bs = motor.armazem.backups();
        if (bs.isEmpty()) return;
        ofereceuBackup = true;
        Armazem.Versao b = bs.get(0);
        new AlertDialog.Builder(this).setTitle("A versão em uso não abriu")
                .setMessage(motor.erro + "\n\nVoltar para o backup mais recente, \"" + b.nome + "\"?")
                .setPositiveButton("Voltar para o backup", (d, w) -> motor.usarBackup(b.id, null))
                .setNegativeButton("Agora não", null).show();
    }

    @Override
    public void aviso(String titulo, String texto) {
        if (titulo == null) {
            Toast.makeText(this, texto, Toast.LENGTH_LONG).show();
        } else {
            new AlertDialog.Builder(this).setTitle(titulo).setMessage(texto).setPositiveButton("OK", null).show();
        }
    }

    // ---------- ações do menu ----------

    private void limparConversa() {
        new AlertDialog.Builder(this).setTitle("Limpar a conversa?")
                .setMessage("As mensagens somem da tela e a memória de IA começa do zero. "
                        + "O que a Laika guardou sobre você continua.")
                .setPositiveButton("Limpar", (d, w) -> motor.limparConversa())
                .setNegativeButton("Cancelar", null).show();
    }

    private void mostrarMemoria() {
        new AlertDialog.Builder(this).setTitle("O que a Laika lembra de você")
                .setMessage(motor.resumoMemoria() + "\n\nPara ensinar, diga \"meu nome é…\", \"eu moro em…\", "
                        + "\"eu gosto de…\" ou \"lembre que…\".")
                .setPositiveButton("OK", null)
                .setNegativeButton("Apagar tudo", (d, w) -> motor.apagarMemoria()).show();
    }
}
