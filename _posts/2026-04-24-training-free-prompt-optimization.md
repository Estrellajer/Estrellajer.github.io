---
layout: post
title: Training-Free Prompt Optimization：从经验库到问题重构
date: 2026-04-24 12:00:00
description: 关于 training-free prompt optimization、GRPO、经验库与 3DrawAgent 的一些思考
tags: prompt-optimization llm agent
categories: Research
---

这篇 blog 源于很久之前的某个晚上和朋友讨论到他的 CVPR 投稿，他提到了他的同门用Training-Free GRPO去迁移到某个子领域获得了比较好的审稿分数。在学校的人总是会对Training-Free相关的范式比较关注。前不久刚才提到的那个 CVPR 文章中了，也终于挂出来，正好最近也没有约面，顺便就梳理一下这些 Traing-free prompt optimization 相关的工作。

## 早期工作

APE 这类早期工作的真正贡献，并非提出了多么复杂的算法，而是验证了一个朴素却关键的事实：**LLM 可以作为 prompt engineer 使用**。

在 GPT 刚兴起时，信息抽取等领域大量工作还在依赖外部模型挑选 Few-shot 示例，这本质上是 prompt engineering 的低级形式。而在此之前，prompt 设计主要靠人工直觉。APE 把这件事转化成一个黑箱优化问题：给定少量输入输出样本，让 LLM 生成候选指令、在验证集上评估效果，并挑选得分更高的 prompt。

这个思路奠定了后续工作的基本范式：

> 生成候选 → 评估表现 → 总结反馈 → 生成更好的候选。

OPRO 把历史 prompt 和分数放进上下文，让 LLM 根据 optimization trajectory 继续爬坡；Promptbreeder / EvoPrompt 把这件事做成 evolutionary search；APO、TextGrad 一类工作则把失败原因写成自然语言梯度。后来的 GEPA、Training-Free GRPO、3DrawAgent 只是在不同场景下，把反馈形式和经验写回方式做得更复杂。

然而，早期工作也暴露了这个方向的几个根本局限：prompt 搜索空间巨大、反馈信号稀疏；语义相近的 prompt 效果可能天差地别；在一个模型上优化的结果换个模型就失效；而且高度依赖强大的 optimizer LLM——如果 optimizer 本身不够强，“self-optimization” 很容易变成自言自语。

因此，我更倾向于把这些方法视为**轻量级适配技巧**，而非训练的真正替代品。

读完这些工作后，一个自然的问题浮现出来：

> **如果不更新模型参数，所谓的 optimization 到底发生在什么地方？**

## 从参数空间到上下文空间

对比 **Vanilla GRPO** 和 **Training-Free GRPO** 最能说明这一点。

Vanilla GRPO 的流程清晰：对同一个 query 采样多条 response，用规则或奖励模型打分，再根据组内相对优势更新模型参数。学习发生在 **parameter space**，代价也来自这里——显存占用、训练稳定性、数据规模和过拟合风险。

**Training-Free GRPO** 则完全不同。它同样采样多条轨迹、比较好坏，但最后不更新参数，而是把轨迹中的经验总结成一段自然语言文本。推理时，模型直接读取这段“经验库”，再生成新答案。

也就是说，learning 从参数空间转移到了 **context space**。模型权重不变，但它被置于一个更有针对性的语境中。这和 LoRA 的直觉类似：都是给模型添加外部适配器，只不过这里的适配器是一段可读可更新的自然语言经验。

## 有用的场景

Training-free 方法最适合的场景，是模型**本来就具备某种能力**，但在默认生成策略下无法稳定调用出来。

一个简单判断指标是 **Pass@k** 与 **Pass@1** 的差距。如果 Pass@50 很高但 Pass@1 很低，说明正确路径其实存在于模型的概率空间中，只是默认采样时没稳定落到那条路径。这时，prompt optimization、reranking 或 Training-Free GRPO 就能发挥作用——它们做的是“对齐与筛选”，而非凭空创造新能力。

这类方法在数学推理、网页操作、工具使用等长链路任务中特别有效。很多失败并非模型“完全不会”，而是犯了可总结的低级错误：

- Web 任务中反复点击已失效按钮；
- 数学题中忘记验证中间变量；
- 工具调用中忽略错误返回；
- 多轮 agent 中遗忘上一轮已完成动作。

经验库在这里像一份 **checklist**，提醒模型避开已知坑。因此，Training-Free GRPO 的价值更像是“错误检查器”和“稳定性提升器”，而非“能力跃迁器”(这也是对标RL的一点)。

## 风险

问题也恰恰出在经验总结上。

很多经验并不是过程稳健的，而是结果导向的。模型可能总结出“看到某类关键词时应该采取某种动作”，这在简单任务中有效，但在十步以上的推理或 agent workflow 里，就可能变成一种危险的捷径。

更具体地说，它可能诱发一种“幻觉补偿”：

> 模型为了符合经验库中的规则，在中间步骤强行圆出一个看似合理的推理过程。

最终答案可能是对的，但过程并不真的可靠。如果只看 accuracy，这种问题会被掩盖。尤其在数学和网页操作任务里，模型有时不是理解了过程，而是学会了某些 benchmark 的经验模式。

所以以下几类额外评估可能是必要的：

第一是时间成本。很多论文强调 training-free 节省训练成本，但没有充分比较推理时间和多轮采样带来的 wall-clock cost。对于实际系统来说，不训练不等于省时间。

第二是过程质量。可以用 PRM 或 step-level verifier 给推理轨迹逐步打分，而不是只看最终答案。如果最终答案正确但中间步骤分数很低，那就说明 prompt 可能只是把模型推向了一个“会猜答案”的状态。

第三是扰动测试。人为修改一个中间变量，观察模型是否会沿着新的变量继续推理。如果它仍然强行回到原题答案，那就说明它并没有真正依赖中间过程。

第四是 out-of-domain 表现。经验库如果只在同分布内有效，那更像是 prompt 级别的过拟合；如果能迁移到新任务或新环境，才说明它捕获到了一些更稳定的行为规则。

## 其他：从“3DrawAgent”习得的写作经验

前面提到了这个文章，实际上就是 Training-Free GRPO 的范式迁移。但是最终拿到了 CVPR 的 highlight 。如果不是知道这个内幕的话，我读文章是很难把它和 Training-Free GRPO 联系起来的。

表面上看，它用的是常规组件：LLM 生成 3D Bézier 曲线、CLIP/LLM 评价、pairwise 对比总结经验、再写回 prompt。但它的价值在于怎么去包装 A 加 B 这种 incremental 的 contribution ，还有就是可能找的这个切入点也比较合适。因为好像还真没有人在这个3D 草图生成里面这样做过。

它Formulate 出来 challenge：想生成 3D 草图却没有 3D 训练数据；想持续改进却不能更新参数；想评价几何质量却没有标准答案。于是，pairwise feedback、LLM judge 和 experience library 就不是可有可无的装饰，而是被问题本身“逼”出来的必要设计。

当然，3DrawAgent 本身肯定也有缺陷：CLIP reward 与真实 3D 几何未必完全对齐，“emergent geometric reasoning” 也可能只是生成更符合评价器偏好的“3D-like”结构。但它证明了：在无 3D 数据和无参数更新的条件下，通过语言反馈仍能构造一个可迭代改进的 sketching loop。这本身可能对于这个领域的 reviewer 来说比较有启发。因为按照他论文里 claim 的来看，好像没人这样做。

虽然说很多经验帖都讲过类似的写作方式，但是实际写作的话，还是很难做到这一点。这个文章整体来说还是写作质量不错的，通讯作者还是有经验。

## 小结

Training-free prompt optimization 的本质，是在不碰模型参数的前提下，通过改变上下文和反馈结构来提升表现。

它最有效时，能让模型已有的潜在能力更稳定地被调用；它最危险时，可能把 benchmark 特定的经验包装成看似深刻的推理。

判断这类工作是否扎实，不能只看最终 accuracy，还要看：经验从何而来、反馈是否可靠、过程是否稳健，以及整个闭环是否真正被问题所驱动。

最后希望我的文章也有一个好运气吧。
