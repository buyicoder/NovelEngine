---
name: novel-track
description: 故事演化追踪系统 — 伏笔生命周期、人物出场频率/设定演化、大纲偏离度检测。自动预警。
allowed-tools: Read Write Edit Grep Bash
argument-hint: "[foreshadowing|characters|outline|all]"
---

# /novel-track — 故事演化追踪

## 目标

追踪写作过程中故事世界的动态变化，在关键问题时主动预警：

| 追踪维度 | 追踪内容 | 预警条件 |
|----------|----------|----------|
| **伏笔** | 埋设→推进→回收全生命周期 | 逾期未回收、长期无推进 |
| **人物** | 每章出场记录、设定变更历史 | 超 N 章未出场、出场过密 |
| **大纲** | 计划章纲 vs 实际内容 | 偏离度超过阈值 |

## 使用方式

```bash
/novel-track                   # 全维度报告
/novel-track foreshadowing     # 只看伏笔
/novel-track characters        # 只看人物
/novel-track outline           # 只看大纲偏离
```

## 流程

### Step 1：加载追踪数据

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"

python -X utf8 "${SCRIPTS_DIR}/webnovel.py" \
  --project-root "${WORKSPACE_ROOT}" track
```

### Step 2：分析并展示

CLI 输出已包含完整报告。Skill 进行二次解读：

1. 标注 P0（紧急修复）、P1（尽快处理）、P2（建议关注）
2. 对每个预警给出具体行动建议
3. 如果健康度为 "good"，简单告知即可

### Step 3：互动操作（可选）

用户可以针对预警进行操作：

```
/novel-track foreshadowing resolve --id fs_003 --chapter 45
/novel-track characters evolve --name 萧炎 --chapter 45 --change "获得新能力" --reason "服用丹药"
/novel-track outline update --chapter 45 --actual "实际剧情描述"
```

## 伏笔操作

```bash
# 埋设伏笔
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action foreshadowing --plant --id fs_001 --name "神秘戒指" --desc "主角在拍卖会获得一枚神秘戒指" \
  --planted 10 --due 50 --tags "宝物,主线"

# 推进伏笔
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action foreshadowing --advance fs_001 --chapter 25 --note "戒指开始发光"

# 回收伏笔
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action foreshadowing --resolve fs_001 --chapter 50 --note "揭示戒指内有远古灵魂"
```

## 人物操作

```bash
# 记录出场
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action character --appear --name 萧炎 --chapter 45

# 记录设定演化
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action character --evolve --name 萧炎 --chapter 45 \
  --change "性格从急躁变得沉稳" --reason "经历宗门大比失利后反思"
```

## 大纲偏离操作

```bash
# 登记计划章纲
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action outline --plan --chapter_num 45 --summary "萧炎在炼药师大会上夺冠"

# 登记实际内容
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" track \
  --action outline --actual --chapter_num 45 \
  --summary "萧炎在炼药师大会上获得第三名" --deviation major --reason "读者反馈夺冠太套路"
```

## 预警级别

| 级别 | 条件 | 建议 |
|------|------|------|
| P0 | 伏笔逾期 30+ 章 | 立即决定：回收 or 废弃 |
| P1 | 角色缺席 20+ 章、大纲重大偏离 | 下 5 章内处理 |
| P2 | 角色出场过密、大纲轻微偏离 | 关注，择机调整 |
