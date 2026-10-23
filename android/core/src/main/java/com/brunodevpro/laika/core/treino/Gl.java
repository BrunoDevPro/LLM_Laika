package com.brunodevpro.laika.core.treino;

import java.nio.ByteBuffer;

/**
 * O pedaço do OpenGL ES 3.1 (compute shaders) que o treino usa. No celular é o GLES31 do
 * Android; nos testes do PC é o Mesa (GPU por software), para conferir as contas com o PyTorch.
 * Todas as chamadas acontecem na mesma thread (a do contexto).
 */
public interface Gl {
    /** Compila e liga um compute shader (GLSL ES 3.10). */
    int programa(String fonte);

    /** Cria um buffer de armazenamento (SSBO) com `bytes` bytes. */
    int buffer(long bytes);

    void apagarBuffer(int buffer);

    /** Copia `dados` (ByteBuffer direto, ordem nativa) para o buffer a partir de `deslocamento` bytes. */
    void escrever(int buffer, long deslocamento, ByteBuffer dados);

    /** Lê `destino.remaining()` bytes do buffer a partir de `deslocamento`. */
    void ler(int buffer, long deslocamento, ByteBuffer destino);

    void usar(int programa);

    void ligar(int binding, int buffer);

    int local(int programa, String uniforme);

    void uniformI(int local, int valor);

    void uniformF(int local, float valor);

    void despachar(int x, int y, int z);

    /** Espera as escritas dos shaders anteriores ficarem visíveis para os próximos. */
    void barreira();

    /** Espera a GPU terminar tudo. */
    void terminar();

    /** Nome da GPU e versão (para mostrar no app). */
    String descricao();

    /** Maior buffer de armazenamento que um shader pode ler (GL_MAX_SHADER_STORAGE_BLOCK_SIZE). */
    long maiorBuffer();

    void fechar();
}
