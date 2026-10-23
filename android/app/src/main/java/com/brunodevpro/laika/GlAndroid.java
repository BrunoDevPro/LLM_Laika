package com.brunodevpro.laika;

import android.opengl.EGL14;
import android.opengl.EGLConfig;
import android.opengl.EGLContext;
import android.opengl.EGLDisplay;
import android.opengl.EGLExt;
import android.opengl.EGLSurface;
import android.opengl.GLES20;
import android.opengl.GLES30;
import android.opengl.GLES31;

import com.brunodevpro.laika.core.treino.Gl;

import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * A GPU do celular para o treino: OpenGL ES 3.1 (compute shaders), num contexto sem tela
 * (pbuffer 1x1). Tem que ser criado e usado sempre na mesma thread.
 */
final class GlAndroid implements Gl {
    private final EGLDisplay display;
    private final EGLContext contexto;
    private final EGLSurface superficie;

    GlAndroid() {
        display = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
        int[] v = new int[2];
        if (!EGL14.eglInitialize(display, v, 0, v, 1)) throw new IllegalStateException("eglInitialize falhou");
        int[] atr = {EGL14.EGL_RENDERABLE_TYPE, EGLExt.EGL_OPENGL_ES3_BIT_KHR, EGL14.EGL_SURFACE_TYPE, EGL14.EGL_PBUFFER_BIT,
                EGL14.EGL_NONE};
        EGLConfig[] cfg = new EGLConfig[1];
        int[] n = new int[1];
        if (!EGL14.eglChooseConfig(display, atr, 0, cfg, 0, 1, n, 0) || n[0] == 0) {
            throw new IllegalStateException("esta GPU não tem OpenGL ES 3");
        }
        contexto = EGL14.eglCreateContext(display, cfg[0], EGL14.EGL_NO_CONTEXT,
                new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION, 3, EGL14.EGL_NONE}, 0);
        if (contexto == null || contexto == EGL14.EGL_NO_CONTEXT) throw new IllegalStateException("eglCreateContext falhou");
        superficie = EGL14.eglCreatePbufferSurface(display, cfg[0], new int[]{EGL14.EGL_WIDTH, 1, EGL14.EGL_HEIGHT, 1,
                EGL14.EGL_NONE}, 0);
        if (!EGL14.eglMakeCurrent(display, superficie, superficie, contexto)) throw new IllegalStateException("eglMakeCurrent falhou");
        int[] maj = new int[1], min = new int[1];
        GLES30.glGetIntegerv(GLES30.GL_MAJOR_VERSION, maj, 0);
        GLES30.glGetIntegerv(GLES30.GL_MINOR_VERSION, min, 0);
        if (maj[0] < 3 || (maj[0] == 3 && min[0] < 1)) {
            fechar();
            throw new IllegalStateException("a GPU tem OpenGL ES " + maj[0] + "." + min[0]
                    + "; o treino precisa do 3.1 (compute shaders)");
        }
    }

    private static void erro(String onde) {
        int e = GLES20.glGetError();
        if (e == GLES20.GL_OUT_OF_MEMORY) throw new IllegalStateException("a GPU ficou sem memória (" + onde + "); use um micro-lote menor");
        if (e != GLES20.GL_NO_ERROR) throw new IllegalStateException(String.format("erro de OpenGL 0x%x em %s", e, onde));
    }

    @Override
    public int programa(String fonte) {
        int sh = GLES20.glCreateShader(GLES31.GL_COMPUTE_SHADER);
        GLES20.glShaderSource(sh, fonte);
        GLES20.glCompileShader(sh);
        int[] ok = new int[1];
        GLES20.glGetShaderiv(sh, GLES20.GL_COMPILE_STATUS, ok, 0);
        if (ok[0] == 0) throw new IllegalStateException("shader não compilou: " + GLES20.glGetShaderInfoLog(sh));
        int p = GLES20.glCreateProgram();
        GLES20.glAttachShader(p, sh);
        GLES20.glLinkProgram(p);
        GLES20.glGetProgramiv(p, GLES20.GL_LINK_STATUS, ok, 0);
        if (ok[0] == 0) throw new IllegalStateException("shader não ligou: " + GLES20.glGetProgramInfoLog(p));
        GLES20.glDeleteShader(sh);
        return p;
    }

    @Override
    public int buffer(long bytes) {
        if (bytes > Integer.MAX_VALUE) throw new IllegalStateException("buffer grande demais");
        int[] id = new int[1];
        GLES20.glGenBuffers(1, id, 0);
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, id[0]);
        GLES20.glBufferData(GLES31.GL_SHADER_STORAGE_BUFFER, (int) bytes, null, GLES30.GL_DYNAMIC_COPY);
        erro("criar buffer de " + (bytes >> 20) + " MB");
        return id[0];
    }

    @Override
    public void apagarBuffer(int b) {
        GLES20.glDeleteBuffers(1, new int[]{b}, 0);
    }

    @Override
    public void escrever(int b, long desl, ByteBuffer dados) {
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, b);
        dados.rewind();
        GLES20.glBufferSubData(GLES31.GL_SHADER_STORAGE_BUFFER, (int) desl, dados.remaining(), dados);
    }

    @Override
    public void ler(int b, long desl, ByteBuffer destino) {
        GLES31.glMemoryBarrier(GLES31.GL_BUFFER_UPDATE_BARRIER_BIT | GLES31.GL_SHADER_STORAGE_BARRIER_BIT);
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, b);
        Buffer m = GLES30.glMapBufferRange(GLES31.GL_SHADER_STORAGE_BUFFER, (int) desl, destino.remaining(),
                GLES30.GL_MAP_READ_BIT);
        if (m == null) throw new IllegalStateException("não consegui ler da GPU");
        ByteBuffer bb = ((ByteBuffer) m).order(ByteOrder.nativeOrder());
        destino.put(bb);
        GLES30.glUnmapBuffer(GLES31.GL_SHADER_STORAGE_BUFFER);
    }

    @Override
    public void usar(int p) {
        GLES20.glUseProgram(p);
    }

    @Override
    public void ligar(int binding, int b) {
        GLES30.glBindBufferBase(GLES31.GL_SHADER_STORAGE_BUFFER, binding, b);
    }

    @Override
    public int local(int p, String nome) {
        return GLES20.glGetUniformLocation(p, nome);
    }

    @Override
    public void uniformI(int l, int v) {
        GLES20.glUniform1i(l, v);
    }

    @Override
    public void uniformF(int l, float v) {
        GLES20.glUniform1f(l, v);
    }

    @Override
    public void despachar(int x, int y, int z) {
        GLES31.glDispatchCompute(x, y, z);
    }

    @Override
    public void barreira() {
        GLES31.glMemoryBarrier(GLES31.GL_SHADER_STORAGE_BARRIER_BIT | GLES31.GL_BUFFER_UPDATE_BARRIER_BIT);
    }

    @Override
    public void terminar() {
        GLES20.glFinish();
    }

    @Override
    public String descricao() {
        return GLES20.glGetString(GLES20.GL_RENDERER) + " · " + GLES20.glGetString(GLES20.GL_VERSION);
    }

    @Override
    public long maiorBuffer() {
        long[] v = new long[1];
        GLES30.glGetInteger64v(GLES31.GL_MAX_SHADER_STORAGE_BLOCK_SIZE, v, 0);
        return v[0] > 0 ? v[0] : 128L << 20;
    }

    @Override
    public void fechar() {
        EGL14.eglMakeCurrent(display, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_CONTEXT);
        EGL14.eglDestroySurface(display, superficie);
        EGL14.eglDestroyContext(display, contexto);
        EGL14.eglTerminate(display);
    }
}
