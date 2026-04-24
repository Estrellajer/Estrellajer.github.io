---
layout: post
title: Leetcode学习笔记
date: 2026-02-12 9:30:00
description: Notes on Leetcode
tags: coding
categories: Learning
---

## Python 语法

### dict

```python
d = defaultdict(list)
if key not in d:
    d[key] = []
```

`d.values()` 返回的是 `dict_values([...])`，不是 `list`，而是一个视图对象。需要转成列表时可以写：

```python
list(d.values())
```

### str

`sorted("eat")` 返回的是 `list`，而不是 `str`：

```python
['a', 'e', 't']
```

`'分隔符'.join(可迭代对象)`

## 三数之和：极简版

### 1. 排序

作用：

- 给双指针创造单调性
- 方便去重
- 便于剪枝

### 2. 枚举第一个数 i

```python
for i in range(n - 2):
    if i > 0 and nums[i] == nums[i - 1]:
        continue
```

### 3. 双指针找另外两个数

```python
j = i + 1
k = n - 1

while j < k:
    s = nums[i] + nums[j] + nums[k]
```

- `s > 0`：`k -= 1`
- `s < 0`：`j += 1`
- `s == 0`：记录答案，然后两边一起去重

### 4. 找到解后去重

```python
j += 1
k -= 1

while j < k and nums[j] == nums[j - 1]:
    j += 1

while j < k and nums[k] == nums[k + 1]:
    k -= 1
```

## 时间复杂度

```text
O(n²)
```

## 最常见错误

1. 写成 `if + if + else`。
   必须是 `if / elif / else`。

2. 忘记排序。
   双指针会直接失效。

3. 去重位置写错。
   容易得到重复解。

4. 找到解后只移动一边。
   容易死循环。

## 记忆模板

> 排序 → 固定 `i` → 双指针逼近 → 找到解后双向去重

更短的速记版：

```text
排序
枚举 i
两头夹
等于收
两边跳
```

## 补充：range(1, n) 在 n = 1 时会发生什么？

在 Python 里，`range(start, stop)` 表示“从 `start` 开始，到 `stop` 之前结束”，不包含 `stop`。

如果 `nums = [5]`，那么 `n = 1`，此时：

```python
for i in range(1, 1):
    ...
```

因为 `start == stop`，循环次数就是 `0`。

## 后记

刷力扣还是要趁早，不要像笔者一样，面对不知道什么时候到来的 coding 面，像面对达摩克利斯之剑一样惴惴不安。
