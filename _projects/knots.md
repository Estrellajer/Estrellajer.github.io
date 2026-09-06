---
layout: page
title: Knots
description: 面向航空航行通告（NOTAM）的大规模多智能体增强专家标注数据集与语义解析Prompt优化基准。
importance: 2
category: research
img: /assets/img/publication_preview/knots.png
github: https://github.com/Estrellajer/Knots
---

**Knots** 是针对航空通告（Notices to Air Missions, NOTAMs）语义解析任务构建的大规模专家标注数据集与大模型优化基准。该项目构建了涵盖全球 194 个飞行情报区（FIR）的 12,347 条高质量专家级 NOTAM 标注数据，并通过多智能体协作框架实现全字段语义挖掘与知识对齐。

项目代码与数据集开源于 [GitHub: Estrellajer/Knots](https://github.com/Estrellajer/Knots)。

---

### 背景与挑战

航行通告（NOTAM）承载着航路临时关闭、导航设施失效、禁航区设立等关乎飞行安全的关键动态。然而，由于历史沿革与电报通信标准，传统通告多采用极度缩写的大写电报格式（如 `RWY 01L/19R CLSD DUE TO WIP`），存在严重的语法不规范、行话隐式语义丰富以及跨系统解析难度高等痛点。

---

### 核心亮点

1. **真实多源的专家级基准**：跨越全球六大洲 194 个飞行情报区，采集并规范化 12,347 条高复杂度实测通告，经过航空专业领域专家严格校验。
2. **多智能体字段发现流水线**：提出结合多智能体协作的 Prompt 深度挖掘机制，自适应识别复杂航空通告中的隐含时间段、地理坐标圈定与条件制约。
3. **闭环演进与语义理解**：结合知识图谱检索增强（KG-RAG）与自我反思机制，大幅提升基础大语言模型在严苛安全约束下的通告结构化解析准确率。
