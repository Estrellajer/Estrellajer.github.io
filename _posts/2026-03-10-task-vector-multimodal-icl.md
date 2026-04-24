---
layout: post
title: Task Vector in Multimodal In-Context Learning 论文阅读笔记
date: 2026-03-10 12:00:00
description: Notes on task vectors, function vectors, in-context vectors, and multimodal in-context learning.
tags: paper-reading
categories: Research
---

这篇主要整理 task vector / function vector / in-context vector 在多模态 in-context learning 中的相关工作，以及一些可能继续探索的问题。

## Unified View

Why Steering Works: Toward a Unified View of Language Model Parameter Dynamics, ZJUNLP

![Unified view of task vectors](https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/202604201401466.png)

LoRA、local weight、steering vector 都可以看作 dynamic weight update。

目标是处理：

> trade-off between enforcing the target concept and preserving task validity

也就是“折页损失”。

这里实际上还隐含了一个问题：steering vector 是一种 test-time scaling 的视角，而 LoRA 和前面提到的 local weight 更多用于 fine-tuning。

## Task Vector Perspective

### Task Vector

Finding Visual Task Vectors, ECCV 2024

该工作 confirms that task vectors exist in the network activation space, and they can guide the model to perform the desired task.

某些 attention head 可以按任务聚类，这暗示 visual task vector 可能存在。

它和 NLP model 的差异在哪里？

- autoregressive
- sequential

所以 NLP 中可以直接选择 last token，因为它必定包含任务信息。

但 CV 中每个 patch 都有 hidden state，patch 不是顺序处理，同时也没有考虑多个 head 的叠加，也就是高阶 interaction。

因此搜索空间变成：

```text
layers × heads × tokens
```

Solution: RL

- action：选择哪些 head / patch
- reward：task accuracy

### Function Vector

Function Vectors in Large Language Models, ICLR 2024

Function vector 是 transformer hidden state 中的一个向量，它代表一个 input-to-output 的函数。

在 ICL 过程中，只有极少数 attention heads 在传播任务信息。这些 heads：

- 集中在 Transformer 中间层
- 主要关注 demonstration 的 output token

#### Q1

> Also, why compute the top attention heads over all tasks and not just have a different distinct set for each task?

由于大多数任务中重要的注意力头存在显著重叠，因此为每个任务设置一套独立的注意力头，与使用一套适用于所有任务的通用注意力头效果大致相同。附录 G 中包含一张图表，展示了每个注意力头的间接效应以及这些注意力头在多个任务中的重叠情况。

#### Q2

> Though the paper mainly investigates attention heads, I’m still wondering why attention heads contain such information rather than the MLP layers. Can the paper discuss more on this part, which would better explain the proposed findings?

我们的工作与之前的研究结果（Meng 2022, Geva 2023）一致，即 MLP 层确实在利用模型中存储的信息丰富 hidden states。然而，Meng 和 Geva 也都发现了直接证据，表明最后一个 token 处的 attention head 传递了一些重要信息。在我们目前的工作中，我们选择研究信息在模型中的传递。

我们研究的注意力机制很有意思，因为与使用不同 MLP 存储不同信息的信息存储方式不同，我们发现了一组很小的 attention heads，它们作为许多不同 ICL 任务的通用中介。

### In-Context Vector

In-Context Vectors: Making In-Context Learning More Effective and Controllable Through Latent Space Steering, ICML 2024

ICL 本质上是通过注意力机制在每一层对 query 的隐藏状态进行偏移，而 ICV 则是通过显式提取这个“偏移向量”，来更直接、可控地引导模型。

任务特征提取通过两种方式实现：

- 对于有配对数据的情况，首先计算多组 demonstration samples $(x_i, y_i)$ 在 LLM 每一层最后位 token 处的 hidden state difference：

  $$
  \Delta H = h(y) - h(x)
  $$

  随后使用 PCA 提取这些差值向量的第一主成分作为 ICV。这一向量代表了从输入到输出转换信号最强的方向。

- 对于无法获得一一对应标签的无配对数据，则通过 contrastive loss 的梯度方向生成 ICV。

应用与干预方面，与 FV 仅关注少数关键 attention heads 不同，ICV 应用于 Transformer 的所有层和所有 token 位置时效果最为显著。

同时，通过调整缩放因子 $\lambda$（step size），可以定量控制任务执行强度。例如，通过增大 $\lambda$ 提升文本脱敏力度。

此外，ICV 还展现了类似 Word2Vec 的线性代数特性：通过负向叠加向量可实现任务取反，例如将正式语体转回非正式；通过向量加减法还可实现任务组合，例如：

$$
(+\mathrm{Safe}) + (-\mathrm{Polite})
$$

可以生成一份“内容安全但语气粗鲁”的回复。

### Implicit In-Context Learning

Implicit In-Context Learning, ICLR 2025

I2CL 将示范样本转化为上下文向量（context vector），并在 activation space 进行 intervention，彻底摆脱了对显式 demonstration tokens 的依赖。

- 独立向量化：不同于 ICL 将示范样本与 query 拼接，I2CL 独立地为每个示范对 $(x_i, y_i)$ 提取向量表示。
- 位置提取改变：模型收集每个示范样本在 MHA 和 MLP 模块中最后一层 token 位置，即 end residual stream 的输出激活值。
- 置换不变性聚合：通过对所有示范样本的向量组件计算算术平均值，生成一个统一的上下文向量 $v$。实验证明，这种聚合方式捕获的任务表征对示范样本的选择和顺序具有很强的鲁棒性。
- 噪声自校准（noisy self-calibration）：为了实现自适应控制，I2CL 使用基于梯度的优化方法，在注入过程中引入高斯噪声，通过最小化示范样本标签的 perplexity 来自动估计线性系数 $\lbrace \lambda, \beta \rbrace$。
- 任务 ID 属性：校准后的线性系数可作为天然的 task IDs。实验表明，语义相似的任务（如 SST-2 和 MR）其系数向量在潜空间中分布更接近，这支持迁移学习，即利用已有任务的锚点提升新任务表现。

### Multimodal Task Vector

Multimodal Task Vectors Enable Many-Shot Multimodal In-Context Learning, NeurIPS 2024

TV 的多模态版本。

### Mimic In-Context Learning

Mimic In-Context Learning for Multimodal Tasks, CVPR 2025

类似 S-Prompts，新增一个模块用来模拟 task vector。这样就能做到 input dependent，自然会有更好的效果。

### Sensitivity-Aware Task Vector

Where and What Matters: Sensitivity-Aware Task Vectors for Many-Shot Multimodal In-Context Learning, AAAI 2026

刷点的工作，更细粒度地控制：

> vector 聚类求均值，然后通过测量 attention head 在有无 in-context 示例时的激活变化幅度，判断哪些 head 对上下文最敏感，最后只在这些 head 上插入 task vector。

## What to Do with Task Vector?

不同 MLLM 的 backbone 对不同 vector 方法有没有影响？有 blog 表明，不同 backbone 对 steering 方法确实有影响。所以这方面的探索应该也可以算一个 contribution。

是否需要 unify？

Input dependent 和 input independent 之间的 trade-off，能否像开头那篇文章一样做到一个 Pareto optimal？

可以考虑这样一个假设：

> Multimodal LLMs represent task behavior as a sparse superposition of a small set of reusable latent task directions.

如果这个假设成立，就可以把任务分成几个正交的 task directions，同时也不用计算所有 hidden forward，具有 inference 效率高的优势。

刷点方向：怎么高效找到 task 对应的 vector？

一个反直觉的矛盾点是：视觉似乎会影响注意力分数，同时示例顺序也会影响输出。那么，学到的 input-independent vector 真的效果好吗？或者说，这里应该探究一个点：如果消除顺序对 output 的影响，对当前任务是有益还是有害？同时它对其他任务上的 transfer 是有益还是有害？

还有一个 topic：考虑任务的泛化线可能没有意义，但如果考虑 safety，就可能存在一个 Pareto optimal。

参考问题：

> Calibrate Before Use: Improving Few-Shot Performance of Language Models

## 顺序包含有用信息

某些任务顺序可能有意义。

例如 curriculum structure：

```text
easy example
medium example
hard example
```

顺序隐含：

```text
learning trajectory
```
