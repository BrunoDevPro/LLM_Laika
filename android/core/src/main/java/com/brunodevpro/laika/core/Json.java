package com.brunodevpro.laika.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** JSON mínimo para o memoria.json (o core roda também fora do Android, sem org.json). */
final class Json {
    private Json() {
    }

    static Object ler(String s) {
        Leitor l = new Leitor(s);
        Object v = l.valor();
        l.espacos();
        if (l.i != s.length()) throw new IllegalArgumentException("JSON com sobra no fim");
        return v;
    }

    private static final class Leitor {
        final String s;
        int i;

        Leitor(String s) {
            this.s = s;
        }

        void espacos() {
            while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++;
        }

        Object valor() {
            espacos();
            if (i >= s.length()) throw new IllegalArgumentException("JSON incompleto");
            char c = s.charAt(i);
            if (c == '{') {
                i++;
                Map<String, Object> m = new LinkedHashMap<>();
                espacos();
                if (s.charAt(i) == '}') {
                    i++;
                    return m;
                }
                while (true) {
                    espacos();
                    String k = texto();
                    espacos();
                    esperar(':');
                    m.put(k, valor());
                    espacos();
                    if (s.charAt(i) == ',') {
                        i++;
                        continue;
                    }
                    esperar('}');
                    return m;
                }
            }
            if (c == '[') {
                i++;
                List<Object> a = new ArrayList<>();
                espacos();
                if (s.charAt(i) == ']') {
                    i++;
                    return a;
                }
                while (true) {
                    a.add(valor());
                    espacos();
                    if (s.charAt(i) == ',') {
                        i++;
                        continue;
                    }
                    esperar(']');
                    return a;
                }
            }
            if (c == '"') return texto();
            if (s.startsWith("null", i)) {
                i += 4;
                return null;
            }
            if (s.startsWith("true", i)) {
                i += 4;
                return Boolean.TRUE;
            }
            if (s.startsWith("false", i)) {
                i += 5;
                return Boolean.FALSE;
            }
            int ini = i;
            while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
            if (ini == i) throw new IllegalArgumentException("JSON inválido em " + i);
            return Double.parseDouble(s.substring(ini, i));
        }

        void esperar(char c) {
            if (i >= s.length() || s.charAt(i) != c) throw new IllegalArgumentException("esperava " + c);
            i++;
        }

        String texto() {
            esperar('"');
            StringBuilder sb = new StringBuilder();
            while (true) {
                char c = s.charAt(i++);
                if (c == '"') return sb.toString();
                if (c != '\\') {
                    sb.append(c);
                    continue;
                }
                char e = s.charAt(i++);
                switch (e) {
                    case 'n': sb.append('\n'); break;
                    case 't': sb.append('\t'); break;
                    case 'r': sb.append('\r'); break;
                    case 'b': sb.append('\b'); break;
                    case 'f': sb.append('\f'); break;
                    case 'u':
                        sb.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                        i += 4;
                        break;
                    default: sb.append(e);
                }
            }
        }
    }

    static String escrever(Object v) {
        StringBuilder sb = new StringBuilder();
        escrever(v, sb, 0);
        return sb.toString();
    }

    @SuppressWarnings("unchecked")
    private static void escrever(Object v, StringBuilder sb, int nivel) {
        if (v == null) {
            sb.append("null");
        } else if (v instanceof Boolean) {
            sb.append(v);
        } else if (v instanceof String) {
            sb.append('"');
            for (char c : ((String) v).toCharArray()) {
                if (c == '"' || c == '\\') sb.append('\\').append(c);
                else if (c == '\n') sb.append("\\n");
                else if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                else sb.append(c);
            }
            sb.append('"');
        } else if (v instanceof Map) {
            Map<String, Object> m = (Map<String, Object>) v;
            if (m.isEmpty()) {
                sb.append("{}");
                return;
            }
            sb.append("{\n");
            int k = 0;
            for (Map.Entry<String, Object> e : m.entrySet()) {
                recuo(sb, nivel + 1);
                escrever(e.getKey(), sb, nivel + 1);
                sb.append(": ");
                escrever(e.getValue(), sb, nivel + 1);
                sb.append(++k < m.size() ? ",\n" : "\n");
            }
            recuo(sb, nivel);
            sb.append('}');
        } else if (v instanceof List) {
            List<Object> a = (List<Object>) v;
            if (a.isEmpty()) {
                sb.append("[]");
                return;
            }
            sb.append("[\n");
            for (int k = 0; k < a.size(); k++) {
                recuo(sb, nivel + 1);
                escrever(a.get(k), sb, nivel + 1);
                sb.append(k + 1 < a.size() ? ",\n" : "\n");
            }
            recuo(sb, nivel);
            sb.append(']');
        } else {
            sb.append(v);
        }
    }

    private static void recuo(StringBuilder sb, int nivel) {
        for (int k = 0; k < nivel; k++) sb.append(' ');
    }
}
