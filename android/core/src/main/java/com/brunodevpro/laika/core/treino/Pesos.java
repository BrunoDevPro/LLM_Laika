package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.ConversorPt;
import com.brunodevpro.laika.core.Modelo;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/** Converte os pesos da GPU (float32) para o laika_*.bin do app (float16 + rodapé) e de volta. */
public final class Pesos {
    private Pesos() {
    }

    /** Grava no mesmo formato do exportar_modelo.py (rodapé com val loss, step e se é de chat). */
    public static void salvar(File destino, Rede.Config c, float[] pesos, double valLoss, long step, boolean chat)
            throws IOException {
        File tmp = new File(destino.getPath() + ".tmp");
        try (OutputStream out = new BufferedOutputStream(new FileOutputStream(tmp), 1 << 16)) {
            ByteBuffer cab = ByteBuffer.allocate(28).order(ByteOrder.LITTLE_ENDIAN);
            cab.put("LAIKA001".getBytes("US-ASCII"));
            cab.putInt(c.vocab).putInt(c.block).putInt(c.dim).putInt(c.heads).putInt(c.layers);
            out.write(cab.array());
            ByteBuffer b = ByteBuffer.allocate(1 << 16).order(ByteOrder.LITTLE_ENDIAN);
            for (float p : pesos) {
                if (!b.hasRemaining()) {
                    out.write(b.array(), 0, b.position());
                    b.clear();
                }
                b.putShort(ConversorPt.paraMeia(p));
            }
            out.write(b.array(), 0, b.position());
            ByteBuffer rod = ByteBuffer.allocate(21).order(ByteOrder.LITTLE_ENDIAN);
            rod.put("INFO".getBytes("US-ASCII"));
            rod.putDouble(valLoss);
            rod.putLong(step);
            rod.put((byte) (chat ? 1 : 0));
            out.write(rod.array());
        }
        if (destino.exists() && !destino.delete()) throw new IOException("não consegui trocar " + destino.getName());
        if (!tmp.renameTo(destino)) throw new IOException("não consegui salvar " + destino.getName());
    }

    /** Lê um laika_*.bin: devolve a config (dropout dado) e os pesos em float32. */
    public static float[] ler(InputStream in, float dropout, Rede.Config[] config) throws IOException {
        DataInputStream d = new DataInputStream(new BufferedInputStream(in, 1 << 16));
        byte[] cab = new byte[28];
        d.readFully(cab);
        if (!new String(cab, 0, 8, "US-ASCII").equals("LAIKA001")) throw new IOException("não é um laika_*.bin");
        ByteBuffer c = ByteBuffer.wrap(cab, 8, 20).order(ByteOrder.LITTLE_ENDIAN);
        Rede.Config cfg = new Rede.Config(c.getInt(), c.getInt(), c.getInt(), c.getInt(), c.getInt(), dropout);
        config[0] = cfg;
        long n = ConversorPt.parametros(cfg.vocab, cfg.block, cfg.dim, cfg.layers);
        float[] p = new float[(int) n];
        byte[] buf = new byte[1 << 16];
        int i = 0;
        while (i < n) {
            int quer = (int) Math.min(buf.length, (n - i) * 2);
            d.readFully(buf, 0, quer);
            ByteBuffer bb = ByteBuffer.wrap(buf, 0, quer).order(ByteOrder.LITTLE_ENDIAN);
            while (bb.hasRemaining()) p[i++] = Modelo.meiaParaFloat(bb.getShort());
        }
        return p;
    }

    public static float[] ler(File f, float dropout, Rede.Config[] config) throws IOException {
        try (InputStream in = new FileInputStream(f)) {
            return ler(in, dropout, config);
        }
    }
}
