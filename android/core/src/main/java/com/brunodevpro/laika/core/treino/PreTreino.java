package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.Texto;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * O train.py no celular: (tokenizer novo se for do zero) -> tokens em disco -> pré-treino na
 * GPU com validação, early stopping, cosseno com aquecimento, AdamW e corte do gradiente.
 * Salva o melhor em saida/laika_base.bin e, a cada validação, o estado completo (pesos,
 * momentos do Adam, passo, gerador) para continuar de onde parou se o app for fechado.
 */
public final class PreTreino {
    public enum Modo {
        /** Tokenizer e pesos novos (o "do_zero" do Colab). */
        DO_ZERO,
        /** Continua do modelo base em uso, com otimizador novo (o "continuar" / --resume do Colab). */
        CONTINUAR,
        /** Retoma um treino interrompido aqui no celular, do passo onde parou. */
        RETOMAR
    }

    public static final class Opcoes {
        public Modo modo = Modo.CONTINUAR;
        /** Para testes: sobrescreve eval_every / eval_iters do preset (0 = o do preset). */
        public int evalEvery = 0, evalIters = 0;
        public String preset = "colab";
        public int maxSteps = 0;          // 0 = o do preset
        public int microLote = 8;
        public long maxBytesTokenizer = 80L << 20;
        public int repetirModern = 3;
        /** Para CONTINUAR: o laika_base.bin e o tokenizer.txt da versão em uso. */
        public InputStream baseAtual, tokenizerAtual;
        public long semente = 1337;
    }

    private PreTreino() {
    }

    public static File estadoJson(File pasta) {
        return new File(pasta, "pretreino/estado.json");
    }

    /** Descrição do treino interrompido (para o botão "Retomar"), ou null. */
    public static String interrompido(File pasta) {
        File f = estadoJson(pasta);
        if (!f.exists()) return null;
        try {
            Map<?, ?> m = (Map<?, ?>) Json.ler(Corpus.lerTexto(f));
            return String.format(Locale.getDefault(), "preset %s, passo %d de %d, melhor val loss %.3f",
                    m.get("preset"), ((Number) m.get("passo")).intValue(), ((Number) m.get("maxSteps")).intValue(),
                    ((Number) m.get("melhorVal")).doubleValue());
        } catch (Exception e) {
            return null;
        }
    }

    @SuppressWarnings("unchecked")
    public static void rodar(Gl gl, Corpus corpus, File pasta, Opcoes op, Registro reg) throws IOException {
        File saida = new File(pasta, "saida"), estadoDir = new File(pasta, "pretreino");
        saida.mkdirs();
        estadoDir.mkdirs();
        reg.log("GPU: " + gl.descricao());

        Map<String, Object> estado = null;
        if (op.modo == Modo.RETOMAR) {
            if (!estadoJson(pasta).exists()) throw new IOException("não há treino interrompido para retomar");
            estado = (Map<String, Object>) Json.ler(Corpus.lerTexto(estadoJson(pasta)));
            op.preset = (String) estado.get("preset");
            op.maxSteps = ((Number) estado.get("maxSteps")).intValue();
            op.microLote = ((Number) estado.get("microLote")).intValue();
        }
        Presets.Preset ps = Presets.TODOS.get(op.preset);
        if (ps == null) throw new IOException("preset desconhecido: " + op.preset);
        int maxSteps = op.maxSteps > 0 ? op.maxSteps : ps.maxSteps;
        int evalEvery = op.evalEvery > 0 ? op.evalEvery : ps.evalEvery, evalIters = op.evalIters > 0 ? op.evalIters : ps.evalIters;
        List<File> arquivos = corpus.preTreino();
        if (arquivos.isEmpty()) throw new IOException("não há textos para o pré-treino (importe o pacote de dados)");
        long bytes = corpus.bytes(arquivos);
        reg.log(String.format("Textos: %d arquivos (%.1f MB).", arquivos.size(), bytes / 1e6));

        // ---------- tokenizer ----------
        File tokFile = new File(saida, "tokenizer.txt");
        String tokTexto;
        if (op.modo == Modo.DO_ZERO) {
            reg.log("Treinando o tokenizer (BPE byte-level, vocabulário " + ps.vocab + ")...");
            List<File> paraTok = new java.util.ArrayList<>(arquivos);
            paraTok.addAll(corpus.txt("qa"));
            if (corpus.bytes(paraTok) > op.maxBytesTokenizer) {
                // Amostra variada: embaralha (sempre igual) e mantém as perguntas escritas à mão.
                java.util.List<File> livros = new java.util.ArrayList<>(arquivos);
                new Aleatorio(op.semente).embaralhar(livros);
                paraTok = new java.util.ArrayList<>(corpus.txt("qa"));
                paraTok.addAll(corpus.txt("modern"));
                paraTok.addAll(livros);
            }
            tokTexto = TreinadorBpe.treinar(paraTok, ps.vocab, Arrays.asList(Texto.PAD, "[UNK]", Texto.USER,
                    Texto.ASSISTANT, Texto.END, Texto.EOT), op.maxBytesTokenizer, reg);
            Files.write(tokFile.toPath(), tokTexto.getBytes(StandardCharsets.UTF_8));
        } else if (op.modo == Modo.RETOMAR) {
            tokTexto = Corpus.lerTexto(tokFile);
        } else {
            tokTexto = new String(Corpus.lerTudo(op.tokenizerAtual), StandardCharsets.UTF_8);
            Files.write(tokFile.toPath(), tokTexto.getBytes(StandardCharsets.UTF_8));
        }
        Tokenizador tok = new Tokenizador(new ByteArrayInputStream(tokTexto.getBytes(StandardCharsets.UTF_8)));
        String idTok = Integer.toHexString(tokTexto.hashCode()) + "-" + tokTexto.length();

        // ---------- tokens ----------
        reg.log("Tokenizando os textos...");
        Tokens tk = Tokens.preparar(arquivos, tok, idTok, op.repetirModern, new File(pasta, "tokens"), reg);
        int block;
        Rede.Config cfg;
        float[] pesosIniciais = null;
        if (op.modo == Modo.CONTINUAR) {
            Rede.Config[] c = new Rede.Config[1];
            pesosIniciais = Pesos.ler(op.baseAtual, ps.dropout, c);
            cfg = c[0];
            if (cfg.vocab != tok.tamanhoVocab()) throw new IOException("o modelo base não combina com o tokenizer");
            if (cfg.dim != ps.dim || cfg.layers != ps.layers || cfg.heads != ps.heads || cfg.block != ps.block) {
                throw new IOException(String.format("o modelo em uso tem %d dim, %d camadas e contexto %d, diferente do "
                        + "preset %s. Escolha o preset do mesmo tamanho ou treine do zero.", cfg.dim, cfg.layers, cfg.block, ps.nome));
            }
        } else {
            cfg = new Rede.Config(tok.tamanhoVocab(), ps.block, ps.dim, ps.heads, ps.layers, ps.dropout);
        }
        block = cfg.block;
        if (tk.nTreino < block * 100 || tk.nVal < block * 10) {
            throw new IOException(String.format("poucos dados (%,d tokens). Importe mais livros/artigos.", tk.nTreino));
        }
        int micro = Math.max(1, Math.min(op.microLote, ps.batch));
        while (ps.batch % micro != 0) micro--;
        int passosMicro = ps.batch / micro;

        try (Rede rede = new Rede(gl, cfg, micro)) {
            reg.log(String.format("Tokens: %,d | Parâmetros: %,d | tokens/parâmetro: %.1f (ideal ≈ 20)", tk.nTreino,
                    rede.nParametros, (double) tk.nTreino / rede.nParametros));
            reg.log(String.format("Lote: %d sequências de %d tokens = %d micro-lotes de %d (memória da GPU ≈ %d MB)",
                    ps.batch, block, passosMicro, micro, Rede.memoriaNecessaria(cfg, micro) >> 20));
            Aleatorio rng = new Aleatorio(op.semente);
            int passoInicial = 0, semMelhora = 0;
            double melhorVal = Double.POSITIVE_INFINITY;
            if (estado != null) {
                rede.carregar(lerF32(new File(estadoDir, "pesos.f32"), rede.nParametros));
                rede.carregarAdam(lerF32(new File(estadoDir, "m.f32"), rede.nParametros),
                        lerF32(new File(estadoDir, "v.f32"), rede.nParametros));
                passoInicial = ((Number) estado.get("passo")).intValue();
                semMelhora = ((Number) estado.get("semMelhora")).intValue();
                melhorVal = ((Number) estado.get("melhorVal")).doubleValue();
                rng.estado = Long.parseLong((String) estado.get("rng"));
                reg.log(String.format("Retomando do passo %d (melhor val loss %.4f).", passoInicial, melhorVal));
            } else if (pesosIniciais != null) {
                rede.carregar(pesosIniciais);
                reg.log("Pesos carregados do modelo base em uso (otimizador novo, como o --resume).");
            } else {
                rede.inicializar(op.semente);
            }

            int[] x = new int[micro * block], y = new int[micro * block];
            long inicio = System.currentTimeMillis();
            long tokensDesdeLog = 0, tLog = System.nanoTime();
            float escala = 1f / (ps.batch * block);
            int step = passoInicial;
            for (; step <= maxSteps; step++) {
                if ((step % evalEvery == 0 || step == maxSteps) && (estado == null || step != passoInicial)) {
                    double val = avaliar(rede, tk, rng, ps, evalIters, micro, block, x, y, reg);
                    String marca = "";
                    if (val < melhorVal) {
                        melhorVal = val;
                        semMelhora = 0;
                        marca = "  <- melhor, salvo";
                        Pesos.salvar(new File(saida, "laika_base.bin"), cfg, rede.pesos(), val, step, false);
                    } else {
                        semMelhora++;
                    }
                    reg.log(String.format(Locale.US, "step %6d | val loss %.4f (ppl %.0f) | %.0fs%s", step, val, Math.exp(val),
                            (System.currentTimeMillis() - inicio) / 1000.0, marca));
                    salvarEstado(estadoDir, rede, op, ps, maxSteps, micro, step, semMelhora, melhorVal, rng);
                    if (semMelhora >= ps.patience) {
                        reg.log("Early stopping: a validação parou de melhorar.");
                        break;
                    }
                    if (step == maxSteps) break;
                }
                if (reg.parar()) {
                    salvarEstado(estadoDir, rede, op, ps, maxSteps, micro, step, semMelhora, melhorVal, rng);
                    reg.log("Parado no passo " + step + ". Use \"Retomar\" para continuar daqui.");
                    throw new Parado();
                }
                float lr = Presets.taxa(step, ps.lr, ps.warmup, maxSteps);
                rede.zerarGradientes();
                double perda = 0;
                for (int u = 0; u < passosMicro; u++) {
                    for (int b = 0; b < micro; b++) {
                        Tokens.janela(tk.treino, rng.inteiro(tk.nTreino - block - 1), block, x, y, b * block);
                    }
                    for (float p : rede.microPasso(x, y, micro, block, true, escala, (int) rng.proximo())) perda += p;
                }
                rede.otimizar(lr, 0.1f, 0f, 0.9f, 0.95f, 1e-8f, 1f, step - passoInicial + 1 + passosOtimizador(estado));
                tokensDesdeLog += (long) ps.batch * block;
                if (step % 100 == 0) {
                    reg.log(String.format(Locale.US, "step %6d | train loss %.4f", step, perda / (ps.batch * block)));
                }
                double seg = (System.nanoTime() - tLog) / 1e9;
                if (seg > 3) {
                    double tps = tokensDesdeLog / seg;
                    double faltam = (maxSteps - step) * (double) ps.batch * block / Math.max(1, tps);
                    reg.progresso((double) step / maxSteps, String.format(Locale.getDefault(),
                            "Pré-treino: passo %d/%d · %.0f tokens/s · faltam ~%s", step, maxSteps, tps, duracao(faltam)));
                    tokensDesdeLog = 0;
                    tLog = System.nanoTime();
                }
            }
            new File(estadoDir, "pesos.f32").delete();
            new File(estadoDir, "m.f32").delete();
            new File(estadoDir, "v.f32").delete();
            estadoJson(pasta).delete();
            reg.log(String.format("Pré-treino concluído. Melhor val loss: %.4f -> saida/laika_base.bin", melhorVal));
            reg.log("Referência: val loss > 4.5 = ainda não aprendeu gramática; < 3.5 = frases já fazem sentido.");
        }
    }

    /** Passos do Adam já dados antes de retomar (para a correção de viés continuar certa). */
    private static int passosOtimizador(Map<String, Object> estado) {
        return estado == null ? 0 : ((Number) estado.get("passoAdam")).intValue();
    }

    static String duracao(double seg) {
        if (seg < 90) return String.format(Locale.getDefault(), "%.0f s", seg);
        if (seg < 5400) return String.format(Locale.getDefault(), "%.0f min", seg / 60);
        return String.format(Locale.getDefault(), "%.1f h", seg / 3600);
    }

    private static double avaliar(Rede rede, Tokens tk, Aleatorio rng, Presets.Preset ps, int evalIters, int micro, int block, int[] x, int[] y,
                                  Registro reg) {
        double soma = 0;
        for (int it = 0; it < evalIters; it++) {
            double lote = 0;
            for (int u = 0; u < ps.batch / micro; u++) {
                for (int b = 0; b < micro; b++) Tokens.janela(tk.val, rng.inteiro(tk.nVal - block - 1), block, x, y, b * block);
                for (float p : rede.microPasso(x, y, micro, block, false, 1f, 0)) lote += p;
            }
            soma += lote / (ps.batch * block);
            if (reg.parar()) break;
        }
        return soma / evalIters;
    }

    private static void salvarEstado(File dir, Rede rede, Opcoes op, Presets.Preset ps, int maxSteps, int micro, int passo,
                                     int semMelhora, double melhorVal, Aleatorio rng) throws IOException {
        escreverF32(new File(dir, "pesos.f32"), rede.pesos());
        float[][] mv = rede.estadoAdam();
        escreverF32(new File(dir, "m.f32"), mv[0]);
        escreverF32(new File(dir, "v.f32"), mv[1]);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("preset", ps.nome);
        m.put("maxSteps", maxSteps);
        m.put("microLote", micro);
        m.put("passo", passo);
        m.put("passoAdam", passo);
        m.put("semMelhora", semMelhora);
        m.put("melhorVal", Double.isInfinite(melhorVal) ? 1e9 : melhorVal);
        m.put("rng", Long.toString(rng.estado));
        m.put("modoOriginal", op.modo.name());
        File j = estadoJson(dir.getParentFile());
        File tmp = new File(j.getPath() + ".tmp");
        Files.write(tmp.toPath(), Json.escrever(m).getBytes(StandardCharsets.UTF_8));
        j.delete();
        tmp.renameTo(j);
    }

    static void escreverF32(File f, float[] v) throws IOException {
        File tmp = new File(f.getPath() + ".tmp");
        try (RandomAccessFile r = new RandomAccessFile(tmp, "rw"); FileChannel c = r.getChannel()) {
            ByteBuffer b = ByteBuffer.allocate(1 << 20).order(ByteOrder.LITTLE_ENDIAN);
            for (float x : v) {
                if (!b.hasRemaining()) {
                    b.flip();
                    c.write(b);
                    b.clear();
                }
                b.putFloat(x);
            }
            b.flip();
            c.write(b);
        }
        f.delete();
        if (!tmp.renameTo(f)) throw new IOException("não consegui salvar " + f.getName());
    }

    static float[] lerF32(File f, int n) throws IOException {
        float[] v = new float[n];
        try (InputStream in = new FileInputStream(f)) {
            byte[] buf = new byte[1 << 20];
            int i = 0;
            while (i < n) {
                int quer = Math.min(buf.length, (n - i) * 4);
                int lidos = 0;
                while (lidos < quer) {
                    int r = in.read(buf, lidos, quer - lidos);
                    if (r < 0) throw new IOException("estado do treino incompleto");
                    lidos += r;
                }
                ByteBuffer b = ByteBuffer.wrap(buf, 0, lidos).order(ByteOrder.LITTLE_ENDIAN);
                while (b.hasRemaining()) v[i++] = b.getFloat();
            }
        }
        return v;
    }
}
