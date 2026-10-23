package com.brunodevpro.laika.core;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

/** tokenizer.json (biblioteca tokenizers) -> tokenizer.txt do app, igual ao exportar_modelo.py. */
public final class ConversorTokenizer {
    private ConversorTokenizer() {
    }

    @SuppressWarnings("unchecked")
    public static String converter(InputStream json) throws IOException {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        byte[] b = new byte[1 << 16];
        int n;
        while ((n = json.read(b)) > 0) buf.write(b, 0, n);
        Map<String, Object> tok;
        try {
            tok = (Map<String, Object>) Json.ler(new String(buf.toByteArray(), StandardCharsets.UTF_8));
        } catch (RuntimeException e) {
            throw new IOException("tokenizer.json inválido: " + e.getMessage());
        }
        Map<String, Object> modelo = (Map<String, Object>) tok.get("model");
        Map<String, Object> pre = (Map<String, Object>) tok.get("pre_tokenizer");
        if (modelo == null || !"BPE".equals(modelo.get("type")) || pre == null || !"ByteLevel".equals(pre.get("type"))) {
            throw new IOException("o app só entende o tokenizer BPE byte-level do train.py");
        }
        Map<String, Object> vocab = (Map<String, Object>) modelo.get("vocab");
        String[] porId = new String[vocab.size()];
        for (Map.Entry<String, Object> e : vocab.entrySet()) {
            int id = ((Number) e.getValue()).intValue();
            if (id < 0 || id >= porId.length || porId[id] != null) throw new IOException("ids do vocabulário não são contínuos");
            porId[id] = e.getKey();
        }
        StringBuilder sb = new StringBuilder();
        sb.append("vocab ").append(porId.length).append('\n');
        for (String t : porId) {
            for (int i = 0; i < t.length(); i++) {
                if (Character.isWhitespace(t.charAt(i))) throw new IOException("token com espaço: " + t);
            }
            sb.append(t).append('\n');
        }
        List<Object> added = (List<Object>) tok.get("added_tokens");
        int especiais = 0;
        StringBuilder esp = new StringBuilder();
        if (added != null) {
            for (Object o : added) {
                Map<String, Object> a = (Map<String, Object>) o;
                if (Boolean.TRUE.equals(a.get("special"))) {
                    esp.append(a.get("content")).append('\n');
                    especiais++;
                }
            }
        }
        sb.append("special ").append(especiais).append('\n').append(esp);
        List<Object> merges = (List<Object>) modelo.get("merges");
        sb.append("merges ").append(merges.size()).append('\n');
        for (Object m : merges) {
            if (m instanceof List) {
                List<Object> par = (List<Object>) m;
                sb.append(par.get(0)).append(' ').append(par.get(1));
            } else {
                sb.append(m);
            }
            sb.append('\n');
        }
        return sb.toString();
    }
}
