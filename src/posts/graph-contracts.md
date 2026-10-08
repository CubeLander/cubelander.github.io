---
title: "Graph 不是开关：捕获、重放与状态所有权"
description: "地址稳定只是开始。请求容量、首次 replay、context/query 拆分和 DMA 所有权，共同决定一张图能否正确执行。"
date: 2026-10-08
order: 2
category: 执行机制
topics: [Graph Replay, 状态契约]
scope: "面向关心执行细节的读者。讨论历史 DSV4 TP8 / K5 路径，不泛化到所有模型与并行布局。"
sources:
  - label: DSV4 执行路径技术报告
    path: docs/REPORT.zh-CN.md
  - label: 分离 context 与 query 的实验
    path: prototypes/full-mixed/SPLIT_DRAFT.md
  - label: 结果账本与正确性边界
    path: RESULTS.md
---
## 捕获的是一段程序，也是一组假设

Graph replay 能减少重复的 host 提交工作，但前提是下一次输入仍然符合捕获时的执行契约。

“指针没有变化”只是其中一项。张量维度、request metadata 的容量、query offsets、捕获时的标量边界，都可能影响已捕获程序会做什么。真正需要维护的是：**地址可以复用，内容可以更新，而程序依赖的结构不能被悄悄换掉。**

BetterScale 的 DSV4 target FULL 工作，对这一点给出了几个具体例子。

## 空席位不等于随意增加一个 dummy request

假设图的 descriptor 保留了四个请求槽位，但某一次实际只有两个请求。此时仍然需要表达四槽位的元数据结构，同时让多出的槽位不产生额外工作。

历史实现采用的处理是重复最后一个真实 query offset，把未使用席位表达成零长度。下面是说明这种结构的简化例子，并非某次实验的原始张量：

```text
真实 query 数： 3, 2
有效 offsets： [0, 3, 5]
四槽位表达：    [0, 3, 5, 5, 5]
                     └─ 两个零长度槽位 ─┘
```

如果通用 padding 逻辑临时引入一个不同容量的 dummy request，replay 时的元数据维度就可能不再符合 capture。输入看似已经“补齐”，结构却改变了。

同样，RoPE 缓冲需要持久存在；target 与 draft 还要各自保留独立缓冲，避免在不同阶段覆盖对方仍要使用的数据。

K5 与 TP8 的对齐也不是取两者较大值这么简单。历史路径同时需要满足 6 和 8 的整除约束，因此桶大小需遵循最小公倍数 24。这是 capture bucket 的兼容性修复，不是修改投机长度。

## 把“大 context”与“小 query”分开

Draft 路径里有两个规模不同的任务：

- 把 N 行 target hidden 写入 draft context KV；
- 根据少量 query 生成候选 token，再交给原生拒绝验证。

对非普通 decode 波次，历史 split 路线的结构是：

```text
N 行 target hidden
        ↓
原生 context KV 写入（实际 N 行）
        ↓
小 query graph
        ↓
原生拒绝验证
```

Query graph 以请求数组织私有 metadata bank，更新数据而不重新绑定地址。普通 K5 decode 则继续使用已有的小 context + query 融合图，并不是所有情况都强制拆开。

这项变化有很具体的收益范围：6+17 的小 mixed 观察从 63.96 ms 到 46.37 ms；4112-token 首波则从 259.65 ms 到 262.16 ms，没有加速。这些是单次配对形状观察，不是稳定服务吞吐的统计结论。

它说明的不是“拆分优于融合”，而是**两段工作是否应该融合，取决于它们的实际规模和复用边界。**

## 首次 capture 不是已经交付了一次执行

一个容易漏掉的正确性问题，发生在第一次调用：初始化图与提交一次服务调用，并不总是同一件事。

历史检查发现，首次 capture 返回的候选 ID 可以一致，但 KV 状态仍不一致。显式执行第一次 replay 后，这个边界才被补齐。因此不能只检查第二次、第三次 replay，然后认为整个生命周期正确。

验证至少需要覆盖：

1. 创建捕获资源的初始化阶段；
2. 对第一次真实调用的交付；
3. 后续 replay 对输入更新的消费；
4. 请求变化或不满足准入条件时的回退行为。

这里的教训是生命周期必须进入测试，不只是稳态循环。

## 等待可以后移，所有权不能省略

在请求集合和索引稳定、全部为 K5 verification 的已准入波次里，CPU 可以使用保守长度上界进行规划，而实际 position、slot mapping 和精确进度仍由 device 逻辑决定。

执行顺序因此可以从“先等 CPU 收据，再提交 target”，改为“先提交 target，再完成相应 bookkeeping”。但其中还有一道不可省略的边界：**当前 input DMA 必须退役，之后 CPU callback 才能改写它可能触及的 pinned host buffer。**

同一 device stream 的顺序能表达设备任务依赖，却不能自动授权 CPU 覆盖一块设备还在读取的 host 内存。请求加入、退出或 mixed 等不满足条件时，仍需要保留原同步路径。

因此，这项优化不是通用的“去掉同步”，也不是完整 N+2 scheduler；它是在受限范围内，重新安排某些收据的消费位置。

## 正确性比较也需要正确的观察单位

在共享 KV 池里，不同 dtype 的 tensor view 可能指向同一块物理 backing。若把整个 backing 依次当成 BF16 或 FP32 读取，别的状态区域可能被解释成异常数值，甚至看似出现 NaN。

严格的历史 shadow 检查因此按唯一物理 backing 比较原始字节，而不是对每个 view 都重复解释整个池。有效输出行与无语义契约的 padding 行也不能混为一谈。

这并不是说字节比较能替代所有数值容差验证；它说明**比较对象必须与实际的状态所有权一致**。同样需要注明，被比较的是 native graph、eager，还是 padded 程序，不能在不同实验之间偷偷换掉参考意义。

Graph 的价值来自复用，Graph 的风险也来自复用。只有把这些边界变成明确契约，减少提交开销才不是在借用未来的正确性。
