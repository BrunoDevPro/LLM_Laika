package com.brunodevpro.laika.core;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Os chats, como nos assistentes de conversa: cada um tem a sua conversa e a sua memória (nome, gostos,
 * "lembre que..."), e não dependem do modelo em uso. Ficam em laika/chats/&lt;id&gt;/ (chat.json, conversa.json e
 * memoria.json); chats/atual.txt guarda o chat aberto. O título vem da IA (depois da primeira resposta) até o
 * usuário renomear.
 */
public final class Chats {
    public static final String SEM_TITULO = "Novo chat";

    public static final class Chat {
        public final String id;
        public String titulo = SEM_TITULO;
        /** O usuário deu o título: a IA não troca mais. */
        public boolean tituloManual, arquivado;
        public long criado, alterado;
        final File pasta;

        Chat(String id, File pasta) {
            this.id = id;
            this.pasta = pasta;
        }

        public File conversa() {
            return new File(pasta, "conversa.json");
        }

        public File memoria() {
            return new File(pasta, "memoria.json");
        }

        /** Número de mensagens guardadas na conversa. */
        public int mensagens() {
            try {
                Object o = Json.ler(new String(Files.readAllBytes(conversa().toPath()), StandardCharsets.UTF_8));
                return o instanceof List ? ((List<?>) o).size() : 0;
            } catch (IOException | RuntimeException e) {
                return 0;
            }
        }

        /** Sem título da IA nem do usuário ainda. */
        public boolean semTitulo() {
            return !tituloManual && SEM_TITULO.equals(titulo);
        }
    }

    private final File raiz, atual;

    public Chats(File raiz) {
        this.raiz = raiz;
        raiz.mkdirs();
        atual = new File(raiz, "atual.txt");
    }

    /** Todos os chats (arquivados também), do mais recente para o mais antigo. */
    public List<Chat> lista() {
        List<Chat> r = new ArrayList<>();
        File[] pastas = raiz.listFiles(File::isDirectory);
        if (pastas != null) {
            for (File p : pastas) {
                try {
                    r.add(ler(p.getName()));
                } catch (IOException | RuntimeException e) {
                    // chat corrompido: não aparece
                }
            }
        }
        r.sort((a, b) -> Long.compare(b.alterado, a.alterado));
        return r;
    }

    public Chat ler(String id) throws IOException {
        File pasta = new File(raiz, id);
        Chat c = new Chat(id, pasta);
        @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) Json.ler(
                new String(Files.readAllBytes(new File(pasta, "chat.json").toPath()), StandardCharsets.UTF_8));
        c.titulo = m.get("titulo") instanceof String ? (String) m.get("titulo") : SEM_TITULO;
        c.tituloManual = Boolean.TRUE.equals(m.get("manual"));
        c.arquivado = Boolean.TRUE.equals(m.get("arquivado"));
        c.criado = m.get("criado") instanceof Number ? ((Number) m.get("criado")).longValue() : 0;
        c.alterado = m.get("alterado") instanceof Number ? ((Number) m.get("alterado")).longValue() : c.criado;
        return c;
    }

    public void gravar(Chat c) throws IOException {
        c.pasta.mkdirs();
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("titulo", c.titulo);
        if (c.tituloManual) m.put("manual", true);
        if (c.arquivado) m.put("arquivado", true);
        m.put("criado", c.criado);
        m.put("alterado", c.alterado);
        Armazem.escreverAtomico(new File(c.pasta, "chat.json"), Json.escrever(m).getBytes(StandardCharsets.UTF_8));
    }

    public Chat novo() throws IOException {
        String id = "c" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6);
        Chat c = new Chat(id, new File(raiz, id));
        c.criado = c.alterado = System.currentTimeMillis();
        gravar(c);
        return c;
    }

    /** Um chat com uma conversa e uma memória que já existiam (a conversa de cada versão, antes da 1.10). */
    public Chat importar(String titulo, byte[] conversa, byte[] memoria, long quando) throws IOException {
        Chat c = novo();
        c.titulo = titulo;
        c.tituloManual = true;
        c.criado = c.alterado = quando;
        if (conversa != null && conversa.length > 0) Armazem.escreverAtomico(c.conversa(), conversa);
        if (memoria != null && memoria.length > 0) Armazem.escreverAtomico(c.memoria(), memoria);
        gravar(c);
        return c;
    }

    /**
     * O chat aberto. Se o guardado sumiu (apagado), o mais recente não arquivado e vazio é reaproveitado, ou um novo
     * é criado.
     */
    public Chat atual() throws IOException {
        if (atual.exists()) {
            String id = new String(Files.readAllBytes(atual.toPath()), StandardCharsets.UTF_8).trim();
            if (!id.isEmpty() && new File(new File(raiz, id), "chat.json").exists()) {
                try {
                    return ler(id);
                } catch (IOException | RuntimeException e) {
                    // corrompido: escolhe outro
                }
            }
        }
        for (Chat c : lista()) {
            if (!c.arquivado) {
                usar(c.id);
                return c;
            }
        }
        Chat c = novo();
        usar(c.id);
        return c;
    }

    public void usar(String id) throws IOException {
        Armazem.escreverAtomico(atual, id.getBytes(StandardCharsets.UTF_8));
    }

    /** Teve mensagem nova: o chat sobe na lista. */
    public void tocar(Chat c) throws IOException {
        c.alterado = System.currentTimeMillis();
        gravar(c);
    }

    public void renomear(String id, String titulo) throws IOException {
        Chat c = ler(id);
        c.titulo = titulo;
        c.tituloManual = true;
        gravar(c);
    }

    /** O título que a IA escolheu; não mexe num título dado pelo usuário. */
    public boolean tituloDaIa(String id, String titulo) throws IOException {
        Chat c = ler(id);
        if (c.tituloManual || titulo == null || titulo.isEmpty()) return false;
        c.titulo = titulo;
        gravar(c);
        return true;
    }

    public void arquivar(String id, boolean arquivado) throws IOException {
        Chat c = ler(id);
        c.arquivado = arquivado;
        gravar(c);
    }

    public void apagar(String id) throws IOException {
        File pasta = new File(raiz, id);
        File[] fs = pasta.listFiles();
        if (fs != null) for (File f : fs) f.delete();
        if (!pasta.delete() && pasta.exists()) throw new IOException("não consegui apagar o chat");
    }

    /** Marca de que a conversa das versões antigas já virou chat (para não importar de novo). */
    public boolean migrado() {
        return new File(raiz, "migrado").exists();
    }

    public void marcarMigrado() throws IOException {
        Armazem.escreverAtomico(new File(raiz, "migrado"), new byte[0]);
    }
}
