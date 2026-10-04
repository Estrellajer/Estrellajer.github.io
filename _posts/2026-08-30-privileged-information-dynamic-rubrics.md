---
layout: post
title: Privileged Information 与 Dynamic Rubrics：七篇 Post-Training 论文串读与实测
date: 2026-08-30 12:00:00
description: 七篇 Post-Training 论文串读：在 Outcome Reward 与 Full Reference 之间，如何用特权信息与动态量规打破困境。
tags: post-training distillation rlvr rubrics
categories: Research
---

Post-Training 长期存在一个 Trade-off：
- **如果只给 Outcome Reward，信号过于粗糙且稀疏**。模型生成了上千个 token 的长链，到底哪一步做对了、哪一个决策埋下了隐患，根本无法做细粒度的 Credit Assignment。摸黑探索的结果，往往是模型学会了寻找评分代理的漏洞，导致 Reward Hacking。
- **如果直接把 Full Reference 摆在面前做强监督，又损失探索能力**。模型会被强行约束在某种固定的表达方式和解题路径上，自主探索的能力与生成多样性会被迅速磨平。
OPD 在今年火起来后很多人都尝试利用它来实现两全其美的效果，但很快大家发现 Vanilla OPD 在很多场景下并不 Work。近期密集出现了一批探索 Privileged Information 与 Rubrics 的工作，核心思路是让特权信息更丰富、更抽象——它可以是标准 Rubric、多维度评判规则、专家错题或后验反思。相比原始直接塞标准答案当特权，这种形式明显更有效。
我梳理了手头近期相关的 7 篇论文。结合我们自己在机器上的复现与工程实测，整理了这篇笔记。这里不摆大表格，直接把每篇的具体机制、关键设计、实操启示与真实局限讲透。
## Online Rubrics Elicitation from Pairwise Comparisons (ICML 2026)
**机构与状态：**北美普通高校，ICLR 审稿 8/6/6/6 被拒，后转投录用于 ICML 2026，[arXiv:2510.07284](https://arxiv.org/abs/2510.07284)。
**Motivation：**预先写好的人工 Rubric 是静态的，只能防范已知问题。随着策略持续强化学习，模型会涌现出全新的错误模式或钻空子行为，固定规则根本覆盖不住。
**核心机制与 Pipeline：**
1. **成对采样（Pairwise Rollout）**：针对同一 Prompt，让当前策略与对照策略各采样一组回答，组成对比样本对；
2. **规则增量提取（Extractor）**：调用 o3-mini 对比成对回答，专门抓取现有 Rubric 未覆盖、但回答中客观表现出的质量差异，提炼为新的评分项 Criteria 并去重；
3. **细则评分与汇总（Grader）**：调用 GPT-4.1-mini 对更新后的每条 Criteria 做二元判断（通过与否），加权求和折算为综合得分；
4. **优势估计与更新**：基于该综合得分计算 Group Advantage，使用标准的 GRPO 算法更新策略。
**实操思考与局限：**
动态修补规则的切入点很务实，但架构上存在一个明显的断层：前端费了很大算力把各项质量维度拆解为清晰的 Criteria，后端却为了适配 GRPO，又把所有维度加权折叠成了一个单一标量。这一折叠，原本清晰的细粒度监督信号再次丢失，模型依然不知道具体哪一个 token 违反了哪条规则。此外，每个训练步都需要 o3-mini 提取规则、GPT-4.1-mini 打分判别，开销极大，本质上是靠两台外部商用强模型在持续做隐式外挂蒸馏。
## Rethinking Reward Supervision: Rubric-Conditioned Self-Distillation (COLM 2026)
**机构与代码：**耶鲁大学 Carrie Gu 团队，[arXiv:2606.19327](https://arxiv.org/abs/2606.19327)，代码 carriegu0818/RCSD。
**Motivation：**标量打分难以归因，而直接用 Reference 监督又容易把单一解题路径强行焊死。RCSD 将 Rubric 作为中间层，实现题目与答案的监督解耦。
**核心机制与 Pipeline：**
1. **Stage I：Rubric 生成器训练**。Student 仅输入 Question，Teacher 输入 Question 加 Reference。两者在 Student 生成的前缀上做 forward KL 对齐，训练一个 Question-only 的量规生成器，使模型在不看答案时也能输出针对该题的具体 Rubric；
2. **Stage II：Rubric 条件下的在策略自蒸馏**。Student 仅看 Question 生成 on-policy 回答；同底座 Teacher 沿用 Student 完全相同的前缀，但在 Context 中额外输入 Stage I 生成的 Rubric；Student 匹配 Teacher 的 next-token 概率分布；
3. **推理阶段**：完全移除 Reference、Rubric 和 Teacher，Student 独立推断。
**实操思考与局限：**
两阶段解耦非常工整，但在机制论证上存在一个未验证的疑点：在 Teacher 训练时，若 Reference 保持正确，但我故意喂给它一个写错的、甚至是对抗性的错误 Rubric，Teacher 的分布到底会不会跑偏？如果 Teacher 依然紧跟 Reference，说明核心特权信号仍然全部来自答案本身，Rubric 只是一个弱提示。
真正值得深入的方向是构建 Reference-Invariant Rubric Bottleneck：面对一道题，从多条解题思路完全不同但均正确的 Reference 中，提取出一致、最小且充分的 Rubric。这样提取出的规则才真正与具体词句表述解耦，逼近解题逻辑的本质。
## Rubric-Guided Self-Distillation: Post-Training Without Rubric Verifiers
**机构与状态：**《Online Rubrics》原班作者的新作，[arXiv:2606.12507](https://arxiv.org/abs/2606.12507)。
**Motivation：**既然像 Online Rubrics 那样把多维规则压缩成标量走 GRPO 无法做到 token 级的精准信用分配，为什么不直接拿掉 Verifier，让模型直接在概率分布层面对齐？
**核心机制与 Pipeline：**
1. **裸机采样**：Student 只看 Question，采样生成一条 on-policy 回答轨迹；
2. **特权前向计算**：同底座 Teacher 沿着 Student 相同的回答前缀进行前向计算，但 Teacher 输入中显式拼接了对应的 Rubric（即输入包含 Rubric、Question 与已有 Prefix）；
3. **Token 级分布蒸馏**：Student 逐 token 逼近 Teacher 的 next-token 输出概率，将带有 Rubric 特权的先验内化回无特权的策略中；
4. **推理阶段**：无需外部 Judge 打分，模型仅凭自身策略裸机生成。
**实操思考与局限：**
RGSD 揭示了一个非常重要的经验法则：**特权信息的“形式”，往往比它的绝对信息量更为关键。**
如果在蒸馏时给 Teacher 塞入过于具象的特权（例如具体的解题步骤或标准答案），就像 CoT 中答案对了但推理过程被过度诱导，会严重锁死策略的探索边界；反而是高维、抽象的评判规则（Rubric），能给模型保留充分的多样性解题空间。
但纯自蒸馏方案在攻坚难题时上限受限：因为同底座 Teacher 的认知上限决定了蒸馏天花板，它往往拼不过配置了强 Verifier 的 GRPO。GRPO 虽然经常通过 hack 判分规则取巧，但强 Verifier 能持续提供外生驱动力。从这个角度看，蒸馏强模型本质上是在隐式蒸馏强模型的 Judge 能力。
## EvoLM: Self-Evolving Language Models through Co-Evolved Discriminative Rubrics
**机构与代码：**华盛顿大学 Stella Li 团队，[arXiv:2605.03871](https://arxiv.org/abs/2605.03871)，代码 stellalisy/EvoLM。
**Motivation：**在没有高质量人工 Rubric 标注的环境下，模型自己生成的规则怎么判定好坏？EvoLM 给出的定义很直接：能够稳定区分优质回答与劣质回答的规则，就是有效规则。
**核心机制与 Pipeline：**
1. **时序对比构造偏好（Temporal Contrast）**：利用当前最新 Checkpoint 与历史旧 Checkpoint 对同一 Prompt 的输出构造天然的好坏偏好对；
2. **规则演化阶段**：冻结 Policy，训练 Rubric 生成器，优化目标是让外部判决器依据该 Rubric 能更准确地把新老模型回答排对（同时监控信息质量 IQ 与规则遵循度 RC 指标）；
3. **策略演化阶段**：冻结优化后的 Rubric 生成器，利用该 Rubric 生成判别信号更新 Policy。两者每隔 50 个训练步交替轮换一次。
**实操思考与局限：**
交替演化本身是标准范式，但这篇文章工程上最值得借鉴的是 **DimensionAwareFilter**：
**清洗和筛选训练样本时，绝不能只看加权综合得分。**很多回答在关键事实或逻辑主干上严重翻车，但由于语气谦逊、格式整齐，在其他软性维度上拿了高分，加权综合分一算居然及格了。如果直接入库，会极大污染模型。正确的工程做法是对每个核心维度单独设立硬门槛，所有关键维度同时达标才放行。此外，针对 Rubric 生成做缓存、使用严格的 JSON Schema 校验以及失败重试 Fallback，都是非常落地的工程细节。
## AgentOPSD: Recursive Self-Distillation for Agentic Reinforcement Learning
**机构：**美团 Longcat 团队，[arXiv:2608.05987](https://arxiv.org/abs/2608.05987)。
**Motivation：**在包含多轮工具调用、环境交互的长链路 Agent 任务中，整条轨迹动辄数十步。若对每一步都强制做 Student 与带特权 Teacher 的 token 级对齐，不仅算力爆炸，还会因惩罚了无害的动作微调（如换了个近义搜索词）而把策略教呆。
**核心机制与 Pipeline：**
1. **非均匀监督**：摒弃全轨迹无差别蒸馏，引入基于 Belief 的反事实因果归因；
2. **测算关键决策影响**：Teacher 拥有全局环境感知特权。算法评估在当前决策步 \$t\$，Student 的动作与 Teacher 动作的分歧是否会显著拉低整条轨迹的最终成功率；
3. **动态加权蒸馏**：如果该步属于致命分叉点（选错直接导致后续任务崩溃），则赋予极高的蒸馏权重；如果只是无关大局的搜索词变体或客套表达，则大幅降低甚至完全忽略其权重。
**实操思考与局限：**
剥去“Belief”这层学术包装，其底层本质就是**基于最终成功率反事实变化的关键步因果信用分配**。在长序列智能体训练中，最忌讳全局均匀发力。给核心分叉点强约束、给非关键步骤保留自由探索度，是保证长链路 Agent 不学僵的核心技巧。
## SEED: Self-Evolving On-Policy Distillation for Agentic Reinforcement Learning
**机构：**清华大学团队，[arXiv:2607.14777](https://arxiv.org/abs/2607.14777)。
**Motivation：**Agent 任务的环境反馈通常只有极其稀疏的 0/1 终局奖励，中间几十步动作到底哪一步有功、哪一步埋雷，无法得到即时信号。
**核心机制与 Pipeline：**
1. **后验技能冷启动（Hindsight Skills）**：先用外部分析器对离线轨迹提炼经验总结，通过 SFT 让模型学会“做完任务后复盘自身轨迹并总结技能”；
2. **在线动态自总结**：强化学习在线探索时，策略采样一条完整轨迹后，由同一个 Checkpoint 对自己的轨迹即时生成一份动态 Skill 复盘；
3. **条件概率增益门控**：固定轨迹中的动作序列，分别在前缀“有 Skill”和“无 Skill”两种上下文下重算动作的 log-prob。如果带上 Skill 后某一步动作的生成概率发生跳涨，说明该动作是成功关键点，通过置信度门控赋予额外的 OPD 蒸馏监督；
4. **双目标联合优化**：同时反传环境 0/1 终局奖励的 RL 梯度与上述技能引导的 OPD 自蒸馏梯度。
**实测与技术思考：**
论文中证明动态生成的 Skill 优于静态 Skill，逻辑是自洽的。**但我们在实际机器上跑了完整复现，得出了一个非常明确的一线结论：代码能跑通，指标确实涨了，但增益的真正源头并非模型内生的自我顿悟，而是通过后验反思的前缀格式，把底座模型 GLM-5.2 本身储备的高阶分析先验给诱导提炼了出来。**
同时，论文在实验呈现上有一个明显的取舍痕迹：在用不同模型总结 Skill 去做前置 SFT 阶段时，作者给出了极其详实的消融对比；但在最终端到端的完整强化学习环节，针对该机制的完整消融却语焉不详。工程经验表明，这种展示策略往往暗示最终 RL 增益中纯算法结构的贡献并不如宣传的那般独立。
## ReflectRL: Learning from Golden Negative Trajectories via Reflective-to-Direct Reasoning
**机构与状态：**论文通讯邮箱为 `bijinhe@outlook.com`，[arXiv:2608.03972](https://arxiv.org/abs/2608.03972)。
**Motivation：**在数学攻坚难题上，强如 DeepSeek-R1 也会频繁失败。传统后训练通常直接丢弃错题轨迹。但深入观察发现，顶尖模型在难题上的失败轨迹，往往前 80% 的审题、解题框架与推导都极具价值，仅仅在收尾阶段出现了局部算术失误或未收敛。直接丢弃这些“黄金负轨迹”（Golden Negative Trajectories, GNT）是巨大的数据浪费。
**核心机制与 Pipeline：**
1. **离线构建 GNT 矿池**：采集 DeepSeek-R1 在数学赛题上的输出，用形式化工具过滤出最终答案错误、但中间过程高质量的轨迹，沉淀出 OpenR1-GNT-69k 数据集；
2. **反思训练接口设计**：构造 Reflective Prompt，输入包含 Question、GNT 以及指令，要求模型执行“定位错误 -\> 修复推理 -\> 给出正确解答”；
3. **退火过渡机制（Reflective-to-Direct）**：强化学习早期，Rollout 包含 GNT 作为反思脚手架；随着训练进行，逐步降低 GNT 出现的概率，迫使模型将这种排错与反思能力内化回仅输入 Question 的直接推断模式；在 OPD 版本中，GNT 则作为 Teacher 侧独有的特权输入。
**实操思考与局限：**
把强模型的失误当做高纯度矿石来挖，立意非常巧妙。但从算法创新的角度审视，**这篇工作的贡献应当理性降级看待：它既没有修改底层奖励函数，也没有推导新的 RL 算法，本质上是一套设计极其精准的 Prompt 与 Context 接口重构**。模型能力的提升，核心依然来自对 DeepSeek-R1 强大解题习惯与纠错手势的隐式蒸馏。
更关键的是，该方案高度依赖一个前置假设：强模型的失误必须是“局部疏忽 + 高质量前缀”。如果大模型在特定题目上从开头就误解了题意，或者出现了概念性的深层幻觉，整条轨迹充斥着逻辑毒素，盲目把这种错题塞给模型去“反思修复”，反而会严重污染策略的解题空间。
## 总结与收敛思考
还有一篇清华的《ADARUBRIC》，[arXiv:2511.02344](https://arxiv.org/abs/2511.02344)，主要是把 Rubric 放在评估与任务自适应上做文章，机制大同小异，偏向 Evaluation 维度，这里就不再展开了。
将这 7 篇工作横向串联，结合实际踩坑体验，后训练与特权信息范式大致呈现出两条清晰的技术收敛主线：
**1. 警惕“无源自演化”的学术修辞：**<br>目前大量宣称纯内生“自我演化（Self-Evolution）”的系统，只要拆解其底层数据流，背后几乎无一例外都连接着 o3-mini、GPT-4、GLM-5.2 或 DeepSeek-R1 这一级别强模型的隐性输血。无论是用强模型提取动态规则、承担多维判决，还是挖掘高质量专家错题，其本质收益依然来自外生高阶智能的知识蒸馏。在没有外部强先验作为杠杆的情况下，仅靠同等水平的弱模型左右互搏实现真正的智力跃升，在当前架构下仍然是极难落地的虚妄设想。
**2. 特权信息的表征逻辑：抽象约束强于具象答案：**<br>从直接喂 Full Reference，到演进为多维度抽象 Rubric，再到基于因果归因筛选关键决策分叉，技术演进的清晰路径是：**特权信息越具体，模型探索越容易被锁死、过拟合；特权信息越抽象，在策略自蒸馏的效果越稳健。**把“监督模型背诵特定答案”转变为“引导模型在多维规则边界内完成对齐”，是当前后训练在探索多样性与稳定性之间取得平衡的最优解。
