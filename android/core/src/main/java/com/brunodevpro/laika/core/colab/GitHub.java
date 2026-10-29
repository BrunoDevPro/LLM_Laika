package com.brunodevpro.laika.core.colab;

import com.brunodevpro.laika.core.Armazem;
import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.dados.Parado;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BooleanSupplier;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * O que a tela Colab do app faz na API do GitHub: disparar o workflow colab.yml (que liga o Colab
 * pelo Colab CLI e roda as células), acompanhar a execução pela verificação "Laika no Colab",
 * cancelar, avisar que o Google Drive foi autorizado (workflow sinal.yml) e baixar o zip pronto.
 */
public final class GitHub {
    public static final String API = "https://api.github.com";
    public static final String WORKFLOW = "colab.yml", SINAL = "sinal.yml", PUBLICAR = "publicar.yml";
    public static final String VERIFICACAO = "Laika no Colab", ARTEFATO = "laika_pacote";
    private static final Pattern DADOS = Pattern.compile("<!-- laika (\\{.*\\}) -->", Pattern.DOTALL);

    /** Erro da API, já explicado para o usuário. */
    public static final class Erro extends IOException {
        public final int codigo;

        Erro(int codigo, String mensagem) {
            super(mensagem);
            this.codigo = codigo;
        }
    }

    /** Uma execução do workflow (um pedido de células). */
    public static final class Execucao {
        public long id;
        public String titulo, status, conclusao, sha, ramo, url;
        public long criada, atualizada;

        public boolean terminou() {
            return "completed".equals(status);
        }

        public boolean deuCerto() {
            return "success".equals(conclusao);
        }
    }

    public static final class Passo {
        public String nome, status, conclusao;
    }

    /** O que o laika_colab.py publica enquanto roda (título, resumo, últimas linhas e os dados para o app). */
    public static final class Verificacao {
        public String titulo = "", resumo = "", texto = "", status, conclusao;
        public Map<String, Object> dados = new LinkedHashMap<>();

        /** Link para autorizar o Google Drive, quando o Colab está esperando por isso. */
        public String autorizar() {
            Object a = dados.get("autorizar");
            return a instanceof String ? (String) a : null;
        }

        @SuppressWarnings("unchecked")
        public List<Map<String, Object>> celulas() {
            Object c = dados.get("celulas");
            return c instanceof List ? (List<Map<String, Object>>) c : new ArrayList<>();
        }
    }

    /** O zip guardado por uma execução (célula 6). */
    public static final class Artefato {
        public long id, tamanho, runId, criado;
        public String nome;
        public boolean expirado;
    }

    private final String api, repo, token;

    public GitHub(String repo, String token) {
        this(API, repo, token);
    }

    public GitHub(String api, String repo, String token) {
        this.api = api.replaceAll("/+$", "");
        this.repo = repo.trim();
        this.token = token == null ? "" : token.trim();
    }

    // ---------- HTTP ----------

    private HttpURLConnection abrir(String metodo, String url, boolean comToken, String accept) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setRequestMethod(metodo);
        c.setInstanceFollowRedirects(false);  // os redirecionamentos vão sem o token (veja seguir())
        c.setConnectTimeout(20_000);
        c.setReadTimeout(60_000);
        c.setRequestProperty("Accept", accept);
        c.setRequestProperty("User-Agent", "Laika-Android");
        c.setRequestProperty("X-GitHub-Api-Version", "2022-11-28");
        if (comToken && !token.isEmpty()) c.setRequestProperty("Authorization", "Bearer " + token);
        return c;
    }

    private static byte[] ler(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        if (in == null) return out.toByteArray();
        try (InputStream i = in) {
            byte[] b = new byte[1 << 15];
            int n;
            while ((n = i.read(b)) > 0) out.write(b, 0, n);
        }
        return out.toByteArray();
    }

    @SuppressWarnings("unchecked")
    private static Erro erro(HttpURLConnection c, int codigo) {
        String msg = "";
        try {
            Object o = Json.ler(new String(ler(c.getErrorStream()), StandardCharsets.UTF_8));
            if (o instanceof Map && ((Map<String, Object>) o).get("message") != null) {
                msg = String.valueOf(((Map<String, Object>) o).get("message"));
            }
        } catch (IOException | RuntimeException ignorado) {
            // sem corpo legível
        }
        String dica;
        if (codigo == 401) dica = "o token do GitHub está errado ou venceu";
        else if (codigo == 403 && "0".equals(c.getHeaderField("X-RateLimit-Remaining")))
            dica = "o GitHub pediu uma pausa (limite de pedidos); tente de novo em alguns minutos";
        else if (codigo == 403) dica = "o token não tem a permissão necessária (Actions: leitura e escrita)";
        else if (codigo == 404) dica = "não encontrado: confira o repositório e se o workflow do Colab já está no branch principal";
        else if (codigo == 422) dica = "o GitHub recusou o pedido";
        else dica = "erro " + codigo + " do GitHub";
        return new Erro(codigo, msg.isEmpty() || codigo == 404 || codigo == 401 ? dica : dica + " (" + msg + ")");
    }

    /** Pede à API (caminho começando com "/") e devolve o JSON (null se vier vazio). */
    private Object pedir(String metodo, String caminho, Object corpo) throws IOException {
        return pedir(metodo, caminho, corpo, true);
    }

    private Object pedir(String metodo, String caminho, Object corpo, boolean comToken) throws IOException {
        HttpURLConnection c = abrir(metodo, api + caminho, comToken, "application/vnd.github+json");
        try {
            if (corpo != null || metodo.equals("POST")) {
                // POST sem corpo (cancelar) vai com corpo vazio: o HttpURLConnection do Android exige
                byte[] b = corpo == null ? new byte[0] : Json.escrever(corpo).getBytes(StandardCharsets.UTF_8);
                c.setDoOutput(true);
                c.setFixedLengthStreamingMode(b.length);
                c.setRequestProperty("Content-Type", "application/json");
                try (OutputStream out = c.getOutputStream()) {
                    out.write(b);
                }
            }
            int codigo = c.getResponseCode();
            if (codigo >= 400) throw erro(c, codigo);
            String s = new String(ler(c.getInputStream()), StandardCharsets.UTF_8).trim();
            return s.isEmpty() ? null : Json.ler(s);
        } finally {
            c.disconnect();
        }
    }

    private String repoPath() {
        return "/repos/" + repo;
    }

    /** Segue redirecionamentos (o GitHub manda os downloads para outro servidor, que não deve receber o token). */
    private HttpURLConnection seguir(String url, String accept) throws IOException {
        boolean comToken = true;
        for (int i = 0; i < 6; i++) {
            HttpURLConnection c = abrir("GET", url, comToken, accept);
            int codigo = c.getResponseCode();
            if (codigo >= 300 && codigo < 400 && c.getHeaderField("Location") != null) {
                String destino = new URL(new URL(url), c.getHeaderField("Location")).toString();
                comToken = comToken && new URL(destino).getHost().equals(new URL(url).getHost());
                c.disconnect();
                url = destino;
                continue;
            }
            if (codigo >= 400) {
                Erro e = erro(c, codigo);
                c.disconnect();
                throw e;
            }
            return c;
        }
        throw new IOException("redirecionamentos demais");
    }

    // ---------- leitura dos campos ----------

    private static String texto(Map<String, Object> m, String k) {
        Object o = m.get(k);
        return o == null ? null : String.valueOf(o);
    }

    private static long numero(Map<String, Object> m, String k) {
        Object o = m.get(k);
        if (o instanceof Number) return ((Number) o).longValue();
        try {
            return o == null ? 0 : Long.parseLong(String.valueOf(o));
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private static long data(Map<String, Object> m, String k) {
        String s = texto(m, k);
        try {
            return s == null ? 0 : Instant.parse(s).toEpochMilli();
        } catch (RuntimeException e) {
            return 0;
        }
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> lista(Object o, String k) {
        if (!(o instanceof Map)) return new ArrayList<>();
        Object l = ((Map<String, Object>) o).get(k);
        return l instanceof List ? (List<Map<String, Object>>) l : new ArrayList<>();
    }

    private static Execucao execucao(Map<String, Object> r) {
        Execucao e = new Execucao();
        e.id = numero(r, "id");
        e.titulo = texto(r, "display_title");
        e.status = texto(r, "status");
        e.conclusao = texto(r, "conclusion");
        e.sha = texto(r, "head_sha");
        e.ramo = texto(r, "head_branch");
        e.url = texto(r, "html_url");
        e.criada = data(r, "created_at");
        e.atualizada = data(r, "updated_at");
        return e;
    }

    private static String q(String s) {
        try {
            return URLEncoder.encode(s, "UTF-8");
        } catch (java.io.UnsupportedEncodingException e) {
            throw new IllegalStateException(e);
        }
    }

    // ---------- API ----------

    /** Confere o token e o repositório; devolve o branch principal. */
    @SuppressWarnings("unchecked")
    public String ramoPrincipal() throws IOException {
        Map<String, Object> r = (Map<String, Object>) pedir("GET", repoPath(), null);
        return r == null || r.get("default_branch") == null ? "main" : String.valueOf(r.get("default_branch"));
    }

    /** Se o workflow do Colab existe (o arquivo precisa estar no branch principal). */
    public boolean temWorkflow() throws IOException {
        try {
            pedir("GET", repoPath() + "/actions/workflows/" + WORKFLOW, null);
            return true;
        } catch (Erro e) {
            if (e.codigo == 404) return false;
            throw e;
        }
    }

    /** O colab.ipynb do ramo (as células que a tela mostra). */
    public String caderno(String ramo) throws IOException {
        HttpURLConnection c = seguir(api + repoPath() + "/contents/colab.ipynb?ref=" + q(ramo),
                "application/vnd.github.raw+json");
        try {
            return new String(ler(c.getInputStream()), StandardCharsets.UTF_8);
        } finally {
            c.disconnect();
        }
    }

    /**
     * Pede as células. Devolve o id da execução, ou 0 se o GitHub não disse (aí use {@link #acharPedido}).
     * pedido é um código único que vai no nome da execução.
     */
    @SuppressWarnings("unchecked")
    public long disparar(String ramo, String celulas, String gpu, String parametrosJson, String pedido) throws IOException {
        Map<String, Object> inputs = new LinkedHashMap<>();
        inputs.put("celulas", celulas);
        inputs.put("gpu", gpu);
        inputs.put("parametros", parametrosJson);
        inputs.put("pedido", pedido);
        Map<String, Object> corpo = new LinkedHashMap<>();
        corpo.put("ref", ramo);
        corpo.put("inputs", inputs);
        corpo.put("return_run_details", true);
        Object r;
        try {
            r = pedir("POST", repoPath() + "/actions/workflows/" + WORKFLOW + "/dispatches", corpo);
        } catch (Erro e) {
            if (e.codigo != 422 || !String.valueOf(e.getMessage()).contains("return_run_details")) throw e;
            corpo.remove("return_run_details");  // API antiga
            r = pedir("POST", repoPath() + "/actions/workflows/" + WORKFLOW + "/dispatches", corpo);
        }
        if (r instanceof Map) {
            for (String k : new String[]{"workflow_run_id", "run_id", "id"}) {
                long id = numero((Map<String, Object>) r, k);
                if (id > 0) return id;
            }
        }
        return 0;
    }

    /** As últimas execuções do workflow do Colab, da mais nova para a mais velha. */
    public List<Execucao> execucoes(int quantas) throws IOException {
        Object r = pedir("GET", repoPath() + "/actions/workflows/" + WORKFLOW + "/runs?per_page=" + quantas, null);
        List<Execucao> l = new ArrayList<>();
        for (Map<String, Object> m : lista(r, "workflow_runs")) l.add(execucao(m));
        return l;
    }

    /** A execução de um pedido (pelo código no nome), ou null se ainda não apareceu. */
    public Execucao acharPedido(String pedido) throws IOException {
        for (Execucao e : execucoes(20)) if (e.titulo != null && e.titulo.contains(pedido)) return e;
        return null;
    }

    @SuppressWarnings("unchecked")
    public Execucao execucao(long id) throws IOException {
        return execucao((Map<String, Object>) pedir("GET", repoPath() + "/actions/runs/" + id, null));
    }

    /** Os passos do job (Instalar o Colab CLI, Rodar as células...). */
    public List<Passo> passos(long runId) throws IOException {
        List<Passo> r = new ArrayList<>();
        for (Map<String, Object> job : lista(pedir("GET", repoPath() + "/actions/runs/" + runId + "/jobs", null), "jobs")) {
            for (Map<String, Object> s : lista(job, "steps")) {
                Passo p = new Passo();
                p.nome = texto(s, "name");
                p.status = texto(s, "status");
                p.conclusao = texto(s, "conclusion");
                r.add(p);
            }
        }
        return r;
    }

    /** A verificação "Laika no Colab" da execução (null se ainda não existe). */
    @SuppressWarnings("unchecked")
    public Verificacao verificacao(Execucao e) throws IOException {
        if (e.sha == null) return null;
        String caminho = repoPath() + "/commits/" + e.sha + "/check-runs?check_name=" + q(VERIFICACAO)
                + "&filter=all&per_page=100";
        Object r;
        try {
            r = pedir("GET", caminho, null);
        } catch (Erro semPermissao) {
            // Token sem a permissão "Checks": num repositório público, a leitura funciona sem token.
            if (semPermissao.codigo != 403) throw semPermissao;
            r = pedir("GET", caminho, null, false);
        }
        for (Map<String, Object> c : lista(r, "check_runs")) {
            if (!String.valueOf(e.id).equals(texto(c, "external_id"))) continue;
            Verificacao v = new Verificacao();
            v.status = texto(c, "status");
            v.conclusao = texto(c, "conclusion");
            Object o = c.get("output");
            if (o instanceof Map) {
                Map<String, Object> out = (Map<String, Object>) o;
                v.titulo = String.valueOf(out.getOrDefault("title", ""));
                v.resumo = out.get("summary") == null ? "" : String.valueOf(out.get("summary"));
                v.texto = out.get("text") == null ? "" : String.valueOf(out.get("text"))
                        .replaceAll("^```\\n?", "").replaceAll("\\n?```$", "");
                Matcher m = DADOS.matcher(v.resumo);
                if (m.find()) {
                    try {
                        Object d = Json.ler(m.group(1));
                        if (d instanceof Map) v.dados = (Map<String, Object>) d;
                    } catch (RuntimeException ignorado) {
                        // resumo de outra versão do script
                    }
                }
            }
            return v;
        }
        return null;
    }

    public void cancelar(long runId) throws IOException {
        pedir("POST", repoPath() + "/actions/runs/" + runId + "/cancel", null);
    }

    /** Avisa a execução que o Google Drive foi autorizado (ela procura o workflow sinal.yml com este nome). */
    public void avisarDriveAutorizado(String ramo, long runId) throws IOException {
        Map<String, Object> inputs = new LinkedHashMap<>();
        inputs.put("sinal", "drive-ok-" + runId);
        Map<String, Object> corpo = new LinkedHashMap<>();
        corpo.put("ref", ramo);
        corpo.put("inputs", inputs);
        pedir("POST", repoPath() + "/actions/workflows/" + SINAL + "/dispatches", corpo);
    }

    /** Os zips prontos (artefato laika_pacote), do mais novo para o mais velho. */
    public List<Artefato> artefatos() throws IOException {
        Object r = pedir("GET", repoPath() + "/actions/artifacts?name=" + q(ARTEFATO) + "&per_page=30", null);
        List<Artefato> l = new ArrayList<>();
        for (Map<String, Object> m : lista(r, "artifacts")) {
            Artefato a = new Artefato();
            a.id = numero(m, "id");
            a.nome = texto(m, "name");
            a.tamanho = numero(m, "size_in_bytes");
            a.criado = data(m, "created_at");
            a.expirado = Boolean.TRUE.equals(m.get("expired"));
            Object run = m.get("workflow_run");
            if (run instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> w = (Map<String, Object>) run;
                a.runId = numero(w, "id");
            }
            l.add(a);
        }
        return l;
    }

    /** Baixa o zip do artefato (é o próprio laika_pacote.zip, pronto para importar). */
    public long baixar(Artefato a, File destino, Armazem.Progresso p, BooleanSupplier cancelar) throws IOException {
        try (OutputStream out = new FileOutputStream(destino)) {
            return baixar(a, out, p, cancelar);
        } catch (IOException | RuntimeException e) {
            destino.delete();
            throw e;
        }
    }

    /** O mesmo, gravando num fluxo (ex.: um arquivo que o usuário escolheu em Downloads). */
    public long baixar(Artefato a, OutputStream out, Armazem.Progresso p, BooleanSupplier cancelar) throws IOException {
        HttpURLConnection c = seguir(api + repoPath() + "/actions/artifacts/" + a.id + "/zip", "application/vnd.github+json");
        long total = c.getContentLengthLong() > 0 ? c.getContentLengthLong() : a.tamanho;
        long feito = 0;
        try (InputStream in = c.getInputStream()) {
            byte[] b = new byte[1 << 16];
            int n;
            long ultimo = 0;
            while ((n = in.read(b)) > 0) {
                if (cancelar != null && cancelar.getAsBoolean()) throw new Parado();
                out.write(b, 0, n);
                feito += n;
                if (p != null && feito - ultimo > (1 << 20)) {
                    ultimo = feito;
                    p.feito(feito, total);
                }
            }
        } finally {
            c.disconnect();
        }
        if (p != null) p.feito(feito, total);
        return feito;
    }

    /**
     * Publica o zip de um artefato como release do GitHub: dispara o workflow publicar.yml, que baixa o artefato no
     * servidor e cria o release (o arquivo não passa pelo celular). Precisa do publicar.yml no ramo principal.
     */
    public void publicar(String ramo, Artefato a, String nome, String notas) throws IOException {
        Map<String, Object> inputs = new LinkedHashMap<>();
        inputs.put("artefato", String.valueOf(a.id));
        inputs.put("nome", nome);
        inputs.put("notas", notas == null ? "" : notas);
        Map<String, Object> corpo = new LinkedHashMap<>();
        corpo.put("ref", ramo);
        corpo.put("inputs", inputs);
        pedir("POST", repoPath() + "/actions/workflows/" + PUBLICAR + "/dispatches", corpo);
    }

    /** Um release recém-criado, esperando o arquivo. */
    public static final class Release {
        public long id;
        public String url, envio;
    }

    /**
     * Cria o release (ainda sem o arquivo). Se o envio do arquivo falhar, {@link #apagarRelease} o tira, para não ficar
     * um release vazio. O token precisa de Contents: leitura e escrita.
     */
    @SuppressWarnings("unchecked")
    public Release criarRelease(String tag, String nome, String notas) throws IOException {
        Map<String, Object> corpo = new LinkedHashMap<>();
        corpo.put("tag_name", tag);
        corpo.put("name", nome);
        corpo.put("body", notas);
        Object r;
        try {
            r = pedir("POST", repoPath() + "/releases", corpo);
        } catch (Erro e) {
            if (e.codigo == 403 || e.codigo == 404) {
                throw new Erro(e.codigo, "o token não pode criar releases: dê a ele a permissão Contents (leitura e "
                        + "escrita) no GitHub e troque o token na tela Treinar");
            }
            throw e;
        }
        Map<String, Object> m = (Map<String, Object>) r;
        Release rel = new Release();
        rel.id = numero(m, "id");
        rel.url = texto(m, "html_url");
        String envio = texto(m, "upload_url");
        rel.envio = envio == null ? null : envio.replaceAll("\\{.*\\}$", "");
        return rel;
    }

    /** Envia o zip para o release (uploads.github.com), mostrando o andamento. */
    public void enviarArquivo(Release rel, File arquivo, String nome, Armazem.Progresso p, BooleanSupplier cancelar)
            throws IOException {
        HttpURLConnection c = abrir("POST", rel.envio + "?name=" + q(nome), true, "application/vnd.github+json");
        c.setReadTimeout(10 * 60_000);
        c.setDoOutput(true);
        c.setFixedLengthStreamingMode(arquivo.length());
        c.setRequestProperty("Content-Type", "application/zip");
        long total = arquivo.length(), feito = 0, ultimo = 0;
        try {
            try (InputStream in = new FileInputStream(arquivo); OutputStream out = c.getOutputStream()) {
                byte[] b = new byte[1 << 16];
                int n;
                while ((n = in.read(b)) > 0) {
                    if (cancelar != null && cancelar.getAsBoolean()) throw new Parado();
                    out.write(b, 0, n);
                    feito += n;
                    if (p != null && feito - ultimo > (1 << 20)) {
                        ultimo = feito;
                        p.feito(feito, total);
                    }
                }
            }
            int codigo = c.getResponseCode();
            if (codigo >= 400) throw erro(c, codigo);
            ler(c.getInputStream());
        } finally {
            c.disconnect();
        }
        if (p != null) p.feito(total, total);
    }

    public void apagarRelease(Release rel) throws IOException {
        pedir("DELETE", repoPath() + "/releases/" + rel.id, null);
    }

    /** Página dos releases do repositório. */
    public String paginaReleases() {
        return "https://github.com/" + repo + "/releases";
    }

    /** O registro (log) de uma execução que já terminou: as últimas linhas do job. */
    @SuppressWarnings("unchecked")
    public String registro(long runId, int linhas) throws IOException {
        List<Map<String, Object>> jobs = lista(pedir("GET", repoPath() + "/actions/runs/" + runId + "/jobs", null), "jobs");
        if (jobs.isEmpty()) return "";
        HttpURLConnection c = seguir(api + repoPath() + "/actions/jobs/" + numero(jobs.get(0), "id") + "/logs",
                "application/vnd.github+json");
        String[] todas;
        try {
            todas = new String(ler(c.getInputStream()), StandardCharsets.UTF_8).split("\n");
        } finally {
            c.disconnect();
        }
        StringBuilder sb = new StringBuilder();
        for (int i = Math.max(0, todas.length - linhas); i < todas.length; i++) {
            // "2026-10-23T12:00:00.1234567Z texto" -> "texto"
            sb.append(todas[i].replaceFirst("^\\d{4}-\\d\\d-\\d\\dT[\\d:.]+Z ", "")).append('\n');
        }
        return sb.toString();
    }
}
