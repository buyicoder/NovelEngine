---
name: novel-deconstruct
description: 拆解参考小说，提取可迁移的创作模式。快速模式(黄金三章)和深度模式(逐章情节点)。不复制原作事实。
allowed-tools: Read Write Edit Grep Bash Agent AskUserQuestion WebSearch WebFetch
argument-hint: "[书名或章节范围]"
---

# /novel-deconstruct — 拆书分析

## 流程
1. 收集输入(书名/来源/分析模式)
2. 调用 deconstruction-agent
3. 校验质量(coverage≥85%, confidence≥0.85)
4. 保存到 拆书存档/<书名>/
5. 呈现结果摘要

## 跨书对比
`/novel-deconstruct --compare <A> <B>` 从存档加载两份分析做对比。
