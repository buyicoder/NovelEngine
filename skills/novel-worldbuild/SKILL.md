---
name: novel-worldbuild
description: 题材自适应世界观搭建。根据题材自动加载不同的聚焦维度——不对女频问力量体系，不对悬疑问经济体系。
allowed-tools: Read Write Edit Grep Bash Agent AskUserQuestion
argument-hint: "[子系统名称或'all']"
---

# /novel-worldbuild — 题材自适应世界观搭建

## 核心机制

**不同题材聚焦不同维度。** 系统根据题材从 `references/genre-dimensions.json` 加载维度映射，覆盖全部 37 个题材。只问你该题材真正需要的问题。

| 题材类型 | 核心聚焦 | 直接跳过 |
|----------|----------|----------|
| 修仙/高武/系统流 | 力量体系、势力格局、资源体系 | — |
| 女频/言情类 | 人物关系、关系变化时间线 | 力量体系 |
| 悬疑/规则怪谈 | 线索链、世界规则、人物动机 | 经济体系 |
| 都市现实类 | 社会规则、人物关系、经济状况 | 力量体系 |
| 种田/经营类 | 资源体系、经济体系、时间线 | 力量体系 |
| 科幻/末世 | 科技/末世规则、资源、势力 | — |

完整维度映射见 `references/genre-dimensions.json`。

## 流程

### Step 1：预检与选题材

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
python -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/webnovel.py" --project-root "${WORKSPACE_ROOT}" preflight
```

读取 `.novel/state.json` 获取当前题材，加载 `${CLAUDE_PLUGIN_ROOT}/references/genre-dimensions.json` 获取该题材的维度映射。打印：

```
题材「修仙」将聚焦：
  必答: 力量体系、势力格局、资源体系
  建议: 人物关系、世界规则
  可选: 经济体系、时间线
```

### Step 2：搭必答维度 (P1)

```text
Agent(
  subagent_type: "novel-engine:worldbuilding-agent",
  prompt: "题材={genre}, 当前维度={dimension_name}, priority=1, focus={该维度的focus说明}, 已有设定={摘要}"
)
```

每个 P1 维度确认后写入对应设定文件。

### Step 3：搭建议维度 (P2)

先问作者是否需要。需要则搭，跳过则标记 skipped。

### Step 4：可选维度 (P3)

不主动问，作者提了再展开。

### Step 5：跳过维度 (P0)

直接标记 skipped，不占用交互时间。

### Step 6：一致性校验

```text
Agent(subagent_type: "novel-engine:consistency-agent", prompt: "...")
```

## 单独搭建

```bash
/novel-worldbuild characters  # 只搭人物关系（按题材的聚焦方式）
```

## 复合题材

A+B 复合题材取两套维度的并集，priority 取较高值。
