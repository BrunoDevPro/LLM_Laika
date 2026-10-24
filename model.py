"""Transformer decoder (estilo GPT) pequeno, em PyTorch puro.

Posições: aprendidas (pos_emb, os presets até 50M) ou RoPE (rope=True no config, o preset de 100M).
Com RoPE não há tabela de posições: a posição entra girando q e k na atenção, então o contexto
pode ser maior sem um embedding de posição enorme.

forward(idx) é o caminho do treino. forward_cached(idx, past) é o da conversa: guarda as chaves e os
valores de cada camada (cache de atenção), para cada token novo custar só a parte dele.
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


def rope_tables(block_size, head_dim, theta=10000.0):
    """cos e sin de cada posição (block_size × head_dim/2), em float32."""
    inv = 1.0 / (theta ** (torch.arange(0, head_dim, 2, dtype=torch.float32) / head_dim))
    freqs = torch.outer(torch.arange(block_size, dtype=torch.float32), inv)
    return freqs.cos(), freqs.sin()


def apply_rope(x, cos, sin):
    """Gira as metades de x (lote, cabeças, seq, head_dim) pelos ângulos de cada posição."""
    half = x.size(-1) // 2
    x1, x2 = x[..., :half], x[..., half:]
    cos, sin = cos.to(x.dtype), sin.to(x.dtype)
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)


class CausalSelfAttention(nn.Module):
    def __init__(self, embed_size, heads, dropout):
        super().__init__()
        assert embed_size % heads == 0, "embed_size precisa ser divisível por heads"
        self.heads = heads
        self.qkv = nn.Linear(embed_size, 3 * embed_size, bias=False)
        self.proj = nn.Linear(embed_size, embed_size, bias=False)
        self.dropout = dropout
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x, rope=None, past=None):
        """rope: (cos, sin) das posições de x, ou None. past: (k, v) do cache, ou None (sem cache).
        Com cache, devolve (saída, (k, v)) com as posições novas acrescentadas."""
        batch, seq, channels = x.shape
        q, k, v = self.qkv(x).split(channels, dim=2)

        def split_heads(t):
            return t.view(batch, seq, self.heads, channels // self.heads).transpose(1, 2)

        q, k, v = split_heads(q), split_heads(k), split_heads(v)
        if rope is not None:
            q, k = apply_rope(q, *rope), apply_rope(k, *rope)

        if past is None or past[0] is None:
            # is_causal=True aplica a máscara causal sem precisar construí-la.
            y = F.scaled_dot_product_attention(q, k, v, dropout_p=self.dropout if self.training else 0.0,
                                               is_causal=True)
            novo = (k, v)
        else:
            k, v = torch.cat([past[0], k], dim=2), torch.cat([past[1], v], dim=2)
            total = k.size(2)
            # Cada posição nova vê o cache inteiro e as novas até ela.
            mask = torch.ones(seq, total, dtype=torch.bool, device=x.device).tril(diagonal=total - seq)
            y = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
            novo = (k, v)
        y = y.transpose(1, 2).contiguous().view(batch, seq, channels)
        out = self.resid_dropout(self.proj(y))
        return out if past is None else (out, novo)


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

    def forward(self, x, rope=None, past=None):
        if past is None:
            x = x + self.attn(self.ln1(x), rope)
            return x + self.ff(self.ln2(x))
        a, novo = self.attn(self.ln1(x), rope, past)
        x = x + a
        return x + self.ff(self.ln2(x)), novo


class TinyLLM(nn.Module):
    def __init__(self, vocab_size, block_size, embed_size, heads, layers, dropout=0.1, rope=False,
                 rope_theta=10000.0):
        super().__init__()
        self.block_size = block_size
        self.rope = rope
        self.tok_emb = nn.Embedding(vocab_size, embed_size)
        if rope:
            cos, sin = rope_tables(block_size, embed_size // heads, rope_theta)
            # Não vão para o state_dict: são recalculadas a partir do config.
            self.register_buffer("rope_cos", cos, persistent=False)
            self.register_buffer("rope_sin", sin, persistent=False)
        else:
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

    def _entrada(self, idx, start):
        seq = idx.size(1)
        if start + seq > self.block_size:
            raise ValueError(f"Sequência ({start + seq}) maior que block_size ({self.block_size}).")
        x = self.tok_emb(idx)
        rope = None
        if self.rope:
            rope = (self.rope_cos[start:start + seq], self.rope_sin[start:start + seq])
        else:
            x = x + self.pos_emb(torch.arange(start, start + seq, device=idx.device))
        return self.drop(x), rope

    def forward(self, idx):
        x, rope = self._entrada(idx, 0)
        for block in self.blocks:
            x = block(x, rope)
        return self.head(self.ln_f(x))

    def forward_cached(self, idx, past=None):
        """Para gerar texto: past = cache devolvido na chamada anterior (None = começar do zero).
        Devolve (logits do último token, cache novo)."""
        start = 0 if not past else past[0][0].size(2)
        x, rope = self._entrada(idx, start)
        novo = []
        for i, block in enumerate(self.blocks):
            x, kv = block(x, rope, past[i] if past else (None, None))
            novo.append(kv)
        return self.head(self.ln_f(x[:, -1:]))[:, -1], novo

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
        rope=config.get("rope", False),
        rope_theta=config.get("rope_theta", 10000.0),
    )
