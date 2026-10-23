package com.brunodevpro.laika.core.treino;

import static org.lwjgl.egl.EGL10.EGL_NONE;
import static org.lwjgl.egl.EGL10.EGL_NO_CONTEXT;
import static org.lwjgl.egl.EGL10.EGL_NO_SURFACE;
import static org.lwjgl.egl.EGL12.EGL_RENDERABLE_TYPE;
import static org.lwjgl.egl.EGL10.EGL_SURFACE_TYPE;
import static org.lwjgl.egl.EGL10.EGL_PBUFFER_BIT;

import org.lwjgl.PointerBuffer;
import org.lwjgl.egl.EGL;
import org.lwjgl.egl.EGL10;
import org.lwjgl.egl.EGL12;
import org.lwjgl.egl.EGLCapabilities;
import org.lwjgl.opengles.GLES;
import org.lwjgl.opengles.GLES20;
import org.lwjgl.opengles.GLES30;
import org.lwjgl.opengles.GLES31;
import org.lwjgl.system.MemoryStack;

import java.nio.ByteBuffer;
import java.nio.IntBuffer;

/** Gl no PC: OpenGL ES 3.1 do Mesa (llvmpipe, GPU por software), sem janela. Só para os testes. */
final class GlMesa implements Gl {
    private final long display, contexto;

    GlMesa() {
        EGLCapabilities cliente = EGL.getCapabilities();
        long d = cliente.EGL_EXT_platform_base
                ? org.lwjgl.egl.EXTPlatformBase.eglGetPlatformDisplayEXT(0x31DD /* SURFACELESS_MESA */, 0, (IntBuffer) null)
                : EGL10.eglGetDisplay(0);
        display = d;
        try (MemoryStack s = MemoryStack.stackPush()) {
            IntBuffer maj = s.mallocInt(1), min = s.mallocInt(1);
            if (!EGL10.eglInitialize(display, maj, min)) throw new IllegalStateException("eglInitialize falhou");
            EGL.createDisplayCapabilities(display, maj.get(0), min.get(0));
            EGL12.eglBindAPI(EGL12.EGL_OPENGL_ES_API);
            IntBuffer atr = s.ints(EGL_RENDERABLE_TYPE, 0x40 /* ES3 */, EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_NONE);
            PointerBuffer cfgs = s.mallocPointer(1);
            IntBuffer n = s.mallocInt(1);
            if (!EGL10.eglChooseConfig(display, atr, cfgs, n) || n.get(0) == 0) {
                atr = s.ints(EGL_RENDERABLE_TYPE, 0x40, EGL_NONE);
                if (!EGL10.eglChooseConfig(display, atr, cfgs, n) || n.get(0) == 0) {
                    throw new IllegalStateException("sem configuração EGL para OpenGL ES 3");
                }
            }
            IntBuffer ctx = s.ints(0x3098 /* MAJOR */, 3, 0x30FB /* MINOR */, 1, EGL_NONE);
            contexto = EGL10.eglCreateContext(display, cfgs.get(0), EGL_NO_CONTEXT, ctx);
            if (contexto == EGL_NO_CONTEXT) throw new IllegalStateException("eglCreateContext falhou");
            if (!EGL10.eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, contexto)) {
                throw new IllegalStateException("eglMakeCurrent falhou");
            }
        }
        GLES.createCapabilities();
    }

    @Override
    public int programa(String fonte) {
        int sh = GLES20.glCreateShader(GLES31.GL_COMPUTE_SHADER);
        GLES20.glShaderSource(sh, fonte);
        GLES20.glCompileShader(sh);
        if (GLES20.glGetShaderi(sh, GLES20.GL_COMPILE_STATUS) == 0) {
            throw new IllegalStateException("shader não compilou: " + GLES20.glGetShaderInfoLog(sh));
        }
        int p = GLES20.glCreateProgram();
        GLES20.glAttachShader(p, sh);
        GLES20.glLinkProgram(p);
        if (GLES20.glGetProgrami(p, GLES20.GL_LINK_STATUS) == 0) {
            throw new IllegalStateException("shader não ligou: " + GLES20.glGetProgramInfoLog(p));
        }
        return p;
    }

    @Override
    public int buffer(long bytes) {
        int b = GLES20.glGenBuffers();
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, b);
        GLES20.glBufferData(GLES31.GL_SHADER_STORAGE_BUFFER, bytes, GLES30.GL_DYNAMIC_COPY);
        return b;
    }

    @Override
    public void apagarBuffer(int b) {
        GLES20.glDeleteBuffers(b);
    }

    @Override
    public void escrever(int b, long desl, ByteBuffer dados) {
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, b);
        dados.rewind();
        GLES20.glBufferSubData(GLES31.GL_SHADER_STORAGE_BUFFER, desl, dados);
    }

    @Override
    public void ler(int b, long desl, ByteBuffer destino) {
        GLES31.glMemoryBarrier(GLES31.GL_BUFFER_UPDATE_BARRIER_BIT | GLES31.GL_SHADER_STORAGE_BARRIER_BIT);
        GLES20.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER, b);
        ByteBuffer m = GLES30.glMapBufferRange(GLES31.GL_SHADER_STORAGE_BUFFER, desl, destino.remaining(),
                GLES30.GL_MAP_READ_BIT);
        destino.put(m);
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
        return GLES30.glGetInteger64(GLES31.GL_MAX_SHADER_STORAGE_BLOCK_SIZE);
    }

    @Override
    public void fechar() {
        EGL10.eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
        EGL10.eglDestroyContext(display, contexto);
        EGL10.eglTerminate(display);
    }
}
