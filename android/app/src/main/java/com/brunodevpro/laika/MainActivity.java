package com.brunodevpro.laika;

import android.app.AlertDialog;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.text.SpannableStringBuilder;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.text.style.RelativeSizeSpan;
import android.text.style.StyleSpan;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.activity.ComponentActivity;
import androidx.activity.EdgeToEdge;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.HashMap;
import java.util.Map;

/** Tela de conversa com a Laika. */
public class MainActivity extends ComponentActivity implements Motor.Ouvinte {
    private static final int PEDIR_INDICE = 1;

    private Motor motor;
    private LinearLayout mensagens;
    private ScrollView rolagem;
    private EditText entrada;
    private ImageButton enviar;
    private TextView estado;
    private final Map<Motor.Mensagem, TextView> bolhas = new HashMap<>();

    @Override
    protected void onCreate(Bundle salvo) {
        EdgeToEdge.enable(this);
        super.onCreate(salvo);
        setContentView(R.layout.activity_main);
        motor = Motor.get(this);

        mensagens = findViewById(R.id.mensagens);
        rolagem = findViewById(R.id.rolagem);
        entrada = findViewById(R.id.entrada);
        enviar = findViewById(R.id.enviar);
        estado = findViewById(R.id.estado);

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

        enviar.setOnClickListener(v -> enviarOuParar());
        findViewById(R.id.menu).setOnClickListener(this::abrirMenu);
    }

    @Override
    protected void onStart() {
        super.onStart();
        motor.setOuvinte(this);
        mensagens.removeAllViews();
        bolhas.clear();
        for (Motor.Mensagem m : motor.conversa) mensagemNova(m);
        estadoMudou();
    }

    @Override
    protected void onStop() {
        motor.setOuvinte(null);
        super.onStop();
    }

    // ---------- enviar ----------

    private void enviarOuParar() {
        if (motor.gerando) {
            motor.pararGeracao();
            return;
        }
        String texto = entrada.getText().toString().trim();
        if (texto.isEmpty() || !motor.pronto) return;
        entrada.setText("");
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
        if (m.fonte == null) return m.texto;
        SpannableStringBuilder sb = new SpannableStringBuilder(m.texto);
        int ini = sb.length();
        sb.append("  *").append(m.fonte);
        sb.setSpan(new StyleSpan(Typeface.ITALIC), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        sb.setSpan(new ForegroundColorSpan(getColor(R.color.fonte)), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        sb.setSpan(new RelativeSizeSpan(0.85f), ini, sb.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
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
        rolarParaFim();
    }

    @Override
    public void mensagemMudou(Motor.Mensagem m) {
        TextView t = bolhas.get(m);
        if (t == null) return;
        t.setText(conteudo(m));
        rolarParaFim();
    }

    private void rolarParaFim() {
        rolagem.post(() -> rolagem.fullScroll(View.FOCUS_DOWN));
    }

    @Override
    public void estadoMudou() {
        String s;
        if (motor.erro != null) s = "erro ao carregar";
        else if (!motor.pronto) s = "carregando…";
        else if (motor.modoCompletar) s = "modo completar texto (modelo só pré-treinado)";
        else s = "RAG: " + (motor.usarRag ? motor.descricaoIndice : "desligado")
                    + " · memória " + (motor.usarMemoria ? "ligada" : "desligada");
        estado.setText(s);
        enviar.setImageResource(motor.gerando ? R.drawable.ic_parar : R.drawable.ic_enviar);
        enviar.setContentDescription(getString(motor.gerando ? R.string.parar : R.string.enviar));
        entrada.setHint(motor.modoCompletar ? "Comece um texto…" : getString(R.string.dica));
    }

    // ---------- menu ----------

    private void abrirMenu(View ancora) {
        PopupMenu pm = new PopupMenu(this, ancora);
        Menu m = pm.getMenu();
        m.add(0, 1, 0, "Mostrar fontes (*Título)").setCheckable(true).setChecked(motor.mostrarFontes);
        m.add(0, 2, 0, "Buscar nos textos (RAG)").setCheckable(true).setChecked(motor.usarRag);
        m.add(0, 3, 0, "Usar memória").setCheckable(true).setChecked(motor.usarMemoria);
        if (motor.temModoCompletar()) {
            m.add(0, 4, 0, "Modo completar texto").setCheckable(true).setChecked(motor.modoCompletar);
        }
        m.add(0, 5, 0, String.format("Criatividade (temperatura %.1f)…", motor.temperatura));
        m.add(0, 6, 0, "O que a Laika lembra de mim");
        m.add(0, 7, 0, motor.indiceCompleto ? "Trocar o índice completo…" : "Importar índice completo (laika_rag.db)…");
        if (motor.indiceCompleto) m.add(0, 8, 0, "Voltar ao índice pequeno");
        m.add(0, 9, 0, "Limpar conversa");
        m.add(0, 10, 0, "Sobre");
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
            case 7: pedirIndice(); break;
            case 8:
                new AlertDialog.Builder(this)
                        .setMessage("Apagar o índice completo do celular e voltar ao índice pequeno?")
                        .setPositiveButton("Apagar", (d, w) -> motor.voltarIndicePequeno())
                        .setNegativeButton("Cancelar", null).show();
                break;
            case 9:
                if (motor.gerando) motor.pararGeracao();
                motor.limparConversa();
                mensagens.removeAllViews();
                bolhas.clear();
                break;
            case 10: sobre(); break;
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

    private void pedirIndice() {
        new AlertDialog.Builder(this).setTitle("Índice completo do RAG")
                .setMessage("Escolha o arquivo laika_rag.db (cerca de 640 MB). Baixe-o antes do Google Drive "
                        + "(Meu Drive/LLM_Laika/rag) para o celular. O app faz uma cópia, então é preciso "
                        + "ter o dobro do espaço livre durante a importação; depois você pode apagar o arquivo baixado.")
                .setPositiveButton("Escolher arquivo", (d, w) -> {
                    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("*/*");
                    startActivityForResult(i, PEDIR_INDICE);
                })
                .setNegativeButton("Cancelar", null).show();
    }

    @Override
    protected void onActivityResult(int pedido, int resultado, Intent dados) {
        super.onActivityResult(pedido, resultado, dados);
        if (pedido != PEDIR_INDICE || resultado != RESULT_OK || dados == null || dados.getData() == null) return;
        Uri uri = dados.getData();
        long tamanho = -1;
        try (Cursor c = getContentResolver().query(uri, new String[]{OpenableColumns.SIZE}, null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) tamanho = c.getLong(0);
        } catch (RuntimeException ignorado) {
            // tamanho desconhecido: mostra o progresso em MB
        }
        motor.importarIndice(uri, tamanho);
    }

    private void sobre() {
        new AlertDialog.Builder(this).setTitle("Sobre a Laika")
                .setMessage("A Laika é um modelo de linguagem pequeno (~7 milhões de parâmetros), treinado do zero "
                        + "em português. Ela roda inteira no celular, sem internet.\n\n"
                        + "A busca nos textos (RAG) põe um trecho da Wikipédia ou dos livros na pergunta e mostra "
                        + "a fonte no fim da resposta (*Título). A memória guarda o que você conta sobre você "
                        + "e fica só neste aparelho.\n\n"
                        + "Comandos: /fontes, /rag, /memoria.\n\n"
                        + "O nome é uma homenagem à cadela Laika (Sputnik 2, 1957).")
                .setPositiveButton("OK", null).show();
    }
}
