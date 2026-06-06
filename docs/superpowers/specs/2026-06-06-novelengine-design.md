# NovelEngine 网文辅助AI系统 — 设计方案

## 概述

NovelEngine 是一个基于 Claude Code 插件的网文创作辅助系统。与 webnovel-writer 不同，它**不做 AI 直接写书**，而是聚焦于五个核心能力：拆书分析、世界观搭建、头脑风暴、剧情走向规划、白话剧情生成。

白话剧情生成是核心创新：AI 用极简口语复述章节核心事件链（每章 2-5 句话），不写场景、对话、心理描写，把文学创作留给作者。

---

## 技术选型

- **运行平台**：Claude Code Plugin
- **AI 推理**：Claude（通过 Skill + Agent prompt 驱动）
- **数据处理**：Python CLI（SQLite + JSON/Markdown 文件）
- **前端**：暂不需要，后续可选加只读 Dashboard

---

## 总体架构

```
┌─────────────────────────────────────────────────┐
│                  Claude Code                     │
├─────────────────────────────────────────────────┤
│  7 个 Skill 命令:                                │
│  deconstruct / worldbuild / brainstorm /         │
│  outline / generate / query / doctor             │
├─────────────────────────────────────────────────┤
│  5 个 Agent:                                     │
│  Deconstruction / Worldbuilding / Brainstorm /   │
│  Outline / Consistency                           │
├─────────────────────────────────────────────────┤
│  Python CLI (webnovel.py):                       │
│  项目管理 / 实体索引 / 关系图 / 模板库 / 归档     │
├─────────────────────────────────────────────────┤
│  项目文件 (每本书一个目录):                       │
│  设定集/  大纲/  拆书存档/  正文/白话剧情/  .novel/ │
└─────────────────────────────────────────────────┘
```

### 设计原则

1. **Agent 只做思考**：通过 prompt 驱动 Claude 推理，不直接写文件
2. **CLI 只做数据**：Python 脚本负责文件读写、数据库操作、格式校验
3. **Skill 做编排**：Slash Command 串起交互流程，协调 Agent 和 CLI
4. **Markdown 为主，SQLite 为辅**：设定用 Markdown（人可读），索引用 SQLite（可查询）

---

## Phase 1：地基（拆书分析 + 世界观搭建）

### 模块一：拆书分析 `/novel-deconstruct`

**Deconstruction Agent**（从 webnovel-writer deconstruction-agent 改造移植）

两种模式：
- **快速模式**：黄金三章拆解 → 钩子分析、爽点铺设、世界观铺设、章尾悬念评分
- **深度模式**：逐章情节点提取 → 聚合为剧情条/故事线 → 角色合并消歧 → 设定/金手指/关系模式抽象

核心约束：
- 只抽离"条件框架"（什么条件组合造成爽感），不复制原作事实
- 角色名、地名、金手指、具体情节不得进入输出
- 质量门控：coverage <85% 触发补充分析，overlap >35% 标记边界模糊

输出：
- 结构化 JSON：`拆书存档/<书名>/analysis.json`
- 包含：reader_promise、opening_hook_patterns、cool_point_loops、protagonist_patterns、antagonist_pressure_patterns、pacing_notes、borrowable_structures、differentiation_requirements、init_candidates
- 可读报告：`拆书存档/<书名>/报告.md`

附加能力：
- 跨书对比：`/novel-deconstruct --compare <书名A> <书名B>` 输出同类题材共性规律

### 模块二：世界观搭建 `/novel-worldbuild`

**Worldbuilding Agent**

五个子系统，交互式逐项搭建：

| 子系统 | 产出文件 | 内容 |
|--------|----------|------|
| 等级/力量体系 | `设定集/力量体系.md` | 境界层级、每级能力解锁、突破条件、战力换算 |
| 货币/经济体系 | `设定集/经济体系.md` | 货币层级、购买力锚定、资源稀缺度 |
| 势力格局 | `设定集/势力格局.md` | 宗门/家族/组织、势力间关系、压迫结构 |
| 人物关系 | `设定集/主角卡.md` `设定集/配角卡.md` 等 | 角色档案、关系图谱、动机模型 |
| 世界规则 | `设定集/世界观.md` | 地理、历史、特殊规则、限制与代价 |

交互流程：
1. 选题材（从 37 个题材模板中选择或自定义）
2. 逐子系统问答（每轮只问当前缺失的关键信息）
3. 生成设定文件
4. Consistency Agent 做冲突检测

**Consistency Agent**：跨设定文件校验冲突（如"力量体系说金丹期能活 500 岁，但人物设定说某角色 200 岁就老态龙钟"）。

---

## Phase 2：核心（剧情走向规划 + 白话剧情生成）

### 模块三：剧情走向规划 `/novel-outline`

**Outline Agent**

三层规划：
1. **总纲**：核心冲突、分卷结构、每卷目标 → `大纲/总纲.md`
2. **卷纲**：章级拆分、时间线、伏笔布局 → `大纲/第N卷-详细大纲.md`
3. **章纲**：每章一句话核心事件 → 包含在卷纲中

章纲粒度约定：每个章纲只写一句话，描述该章核心事件，不展开。

规划时自动注入：
- 相关角色设定（从设定集读取）
- 已有伏笔清单（需推进或回收）
- 节奏约束（主线/感情/世界观的比例建议）

### 模块四：白话剧情生成 `/novel-generate`

**核心创新模块**

Generate 过程（由 Skill 编排，Claude 直接推理）：
1. 读取该章章纲
2. 读取前 3 章白话剧情（上下文衔接）
3. 读取相关设定（角色、世界观、活跃伏笔）
4. 生成极简白话剧情（每章 2-5 句话，~100-300 字）
5. Consistency Agent 校验是否违反设定

示例：
```
章纲：「萧炎得知炼药师大会，开始准备」

白话剧情：
药老告诉萧炎明天就是炼药师大会。萧炎虽然紧张但还是接下了。
他回房间练习新丹方，一开始连炸两炉，后来慢慢找到了感觉，
终于在第三次成功了。
```

输出目录：`正文/白话剧情/第XXXX章-白话剧情.md`

校验点：
- 出场角色是否与章纲一致
- 行为是否违反已有设定（如越级使用能力）
- 伏笔推进是否与大纲对齐
- 前后章之间是否有逻辑断裂

---

## Phase 3：增强（头脑风暴引擎）

### 模块五：头脑风暴 `/novel-brainstorm`

**Brainstorm Agent**

四种发散模式：

| 模式 | 示例 | 输出 |
|------|------|------|
| 创意候选生成 | "金手指还可以怎么设计？" | 3-5 个差异化方案 |
| 反套路推演 | "这个桥段太老套了，怎么反着写？" | 反套路版本 + 预期效果 |
| 假设性推演 | "如果主角在炼药师大会上输了会怎样？" | 连锁反应推演 |
| 题材融合 | "修仙 + 悬疑可以怎么结合？" | 融合方案 + 冲突点 |

可在任意环节调用（世界观搭建时发散设定、规划时发散剧情方向、拆书时提出替代写法）。

---

## 辅助模块

### 综合查询 `/novel-query`

查询当前项目状态：角色详情、势力关系、伏笔清单、设定索引、章节规划。

### 项目体检 `/novel-doctor`

阶段感知检查：目录完整性、设定文件格式、实体索引健康、依赖项。

---

## Python CLI 设计

统一入口：`scripts/webnovel.py`

### 子命令

| 子命令 | 功能 |
|--------|------|
| `where` | 解析当前书项目根目录 |
| `preflight` | 项目健康检查（目录/文件/依赖） |
| `index` | 实体索引管理（角色/势力/地点/物品的 CRUD） |
| `relations` | 人物/势力关系图操作 |
| `templates` | 体系模板管理（等级/货币/力量体系） |
| `deconstruct` | 拆书存档的查询/导出/跨书对比 |
| `archive` | 项目归档与备份 |
| `doctor` | 诊断并输出修复建议 |

### 数据模块

```
scripts/
├── webnovel.py                   # CLI 入口
└── data_modules/
    ├── config.py                 # 配置管理
    ├── index_manager.py          # SQLite 实体索引
    ├── relation_graph.py         # 人物/势力关系图
    ├── consistency_checker.py    # 设定冲突检测
    ├── template_manager.py       # 体系模板库
    ├── deconstruct_store.py      # 拆书存档管理
    ├── project_phase.py          # 项目阶段感知
    ├── placeholder_scanner.py    # 占位符检测
    └── archive_manager.py        # 备份归档
```

---

## 项目目录结构（每本书）

```
book-project/
├── .novel/                       # 系统数据（不手动编辑）
│   ├── state.json                # 项目状态与元数据
│   ├── index.db                  # SQLite 实体索引
│   └── backups/                  # 自动备份
├── 设定集/                        # 世界观设定
│   ├── 世界观.md
│   ├── 力量体系.md
│   ├── 经济体系.md
│   ├── 势力格局.md
│   ├── 主角卡.md
│   ├── 配角卡.md
│   └── 反派设计.md
├── 大纲/                          # 剧情规划
│   ├── 总纲.md
│   ├── 第N卷-详细大纲.md
│   └── 第N卷-时间线.md
├── 正文/                          # 产出内容
│   └── 白话剧情/
│       └── 第XXXX章-白话剧情.md
└── 拆书存档/                      # 参考书拆解结果
    └── <书名>/
        ├── analysis.json
        └── 报告.md
```

---

## 插件结构

```
NovelEngine/
├── .claude-plugin/
│   └── plugin.json               # Claude Code 插件清单
├── skills/                        # Skill 命令定义
│   ├── novel-deconstruct/
│   │   └── SKILL.md
│   ├── novel-worldbuild/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── power-systems.md
│   │       ├── currency-systems.md
│   │       ├── faction-systems.md
│   │       ├── character-design.md
│   │       └── world-rules.md
│   ├── novel-brainstorm/
│   │   └── SKILL.md
│   ├── novel-outline/
│   │   └── SKILL.md
│   ├── novel-generate/
│   │   └── SKILL.md
│   ├── novel-query/
│   │   └── SKILL.md
│   └── novel-doctor/
│       └── SKILL.md
├── agents/                        # Agent 角色定义
│   ├── deconstruction-agent.md
│   ├── worldbuilding-agent.md
│   ├── brainstorm-agent.md
│   ├── outline-agent.md
│   └── consistency-agent.md
├── scripts/                       # Python CLI
│   ├── webnovel.py
│   └── data_modules/
│       └── ...
├── references/                    # 共享领域知识
│   ├── genre-profiles.md          # 37 题材配置
│   └── deconstruction-patterns/   # 拆书模式积累
├── templates/                     # 输出模板
│   ├── genres/                    # 37 题材模板
│   └── outputs/                   # 设定输出模板
├── requirements.txt
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-06-06-novelengine-design.md
```

---

## 数据流总览

```
拆书分析 ──→ 拆书存档（知识库，可选参考）
                  │
世界观搭建 ──→ 设定集/
                  │
                  ├──→ 剧情走向规划 → 大纲/
                  │                        │
     头脑风暴 ←──→│                        │
                  │                        │
                  └──→ 白话剧情生成 ←──→ 正文/白话剧情/
                           ↑
                    Consistency Agent
                    （校验不违反设定）
```

**各模块间的输入输出关系：**
- 拆书 → 世界观：拆书发现的模式可启发世界观设计（不直接写入）
- 世界观 → 剧情规划：设定约束剧情走向（角色动机、势力关系决定冲突方向）
- 剧情规划 → 白话生成：章纲作为白话生成的输入
- 头脑风暴 ↔ 全部：任意环节可按需调用发散思考
- Consistency Agent：横跨世界观和生成环节做校验

---

## 从 webnovel-writer 复用清单

| 来源 | 复用方式 | 用途 |
|------|----------|------|
| deconstruction-agent.md | 改造移植 | 拆书核心引擎 |
| 37 个 genre 模板 | 直接复制 | 题材知识库 |
| worldbuilding references | 改造增强 | 力量/势力/角色/规则设计 |
| init skill 交互流程 | 参考设计 | 分阶段问答模式 |
| index_manager + SQLite schema | 裁剪移植 | 实体索引管理 |
| genre-profiles / taxonomy | 直接移植 | 题材映射与配置 |
| output templates | 改造 | 设定文件输出格式 |
| preflight / doctor | 裁剪移植 | 健康检查 |
| anti-trope references | 直接复用 | 反套路知识库 |

## 明确不做的

- ❌ AI 直接写正文（文笔、对话、场景、心理描写由作者完成）
- ❌ 章节审查/质量打分（没有正文产出，不需要审查）
- ❌ Chapter Commit 链和投影系统（没有每章的事实沉淀需求）
- ❌ Strand Weave 节奏追踪（太耦合写章流程）
- ❌ Dashboard 前端（Phase 1-3 先不做，后续可选）
