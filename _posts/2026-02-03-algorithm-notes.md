---
layout: post
title: LLM八股学习与手撕
date: 2026-02-03 11:30:00
description: Notes on LLM algorithms
tags: llm
categories: Learning
---

## Attention

### 缩放点积注意力

步骤总结：
Q 与 K 转置做矩阵乘法 -- 除以 √d_k 缩放 -- (可选) mask -- softmax 归一化 -- 与 V 做矩阵乘法

```python
import torch
from torch import nn


class SqdtAttention(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, q, k, v, mask=None):
        d_k = q.size(-1)
        attn_weight = (q @ k.transpose(-2, -1)) / (d_k ** 0.5)

        if mask is not None:
            attn_weight = attn_weight.masked_fill(mask == 0, float("-inf"))

        attn_weight = torch.softmax(attn_weight, dim=-1)
        output = attn_weight @ v
        return output


def test_attn():
    batch_size = 128
    seq_len = 512
    hidden_size = 1024

    query = torch.randn(batch_size, seq_len, hidden_size)
    key = torch.randn(batch_size, seq_len, hidden_size)
    value = torch.randn(batch_size, seq_len, hidden_size)

    sdpa = SqdtAttention()
    output = sdpa(query, key, value)

    print("Query shape:", query.shape)
    print("Key shape:", key.shape)
    print("Value shape:", value.shape)
    print("Output shape:", output.shape)


if __name__ == "__main__":
    test_attn()
```

### 多头注意力（MHA）

步骤总结：
Q/K/V 线性投影 -- 重塑为 `(batch, seq, num_heads, head_dim)` -- 转置为 `(batch, num_heads, seq, head_dim)` -- 每头计算 QK^T / √d_k -- (可选) mask -- softmax -- 与 V 相乘 -- 拼接多头并输出投影

```python
import torch
from torch import nn


class MultiHeadAttention(nn.Module):
    def __init__(self, hidden_size, num_heads):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        self.q_linear = nn.Linear(hidden_size, hidden_size)
        self.k_linear = nn.Linear(hidden_size, hidden_size)
        self.v_linear = nn.Linear(hidden_size, hidden_size)
        self.o_linear = nn.Linear(hidden_size, hidden_size)

    def forward(self, hidden_state, mask=None):
        batch_size, seq_len = hidden_state.size(0), hidden_state.size(1)

        query = self.q_linear(hidden_state).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key = self.k_linear(hidden_state).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value = self.v_linear(hidden_state).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        attn_scores = (query @ key.transpose(-2, -1)) / (self.head_dim ** 0.5)

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float("-inf"))

        attn_probs = torch.softmax(attn_scores, dim=-1)
        output = (attn_probs @ value).transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_size)
        output = self.o_linear(output)

        return output


def test_mha():
    batch_size = 128
    seq_len = 512
    hidden_size = 1024
    num_heads = 8

    hidden_state = torch.randn(batch_size, seq_len, hidden_size)
    causal_mask = 1 - torch.triu(torch.ones(seq_len, seq_len), diagonal=1)

    mha = MultiHeadAttention(hidden_size, num_heads)
    output = mha(hidden_state, mask=causal_mask)

    print("Input shape:", hidden_state.shape)
    print("Output shape:", output.shape)


if __name__ == "__main__":
    test_mha()
```

### 多查询注意力（MQA）

步骤总结：
Q 全头线性投影、K/V 共享头线性投影 `(head_dim)` -- Q 分头、K/V 保持单头 -- 每头 Q 与共享 K^T 做点积 / √d_k -- (可选) mask -- softmax -- 与 V 相乘 -- 拼接多头并输出投影

```python
import torch
from torch import nn


class MultiQueryAttention(nn.Module):
    def __init__(self, hidden_size, num_heads):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        self.q_linear = nn.Linear(hidden_size, hidden_size)
        self.k_linear = nn.Linear(hidden_size, self.head_dim)
        self.v_linear = nn.Linear(hidden_size, self.head_dim)
        self.o_linear = nn.Linear(hidden_size, hidden_size)

    def forward(self, hidden_state, mask=None):
        query = self.split_head(self.q_linear(hidden_state))
        key = self.split_head(self.k_linear(hidden_state), 1)
        value = self.split_head(self.v_linear(hidden_state), 1)

        attn_scores = (query @ key.transpose(-2, -1)) / (self.head_dim ** 0.5)

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float("-inf"))

        attn_probs = torch.softmax(attn_scores, dim=-1)
        output = (attn_probs @ value).transpose(1, 2).contiguous().view(hidden_state.size(0), hidden_state.size(1), self.hidden_size)
        output = self.o_linear(output)

        return output

    def split_head(self, x, head_num=None):
        batch_size = x.size(0)
        if head_num is None:
            head_num = self.num_heads
        head_dim = x.size(-1) // head_num
        return x.view(batch_size, -1, head_num, head_dim).transpose(1, 2)
```

### 维度变换速查：split_head 与 repeat_kv

**split_head(x, head_num)** — 把最后一维拆成 `head_num × head_dim`

```text
输入: (B, seq, feat)  其中 feat = head_num × head_dim
view: (B, seq, head_num, head_dim)
transpose(1,2): (B, head_num, seq, head_dim)  ← 把 head 提前，便于逐头计算
```

**repeat_kv(x)** — 把 `num_kv_heads` 扩成 `num_heads`（GQA 专用）

```text
输入: (B, num_kv_heads, seq, head_dim)
unsqueeze(2): (B, num_kv_heads, 1, seq, head_dim)
repeat(1,1,n_rep,1,1): (B, num_kv_heads, n_rep, seq, head_dim)  每个 kv 头重复 n_rep 次
reshape: (B, num_heads, seq, head_dim)  其中 num_heads = num_kv_heads × n_rep
```

**记忆口诀**：split 是「拆尾维 → view → transpose 把 head 提前」，repeat 是「unsqueeze 插维 → repeat 复制 → reshape 拉平」。

---

### 分组查询注意力（GQA）

步骤总结：
Q 全头线性投影、K/V 分组头线性投影 `(num_kv_heads × head_dim)` -- Q 分 `num_heads` 头、K/V 分 `num_kv_heads` 头 -- `repeat_kv` 将 K/V 扩至 `num_heads` -- 点积 / √d_k -- (可选) mask -- softmax -- 与 V 相乘 -- 拼接多头并输出投影

```python
import torch
from torch import nn


class GroupedQueryAttention(nn.Module):
    def __init__(self, hidden_size, num_heads, num_kv_heads=None):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads or num_heads
        self.head_dim = hidden_size // num_heads

        self.q_linear = nn.Linear(hidden_size, hidden_size)
        self.k_linear = nn.Linear(hidden_size, self.num_kv_heads * self.head_dim)
        self.v_linear = nn.Linear(hidden_size, self.num_kv_heads * self.head_dim)
        self.o_linear = nn.Linear(hidden_size, hidden_size)

    def forward(self, hidden_state, mask=None):
        batch_size, seq_len = hidden_state.size(0), hidden_state.size(1)

        query = self._split_head(self.q_linear(hidden_state), self.num_heads)
        key = self._split_head(self.k_linear(hidden_state), self.num_kv_heads)
        value = self._split_head(self.v_linear(hidden_state), self.num_kv_heads)

        key = self._repeat_kv(key)
        value = self._repeat_kv(value)

        attn_scores = (query @ key.transpose(-2, -1)) / (self.head_dim ** 0.5)

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float("-inf"))

        attn_probs = torch.softmax(attn_scores, dim=-1)
        output = (attn_probs @ value).transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_size)
        output = self.o_linear(output)

        return output

    def _split_head(self, x, head_num):
        batch_size = x.size(0)
        head_dim = x.size(-1) // head_num
        return x.view(batch_size, -1, head_num, head_dim).transpose(1, 2)

    def _repeat_kv(self, x):
        n_rep = self.num_heads // self.num_kv_heads
        return x.unsqueeze(2).repeat(1, 1, n_rep, 1, 1).reshape(x.size(0), self.num_heads, -1, x.size(-1))


def test_gqa():
    batch_size, seq_len, hidden_size, num_heads, num_kv_heads = 2, 16, 256, 8, 2
    hidden_state = torch.randn(batch_size, seq_len, hidden_size)
    gqa = GroupedQueryAttention(hidden_size, num_heads, num_kv_heads)
    output = gqa(hidden_state)
    print("GQA output shape:", output.shape)  # (2, 16, 256)


if __name__ == "__main__":
    test_gqa()
```

## DPO（Direct Preference Optimization）

### compute_log_probs 步骤总结

`log_softmax` -- `gather` 取 label 对应概率 -- `mask` 保留 response 位置 -- `sum` 汇总

**gather 要点**：`log_probs[b, i, labels[b, i]]` 等价于 `gather(log_probs, dim=-1, index=labels.unsqueeze(-1))`。`index` 必须与 `log_probs` 同维，所以 `labels (B, S) → unsqueeze(-1) → (B, S, 1)`。

**gather 具体例子**：

```text
log_probs: (1, 3, 5)  即 1 句 3 词，词表大小 5
  位置0: [-2.1, -0.5, -1.0, -3.0, -2.5]
  位置1: [-1.2, -2.3, -0.8, -4.0, -1.5]
  位置2: [-3.0, -1.0, -0.3, -2.0, -2.2]

labels: (1, 3) = [[2, 0, 4]]
labels.unsqueeze(-1): (1, 3, 1) = [[[2], [0], [4]]]

gather(dim=-1):
  out[0,0,0] = log_probs[0,0,2] = -1.0
  out[0,1,0] = log_probs[0,1,0] = -1.2
  out[0,2,0] = log_probs[0,2,4] = -2.2

squeeze(-1) → (1, 3) = [[-1.0, -1.2, -2.2]]
```

---

### DPO Loss 步骤总结

`chosen/rejected` 各算 `log_ratio = policy_logp - ref_logp` -- `logits = β × (chosen_ratio - rejected_ratio)` -- `loss = -logsigmoid(logits)`

**公式**：$\mathcal{L} = -\mathbb{E}\left[\log \sigma\left(\beta \log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)\right]$

**记忆**：让 `chosen` 的 `log_ratio` 比 `rejected` 大，loss 才小；`β` 控制偏离参考模型的强度。

**手撕流程**：

1. `compute_log_probs`：`log_softmax → gather → mask → sum`
2. `dpo_loss`：`log_ratio = policy - ref → logits = β × (chosen - rejected) → -logsigmoid → mean`

---

```python
import torch
import torch.nn.functional as F


def compute_log_probs(
    logits: torch.Tensor,  # (batch, seq_len, vocab_size)
    labels: torch.Tensor,  # (batch, seq_len)
    mask: torch.Tensor,  # (batch, seq_len)，1=response 需计算，0=prompt 忽略
) -> torch.Tensor:
    """
    计算序列的对数概率，只算 response 部分（RLHF/DPO 常用）
    """
    log_probs = F.log_softmax(logits, dim=-1)

    per_token_log_probs = torch.gather(
        log_probs,
        dim=-1,
        index=labels.unsqueeze(-1),
    ).squeeze(-1)

    return (per_token_log_probs * mask).sum(dim=-1)  # → (batch,)


def dpo_loss(
    policy_chosen_logps: torch.Tensor,  # (batch,)
    policy_rejected_logps: torch.Tensor,  # (batch,)
    ref_chosen_logps: torch.Tensor,  # (batch,)
    ref_rejected_logps: torch.Tensor,  # (batch,)
    beta: float = 0.1,
) -> torch.Tensor:
    """
    DPO Loss：无 RL 的偏好优化，直接优化 policy 使 chosen 优于 rejected
    """
    chosen_log_ratios = policy_chosen_logps - ref_chosen_logps
    rejected_log_ratios = policy_rejected_logps - ref_rejected_logps

    logits = beta * (chosen_log_ratios - rejected_log_ratios)
    return (-F.logsigmoid(logits)).mean()
```
