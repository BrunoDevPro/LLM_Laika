package com.brunodevpro.laika.core.treino;

import com.brunodevpro.laika.core.IndiceRag;
import com.brunodevpro.laika.core.Laika;
import com.brunodevpro.laika.core.Modelo;
import com.brunodevpro.laika.core.Texto;
import com.brunodevpro.laika.core.Tokenizador;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Set;

/**
 * O finetune.py no celular: mistura exemplos escritos à mão (data/qa), sintéticos dos livros e
 * perguntas da Wikipédia (data/qa_auto), parte com Contexto do RAG, loss só na resposta,
 * replay de texto puro, validação por época com early stopping. Grava saida/laika_chat.bin.
 */
public final class FineTuning {
    public static final class Opcoes {
        public int epocas = 2, maxQaRepeat = 2, identityBoost = 2, sinteticos = 4000, wikiQa = 3000, batch = 16;
        public int maxResumoLivros = 80, patience = 2, microLote = 8;
        public float lr = 5e-5f, qaShare = 0.25f, ragShare = 0.5f, replay = 0.25f, valFraction = 0.1f, dropout = 0.1f;
        /** MB de texto amostrado para os sintéticos e o replay (no Colab são 40; no celular cabe menos). */
        public float maxTextoMb = 15;
        public long semente = 0;
        /** Pesos de partida (laika_base.bin) e tokenizer. */
        public InputStream base;
        public String tokenizer;
        /** Índice para dar Contexto a parte das perguntas (pode ser null). */
        public IndiceRag rag;
    }

    static final String[] AMOSTRAS = {"Qual é o seu nome?", "Oi", "O que é um vulcão?", "Quem foi Santos Dumont?",
            "Qual é a capital da França?", "Complete a frase: Quem espera", "Escreva uma frase com a palavra noite.",
            "Resuma o texto: O menino acordou cedo, tomou café e foi para a escola de bicicleta. No caminho, viu um cachorro "
                    + "perdido e parou para ajudar. Por isso, chegou atrasado, mas a professora entendeu quando ele contou o "
                    + "que tinha acontecido."};

    private FineTuning() {
    }

    /** Um exemplo pronto: entrada e alvos (-1 = sem perda). */
    static final class Item {
        final int[] entrada, alvo;

        Item(int[] entrada, int[] alvo) {
            this.entrada = entrada;
            this.alvo = alvo;
        }
    }

    public static void rodar(Gl gl, Corpus corpus, File pasta, Opcoes op, Registro reg) throws IOException {
        File saida = new File(pasta, "saida");
        saida.mkdirs();
        reg.log("GPU: " + gl.descricao());
        Aleatorio rng = new Aleatorio(op.semente);
        Tokenizador tok = new Tokenizador(new ByteArrayInputStream(op.tokenizer.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        Rede.Config[] c = new Rede.Config[1];
        float[] pesos = Pesos.ler(op.base, op.dropout, c);
        Rede.Config cfg = c[0];
        int block = cfg.block;
        if (cfg.vocab != tok.tamanhoVocab()) throw new IOException("o modelo base não combina com o tokenizer");
        reg.log(String.format("Modelo base: %,d parâmetros, contexto %d.", pesos.length, block));

        // ---------- textos ----------
        List<File> todos = new ArrayList<>(corpus.preTreino());
        if (todos.isEmpty()) throw new IOException("não há textos (nem os de data/modern)");
        List<File> embaralhados = new ArrayList<>(todos);
        rng.embaralhar(embaralhados);
        embaralhados.sort((a, b) -> Boolean.compare(!a.getParentFile().getName().equals("modern"),
                !b.getParentFile().getName().equals("modern")));
        List<String> textos = new ArrayList<>();
        long lidos = 0, max = (long) (op.maxTextoMb * 1e6);
        for (File f : embaralhados) {
            if (lidos >= max && !f.getParentFile().getName().equals("modern")) break;
            textos.add(Corpus.lerTexto(f));
            lidos += f.length();
        }
        List<File> livros = new ArrayList<>(corpus.txt("books"));
        rng.embaralhar(livros);
        List<String> textosResumo = new ArrayList<>();
        for (int i = 0; i < Math.min(op.maxResumoLivros, livros.size()); i++) textosResumo.add(Corpus.lerTexto(livros.get(i)));
        reg.log(String.format("Textos usados: %d de %d arquivos (~%.0f M caracteres)", textos.size(), todos.size(),
                somaChars(textos) / 1e6));

        reg.log("Lendo perguntas/respostas:");
        List<String> qa = DadosChat.lerPerguntas(corpus.txt("qa"), reg);
        Set<String> identidade = new HashSet<>();
        File id = new File(corpus.pasta("qa"), "identidade.txt");
        if (id.exists()) identidade.addAll(DadosChat.lerPerguntas(Corpus.lerTexto(id)));
        List<String> sint = DadosChat.sinteticos(textos, op.sinteticos, rng, textosResumo.isEmpty() ? null : textosResumo);
        reg.log(String.format("Exemplos sintéticos gerados dos textos: %d (resumos de %d livros)", sint.size(),
                textosResumo.size()));
        if (!corpus.txt("qa_auto").isEmpty()) {
            reg.log("Perguntas automáticas (Wikipédia):");
            List<String> auto = DadosChat.lerPerguntas(corpus.txt("qa_auto"), reg);
            rng.embaralhar(auto);
            sint.addAll(auto.subList(0, Math.min(op.wikiQa, auto.size())));
        }
        if (reg.parar()) throw new Parado();

        // ---------- Contexto do RAG ----------
        if (op.rag != null) {
            int[] n = new int[1];
            qa = comContexto(qa, op, tok, block, rng, n);
            int nq = n[0];
            n[0] = 0;
            sint = comContexto(sint, op, tok, block, rng, n);
            reg.log(String.format("RAG: %d perguntas escritas à mão e %d automáticas ganharam Contexto", nq, n[0]));
        } else {
            reg.log("RAG desligado: o fine-tuning segue sem exemplos com Contexto do RAG.");
        }

        // ---------- tokens ----------
        int assistant = tok.id(Texto.ASSISTANT), end = tok.id(Texto.END), pad = tok.id(Texto.PAD), eot = tok.id(Texto.EOT);
        int[] longos = new int[1];
        List<Item> qaItens = codificar(qa, identidade, tok, block, assistant, end, longos);
        List<Item> idItens = codificar(new ArrayList<>(identidade), null, tok, block, assistant, end, new int[1]);
        List<Item> sinItens = codificar(sint, null, tok, block, assistant, end, new int[1]);
        if (longos[0] > 0) reg.log("ATENÇÃO: " + longos[0] + " exemplos escritos passam de " + block + " tokens e foram descartados.");
        if (sinItens.isEmpty()) throw new IOException("não consegui gerar exemplos dos textos");
        List<Item>[] qaS = dividir(qaItens, op, rng), idS = dividir(idItens, op, rng), sinS = dividir(sinItens, op, rng);
        List<Item> qaTreino = qaS[0], qaVal = qaS[1], idTreino = idS[0], sinTreino = sinS[0], sinVal = sinS[1];
        qaVal.addAll(idS[1]);
        int qaRepeat = 0;
        if (!qaTreino.isEmpty()) {
            double quer = op.qaShare / (1 - op.qaShare) * sinTreino.size();
            qaRepeat = Math.min(op.maxQaRepeat, Math.max(1, (int) Math.round(quer / qaTreino.size())));
        }
        int idRepeat = idTreino.isEmpty() ? 0 : qaRepeat * op.identityBoost;
        reg.log(String.format("Treino: %d sintéticos + %d do pergeresp (x%d) + %d de identidade (x%d) | validação: %d sintéticos + %d escritos à mão",
                sinTreino.size(), qaTreino.size(), qaRepeat, idTreino.size(), idRepeat, sinVal.size(), qaVal.size()));

        // texto contínuo para o replay
        int[] stream = new int[1 << 20];
        int nStream = 0;
        for (String t : textos) {
            int[] ids = tok.codificar(t);
            if (nStream + ids.length + 1 > stream.length) {
                stream = java.util.Arrays.copyOf(stream, Math.max(stream.length * 2, nStream + ids.length + 1));
            }
            System.arraycopy(ids, 0, stream, nStream, ids.length);
            nStream += ids.length;
            stream[nStream++] = eot;
            if (reg.parar()) throw new Parado();
        }
        stream = java.util.Arrays.copyOf(stream, nStream);
        textos = null;  // libera a memória antes do treino
        int nReplay = op.replay > 0 ? Math.round(op.batch * op.replay / (1 - op.replay)) : 0;

        int porEpoca = sinTreino.size() + qaTreino.size() * qaRepeat + idTreino.size() * idRepeat;
        int passosEpoca = (porEpoca + op.batch - 1) / op.batch, total = passosEpoca * op.epocas;
        int warmup = Math.min(100, total / 10);
        reg.log(String.format("%d steps por época, até %d no total (lote = %d de chat + %d de livro)", passosEpoca, total, op.batch,
                nReplay));

        int micro = Math.max(1, Math.min(op.microLote, op.batch + nReplay));
        try (Rede rede = new Rede(gl, cfg, micro)) {
            rede.carregar(pesos);
            Random rngAmostra = new Random(op.semente);
            reg.log("\nAntes do fine-tuning:");
            amostras(rede, cfg, tok, op.rag, block, rngAmostra, reg);
            double melhor = Double.POSITIVE_INFINITY;
            int ruins = 0, step = 0;
            long t0 = System.nanoTime();
            for (int ep = 1; ep <= op.epocas; ep++) {
                List<Item> itens = new ArrayList<>(sinTreino);
                for (int r = 0; r < qaRepeat; r++) itens.addAll(qaTreino);
                for (int r = 0; r < idRepeat; r++) itens.addAll(idTreino);
                rng.embaralhar(itens);
                double corrida = 0;
                for (int i = 0; i < itens.size(); i += op.batch) {
                    if (reg.parar()) {
                        reg.log("Parado. O melhor modelo até aqui está em saida/laika_chat.bin" + (melhor < 1e9 ? "." : " (nenhum ainda)."));
                        throw new Parado();
                    }
                    List<Item> lote = new ArrayList<>(itens.subList(i, Math.min(i + op.batch, itens.size())));
                    for (int r = 0; r < nReplay; r++) {
                        int s = rng.inteiro(stream.length - block - 1);
                        lote.add(new Item(java.util.Arrays.copyOfRange(stream, s, s + block),
                                java.util.Arrays.copyOfRange(stream, s + 1, s + block + 1)));
                    }
                    float lr = Presets.taxa(step, op.lr, warmup, total);
                    corrida += passo(rede, lote, micro, pad, true, (int) rng.proximo());
                    rede.otimizar(lr, 0.01f, 0.01f, 0.9f, 0.999f, 1e-8f, 1f, step + 1);
                    step++;
                    double seg = (System.nanoTime() - t0) / 1e9;
                    double faltam = seg / step * (total - step);
                    reg.progresso((double) step / total, String.format(Locale.getDefault(),
                            "Fine-tuning: época %d/%d · passo %d/%d · faltam ~%s", ep, op.epocas, step, total,
                            PreTreino.duracao(faltam)));
                }
                double sinV = validar(rede, sinVal, op.batch, micro, pad), qaV = validar(rede, qaVal, op.batch, micro, pad);
                double comb = Double.isNaN(qaV) ? sinV : 0.5 * (sinV + qaV);
                String nota = "";
                if (comb < melhor) {
                    melhor = comb;
                    ruins = 0;
                    nota = "  <- melhor, salvo";
                    Pesos.salvar(new File(saida, "laika_chat.bin"), cfg, rede.pesos(), comb, -1, true);
                } else {
                    ruins++;
                }
                reg.log(String.format(Locale.US, "\népoca %d | treino %.4f | val livros %.4f | val pergeresp %.4f%s", ep,
                        corrida / passosEpoca, sinV, qaV, nota));
                amostras(rede, cfg, tok, op.rag, block, rngAmostra, reg);
                if (ruins >= op.patience) {
                    reg.log("Early stopping.");
                    break;
                }
            }
            reg.log(String.format(Locale.US, "Fine-tuning concluído. Melhor val: %.4f -> saida/laika_chat.bin", melhor));
        }
    }

    private static long somaChars(List<String> t) {
        long n = 0;
        for (String s : t) n += s.length();
        return n;
    }

    private static List<String> comContexto(List<String> exemplos, Opcoes op, Tokenizador tok, int block, Aleatorio rng, int[] n) {
        List<String> r = new ArrayList<>(exemplos.size());
        for (String e : exemplos) {
            String[] qr = DadosChat.separar(e);
            if (rng.real() < op.ragShare && Texto.querRag(qr[0])) {
                IndiceRag.Trecho hit = op.rag.melhor(qr[0]);
                if (hit != null) {
                    String ans = qr[1];
                    String u = Texto.ajustarContexto(t -> tok.codificar(Texto.USER + " " + t + " " + Texto.ASSISTANT + " " + ans
                            + " " + Texto.END).length, qr[0], hit.texto, block);
                    if (u != null) {
                        r.add(Texto.USER + " " + u + " " + Texto.ASSISTANT + " " + ans + " " + Texto.END);
                        n[0]++;
                        continue;
                    }
                }
            }
            r.add(e);
        }
        return r;
    }

    /** encode_chat: perda só na resposta (e no <|end|>). */
    private static List<Item> codificar(List<String> textos, Set<String> pular, Tokenizador tok, int block, int assistant,
                                        int end, int[] longos) {
        List<Item> r = new ArrayList<>();
        for (String t : textos) {
            if (pular != null && pular.contains(t)) continue;
            int[] ids = tok.codificar(t);
            if (ids.length > block) {
                longos[0]++;
                continue;
            }
            int ia = -1;
            boolean temFim = false;
            for (int i = 0; i < ids.length; i++) {
                if (ids[i] == assistant && ia < 0) ia = i;
                if (ids[i] == end) temFim = true;
            }
            if (ia < 0 || !temFim) continue;
            int inicioResposta = ia + 1;
            int[] entrada = java.util.Arrays.copyOf(ids, ids.length - 1);
            int[] alvo = new int[ids.length - 1];
            for (int p = 0; p < alvo.length; p++) alvo[p] = p + 1 >= inicioResposta ? ids[p + 1] : -1;
            r.add(new Item(entrada, alvo));
        }
        return r;
    }

    @SuppressWarnings("unchecked")
    private static List<Item>[] dividir(List<Item> itens, Opcoes op, Aleatorio rng) {
        List<Item> l = new ArrayList<>(itens);
        rng.embaralhar(l);
        int nVal = l.size() >= 10 ? Math.max(1, (int) (l.size() * op.valFraction)) : 0;
        return new List[]{new ArrayList<>(l.subList(nVal, l.size())), new ArrayList<>(l.subList(0, nVal))};
    }

    /**
     * Um lote (com padding à direita), dividido em micro-lotes; a escala é 1/alvos do lote inteiro,
     * como o F.cross_entropy(..., ignore_index=-100) do lote. Devolve a perda média.
     */
    private static double passo(Rede rede, List<Item> lote, int micro, int pad, boolean treinar, int semente) {
        int validos = 0;
        for (Item it : lote) for (int a : it.alvo) if (a >= 0) validos++;
        if (validos == 0) return 0;
        float escala = 1f / validos;
        if (treinar) rede.zerarGradientes();
        double soma = 0;
        for (int i = 0; i < lote.size(); i += micro) {
            List<Item> m = lote.subList(i, Math.min(i + micro, lote.size()));
            int T = 0;
            for (Item it : m) T = Math.max(T, it.entrada.length);
            int B = m.size();
            int[] x = new int[B * T], y = new int[B * T];
            for (int b = 0; b < B; b++) {
                Item it = m.get(b);
                for (int t = 0; t < T; t++) {
                    boolean dentro = t < it.entrada.length;
                    x[b * T + t] = dentro ? it.entrada[t] : pad;
                    y[b * T + t] = dentro ? it.alvo[t] : -1;
                }
            }
            for (float p : rede.microPasso(x, y, B, T, treinar, escala, semente + i)) soma += p;
        }
        return soma / validos;
    }

    private static double validar(Rede rede, List<Item> itens, int batch, int micro, int pad) {
        if (itens.isEmpty()) return Double.NaN;
        double s = 0;
        int n = 0;
        for (int i = 0; i < itens.size(); i += batch) {
            s += passo(rede, itens.subList(i, Math.min(i + batch, itens.size())), micro, pad, false, 0);
            n++;
        }
        return s / n;
    }

    /** As respostas de teste do finetune.py, geradas no processador com os pesos atuais. */
    private static void amostras(Rede rede, Rede.Config cfg, Tokenizador tok, IndiceRag rag, int block, Random rng, Registro reg)
            throws IOException {
        File tmp = File.createTempFile("laika_amostra", ".bin");
        try {
            Pesos.salvar(tmp, cfg, rede.pesos(), Double.NaN, -1, true);
            Modelo m;
            try (InputStream in = new FileInputStream(tmp)) {
                m = new Modelo(in, Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors())));
            }
            try {
                Laika l = new Laika(m, tok);
                Laika.Opcoes op = new Laika.Opcoes();
                op.maxNovos = 60;
                for (String q : AMOSTRAS) {
                    Laika.Prompt p = l.montarPrompt(q, rag, null, 60);
                    String r = l.gerar(p.texto, op, true, rng, null, null);
                    reg.log("   Você: " + q + "\n   LLM:  " + Laika.comCitacao(r, p.fonte));
                }
            } finally {
                m.fechar();
            }
        } finally {
            tmp.delete();
        }
    }
}
