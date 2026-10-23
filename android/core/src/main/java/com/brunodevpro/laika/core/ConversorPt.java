package com.brunodevpro.laika.core;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Converte um checkpoint do PyTorch (finetuned.pt / pretrain_best.pt) para o formato do app,
 * no próprio celular: o mesmo arquivo que o android/exportar_modelo.py gera.
 * Assim uma atualização pode ser importada direto dos arquivos do Google Drive.
 */
public final class ConversorPt {
    private ConversorPt() {
    }

    /** O que se sabe do checkpoint (vai para a descrição da versão). */
    public static final class Info {
        public int vocab, block, dim, heads, layers;
        public long parametros;
        public boolean finetuned;
        public Double valLoss;
        public Long step;
        /** false em arquivos .bin antigos, que não dizem se são de chat ou de pré-treino. */
        public boolean temRodape = true;

        public String descricao() {
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("%.1f M parâmetros · %d dim · %d camadas · contexto %d",
                    parametros / 1e6, dim, layers, block));
            if (valLoss != null) sb.append(String.format(" · val loss %.3f", valLoss));
            if (step != null) sb.append(" · step ").append(step);
            return sb.toString();
        }
    }

    private static List<String> ordem(int layers) {
        List<String> n = new ArrayList<>();
        n.add("tok_emb.weight");
        n.add("pos_emb.weight");
        for (int i = 0; i < layers; i++) {
            String p = "blocks." + i + ".";
            for (String s : new String[]{"ln1.weight", "ln1.bias", "attn.qkv.weight", "attn.proj.weight", "ln2.weight",
                    "ln2.bias", "ff.net.0.weight", "ff.net.0.bias", "ff.net.2.weight", "ff.net.2.bias"}) {
                n.add(p + s);
            }
        }
        n.add("ln_f.weight");
        n.add("ln_f.bias");
        return n;
    }

    private static int[] formaEsperada(String nome, int v, int b, int d) {
        if (nome.equals("tok_emb.weight")) return new int[]{v, d};
        if (nome.equals("pos_emb.weight")) return new int[]{b, d};
        if (nome.endsWith("attn.qkv.weight")) return new int[]{3 * d, d};
        if (nome.endsWith("attn.proj.weight")) return new int[]{d, d};
        if (nome.endsWith("ff.net.0.weight")) return new int[]{4 * d, d};
        if (nome.endsWith("ff.net.0.bias")) return new int[]{4 * d};
        if (nome.endsWith("ff.net.2.weight")) return new int[]{d, 4 * d};
        return new int[]{d};
    }

    /**
     * Lê o cabeçalho e o rodapé de um laika_*.bin sem carregar os pesos.
     * Arquivos antigos (sem rodapé) ficam sem val loss e com temRodape=false.
     */
    public static Info lerBin(InputStream in) throws IOException {
        java.io.DataInputStream d = new java.io.DataInputStream(new java.io.BufferedInputStream(in, 1 << 16));
        byte[] cab = new byte[28];
        d.readFully(cab);
        if (!new String(cab, 0, 8, "US-ASCII").equals("LAIKA001")) throw new IOException("não é um arquivo de pesos da Laika");
        ByteBuffer c = ByteBuffer.wrap(cab, 8, 20).order(ByteOrder.LITTLE_ENDIAN);
        Info i = new Info();
        i.temRodape = false;
        i.vocab = c.getInt();
        i.block = c.getInt();
        i.dim = c.getInt();
        i.heads = c.getInt();
        i.layers = c.getInt();
        i.parametros = parametros(i.vocab, i.block, i.dim, i.layers);
        long pular = i.parametros * 2;
        while (pular > 0) {
            long p = d.skip(pular);
            if (p <= 0) throw new IOException("arquivo de pesos incompleto");
            pular -= p;
        }
        byte[] rod = new byte[21];
        int lidos = 0;
        while (lidos < rod.length) {
            int n = d.read(rod, lidos, rod.length - lidos);
            if (n < 0) break;
            lidos += n;
        }
        if (lidos == rod.length && new String(rod, 0, 4, "US-ASCII").equals("INFO")) {
            ByteBuffer r = ByteBuffer.wrap(rod, 4, 17).order(ByteOrder.LITTLE_ENDIAN);
            double v = r.getDouble();
            long st = r.getLong();
            i.valLoss = Double.isNaN(v) ? null : v;
            i.step = st < 0 ? null : st;
            i.finetuned = r.get() == 1;
            i.temRodape = true;
        }
        return i;
    }

    /** Número de parâmetros do TinyLLM (sem contar a saída, que é o embedding). */
    public static long parametros(int vocab, int block, int dim, int layers) {
        long d = dim, porCamada = 2 * d + 3 * d * d + d * d + 2 * d + 4 * d * d + 4 * d + 4 * d * d + d;
        return (long) vocab * d + (long) block * d + layers * porCamada + 2 * d;
    }

    /** Só lê o cabeçalho (config, val loss...) para identificar o arquivo. */
    public static Info ler(File pt) throws IOException {
        try (ZipFile zip = new ZipFile(pt)) {
            return info(carregarDict(zip, prefixo(zip)));
        }
    }

    /** Converte e grava os pesos em `saida` (formato LAIKA001, float16). */
    @SuppressWarnings("unchecked")
    public static Info converter(File pt, OutputStream saida) throws IOException {
        try (ZipFile zip = new ZipFile(pt)) {
            String prefixo = prefixo(zip);
            Map<Object, Object> ckpt = carregarDict(zip, prefixo);
            Info info = info(ckpt);
            Map<Object, Object> estado = (Map<Object, Object>) ckpt.get("model");

            List<String> nomes = ordem(info.layers);
            Set<String> sobra = new LinkedHashSet<>();
            for (Object k : estado.keySet()) sobra.add(String.valueOf(k));
            sobra.removeAll(nomes);
            sobra.remove("head.weight");
            if (!sobra.isEmpty()) {
                throw new IOException("o modelo tem partes que este app não conhece (" + String.join(", ", sobra)
                        + "). Ele foi feito para o model.py atual (posições aprendidas, sem RoPE).");
            }
            Pickle.Tensor emb = (Pickle.Tensor) estado.get("tok_emb.weight");
            Pickle.Tensor head = (Pickle.Tensor) estado.get("head.weight");
            if (head != null && !(head.armazenamento.chave.equals(emb.armazenamento.chave)
                    && head.deslocamento == emb.deslocamento)) {
                throw new IOException("head.weight diferente de tok_emb.weight (o app espera pesos compartilhados)");
            }

            ByteBuffer cab = ByteBuffer.allocate(28).order(ByteOrder.LITTLE_ENDIAN);
            cab.put("LAIKA001".getBytes("US-ASCII"));
            cab.putInt(info.vocab).putInt(info.block).putInt(info.dim).putInt(info.heads).putInt(info.layers);
            saida.write(cab.array());

            long params = 0;
            for (String nome : nomes) {
                Pickle.Tensor t = (Pickle.Tensor) estado.get(nome);
                if (t == null) throw new IOException("falta o tensor " + nome);
                int[] esperado = formaEsperada(nome, info.vocab, info.block, info.dim);
                if (!java.util.Arrays.equals(esperado, t.forma)) {
                    throw new IOException(nome + " com forma " + java.util.Arrays.toString(t.forma)
                            + ", esperava " + java.util.Arrays.toString(esperado));
                }
                saida.write(paraMeias(zip, prefixo, t));
                params += t.numel();
            }
            info.parametros = params;
            // Rodapé igual ao do exportar_modelo.py.
            ByteBuffer rod = ByteBuffer.allocate(21).order(ByteOrder.LITTLE_ENDIAN);
            rod.put("INFO".getBytes("US-ASCII"));
            rod.putDouble(info.valLoss == null ? Double.NaN : info.valLoss);
            rod.putLong(info.step == null ? -1 : info.step);
            rod.put((byte) (info.finetuned ? 1 : 0));
            saida.write(rod.array());
            return info;
        }
    }

    private static String prefixo(ZipFile zip) throws IOException {
        Enumeration<? extends ZipEntry> e = zip.entries();
        while (e.hasMoreElements()) {
            String n = e.nextElement().getName();
            if (n.endsWith("data.pkl")) return n.substring(0, n.length() - "data.pkl".length());
        }
        throw new IOException("não é um checkpoint do PyTorch (falta data.pkl)");
    }

    @SuppressWarnings("unchecked")
    private static Map<Object, Object> carregarDict(ZipFile zip, String prefixo) throws IOException {
        Object o = Pickle.ler(lerTudo(zip, prefixo + "data.pkl"));
        if (!(o instanceof Map) || !(((Map<Object, Object>) o).get("model") instanceof Map)
                || !(((Map<Object, Object>) o).get("config") instanceof Map)) {
            throw new IOException("checkpoint sem 'model' e 'config' (não foi salvo pelo train.py/finetune.py)");
        }
        return (Map<Object, Object>) o;
    }

    @SuppressWarnings("unchecked")
    private static Info info(Map<Object, Object> ckpt) throws IOException {
        Map<Object, Object> cfg = (Map<Object, Object>) ckpt.get("config");
        Info i = new Info();
        try {
            i.vocab = ((Number) cfg.get("vocab_size")).intValue();
            i.block = ((Number) cfg.get("block_size")).intValue();
            i.dim = ((Number) cfg.get("embed_size")).intValue();
            i.heads = ((Number) cfg.get("heads")).intValue();
            i.layers = ((Number) cfg.get("layers")).intValue();
        } catch (RuntimeException e) {
            throw new IOException("config do checkpoint incompleta");
        }
        i.finetuned = Boolean.TRUE.equals(ckpt.get("finetuned"));
        if (ckpt.get("val_loss") instanceof Number) i.valLoss = ((Number) ckpt.get("val_loss")).doubleValue();
        if (ckpt.get("step") instanceof Number) i.step = ((Number) ckpt.get("step")).longValue();
        Map<Object, Object> estado = (Map<Object, Object>) ckpt.get("model");
        long n = 0;
        for (Map.Entry<Object, Object> e : estado.entrySet()) {
            if (!"head.weight".equals(e.getKey()) && e.getValue() instanceof Pickle.Tensor) {
                n += ((Pickle.Tensor) e.getValue()).numel();
            }
        }
        i.parametros = n;
        return i;
    }

    private static byte[] lerTudo(ZipFile zip, String nome) throws IOException {
        ZipEntry e = zip.getEntry(nome);
        if (e == null) throw new IOException("falta " + nome + " no checkpoint");
        try (InputStream in = zip.getInputStream(e)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream(e.getSize() > 0 ? (int) e.getSize() : 1 << 16);
            byte[] buf = new byte[1 << 16];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return out.toByteArray();
        }
    }

    /** Lê o tensor (qualquer stride, float32/16/bf16/64) e devolve os valores em float16 little-endian. */
    private static byte[] paraMeias(ZipFile zip, String prefixo, Pickle.Tensor t) throws IOException {
        ByteBuffer dados = ByteBuffer.wrap(lerTudo(zip, prefixo + "data/" + t.armazenamento.chave))
                .order(ByteOrder.LITTLE_ENDIAN);
        String tipo = t.armazenamento.tipo;
        long n = t.numel();
        ByteBuffer out = ByteBuffer.allocate((int) (n * 2)).order(ByteOrder.LITTLE_ENDIAN);
        int[] idx = new int[t.forma.length];
        for (long k = 0; k < n; k++) {
            long pos = t.deslocamento;
            for (int d = 0; d < idx.length; d++) pos += (long) idx[d] * t.passos[d];
            short h;
            switch (tipo) {
                case "FloatStorage": h = paraMeia(dados.getFloat((int) (pos * 4))); break;
                case "HalfStorage": h = dados.getShort((int) (pos * 2)); break;
                case "BFloat16Storage":
                    h = paraMeia(Float.intBitsToFloat((dados.getShort((int) (pos * 2)) & 0xFFFF) << 16));
                    break;
                case "DoubleStorage": h = paraMeia((float) dados.getDouble((int) (pos * 8))); break;
                default: throw new IOException("tipo de tensor não suportado: " + tipo);
            }
            out.putShort(h);
            for (int d = idx.length - 1; d >= 0; d--) {  // próximo índice (ordem C)
                if (++idx[d] < t.forma[d]) break;
                idx[d] = 0;
            }
        }
        return out.array();
    }

    /** float32 -> float16 com arredondamento para o par mais próximo (igual ao numpy). */
    public static short paraMeia(float f) {
        int bits = Float.floatToRawIntBits(f);
        int sinal = (bits >>> 16) & 0x8000;
        int exp = (bits >>> 23) & 0xFF;
        int mant = bits & 0x7FFFFF;
        if (exp == 0xFF) return (short) (sinal | 0x7C00 | (mant != 0 ? 0x200 : 0));
        int e = exp - 127 + 15;
        if (e >= 31) return (short) (sinal | 0x7C00);
        if (e <= 0) {
            if (e < -10) return (short) sinal;
            mant |= 0x800000;
            int desloc = 14 - e;
            int meia = mant >> desloc;
            int resto = mant & ((1 << desloc) - 1), meio = 1 << (desloc - 1);
            if (resto > meio || (resto == meio && (meia & 1) == 1)) meia++;
            return (short) (sinal | meia);
        }
        int meia = (e << 10) | (mant >> 13);
        int resto = mant & 0x1FFF;
        if (resto > 0x1000 || (resto == 0x1000 && (meia & 1) == 1)) meia++;
        return (short) (sinal | meia);
    }
}
