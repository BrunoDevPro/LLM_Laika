package com.brunodevpro.laika;

import android.app.job.JobParameters;
import android.app.job.JobService;

/** Consulta em segundo plano as execuções do Colab pedidas pelo app (veja {@link Colab#verificar}). */
public class ColabJob extends JobService {
    @Override
    public boolean onStartJob(JobParameters params) {
        new Thread(() -> {
            boolean continuar = Colab.verificar(this);
            if (continuar) Colab.agendar(this, 3 * 60_000);
            jobFinished(params, false);
        }, "laika-colab").start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters params) {
        return true;
    }
}
