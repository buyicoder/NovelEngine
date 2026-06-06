---
name: novel-generate
description: 白话剧情生成——基于章纲生成极简口语化剧情复述。每章2-5句话，不写文笔、场景、对话、心理。
allowed-tools: Read Write Edit Grep Bash Agent
argument-hint: "[章节号或范围]"
---

# /novel-generate — 白话剧情生成

## 目标

将章纲（一句话核心事件）展开为极简白话剧情。每章 2-5 句话，~100-300 字，口语化复述核心事件链。不写场景、对话、心理描写、修辞——文学创作留给作者。

## 示例

```
章纲：「萧炎得知炼药师大会，开始准备」

白话剧情：
药老告诉萧炎明天就是炼药师大会。萧炎虽然紧张但还是接下了。
他回房间练习新丹方，一开始连炸两炉，后来慢慢找到了感觉，
终于在第三次成功了。
```

## 流程

### Step 1：预检与加载

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" preflight
```

### Step 2：收集上下文

对要生成的章节 N，读取：
- `大纲/第X卷-详细大纲.md` — 获取该章的章纲（一句话核心事件）
- 前 3 章的白话剧情（`正文/白话剧情/第{N-3}章-白话剧情.md` 等）— 保持叙事衔接
- 该章涉及的角色的设定卡（从设定集/）— 确保行为符合人设
- 该卷的活跃伏笔清单 — 确保伏笔推进

### Step 3：生成白话剧情

直接由 Claude 推理生成（不需要调用子 Agent）：

1. 基于章纲的核心事件，推演事件链的因果逻辑
2. 用口语化的方式复述事件流程
3. 确保涉及角色的行为符合其设定
4. 确保与前一章的白话剧情内容衔接
5. 如果章纲涉及伏笔，在白话剧情中体现

约束：
- 每章 2-5 句话，100-300 字
- 只用口语大白话，不用任何文学修辞
- 不写对话（如必须提及对话内容，用间接引语："A告诉B..."）
- 不写场景描写、心理活动、外貌描写
- 不引入章纲之外的剧情

### Step 4：一致性校验

```text
Agent(
  subagent_type: "novel-engine:consistency-agent",
  prompt: "单章校验：检查 正文/白话剧情/第{N}章-白话剧情.md 是否违反 设定集/ 中的约束。重点检查：角色行为是否越级、世界规则是否被违反、时间线是否矛盾。"
)
```

如果发现 P0 问题，自动修正后重新校验。P1/P2 问题标注在文件顶部供作者参阅。

### Step 5：写入文件

```bash
cat > "${WORKSPACE_ROOT}/正文/白话剧情/第$(printf '%04d' {N})章-白话剧情.md" << 'EOF'
---
chapter: {N}
outline: "{章纲原文}"
generated_at: "{timestamp}"
consistency: "{pass|warning|block}"
---
{白话剧情内容}
EOF
```

### Step 6：更新项目状态

记录已生成的章节号到 state.json 的 `generated_chapters` 字段。

## 批量生成

```bash
/novel-generate 1-10    # 连续生成第 1-10 章的白话剧情
```

每章生成后做一致性校验，校验通过再继续下一章。不通过则暂停并报告。
