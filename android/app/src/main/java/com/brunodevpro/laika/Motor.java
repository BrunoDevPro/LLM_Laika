package com.brunodevpro.laika;

import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;

import androidx.core.content.pm.PackageInfoCompat;
import androidx.sqlite.SQLiteConnection;
import androidx.sqlite.driver.bundled.BundledSQLite;
import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import com.brunodevpro.laika.core.Armazem;
import com.brunodevpro.laika.core.Chats;
import com.brunodevpro.laika.core.Importador;
import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.Laika;
import com.brunodevpro.laika.core.Memoria;
import com.brunodevpro.laika.core.Modelo;
import com.brunodevpro.laika.core.Pacote;
import com.brunodevpro.laika.core.Texto;
import com.brunodevpro.laika.core.Tokenizador;
import com.brunodevpro.laika.core.colab.GitHub;
import com.brunodevpro.laika.core.dados.ConstrutorIndice;
import com.brunodevpro.laika.core.dados.Corpus;
import com.brunodevpro.laika.core.dados.Parado;
import com.brunodevpro.laika.core.dados.Registro;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Tudo o que não é tela: a versão em uso (modelo, tokenizer, índice RAG), os chats (cada um com a sua conversa e
 * a sua memória), os backups, as importações (inclusive o zip do Colab) e a geração das respostas.
 * Vive enquanto o app estiver aberto. O trabalho pesado roda numa única thread de fundo, em ordem.
 */
final class Motor {
    /** Uma mensagem da conversa. */
    static final class Mensagem {
        final boolean usuario, aviso;
        /** Mensagem do modo completar texto (não entra na memória de IA). */
        boolean completar;
        /** trecho: o texto que o RAG achou e entrou no prompt (para "Ver o trecho usado"). */
        volatile String texto, fonte, detalhe, trecho;
        /** O modelo que gerou esta resposta (o arquivo do chat e o nome na hora), ou null (resposta da memória). */
        volatile String modeloRef, modeloNome;
        /** A linha "*modelo X usado" onde o modelo muda (calculada, não é salva). */
        boolean marcaModelo;

        Mensagem(boolean usuario, boolean aviso, String texto) {
            this.usuario = usuario;
            this.aviso = aviso;
            this.texto = texto;
        }
    }

    /** Resposta ainda sendo gerada (a tela mostra os pontinhos de "digitando"). */
    static final String DIGITANDO = "…", SEM_RESPOSTA = "(sem resposta)";

    /** Uma tela aberta (todas as chamadas vêm na thread principal). */
    interface Ouvinte {
        default void mensagemNova(Mensagem m) {
        }

        default void mensagemMudou(Mensagem m) {
        }

        /** A conversa inteira foi trocada (outro chat, conversa limpa). */
        default void conversaTrocada() {
        }

        /** A lista de chats mudou (título novo, chat apagado ou arquivado). */
        default void chatsMudaram() {
        }

        default void estadoMudou() {
        }

        /** Resultado de uma operação (importar, backup...), para mostrar ao usuário. */
        default void aviso(String titulo, String texto) {
        }

        /** Um modelo novo foi guardado nos backups (a tela pode oferecer "Usar agora"). */
        default void backupNovo(String titulo, String texto, String id) {
            aviso(titulo, texto);
        }
    }

    private static Motor instancia;

    static synchronized Motor get(Context ctx) {
        if (instancia == null) instancia = new Motor(ctx.getApplicationContext());
        return instancia;
    }

    /** Limites das barrinhas do menu: temperatura e tamanho máximo da resposta (tokens; o chat.py usa 80). */
    static final double TEMP_MIN = 0.1, TEMP_MAX = 1.5;
    static final int TAMANHO_MIN = 16, TAMANHO_MAX = 120;
    /** Janela do modelo de conversa em uso (para o limite da barrinha de tamanho). */
    volatile int janela = 256;

    private final Context ctx;
    private final SharedPreferences prefs;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final ExecutorService fundo = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "laika");
        t.setDaemon(true);
        return t;
    });
    private final AtomicBoolean cancelar = new AtomicBoolean(), pararTarefa = new AtomicBoolean();
    private final Random rng = new Random();
    private final Set<Ouvinte> ouvintes = new LinkedHashSet<>();
    private final int threads = Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors()));

    final List<Mensagem> conversa = new ArrayList<>();

    Armazem armazem;
    private Tokenizador tok;
    private Laika chat, base;
    private IndiceRag rag;
    private Memoria memoria;
    private volatile String refChat, refBase;
    /** Arquivo do modelo de chat -> nome exibido (apelido ou nome), de todas as versões, para as marcas de modelo. */
    private volatile Map<String, String> nomesPorRef = new java.util.HashMap<>();
    Chats chats;
    /** O chat aberto (muda na thread de fundo) e o que a tela mostra (muda na thread principal, junto com conversa). */
    private volatile Chats.Chat chatAtual;
    private Chats.Chat chatDaTela;
    volatile String tituloChat = Chats.SEM_TITULO;

    volatile boolean pronto, gerando;
    volatile String erro;
    /** Operação longa em andamento (importar, exportar, trocar de versão) ou null. */
    volatile String tarefa;
    /** 0..100, ou -1 se não dá para medir. */
    volatile int progresso = -1;
    /** A tarefa em andamento pode ser cancelada (importação, índice, download). */
    volatile boolean tarefaCancelavel;
    volatile String nomeVersao = "", nomeExibido = "";
    volatile String descricaoIndice = "", descricaoModelo = "";
    volatile boolean temBase;

    // Opções do app (valem para todas as versões)
    /** usarHistorico: a "memória de IA" (as últimas trocas da conversa entram no prompt). */
    /** respostasLongas: acrescenta o gatilho "Resposta longa." à pergunta e usa o tamanho máximo. */
    boolean mostrarFontes, usarRag, usarMemoria, usarHistorico, modoCompletar, respostasLongas;
    double temperatura;
    int tamanhoResposta;

    private Motor(Context ctx) {
        this.ctx = ctx;
        prefs = ctx.getSharedPreferences("opcoes", Context.MODE_PRIVATE);
        mostrarFontes = prefs.getBoolean("fontes", true);
        usarRag = prefs.getBoolean("rag", true);
        usarMemoria = prefs.getBoolean("memoria", true);
        usarHistorico = prefs.getBoolean("historico", true);
        respostasLongas = prefs.getBoolean("longas", false);
        temperatura = Math.max(TEMP_MIN, Math.min(TEMP_MAX, prefs.getFloat("temperatura", 0.7f)));
        tamanhoResposta = Math.max(TAMANHO_MIN, Math.min(400, prefs.getInt("tamanho", 80)));
        tarefa = "Carregando a Laika…";
        fundo.execute(this::iniciar);
    }

    /**
     * Até 120 tokens com janela de 256 (o resto fica para a pergunta, o RAG e o histórico); 200 com 512 e 400 com
     * 1024 ou mais (o modelo de 100M, com 2048), que têm espaço para respostas longas.
     */
    int tamanhoMaximo() {
        return janela >= 1024 ? 400 : janela >= 512 ? 200 : TAMANHO_MAX;
    }

    void salvarOpcoes() {
        prefs.edit().putBoolean("fontes", mostrarFontes).putBoolean("rag", usarRag)
                .putBoolean("memoria", usarMemoria).putBoolean("historico", usarHistorico)
                .putBoolean("longas", respostasLongas)
                .putFloat("temperatura", (float) temperatura).putInt("tamanho", tamanhoResposta).apply();
        avisarEstado();
    }

    void adicionarOuvinte(Ouvinte o) {
        ouvintes.add(o);
    }

    void removerOuvinte(Ouvinte o) {
        ouvintes.remove(o);
    }

    boolean ocupado() {
        return tarefa != null;
    }

    /** Pede para parar a tarefa longa em andamento (ela desfaz o que estava fazendo). */
    void cancelarTarefa() {
        pararTarefa.set(true);
        if (tarefa != null) tarefa("Cancelando…", -1);
    }

    // ---------- avisos para as telas ----------

    private void naTela(Runnable r) {
        if (Looper.myLooper() == Looper.getMainLooper()) r.run();
        else ui.post(r);
    }

    private void avisarEstado() {
        naTela(() -> {
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.estadoMudou();
        });
    }

    private void tarefa(String t, int pct) {
        tarefa = t;
        progresso = pct;
        avisarEstado();
    }

    private void avisarBackupNovo(String titulo, String texto, String id) {
        naTela(() -> {
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.backupNovo(titulo, texto, id);
        });
    }

    private void avisarUsuario(String titulo, String texto) {
        naTela(() -> {
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.aviso(titulo, texto);
        });
    }

    private Mensagem adicionar(Mensagem m) {
        naTela(() -> {
            conversa.add(m);
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.mensagemNova(m);
        });
        return m;
    }

    private void mudou(Mensagem m) {
        naTela(() -> {
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.mensagemMudou(m);
        });
    }

    Mensagem aviso(String texto) {
        return adicionar(new Mensagem(false, true, texto));
    }

    static String agora() {
        return new SimpleDateFormat("dd/MM/yyyy HH:mm", new Locale("pt", "BR")).format(new Date());
    }

    // ---------- carregamento ----------

    private void iniciar() {
        long t0 = System.currentTimeMillis();
        try {
            armazem = new Armazem(new File(ctx.getFilesDir(), "laika"), new Armazem.Fabrica() {
                @Override
                public InputStream abrir(String nome) throws IOException {
                    return ctx.getAssets().open(nome);
                }

                @Override
                public boolean existe(String nome) {
                    try (InputStream in = ctx.getAssets().open(nome)) {
                        return true;
                    } catch (IOException e) {
                        return false;
                    }
                }
            });
            migrarDaVersaoAntiga();
            chats = new Chats(new File(ctx.getFilesDir(), "laika/chats"));
            migrarConversas();
            abrirChat(chats.atual());
            carregarVersao();
            aviso(String.format(Locale.getDefault(), "Laika pronta em %.1f s.", (System.currentTimeMillis() - t0) / 1000.0));
        } catch (Throwable e) {
            erro = "Não consegui carregar o modelo: " + e.getMessage();
            aviso(erro + " Abra Versões e backups para usar outra versão.");
        }
        tarefa(null, -1);
    }

    /** O app 1.0 guardava o índice importado e a memória direto na pasta do app. */
    private void migrarDaVersaoAntiga() throws IOException {
        File indice = new File(ctx.getFilesDir(), "laika_rag.db");
        File mem = new File(ctx.getFilesDir(), "memoria.json");
        Map<String, Armazem.Arquivo> trocas = new LinkedHashMap<>();
        if (indice.exists()) {
            long n;
            try (IndiceRag r = new IndiceRag(abrirSomenteLeitura(indice))) {
                n = r.contarTrechos();
            } catch (RuntimeException e) {
                indice.delete();
                n = -1;
            }
            if (n >= 0) {
                trocas.put(Armazem.INDICE, armazem.guardar(indice, "db", "laika_rag.db",
                        String.format(Locale.getDefault(), "índice com %,d trechos", n)));
            }
        }
        byte[] memoria = null;
        if (mem.exists()) {
            if (!armazem.memoriaAtual().exists()) memoria = Files.readAllBytes(mem.toPath());
            mem.delete();
        }
        if (!trocas.isEmpty() || memoria != null) armazem.aplicar(trocas, null, memoria);
        // O app 1.1 treinava no celular. Um resultado de treino que não foi usado vira um backup;
        // o resto (dados importados, tokens, estado do treino) não serve mais e só ocupa espaço.
        File treino = new File(ctx.getFilesDir(), "laika/treino");
        if (treino.exists() && guardarTreinoAntigo(new File(treino, "saida"))) apagarPasta(treino);
        apagarPasta(new File(ctx.getFilesDir(), "laika/dados"));
    }

    /** Guarda laika/treino/saida (app 1.1) como backup. false se não conseguiu (aí nada é apagado). */
    private boolean guardarTreinoAntigo(File saida) {
        File chatBin = new File(saida, "laika_chat.bin"), tokTxt = new File(saida, "tokenizer.txt");
        if (!chatBin.exists() || !tokTxt.exists()) return true;
        try {
            String[][] papeis = {{Armazem.CHAT, "laika_chat.bin", "bin"}, {Armazem.BASE, "laika_base.bin", "bin"},
                    {Armazem.TOKENIZER, "tokenizer.txt", "txt"}, {Armazem.INDICE, "laika_rag.db", "db"}};
            // Primeiro confere tudo (sem mexer em nada); só depois move os arquivos para os blobs.
            Map<String, String> descricoes = new LinkedHashMap<>();
            for (String[] p : papeis) {
                File f = new File(saida, p[1]);
                if (!f.exists()) continue;
                if (p[2].equals("bin")) {
                    try (InputStream in = new FileInputStream(f)) {
                        descricoes.put(p[0], com.brunodevpro.laika.core.ConversorPt.lerBin(in).descricao());
                    }
                } else if (p[2].equals("txt")) {
                    try (InputStream in = new FileInputStream(f)) {
                        descricoes.put(p[0], Armazem.descricaoTokenizer(in));
                    }
                } else {
                    descricoes.put(p[0], String.format(Locale.getDefault(), "índice com %,d trechos", conferirIndice(f)));
                }
            }
            Map<String, Armazem.Arquivo> arqs = new LinkedHashMap<>();
            for (String[] p : papeis) {
                if (descricoes.containsKey(p[0])) {
                    arqs.put(p[0], armazem.guardar(new File(saida, p[1]), p[2], p[1] + " (treino no celular)",
                            descricoes.get(p[0])));
                }
            }
            armazem.backupDeArquivos("Treino no celular (app 1.1)", arqs);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private static void apagarPasta(File f) {
        File[] fs = f.listFiles();
        if (fs != null) for (File x : fs) apagarPasta(x);
        f.delete();
    }

    private static SQLiteConnection abrirSomenteLeitura(File f) {
        return new BundledSQLiteDriver().open(f.getPath(), BundledSQLite.SQLITE_OPEN_READONLY);
    }

    private static long conferirIndice(File f) {
        try (IndiceRag r = new IndiceRag(abrirSomenteLeitura(f))) {
            long n = r.contarTrechos();
            r.buscar("O que é um vulcão?");
            return n;
        }
    }

    private void fecharTudo() {
        if (chat != null) chat.modelo.fechar();
        if (base != null) base.modelo.fechar();
        if (rag != null) rag.close();
        chat = base = null;
        rag = null;
        tok = null;
        pronto = false;
    }

    /** Carrega a versão em uso: modelo, tokenizer, índice, memória e conversa. */
    private void carregarVersao() throws IOException {
        fecharTudo();
        erro = null;
        Armazem.Versao v = armazem.atual();
        nomeVersao = v.nome;
        nomeExibido = v.nomeExibido();
        Armazem.Arquivo arqChat = v.arquivos.get(Armazem.CHAT);
        descricaoModelo = arqChat.descricao == null ? "" : arqChat.descricao;
        try (InputStream in = armazem.abrir(v.arquivos.get(Armazem.TOKENIZER).ref)) {
            tok = new Tokenizador(in);
        }
        refChat = arqChat.ref;
        chat = carregar(refChat);
        janela = chat.modelo.block;
        Armazem.Arquivo b = v.arquivos.get(Armazem.BASE);
        refBase = b == null ? null : b.ref;
        temBase = b != null;
        if (!temBase) modoCompletar = false;

        Armazem.Arquivo ind = v.arquivos.get(Armazem.INDICE);
        File db = armazem.arquivo(ind.ref);
        if (db == null) db = indiceDeFabrica(ind.ref.substring(Armazem.FABRICA.length()));
        try {
            rag = new IndiceRag(abrirSomenteLeitura(db));
            long n = rag.contarTrechos();
            descricaoIndice = String.format(Locale.getDefault(), "%s (%,d trechos)",
                    n > 100_000 ? "índice completo" : "índice pequeno", n);
        } catch (RuntimeException e) {
            rag = null;
            descricaoIndice = "índice com erro";
            aviso("O índice desta versão não abriu: " + e.getMessage());
        }
        pronto = true;
        atualizarNomes();
    }

    // ---------- chats ----------

    /**
     * Até a 1.9, cada versão tinha a sua conversa e a sua memória. Na primeira vez, cada uma que tinha alguma coisa
     * vira um chat (sem repetir as iguais); a da versão em uso fica aberta.
     */
    private void migrarConversas() throws IOException {
        if (chats.migrado()) return;
        java.util.Set<String> vistas = new java.util.HashSet<>();
        String abrir = null;
        List<Armazem.Versao> versoes = new ArrayList<>();
        versoes.add(armazem.atual());
        versoes.addAll(armazem.backups());
        for (Armazem.Versao v : versoes) {
            byte[] conv = lerOuNada(v.conversa()), mem = lerOuNada(v.memoria());
            boolean temConversa = conv != null && v.mensagens() > 0;
            boolean temMemoria = mem != null && !new Memoria(v.memoria()).resumo().startsWith("Ainda não sei");
            if (!temConversa && !temMemoria) continue;
            String chave = (conv == null ? "" : new String(conv, StandardCharsets.UTF_8)) + "|"
                    + (mem == null ? "" : new String(mem, StandardCharsets.UTF_8));
            if (!vistas.add(chave)) continue;
            Chats.Chat c = chats.importar("Conversa de " + v.nomeExibido(), conv, mem, v.alterado);
            if (v.id == null) abrir = c.id;
        }
        if (abrir != null) chats.usar(abrir);
        chats.marcarMigrado();
    }

    private static byte[] lerOuNada(File f) {
        try {
            return f.exists() ? Files.readAllBytes(f.toPath()) : null;
        } catch (IOException e) {
            return null;
        }
    }

    /** Abre um chat (na thread de fundo): a memória e a conversa dele. */
    private void abrirChat(Chats.Chat c) throws IOException {
        chats.usar(c.id);
        chatAtual = c;
        tituloChat = c.titulo;
        memoria = new Memoria(c.memoria());
        List<Mensagem> lidas = lerConversa(c.conversa());
        naTela(() -> {
            chatDaTela = c;
            conversa.clear();
            conversa.addAll(lidas);
            marcarModelos(false);
            for (Ouvinte o : new ArrayList<>(ouvintes)) {
                o.conversaTrocada();
                o.chatsMudaram();
            }
        });
        avisarEstado();
    }

    /**
     * As linhas discretas "*modelo X usado": depois da última resposta de cada trecho da conversa feito com um modelo
     * diferente do seguinte (ou do modelo em uso, no fim). Na thread principal; avisar = redesenhar se mudou.
     */
    private void marcarModelos(boolean avisar) {
        List<Mensagem> base = new ArrayList<>();
        for (Mensagem m : conversa) if (!m.marcaModelo) base.add(m);
        List<Mensagem> nova = new ArrayList<>();
        Map<String, String> nomes = nomesPorRef;
        for (int i = 0; i < base.size(); i++) {
            Mensagem m = base.get(i);
            nova.add(m);
            if (m.usuario || m.aviso || m.modeloRef == null) continue;
            String proximo = refChat;
            for (int k = i + 1; k < base.size(); k++) {
                Mensagem n = base.get(k);
                if (!n.usuario && !n.aviso && n.modeloRef != null) {
                    proximo = n.modeloRef;
                    break;
                }
            }
            if (proximo == null || m.modeloRef.equals(proximo)) continue;
            String nome = nomes.containsKey(m.modeloRef) ? nomes.get(m.modeloRef) : m.modeloNome;
            Mensagem marca = new Mensagem(false, true, "*modelo " + nome + " usado");
            marca.marcaModelo = true;
            nova.add(marca);
        }
        boolean igual = nova.size() == conversa.size();
        for (int i = 0; igual && i < nova.size(); i++) {
            Mensagem a = nova.get(i), b = conversa.get(i);
            igual = a == b || (a.marcaModelo && b.marcaModelo && a.texto.equals(b.texto));
        }
        if (igual) return;
        conversa.clear();
        conversa.addAll(nova);
        if (avisar) for (Ouvinte o : new ArrayList<>(ouvintes)) o.conversaTrocada();
    }

    /** Os nomes (apelidos) dos modelos de todas as versões, para as marcas "*modelo X usado". */
    private void atualizarNomes() throws IOException {
        Map<String, String> m = new java.util.HashMap<>();
        for (Armazem.Versao b : armazem.backups()) {
            Armazem.Arquivo a = b.arquivos.get(Armazem.CHAT);
            if (a != null) m.put(a.ref, b.nomeExibido());
        }
        Armazem.Versao v = armazem.atual();
        m.put(v.arquivos.get(Armazem.CHAT).ref, v.nomeExibido());
        nomesPorRef = m;
        naTela(() -> marcarModelos(true));
    }

    private void avisarChats() {
        naTela(() -> {
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.chatsMudaram();
        });
    }

    /** Os chats (arquivados também), do mais recente para o mais antigo; vazio enquanto carrega. */
    List<Chats.Chat> listaChats() {
        return chats == null ? new ArrayList<>() : chats.lista();
    }

    String idChatAtual() {
        Chats.Chat c = chatAtual;
        return c == null ? null : c.id;
    }

    private void noChat(Tarefa t) {
        if (gerando) cancelar.set(true);
        fundo.execute(() -> {
            try {
                if (chats != null) t.rodar();
            } catch (Exception e) {
                avisarUsuario("Não deu certo", e.getMessage());
            }
        });
    }

    /** Um chat novo; se o aberto ainda está vazio, fica nele. */
    void novoChat() {
        noChat(() -> {
            Chats.Chat c = chatAtual;
            if (c != null && !c.arquivado && c.mensagens() == 0 && c.semTitulo()) {
                abrirChat(c);
                return;
            }
            abrirChat(chats.novo());
        });
    }

    void usarChat(String id) {
        noChat(() -> abrirChat(chats.ler(id)));
    }

    void renomearChat(String id, String titulo) {
        noChat(() -> {
            chats.renomear(id, titulo);
            Chats.Chat c = chatAtual;
            if (c != null && c.id.equals(id)) {
                c.titulo = titulo;
                c.tituloManual = true;
                tituloChat = titulo;
                avisarEstado();
            }
            avisarChats();
        });
    }

    void arquivarChat(String id, boolean arquivar) {
        noChat(() -> {
            chats.arquivar(id, arquivar);
            Chats.Chat c = chatAtual;
            if (arquivar && c != null && c.id.equals(id)) abrirChat(proximoChat(id));
            avisarChats();
        });
    }

    void apagarChat(String id) {
        noChat(() -> {
            chats.apagar(id);
            Chats.Chat c = chatAtual;
            if (c != null && c.id.equals(id)) abrirChat(proximoChat(id));
            avisarChats();
        });
    }

    /** Depois de arquivar ou apagar o chat aberto: o mais recente não arquivado, ou um novo. */
    private Chats.Chat proximoChat(String fora) throws IOException {
        for (Chats.Chat c : chats.lista()) if (!c.arquivado && !c.id.equals(fora)) return c;
        return chats.novo();
    }

    /** Depois da primeira resposta: a IA dá um título ao chat (o usuário pode renomear depois). */
    private void tituloDoChat(Chats.Chat c, String pergunta, boolean completar) {
        String titulo;
        try {
            String gerado = "";
            if (!completar && chat != null) {
                String p = pergunta.length() > 300 ? pergunta.substring(0, 300) : pergunta;
                Laika.Opcoes op = new Laika.Opcoes();
                op.temperatura = 0.2;
                op.topK = 1;
                op.maxNovos = 16;
                Laika.Prompt pr = chat.montarPrompt(Texto.PEDIDO_TITULO + p, null, null, op.maxNovos, new ArrayList<>());
                gerado = chat.gerar(pr.texto, op, true, rng, parcial -> {
                }, () -> false);
            }
            titulo = Texto.limparTitulo(gerado, pergunta);
            if (!chats.tituloDaIa(c.id, titulo)) return;
        } catch (Throwable e) {
            return;  // sem título: continua "Novo chat"
        }
        if (chatAtual == c) {
            c.titulo = titulo;
            tituloChat = titulo;
            avisarEstado();
        }
        avisarChats();
    }

    private Laika carregar(String ref) throws IOException {
        try (InputStream in = armazem.abrir(ref)) {
            return new Laika(new Modelo(in, threads), tok);
        } catch (OutOfMemoryError e) {
            throw new IOException("falta memória no celular para este modelo");
        }
    }

    /** Modelos de dezenas de milhões de parâmetros (~200 MB na memória): só um carregado por vez. */
    private static boolean grande(Laika l) {
        Modelo m = l.modelo;
        return 12L * m.dim * m.dim * m.layers > 20_000_000L;
    }

    /** O índice que vem no APK precisa virar arquivo para o SQLite abrir. */
    private File indiceDeFabrica(String nome) throws IOException {
        File f = new File(ctx.getFilesDir(), nome);
        long versao = versaoDoApp();
        if (!f.exists() || prefs.getLong("versao_mini", -1) != versao) {
            try (InputStream in = ctx.getAssets().open(nome)) {
                Armazem.copiar(in, f, -1, null);
            }
            prefs.edit().putLong("versao_mini", versao).apply();
        }
        return f;
    }

    private long versaoDoApp() {
        try {
            return PackageInfoCompat.getLongVersionCode(ctx.getPackageManager().getPackageInfo(ctx.getPackageName(), 0));
        } catch (Exception e) {
            return 0;
        }
    }

    // ---------- conversa salva ----------

    @SuppressWarnings("unchecked")
    private static List<Mensagem> lerConversa(File f) {
        List<Mensagem> r = new ArrayList<>();
        if (!f.exists()) return r;
        try {
            Object o = Json.ler(new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8));
            for (Object x : (List<Object>) o) {
                Map<String, Object> m = (Map<String, Object>) x;
                Mensagem msg = new Mensagem(Boolean.TRUE.equals(m.get("u")), false, String.valueOf(m.get("t")));
                msg.fonte = (String) m.get("f");
                msg.detalhe = (String) m.get("d");
                msg.trecho = (String) m.get("c");
                msg.completar = Boolean.TRUE.equals(m.get("x"));
                msg.modeloRef = (String) m.get("r");
                msg.modeloNome = (String) m.get("m");
                r.add(msg);
            }
        } catch (Exception e) {
            // conversa corrompida: começa vazia
        }
        return r;
    }

    /** Chamado na thread principal; grava em segundo plano, no chat que está na tela. */
    void salvarConversa() {
        Chats.Chat alvo = chatDaTela;
        if (alvo == null) return;
        List<Map<String, Object>> lista = new ArrayList<>();
        for (Mensagem m : conversa) {
            if (m.aviso) continue;
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("u", m.usuario);
            o.put("t", m.texto);
            if (m.fonte != null) o.put("f", m.fonte);
            if (m.detalhe != null) o.put("d", m.detalhe);
            if (m.trecho != null) o.put("c", m.trecho);
            if (m.completar) o.put("x", true);
            if (m.modeloRef != null) {
                o.put("r", m.modeloRef);
                o.put("m", m.modeloNome);
            }
            lista.add(o);
        }
        String json = Json.escrever(lista);
        fundo.execute(() -> {
            try {
                Files.write(alvo.conversa().toPath(), json.getBytes(StandardCharsets.UTF_8));
                chats.tocar(alvo);
                avisarChats();
            } catch (IOException ignorado) {
                // sem espaço: a conversa continua na tela
            }
        });
    }

    void limparConversa() {
        if (gerando) cancelar.set(true);
        conversa.clear();
        for (Ouvinte o : new ArrayList<>(ouvintes)) o.conversaTrocada();
        salvarConversa();
    }

    // ---------- conversa ----------

    String resumoMemoria() {
        return memoria == null ? "" : memoria.resumo();
    }

    void apagarMemoria() {
        fundo.execute(() -> {
            if (memoria != null) memoria.tratar("esqueça tudo");
            aviso("Memória apagada.");
        });
    }

    void pararGeracao() {
        cancelar.set(true);
    }

    void enviar(String texto) {
        Mensagem eu = new Mensagem(true, false, texto);
        eu.completar = modoCompletar;
        conversa.add(eu);
        for (Ouvinte o : new ArrayList<>(ouvintes)) o.mensagemNova(eu);
        responder(eu, null, historicoAte(conversa.size() - 1));
    }

    /** Índice da pergunta que gerou esta resposta (a mensagem do usuário logo antes), ou -1. */
    private int indicePergunta(Mensagem resposta) {
        int i = conversa.indexOf(resposta);
        for (int k = i - 1; k >= 0; k--) {
            Mensagem m = conversa.get(k);
            if (m.aviso) continue;
            return m.usuario ? k : -1;
        }
        return -1;
    }

    /** A pergunta que gerou esta resposta, ou null. */
    String perguntaDe(Mensagem resposta) {
        int i = indicePergunta(resposta);
        return i < 0 ? null : conversa.get(i).texto;
    }

    /** Gera outra resposta para a mesma pergunta, no lugar desta (com o histórico de antes da pergunta). */
    void gerarDeNovo(Mensagem resposta) {
        int i = indicePergunta(resposta);
        if (i < 0 || gerando) return;
        resposta.texto = DIGITANDO;
        resposta.fonte = resposta.detalhe = resposta.trecho = null;
        mudou(resposta);
        responder(conversa.get(i), resposta, historicoAte(i));
    }

    /**
     * A memória de IA: as últimas trocas (pergunta, resposta) da conversa antes da posição fim, como o
     * history do chat.py. Pula avisos, erros, respostas vazias ou interrompidas e o modo completar texto.
     */
    private List<String[]> historicoAte(int fim) {
        List<String[]> r = new ArrayList<>();
        if (!usarHistorico) return r;
        for (int i = 0; i < fim; i++) {
            Mensagem p = conversa.get(i);
            if (!p.usuario || p.aviso || p.completar) continue;
            int j = i + 1;
            while (j < fim && conversa.get(j).aviso) j++;
            if (j >= fim) break;
            Mensagem a = conversa.get(j);
            if (a.usuario || a.completar || a.texto == null || a.texto.equals(DIGITANDO) || a.texto.equals(SEM_RESPOSTA)
                    || a.texto.startsWith("Erro:")
                    || (a.detalhe != null && a.detalhe.contains("interrompida"))) continue;
            r.add(new String[]{p.texto, a.texto});
        }
        return r.size() > Texto.MAX_HISTORY ? new ArrayList<>(r.subList(r.size() - Texto.MAX_HISTORY, r.size())) : r;
    }

    private void responder(Mensagem pergunta, Mensagem existente, List<String[]> historico) {
        final String texto = pergunta.texto;
        gerando = true;
        cancelar.set(false);
        avisarEstado();
        final boolean completar = modoCompletar, fontes = mostrarFontes, comRag = usarRag, comMemoria = usarMemoria;
        final double temp = temperatura;
        final int tamanho = Math.min(tamanhoResposta, tamanhoMaximo());
        final boolean longas = respostasLongas;
        if (existente != null) existente.completar = completar;
        fundo.execute(() -> {
            Mensagem resp = existente;
            if (resp == null) {
                resp = new Mensagem(false, false, DIGITANDO);
                resp.completar = completar;
                adicionar(resp);
            }
            responderEm(pergunta, resp, texto, historico, completar, fontes, comRag, comMemoria, temp, tamanho, longas);
        });
    }

    private void responderEm(Mensagem pergunta, Mensagem resp, String texto, List<String[]> historico, boolean completar,
                             boolean fontes, boolean comRag, boolean comMemoria, double temp, int tamanho,
                             boolean longas) {
        long t0 = System.nanoTime();
        Laika.Opcoes op = new Laika.Opcoes();
        try {
            if (!pronto) throw new IllegalStateException(erro != null ? erro : "o modelo ainda está carregando");
            op.temperatura = temp;
            if (completar && refBase != null) {
                if (base == null) {
                    if (chat != null && grande(chat)) {  // um modelo grande por vez
                        chat.modelo.fechar();
                        chat = null;
                    }
                    resp.texto = "Carregando o modelo de completar texto…";
                    mudou(resp);
                    base = carregar(refBase);
                }
                op.maxNovos = tamanho * 2;
                String r = base.gerar(texto, op, false, rng, parcial -> {
                    resp.texto = texto + " " + parcial;
                    mudou(resp);
                }, cancelar::get);
                resp.texto = texto + " " + r;
                resp.modeloRef = refChat;
                resp.modeloNome = nomeExibido;
            } else {
                String direto = comMemoria ? memoria.tratar(texto) : null;
                if (direto != null) {
                    resp.texto = direto;
                    resp.modeloRef = resp.modeloNome = null;  // a memória respondeu, não o modelo
                } else {
                    if (chat == null) {  // foi liberado para o modelo de completar texto (modelo grande)
                        if (base != null) {
                            base.modelo.fechar();
                            base = null;
                        }
                        resp.texto = "Carregando o modelo de conversa…";
                        mudou(resp);
                        chat = carregar(refChat);
                    }
                    // Respostas longas: o gatilho do fine-tuning ("Resposta longa.") e o tamanho máximo.
                    String paraModelo = longas && !Texto.querLonga(texto) ? texto + " " + Texto.GATILHO_LONGO : texto;
                    op.maxNovos = Texto.querLonga(paraModelo) ? tamanhoMaximo() : tamanho;
                    Laika.Prompt p = chat.montarPrompt(paraModelo, comRag ? rag : null, comMemoria ? memoria : null,
                            op.maxNovos, historico);
                    String r = chat.gerar(p.texto, op, true, rng, parcial -> {
                        resp.texto = parcial.isEmpty() ? DIGITANDO : parcial;
                        mudou(resp);
                    }, cancelar::get);
                    resp.texto = r.isEmpty() ? SEM_RESPOSTA : r;
                    resp.modeloRef = refChat;
                    resp.modeloNome = nomeExibido;
                    if (fontes) resp.fonte = p.fonte;
                    resp.trecho = p.trecho;
                }
            }
            double seg = (System.nanoTime() - t0) / 1e9;
            // Tokens: os da pergunta, os da resposta e o total que passou pelo modelo (prompt com contexto,
            // histórico e gatilho + resposta).
            int naPergunta = tok.codificar(texto).length;
            int naResposta = op.gerados > 0 ? op.gerados : tok.codificar(resp.texto).length;
            pergunta.detalhe = naPergunta + (naPergunta == 1 ? " token" : " tokens");
            mudou(pergunta);
            resp.detalhe = String.format(Locale.getDefault(), "%.1f s%s · %d tokens%s%s", seg,
                    op.gerados > 0 ? String.format(Locale.getDefault(), " · %d tokens/s", Math.round(op.gerados / seg)) : "",
                    naResposta,
                    op.tokensPrompt > 0 ? String.format(Locale.getDefault(), " · %d no total", op.tokensPrompt + op.gerados) : "",
                    cancelar.get() ? " · interrompida" : "");
        } catch (Throwable e) {
            resp.texto = "Erro: " + e.getMessage();
        }
        mudou(resp);
        gerando = false;
        naTela(() -> {
            salvarConversa();
            marcarModelos(true);
        });
        avisarEstado();
        Chats.Chat c = chatAtual;
        if (c != null && c.semTitulo() && !resp.texto.startsWith("Erro:")) tituloDoChat(c, texto, completar);
    }

    // ---------- versões e backups ----------

    /** longa: importação/exportação/download, que segue com a tela apagada (TrabalhoService). */
    private void emFundo(String titulo, boolean longa, Tarefa t) {
        cancelar.set(true);  // para uma resposta em andamento antes de mexer na versão
        pararTarefa.set(false);
        tarefaCancelavel = longa;
        tarefa(titulo, -1);
        if (longa) TrabalhoService.iniciar(ctx);
        fundo.execute(() -> {
            try {
                t.rodar();
            } catch (Throwable e) {
                if (cancelado(e)) {
                    try {
                        armazem.limparBlobs();
                    } catch (IOException ignorado) {
                        // sobra lixo até a próxima importação
                    }
                    avisarUsuario(null, "Cancelado.");
                } else {
                    avisarUsuario("Não deu certo", e.getMessage() == null ? e.toString() : e.getMessage());
                }
                if (!pronto) {
                    try {
                        carregarVersao();
                    } catch (Throwable e2) {
                        erro = "Não consegui carregar a versão: " + e2.getMessage();
                    }
                }
            }
            tarefaCancelavel = false;
            tarefa(null, -1);
        });
    }

    private static boolean cancelado(Throwable e) {
        for (Throwable x = e; x != null; x = x.getCause()) if (x instanceof Parado) return true;
        return false;
    }

    private interface Tarefa {
        void rodar() throws Exception;
    }

    private Armazem.Progresso progresso(String titulo) {
        int[] ultimo = {-2};
        return (feito, total) -> {
            if (pararTarefa.get()) throw new Parado();
            int pct = total > 0 ? (int) Math.min(100, feito * 100 / total) : -1;
            if (pct != ultimo[0]) {
                ultimo[0] = pct;
                tarefa(total > 0 ? titulo : titulo + " " + (feito >> 20) + " MB", pct);
            }
        };
    }

    void fazerBackup(String nome) {
        emFundo("Fazendo backup…", false, () -> {
            armazem.fazerBackup(nome);
            avisarUsuario(null, "Backup \"" + nome + "\" criado.");
        });
    }

    /**
     * Passa a usar o modelo do backup id. A conversa e a memória são do chat, então nada se perde; se o modelo em uso
     * não está em nenhum backup, ele é guardado antes (com o nome que tem).
     */
    void usarBackup(String id) {
        emFundo("Trocando de modelo…", false, () -> {
            if (armazem.backupComMesmosArquivos() == null) armazem.fazerBackup(nomeVersao);
            armazem.usarBackup(id);
            carregarVersao();  // e as marcas "*modelo X usado" dos chats (atualizarNomes)
            avisarEstado();
        });
    }

    /** Apelido do modelo (vazio = tira); id null = o modelo em uso. */
    void apelidar(String id, String apelido) {
        emFundo("Guardando o apelido…", false, () -> {
            armazem.apelidar(id, apelido);
            nomeExibido = armazem.atual().nomeExibido();
            atualizarNomes();
        });
    }

    void renomear(String id, String nome) {
        emFundo("Renomeando…", false, () -> {
            armazem.renomear(id, nome);
            if (id == null) nomeVersao = nome;
            nomeExibido = armazem.atual().nomeExibido();
            atualizarNomes();
        });
    }

    void apagarBackup(String id) {
        emFundo("Apagando backup…", false, () -> armazem.apagar(id));
    }

    void exportar(String id, Uri destino, boolean incluirIndice) {
        emFundo("Exportando…", true, () -> {
            try (OutputStream out = ctx.getContentResolver().openOutputStream(destino)) {
                if (out == null) throw new IOException("não consegui criar o arquivo");
                armazem.exportar(id, out, incluirIndice, progresso("Exportando…"));
            }
            avisarUsuario(null, "Backup exportado. Guarde o arquivo .zip no Google Drive para não perder seus dados.");
        });
    }

    static String nomeDoArquivo(Context ctx, Uri uri) {
        try (Cursor c = ctx.getContentResolver().query(uri, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getString(0);
        } catch (RuntimeException ignorado) {
            // sem nome
        }
        String s = uri.getLastPathSegment();
        return s == null ? "arquivo" : s;
    }

    static long tamanhoDoArquivo(Context ctx, Uri uri) {
        try (Cursor c = ctx.getContentResolver().query(uri, new String[]{OpenableColumns.SIZE}, null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getLong(0);
        } catch (RuntimeException ignorado) {
            // tamanho desconhecido
        }
        return -1;
    }

    // ---------- importar ----------

    /** Um arquivo a importar: escolhido no seletor ou baixado do Colab. */
    private interface Fonte {
        String nome();

        long tamanho();

        InputStream abrir() throws IOException;
    }

    private Fonte fonte(Uri u) {
        String nome = nomeDoArquivo(ctx, u);
        long tam = tamanhoDoArquivo(ctx, u);
        return new Fonte() {
            public String nome() {
                return nome;
            }

            public long tamanho() {
                return tam;
            }

            public InputStream abrir() throws IOException {
                InputStream in = ctx.getContentResolver().openInputStream(u);
                if (in == null) throw new IOException("não consegui abrir " + nome);
                return in;
            }
        };
    }

    private static Fonte fonte(File f, String nome) {
        return new Fonte() {
            public String nome() {
                return nome;
            }

            public long tamanho() {
                return f.length();
            }

            public InputStream abrir() throws IOException {
                return new FileInputStream(f);
            }
        };
    }

    /** Importa os arquivos escolhidos no seletor: uma atualização, o zip do Colab ou backups .zip. */
    void importar(List<Uri> uris) {
        List<Fonte> fontes = new ArrayList<>();
        for (Uri u : uris) fontes.add(fonte(u));
        emFundo("Importando…", true, () -> importarFontes(fontes, null));
    }

    /** Baixa o zip pronto de uma execução do Colab e o usa como versão nova. */
    void baixarDoColab(GitHub github, GitHub.Artefato a) {
        emFundo("Baixando do Colab…", true, () -> {
            File zip = new File(ctx.getCacheDir(), "colab_" + a.id + ".zip");
            if (a.tamanho > 0 && ctx.getFilesDir().getUsableSpace() < a.tamanho * 2 + (200L << 20)) {
                throw new IOException(String.format(Locale.getDefault(),
                        "falta espaço no celular: o zip tem %d MB e precisa de uns %d MB livres", a.tamanho >> 20,
                        (a.tamanho * 2 >> 20) + 200));
            }
            try {
                github.baixar(a, zip, progresso("Baixando do Colab…"), pararTarefa::get);
                importarFontes(List.of(fonte(zip, "laika_pacote.zip")), "Colab de " + agora());
            } finally {
                zip.delete();
            }
        });
    }

    private void importarFontes(List<Fonte> fontes, String nomeNovo) throws Exception {
        List<Importador.Entrada> entradas = new ArrayList<>();
        List<String> feitos = new ArrayList<>(), avisos = new ArrayList<>();
        long total = 0;
        for (Fonte f : fontes) total += Math.max(0, f.tamanho());
        if (total > 0 && ctx.getFilesDir().getUsableSpace() < total + total / 3 + (200L << 20)) {
            throw new IOException(String.format(Locale.getDefault(),
                    "falta espaço no celular: os arquivos têm %d MB e a importação precisa de uns %d MB livres",
                    total >> 20, (total + total / 3 >> 20) + 200));
        }
        File pastaCorpus = new File(ctx.getCacheDir(), "corpus");
        apagarPasta(pastaCorpus);
        Corpus corpus = new Corpus(pastaCorpus);
        int textos = 0;
        boolean temIndice = false;
        String nomePacote = null;
        try {
            int i = 0;
            for (Fonte f : fontes) {
                i++;
                String nome = f.nome();
                String titulo = (fontes.size() > 1 ? "(" + i + "/" + fontes.size() + ") " : "") + "Lendo " + nome + "…";
                try (InputStream bruto = f.abrir()) {
                    BufferedInputStream in = new BufferedInputStream(bruto, 1 << 16);
                    String tipo = Pacote.tipo(in);
                    if (Pacote.BACKUP.equals(tipo)) {
                        // Backup exportado: lido direto, sem cópia temporária.
                        Armazem.Versao b = armazem.importarBackup(in, f.tamanho(), progresso("Importando " + nome + "…"));
                        feitos.add("backup \"" + b.nome + "\"");
                        continue;
                    }
                    if (Pacote.PACOTE.equals(tipo)) {
                        Pacote p = Pacote.extrair(in, f.tamanho(), armazem, corpus, progresso(titulo));
                        entradas.addAll(p.entradas);
                        textos += p.textos;
                        temIndice |= p.temIndice();
                        if (p.nome != null) nomePacote = p.nome;
                        if (!p.ignorados.isEmpty()) {
                            avisos.add(String.format(Locale.getDefault(), "%d arquivo(s) do zip não servem para o app e "
                                    + "foram ignorados (ex.: %s)", p.ignorados.size(), p.ignorados.get(0)));
                        }
                        continue;
                    }
                    File tmp = armazem.temporario("x");
                    Armazem.copiar(in, tmp, f.tamanho(), progresso(titulo));
                    entradas.add(new Importador.Entrada(tmp, nome));
                    if (nome.toLowerCase(Locale.ROOT).endsWith(".db")) temIndice = true;
                }
            }
            if (textos > 0) {
                if (temIndice) avisos.add("os textos do zip não foram usados, porque ele já trazia o índice pronto");
                else entradas.add(montarIndice(corpus));
            }
            tarefaCancelavel = false;
            tarefa("Convertendo e conferindo os arquivos…", -1);
            Importador.Resultado r = new Importador(armazem, Motor::conferirIndice).importar(entradas);
            entradas.clear();
            for (Armazem.Versao b : r.backupsImportados) feitos.add("backup \"" + b.nome + "\"");
            String nomeVersaoNova = null;
            Armazem.Versao backupNovo = null;
            if (r.mudaVersao() && nomePacote != null) {
                // Modelo de um PROJETO do Colab: vai direto para os backups com o nome dele.
                tarefa("Guardando nos backups…", -1);
                backupNovo = armazem.backupComTrocas(nomePacote, r.trocas, null);
                memoriaDoPacote(r.memoria);
            } else if (r.mudaVersao()) {
                tarefa("Aplicando a atualização…", -1);
                String quando = agora();
                if (armazem.backupComMesmosArquivos() == null) {
                    armazem.fazerBackup(nomeVersao + " (antes da atualização de " + quando + ")");
                }
                nomeVersaoNova = nomeNovo != null ? nomeNovo : "Atualização de " + quando;
                armazem.aplicar(r.trocas, nomeVersaoNova, null);
                memoriaDoPacote(r.memoria);
                carregarVersao();
                aviso("Atualização aplicada: " + String.join(", ", r.feitos) + ".");
            }
            StringBuilder msg = new StringBuilder();
            if (backupNovo != null) {
                msg.append("O modelo \"").append(backupNovo.nome).append("\" foi guardado nos backups com: ")
                        .append(String.join(", ", r.feitos)).append(".\n\nA versão em uso continua a mesma. Para usar o novo, ")
                        .append("toque no nome da versão no topo da conversa e escolha \"").append(backupNovo.nome)
                        .append("\".");
            }
            if (nomeVersaoNova != null) {
                msg.append("Agora usando \"").append(nomeVersaoNova).append("\" com: ")
                        .append(String.join(", ", r.feitos)).append(".\n\nA versão anterior foi guardada nos backups.");
            }
            if (!feitos.isEmpty()) {
                if (msg.length() > 0) msg.append("\n\n");
                msg.append("Importado para a lista de backups: ").append(String.join(", ", feitos)).append('.');
            }
            avisos.addAll(r.avisos);
            if (!avisos.isEmpty()) msg.append("\n\nAtenção: ").append(String.join("; ", avisos)).append('.');
            String texto = msg.length() == 0 ? "Nada para importar." : msg.toString();
            if (backupNovo != null) avisarBackupNovo("Importação concluída", texto, backupNovo.id);
            else avisarUsuario("Importação concluída", texto);
        } finally {
            for (Importador.Entrada e : entradas) e.arquivo.delete();
            corpus.apagar();
        }
    }

    /** Um memoria.json que veio num pacote vai para o chat aberto, se ele ainda não tem memória. */
    private void memoriaDoPacote(byte[] mem) throws IOException {
        Chats.Chat c = chatAtual;
        if (mem == null || c == null || c.memoria().exists()) return;
        Files.write(c.memoria().toPath(), mem);
        memoria = new Memoria(c.memoria());
    }

    /** O "rag.py build" no celular, com os textos que vieram no zip (e os textos próprios do APK). */
    private Importador.Entrada montarIndice(Corpus corpus) throws IOException {
        corpus.garantirModerno(new Corpus.Fabrica() {
            @Override
            public String[] listar(String pasta) throws IOException {
                String[] r = ctx.getAssets().list("dados/" + pasta);
                return r == null ? new String[0] : r;
            }

            @Override
            public InputStream abrir(String caminho) throws IOException {
                return ctx.getAssets().open("dados/" + caminho);
            }
        });
        String resumo = corpus.resumo();
        tarefa("Montando o índice do RAG (" + resumo + ")…", -1);
        File db = armazem.temporario("db");
        SQLiteConnection con = new BundledSQLiteDriver().open(db.getPath());
        try {
            ConstrutorIndice.construir(corpus, con, new Registro() {
                @Override
                public void log(String linha) {
                }

                @Override
                public void progresso(double fracao, String texto) {
                    tarefa("Montando o índice do RAG: " + texto.replace("Índice: ", ""), fracao < 0 ? -1 : (int) (fracao * 100));
                }

                @Override
                public boolean parar() {
                    return pararTarefa.get();
                }
            });
        } catch (IOException | RuntimeException e) {
            con.close();
            db.delete();
            throw e;
        }
        con.close();
        return new Importador.Entrada(db, "índice montado no celular com " + resumo);
    }
}
