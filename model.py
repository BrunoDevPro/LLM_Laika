"""Transformer decoder (estilo GPT) pequeno, em PyTorch puro."""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, embed_size, heads, dropout):
        super().__init__()
        assert embed_size % heads == 0, "embed_size precisa ser divisível por heads"
        self.heads = heads
        self.qkv = nn.Linear(embed_size, 3 * embed_size, bias=False)
        self.proj = nn.Linear(embed_size, embed_size, bias=False)
        self.dropout = dropout
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        batch, seq, channels = x.shape
        q, k, v = self.qkv(x).split(channels, dim=2)

        def split_heads(t):
            return t.view(batch, seq, self.heads, channels // self.heads).transpose(1, 2)

        q, k, v = split_heads(q), split_heads(k), split_heads(v)

        # is_causal=True aplica a máscara causal sem precisar construí-la.
        y = F.scaled_dot_product_attention(
            q, k, v,
            dropout_p=self.dropout if self.training else 0.0,
            is_causal=True,
        )
        y = y.transpose(1, 2).contiguous().view(batch, seq, channels)
        return self.resid_dropout(self.proj(y))


class FeedForward(nn.Module):
    def __init__(self, embed_size, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_size, 4 * embed_size),
            nn.GELU(),
            nn.Linear(4 * embed_size, embed_size),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    def __init__(self, embed_size, heads, dropout):
        super().__init__()
        self.ln1 = nn.LayerNorm(embed_size)
        self.attn = CausalSelfAttention(embed_size, heads, dropout)
        self.ln2 = nn.LayerNorm(embed_size)
        self.ff = FeedForward(embed_size, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x


class TinyLLM(nn.Module):
    def __init__(self, vocab_size, block_size, embed_size, heads, layers, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, embed_size)
        self.pos_emb = nn.Embedding(block_size, embed_size)
        self.drop = nn.Dropout(dropout)
        self.blocks = nn.ModuleList(
            [Block(embed_size, heads, dropout) for _ in range(layers)]
        )
        self.ln_f = nn.LayerNorm(embed_size)
        self.head = nn.Linear(embed_size, vocab_size, bias=False)
        self.head.weight = self.tok_emb.weight  # pesos compartilhados

        self.apply(self._init_weights)
        # Inicialização escalada nas projeções residuais (como no GPT-2).
        for name, param in self.named_parameters():
            if name.endswith("proj.weight") or name.endswith("net.2.weight"):
                nn.init.normal_(param, mean=0.0, std=0.02 / math.sqrt(2 * layers))

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx):
        _, seq = idx.shape
        if seq > self.block_size:
            raise ValueError(f"Sequência ({seq}) maior que block_size ({self.block_size}).")
        positions = torch.arange(seq, device=idx.device)
        x = self.drop(self.tok_emb(idx) + self.pos_emb(positions))
        for block in self.blocks:
            x = block(x)
        return self.head(self.ln_f(x))

    def num_params(self):
        return sum(p.numel() for p in self.parameters())


def build_model(config, dropout=None):
    """Cria o modelo a partir do dict de config salvo nos checkpoints."""
    return TinyLLM(
        vocab_size=config["vocab_size"],
        block_size=config["block_size"],
        embed_size=config["embed_size"],
        heads=config["heads"],
        layers=config["layers"],
        dropout=config.get("dropout", 0.1) if dropout is None else dropout,
    )
