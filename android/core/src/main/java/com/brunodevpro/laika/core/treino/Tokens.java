package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.Texto;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.nio.ByteOrder;
import java.nio.ShortBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Os textos do pré-treino já tokenizados, em disco (uint16), como o train.py monta na memória:
 * cada arquivo vira tokens + <|endoftext|>; os últimos 5% de CADA arquivo vão para a validação;
 * os textos de data/modern entram 3 vezes no treino. Lido com memória mapeada (não ocupa a RAM).
 */
public final class Tokens {
    public final ShortBuffer treino, val;
    public final int nTreino, nVal;

    private Tokens(ShortBuffer treino, ShortBuffer val) {
        this.treino = treino;
        this.val = val;
        nTreino = treino.capacity();
        nVal = val.capacity();
    }

    /** Usa os arquivos já prontos se o corpus e o tokenizer forem os mesmos; senão tokeniza tudo de novo. */
    public static Tokens preparar(List<File> arquivos, Tokenizador tok, String idTokenizer, int repetirModern, File pasta,
                                  Registro reg) throws IOException {
        pasta.mkdirs();
        File meta = new File(pasta, "tokens.json"), ft = new File(pasta, "treino.u16"), fv = new File(pasta, "val.u16");
        String assinatura = Corpus.assinatura(arquivos) + "|" + idTokenizer + "|" + repetirModern;
        if (meta.exists() && ft.exists() && fv.exists()) {
            try {
                Object m = Json.ler(new String(Files.readAllBytes(meta.toPath()), StandardCharsets.UTF_8));
                if (m instanceof Map && assinatura.equals(((Map<?, ?>) m).get("assinatura"))) {
                    Tokens t = abrir(ft, fv);
                    reg.log(String.format("Tokens já prontos: %,d de treino e %,d de validação.", t.nTreino, t.nVal));
                    return t;
                }
            } catch (RuntimeException ignorado) {
                // refaz
            }
        }
        if (tok.tamanhoVocab() > 65535) throw new IOException("vocabulário grande demais para uint16");
        meta.delete();
        int eot = tok.id(Texto.EOT);
        long total = 0, feitos = 0, nt = 0, nv = 0;
        for (File f : arquivos) total += f.length();
        tok.cacheMaximo(400_000);
        long t0 = System.currentTimeMillis();
        try (OutputStream ot = new BufferedOutputStream(new FileOutputStream(ft), 1 << 20);
             OutputStream ov = new BufferedOutputStream(new FileOutputStream(fv), 1 << 20)) {
            int i = 0;
            for (File f : arquivos) {
                if (reg.parar()) throw new Parado();
                int[] ids = tok.codificar(Corpus.lerTexto(f));
                int[] comFim = java.util.Arrays.copyOf(ids, ids.length + 1);
                comFim[ids.length] = eot;
                int corte = (int) (comFim.length * 0.95);
                int vezes = f.getParentFile().getName().equals("modern") ? Math.max(1, repetirModern) : 1;
                for (int v = 0; v < vezes; v++) nt += escrever(ot, comFim, 0, corte);
                nv += escrever(ov, comFim, corte, comFim.length);
                feitos += f.length();
                i++;
                if (i % 10 == 0 || i == arquivos.size()) {
                    double seg = (System.currentTimeMillis() - t0) / 1000.0;
                    reg.progresso((double) feitos / Math.max(1, total), String.format("Tokenizando %d/%d arquivos (%.1f MB/s)",
                            i, arquivos.size(), feitos / 1e6 / Math.max(0.1, seg)));
                }
                if (i % 100 == 0) reg.log(String.format("  tokenizados %d/%d arquivos", i, arquivos.size()));
            }
        }
        tok.cacheMaximo(50_000);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("assinatura", assinatura);
        m.put("treino", nt);
        m.put("val", nv);
        Files.write(meta.toPath(), Json.escrever(m).getBytes(StandardCharsets.UTF_8));
        Tokens t = abrir(ft, fv);
        reg.log(String.format("Tokens: %,d de treino e %,d de validação (%.0f s).", t.nTreino, t.nVal,
                (System.currentTimeMillis() - t0) / 1000.0));
        return t;
    }

    private static long escrever(OutputStream out, int[] ids, int de, int ate) throws IOException {
        byte[] b = new byte[(ate - de) * 2];
        for (int i = de, k = 0; i < ate; i++, k += 2) {
            b[k] = (byte) ids[i];
            b[k + 1] = (byte) (ids[i] >>> 8);
        }
        out.write(b);
        return ate - de;
    }

    private static Tokens abrir(File ft, File fv) throws IOException {
        return new Tokens(mapear(ft), mapear(fv));
    }

    private static ShortBuffer mapear(File f) throws IOException {
        try (RandomAccessFile r = new RandomAccessFile(f, "r"); FileChannel c = r.getChannel()) {
            return c.map(FileChannel.MapMode.READ_ONLY, 0, c.size()).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer();
        }
    }

    /** Copia T+1 tokens a partir de `inicio` (entrada = os T primeiros, alvo = os T últimos). */
    public static void janela(ShortBuffer fonte, int inicio, int T, int[] x, int[] y, int destino) {
        for (int i = 0; i < T; i++) {
            x[destino + i] = fonte.get(inicio + i) & 0xFFFF;
            y[destino + i] = fonte.get(inicio + i + 1) & 0xFFFF;
        }
    }
}
