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
import com.brunodevpro.laika.core.Importador;
import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.Laika;
import com.brunodevpro.laika.core.Memoria;
import com.brunodevpro.laika.core.Modelo;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.File;
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
 * Tudo o que não é tela: a versão em uso (modelo, tokenizer, índice RAG, memória, conversa),
 * os backups e a geração das respostas. Vive enquanto o app estiver aberto.
 * O trabalho pesado roda numa única thread de fundo, em ordem.
 */
final class Motor {
    /** Uma mensagem da conversa. */
    static final class Mensagem {
        final boolean usuario, aviso;
        volatile String texto, fonte, detalhe;

        Mensagem(boolean usuario, boolean aviso, String texto) {
            this.usuario = usuario;
            this.aviso = aviso;
            this.texto = texto;
        }
    }

    /** Uma tela aberta (todas as chamadas vêm na thread principal). */
    interface Ouvinte {
        default void mensagemNova(Mensagem m) {
        }

        default void mensagemMudou(Mensagem m) {
        }

        /** A conversa inteira foi trocada (outra versão, conversa limpa). */
        default void conversaTrocada() {
        }

        default void estadoMudou() {
        }

        /** Resultado de uma operação (importar, backup...), para mostrar ao usuário. */
        default void aviso(String titulo, String texto) {
        }
    }

    private static Motor instancia;

    static synchronized Motor get(Context ctx) {
        if (instancia == null) instancia = new Motor(ctx.getApplicationContext());
        return instancia;
    }

    private static final String INDICE_MINI = "laika_rag_mini.db";

    private final Context ctx;
    private final SharedPreferences prefs;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final ExecutorService fundo = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "laika");
        t.setDaemon(true);
        return t;
    });
    private final AtomicBoolean cancelar = new AtomicBoolean();
    private final Random rng = new Random();
    private final Set<Ouvinte> ouvintes = new LinkedHashSet<>();
    private final int threads = Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors()));

    final List<Mensagem> conversa = new ArrayList<>();

    Armazem armazem;
    private Tokenizador tok;
    private Laika chat, base;
    private IndiceRag rag;
    private Memoria memoria;
    private String refBase;

    volatile boolean pronto, gerando;
    volatile String erro;
    /** Operação longa em andamento (importar, exportar, trocar de versão) ou null. */
    volatile String tarefa;
    /** 0..100, ou -1 se não dá para medir. */
    volatile int progresso = -1;
    volatile String nomeVersao = "";
    volatile String descricaoIndice = "";
    volatile boolean temBase;

    // Opções do app (valem para todas as versões)
    boolean mostrarFontes, usarRag, usarMemoria, modoCompletar;
    double temperatura;

    private Motor(Context ctx) {
        this.ctx = ctx;
        prefs = ctx.getSharedPreferences("opcoes", Context.MODE_PRIVATE);
        mostrarFontes = prefs.getBoolean("fontes", true);
        usarRag = prefs.getBoolean("rag", true);
        usarMemoria = prefs.getBoolean("memoria", true);
        temperatura = prefs.getFloat("temperatura", 0.7f);
        tarefa = "Carregando a Laika…";
        fundo.execute(this::iniciar);
    }

    void salvarOpcoes() {
        prefs.edit().putBoolean("fontes", mostrarFontes).putBoolean("rag", usarRag)
                .putBoolean("memoria", usarMemoria).putFloat("temperatura", (float) temperatura).apply();
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

    private static String agora() {
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
        try (InputStream in = armazem.abrir(v.arquivos.get(Armazem.TOKENIZER).ref)) {
            tok = new Tokenizador(in);
        }
        try (InputStream in = armazem.abrir(v.arquivos.get(Armazem.CHAT).ref)) {
            chat = new Laika(new Modelo(in, threads), tok);
        }
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
        memoria = new Memoria(armazem.memoriaAtual());
        List<Mensagem> lidas = lerConversa(armazem.conversaAtual());
        naTela(() -> {
            conversa.clear();
            conversa.addAll(lidas);
            for (Ouvinte o : new ArrayList<>(ouvintes)) o.conversaTrocada();
        });
        pronto = true;
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
                r.add(msg);
            }
        } catch (Exception e) {
            // conversa corrompida: começa vazia
        }
        return r;
    }

    /** Chamado na thread principal; grava em segundo plano. */
    void salvarConversa() {
        List<Map<String, Object>> lista = new ArrayList<>();
        for (Mensagem m : conversa) {
            if (m.aviso) continue;
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("u", m.usuario);
            o.put("t", m.texto);
            if (m.fonte != null) o.put("f", m.fonte);
            if (m.detalhe != null) o.put("d", m.detalhe);
            lista.add(o);
        }
        String json = Json.escrever(lista);
        fundo.execute(() -> {
            try {
                if (armazem != null) Files.write(armazem.conversaAtual().toPath(), json.getBytes(StandardCharsets.UTF_8));
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
        conversa.add(eu);
        for (Ouvinte o : new ArrayList<>(ouvintes)) o.mensagemNova(eu);
        gerando = true;
        cancelar.set(false);
        avisarEstado();
        final boolean completar = modoCompletar, fontes = mostrarFontes, comRag = usarRag, comMemoria = usarMemoria;
        final double temp = temperatura;
        fundo.execute(() -> {
            Mensagem resp = adicionar(new Mensagem(false, false, "…"));
            long t0 = System.nanoTime();
            try {
                if (!pronto) throw new IllegalStateException(erro != null ? erro : "o modelo ainda está carregando");
                Laika.Opcoes op = new Laika.Opcoes();
                op.temperatura = temp;
                if (completar && refBase != null) {
                    if (base == null) {
                        resp.texto = "Carregando o modelo de completar texto…";
                        mudou(resp);
                        try (InputStream in = armazem.abrir(refBase)) {
                            base = new Laika(new Modelo(in, threads), tok);
                        }
                    }
                    op.maxNovos = 160;
                    String r = base.gerar(texto, op, false, rng, parcial -> {
                        resp.texto = texto + " " + parcial;
                        mudou(resp);
                    }, cancelar::get);
                    resp.texto = texto + " " + r;
                } else {
                    String direto = comMemoria ? memoria.tratar(texto) : null;
                    if (direto != null) {
                        resp.texto = direto;
                    } else {
                        Laika.Prompt p = chat.montarPrompt(texto, comRag ? rag : null, comMemoria ? memoria : null,
                                op.maxNovos);
                        String r = chat.gerar(p.texto, op, true, rng, parcial -> {
                            resp.texto = parcial.isEmpty() ? "…" : parcial;
                            mudou(resp);
                        }, cancelar::get);
                        resp.texto = r.isEmpty() ? "…" : r;
                        if (fontes) resp.fonte = p.fonte;
                    }
                }
                resp.detalhe = String.format(Locale.getDefault(), "%.1f s%s", (System.nanoTime() - t0) / 1e9,
                        cancelar.get() ? " · interrompida" : "");
            } catch (Throwable e) {
                resp.texto = "Erro: " + e.getMessage();
            }
            mudou(resp);
            gerando = false;
            naTela(this::salvarConversa);
            avisarEstado();
        });
    }

    // ---------- versões e backups ----------

    private void emFundo(String titulo, Tarefa t) {
        cancelar.set(true);  // para uma resposta em andamento antes de mexer na versão
        tarefa(titulo, -1);
        fundo.execute(() -> {
            try {
                t.rodar();
            } catch (Throwable e) {
                avisarUsuario("Não deu certo", e.getMessage() == null ? e.toString() : e.getMessage());
                if (!pronto) {
                    try {
                        carregarVersao();
                    } catch (Throwable e2) {
                        erro = "Não consegui carregar a versão: " + e2.getMessage();
                    }
                }
            }
            tarefa(null, -1);
        });
    }

    private interface Tarefa {
        void rodar() throws Exception;
    }

    private Armazem.Progresso progresso(String titulo) {
        int[] ultimo = {-2};
        return (feito, total) -> {
            int pct = total > 0 ? (int) Math.min(100, feito * 100 / total) : -1;
            if (pct != ultimo[0]) {
                ultimo[0] = pct;
                tarefa(total > 0 ? titulo : titulo + " " + (feito >> 20) + " MB", pct);
            }
        };
    }

    void fazerBackup(String nome) {
        emFundo("Fazendo backup…", () -> {
            armazem.fazerBackup(nome);
            avisarUsuario(null, "Backup \"" + nome + "\" criado.");
        });
    }

    /** guardarAtualComo != null: guarda a versão em uso como backup antes de trocar. */
    void usarBackup(String id, String guardarAtualComo) {
        emFundo("Trocando de versão…", () -> {
            if (guardarAtualComo != null) armazem.fazerBackup(guardarAtualComo);
            armazem.usarBackup(id);
            carregarVersao();
            aviso("Usando a versão \"" + nomeVersao + "\".");
            avisarUsuario(null, "Agora usando \"" + nomeVersao + "\".");
        });
    }

    void renomear(String id, String nome) {
        emFundo("Renomeando…", () -> {
            armazem.renomear(id, nome);
            if (id == null) nomeVersao = nome;
        });
    }

    void apagarBackup(String id) {
        emFundo("Apagando backup…", () -> armazem.apagar(id));
    }

    void exportar(String id, Uri destino, boolean incluirIndice) {
        emFundo("Exportando…", () -> {
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

    /** Importa os arquivos de uma atualização (ou backups .zip) escolhidos no seletor. */
    void importar(List<Uri> uris) {
        emFundo("Importando…", () -> {
            List<Importador.Entrada> entradas = new ArrayList<>();
            List<String> feitos = new ArrayList<>();
            long total = 0;
            for (Uri u : uris) total += Math.max(0, tamanhoDoArquivo(ctx, u));
            if (total > 0 && ctx.getFilesDir().getUsableSpace() < total * 2 + (100L << 20)) {
                throw new IOException(String.format(Locale.getDefault(),
                        "falta espaço no celular: os arquivos têm %d MB e a importação precisa de mais ou menos o dobro",
                        total >> 20));
            }
            try {
                int i = 0;
                for (Uri u : uris) {
                    i++;
                    String nome = nomeDoArquivo(ctx, u);
                    long tam = tamanhoDoArquivo(ctx, u);
                    String titulo = (uris.size() > 1 ? "(" + i + "/" + uris.size() + ") " : "") + "Copiando " + nome + "…";
                    try (InputStream in = ctx.getContentResolver().openInputStream(u)) {
                        if (in == null) throw new IOException("não consegui abrir " + nome);
                        if (nome.toLowerCase(Locale.ROOT).endsWith(".zip")) {
                            // Backup exportado: lido direto, sem cópia temporária.
                            Armazem.Versao b = armazem.importarBackup(in, tam, progresso("Importando " + nome + "…"));
                            feitos.add("backup \"" + b.nome + "\"");
                            continue;
                        }
                        File tmp = armazem.temporario("x");
                        Armazem.copiar(in, tmp, tam, progresso(titulo));
                        entradas.add(new Importador.Entrada(tmp, nome));
                    }
                }
                tarefa("Convertendo e conferindo os arquivos…", -1);
                Importador.Resultado r = new Importador(armazem, Motor::conferirIndice).importar(entradas);
                entradas.clear();
                for (Armazem.Versao b : r.backupsImportados) feitos.add("backup \"" + b.nome + "\"");
                String nomeNovo = null;
                if (r.mudaVersao()) {
                    tarefa("Aplicando a atualização…", -1);
                    String quando = agora();
                    if (armazem.backupIgualAoAtual() == null) {
                        armazem.fazerBackup(nomeVersao + " (antes da atualização de " + quando + ")");
                    }
                    nomeNovo = "Atualização de " + quando;
                    armazem.aplicar(r.trocas, nomeNovo, r.memoria);
                    carregarVersao();
                    aviso("Atualização aplicada: " + String.join(", ", r.feitos) + ".");
                }
                StringBuilder msg = new StringBuilder();
                if (nomeNovo != null) {
                    msg.append("Agora usando \"").append(nomeNovo).append("\" com: ")
                            .append(String.join(", ", r.feitos)).append(".\n\nA versão anterior foi guardada nos backups.");
                }
                if (!feitos.isEmpty()) {
                    if (msg.length() > 0) msg.append("\n\n");
                    msg.append("Importado para a lista de backups: ").append(String.join(", ", feitos)).append('.');
                }
                if (!r.avisos.isEmpty()) msg.append("\n\nAtenção: ").append(String.join("; ", r.avisos)).append('.');
                avisarUsuario("Importação concluída", msg.length() == 0 ? "Nada para importar." : msg.toString());
            } finally {
                for (Importador.Entrada e : entradas) e.arquivo.delete();
            }
        });
    }
}
