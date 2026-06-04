---
layout: post
title: Leetcode学习笔记
date: 2026-02-12 9:30:00
description: Notes on Leetcode
tags: coding
categories: Learning
---

## 数组

### 三数之和

如果只去剪枝，然后在这之前没有对 x 去重的话，有的测试用例会通不过，因为会直接 break。然后这样输出的是 null，而不是空数组：

> 输入 `nums = [0,1,1]`，输出 `null`，预期结果 `[]`

```python
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        ans = []
        n = len(nums)
        for i in range(n - 2):
            x = nums[i]
            if i > 0 and x == nums[i - 1]:
                continue
            if x + nums[i + 1] + nums[i + 2] > 0:
                break
```

### 合并区间（lambda 表达式）

```python
intervals.sort(key=lambda p: p[0])
```

可以拆成三部分理解：

1. `sort()` — 对列表进行**原地排序**，默认按元素本身排序
2. `key=...` — **告诉 Python 按什么规则排序**，每个元素先"映射"成一个值，再按这个值排序
3. `lambda p: p[0]` — 匿名函数，等价于 `def f(p): return p[0]`，`p` 是每个区间（如 `[1, 3]`），`p[0]` 是区间的左端点

整体意思：**按照每个区间的第一个元素排序**。

### 238. 除自身以外数组的乘积

前后缀的起始条件：前缀应遍历范围是 `1~N-1`，这样第二个才能得到左边的范围。最后乘积没必要再遍历 index，可以用 zip：`[p * s for p, s in zip(pre, suf)]`

### 48. 旋转图像

要考虑遍历上三角还是下三角，否则不对 j 的范围进行限制的话，交换两次等于没交换。

## 链表

### 206. 反转链表

头插法时忘记设置一个头为虚拟节点，`cur.next = cur` 会死循环。

### 19. 删除链表的倒数第 N 个节点

while 的判断条件是 `right.next` 而不是 `right`，因为要让 `left` 停在倒数第 N 个节点的前一个节点，而不是第 N 个节点本身。

### 24. 两两交换链表中的节点

判断条件不能只写 `node0.next`，还应该判断 `node0.next.next`，因为两两交换需要保证至少有两个后续节点。

### 25. K 个一组反转链表

不知道怎么把反转后的这一段接回去，并更新 `p0` 到下一组的起点。

### 链表操作记忆

```
👉 改 .next = 改链表
👉 改变量 = 不影响链表

📌 对照记忆
写法         本质      影响
p = p.next   指针移动  ❌ 不改链表
p.next = x   修改连接  ✅ 改链表
```

### 138. 随机链表

没有看清楚题目——有的节点没有 random。所以最后还需要遍历，第二次来进行 random 的拷贝。

### 148. 排序链表

1. 找中间节点需要把中间节点的前一个节点和中间节点分开，否则前半部分调用还是会调用到后面的节点
2. 分治：递归对 `head1` 和 `head2` 处理

## 排序

### 快速排序：`< pivot` vs `<= pivot`

代码扫描时写的是：

```python
while i <= j and nums[i] < pivot:
    i += 1
while i <= j and nums[j] > pivot:
    j -= 1
```

它没有写成 `nums[i] <= pivot` / `nums[j] >= pivot`，原因是：**等于 pivot 的元素不能被一边倒地跳过去，否则大量重复元素时会退化。**

以 `[2, 2, 2, 2, 2]`，pivot = 2 为例：`<` 和 `>` 条件下，`i` 和 `j` 都会在等于 pivot 时停下来，交换后再同时往中间移动，避免每次只缩小一个元素。

**扫描条件：** i 跳过 `< pivot` 的，j 跳过 `> pivot` 的
**划分结果：** 左边 `<= pivot`，右边 `>= pivot`

这不是矛盾，而是为了让等于 pivot 的元素分散到两边，划分更均匀。

### 为什么最终和 j 交换？

循环结束后：

```
[ pivot | <= pivot | >= pivot ]
  left          j   i
```

`j` 是左侧最后一个 `<= pivot` 的位置，所以 pivot 应放到 `j`。如果和 `i` 交换，pivot 左边可能出现大于 pivot 的值。

e.g. `[4 | 1, 3, 2 | 5, 6]`，`nums[j] = 2 <= 4`，`nums[i] = 5 >= 4`。和 `j` 交换得 `[2, 1, 3, 4, 5, 6]` ✓；和 `i` 交换得 `[5, 1, 3, 2, 4, 6]` ✗，pivot 左边出现了 `5`。

## 螺旋矩阵

### 常见错误

1. `x, y = i + DIR[di][0], y + DIR[di][1]` — `y` 未定义，应改为 `j + DIR[di][1]`
2. `matrix[x][y] = None` 用作判断 — `=` 是赋值，判断应写成 `matrix[x][y] is None`

### 正确代码

```python
DIR = (0, 1), (1, 0), (0, -1), (-1, 0)

class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        m, n = len(matrix), len(matrix[0])
        ans = []
        i = j = di = 0

        for _ in range(m * n):
            ans.append(matrix[i][j])
            matrix[i][j] = None

            x, y = i + DIR[di][0], j + DIR[di][1]

            if x < 0 or x >= m or y < 0 or y >= n or matrix[x][y] is None:
                di = (di + 1) % 4

            i += DIR[di][0]
            j += DIR[di][1]

        return ans
```

### 核心理解

代码没有真的走到越界位置。`x, y = ...` 只是**试探坐标**（预判下一步是否合法），`i += ...` / `j += ...` 才是**真正移动坐标**。

流程：当前位置 → 预判下一步 → 不合法则转向 → 按新方向移动。所以无需"减回来"。

13.罗马数字转整数

pairwise function不知道，统一六种规则（比较相邻，前小后大加相反数）

## PyTorch

### Linear 层的矩阵乘法

x 通常是 `[batch_size, in_features]`，weight 存成 `[out_features, in_features]`。要用 `x @ weight.T` 得到 `[batch_size, out_features]`。如果写 `weight @ x` 维度对不上；写 `weight @ x.T` 结果会是 `[out_features, batch_size]`，还要再转置。

### x.max(dim=...)

返回"最大值 + 最大值位置"：`.values` 取最大值本身，`.indices` 取最大值的下标。

### torch.sqrt

输入必须是 Tensor 而不是 int，所以缩放 attention 时应该用 `math.sqrt`。

### super().**init**()

`nn.Module` 的 `__init__` 会准备：记录子模块、记录参数、支持 `.to(device)`、`.parameters()`、`train()/eval()`、`state_dict()`。不写的话，后面定义的层不会被正确注册。

### shape vs size

- `shape` 是属性，用 `[]`
- `size` 是方法，用 `()`

```
K.shape[-1] == K.size(-1)
K.shape[1]  == K.size(1)
```

### GQA 中的 expand + reshape

`reshape` 只能改形状，不能复制数据；`expand` 负责制造"复制视图"，`reshape` 只是把复制后的 head 维度合并起来。所以在 GQA 里需要 `expand` 再 `reshape`，而不能直接修改维度的值。

## 杂项

### range(start, stop) 补充

如果 `n = 1`，`for i in range(1, 1)` 因为 `start == stop`，循环次数为 0。
