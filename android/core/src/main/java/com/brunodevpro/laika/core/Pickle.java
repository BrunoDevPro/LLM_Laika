package com.brunodevpro.laika.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Leitor mínimo de pickle, só o necessário para o data.pkl de um checkpoint do torch.save
 * (dicts, listas, tuplas, números, textos e tensores). Não executa código: as "classes"
 * do pickle viram objetos simples (Global, Tensor, Armazenamento).
 */
final class Pickle {
    /** Referência a uma classe/função do Python (ex.: collections.OrderedDict). */
    static final class Global {
        final String modulo, nome;

        Global(String modulo, String nome) {
            this.modulo = modulo;
            this.nome = nome;
        }

        String completo() {
            return modulo + "." + nome;
        }
    }

    /** Um storage do torch: arquivo data/<chave> dentro do zip. */
    static final class Armazenamento {
        final String tipo, chave;  // tipo: FloatStorage, HalfStorage, BFloat16Storage...
        final long numel;

        Armazenamento(String tipo, String chave, long numel) {
            this.tipo = tipo;
            this.chave = chave;
            this.numel = numel;
        }
    }

    /** Um tensor: pedaço de um storage com forma e passos (stride). */
    static final class Tensor {
        final Armazenamento armazenamento;
        final long deslocamento;
        final int[] forma, passos;

        Tensor(Armazenamento a, long deslocamento, int[] forma, int[] passos) {
            this.armazenamento = a;
            this.deslocamento = deslocamento;
            this.forma = forma;
            this.passos = passos;
        }

        long numel() {
            long n = 1;
            for (int f : forma) n *= f;
            return n;
        }
    }

    /** Objeto montado por REDUCE com uma classe desconhecida (guardamos só os argumentos). */
    static final class Objeto {
        final Global classe;
        final Object args;
        Object estado;

        Objeto(Global classe, Object args) {
            this.classe = classe;
            this.args = args;
        }
    }

    private static final Object MARCA = new Object();

    private final ByteBuffer b;
    private final List<Object> pilha = new ArrayList<>();
    private final Map<Integer, Object> memo = new HashMap<>();

    private Pickle(byte[] dados) {
        b = ByteBuffer.wrap(dados).order(ByteOrder.LITTLE_ENDIAN);
    }

    static Object ler(byte[] dados) throws IOException {
        try {
            return new Pickle(dados).executar();
        } catch (RuntimeException e) {
            throw new IOException("pickle inválido: " + e.getMessage(), e);
        }
    }

    private Object pop() {
        return pilha.remove(pilha.size() - 1);
    }

    private Object topo() {
        return pilha.get(pilha.size() - 1);
    }

    /** Tira da pilha tudo até a última MARK. */
    private List<Object> ateMarca() {
        int i = pilha.size() - 1;
        while (pilha.get(i) != MARCA) i--;
        List<Object> itens = new ArrayList<>(pilha.subList(i + 1, pilha.size()));
        while (pilha.size() > i) pilha.remove(pilha.size() - 1);
        return itens;
    }

    private String texto(int n) {
        byte[] s = new byte[n];
        b.get(s);
        return new String(s, StandardCharsets.UTF_8);
    }

    private String linha() {
        StringBuilder sb = new StringBuilder();
        byte c;
        while ((c = b.get()) != '\n') sb.append((char) c);
        return sb.toString();
    }

    @SuppressWarnings("unchecked")
    private Object executar() throws IOException {
        while (true) {
            int op = b.get() & 0xFF;
            switch (op) {
                case 0x80: b.get(); break;                       // PROTO
                case 0x95: b.getLong(); break;                   // FRAME
                case '}': pilha.add(new LinkedHashMap<>()); break; // EMPTY_DICT
                case ']': pilha.add(new ArrayList<>()); break;   // EMPTY_LIST
                case ')': pilha.add(new Object[0]); break;       // EMPTY_TUPLE
                case '(': pilha.add(MARCA); break;               // MARK
                case 't': pilha.add(ateMarca().toArray()); break; // TUPLE
                case 0x85: pilha.add(new Object[]{pop()}); break; // TUPLE1
                case 0x86: {                                     // TUPLE2
                    Object y = pop(), x = pop();
                    pilha.add(new Object[]{x, y});
                    break;
                }
                case 0x87: {                                     // TUPLE3
                    Object z = pop(), y = pop(), x = pop();
                    pilha.add(new Object[]{x, y, z});
                    break;
                }
                case 'N': pilha.add(null); break;                // NONE
                case 0x88: pilha.add(Boolean.TRUE); break;       // NEWTRUE
                case 0x89: pilha.add(Boolean.FALSE); break;      // NEWFALSE
                case 'J': pilha.add((long) b.getInt()); break;   // BININT
                case 'K': pilha.add((long) (b.get() & 0xFF)); break; // BININT1
                case 'M': pilha.add((long) (b.getShort() & 0xFFFF)); break; // BININT2
                case 0x8a: {                                     // LONG1
                    int n = b.get() & 0xFF;
                    long v = 0;
                    for (int i = 0; i < n; i++) v |= (long) (b.get() & 0xFF) << (8 * i);
                    if (n > 0 && n < 8 && (v >> (8 * n - 1) & 1) == 1) v -= 1L << (8 * n);  // negativo
                    pilha.add(v);
                    break;
                }
                case 'G':                                        // BINFLOAT (big-endian)
                    pilha.add(b.order(ByteOrder.BIG_ENDIAN).getDouble());
                    b.order(ByteOrder.LITTLE_ENDIAN);
                    break;
                case 'X': pilha.add(texto(b.getInt())); break;   // BINUNICODE
                case 0x8c: pilha.add(texto(b.get() & 0xFF)); break; // SHORT_BINUNICODE
                case 'q': memo.put(b.get() & 0xFF, topo()); break; // BINPUT
                case 'r': memo.put(b.getInt(), topo()); break;   // LONG_BINPUT
                case 0x94: memo.put(memo.size(), topo()); break; // MEMOIZE
                case 'h': pilha.add(memo.get(b.get() & 0xFF)); break; // BINGET
                case 'j': pilha.add(memo.get(b.getInt())); break; // LONG_BINGET
                case 'c': pilha.add(new Global(linha(), linha())); break; // GLOBAL
                case 0x93: {                                     // STACK_GLOBAL
                    String nome = (String) pop(), mod = (String) pop();
                    pilha.add(new Global(mod, nome));
                    break;
                }
                case 's': {                                      // SETITEM
                    Object v = pop(), k = pop();
                    ((Map<Object, Object>) topo()).put(k, v);
                    break;
                }
                case 'u': {                                      // SETITEMS
                    List<Object> itens = ateMarca();
                    Map<Object, Object> d = (Map<Object, Object>) topo();
                    for (int i = 0; i + 1 < itens.size(); i += 2) d.put(itens.get(i), itens.get(i + 1));
                    break;
                }
                case 'a': {                                      // APPEND
                    Object v = pop();
                    ((List<Object>) topo()).add(v);
                    break;
                }
                case 'e': {                                      // APPENDS
                    List<Object> itens = ateMarca();
                    ((List<Object>) topo()).addAll(itens);
                    break;
                }
                case 'Q': pilha.add(persistente(pop())); break;  // BINPERSID
                case 'R': {                                      // REDUCE
                    Object args = pop();
                    Global g = (Global) pop();
                    pilha.add(reduzir(g, (Object[]) args));
                    break;
                }
                case 0x81: {                                     // NEWOBJ
                    Object args = pop();
                    pilha.add(reduzir((Global) pop(), (Object[]) args));
                    break;
                }
                case 'b': {                                      // BUILD
                    Object estado = pop();
                    Object alvo = topo();
                    if (alvo instanceof Objeto) ((Objeto) alvo).estado = estado;
                    // OrderedDict/Tensor: o estado extra (metadados) não importa aqui.
                    break;
                }
                case '.': return pop();                          // STOP
                default:
                    throw new IOException(String.format("instrução de pickle não suportada: 0x%02x", op));
            }
        }
    }

    /** ('storage', torch.FloatStorage, '0', 'cpu', numel) */
    private Object persistente(Object id) {
        Object[] t = (Object[]) id;
        if (t.length < 5 || !"storage".equals(t[0])) throw new IllegalStateException("persistent_id desconhecido");
        Global tipo = (Global) t[1];
        return new Armazenamento(tipo.nome, String.valueOf(t[2]), ((Number) t[4]).longValue());
    }

    private Object reduzir(Global g, Object[] args) {
        switch (g.completo()) {
            case "collections.OrderedDict":
                return new LinkedHashMap<>();
            case "torch._utils._rebuild_tensor_v2":
            case "torch._utils._rebuild_tensor": {
                Armazenamento a = (Armazenamento) args[0];
                long desl = ((Number) args[1]).longValue();
                return new Tensor(a, desl, inteiros((Object[]) args[2]), inteiros((Object[]) args[3]));
            }
            case "torch._utils._rebuild_parameter":
                return args[0];
            default:
                return new Objeto(g, args);
        }
    }

    private static int[] inteiros(Object[] t) {
        int[] r = new int[t.length];
        for (int i = 0; i < t.length; i++) r[i] = ((Number) t[i]).intValue();
        return r;
    }
}
