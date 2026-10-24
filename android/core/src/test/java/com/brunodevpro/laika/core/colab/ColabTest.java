package com.brunodevpro.laika.core.colab;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import com.brunodevpro.laika.core.Json;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** O leitor do colab.ipynb (igual ao do laika_colab.py) e o cliente do GitHub contra um servidor falso. */
class ColabTest {
    static File repo = new File(System.getProperty("laika.repo", "../.."));

    @TempDir
    File tmp;
    HttpServer srv;
    String base;
    final Map<String, String> recebido = new ConcurrentHashMap<>();
    final List<String> tokens = new ArrayList<>();

    static String caderno() throws IOException {
        return new String(Files.readAllBytes(new File(repo, "colab.ipynb").toPath()), StandardCharsets.UTF_8);
    }

    // ---------- caderno ----------

    @Test
    void celulasDoNotebook() throws IOException {
        List<Caderno.Celula> cs = Caderno.ler(caderno());
        assertEquals(8, cs.size());
        Caderno.Celula c3 = cs.get(3);
        assertEquals(3, c3.numero);
        assertEquals("PRÉ-TREINO", c3.nome);
        assertFalse(c3.soNavegador);
        Caderno.Parametro modo = c3.parametro("MODO");
        assertEquals("opcoes", modo.tipo);
        assertEquals("pular", modo.padrao);
        assertEquals(List.of("pular", "continuar", "do_zero"), modo.opcoes);
        assertEquals("integer", c3.parametro("PASSOS").tipo);
        assertEquals(0L, c3.parametro("PASSOS").padrao);
        assertTrue(cs.get(0).soNavegador && cs.get(5).soNavegador);
        assertEquals(Boolean.TRUE, cs.get(4).parametro("USAR_RAG").padrao);
        assertEquals("true", Caderno.textoDoPadrao(cs.get(4).parametro("USAR_RAG")));
        assertEquals(3L, Caderno.converter(cs.get(4).parametro("EPOCAS"), " 3 "));
        assertEquals("do_zero", Caderno.converter(modo, "do_zero"));
        assertThrows(IllegalArgumentException.class, () -> Caderno.converter(modo, "xyz"));
        assertThrows(IllegalArgumentException.class, () -> Caderno.converter(c3.parametro("PASSOS"), "dois"));
        assertEquals(Boolean.FALSE, Caderno.converter(cs.get(4).parametro("USAR_RAG"), "não"));
    }

    /** O app e o laika_colab.py (que roda no GitHub) precisam ver as mesmas células e parâmetros. */
    @Test
    @SuppressWarnings("unchecked")
    void igualAoPython() throws Exception {
        File script = new File(repo, "colab/laika_colab.py");
        Process p;
        try {
            p = new ProcessBuilder("python3", script.getPath(), "celulas").redirectErrorStream(true).start();
        } catch (IOException semPython) {
            assumeTrue(false, "python3 não encontrado");
            return;
        }
        String saida = new String(p.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        assertTrue(p.waitFor(60, TimeUnit.SECONDS));
        assertEquals(0, p.exitValue(), saida);
        List<Object> py = (List<Object>) Json.ler(saida);
        List<Caderno.Celula> java = Caderno.ler(caderno());
        assertEquals(py.size(), java.size());
        for (int i = 0; i < py.size(); i++) {
            Map<String, Object> c = (Map<String, Object>) py.get(i);
            Caderno.Celula j = java.get(i);
            assertEquals(((Number) c.get("numero")).intValue(), j.numero);
            assertEquals(c.get("nome"), j.nome);
            assertEquals(c.get("titulo"), j.titulo);
            assertEquals(c.get("descricao"), j.descricao);
            assertEquals(c.get("so_navegador"), j.soNavegador);
            List<Object> ps = (List<Object>) c.get("parametros");
            assertEquals(ps.size(), j.parametros.size());
            for (int k = 0; k < ps.size(); k++) {
                Map<String, Object> pp = (Map<String, Object>) ps.get(k);
                Caderno.Parametro jp = j.parametros.get(k);
                assertEquals(pp.get("nome"), jp.nome);
                assertEquals(pp.get("tipo"), jp.tipo);
                Object padrao = pp.get("padrao");
                // Números com vírgula (RAG_FRACAO = 0.7) ficam Double; os inteiros, Long.
                Object esperado = !(padrao instanceof Number) ? padrao : jp.padrao instanceof Double
                        ? (Object) ((Number) padrao).doubleValue() : (Object) ((Number) padrao).longValue();
                assertEquals(esperado, jp.padrao);
                if (pp.containsKey("opcoes")) assertEquals(pp.get("opcoes"), jp.opcoes);
            }
        }
    }

    // ---------- GitHub falso ----------

    void responder(HttpExchange t, int codigo, String corpo) throws IOException {
        byte[] b = corpo.getBytes(StandardCharsets.UTF_8);
        t.getResponseHeaders().add("Content-Type", "application/json");
        t.sendResponseHeaders(codigo, b.length == 0 ? -1 : b.length);
        if (b.length > 0) {
            try (OutputStream o = t.getResponseBody()) {
                o.write(b);
            }
        }
        t.close();
    }

    @BeforeEach
    void ligar() throws IOException {
        srv = HttpServer.create(new InetSocketAddress(0), 0);
        int porta = srv.getAddress().getPort();
        base = "http://127.0.0.1:" + porta;
        String r = "/repos/dono/repo";
        srv.createContext("/", t -> {
            String caminho = t.getRequestURI().getPath(), query = t.getRequestURI().getRawQuery();
            String auth = t.getRequestHeaders().getFirst("Authorization");
            synchronized (tokens) {
                tokens.add(caminho + " " + auth);
            }
            String corpo = new String(t.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            if (caminho.startsWith("/blob/")) {  // outro "servidor": não pode receber o token
                responder(t, auth == null ? 200 : 400, "conteudo-do-zip");
                return;
            }
            boolean verificacoes = caminho.startsWith(r + "/commits/");
            if (verificacoes && "Bearer tok-sem-checks".equals(auth)) {
                responder(t, 403, "{\"message\": \"Resource not accessible by personal access token\"}");
                return;
            }
            if (!"Bearer tok".equals(auth) && !(verificacoes && auth == null)) {  // repositório público: lê sem token
                responder(t, 401, "{\"message\": \"Bad credentials\"}");
                return;
            }
            String m = t.getRequestMethod();
            if (caminho.equals(r) && m.equals("GET")) responder(t, 200, "{\"default_branch\": \"main\"}");
            else if (caminho.equals(r + "/actions/workflows/colab.yml")) responder(t, 200, "{\"id\": 1}");
            else if (caminho.equals(r + "/contents/colab.ipynb")) {
                assertEquals("application/vnd.github.raw+json", t.getRequestHeaders().getFirst("Accept"));
                assertEquals("ref=meu-ramo", query);
                responder(t, 200, caderno());
            } else if (caminho.equals(r + "/actions/workflows/colab.yml/dispatches") && m.equals("POST")) {
                recebido.put("disparo", corpo);
                responder(t, 200, "{\"workflow_run_id\": 12345678901, \"run_url\": \"x\", \"html_url\": \"y\"}");
            } else if (caminho.equals(r + "/actions/workflows/sinal.yml/dispatches") && m.equals("POST")) {
                recebido.put("sinal", corpo);
                responder(t, 204, "");
            } else if (caminho.equals(r + "/actions/workflows/colab.yml/runs")) {
                responder(t, 200, "{\"workflow_runs\": [{\"id\": 5, \"display_title\": \"Colab: células 4 (T4) #outro\"},"
                        + "{\"id\": 12345678901, \"display_title\": \"Colab: células 4,6 (T4) #ab12cd\", \"status\": \"in_progress\","
                        + "\"head_sha\": \"abc\", \"created_at\": \"2026-10-23T12:00:00Z\"}]}");
            } else if (caminho.equals(r + "/actions/runs/12345678901")) {
                responder(t, 200, "{\"id\": 12345678901, \"status\": \"completed\", \"conclusion\": \"success\", \"head_sha\": \"abc\"}");
            } else if (caminho.equals(r + "/actions/runs/12345678901/cancel") && m.equals("POST")) {
                recebido.put("cancelar", "sim");
                responder(t, 202, "{}");
            } else if (caminho.equals(r + "/actions/runs/12345678901/jobs")) {
                responder(t, 200, "{\"jobs\": [{\"id\": 9, \"steps\": [{\"name\": \"Instalar o Colab CLI\", \"status\": \"completed\","
                        + "\"conclusion\": \"success\"}, {\"name\": \"Rodar as células no Colab\", \"status\": \"in_progress\"}]}]}");
            } else if (caminho.equals(r + "/actions/jobs/9/logs")) {
                t.getResponseHeaders().add("Location", "http://localhost:" + porta + "/blob/log");
                responder(t, 302, "");
            } else if (caminho.equals(r + "/commits/abc/check-runs")) {
                assertTrue(query.contains("check_name=Laika+no+Colab") && query.contains("filter=all"), query);
                String dados = "{\\\"fase\\\": \\\"autorizar\\\", \\\"autorizar\\\": \\\"https://accounts.google.com/x?state=1\\\","
                        + "\\\"celulas\\\": [{\\\"numero\\\": 1, \\\"nome\\\": \\\"PREPARAR\\\", \\\"situacao\\\": \\\"ok\\\"}]}";
                responder(t, 200, "{\"check_runs\": [{\"external_id\": \"999\", \"output\": {\"title\": \"outra\"}},"
                        + "{\"external_id\": \"12345678901\", \"status\": \"in_progress\", \"output\": {\"title\": \"Montando o Drive\","
                        + "\"summary\": \"**x**\\n<!-- laika " + dados + " -->\", \"text\": \"```\\nlinha 1\\nlinha 2\\n```\"}}]}");
            } else if (caminho.equals(r + "/actions/artifacts")) {
                assertEquals("name=laika_pacote&per_page=30", query);
                responder(t, 200, "{\"artifacts\": [{\"id\": 77, \"name\": \"laika_pacote\", \"size_in_bytes\": 15,"
                        + "\"expired\": false, \"created_at\": \"2026-10-23T13:00:00Z\", \"workflow_run\": {\"id\": 12345678901}}]}");
            } else if (caminho.equals(r + "/actions/artifacts/77/zip")) {
                t.getResponseHeaders().add("Location", "http://localhost:" + porta + "/blob/77?sig=1");
                responder(t, 302, "");
            } else {
                responder(t, 404, "{\"message\": \"Not Found\"}");
            }
        });
        srv.start();
    }

    @AfterEach
    void desligar() {
        srv.stop(0);
    }

    @Test
    @SuppressWarnings("unchecked")
    void disparoAcompanhamentoEDownload() throws Exception {
        GitHub g = new GitHub(base, "dono/repo", "tok");
        assertEquals("main", g.ramoPrincipal());
        assertTrue(g.temWorkflow());
        assertEquals(8, Caderno.ler(g.caderno("meu-ramo")).size());

        long id = g.disparar("main", "4,6", "T4", "{\"4\": {\"EPOCAS\": 3}}", "#ab12cd");
        assertEquals(12345678901L, id);
        Map<String, Object> d = (Map<String, Object>) Json.ler(recebido.get("disparo"));
        assertEquals("main", d.get("ref"));
        assertEquals(Boolean.TRUE, d.get("return_run_details"));
        Map<String, Object> in = (Map<String, Object>) d.get("inputs");
        assertEquals("4,6", in.get("celulas"));
        assertEquals("{\"4\": {\"EPOCAS\": 3}}", in.get("parametros"));  // texto: os inputs do workflow são strings

        GitHub.Execucao e = g.acharPedido("#ab12cd");
        assertEquals(12345678901L, e.id);
        assertEquals("abc", e.sha);
        assertTrue(e.criada > 0);
        assertNull(g.acharPedido("#naoexiste"));
        assertTrue(g.execucao(id).deuCerto());
        assertEquals(2, g.passos(id).size());

        GitHub.Verificacao v = g.verificacao(e);
        assertEquals("Montando o Drive", v.titulo);
        assertEquals("linha 1\nlinha 2", v.texto);
        assertEquals("https://accounts.google.com/x?state=1", v.autorizar());
        assertEquals("PREPARAR", v.celulas().get(0).get("nome"));

        // token sem a permissão Checks: a verificação é lida sem token (repositório público)
        GitHub.Verificacao v2 = new GitHub(base, "dono/repo", "tok-sem-checks").verificacao(e);
        assertEquals("Montando o Drive", v2.titulo);

        g.avisarDriveAutorizado("main", id);
        Map<String, Object> s = (Map<String, Object>) Json.ler(recebido.get("sinal"));
        assertEquals("drive-ok-12345678901", ((Map<String, Object>) s.get("inputs")).get("sinal"));
        g.cancelar(id);
        assertEquals("sim", recebido.get("cancelar"));

        List<GitHub.Artefato> as = g.artefatos();
        assertEquals(1, as.size());
        assertEquals(12345678901L, as.get(0).runId);
        File zip = new File(tmp, "pacote.zip");
        assertEquals(15, g.baixar(as.get(0), zip, null, () -> false));
        assertEquals("conteudo-do-zip", new String(Files.readAllBytes(zip.toPath()), StandardCharsets.UTF_8));
        // o download foi redirecionado para outro servidor, sem o token
        assertTrue(tokens.contains("/blob/77 null"), tokens.toString());
    }

    @Test
    void errosExplicados() {
        GitHub errado = new GitHub(base, "dono/repo", "outro");
        GitHub.Erro e = assertThrows(GitHub.Erro.class, errado::ramoPrincipal);
        assertEquals(401, e.codigo);
        assertTrue(e.getMessage().contains("token"), e.getMessage());
        GitHub.Erro e2 = assertThrows(GitHub.Erro.class, () -> new GitHub(base, "dono/naoexiste", "tok").ramoPrincipal());
        assertEquals(404, e2.codigo);
        assertTrue(e2.getMessage().contains("repositório"), e2.getMessage());
    }
}
