# Scholar Monitor Report

**Run:** 2026-05-28 21:10 UTC  |  **Total:** 57  |  RSS 1  |  CHG 1  |  FIRST 1  |  OK 54  |  ERR 0

---
## New Publications & Blog Posts (1)

### CV
**[Junyao Hu Blog](https://junyaohu.github.io/)**
- [用AI回顾我去年所有周报，差点破防了丨2023总结](https://junyaohu.github.io/blog/2023-review/) - ?
- [糖尿病遗传风险检测挑战赛 - Coggle 30 Days of ML（22年7月）](https://junyaohu.github.io/blog/30days-of-ml-202207/) - ?
- [端正奋斗心态，追寻自身热爱（2022朋辈指导讲座文字稿）](https://junyaohu.github.io/blog/advice-for-freshman-2022/) - ?
- [推免一周年丨人生轨迹可以由自己选择吗？](https://junyaohu.github.io/blog/baoyan-1th-anniversary/) - ?
- [基于Bert-UNILM及Django的智能创作平台 - 软件杯2022](https://junyaohu.github.io/blog/cnsoft2022-bert-django-demo-easywriting/) - ?
- [Firefly 代码块示例](https://junyaohu.github.io/blog/code-examples/) - ?
- [C++常用STL](https://junyaohu.github.io/blog/common-stl-of-cpp/) - ?
- [中国矿业大学2020-2021-1高级语言程序设计实验期末考题](https://junyaohu.github.io/blog/cpp-practice-exam-2020-2021-1/) - ?
- [北京邮电大学鲁鹏《计算机视觉（本科）》笔记](https://junyaohu.github.io/blog/cv-base-learning-bupt-lupeng/) - ?
- [《动手学深度学习》笔记](https://junyaohu.github.io/blog/d2l/) - ?
- [草稿示例](https://junyaohu.github.io/blog/draft/) - ?
- [Firefly 文章加密](https://junyaohu.github.io/blog/encrypted-demo/) - ?
- [Firefly 一款清新美观的 Astro 博客主题模板](https://junyaohu.github.io/blog/firefly/) - ?
- [Firefly 布局系统详解](https://junyaohu.github.io/blog/firefly-layout-system/) - ?
- [First post](https://junyaohu.github.io/blog/first-post/) - ?
- [内网穿透配置](https://junyaohu.github.io/blog/frp-setting/) - ?
- [Firefly 简单使用指南](https://junyaohu.github.io/blog/guide/) - ?
- [和鲸社区2022咸鱼打挺夏令营-机器学习原理与实践·闯关-作业答案与部分解析](https://junyaohu.github.io/blog/heywhale-summer-camp-ai/) - ?
- [和鲸社区2022咸鱼打挺夏令营-数据结构·闯关-作业答案](https://junyaohu.github.io/blog/heywhale-summer-camp-ds/) - ?
- [和鲸社区2022咸鱼打挺夏令营-【NLP最佳实践】Huggingface Transformers实战教程-笔记、作业答案与部分解析](https://junyaohu.github.io/blog/heywhale-summer-camp-transformer/) - ?

---
## Pages with Changes (1)

### Test time Scaling
**[孙宇](https://yueatsprograms.github.io/)** [英伟达]
```diff
--- 孙宇 (previous)
+++ 孙宇 (current)
@@ -1,188 +1,72 @@
-搜索此网站
-嵌入的文件
-跳至主要内容
-调至导航栏
-I am a Machine Learning researcher.
-My name is Ke Sun (孙科). I am currently a postdoctoral researcher at University of Pennsylvania, working with
-Prof. Qi Long
-and
-Prof. Weijie Su
-, starting from early 2026.
-I was a postdoctoral f
-ellow working with
-Prof. Susan A. Murphy
-at Harvard University in 2025.
-I received my Ph.D. degree in
-Statistical Machine Learning
-from
-University of Alberta in 2024, advised by
-Prof. Linglong Kong
-, also affiliated at
-Alberta Machine Intelligence Institute (
-Amii
-)
-. I was fortunate to visit
-Prof. Chengchun Shi
-at the London School of Economics and Political Science
-in 2023.
-I obtained my
-MPhil in Data Science at Peking University
-in 2020 advised by
-Prof. Zhouchen Lin
-and
-Prof. Zhanxing Zhu
-. I earned my Bachelor's degree in finantial statistics and risk management from SouthWestern University of Finance and Economics in 2017.
-Contact
-:
-kesun6[AT] upenn
-.edu
-/
-ke.sun[AT]
-pennmedicine.upenn.edu
-Links
-:
+Yu Sun
+Email: ys646 [at] stanford.edu
+I'm a postdoc at Stanford University and a researcher at NVIDIA.
+My research focuses on continual learning, specifically a conceptual framework called test-time training, where each test instance defines its own learning problem.
+My Research
+The high-level goal of my research is to enable AI systems to continuously learn like humans.
+Specifically, my research addresses two aspects in which human continual learning truly stands out.
+First, each person has a unique brain that learns within the context of their individual life.
+This personalized form of continual learning is quite different from, for example, a chatbot model that is fine-tuned hourly using the latest information available worldwide.
+While such a model does change over time, it is still the same at any given moment for every user and every problem instance.
+Second, most human learning happens without a boundary between training and testing.
+Consider your commute to work this morning. It is both "testing" because you did care about getting to work this very morning, and "training" because you were also gaining experience for future commutes.
+But in machine learning, the train-test split has always been a fundamental concept, often taught in the first lecture of an introductory course as:
+"Do not train on the test set!"
+I believe that these two special aspects of human learning are intimately connected and should be studied together in the field of AI.
+In particular, continual learning will be most powerful when it targets the specific problem instance that we care about, conventionally known as the test instance.
+To focus on these two aspects, I have been developing a conceptual framework called test-time training since 2019.
+The best way to learn more about the technical side of my research is to look at the selected papers below.
+Selected Papers
+For a complete list of papers, please see my
 Google Scholar
-/
-CV
-/
-Github
-/
-LinkedIn
-Research Interests
-My research interest is
-reinforcement learning
-, especially the
-algorithm
-ic foundations and development
-grounded in
-mathematical and statistical principles.
-My key research goal is to build agents with effective perception, memory,
-reasoning,
-planning, exploration, and adaptation in complex and unknown environments to achieve
-decision intelligence
-, with broad applications in games, robotics, control systems, healthcare, economics, and language.
-[1] Algorithmic and Theoretical Foundations in Pure RL (RL as Problem Formulation):
-Uncertainty & Exploration
-:
-Distributional Learning and Risk Control, Entropy Regularization and Exploration
-Robustness & Adaptation
-:
-Environmental Nonstationarity
-, Safe/Robust RL, Transfer/Multi-task/Meta/
-Continual RL
-Offline &
-Causality
-: Offline and Hy
-brid
-RL, Causality for RL, Adaptive Experiment Design
-[2] Foundations in RL for General Intelligence (RL as Optimization Tool vs Problem Formulation):
-Language & Agentic AI
-: Alignment, Reasoning, Post-training, Agentic RL, Multi-agent interaction
-Robotics & Embodied AI
-:
-Model-based RL and
-World Model, Generative and Self-supervised RL, Imitation learning
-Vision & Multimodal Models
-: Vision-language-action, Multimodal reasoning, Active perception
-Selected
-Preprints
-/ Publications [
-Full Publications
+.
+Learning to Discover at Test Time
+Mert Yuksekgonul*, Daniel Koceja*, Xinhao Li*, Federico Bianchi*, Jed McCaleb, Xiaolong Wang, Jan Kautz, Yejin Choi, James Zou†, Carlos Guestrin†, Yu Sun* (*: core contributors)
+[
+paper
 ]
-[7] Ke Sun*,
-Yizhou Zhao*, Jiayi Xin, Qi Long, Weijie Su
-.
-CurveRL: Principled Distribution-Aware Context Reweighting for LLM Reasoning
-(
-submitted
-), 2026. [
-Code
-]
-[6] Ke Sun,
-Linglong Kong, Hongtu Zhu, Chengchun Shi.
-ARMA-Design: Optimal Treatment Allocation Strategies for A/B Testing in Partially Observable Experiments
-.
-(
-Minor
-Revision in Journal of American Statistical Association, 202
-6
-) [
-Code
-]
-[5]
-Ke Sun
-*
-,
-Hongming Zh
-ang*
-,
-Jun Jin, Chao Gao, Xi Chen, Wulong Liu, Linglong Kong.
-Principled Fast and Meta Knowledge Learners for Continual Reinforcement Learning
-.
-International Conference on Learning Representations (
```

---
## First-time Snapshots (1)

- 孙科