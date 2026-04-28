## 一、原理

![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=YmIzZTNlZDI4MmQzM2NjOWI0ZTUzZTIyYmU5ZGExYTRfODh2dlJTY1lpUHB4QjhQbDFIaFN2d2VGcXV4OVlaOEdfVG9rZW46RkphOWJMNEhhb25SYnB4ZmZ3RmNBVk50bmpmXzE3NzY2NjYxMDE6MTc3NjY2OTcwMV9WNA)

#### Vanilla GRPO

- 输入一条query，生成多个response

- 基于规则或者奖励模型计算多个response的奖励

- 根据得到的奖励按照如下公式计算优势：

![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=NTgxM2ViYTQwZDg1YzA2NjYyYjE2N2VmYzdlOTVjN2VfNDdUVjBlYU41Zmdwd25jbWFNRTE5dTdpRGtuM1IzWlNfVG9rZW46Q294MGIza29ob2RWYlF4NjNFT2NoREg5bnFyXzE3NzY2NjYxMDE6MTc3NjY2OTcwMV9WNA)

- 根据优势计算损失，更新模型参数

#### Training-free GRPO

- 输入一条query，生成多个response

- 生成推理步骤总结：模型根据推理过程（多个步骤）和groundtruth（可有可无）对推理轨迹中的每一个步骤进行总结

- 汇总组内所有轨迹的总结，由大模型生成经验（在迭代过程中可对已有经验库中的经验进行新增、修改、删除、不变）

- 迭代完成后，模型参考最新的经验（类似于指导规则）进行推理

## 二、差异

- 原始的GRPO方法最终得到的是一个更新了参数的模型

- Training-free GRPO最终得到的是一个文本形式的经验库，无需对模型本身做任何更新，推理时外挂经验库即可（类似于lora的思想）

## 三、优劣势

#### 优势

- 无需更新模型参数，对于大参数模型的强化学习友好，节省显存

- 对模型形式无限制，无论是调用的第三方模型api还是本地部署的模型，均可使用此种方法进行优化

#### 劣势

- 对于大数据量场景不友好，可能出现经验库中经验过多，超出上下文长度限制或过长的上下文影响模型性能

- 对于小参数模型不友好，小参数模型推理和理解能力较差，性能提升不明显甚至下降

## 四、适用场景

- 垂直非通用场景，训练数据量有限（几百条），做sft或rl容易过拟合
- 对于大量数据场景，原始GRPO会更好（算力要求会更高）

一个潜在问题是，仅仅对比了训练成本，但是没有对比时间。

post-train bench

在数学（Math）和网页操作（Web）这类领域，问题在于：

- 它提取的经验往往是**结果导向**的，而不是**过程稳健**的。
- 模型可能总结出：“当看到 X 词时，执行 Y”。这在简单场景有效，但在需要 10 步以上推理的场景，这种“经验缝合”出来的 Prompt 可能会导致模型在中间步骤出现“幻觉补偿”，即为了符合经验而强行推理。

这种方法的真正价值和局限可以总结为：

- **有用之处**：它适合作为一种**“错误检查工具”**。比如在 Web 任务中，总结出“_不要反复点击已经失效的按钮_”这种硬性规则，模型是能理解并显著提升成功率的。
- **无用之处**：它很难产生真正的**“智能跃迁”**。它不能让模型学会它原本不会的复杂概念，只能让模型在已有的能力边界内，“少犯低级错误”。

你的这三个想法都非常深入，触及了当前大模型推理优化和可解释性研究的前沿问题。我们逐一探讨：

### 1. 关于 $Pass@k$（$k=50$）作为性能上界

**这个直觉非常准确，但需要加一个限定条件：它是“搜索空间”的上界，而非“泛化能力”的上界。**

- **作为上界**：如果 $Pass@50$ 的准确率是 80%，这意味着该模型在当前的参数下，其概率空间内**存在**通往正确答案的路径。如果 $Pass@1$ 只有 30%，那么剩下的 50% 空间就是通过 Prompt 优化、Reranking 或 RL 能够挖掘的“潜能”。
- **不完整性**：它之所以不完整，是因为模型在 $T > 0$ 时产生的正确答案可能是“蒙对的”（Luck paths）。
- **实际意义**：在工业界，我们常把 $Pass@k$ 作为一个基准。如果 $Pass@k$ 很高但 $Pass@1$ 很低，说明模型的**推理对齐（Alignment）**做得极差，这时候用这个项目的 Training-free GRPO 方法是非常合适的，因为有大量的“正确素材”可供归纳。

### 2. 如何自动化探索“非逻辑咒语”？

你提到的“不合逻辑但有效”的提示词（比如加一句 `This is very important for my career` 提升性能），确实可以通过类似本项目的方法进行自动化探索：

- **遗传算法 / 演化策略 (Evol-Prompt)**：
  - **方法**：不让模型提取“逻辑经验”，而是让模型对 Prompt 进行微小的**词法变异**（如变换语气、调整标点、添加无关填充词）。
  - _梯度替代_：在 Training-free 场景下，我们可以把“正确率提升”看作奖励信号，保留那些能让正确率提升的“变异”，哪怕它们看起来毫无逻辑。
- **Prompt 离散空间搜索**：
  - 目前有一些研究（如 **DSPy** 或 **OPRO**）已经在做类似的事：由 LLM 充当优化器，根据历史表现不断迭代生成新的指令前缀。
  - **探索方向**：你可以修改本仓库的 `ExperienceUpdater`，让它不总结经验，而是模仿人类各种奇怪的语气去重写 `PROBLEM_WITH_EXPERIENCE_TEMPLATE`，看哪种“玄学”前缀能让 $Pass@1$ 逼近 $Pass@50$。

### 3. 如何对“中间步骤幻觉补偿”进行定性与定量测试？

要分析模型是为了迎合 Prompt 规则而强行“圆谎”（幻觉补偿），可以尝试以下方法：

#### **定性分析 (Qualitative)**:

- **对比轨迹分析**：对比“有经验提示”和“无经验提示”下同一题目的失败轨迹。
- **关键特征**：寻找 **“逻辑断层”**。如果模型在倒数第二步突然跳到了一个正确结论，但前一步的计算逻辑完全不支持这个结论，这就是典型的补偿现象。

#### **定量分析 (Quantitative)**:

- **过程奖励模型探测 (PRM Detection)**：
  - 使用一个专门训练过的判别模型（如 Math-Verify 模型）对轨迹的**每一步**打分。
  - 计算轨迹的 **“累积逻辑分 vs. 最终结果”**。如果最终结果对，但中间步骤的分数很低，这就能定量证明“幻觉补偿”的发生概率。
- **扰动测试 (Perturbation Test)**：
  - 在模型推理的中间步骤，人为修改一个微小的中间常量（如把 $x=2$ 改成 $x=3$）。
  - **测试目标**：如果模型由于“经验过拟合”，依然强行在最后得出了原题的正确答案，说明它根本没在推理，而是在寻找符合 Prompt 预设的路径。

### 建议尝试

如果你想在当前仓库中实验，可以尝试修改 [training_free_grpo/math/experience.py](training_free_grpo/math/experience.py)，将 `ExperienceUpdater` 的倾向从“逻辑总结”转变为“指令重写（Rewrite）”，并观察在 AIME 或其他高难度数据集上，$Pass@1$ 的提升是否真的伴随逻辑结构的优化。

这种“黑盒优化”虽然有时能刷高分数，但也确实如你所说，可能掩盖了模型真正的推理缺陷。

# Neural Thickets和多教师 on policy disillation 的结合

# Cross Tokenizer Distillation

### 🎯 两种主要蒸馏方法

### 📝 Text Distillation（黑盒蒸馏）

- **工作原理**

教师模型生成数据微调学生模型，对教师模型和学生模型的词表没有任何限制，本质是微调，将教师模型的输出作为真实标签，通过交叉熵损失进行优化。

### 🔍 Logits Distillation（白盒蒸馏）

- **工作原理**：对齐学生模型和教师模型的输出概率分布

---

#### 📊 Tokenizer一致的情况

tokenizer一致时，教师模型和学生模型对于同一序列进行分词之后得到的token ids长度是一致的，且词表大小也是一致的，两个模型输出的logits\[bs, seq_len, vocal_size]形状也是一致的，转换成概率分布之后即可通过KL散度进行对齐优化。

---

#### ⚠️ Tokenizer不一致的情况

当tokenizer不一致时，对于同样的一条序列，经过两个tokenizer编码之后得到的token id是不一致的，长度也不一致，并且词表大小也是不一致的。

参考如下表格：

这两个不一致就导致了两个模型输出的logits形状不同，无法直接通过KL散度进行优化对齐。

针对这两个问题如何进行处理呢？

##### 🛠️ 序列长度不一致的处理

###### 方法一：截断处理

截断是最简单的做法，获取两者token ids长度的较小者作为截断长度，对原始序列进行截断

```python
min_length = min(len(student_token_ids), len(teacher_token_ids))
student_aligned = student_probs[:min_length, :]
teacher_aligned = teacher_probs[:min_length, :]
```

截断之后：

🟡 Qwen2.5: \[101329, 77419, 99609, 9754] → \['偷', '星', '九', '月']

🟡 GLM4: \[101379, 98978, 114687, 121577] → \['偷', '星', '九月', '333']

这样会损失一部分语义，某些情况下语义损失会更严重。

---

###### 方法二：分组合并 🎯

分组合并的处理方式就是按照token（不是token id，而是token str）进行token id的分组。因为token str是固定的，按照token str进行分组合并最终得到的长度也是固定的。

进行分组之后可得到如下结果：

🟢 Qwen2.5: \[\[101329], \[77419], \[99609, 9754], \[18, 18, 18]]

🟢 GLM4: \[\[101379], \[98978], \[114687], \[121577]]

对应关系：

组1: \[101329] ↔ \[101379] # '偷'

组2: \[77419] ↔ \[98978] # '星' &#x20;

组3: \[99609, 9754] ↔ \[114687] # '九月'

组4: \[18, 18, 18] ↔ \[121577] # '333'

有些组内是一个token，有些组内不止一个token，每个token都有一个概率分布，如何处理它们的概率呢？

一个简单的做法就是将组内token的概率进行累乘，累乘之后需要进行softmax，因为需要保证其仍然是一个概率分布。

这样，我们在序列长度维度就实现了对齐。

---

## 📈 词表大小不一致的处理

针对词表大小不一致的情况有如下处理方法：

### 方法一：排序填充法

先在第三个维度（词表维度，这一维度是词表中每个词的概率）按照概率大小进行降序排序。

然后对第三个维度进行padding，padding长度取较大词表的长度，填充值为0。

最后使用l1距离衡量二者差异。

```python
student_sorted = student_aligned.sort(dim=-1, descending=True).values
teacher_sorted = teacher_aligned.sort(dim=-1, descending=True).values

student_vocab_size = student_sorted.size(-1)
teacher_vocab_size = teacher_sorted.size(-1)
max_vocab_size = max(student_vocab_size, teacher_vocab_size)

if student_vocab_size < max_vocab_size:
    student_sorted = F.pad(student_sorted, (0, max_vocab_size - student_vocab_size))
if teacher_vocab_size < max_vocab_size:
    teacher_sorted = F.pad(teacher_sorted, (0, max_vocab_size - teacher_vocab_size))

aligned_loss = F.l1_loss(student_sorted, teacher_sorted, reduction="sum")
```

为什么先排序再计算l1_loss？

未匹配到的token没有自然的对应关系，计算其kl散度意义不大，所以先对概率进行排序，实际上是在比较两个分布的总体形状，而不是逐个对应。

---

### 方法二：混合处理法 🎯

对比教师模型和学生模型的词表，找出两个词表中一致的部分（token对应的文本一致即可，不考虑token id是否一致）。

对于两个词表中重合的部分（match）使用kl散度计算损失，对于不重合的部分（unmatch）使用sort + pad的方式，通过l1距离计算损失，最后对两部分损失进行加权，得到最终的蒸馏损失。

处理流程：

> ## 整体流程如下：

# On Policy Distillation

### 🎯on policy vs off policy

**Off policy（最传统、经典的知识蒸馏）**

学生模型的训练数据来自于真实数据或者由教师模型生成，即：

教师模型生成数据，学生模型学习教师模型的分布

**优势**：数据可复用，训练资源占用较低（教师模型数据可提前生成，无需在训练过程中生成）

**劣势**：只是一味的学习教师模型的分布，当教师模型产生的数据多样性或者质量较低，会导致学生模型泛化性能很差（推理与训练不一致，训练在教师模型的分布上学习，推理时在自己分布上生成）

**On policy**

学生模型的训练数据由学生模型自己生成，即：

学生模型自己与环境交互 → 生成数据 → 教师模型纠正学生模型分布

**优势**：归根结底学生模型是在自己的分布上学习，不再是一味地模仿，模型不仅能接收到正确到反馈，也能接收负反馈，这也决定了其泛化性能会更好（训练和推理都在自己到分布上）

**劣势**：如果学生模型自身产生了一些质量比较低的样本，会导致难以优化

### 🎯on policy distillation

我们很容易发现，on policy distillation和rl类似，都是由当前需要优化的模型进行rollout生成数据，然后根据外界的反馈信号进行优化

on policy distillation的反馈信号来自教师模型（kl散度），rl的反馈信号来自奖励模型，那么很自然的就可以想到，可以将教师模型与学生模型的kl散度作为奖励使用策略梯度来进行优化（rl），并且kl散度可以提供一种更细粒度的奖励信号（token级）

```python
reward = -kl
```

token的kl散度越小，说明教师模型与学生模型在当前token的分布越相似，就认为学生模型生成的token是好的，其奖励应该越大，反之，则给予更小的奖励

因为kl散度非负，所以reward都是负的，这不是很符合直觉，于是我们减去一个baseline

```python
adv = reward - reward_mean

```

reward_mean是样本内所有token奖励的均值

到这里，就可以使用策略梯度算法进行优化了

```python
logprobs_diff = student_probs - old_student_probs
ratio = torch.exp(logprobs_diff)
pg_losses = -adv * ratio
pg_losses2 = -adv * torch.clamp(ratio, 1.0 - self.args.cliprange, 1.0 + self.args.cliprange)
pg_loss_max = torch.max(pg_losses, pg_losses2)
```

ps：这里也不一定使用token粒度的奖励，将token粒度的kl散度聚合作为句子粒度的奖励也可以，并且重要性权重也可以采用句子粒度的比值

所以对于on policy distillation，可以有两种做法进行优化：

- 将kl散度作为直接目标进行优化（kl散度直接作为损失）

- 将kl散度作为奖励信号使用策略梯度算法进行优化

### **RLVR**

- 标量奖励（正确：1，错误：0）

- 信息瓶颈：只有对或错，模型知道错了，但是不知道错在哪

- 无正确答案生成时，优势为0（GRPO），无法优化，样本利用率低

### **SDPO**

$$\mathcal{L}_{\text{SDPO}}(\theta) = \sum_t \mathrm{KL}\bigl(\pi_\theta(\cdot | x, y_{<t}) \big\| \mathrm{stopgrad}(\pi_\theta(\cdot | x, f, y_{<t}))\bigr)$$

![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=NzJlMDQ0ZDljZDM0OGYxY2M2NTRjZjk0MmFjMjk5OGVfTU9wTDd3MzY1T2NPeDFkUDZIZ3hKZERodDZNVW92YVNfVG9rZW46UEpMUWJSZXY4bzR3bHJ4bmFmSWNWazRxbnJWXzE3NzY2NjcxMjM6MTc3NjY3MDcyM19WNA)

![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjY2NTdiOTlmNWVhMTk3NDA5OWQ5NGVmNGUwMzU5NzNfMDZOSUNkWERqTGZnN0k5MWllcEg2SGRnYWtwb2EwVUFfVG9rZW46TVU5bGJuZUhYb2ZQNmh4OXBua2NZRjI4bnFjXzE3NzY2NjcxMjM6MTc3NjY3MDcyM19WNA)

---

- **核心：Context Distillation**

  - 模型的context learning能力

  - 由带有更丰富上下文信息的模型作为教师模型，对学生模型的输出进行评判（KL散度）

---

- **反馈的来源**

  - 代码执行

    - 报错信息

  - 格式解析

    - 解析错误信息

  - 答案比对

    - 回答错误（和标准答案不匹配）

  - 工具调用

    - 工具输出

  - LLM的文本评判

---

- **流程**

  - 初始化模型（由同一个模型进行初始化，教师模型不参与梯度更新）

  - 学生模型采样，对于同一输入，生成多条输出（有正确的、有错误的）

  - 构建feedback，如果当前样本回答错误，将组内回答正确的输出和当前样本的错误信息拼接到教师模型上下文中，如果当前样本回答正确，将当前样本的输出拼接到教师模型的上下文

  - KL散度计算，将学生模型的输出拼接给教师模型，做一次forward，得到teacher logits，与学生模型的student logits计算KL散度，作为token粒度的reward信号

  - 更新学生模型的参数

---

- **教师模型如何更新？**

  - 不更新：能力上限受限

  - 每一轮直接替换为更新之后的学生模型：训练不稳定，不收敛

  - 论文提供了两种方法（$$\alpha$$很小0.05）：

    - 显示信任域方法:

      ![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=MjhhOTVmNTIyYWMzNTUzMWJlMGQ1YjY3OWNhOGIxYzNfNll1R3Izb3Z2S3ozbjVUVDlPc21XbERWa24wN0IxR1JfVG9rZW46SVhWUWJpTVF3b0JVNlF4TmVsN2NnQzkzbmVmXzE3NzY2NjcxMjM6MTc3NjY3MDcyM19WNA)

      - 参考模型固定（训练开始时的模型）

      - 每次训练前向传播时，同时计算当前模型和参考模型的对数概率（log-probs）

      - 按照公式对两者进行加权，得到的结果作为教师模型的预测值，

    - 指数移动平均方法（EMA）：

    ![](https://my.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGE4YzA4YzVhN2EwODBmMGE4MGE2MmM2MzY2MmJiOWJfbjlhclZmTVoxVThzZVhQSmE3NU1kWHByNzVHNDNRVnBfVG9rZW46TEd6YWJnQWxEb1VZNEZ4dUh0OWN0V3ZYbnlvXzE3NzY2NjcxMjM6MTc3NjY3MDcyM19WNA)

---

- **显存进一步优化**

  - Top-k KL散度：仅计算学生模型的 top- K logits 以及教师模型相应的 logits

Daniel Tang
