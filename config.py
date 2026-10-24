"""Presets de tamanho. Escolha com: python train.py --preset tiny|colab|colab_big|colab_50m|colab_100m"""

PRESETS = {
    # Para testar rápido em CPU (~1-2M de parâmetros).
    "tiny": dict(
        block_size=128, embed_size=128, heads=4, layers=4, dropout=0.1,
        vocab_size=4000, batch_size=32, learning_rate=1e-3,
        max_steps=3000, warmup_steps=100, eval_every=250, eval_iters=20, patience=8,
    ),
    # O tiny com RoPE (como o de 100M), para testar em CPU o caminho sem tabela de posições.
    "tiny_rope": dict(
        block_size=256, embed_size=128, heads=4, layers=4, dropout=0.1, rope=True,
        vocab_size=4000, batch_size=32, learning_rate=1e-3,
        max_steps=3000, warmup_steps=100, eval_every=250, eval_iters=20, patience=8,
    ),
    # Para a GPU gratuita do Colab (~7M de parâmetros). Antes eram ~14M para ~4M de
    # tokens: o modelo decorava os livros (train loss 3.0, val loss 4.9).
    "colab": dict(
        block_size=256, embed_size=256, heads=8, layers=6, dropout=0.2,
        vocab_size=8000, batch_size=64, learning_rate=8e-4,
        max_steps=10000, warmup_steps=300, eval_every=500, eval_iters=40, patience=6,
    ),
    # ~52M de parâmetros, contexto 512 e vocabulário de 16 mil. Precisa de muitos dados
    # (a Wikipédia com 1 milhão de artigos, ~450 M tokens) e de MODO "do_zero" (tokenizer novo).
    # Lote efetivo 32 × 2 (acumulação) × 512 = 32 mil tokens por passo: 15 mil passos ≈ 490 M tokens.
    # T4: ~4–5 h (o GitHub Actions para em 6 h; "continuar" retoma do pretrain_last.pt). A100: ~1 h.
    "colab_50m": dict(
        block_size=512, embed_size=512, heads=8, layers=14, dropout=0.1,
        vocab_size=16000, batch_size=32, accum=2, learning_rate=5e-4,
        max_steps=15000, warmup_steps=750, eval_every=500, eval_iters=30, patience=6,
    ),
    # ~104M de parâmetros (768 dim, 12 camadas, 12 cabeças), contexto 2048 com RoPE (sem tabela de
    # posições) e vocabulário de 24 mil. Feito para ~2 bilhões de tokens (20 por parâmetro): Wikipédia
    # inteira + livros + Corpus Carolina + parte do GigaVerbo (prepare_data.py --carolina --gigaverbo).
    # Lote efetivo 16 × 8 (acumulação) × 2048 = 262 mil tokens por passo: 8 mil passos ≈ 2,1 bilhões.
    # Precisa de A100 (~4–6 h; o GitHub Actions para em 6 h e "continuar" retoma do pretrain_last.pt).
    # O tokenizer é treinado numa amostra de 1,5 GB (tokenizer_mb), não nos ~8 GB de texto.
    "colab_100m": dict(
        block_size=2048, embed_size=768, heads=12, layers=12, dropout=0.0, rope=True,
        vocab_size=24000, batch_size=16, accum=8, learning_rate=5e-4, tokenizer_mb=1500,
        max_steps=8000, warmup_steps=400, eval_every=250, eval_iters=40, patience=8,
    ),
    # Modelo maior (~14M): use se o train.py mostrar 30M+ tokens.
    "colab_big": dict(
        block_size=256, embed_size=384, heads=6, layers=6, dropout=0.15,
        vocab_size=8000, batch_size=64, learning_rate=6e-4,
        max_steps=15000, warmup_steps=500, eval_every=500, eval_iters=40, patience=6,
    ),
}
