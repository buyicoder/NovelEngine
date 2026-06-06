---
name: novel-brainstorm
description: 头脑风暴引擎——创意候选生成、反套路推演、假设性推演、题材融合。在任意创作阶段按需调用。
allowed-tools: Read Grep Bash Agent AskUserQuestion WebSearch
argument-hint: "[问题描述]"
---

# /novel-brainstorm — 头脑风暴引擎

## 目标

在创作的任意阶段提供发散性思维辅助。不替代作者判断，只提供可选项。

## 四种模式

| 模式 | 触发方式 | 示例 |
|------|----------|------|
| 创意候选 | `/novel-brainstorm 金手指还可以怎么设计` | 生成 3-5 个差异化方案 |
| 反套路 | `/novel-brainstorm --anti-trope 退婚流` | 给出反套路版本 |
| 假设推演 | `/novel-brainstorm --what-if 主角在决赛输了` | 推演连锁反应 |
| 题材融合 | `/novel-brainstorm --fusion 修仙+悬疑` | 分析融合方案 |

## 流程

### Step 1：收集上下文

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
```

读取当前项目已有的设定文件，确保头脑风暴基于已有世界观上下文。

### Step 2：调用 Brainstorm Agent

```text
Agent(
  subagent_type: "novel-engine:brainstorm-agent",
  prompt: "模式={创意候选/反套路/假设推演/题材融合}。问题={用户的问题}。已有设定={设定摘要}。请基于上下文给出候选方案。"
)
```

### Step 3：展示结果

展示 Agent 返回的候选方案，标注每个方案的优劣和兼容度。作者可选择：
- 采纳某个方案 → 更新到相应设定文件
- 基于某个方案进一步深挖 → 继续头脑风暴
- 都不满意 → 换角度重新发散

## 模式自动检测

如果用户没有显式指定模式，根据问题内容自动判断：
- 包含"还可以/还有其他/怎么设计" → 创意候选
- 包含"太老套/太套路/反着写" → 反套路
- 包含"如果/假设/要是...会怎样" → 假设推演
- 包含"A+B/融合/结合" → 题材融合
