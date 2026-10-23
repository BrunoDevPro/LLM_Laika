package com.brunodevpro.laika.core.treino;

/**
 * Compute shaders (GLSL ES 3.10) do treino: forward e backward do TinyLLM escritos à mão,
 * como no llm.c. Tudo em float32. Os buffers grandes recebem "offsets" (em floats) como
 * uniformes, porque os parâmetros e gradientes ficam num buffer só.
 */
final class Shaders {
    private Shaders() {
    }

    static final String CABECALHO = "#version 310 es\nprecision highp float;\nprecision highp int;\n";

    /** Índice linear para despachos 2D (mais de 65535 grupos). 128 threads por grupo: o mínimo garantido no ES 3.1. */
    static final String INDICE = "int indice() { return int(gl_WorkGroupID.y * gl_NumWorkGroups.x + gl_WorkGroupID.x) * 128 "
            + "+ int(gl_LocalInvocationID.x); }\n";

    /** Número aleatório em [0,1) a partir de (semente, índice): o dropout refaz a mesma máscara no backward. */
    static final String ALEATORIO = "float aleatorio(int semente, int i) {\n"
            + "  uint h = uint(i) * 747796405u + uint(semente) * 2891336453u + 1442695041u;\n"
            + "  h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;\n"
            + "  h = (h >> 22u) ^ h;\n"
            + "  h ^= h >> 16u; h *= 2246822519u; h ^= h >> 13u;\n"
            + "  return float(h >> 8u) / 16777216.0;\n"
            + "}\n";

    /**
     * C[i,j] = alpha * sum_k A(i,k) B(k,j) (+ bias[j]) (+ C[i,j] se acumular).
     * A(i,k) = A[offA + i*sAi + k*sAk] etc.: com os passos certos o mesmo shader faz
     * x·Wᵀ (forward), dout·W (gradiente da entrada) e doutᵀ·x (gradiente dos pesos).
     * Bloco de 64x64 saídas por grupo de 128 threads (cada uma calcula 8x4).
     */
    static final String MATMUL = CABECALHO
            + "layout(local_size_x = 16, local_size_y = 8) in;\n"
            + "layout(std430, binding = 0) readonly buffer BA { float A[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BB { float B[]; };\n"
            + "layout(std430, binding = 2) buffer BC { float C[]; };\n"
            + "layout(std430, binding = 3) readonly buffer BV { float vies[]; };\n"
            + "uniform int M; uniform int N; uniform int K;\n"
            + "uniform int offA; uniform int sAi; uniform int sAk;\n"
            + "uniform int offB; uniform int sBk; uniform int sBj;\n"
            + "uniform int offC; uniform int sCi; uniform int sCj;\n"
            + "uniform int offVies; uniform int temVies; uniform int acumular; uniform float alpha;\n"
            + "shared float As[1024];\n"
            + "shared float Bs[1024];\n"
            + "void main() {\n"
            + "  int lx = int(gl_LocalInvocationID.x), ly = int(gl_LocalInvocationID.y);\n"
            + "  int tid = ly * 16 + lx;\n"
            + "  int i0 = int(gl_WorkGroupID.y) * 64, j0 = int(gl_WorkGroupID.x) * 64;\n"
            + "  float acc[32];\n"
            + "  for (int q = 0; q < 32; q++) acc[q] = 0.0;\n"
            + "  for (int k0 = 0; k0 < K; k0 += 16) {\n"
            + "    for (int q = 0; q < 8; q++) {\n"
            + "      int e = tid + q * 128;\n"
            // Ordem de leitura que deixa threads vizinhas lendo endereços vizinhos.
            + "      int kk, ii;\n"
            + "      if (sAk == 1) { ii = e / 16; kk = e - ii * 16; } else { kk = e / 64; ii = e - kk * 64; }\n"
            + "      int gi = i0 + ii, gk = k0 + kk;\n"
            + "      As[kk * 64 + ii] = (gi < M && gk < K) ? A[offA + gi * sAi + gk * sAk] : 0.0;\n"
            + "      int jj;\n"
            + "      if (sBk == 1) { jj = e / 16; kk = e - jj * 16; } else { kk = e / 64; jj = e - kk * 64; }\n"
            + "      int gj = j0 + jj; gk = k0 + kk;\n"
            + "      Bs[kk * 64 + jj] = (gj < N && gk < K) ? B[offB + gk * sBk + gj * sBj] : 0.0;\n"
            + "    }\n"
            + "    barrier();\n"
            + "    for (int kk = 0; kk < 16; kk++) {\n"
            + "      float a[8]; float b[4];\n"
            + "      for (int r = 0; r < 8; r++) a[r] = As[kk * 64 + ly + 8 * r];\n"
            + "      for (int c = 0; c < 4; c++) b[c] = Bs[kk * 64 + lx + 16 * c];\n"
            + "      for (int r = 0; r < 8; r++) for (int c = 0; c < 4; c++) acc[r * 4 + c] += a[r] * b[c];\n"
            + "    }\n"
            + "    barrier();\n"
            + "  }\n"
            + "  for (int r = 0; r < 8; r++) {\n"
            + "    int i = i0 + ly + 8 * r;\n"
            + "    if (i >= M) continue;\n"
            + "    for (int c = 0; c < 4; c++) {\n"
            + "      int j = j0 + lx + 16 * c;\n"
            + "      if (j >= N) continue;\n"
            + "      float v = alpha * acc[r * 4 + c];\n"
            + "      if (temVies == 1) v += vies[offVies + j];\n"
            + "      int idx = offC + i * sCi + j * sCj;\n"
            + "      C[idx] = (acumular == 1) ? C[idx] + v : v;\n"
            + "    }\n"
            + "  }\n"
            + "}\n";

    /** Operações elemento a elemento (op escolhe a conta). */
    static final String ELEMENTOS = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) buffer BX { float X[]; };\n"
            + "layout(std430, binding = 1) buffer BY { float Y[]; };\n"
            + "layout(std430, binding = 2) buffer BZ { float Z[]; };\n"
            + "uniform int n; uniform int op; uniform int offX; uniform int offY; uniform int offZ;\n"
            + "uniform float valor; uniform int semente; uniform float p;\n"
            + INDICE + ALEATORIO
            + "float erf_(float x) {\n"
            + "  float z = abs(x); float t = 1.0 / (1.0 + 0.5 * z);\n"
            + "  float r = t * exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806"
            + " + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));\n"
            + "  return x >= 0.0 ? 1.0 - r : r - 1.0;\n"
            + "}\n"
            + "void main() {\n"
            + "  int i = indice();\n"
            + "  if (i >= n) return;\n"
            + "  if (op == 0) { Z[offZ + i] = valor; }\n"                                   // preencher
            + "  else if (op == 1) { Z[offZ + i] = X[offX + i]; }\n"                       // copiar
            + "  else if (op == 2) { Z[offZ + i] = X[offX + i] + Y[offY + i]; }\n"         // somar
            + "  else if (op == 3) { Z[offZ + i] += X[offX + i]; }\n"                      // acumular
            + "  else if (op == 4) {\n"                                                     // GELU exato
            + "    float x = X[offX + i]; Z[offZ + i] = 0.5 * x * (1.0 + erf_(x * 0.70710678118654752));\n"
            + "  } else if (op == 5) {\n"                                                   // gradiente do GELU
            + "    float x = Y[offY + i];\n"
            + "    float cdf = 0.5 * (1.0 + erf_(x * 0.70710678118654752));\n"
            + "    float pdf = exp(-0.5 * x * x) * 0.3989422804014327;\n"
            + "    Z[offZ + i] = X[offX + i] * (cdf + x * pdf);\n"
            + "  } else if (op == 6) {\n"                                                   // dropout (in-place)
            + "    Z[offZ + i] = aleatorio(semente, i) < p ? 0.0 : Z[offZ + i] / (1.0 - p);\n"
            + "  } else if (op == 7) { Z[offZ + i] *= valor; }\n"                          // escalar
            + "}\n";

    /** LayerNorm (forward): um grupo por linha; guarda média e 1/desvio para o backward. */
    static final String LN_FRENTE = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BI { float inp[]; };\n"
            + "layout(std430, binding = 1) buffer BO { float outp[]; };\n"
            + "layout(std430, binding = 2) readonly buffer BP { float par[]; };\n"
            + "layout(std430, binding = 3) buffer BS { float stat[]; };\n"
            + "uniform int D; uniform int offI; uniform int offO; uniform int offW; uniform int offB; uniform int offS;"
            + " uniform int linhas;\n"
            + "shared float red[64];\n"
            + "void main() {\n"
            + "  int row = int(gl_WorkGroupID.x), t = int(gl_LocalInvocationID.x);\n"
            + "  int base = offI + row * D;\n"
            + "  float s = 0.0;\n"
            + "  for (int c = t; c < D; c += 64) s += inp[base + c];\n"
            + "  red[t] = s; barrier();\n"
            + "  for (int k = 32; k > 0; k >>= 1) { if (t < k) red[t] += red[t + k]; barrier(); }\n"
            + "  float media = red[0] / float(D);\n"
            + "  barrier();\n"
            + "  s = 0.0;\n"
            + "  for (int c = t; c < D; c += 64) { float d = inp[base + c] - media; s += d * d; }\n"
            + "  red[t] = s; barrier();\n"
            + "  for (int k = 32; k > 0; k >>= 1) { if (t < k) red[t] += red[t + k]; barrier(); }\n"
            + "  float rstd = 1.0 / sqrt(red[0] / float(D) + 1e-5);\n"
            + "  for (int c = t; c < D; c += 64) outp[offO + row * D + c] = (inp[base + c] - media) * rstd * par[offW + c] + par[offB + c];\n"
            + "  if (t == 0) { stat[offS + row] = media; stat[offS + linhas + row] = rstd; }\n"
            + "}\n";

    /** LayerNorm (backward da entrada): dinp += ... (um grupo por linha). */
    static final String LN_TRAS = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BD { float dout[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BI { float inp[]; };\n"
            + "layout(std430, binding = 2) readonly buffer BP { float par[]; };\n"
            + "layout(std430, binding = 3) readonly buffer BS { float stat[]; };\n"
            + "layout(std430, binding = 4) buffer BG { float dinp[]; };\n"
            + "uniform int D; uniform int offD; uniform int offI; uniform int offW; uniform int offS; uniform int offG;"
            + " uniform int linhas;\n"
            + "shared float r1[64]; shared float r2[64];\n"
            + "void main() {\n"
            + "  int row = int(gl_WorkGroupID.x), t = int(gl_LocalInvocationID.x);\n"
            + "  float media = stat[offS + row], rstd = stat[offS + linhas + row];\n"
            + "  float a = 0.0, b = 0.0;\n"
            + "  for (int c = t; c < D; c += 64) {\n"
            + "    float norm = (inp[offI + row * D + c] - media) * rstd;\n"
            + "    float dn = dout[offD + row * D + c] * par[offW + c];\n"
            + "    a += dn; b += dn * norm;\n"
            + "  }\n"
            + "  r1[t] = a; r2[t] = b; barrier();\n"
            + "  for (int k = 32; k > 0; k >>= 1) { if (t < k) { r1[t] += r1[t + k]; r2[t] += r2[t + k]; } barrier(); }\n"
            + "  float mdn = r1[0] / float(D), mdnn = r2[0] / float(D);\n"
            + "  for (int c = t; c < D; c += 64) {\n"
            + "    float norm = (inp[offI + row * D + c] - media) * rstd;\n"
            + "    float dn = dout[offD + row * D + c] * par[offW + c];\n"
            + "    dinp[offG + row * D + c] += (dn - mdn - norm * mdnn) * rstd;\n"
            + "  }\n"
            + "}\n";

    /** LayerNorm (gradiente do peso e do viés): uma thread por coluna, somando as linhas. */
    static final String LN_TRAS_PESOS = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BD { float dout[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BI { float inp[]; };\n"
            + "layout(std430, binding = 3) readonly buffer BS { float stat[]; };\n"
            + "layout(std430, binding = 4) buffer BG { float grad[]; };\n"
            + "uniform int D; uniform int offD; uniform int offI; uniform int offS; uniform int linhas;"
            + " uniform int offGW; uniform int offGB;\n"
            + "void main() {\n"
            + "  int c = int(gl_GlobalInvocationID.x);\n"
            + "  if (c >= D) return;\n"
            + "  float dw = 0.0, db = 0.0;\n"
            + "  for (int r = 0; r < linhas; r++) {\n"
            + "    float norm = (inp[offI + r * D + c] - stat[offS + r]) * stat[offS + linhas + r];\n"
            + "    float d = dout[offD + r * D + c];\n"
            + "    dw += d * norm; db += d;\n"
            + "  }\n"
            + "  grad[offGW + c] += dw; grad[offGB + c] += db;\n"
            + "}\n";

    /** Soma das colunas (gradiente do viés de uma camada linear). */
    static final String SOMA_COLUNAS = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BD { float dout[]; };\n"
            + "layout(std430, binding = 1) buffer BG { float grad[]; };\n"
            + "uniform int N; uniform int linhas; uniform int offD; uniform int offG;\n"
            + "void main() {\n"
            + "  int c = int(gl_GlobalInvocationID.x);\n"
            + "  if (c >= N) return;\n"
            + "  float s = 0.0;\n"
            + "  for (int r = 0; r < linhas; r++) s += dout[offD + r * N + c];\n"
            + "  grad[offG + c] += s;\n"
            + "}\n";

    /**
     * Atenção causal (forward): uma thread por (lote, cabeça, posição). Guarda as probabilidades
     * (antes do dropout) para o backward; o dropout da atenção é refeito pela semente.
     */
    static final String ATENCAO_FRENTE = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BQ { float qkv[]; };\n"
            + "layout(std430, binding = 1) buffer BA { float att[]; };\n"
            + "layout(std430, binding = 2) buffer BO { float outp[]; };\n"
            + "uniform int B; uniform int T; uniform int H; uniform int hd; uniform int TMAX;\n"
            + "uniform int semente; uniform float p;\n"
            + ALEATORIO
            + "void main() {\n"
            + "  int idx = int(gl_GlobalInvocationID.x);\n"
            + "  if (idx >= B * H * T) return;\n"
            + "  int t = idx % T, h = (idx / T) % H, b = idx / (T * H);\n"
            + "  int D = H * hd, C3 = 3 * D;\n"
            + "  int q0 = (b * T + t) * C3 + h * hd;\n"
            + "  int a0 = ((b * H + h) * TMAX + t) * TMAX;\n"
            + "  float escala = 1.0 / sqrt(float(hd));\n"
            + "  float mx = -1e30;\n"
            + "  for (int t2 = 0; t2 <= t; t2++) {\n"
            + "    int k0 = (b * T + t2) * C3 + D + h * hd;\n"
            + "    float s = 0.0;\n"
            + "    for (int i = 0; i < hd; i++) s += qkv[q0 + i] * qkv[k0 + i];\n"
            + "    s *= escala; att[a0 + t2] = s; mx = max(mx, s);\n"
            + "  }\n"
            + "  float soma = 0.0;\n"
            + "  for (int t2 = 0; t2 <= t; t2++) { float e = exp(att[a0 + t2] - mx); att[a0 + t2] = e; soma += e; }\n"
            + "  float acc[64];\n"
            + "  for (int i = 0; i < hd; i++) acc[i] = 0.0;\n"
            + "  for (int t2 = 0; t2 <= t; t2++) {\n"
            + "    float pr = att[a0 + t2] / soma; att[a0 + t2] = pr;\n"
            + "    float pd = pr;\n"
            + "    if (p > 0.0) pd = aleatorio(semente, a0 + t2) < p ? 0.0 : pr / (1.0 - p);\n"
            + "    int v0 = (b * T + t2) * C3 + 2 * D + h * hd;\n"
            + "    for (int i = 0; i < hd; i++) acc[i] += pd * qkv[v0 + i];\n"
            + "  }\n"
            + "  for (int t2 = t + 1; t2 < T; t2++) att[a0 + t2] = 0.0;\n"
            + "  for (int i = 0; i < hd; i++) outp[(b * T + t) * D + h * hd + i] = acc[i];\n"
            + "}\n";

    /** Atenção (backward, parte 1): por linha t — gradiente das pontuações (guardado em datt) e dq. */
    static final String ATENCAO_TRAS1 = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BQ { float qkv[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BA { float att[]; };\n"
            + "layout(std430, binding = 2) readonly buffer BD { float dout[]; };\n"
            + "layout(std430, binding = 3) buffer BT { float datt[]; };\n"
            + "layout(std430, binding = 4) buffer BG { float dqkv[]; };\n"
            + "uniform int B; uniform int T; uniform int H; uniform int hd; uniform int TMAX;\n"
            + "uniform int semente; uniform float p;\n"
            + ALEATORIO
            + "void main() {\n"
            + "  int idx = int(gl_GlobalInvocationID.x);\n"
            + "  if (idx >= B * H * T) return;\n"
            + "  int t = idx % T, h = (idx / T) % H, b = idx / (T * H);\n"
            + "  int D = H * hd, C3 = 3 * D;\n"
            + "  int a0 = ((b * H + h) * TMAX + t) * TMAX;\n"
            + "  int o0 = (b * T + t) * D + h * hd;\n"
            + "  float escala = 1.0 / sqrt(float(hd));\n"
            + "  float s = 0.0;\n"
            + "  for (int t2 = 0; t2 <= t; t2++) {\n"
            + "    int v0 = (b * T + t2) * C3 + 2 * D + h * hd;\n"
            + "    float g = 0.0;\n"
            + "    for (int i = 0; i < hd; i++) g += dout[o0 + i] * qkv[v0 + i];\n"
            + "    if (p > 0.0) g = aleatorio(semente, a0 + t2) < p ? 0.0 : g / (1.0 - p);\n"
            + "    datt[a0 + t2] = g;\n"
            + "    s += att[a0 + t2] * g;\n"
            + "  }\n"
            + "  float dq[64];\n"
            + "  for (int i = 0; i < hd; i++) dq[i] = 0.0;\n"
            + "  for (int t2 = 0; t2 <= t; t2++) {\n"
            + "    float d = att[a0 + t2] * (datt[a0 + t2] - s) * escala;\n"
            + "    datt[a0 + t2] = d;\n"
            + "    int k0 = (b * T + t2) * C3 + D + h * hd;\n"
            + "    for (int i = 0; i < hd; i++) dq[i] += d * qkv[k0 + i];\n"
            + "  }\n"
            + "  int q0 = (b * T + t) * C3 + h * hd;\n"
            + "  for (int i = 0; i < hd; i++) dqkv[q0 + i] = dq[i];\n"
            + "}\n";

    /** Atenção (backward, parte 2): por coluna t2 — dk e dv. */
    static final String ATENCAO_TRAS2 = CABECALHO
            + "layout(local_size_x = 64) in;\n"
            + "layout(std430, binding = 0) readonly buffer BQ { float qkv[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BA { float att[]; };\n"
            + "layout(std430, binding = 2) readonly buffer BD { float dout[]; };\n"
            + "layout(std430, binding = 3) readonly buffer BT { float datt[]; };\n"
            + "layout(std430, binding = 4) buffer BG { float dqkv[]; };\n"
            + "uniform int B; uniform int T; uniform int H; uniform int hd; uniform int TMAX;\n"
            + "uniform int semente; uniform float p;\n"
            + ALEATORIO
            + "void main() {\n"
            + "  int idx = int(gl_GlobalInvocationID.x);\n"
            + "  if (idx >= B * H * T) return;\n"
            + "  int t2 = idx % T, h = (idx / T) % H, b = idx / (T * H);\n"
            + "  int D = H * hd, C3 = 3 * D;\n"
            + "  float dk[64]; float dv[64];\n"
            + "  for (int i = 0; i < hd; i++) { dk[i] = 0.0; dv[i] = 0.0; }\n"
            + "  for (int t = t2; t < T; t++) {\n"
            + "    int a = ((b * H + h) * TMAX + t) * TMAX + t2;\n"
            + "    float d = datt[a];\n"
            + "    float pd = att[a];\n"
            + "    if (p > 0.0) pd = aleatorio(semente, a) < p ? 0.0 : pd / (1.0 - p);\n"
            + "    int q0 = (b * T + t) * C3 + h * hd;\n"
            + "    int o0 = (b * T + t) * D + h * hd;\n"
            + "    for (int i = 0; i < hd; i++) { dk[i] += d * qkv[q0 + i]; dv[i] += pd * dout[o0 + i]; }\n"
            + "  }\n"
            + "  int k0 = (b * T + t2) * C3 + D + h * hd;\n"
            + "  for (int i = 0; i < hd; i++) { dqkv[k0 + i] = dk[i]; dqkv[k0 + D + i] = dv[i]; }\n"
            + "}\n";

    /** Embedding (forward): x = tok_emb[token] + pos_emb[posição]. */
    static final String EMBED_FRENTE = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) readonly buffer BT { int tok[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BP { float par[]; };\n"
            + "layout(std430, binding = 2) buffer BO { float outp[]; };\n"
            + "uniform int n; uniform int D; uniform int T; uniform int offTok; uniform int offPos;\n"
            + INDICE
            + "void main() {\n"
            + "  int i = indice();\n"
            + "  if (i >= n) return;\n"
            + "  int r = i / D, c = i - r * D;\n"
            + "  outp[i] = par[offTok + tok[r] * D + c] + par[offPos + (r % T) * D + c];\n"
            + "}\n";

    /**
     * Embedding (backward): as posições de cada token vêm agrupadas (CSR montado na CPU),
     * então cada thread soma as linhas de um token sem precisar de soma atômica.
     * csr = [token_0, inicio_0, fim_0, token_1, ...] seguido da lista de linhas.
     */
    static final String EMBED_TRAS_TOK = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) readonly buffer BC { int csr[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BD { float dx[]; };\n"
            + "layout(std430, binding = 2) buffer BG { float grad[]; };\n"
            + "uniform int unicos; uniform int D; uniform int offTok; uniform int offLista;\n"
            + INDICE
            + "void main() {\n"
            + "  int i = indice();\n"
            + "  if (i >= unicos * D) return;\n"
            + "  int u = i / D, c = i - u * D;\n"
            + "  int tok = csr[u * 3], ini = csr[u * 3 + 1], fim = csr[u * 3 + 2];\n"
            + "  float s = 0.0;\n"
            + "  for (int k = ini; k < fim; k++) s += dx[csr[offLista + k] * D + c];\n"
            + "  grad[offTok + tok * D + c] += s;\n"
            + "}\n";

    static final String EMBED_TRAS_POS = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) readonly buffer BD { float dx[]; };\n"
            + "layout(std430, binding = 1) buffer BG { float grad[]; };\n"
            + "uniform int B; uniform int T; uniform int D; uniform int offPos;\n"
            + INDICE
            + "void main() {\n"
            + "  int i = indice();\n"
            + "  if (i >= T * D) return;\n"
            + "  float s = 0.0;\n"
            + "  for (int b = 0; b < B; b++) s += dx[b * T * D + i];\n"
            + "  grad[offPos + i] += s;\n"
            + "}\n";

    /**
     * Entropia cruzada: um grupo por linha. Troca os logits pelo gradiente
     * (softmax - one_hot) * escala e guarda a perda da linha. Alvo < 0 = ignorar (pergunta, padding).
     */
    static final String ENTROPIA = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) buffer BL { float lg[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BT { int alvo[]; };\n"
            + "layout(std430, binding = 2) buffer BP { float perda[]; };\n"
            + "uniform int V; uniform float escala;\n"
            + "shared float red[128];\n"
            + "void main() {\n"
            + "  int row = int(gl_WorkGroupID.y * gl_NumWorkGroups.x + gl_WorkGroupID.x);\n"
            + "  int t = int(gl_LocalInvocationID.x);\n"
            + "  int base = row * V;\n"
            + "  int a = alvo[row];\n"
            + "  if (a < 0) {\n"
            + "    for (int v = t; v < V; v += 128) lg[base + v] = 0.0;\n"
            + "    if (t == 0) perda[row] = 0.0;\n"
            + "    return;\n"
            + "  }\n"
            + "  float mx = -1e30;\n"
            + "  for (int v = t; v < V; v += 128) mx = max(mx, lg[base + v]);\n"
            + "  red[t] = mx; barrier();\n"
            + "  for (int k = 64; k > 0; k >>= 1) { if (t < k) red[t] = max(red[t], red[t + k]); barrier(); }\n"
            + "  mx = red[0]; barrier();\n"
            + "  float s = 0.0;\n"
            + "  for (int v = t; v < V; v += 128) s += exp(lg[base + v] - mx);\n"
            + "  red[t] = s; barrier();\n"
            + "  for (int k = 64; k > 0; k >>= 1) { if (t < k) red[t] += red[t + k]; barrier(); }\n"
            + "  s = red[0];\n"
            + "  float la = lg[base + a];\n"
            + "  barrier();\n"
            + "  for (int v = t; v < V; v += 128) {\n"
            + "    float pr = exp(lg[base + v] - mx) / s;\n"
            + "    lg[base + v] = (pr - (v == a ? 1.0 : 0.0)) * escala;\n"
            + "  }\n"
            + "  if (t == 0) perda[row] = log(s) + mx - la;\n"
            + "}\n";

    /** Soma dos quadrados dos gradientes (parte 1: um valor por grupo). */
    static final String NORMA1 = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) readonly buffer BG { float g[]; };\n"
            + "layout(std430, binding = 1) buffer BP { float parcial[]; };\n"
            + "uniform int n;\n"
            + "shared float red[128];\n"
            + "void main() {\n"
            + "  int t = int(gl_LocalInvocationID.x), grupo = int(gl_WorkGroupID.x), grupos = int(gl_NumWorkGroups.x);\n"
            + "  float s = 0.0;\n"
            + "  for (int i = grupo * 128 + t; i < n; i += grupos * 128) s += g[i] * g[i];\n"
            + "  red[t] = s; barrier();\n"
            + "  for (int k = 64; k > 0; k >>= 1) { if (t < k) red[t] += red[t + k]; barrier(); }\n"
            + "  if (t == 0) parcial[grupo] = red[0];\n"
            + "}\n";

    /** Parte 2: norma total e fator de corte (clip_grad_norm_ do PyTorch) em parcial[grupos], [grupos+1]. */
    static final String NORMA2 = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 1) buffer BP { float parcial[]; };\n"
            + "uniform int grupos; uniform float maximo;\n"
            + "shared float red[128];\n"
            + "void main() {\n"
            + "  int t = int(gl_LocalInvocationID.x);\n"
            + "  float s = 0.0;\n"
            + "  for (int i = t; i < grupos; i += 128) s += parcial[i];\n"
            + "  red[t] = s; barrier();\n"
            + "  for (int k = 64; k > 0; k >>= 1) { if (t < k) red[t] += red[t + k]; barrier(); }\n"
            + "  if (t == 0) {\n"
            + "    float norma = sqrt(red[0]);\n"
            + "    parcial[grupos] = norma;\n"
            + "    parcial[grupos + 1] = maximo > 0.0 ? min(1.0, maximo / (norma + 1e-6)) : 1.0;\n"
            + "  }\n"
            + "}\n";

    /** AdamW do PyTorch (weight decay desacoplado), com o fator de corte do gradiente. */
    static final String ADAMW = CABECALHO
            + "layout(local_size_x = 128) in;\n"
            + "layout(std430, binding = 0) buffer BP { float par[]; };\n"
            + "layout(std430, binding = 1) readonly buffer BG { float g[]; };\n"
            + "layout(std430, binding = 2) buffer BM { float m[]; };\n"
            + "layout(std430, binding = 3) buffer BV { float v[]; };\n"
            + "layout(std430, binding = 4) readonly buffer BC { float corte[]; };\n"
            + "uniform int n; uniform int off; uniform int idxCorte;\n"
            + "uniform float lr; uniform float b1; uniform float b2; uniform float eps; uniform float wd;\n"
            + "uniform float c1; uniform float c2;\n"
            + INDICE
            + "void main() {\n"
            + "  int k = indice();\n"
            + "  if (k >= n) return;\n"
            + "  int i = off + k;\n"
            + "  float gr = g[i] * corte[idxCorte];\n"
            + "  float mm = b1 * m[i] + (1.0 - b1) * gr;\n"
            + "  float vv = b2 * v[i] + (1.0 - b2) * gr * gr;\n"
            + "  m[i] = mm; v[i] = vv;\n"
            + "  float pp = par[i] * (1.0 - lr * wd);\n"
            + "  par[i] = pp - lr * (mm / c1) / (sqrt(vv / c2) + eps);\n"
            + "}\n";
}
