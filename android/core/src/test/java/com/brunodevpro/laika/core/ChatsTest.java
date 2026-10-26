package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

/** Os chats (conversa e memória de cada um) e o título que a IA dá. */
class ChatsTest {
    @TempDir
    File tmp;

    @Test
    void criarAbrirRenomearArquivarApagar() throws Exception {
        Chats chats = new Chats(new File(tmp, "chats"));
        Chats.Chat a = chats.atual();  // sem nenhum: cria um
        assertTrue(a.semTitulo());
        assertEquals(a.id, chats.atual().id);
        Files.writeString(a.conversa().toPath(), "[{\"u\": true, \"t\": \"oi\"}, {\"u\": false, \"t\": \"olá\"}]");
        assertEquals(2, chats.ler(a.id).mensagens());

        Thread.sleep(5);
        Chats.Chat b = chats.novo();
        chats.usar(b.id);
        assertEquals(b.id, chats.atual().id);
        assertEquals(b.id, chats.lista().get(0).id);
        Thread.sleep(5);
        chats.tocar(chats.ler(a.id));  // mensagem nova em a: sobe na lista
        assertEquals(a.id, chats.lista().get(0).id);

        assertTrue(chats.tituloDaIa(a.id, "Saudações"));
        assertEquals("Saudações", chats.ler(a.id).titulo);
        chats.renomear(a.id, "Meu chat");
        assertFalse(chats.tituloDaIa(a.id, "Outro"));  // o título do usuário fica
        assertEquals("Meu chat", chats.ler(a.id).titulo);

        chats.arquivar(a.id, true);
        assertTrue(chats.ler(a.id).arquivado);
        chats.apagar(b.id);
        // O aberto foi apagado: abre o mais recente não arquivado, ou um novo.
        Chats.Chat c = chats.atual();
        assertNotEquals(b.id, c.id);
        assertNotEquals(a.id, c.id);
        assertEquals(2, chats.lista().size());
    }

    @Test
    void importarDasVersoesAntigas() throws Exception {
        Chats chats = new Chats(new File(tmp, "chats"));
        assertFalse(chats.migrado());
        Chats.Chat c = chats.importar("Conversa de Laika 7M", "[{\"u\": true, \"t\": \"oi\"}]".getBytes(StandardCharsets.UTF_8),
                "{\"nome\": \"Ana\", \"notas\": []}".getBytes(StandardCharsets.UTF_8), 1000);
        chats.marcarMigrado();
        assertTrue(chats.migrado());
        Chats.Chat lido = chats.ler(c.id);
        assertEquals("Conversa de Laika 7M", lido.titulo);
        assertTrue(lido.tituloManual);
        assertEquals(1, lido.mensagens());
        assertTrue(new Memoria(lido.memoria()).resumo().contains("Ana"));
        List<Chats.Chat> l = chats.lista();
        assertEquals(1, l.size());
    }

    @Test
    void tituloDaIa() {
        assertEquals("Capital da França", Texto.limparTitulo(" \"Capital da França.\"\nMais texto", "Qual é a capital da França?"));
        assertEquals("Vulcões", Texto.limparTitulo("vulcões", "O que é um vulcão?"));
        // Vazio, pergunta ou frase longa: usa o começo da mensagem do usuário.
        assertEquals("Qual é a capital da França", Texto.limparTitulo("", "qual é a capital da França?"));
        assertEquals("O que é um vulcão", Texto.limparTitulo("Você quer saber o que é um vulcão?", "O que é um vulcão?"));
        String longa = Texto.limparTitulo("um dois três quatro cinco seis sete oito",
                "Me explique com detalhes como funcionam os vulcões e por que eles entram em erupção");
        assertTrue(longa.endsWith("…") && longa.length() <= 41, longa);
        assertEquals(Chats.SEM_TITULO, Texto.limparTitulo(null, ""));
    }
}
