"""Presets de tamanho. Escolha com: python train.py --preset tiny|colab"""

PRESETS = {
    # Para testar rápido em CPU (~1-2M de parâmetros).
    "tiny": dict(
        block_size=128, embed_size=128, heads=4, layers=4, dropout=0.1,
        vocab_size=4000, batch_size=32, learning_rate=1e-3,
        max_steps=3000, warmup_steps=100, eval_every=250, eval_iters=20, patience=8,
    ),
    # Para a GPU gratuita do Colab (~15M de parâmetros).
    "colab": dict(
        block_size=256, embed_size=384, heads=6, layers=6, dropout=0.1,
        vocab_size=8000, batch_size=64, learning_rate=6e-4,
        max_steps=10000, warmup_steps=300, eval_every=500, eval_iters=30, patience=8,
    ),
}
