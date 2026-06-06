---
name: novel-outline
description: 剧情走向规划——从总纲到卷纲到章纲，逐层规划全书剧情骨架。章纲粒度严格控制在每章一句话核心事件。
allowed-tools: Read Write Edit Grep Bash Agent AskUserQuestion
argument-hint: "[卷号或'all']"
---

# /novel-outline — 剧情走向规划

## 目标

基于已有的世界观设定，逐层生成总纲→卷纲→章纲。章纲严格控制在每章一句话（20-50字），不做任何展开。

## 流程

### Step 1：预检与加载

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" preflight
```

检查设定集是否有至少一个已完成的设定文件。如果没有，提示先运行 `/novel-worldbuild`。

### Step 2：加载设定上下文

读取以下文件供 Outline Agent 参考：
- `设定集/世界观.md`
- `设定集/力量体系.md`（如有）
- `设定集/主角卡.md`（如有）
- `设定集/势力格局.md`（如有）
- `大纲/总纲.md`（如已存在，表示已有规划，进入增量模式）

### Step 3：确认目标规模

询问用户目标总字数和总章数。如果用户不确定，给出建议（如"100万字 ≈ 500章"）。

### Step 4：生成总纲

```text
Agent(
  subagent_type: "novel-engine:outline-agent",
  prompt: "聚焦：总纲。设定={已加载的设定摘要}。目标规模={字数和章数}。请规划核心冲突、终极目标、分卷结构。"
)
```

确认后写入 `大纲/总纲.md`。

### Step 5：逐卷生成卷纲

对每卷：
1. 调用 Outline Agent 生成该卷的章级拆分和时间线
2. 展示章纲列表（一句话/章），确认
3. 写入 `大纲/第N卷-详细大纲.md` 和 `大纲/第N卷-时间线.md`

### Step 6：一致性校验

```text
Agent(
  subagent_type: "novel-engine:consistency-agent",
  prompt: "校验 大纲/ 下所有大纲文件与 设定集/ 的一致性。检查角色能力、世界规则、时间线是否矛盾。返回 issues 清单。"
)
```

### Step 7：更新状态

```bash
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" preflight
```

## 增量模式

如果项目已有大纲文件，大纲文件存在时进入增量模式：
- `/novel-outline 3` — 只规划/修改第 3 卷
- `/novel-outline --replan 2` — 重新规划第 2 卷（原文件备份到 .novel/backups/）
