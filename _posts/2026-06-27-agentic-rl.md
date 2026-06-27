---
layout: post
title: Agentic RL 综述：工具调用、信用分配与训练稳定性——从 RAP 到 AEPO
date: 2026-06-27 12:00:00
description: 梳理 Agentic RL 从树搜索到可训练策略的演进，涵盖 Planner-R1、TORL/ToolRL/ARTIST、GiGPO/ARPO、RAGEN/RAGEN-2 及 AEPO，聚焦 reward 设计、credit assignment 与 reasoning collapse 三大核心问题。
tags: agentic-rl llm agent tool-use grpo reasoning
categories: Research
---

## 一、背景：Agent 需要什么样的学习信号

ReAct-style tool calling 可以通过 prompt engineering 或 SFT 让模型学会调用工具，但泛化能力有限——遇到新工具、新参数、新错误时容易崩。真正想让模型掌握工具使用，需要 **Tool-Integrated RL**：把工具调用放进训练循环，让模型在真实环境中 rollout，通过 reward 学会何时调用、怎么调用、失败后怎么修正。

这带来了几个核心挑战：

- **长程多轮**：不同于 single-turn math，Agent 任务涉及多轮 decoding 和 tool interaction，轨迹很长
- **Credit Assignment**：最终失败不代表每一步都错，稀疏 reward 很难精确定位错误动作
- **Memory**：RAG-style / token-level / structured memory 的选择影响训练稳定性

本文梳理从早期 Agent planning 框架到现代 Agentic RL 的核心演进，重点关注各工作的 **insight、局限性和相互关联**。

---

## 二、早期 Planning：树搜索与外部反馈

### 2.1 RAP (EMNLP 2023)：Reasoning with Language Model is Planning with World Model

**核心 insight：**

- 显式状态比纯 CoT 更重要——现代 Agent 通常都会维护显式状态、任务进度、工具调用结果
- 推理需要搜索，而不是一条路走到黑
- Reward 或 verifier 对于 Agent 是重要的

RAP 试图让 LLM 自己充当 world model：LLM 生成 action，LLM 预测下一 state，再用 reward 和 MCTS 搜索。**问题是它在模型想象出来的世界里搜索**，state model 通过 prompt 来预测下个状态，高度依赖任务是否能被离散状态化。MCTS 计算成本也高。

**真正留下来的：** LLM agent 的能力可以通过推理时的结构化计算增强——维护状态、生成候选动作、预测后果、评价中间步骤、搜索/回溯、聚合结果。

### 2.2 LATS (ICML 2024)：Language Agent Tree Search

LATS 可以看作 RAP 的自然后续。核心转向：**不要让 LLM 自己幻想下一状态，而是让 environment 返回 observation。**

LATS 的节点不是 RAP 那种纯 internal state，而是 `s = [x, a_{1:i}, o_{1:i}]`——原始任务、历史 actions、历史 observations。它把 ReAct 的 Thought/Action/Observation loop 扩展成树搜索。

**LATS 相比 RAP 的关键进步：**

1. **Agent 的 state 应该包含 observation，而不只是 thought**。代码 Agent 强不是因为它"想得更好"，而是因为它能跑测试、看报错、改代码、再跑。
2. **ReAct 是线性的，复杂任务需要在 action 层面搜索**。同一个 state 下 sample 多个 actions，让 environment 返回不同 observations。
3. **外部反馈比纯自我反思更可靠**。LLM 自我反思不是魔法——真正有用的是 unit tests、compiler、browser observation、tool output、environment reward、verifier feedback。
4. **LM 可以同时扮演 policy、value function、reflection generator**。同一个 LM 被复用成 agent、state evaluator、feedback generator。

**局限性：**

- MCTS 仍然太重，不适合 production
- 要求环境可回滚（发邮件、下单、转账等不可逆操作不适用）
- Value function 是 prompt-based，可靠性有限
- Memory 更像 prompt buffer，不是可检索、可更新、可验证的经验系统
- 实验环境偏小（WebShop 50 instructions，HotPotQA 100 questions）

**后向意义：** LATS 证明了 deliberation + external feedback 有用，但 MCTS 不是最终最 scalable 的承载方式。后来的 Agent 系统保留了这个闭环，但把重型树搜索替换成更工程化、更可学习的机制。

---

## 三、范式转折：Planner-R1——用环境 Reward 训练 Agent Policy

Planner-R1 是这条线上的阶段性转折：

> **RAP：用 LLM 模拟 world model，在脑内搜索** > **LATS：用环境 observation 替代 world model，在交互轨迹上搜索** > **Planner-R1：不再主要靠搜索，而是用环境 reward 训练 agent policy**

### 3.1 核心意义

不是 "TravelPlanner 上分数很高"，而是说明：**agentic ability 可以通过任务级 RL 直接训练出来，而且不一定需要特别大的模型。**

论文把 TravelPlanner 建模成多步 tool-use MDP：state 是完整历史（system/user prompt、partial plan、tool calls、tool responses）；action 是 token；environment 执行七类 API 工具并返回 JSON；reward 由 schema validity、commonsense constraints、hard constraints 和 final pass 构成。

实验结论：Planner-R1-8B 长训后达到 56.4% final-pass，远高于 GPT-5 high effort 的 21.2%。**任务定制 RL 对 agent 行为的提升非常大。**

### 3.2 范式进步

**从"搜索策略"转向"策略学习"：** RAP/LATS 的核心是 inference 时多探索、多评估、多回溯。Planner-R1 的核心是：不要每次都临场搜索，而是通过 RL 让模型本身学会更好的 action distribution。Tree search 是 test-time compute，Planner-R1 是 training-time compute。

**从"LLM 自评"转向"可验证 reward"：** reward 由 schema validator、constraint checker、final pass metric 组成。Agent RL 能成立的前提就是 reward 足够可验证。

**从"反思/记忆"转向"reward shaping"：** 真正有效的不是让模型写反思，而是设计可学习的 reward 梯度。核心发现：**小模型特别吃 reward shaping。** 8B 在 dense Stage 1 reward 下表现很好，但在 sparse Stage 2/Stage 3 下容易 collapse；32B 对 sparse reward 更 robust。

### 3.3 关键 Insight

1. **Agentic RL 的关键不是 RL 算法本身，而是 reward decomposition。** 如果只给最终 0/1，模型无法知道错在哪里。Planner-R1 拆成 schema → micro constraints → macro constraints → final pass。
2. **小模型在 agentic RL 里可能更有性价比。** 8B peak 56.4% vs 32B peak 56.9%，差异不显著，但 8B 约 3.5× compute efficiency。
3. **Agent 失败主要不是"不会说"，而是工具顺序和约束 bookkeeping。** 困难不在于写一段计划，而在于查对实体、不要 hallucinate、预算算对、约束满足、多工具调用顺序。
4. **结构化输出是 Agent RL 的重要稳定器。** 把最终计划强制成 JSON schema，用 schema validity gate reward——结构化输出不是小细节，而是 reward、evaluation、tool execution、safety control 的接口。

### 3.4 局限

- TravelPlanner 对 RL 太友好：明确 schema、明确数据库、明确 constraints。很多真实 Agent 任务没有这么干净
- 56.9% final pass 仍然远没解决任务
- Agent 学到的是可迁移的 agent hygiene（守 schema、约束检查、少 hallucination），未必是通用规划能力

**一句话总结：** Planner-R1 是从"让 LLM 在推理时多想/多搜"转向"用环境反馈把 Agent 行为训练出来"的代表性工作；它说明现代 Agent 的关键不再是 prompt trick 或 tree search，而是可验证任务环境、reward shaping、以及把工具使用和约束满足内化进 policy。

---

## 四、Recipe 探索：TORL、ToolRL、ARTIST

这三篇 2025 年初的工作，核心贡献不是发明全新的 agent 架构，而是把 R1/GRPO 之后的 RL scaling 经验迁移到 tool-integrated reasoning 里，系统回答：**LLM 在需要调用工具的场景下，怎么通过 RL 学会"何时用、怎么用、用完怎么修正"，以及 reward 应该怎么设计。**

### 4.1 TORL：从 base model 直接 RL 出工具使用策略

**核心主张：** 不要先用 SFT 固定工具调用轨迹，而是让 base model 在 RL 环境里探索工具调用策略。7B 在 AIME24 达到 43.3%，比无工具 RL 高 14%。

**关键训练动力学分析：**

- 训练早期 code ratio 从约 40% 增到 80%，pass ratio 也持续上升
- 模型会学会减少无效代码——不是简单鼓励多调用工具，而是学会区分什么时候工具有用、什么时候代码是浪费
- 工程细节：tool call 上限、sandbox 选择、错误信息压缩、**tool output masking**（不 mask 工具输出，模型可能学着复现 deterministic observation，而不是学习如何调用工具）

**贡献：** 证明"工具使用能力"可以通过 reward-driven exploration 从 base model 中涌现，并给出了一套能跑通的训练配方。

### 4.2 ToolRL：Reward 设计就是 Tool Learning 的核心

**标题已经很直白：Reward is All Tool Learning Needs。**

系统研究 reward 如何设计：粗粒度 answer reward 不够，因为工具调用涉及工具名、参数名、参数值、多步调用、是否应拒绝不合适工具等。

**Reward 设计：**

- Format reward：输出是否包含 `<think>`、`<tool_call>`、`<response>` 且顺序正确
- Correctness reward：细分成 tool name matching、parameter name matching、parameter content matching

**最重要的经验结论：**

- 长 reasoning trace 不一定更好，直接 reward 长度可能伤害性能
- 动态 reward scale 有助于从简单行为过渡到复杂行为
- **细粒度 reward decomposition 比二值 reward 更稳定、更有效**
- SFT 会 overfit 到固定模式，甚至学到 "but wait" 这类表面深思模式

**贡献：** 把"怎么给工具调用打分"从经验问题变成了系统实验问题。

### 4.3 ARTIST：统一 GRPO Rollout 框架

覆盖数学 reasoning + multi-turn function calling + external environments。把 rollout 设计成 reasoning、tool query、tool output、final answer 的交替过程。

**关键细节：mask 工具输出 token 的 loss。** 工具输出是环境 observation，不应该被当成 model target 学——这个点和 TORL 一致，说明这些工作共同踩到同一个坑。

**贡献：** 更偏统一框架 + evaluation（MATH-500、AIME、τ-bench、BFCL v3 等）。

### 4.4 三篇的共同贡献与差异

**共同贡献：** 把工具调用从 prompt/SFT 模仿，转成 outcome/reward-driven 的策略学习问题。工具调用不是格式学习，而是决策学习——何时调用、调用哪个、参数怎么填、失败后怎么恢复、什么时候不调用。

这些工作的真正贡献不在 GRPO 公式，而在 reward/environment recipe：reward 太粗学不到、太密 overfit、奖励长度导致 overthinking、工具输出不能参与 loss、sandbox 错误要返回但不能太 verbose……

| 工作   | 核心问题                                                         | 主要贡献                      |
| ------ | ---------------------------------------------------------------- | ----------------------------- |
| TORL   | base model 能否通过 RL 学会调用代码工具？                        | 强 scaling/recipe 贡献        |
| ToolRL | 通用 tool use 里 reward 怎么设计才稳定、泛化？                   | 最像 reward 设计指南/踩坑总结 |
| ARTIST | 更一般的 agentic reasoning + tool interaction 怎么用 GRPO 训练？ | 框架化包装 + 多任务验证       |

---

## 五、Credit Assignment：GiGPO 与 ARPO

### 5.1 问题的本质

GRPO 不训练 critic，而是对同一个 query 采一组 responses/trajectories，用组内 reward 的均值、方差来算相对 advantage。所以 **GRPO 的有效信号来自组内相对差异。**

如果组内样本 reward 都一样（全对或全错），advantage 接近 0，训练信号很弱。Agent 场景里这个问题更严重：一条 trajectory 很长，最终 reward 有差异但 credit 很混乱——你不知道 reward 差异来自哪一步。

### 5.2 GiGPO：利用重复状态做 Step-Level Credit Assignment

**思路：** 已有 trajectories 里，如果碰到相同 state，就比较同一 state 下不同 action 的 return，形成局部差异。

**局限：** 依赖状态重复——如果环境状态空间很大，相同 state 很少出现。

### 5.3 ARPO：在高不确定性节点主动 Branch

**核心逻辑：** 工具返回之后，模型 token entropy 往往升高。这个高 entropy 表示模型对下一步不确定——要不要继续搜？要不要换 query？要不要调用 Python？要不要直接回答？

ARPO 在这些高 entropy 节点 branch 出多个 partial rollout，更容易产生 reward 差异，让 GRPO-style 相对 advantage 更有训练价值。

**一句话：** GRPO 需要差异；ARPO 主动去高不确定性位置制造更有用的差异。

---

## 六、Collapse 问题：RAGEN 到 RAGEN-2

### 6.1 RAGEN：Multi-Turn Agent RL 会出新问题

RAGEN 是 R1/GRPO 热潮后对 multi-turn agent RL 的早期系统研究。核心发现：

**第一，vanilla PPO/GRPO 在 multi-turn agent 上会 collapse。** 早期可能提升，但之后 performance collapse；WebShop 因为语言 prior 强反而比较容易提升。

**第二，collapse 的表现是 Echo Trap。** 早期有多样化 symbolic reasoning，训练后期变成重复、确定、模板化的响应。RL 可能过度放大局部 rewarded reasoning shortcuts，压制 exploration。

**第三，只靠 trajectory-level reward 很难让 reasoning 真正 emerge。** 模型可能逐渐缩短 reasoning，甚至退化到 direct action selection；更糟的是，可能产生和环境状态不匹配的 hallucinated reasoning，但仍然拿到高 reward。

多轮 RL 的关键不是简单把 GRPO 套到 trajectory 上，而是 rollout 质量、reward variance、gradient stability、reasoning-aware reward 都会决定训练是否 collapse。

### 6.2 RAGEN-2：Entropy 不足以诊断 Reasoning 质量

RAGEN-2 抓住了更深的问题：**reasoning collapse 不一定表现为低 entropy，而可能表现为低 input dependence。**

#### Entropy 的误导性

过去很多工作依赖 entropy 监控探索或 reasoning 稳定性。RAGEN-2 指出：entropy 只衡量同一 input 下输出有多多样，但不知道 reasoning 是否真的依赖输入。

它把 reasoning 分解为：

```
reasoning diversity = within-input diversity + cross-input dependence
H(Z) = I(X; Z) + H(Z | X)
```

四种状态：

| 状态                  | Entropy | MI     | 含义                       |
| --------------------- | ------- | ------ | -------------------------- |
| Diverse reasoning     | 高      | 高     | 理想：既多样又和输入相关   |
| **Template collapse** | **高**  | **低** | **看似多样，但和输入无关** |
| Compressed reasoning  | 低      | 高     | 简洁但仍输入相关           |
| Low-entropy collapse  | 低      | 低     | 完全退化                   |

**Template collapse 是 entropy 和已有 metrics 都不可见的 failure mode。** 模型可能 entropy 很高，但不同输入下都说类似模板，只是表面词不同。

#### SNR-Aware Filtering

RAGEN-2 提出：有用的 RL update 需要足够高的 signal-to-noise ratio。Within-input reward variance 越高，advantage 越有 task-discriminative signal；reward variance 越低，task gradient 越弱，KL/entropy 这些 input-agnostic regularizer 越容易主导更新。

方法：

```
每轮 rollout
→ 对每个 prompt 采 G 条 trajectories
→ 计算这个 prompt 内 reward variance
→ 只保留 top-p 高 variance prompts 做 update
```

### 6.3 RAGEN-2 与 ARPO 的关系

ARPO 用 entropy 决定在哪里分叉探索；RAGEN-2 指出 entropy 不能证明分叉探索是 input-grounded 或 task-relevant。

两者不完全矛盾，而是分工不同：

> **ARPO：entropy 可以帮助找"哪里要探索"** > **RAGEN-2：entropy 不能证明"探索出来的是 input-grounded reasoning"**

更完整的 recipe 需要 ARPO 式 adaptive branching + RAGEN-2 式 MI/SNR 诊断与 filtering。

---

## 七、AEPO：从 Entropy-Guided 到 Entropy-Balanced

AEPO 是 ARPO 作者对 ARPO 的自我修正。**核心变化：把 entropy 从"越高越值得探索"改为"需要 balance 的资源"。**

### 7.1 ARPO 的两个问题

**第一，rollout 阶段会 over-branch。** 如果某条 trajectory 连续出现 high-entropy tool-call steps，ARPO 会一直沿着这条路径 branch，导致 branch budget 被少数 trajectory 吃掉。统计显示连续 high-entropy turns 占 56.5%，93.4% 的 branch 集中在 1-3 条 trajectories 上。

**第二，policy update 阶段 high-entropy tokens 容易被 clipping 掉。** "However"、"Maybe"、"<search>"、"<python>"——这些 token 可能代表模型在关键位置切换策略，但 importance sampling ratio 容易超过 clipping threshold，被 GRPO/PPO 剪掉。

### 7.2 两个机制

**Dynamic Entropy-Balanced Rollout：** 先做 entropy pre-monitoring（预先生成一条完整 trajectory 估计 H_root 和 H_tool_avg），根据差值动态分配 rollout budget：

- H_root > H_tool_avg → 多做 global rollout，从问题起点探索不同解法
- H_root < H_tool_avg → 多留 budget 给 tool-call 后的 branch sampling

再加 **consecutive branch penalty**：同一条路径连续多次 high-entropy 会降低继续 branch 的概率，避免所有预算砸在同一条路径上。

**Entropy-Balanced Policy Optimization：** 高熵探索 token 的梯度不要完全剪掉，而是保留受控梯度。同时 entropy-aware advantage estimation：最终 advantage 不只看 answer correctness，也纳入 token entropy shaping。

### 7.3 与 RAGEN-2 的对比

| 维度              | AEPO                                                                         | RAGEN-2                        |
| ----------------- | ---------------------------------------------------------------------------- | ------------------------------ |
| 解决的问题        | entropy 的资源分配失衡                                                       | entropy 的诊断有效性           |
| 方法              | budget balancing + branch penalty + high-entropy token gradient preservation | MI proxy + SNR-aware filtering |
| 对 entropy 的态度 | 需要 balance                                                                 | 不能衡量 input dependence      |

AEPO 解决的是 **entropy 的资源分配问题**，RAGEN-2 解决的是 **entropy 的诊断有效性问题**。AEPO 承认 entropy 会带来 collapse，但仍在 entropy 框架内部修补，没有验证 entropy 是否真的对应有效 reasoning。

### 7.4 AEPO 的局限

- **没有解决 entropy 的语义问题。** 高 entropy token 可能是有效探索、无效摇摆、噪声响应或格式化连接词，AEPO 不加区分
- **Entropy pre-monitoring 的理论包装比较粗。** token entropy 不等于 task-relevant information gain
- **Consecutive branch penalty 可能错杀需深挖的复杂路径。** 在 deep research 中，真正正确的路径可能天然需要连续 branching
- **Attribution 不够完全。** 不清楚主要 gain 来自 rollout budget rebalancing 还是 GPPO-style clipping trick

---

## 八、整体脉络

把这些工作串起来：

```
ToolRL / TORL / ARTIST:
    RL 怎么让模型学会 tool use？reward / format / execution 怎么设计？

GiGPO:
    怎么利用 repeated states 做 step-level credit assignment？

ARPO:
    不要等 repeated states；在 tool feedback 后 high entropy 处主动 branch

RAGEN:
    直接做 multi-turn RL 会 collapse，要看 reward std / entropy / gradient norm

RAGEN-2:
    entropy 不够，要看 MI / input dependence；reward variance 是 SNR proxy

AEPO:
    接受 ARPO 的 entropy branching，但修正过度依赖：
    rollout 端平衡 branch budget，update 端保护高熵 token 梯度
```

一条主线贯穿始终：**从"让模型在推理时多搜"到"用环境反馈训练 agent policy"，再到"解决训练过程中的 collapse 和 credit assignment"。**

每一个新方法都在修补前一个方法的缺陷，但也都引入新的假设和局限。更理想的下一步可能是结合：

> AEPO 的 entropy-balanced rollout + RAGEN-2 的 MI/input-dependence diagnostic + SNR-aware reward variance filtering

也就是：在高 entropy 节点 branch，但只强化那些既带来 reward variance、又保持 input-dependent reasoning 的分支。

---

_本文基于对 Agentic RL 相关论文的阅读笔记整理而成，后续会持续补充新的工作和实验分析。_
