"""Presets de tamanho. Escolha com: python train.py --preset tiny|colab"""

PRESETS = {
    # Para testar rápido em CPU (~1-2M de parâmetros).
    "tiny": dict(
        block_size=128, embed_size=128, heads=4, layers=4, dropout=0.1,
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
    # Modelo maior (~14M): use se o train.py mostrar 30M+ tokens.
    "colab_big": dict(
        block_size=256, embed_size=384, heads=6, layers=6, dropout=0.15,
        vocab_size=8000, batch_size=64, learning_rate=6e-4,
        max_steps=15000, warmup_steps=500, eval_every=500, eval_iters=40, patience=6,
    ),
}
