---
layout: post
title: Leetcode学习笔记
date: 2026-02-12 9:30:00
description: Notes on Leetcode
tags: notes
categories: Skill
---

### python语法

#### dict
d = defaultdict(list)等价
if key not in d:
    d[key] = []
字典的 values()
d.values()


返回：

dict_values([...])


不是 list，而是视图对象。

转换为列表：

list(d.values())

#### str
sorted返回的是list而不是str
sorted("eat")
# ['a','e','t']

'分隔符'.join(可迭代对象)


三数之和：好，给你一份**极简、高密度版本**，只保留核心结构和高频错误。

---

# 一、核心思路（4 步）

### 1️⃣ 排序

为：

* 双指针创造单调性
* 去重
* 剪枝

---

### 2️⃣ 枚举第一个数 i

```python
for i in range(n-2):
```

跳过重复：

```python
if i > 0 and nums[i] == nums[i-1]:
    continue
```

---

### 3️⃣ 双指针找两数

```
j = i+1
k = n-1
```

```
while j < k:
    s = nums[i] + nums[j] + nums[k]
```

* s > 0 → k--
* s < 0 → j++
* s == 0 → 记录 + 双边跳重

---

### 4️⃣ 去重（找到解后）

```python
j += 1
k -= 1
while j < k and nums[j] == nums[j-1]: j += 1
while j < k and nums[k] == nums[k+1]: k -= 1
```

---

# 二、时间复杂度

```
O(n²)
```

---

# 三、最常见错误（高频 4 个）

1. ❌ 写成 `if + if + else`
   必须 `if / elif / else`

2. ❌ 忘排序
   → 双指针失效

3. ❌ 去重位置错
   → 重复解

4. ❌ 找到解后只移动一边
   → 死循环

---

# 四、记忆模板（一句话）

> 排序 → 固定 i → 双指针逼近 → 找到后双向去重

---

如果你要更极简记忆版：

```
排序
枚举 i
两头夹
等于收
两边跳
```

需要我再压缩成考试速记卡片吗？


range(1, n) 在 n=1 时发生了什么？
在 Python 中，range(start, stop) 的规则是：从 start 开始，到 stop 之前结束（不包含 stop）。

如果 nums = [5]，那么 n = 1。

此时循环语句变为 for i in range(1, 1):。

因为 start (1) 已经不小于 stop (1) 了，所以这个循环的迭代次数为 0。


### 后记

只能说刷力扣还是要趁早，不要像笔者一样面对不知道什么时候的coding面，犹如面对达摩克里斯之剑一样。惴惴不安。