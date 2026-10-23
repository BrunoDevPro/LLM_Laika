package com.brunodevpro.laika;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.job.JobInfo;
import android.app.job.JobScheduler;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;

import com.brunodevpro.laika.core.Json;
import com.brunodevpro.laika.core.colab.GitHub;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Configuração da tela Colab (repositório, token, escolhas) e o acompanhamento das execuções em
 * segundo plano: o {@link ColabJob} consulta o GitHub de tempos em tempos e avisa por notificação
 * quando o Colab pede autorização do Google Drive e quando termina.
 */
final class Colab {
    static final String REPO_PADRAO = "BrunoDevPro/LLM_Laika";
    static final String CANAL = "colab";
    static final String DRIVE_OK = "com.brunodevpro.laika.DRIVE_OK";
    private static final int JOB = 31, NOTIF_BASE = 4000;

    private Colab() {
    }

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences("colab", Context.MODE_PRIVATE);
    }

    static String repo(Context c) {
        return prefs(c).getString("repo", REPO_PADRAO);
    }

    static String ramo(Context c) {
        return prefs(c).getString("ramo", "main");
    }

    /** O token fica fora dos backups automáticos do Android (noBackupFilesDir). */
    private static File arquivoToken(Context c) {
        return new File(c.getNoBackupFilesDir(), "github_token");
    }

    static String token(Context c) {
        try {
            File f = arquivoToken(c);
            return f.exists() ? new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8).trim() : "";
        } catch (IOException e) {
            return "";
        }
    }

    static void salvar(Context c, String repo, String token) throws IOException {
        prefs(c).edit().putString("repo", repo.trim()).apply();
        Files.write(arquivoToken(c).toPath(), token.trim().getBytes(StandardCharsets.UTF_8));
    }

    static void esquecerToken(Context c) {
        arquivoToken(c).delete();
    }

    static boolean configurado(Context c) {
        return !token(c).isEmpty();
    }

    static GitHub github(Context c) {
        return new GitHub(repo(c), token(c));
    }

    /** Código curto e único para achar a execução pelo nome (vai no run-name do workflow). */
    static String novoPedido() {
        String letras = "abcdefghijkmnpqrstuvwxyz23456789";
        SecureRandom r = new SecureRandom();
        StringBuilder sb = new StringBuilder("#");
        for (int i = 0; i < 6; i++) sb.append(letras.charAt(r.nextInt(letras.length())));
        return sb.toString();
    }

    // ---------- execuções acompanhadas ----------

    /** Uma execução pedida pelo app que ainda não terminou. */
    static final class Vigiada {
        long id;
        String pedido, celulas, ultimaUrl, ultimoTitulo;
        long pedidaEm;
    }

    @SuppressWarnings("unchecked")
    static synchronized List<Vigiada> vigiadas(Context c) {
        List<Vigiada> r = new ArrayList<>();
        try {
            for (Object o : (List<Object>) Json.ler(prefs(c).getString("vigiadas", "[]"))) {
                Map<String, Object> m = (Map<String, Object>) o;
                Vigiada v = new Vigiada();
                v.id = ((Number) m.get("id")).longValue();
                v.pedido = (String) m.get("pedido");
                v.celulas = (String) m.get("celulas");
                v.ultimaUrl = (String) m.get("url");
                v.ultimoTitulo = (String) m.get("titulo");
                v.pedidaEm = ((Number) m.get("em")).longValue();
                r.add(v);
            }
        } catch (RuntimeException e) {
            // lista corrompida: começa de novo
        }
        return r;
    }

    static synchronized void gravar(Context c, List<Vigiada> l) {
        List<Object> lista = new ArrayList<>();
        for (Vigiada v : l) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", v.id);
            m.put("pedido", v.pedido);
            m.put("celulas", v.celulas);
            m.put("url", v.ultimaUrl);
            m.put("titulo", v.ultimoTitulo);
            m.put("em", v.pedidaEm);
            lista.add(m);
        }
        prefs(c).edit().putString("vigiadas", Json.escrever(lista)).apply();
    }

    static void vigiar(Context c, long id, String pedido, String celulas) {
        List<Vigiada> l = vigiadas(c);
        Vigiada v = new Vigiada();
        v.id = id;
        v.pedido = pedido;
        v.celulas = celulas;
        v.pedidaEm = System.currentTimeMillis();
        l.add(v);
        gravar(c, l);
        agendar(c, 60_000);
    }

    /** Agenda a próxima consulta em segundo plano (só com internet). */
    static void agendar(Context c, long atrasoMs) {
        JobScheduler js = c.getSystemService(JobScheduler.class);
        js.schedule(new JobInfo.Builder(JOB, new ComponentName(c, ColabJob.class))
                .setMinimumLatency(atrasoMs)
                .setOverrideDeadline(atrasoMs + 15 * 60_000)
                .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
                .build());
    }

    /**
     * Consulta as execuções vigiadas e avisa por notificação o que mudou (pedido de autorização do
     * Drive, fim). Roda fora da thread principal. Devolve true se ainda há execução em andamento.
     */
    static boolean verificar(Context c) {
        if (!configurado(c)) return false;
        GitHub g = github(c);
        List<Vigiada> l = vigiadas(c);
        List<Vigiada> continuam = new ArrayList<>();
        for (Vigiada v : l) {
            try {
                GitHub.Execucao e = null;
                if (v.id == 0) {
                    e = g.acharPedido(v.pedido);
                    if (e != null) v.id = e.id;
                } else {
                    e = g.execucao(v.id);
                }
                if (e == null) {  // ainda não apareceu na lista (ou sumiu): desiste depois de 1 hora
                    if (System.currentTimeMillis() - v.pedidaEm < 3_600_000) continuam.add(v);
                    continue;
                }
                GitHub.Verificacao ver;
                try {
                    ver = g.verificacao(e);
                } catch (IOException semDetalhes) {
                    ver = null;  // sem os detalhes ao vivo; o fim da execução ainda é avisado
                }
                if (e.terminou()) {
                    notificarFim(c, v, e, ver);
                    continue;
                }
                continuam.add(v);
                String url = ver == null ? null : ver.autorizar();
                if (url != null && !url.equals(v.ultimaUrl)) notificarDrive(c, v, e, url);
                v.ultimaUrl = url;
                if (url == null) c.getSystemService(NotificationManager.class).cancel(NOTIF_BASE + (int) (v.id % 1000) * 2);
                v.ultimoTitulo = ver == null ? null : ver.titulo;
            } catch (IOException erro) {
                continuam.add(v);  // sem internet ou GitHub fora do ar: tenta de novo depois
            }
        }
        gravar(c, continuam);
        return !continuam.isEmpty();
    }

    static void criarCanal(Context c) {
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        if (nm.getNotificationChannel(CANAL) == null) {
            NotificationChannel ch = new NotificationChannel(CANAL, "Colab", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Avisos das células rodando no Colab");
            nm.createNotificationChannel(ch);
        }
    }

    private static PendingIntent abrirTela(Context c) {
        return PendingIntent.getActivity(c, 0, new Intent(c, ColabActivity.class).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    private static void notificarDrive(Context c, Vigiada v, GitHub.Execucao e, String url) {
        criarCanal(c);
        PendingIntent abrir = PendingIntent.getActivity(c, (int) (e.id % 100000),
                new Intent(Intent.ACTION_VIEW, Uri.parse(url)), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        PendingIntent pronto = PendingIntent.getBroadcast(c, (int) (e.id % 100000),
                new Intent(c, ColabReceiver.class).setAction(DRIVE_OK).putExtra("id", e.id),
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        String texto = "O Colab precisa da sua autorização para usar o Google Drive. Toque em Autorizar, "
                + "permita o acesso e depois toque em Já autorizei.";
        c.getSystemService(NotificationManager.class).notify(NOTIF_BASE + (int) (e.id % 1000) * 2,
                new Notification.Builder(c, CANAL).setSmallIcon(R.drawable.ic_notificacao)
                        .setContentTitle("Colab: autorize o Google Drive")
                        .setContentText(texto)
                        .setStyle(new Notification.BigTextStyle().bigText(texto))
                        .setContentIntent(abrirTela(c))
                        .addAction(new Notification.Action.Builder(null, "Autorizar", abrir).build())
                        .addAction(new Notification.Action.Builder(null, "Já autorizei", pronto).build())
                        .setAutoCancel(true)
                        .build());
    }

    private static void notificarFim(Context c, Vigiada v, GitHub.Execucao e, GitHub.Verificacao ver) {
        criarCanal(c);
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        nm.cancel(NOTIF_BASE + (int) (e.id % 1000) * 2);
        String titulo = e.deuCerto() ? "Colab terminou" : "cancelled".equals(e.conclusao) ? "Colab cancelado" : "Colab falhou";
        String texto = ver != null && !ver.titulo.isEmpty() ? ver.titulo
                : e.deuCerto() ? "As células " + v.celulas + " rodaram." : "Veja o registro na tela Colab.";
        if (e.deuCerto() && Boolean.TRUE.equals(ver == null ? null : ver.dados.get("pacote"))) {
            texto += " Toque para baixar o modelo novo.";
        }
        nm.notify(NOTIF_BASE + (int) (e.id % 1000) * 2 + 1, new Notification.Builder(c, CANAL)
                .setSmallIcon(R.drawable.ic_notificacao)
                .setContentTitle(titulo)
                .setContentText(texto)
                .setStyle(new Notification.BigTextStyle().bigText(texto))
                .setContentIntent(abrirTela(c))
                .setAutoCancel(true)
                .build());
    }

    /** "há 5 min", "há 2 h" */
    static String ha(long quando) {
        if (quando <= 0) return "";
        long s = Math.max(0, (System.currentTimeMillis() - quando) / 1000);
        if (s < 60) return "agora";
        if (s < 3600) return "há " + s / 60 + " min";
        if (s < 86400) return String.format(Locale.getDefault(), "há %d h %02d min", s / 3600, s % 3600 / 60);
        return "há " + s / 86400 + " dia" + (s / 86400 > 1 ? "s" : "");
    }
}
