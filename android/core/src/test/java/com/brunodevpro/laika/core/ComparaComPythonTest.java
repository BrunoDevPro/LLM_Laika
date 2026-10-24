package com.brunodevpro.laika.core;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import androidx.sqlite.driver.bundled.BundledSQLiteDriver;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Compara o core em Java com o código Python original. As referências vêm de
 * android/core/referencias.py e os pesos de android/exportar_modelo.py; sem eles, os testes são pulados.
 */
class ComparaComPythonTest {
    static File assets, refs;
    static Tokenizador tok;
    static Modelo chat, base;
    static IndiceRag rag;

    @BeforeAll
    static void carregar() throws IOException {
        assets = new File(System.getProperty("laika.assets", "../app/src/main/assets"));
        refs = new File(System.getProperty("laika.referencias", "build/referencias"));
        assumeTrue(new File(assets, "tokenizer.txt").exists() && new File(refs, "modelo.jsonl").exists(),
                "rode exportar_modelo.py e referencias.py antes");
        tok = new Tokenizador(new FileInputStream(new File(assets, "tokenizer.txt")));
        chat = new Modelo(new FileInputStream(new File(assets, "laika_chat.bin")), 4);
        base = new Modelo(new FileInputStream(new File(assets, "laika_base.bin")), 4);
        // LAIKA_RAG_DB: outro índice (o mesmo passado ao referencias.py --rag-db), ex.: um com artigos reais.
        String outroDb = System.getProperty("laika.ragdb");
        File db = outroDb != null && !outroDb.isEmpty() ? new File(outroDb) : new File(assets, "laika_rag_mini.db");
        rag = new IndiceRag(new BundledSQLiteDriver().open(db.getPath()));
    }

    @AfterAll
    static void fechar() {
        if (rag != null) rag.close();
        if (chat != null) chat.fechar();
        if (base != null) base.fechar();
    }

    @SuppressWarnings("unchecked")
    static List<Map<String, Object>> ler(String nome) throws IOException {
        List<Map<String, Object>> r = new ArrayList<>();
        for (String linha : Files.readAllLines(new File(refs, nome).toPath(), StandardCharsets.UTF_8)) {
            if (!linha.isEmpty()) r.add((Map<String, Object>) Json.ler(linha));
        }
        return r;
    }

    static int[] ints(Object lista) {
        List<?> l = (List<?>) lista;
        int[] r = new int[l.size()];
        for (int i = 0; i < r.length; i++) r[i] = ((Double) l.get(i)).intValue();
        return r;
    }

    @Test
    void tokenizer() throws IOException {
        int n = 0;
        for (Map<String, Object> c : ler("tokenizer.jsonl")) {
            String texto = (String) c.get("texto");
            int[] esperado = ints(c.get("ids"));
            int[] obtido = tok.codificar(texto);
            assertEquals(java.util.Arrays.toString(esperado), java.util.Arrays.toString(obtido), "codificar: " + texto);
            assertEquals(c.get("decod"), tok.decodificar(obtido), "decodificar: " + texto);
            n++;
        }
        System.out.println("tokenizer: " + n + " textos iguais ao Python");
    }

    @Test
    void modelo() throws IOException {
        double pior = 0;
        for (Map<String, Object> c : ler("modelo.jsonl")) {
            Modelo m = "finetuned".equals(c.get("modelo")) ? chat : base;
            int[] ids = ints(c.get("ids"));
            if (c.get("logits") != null) {
                // Tudo de uma vez e token a token (cache) têm que dar os mesmos logits do PyTorch.
                float[] juntos = m.avancar(m.novoCache(), ids, 0, ids.length);
                Modelo.Cache cache = m.novoCache();
                float[] passo = null;
                for (int i = 0; i < ids.length; i++) passo = m.avancar(cache, ids, i, i + 1);
                List<?> esperado = (List<?>) c.get("logits");
                for (int v = 0; v < esperado.size(); v++) {
                    double e = (Double) esperado.get(v);
                    pior = Math.max(pior, Math.max(Math.abs(e - juntos[v]), Math.abs(e - passo[v])));
                }
            }
            // Geração gulosa com cache = geração gulosa do PyTorch sem cache (inclusive passando da janela).
            int[] guloso = ints(c.get("guloso"));
            int[] seq = java.util.Arrays.copyOf(ids, ids.length + guloso.length);
            int n = ids.length;
            Modelo.Cache cache = m.novoCache();
            for (int k = 0; k < guloso.length; k++) {
                float[] lg;
                if (n <= m.block) {
                    lg = m.avancar(cache, seq, cache.tamanho(), n);
                } else {
                    cache.limpar();
                    lg = m.avancar(cache, seq, n - m.block, n);
                }
                int arg = 0;
                for (int v = 1; v < lg.length; v++) if (lg[v] > lg[arg]) arg = v;
                seq[n++] = arg;
            }
            assertEquals(java.util.Arrays.toString(guloso),
                    java.util.Arrays.toString(java.util.Arrays.copyOfRange(seq, ids.length, n)), "guloso " + c.get("modelo"));
        }
        System.out.printf("modelo: maior diferença de logit para o PyTorch = %.2e%n", pior);
        assertTrue(pior < 2e-3, "logits diferentes do PyTorch: " + pior);
    }

    @Test
    void modoCompactoDaOMesmoResultado() throws IOException {
        // Pesos em float16 na memória (modelos grandes): os mesmos logits, bit a bit.
        Modelo compacto = new Modelo(new FileInputStream(new File(assets, "laika_chat.bin")), 4, true);
        assertTrue(compacto.compacto && !chat.compacto);
        for (Map<String, Object> c : ler("modelo.jsonl")) {
            if (!"finetuned".equals(c.get("modelo"))) continue;
            int[] ids = ints(c.get("ids"));
            float[] a = chat.avancar(chat.novoCache(), ids, 0, ids.length);
            float[] b = compacto.avancar(compacto.novoCache(), ids, 0, ids.length);
            assertTrue(java.util.Arrays.equals(a, b), "compacto diferente");
        }
        compacto.fechar();
    }

    @Test
    void ragEPalavras() throws IOException {
        for (Map<String, Object> c : ler("rag.jsonl")) {
            String p = (String) c.get("pergunta");
            assertEquals(c.get("palavras"), Texto.palavrasDeConteudo(p), "palavras: " + p);
            List<String> radicais = new ArrayList<>();
            for (String w : Texto.palavrasDeConteudo(p)) radicais.add(IndiceRag.radical(w));
            assertEquals(c.get("radicais"), radicais, "radicais: " + p);
            assertEquals(c.get("quer_rag"), Texto.querRag(p), "querRag: " + p);
            List<?> top = (List<?>) c.get("top");
            List<IndiceRag.Trecho> r = rag.buscar(p);
            for (int i = 0; i < top.size(); i++) {
                List<?> e = (List<?>) top.get(i);
                assertEquals(e.get(0), r.get(i).titulo, "título " + i + ": " + p);
                assertEquals((Double) e.get(1), r.get(i).nota, 1e-6, "nota " + i + ": " + p);
                assertEquals((Double) e.get(2), r.get(i).cobertura, 1e-9, "cobertura " + i + ": " + p);
            }
            IndiceRag.Trecho m = rag.melhor(p);
            assertEquals(c.get("melhor"), m == null ? null : m.titulo, "melhor: " + p);
            assertEquals(c.get("nome"), Texto.nomeDaPergunta(p), "nome: " + p);
            assertEquals(c.get("segue"), Texto.segueConversa(p), "segueConversa: " + p);
            assertEquals(c.get("sem_gatilho"), Texto.semGatilho(p), "semGatilho: " + p);
            assertEquals(c.get("longa"), Texto.querLonga(p), "querLonga: " + p);
            assertEquals(c.get("consultas"), Texto.consultasRag(p), "consultas: " + p);
            Map<?, ?> contextos = (Map<?, ?>) c.get("contextos");
            for (int k : new int[]{1, 2, 3, 6}) {
                List<List<String>> obtido = new ArrayList<>();
                for (IndiceRag.Trecho t : rag.contextos(p, k)) obtido.add(java.util.Arrays.asList(t.titulo, t.texto));
                assertEquals(contextos.get(String.valueOf(k)), obtido, "contextos k=" + k + ": " + p);
            }
        }
    }

    @Test
    void memoria() throws IOException {
        File f = File.createTempFile("memoria", ".json");
        f.delete();
        Memoria mem = new Memoria(f);
        for (Map<String, Object> c : ler("memoria.jsonl")) {
            String msg = (String) c.get("msg");
            assertEquals(c.get("resposta"), mem.tratar(msg), "resposta: " + msg);
            assertEquals(c.get("contexto"), mem.contextoPara(msg), "contexto: " + msg);
            assertEquals(c.get("resumo"), mem.resumo(), "resumo: " + msg);
        }
        // O arquivo salvo volta igual.
        mem.tratar("meu nome é Bia");
        mem.tratar("lembre que \"aspas\" e \\ barra");
        assertEquals(mem.resumo(), new Memoria(f).resumo());
        f.delete();
    }

    @Test
    void prompt() throws IOException {
        File f = File.createTempFile("memoria2", ".json");
        f.delete();
        Memoria mem = new Memoria(f);
        mem.tratar("lembre que o vulcão da feira de ciências é de argila");
        Laika laika = new Laika(chat, tok);
        int comHistorico = 0;
        for (Map<String, Object> c : ler("prompt.jsonl")) {
            String p = (String) c.get("pergunta");
            int bloco = c.containsKey("bloco") ? ((Double) c.get("bloco")).intValue() : 256;
            int maxNovos = c.containsKey("max_novos") ? ((Double) c.get("max_novos")).intValue() : 80;
            List<String[]> hist = new ArrayList<>();
            if (c.containsKey("historico")) {
                for (Object t : (List<?>) c.get("historico")) {
                    List<?> par = (List<?>) t;
                    hist.add(new String[]{(String) par.get(0), (String) par.get(1)});
                }
            }
            Laika.Prompt pr = laika.montarPrompt(p, rag, Boolean.TRUE.equals(c.get("memoria")) ? mem : null,
                    maxNovos, hist, bloco);
            String caso = p + " (bloco " + bloco + ", " + maxNovos + " tokens, " + hist.size() + " trocas)";
            assertEquals(c.get("prompt"), pr.texto, "prompt: " + caso);
            assertEquals(c.get("fonte"), pr.fonte, "fonte: " + caso);
            if (pr.texto.indexOf(Texto.END) > 0) comHistorico++;
        }
        System.out.println("prompt: " + comHistorico + " prompts com histórico iguais ao Python");
        assertTrue(comHistorico > 0, "nenhum prompt com histórico");
        f.delete();
    }

    @Test
    void penalidadeDoFim() throws IOException {
        for (Map<String, Object> c : ler("penalidade.jsonl")) {
            int maxNovos = ((Double) c.get("max_novos")).intValue();
            int minimo = Laika.minimoResposta(maxNovos);
            assertEquals(((Double) c.get("minimo")).intValue(), minimo, "mínimo: " + maxNovos);
            List<?> valores = (List<?>) c.get("valores");
            for (int k = 0; k < valores.size(); k++) {
                assertEquals((Double) valores.get(k), Laika.penalidadeFim(k, minimo), 1e-12, "passo " + k);
            }
        }
    }

    @Test
    void conversaDeVerdade() {
        // Não compara com o Python (a amostragem é aleatória): só mostra respostas e o tempo por token.
        Laika laika = new Laika(chat, tok);
        Laika.Opcoes op = new Laika.Opcoes();
        Random rng = new Random(42);
        for (String p : new String[]{"Qual é o seu nome?", "O que é um vulcão?", "Quem foi a Laika?", "Oi"}) {
            Laika.Prompt pr = laika.montarPrompt(p, rag, null, op.maxNovos);
            long t0 = System.nanoTime();
            int[] cont = {0};
            String r = laika.gerar(pr.texto, op, true, rng, s -> cont[0]++, null);
            double ms = (System.nanoTime() - t0) / 1e6;
            System.out.printf("Você: %s%nLaika: %s%n   (%d tokens, %.0f ms, %.1f ms/token)%n", p,
                    Laika.comCitacao(r, pr.fonte), cont[0], ms, ms / Math.max(1, cont[0]));
            assertTrue(!r.isEmpty());
        }
        String cont = new Laika(base, tok).gerar("Era uma vez", op, false, rng, null, null);
        System.out.println("Completar: Era uma vez " + cont);
    }
}
