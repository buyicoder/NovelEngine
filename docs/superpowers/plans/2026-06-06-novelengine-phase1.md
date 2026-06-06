# NovelEngine Phase 1 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 NovelEngine 插件骨架，移植 webnovel-writer 领域知识资产，实现拆书分析和世界观搭建两个核心模块。

**Architecture:** Claude Code Plugin 架构 — 7 个目录（skills/ agents/ scripts/ references/ templates/ docs/）、Python CLI 入口、5 个 Agent 定义、7 个 Skill 定义。Phase 1 先实现 deconstruct/worldbuild/query/doctor 四个 Skill 和 Deconstruction/Worldbuilding/Consistency 三个 Agent。

**Tech Stack:** Claude Code Plugin, Python 3.10+, SQLite, Markdown

---

## 文件结构规划

```
NovelEngine/
├── .claude-plugin/
│   └── plugin.json                          # 插件清单
├── .gitignore
├── requirements.txt
├── claude-pre.bat                           # 已有，不改
├── skills/
│   ├── novel-deconstruct/
│   │   └── SKILL.md                         # 拆书 Skill 定义
│   ├── novel-worldbuild/
│   │   ├── SKILL.md                         # 世界观搭建 Skill 定义
│   │   └── references/
│   │       ├── power-systems.md             # 力量体系设计指南 [移植]
│   │       ├── currency-systems.md          # 货币经济体系指南 [新写]
│   │       ├── faction-systems.md           # 势力格局设计指南 [移植]
│   │       ├── character-design.md          # 人物设计指南 [移植]
│   │       ├── world-rules.md               # 世界规则指南 [移植]
│   │       └── setting-consistency.md       # 设定一致性检查 [移植]
│   ├── novel-query/
│   │   └── SKILL.md                         # 综合查询 Skill 定义
│   └── novel-doctor/
│       └── SKILL.md                         # 项目体检 Skill 定义
├── agents/
│   ├── deconstruction-agent.md              # 拆书 Agent [移植改造]
│   ├── worldbuilding-agent.md               # 世界观搭建 Agent [新写]
│   └── consistency-agent.md                 # 一致性校验 Agent [新写]
├── scripts/
│   ├── webnovel.py                          # CLI 统一入口
│   ├── project_locator.py                   # 项目根定位 [移植裁剪]
│   ├── init_project.py                      # 新项目初始化
│   └── data_modules/
│       ├── __init__.py
│       ├── config.py                        # 配置管理
│       ├── cli_args.py                      # CLI 参数解析 [移植裁剪]
│       ├── cli_output.py                    # CLI 输出格式化 [移植裁剪]
│       ├── index_manager.py                 # SQLite 实体索引 [移植裁剪]
│       ├── relation_graph.py                # 关系图管理
│       ├── consistency_checker.py           # 设定冲突检测
│       ├── template_manager.py              # 模板管理
│       ├── deconstruct_store.py             # 拆书存档管理
│       ├── project_phase.py                 # 项目阶段感知 [移植裁剪]
│       ├── placeholder_scanner.py           # 占位符检测 [移植裁剪]
│       ├── archive_manager.py               # 备份归档
│       └── doctor.py                        # 诊断模块 [移植裁剪]
├── references/
│   ├── genre-profiles.md                    # 37 题材配置 [移植]
│   ├── creative-combination.md              # 复合题材融合 [移植]
│   ├── creativity-constraints.md            # 创意约束 [移植]
│   ├── anti-trope-xianxia.md                # 反套路-修仙 [移植]
│   ├── anti-trope-urban.md                  # 反套路-都市 [移植]
│   ├── anti-trope-mystery.md                # 反套路-悬疑 [移植]
│   ├── anti-trope-game.md                   # 反套路-游戏 [移植]
│   ├── core-constraints.md                  # 核心约束 [移植]
│   ├── deconstruction-patterns/
│   │   └── .gitkeep                         # 拆书模式积累目录
│   └── csv/                                 # CSV 参考数据 [移植]
│       ├── 命名规则.csv
│       ├── 爽点与节奏.csv
│       ├── 金手指与设定.csv
│       ├── 题材与调性推理.csv
│       └── ...其他 CSV
├── templates/
│   ├── genres/                              # 37 题材模板 [移植]
│   │   ├── 修仙.md
│   │   ├── 系统流.md
│   │   └── ... (35 more)
│   └── outputs/                             # 输出模板
│       ├── 设定集-世界观.md                  # [移植]
│       ├── 设定集-力量体系.md                # [移植]
│       ├── 设定集-主角卡.md                  # [移植]
│       ├── 设定集-主角组.md                  # [移植]
│       ├── 设定集-反派设计.md                # [移植]
│       ├── 设定集-经济体系.md                # [新写]
│       ├── 设定集-势力格局.md                # [新写]
│       ├── 大纲-总纲.md                      # [移植]
│       ├── 大纲-卷时间线.md                  # [移植]
│       ├── 大纲-卷节拍表.md                  # [移植]
│       ├── 白话剧情-章节模板.md              # [新写]
│       └── 复合题材-融合逻辑.md              # [移植]
├── hooks/
│   └── session_start.py                     # 会话启动钩子
├── tests/
│   ├── test_webnovel_cli.py
│   ├── test_project_locator.py
│   ├── test_init_project.py
│   ├── test_index_manager.py
│   ├── test_relation_graph.py
│   └── test_consistency_checker.py
└── docs/
    └── superpowers/
        ├── specs/
        │   └── 2026-06-06-novelengine-design.md
        └── plans/
            └── 2026-06-06-novelengine-phase1.md
```

**职责说明：**
- `skills/` — Skill prompt 定义，每个文件定义一个 Claude Code Slash Command 的行为
- `agents/` — Agent 角色 prompt，被 Skill 通过 Agent 工具调用
- `scripts/` — Python 可执行代码，CLI 入口和数据管理
- `references/` — 只读领域知识，供 Skill/Agent 在推理时加载
- `templates/` — 输出模板，供 init/new 命令复制到新书项目中
- `hooks/` — Claude Code 生命周期钩子

---

### Task 1: 创建项目骨架

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `hooks/session_start.py`
- Create: 各目录的 `.gitkeep`

- [ ] **Step 1: 创建目录结构**

```bash
cd "D:/占占tools/NovelEngine"
mkdir -p .claude-plugin
mkdir -p skills/novel-deconstruct
mkdir -p skills/novel-worldbuild/references
mkdir -p skills/novel-query
mkdir -p skills/novel-doctor
mkdir -p agents
mkdir -p scripts/data_modules
mkdir -p references/csv
mkdir -p references/deconstruction-patterns
mkdir -p templates/genres
mkdir -p templates/outputs
mkdir -p hooks
mkdir -p tests
```

- [ ] **Step 2: 写入 plugin.json**

```json
{
  "name": "novel-engine",
  "version": "0.1.0",
  "description": "网文创作辅助系统 — 拆书分析、世界观搭建、头脑风暴、剧情规划、白话剧情生成",
  "author": {
    "name": "NovelEngine"
  },
  "homepage": "",
  "repository": "",
  "license": "MIT",
  "keywords": [
    "webnovel",
    "claude-code",
    "worldbuilding",
    "deconstruction",
    "story-planning"
  ]
}
```

- [ ] **Step 3: 写入 .gitignore**

```gitignore
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
.env
.novel/
```

- [ ] **Step 4: 写入 requirements.txt**

```text
# NovelEngine Python dependencies
# Core
pydantic>=2.0

# No embedding/rerank deps needed in Phase 1
# RAG support will be added in later phases
```

- [ ] **Step 5: 写入 hooks/session_start.py**

```python
"""Session start hook for NovelEngine plugin."""
import os
import sys


def main():
    """Initialize NovelEngine environment on session start."""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        return

    scripts_dir = os.path.join(plugin_root, "scripts")
    if os.path.isdir(scripts_dir) and scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    print(f"[NovelEngine] Plugin root: {plugin_root}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: 验证目录结构**

```bash
find "D:/占占tools/NovelEngine" -not -path '*/.git/*' -not -path '*/.claude/*' -type d | sort
```

期望：所有上述目录存在。

- [ ] **Step 7: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git init
git add -A
git commit -m "feat: create project skeleton with plugin manifest and directory structure"
```

---

### Task 2: 从 webnovel-writer 移植题材模板 (37 个)

**Files:**
- Create: `templates/genres/*.md` (37 files)

- [ ] **Step 1: 复制题材模板**

```bash
cp "/tmp/webnovel-writer/webnovel-writer/templates/genres/"*.md "D:/占占tools/NovelEngine/templates/genres/"
```

- [ ] **Step 2: 验证文件数量**

```bash
ls "D:/占占tools/NovelEngine/templates/genres/" | wc -l
```

期望：37

- [ ] **Step 3: 检查文件不为空**

```bash
for f in "D:/占占tools/NovelEngine/templates/genres/"*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -lt 5 ]; then
    echo "WARNING: $f has only $lines lines"
  fi
done
echo "Check complete"
```

- [ ] **Step 4: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add templates/genres/
git commit -m "feat: transplant 37 genre templates from webnovel-writer"
```

---

### Task 3: 从 webnovel-writer 移植世界观设计 references

**Files:**
- Create: `skills/novel-worldbuild/references/power-systems.md`
- Create: `skills/novel-worldbuild/references/faction-systems.md`
- Create: `skills/novel-worldbuild/references/character-design.md`
- Create: `skills/novel-worldbuild/references/world-rules.md`
- Create: `skills/novel-worldbuild/references/setting-consistency.md`

- [ ] **Step 1: 复制世界观 references**

```bash
cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/worldbuilding/power-systems.md" \
   "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/power-systems.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/worldbuilding/faction-systems.md" \
   "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/faction-systems.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/worldbuilding/character-design.md" \
   "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/character-design.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/worldbuilding/world-rules.md" \
   "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/world-rules.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/worldbuilding/setting-consistency.md" \
   "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/setting-consistency.md"
```

- [ ] **Step 2: 验证文件**

```bash
ls -la "D:/占占tools/NovelEngine/skills/novel-worldbuild/references/"
```

- [ ] **Step 3: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add skills/novel-worldbuild/references/
git commit -m "feat: transplant worldbuilding references from webnovel-writer"
```

---

### Task 4: 从 webnovel-writer 移植创意与反套路 references

**Files:**
- Create: `references/genre-profiles.md`
- Create: `references/creative-combination.md`
- Create: `references/creativity-constraints.md`
- Create: `references/anti-trope-xianxia.md`
- Create: `references/anti-trope-urban.md`
- Create: `references/anti-trope-mystery.md`
- Create: `references/anti-trope-game.md`
- Create: `references/core-constraints.md`

- [ ] **Step 1: 复制 references**

```bash
cp "/tmp/webnovel-writer/webnovel-writer/references/genre-profiles.md" \
   "D:/占占tools/NovelEngine/references/genre-profiles.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/creative-combination.md" \
   "D:/占占tools/NovelEngine/references/creative-combination.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/creativity-constraints.md" \
   "D:/占占tools/NovelEngine/references/creativity-constraints.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/anti-trope-xianxia.md" \
   "D:/占占tools/NovelEngine/references/anti-trope-xianxia.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/anti-trope-urban.md" \
   "D:/占占tools/NovelEngine/references/anti-trope-urban.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/anti-trope-rules-mystery.md" \
   "D:/占占tools/NovelEngine/references/anti-trope-mystery.md"

cp "/tmp/webnovel-writer/webnovel-writer/skills/webnovel-init/references/creativity/anti-trope-game.md" \
   "D:/占占tools/NovelEngine/references/anti-trope-game.md"

cp "/tmp/webnovel-writer/webnovel-writer/references/shared/core-constraints.md" \
   "D:/占占tools/NovelEngine/references/core-constraints.md"
```

- [ ] **Step 2: 复制 CSV 参考数据**

```bash
cp "/tmp/webnovel-writer/webnovel-writer/references/csv/"*.csv "D:/占占tools/NovelEngine/references/csv/" 2>/dev/null || true
```

- [ ] **Step 3: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add references/
git commit -m "feat: transplant creativity references and CSV data from webnovel-writer"
```

---

### Task 5: 移植输出模板

**Files:**
- Create: `templates/outputs/*.md` (12 files)

- [ ] **Step 1: 复制输出模板**

```bash
cp "/tmp/webnovel-writer/webnovel-writer/templates/output/设定集-世界观.md" \
   "D:/占占tools/NovelEngine/templates/outputs/设定集-世界观.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/设定集-力量体系.md" \
   "D:/占占tools/NovelEngine/templates/outputs/设定集-力量体系.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/设定集-主角卡.md" \
   "D:/占占tools/NovelEngine/templates/outputs/设定集-主角卡.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/设定集-主角组.md" \
   "D:/占占tools/NovelEngine/templates/outputs/设定集-主角组.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/设定集-反派设计.md" \
   "D:/占占tools/NovelEngine/templates/outputs/设定集-反派设计.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/大纲-总纲.md" \
   "D:/占占tools/NovelEngine/templates/outputs/大纲-总纲.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/大纲-卷时间线.md" \
   "D:/占占tools/NovelEngine/templates/outputs/大纲-卷时间线.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/大纲-卷节拍表.md" \
   "D:/占占tools/NovelEngine/templates/outputs/大纲-卷节拍表.md"

cp "/tmp/webnovel-writer/webnovel-writer/templates/output/复合题材-融合逻辑.md" \
   "D:/占占tools/NovelEngine/templates/outputs/复合题材-融合逻辑.md"
```

- [ ] **Step 2: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add templates/outputs/
git commit -m "feat: transplant output templates from webnovel-writer"
```

---

### Task 6: 编写 Python CLI 基础框架

**Files:**
- Create: `scripts/webnovel.py`
- Create: `scripts/data_modules/__init__.py`
- Create: `scripts/data_modules/config.py`
- Create: `scripts/data_modules/cli_args.py`
- Create: `scripts/data_modules/cli_output.py`

- [ ] **Step 1: 编写 CLI 入口 `scripts/webnovel.py`**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NovelEngine CLI 统一入口。

Usage:
    python -X utf8 webnovel.py --project-root <path> <subcommand> [args]
"""

import sys
import os


def main():
    """CLI 主入口，路由到各子命令处理模块。"""
    # Ensure scripts dir on path
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from data_modules.cli_args import parse_args
    from data_modules.cli_output import print_banner

    args = parse_args()
    print_banner(args)

    # Route to subcommand
    subcommand = args.get("subcommand", "help")
    routes = {
        "where": _cmd_where,
        "preflight": _cmd_preflight,
        "index": _cmd_index,
        "relations": _cmd_relations,
        "templates": _cmd_templates,
        "deconstruct": _cmd_deconstruct,
        "archive": _cmd_archive,
        "doctor": _cmd_doctor,
        "init": _cmd_init,
        "help": _cmd_help,
    }

    handler = routes.get(subcommand, _cmd_help)
    handler(args)


def _cmd_where(args):
    """Print resolved project root."""
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    print(root)


def _cmd_preflight(args):
    """Run project health preflight checks."""
    from data_modules.config import resolve_project_root, validate_project_structure
    root = resolve_project_root(args.get("project_root"))
    issues = validate_project_structure(root)
    if issues:
        for issue in issues:
            print(f"[WARN] {issue}")
        sys.exit(1)
    print(f"[OK] Project at {root} passes preflight.")


def _cmd_index(args):
    """Entity index management stub."""
    print("index subcommand — not yet implemented in Phase 1 core.")


def _cmd_relations(args):
    """Relation graph management stub."""
    print("relations subcommand — not yet implemented in Phase 1 core.")


def _cmd_templates(args):
    """Template management stub."""
    print("templates subcommand — not yet implemented in Phase 1 core.")


def _cmd_deconstruct(args):
    """Deconstruction archive management stub."""
    print("deconstruct subcommand — not yet implemented in Phase 1 core.")


def _cmd_archive(args):
    """Archive management stub."""
    print("archive subcommand — not yet implemented in Phase 1 core.")


def _cmd_doctor(args):
    """Project doctor stub."""
    from data_modules.doctor import run_doctor
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    report = run_doctor(root)
    print(report)


def _cmd_init(args):
    """Initialize a new book project."""
    from init_project import init_book_project
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    init_book_project(root, args.get("name", ""), args.get("genre", ""))


def _cmd_help(args):
    """Print help."""
    print(__doc__)
    print("Available subcommands:")
    print("  where        Print resolved project root")
    print("  preflight    Run project health preflight")
    print("  doctor       Diagnose project issues")
    print("  init         Initialize new book project")
    print("  index        Entity index management")
    print("  relations    Relation graph management")
    print("  templates    Template management")
    print("  deconstruct  Deconstruction archive management")
    print("  archive      Project backup and archive")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 编写 `scripts/data_modules/__init__.py`**

```python
# NovelEngine data modules
```

- [ ] **Step 3: 编写 `scripts/data_modules/config.py`**

```python
"""Configuration management for NovelEngine."""

import os
import json

# Book project required directories
REQUIRED_DIRS = ["设定集", "大纲", "正文/白话剧情", "拆书存档"]
REQUIRED_SYSTEM_DIRS = [".novel"]
REQUIRED_SYSTEM_FILES = [".novel/state.json"]


def resolve_project_root(explicit_root=None):
    """Resolve the book project root directory.

    Priority:
    1. Explicit --project-root argument
    2. Current working directory (if it looks like a book project)
    3. Walk up from CWD to find a .novel/ directory
    """
    if explicit_root and os.path.isdir(explicit_root):
        return os.path.abspath(explicit_root)

    cwd = os.getcwd()
    # Walk up from CWD
    path = cwd
    while True:
        if os.path.isdir(os.path.join(path, ".novel")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent

    return cwd


def load_project_state(project_root):
    """Load .novel/state.json, return empty dict if not found."""
    state_path = os.path.join(project_root, ".novel", "state.json")
    if not os.path.isfile(state_path):
        return {}
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project_state(project_root, state):
    """Save .novel/state.json."""
    state_dir = os.path.join(project_root, ".novel")
    os.makedirs(state_dir, exist_ok=True)
    state_path = os.path.join(state_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def validate_project_structure(project_root):
    """Check project directory structure. Returns list of issue strings."""
    issues = []
    for d in REQUIRED_DIRS + REQUIRED_SYSTEM_DIRS:
        full = os.path.join(project_root, d)
        if not os.path.isdir(full):
            issues.append(f"Missing directory: {d}")
    for f in REQUIRED_SYSTEM_FILES:
        full = os.path.join(project_root, f)
        if not os.path.isfile(full):
            issues.append(f"Missing file: {f}")
    return issues


def get_project_phase(project_root):
    """Determine project phase from state.json."""
    state = load_project_state(project_root)
    return state.get("phase", "unknown")
```

- [ ] **Step 4: 编写 `scripts/data_modules/cli_args.py`**

```python
"""CLI argument parsing for webnovel.py."""

import sys


def parse_args(argv=None):
    """Parse CLI arguments. Returns a dict.

    Simple arg parser — no external deps needed for Phase 1.
    Format: python webnovel.py --project-root <path> <subcommand> [--key value ...]
    """
    if argv is None:
        argv = sys.argv[1:]

    args = {"project_root": None, "subcommand": "help", "extra": {}}
    i = 0
    positional = []

    while i < len(argv):
        arg = argv[i]
        if arg == "--project-root" and i + 1 < len(argv):
            i += 1
            args["project_root"] = argv[i]
        elif arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                i += 1
                args["extra"][key] = argv[i]
            else:
                args["extra"][key] = True
        else:
            positional.append(arg)
        i += 1

    if positional:
        args["subcommand"] = positional[0]
        args["extra"]["_positional"] = positional[1:]

    return args
```

- [ ] **Step 5: 编写 `scripts/data_modules/cli_output.py`**

```python
"""CLI output formatting utilities."""

import sys


def print_banner(args):
    """Print a startup banner with parsed args summary."""
    subcommand = args.get("subcommand", "help")
    project_root = args.get("project_root") or "(auto-detect)"
    print(f"[NovelEngine] subcommand={subcommand} root={project_root}", file=sys.stderr)


def format_success(msg):
    """Format a success message."""
    return f"[OK] {msg}"


def format_warning(msg):
    """Format a warning message."""
    return f"[WARN] {msg}"


def format_error(msg):
    """Format an error message."""
    return f"[ERROR] {msg}"


def format_table(headers, rows):
    """Format data as a simple aligned table."""
    if not rows:
        return ""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    lines = []
    # Header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    # Rows
    for row in rows:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return "\n".join(lines)
```

- [ ] **Step 6: 编写测试 `tests/test_webnovel_cli.py`**

```python
"""Tests for CLI argument parsing and entry point."""

import sys
import os
import pytest

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.cli_args import parse_args
from data_modules.config import resolve_project_root, validate_project_structure


class TestCliArgs:
    def test_parse_no_args(self):
        args = parse_args([])
        assert args["subcommand"] == "help"
        assert args["project_root"] is None

    def test_parse_subcommand_only(self):
        args = parse_args(["where"])
        assert args["subcommand"] == "where"

    def test_parse_project_root(self):
        args = parse_args(["--project-root", "/tmp/test", "preflight"])
        assert args["subcommand"] == "preflight"
        assert args["project_root"] == "/tmp/test"

    def test_parse_extra_flags(self):
        args = parse_args(["--project-root", "/tmp", "doctor", "--format", "text"])
        assert args["subcommand"] == "doctor"
        assert args["extra"]["format"] == "text"

    def test_parse_positional_args(self):
        args = parse_args(["index", "get-core-entities"])
        assert args["subcommand"] == "index"
        assert args["extra"]["_positional"] == ["get-core-entities"]


class TestConfig:
    def test_resolve_explicit_root(self):
        result = resolve_project_root("/tmp")
        assert result == os.path.abspath("/tmp")

    def test_resolve_nonexistent_returns_cwd(self, monkeypatch):
        monkeypatch.setattr(os, "getcwd", lambda: "/tmp")
        result = resolve_project_root("/nonexistent/path/xyz")
        # Falls back to cwd since explicit root doesn't exist
        assert os.path.isabs(result)

    def test_validate_missing_dirs(self, tmp_path):
        issues = validate_project_structure(str(tmp_path))
        assert len(issues) > 0  # Missing all required dirs
```

- [ ] **Step 7: 运行测试**

```bash
cd "D:/占占tools/NovelEngine"
python -m pytest tests/test_webnovel_cli.py -v
```

期望：全部 PASS（test_validate_missing_dirs 会 PASS 因为 tmp_path 确实缺少目录）

- [ ] **Step 8: 验证 CLI 可执行**

```bash
cd "D:/占占tools/NovelEngine"
python -X utf8 scripts/webnovel.py help
```

期望：打印帮助信息，无错误

- [ ] **Step 9: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add scripts/ tests/
git commit -m "feat: add Python CLI skeleton with arg parsing and config modules"
```

---

### Task 7: 编写 init_project.py 新书初始化

**Files:**
- Create: `scripts/init_project.py`

- [ ] **Step 1: 编写 `scripts/init_project.py`**

```python
"""Initialize a new book project directory with standard structure."""

import os
import json
import shutil
from datetime import datetime


# Directories to create in a new book project
BOOK_DIRS = [
    "设定集",
    "大纲",
    "正文/白话剧情",
    "拆书存档",
    ".novel/backups",
    ".novel/tmp",
]

# Default state.json template
DEFAULT_STATE = {
    "project_info": {
        "name": "",
        "genre": "",
        "created_at": "",
        "phase": "init",
    },
    "settings": {
        "世界观": {"status": "pending", "file": "设定集/世界观.md"},
        "力量体系": {"status": "pending", "file": "设定集/力量体系.md"},
        "经济体系": {"status": "pending", "file": "设定集/经济体系.md"},
        "势力格局": {"status": "pending", "file": "设定集/势力格局.md"},
        "主角卡": {"status": "pending", "file": "设定集/主角卡.md"},
        "配角卡": {"status": "pending", "file": "设定集/配角卡.md"},
        "反派设计": {"status": "pending", "file": "设定集/反派设计.md"},
    },
    "outline": {
        "总纲": {"status": "pending", "file": "大纲/总纲.md"},
        "volumes": [],
    },
    "deconstruction_archive": [],
    "generated_chapters": [],
    "entity_index": {"last_synced": None},
    "relation_graph": {"last_updated": None},
}


def init_book_project(project_root, name="", genre=""):
    """Create a new book project at project_root.

    Args:
        project_root: Absolute path to the book project directory.
        name: Working title of the book.
        genre: Primary genre.

    Raises:
        FileExistsError: If .novel/state.json already exists.
    """
    state_path = os.path.join(project_root, ".novel", "state.json")
    if os.path.isfile(state_path):
        raise FileExistsError(f"Project already initialized: {state_path} exists")

    # Create directories
    for d in BOOK_DIRS:
        full = os.path.join(project_root, d)
        os.makedirs(full, exist_ok=True)

    # Create state.json
    state = dict(DEFAULT_STATE)  # shallow copy
    state["project_info"]["name"] = name
    state["project_info"]["genre"] = genre
    state["project_info"]["created_at"] = datetime.now().isoformat()

    state_dir = os.path.join(project_root, ".novel")
    os.makedirs(state_dir, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # Copy output templates as starter files if templates dir exists
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    templates_src = os.path.join(plugin_root, "templates", "outputs")
    if os.path.isdir(templates_src):
        _copy_template_if_exists(templates_src, "设定集-世界观.md",
                                 os.path.join(project_root, "设定集", "世界观.md"))
        _copy_template_if_exists(templates_src, "设定集-力量体系.md",
                                 os.path.join(project_root, "设定集", "力量体系.md"))

    print(f"[NovelEngine] Book project initialized at: {project_root}")
    print(f"  Name: {name or '(untitled)'}")
    print(f"  Genre: {genre or '(unspecified)'}")


def _copy_template_if_exists(src_dir, filename, dest_path):
    """Copy a template file if it exists and dest doesn't exist."""
    src = os.path.join(src_dir, filename)
    if os.path.isfile(src) and not os.path.isfile(dest_path):
        shutil.copy2(src, dest_path)
```

- [ ] **Step 2: 编写测试 `tests/test_init_project.py`**

```python
"""Tests for project initialization."""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from init_project import init_book_project, DEFAULT_STATE


class TestInitProject:
    def test_init_creates_state_json(self, tmp_path):
        init_book_project(str(tmp_path), name="测试书", genre="修仙")
        state_path = os.path.join(str(tmp_path), ".novel", "state.json")
        assert os.path.isfile(state_path)
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        assert state["project_info"]["name"] == "测试书"
        assert state["project_info"]["genre"] == "修仙"
        assert state["project_info"]["phase"] == "init"

    def test_init_creates_directories(self, tmp_path):
        init_book_project(str(tmp_path))
        for d in ["设定集", "大纲", "正文/白话剧情", "拆书存档"]:
            assert os.path.isdir(os.path.join(str(tmp_path), d))

    def test_init_raises_if_exists(self, tmp_path):
        init_book_project(str(tmp_path))
        with pytest.raises(FileExistsError):
            init_book_project(str(tmp_path))

    def test_default_state_has_required_keys(self):
        assert "project_info" in DEFAULT_STATE
        assert "settings" in DEFAULT_STATE
        assert "outline" in DEFAULT_STATE
        assert "entity_index" in DEFAULT_STATE
        assert "relation_graph" in DEFAULT_STATE
```

- [ ] **Step 3: 运行测试**

```bash
cd "D:/占占tools/NovelEngine"
python -m pytest tests/test_init_project.py -v
```

- [ ] **Step 4: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add scripts/init_project.py tests/test_init_project.py
git commit -m "feat: add book project initialization with standard directory structure"
```

---

### Task 8: 编写 Deconstruction Agent

**Files:**
- Create: `agents/deconstruction-agent.md`

- [ ] **Step 1: 编写 `agents/deconstruction-agent.md`**

从 webnovel-writer deconstruction-agent.md 改造，去掉写文件的约束（我们本来就不写 canon），保留核心拆解逻辑、两模式流程、schema 定义和质量门控。主要改动：简化禁止项描述，去掉对 .story-system/.webnovel 的引用，增加输出存储指导（结果由 Skill 编排写入 拆书存档/）。

完整内容见 webnovel-writer `/tmp/webnovel-writer/webnovel-writer/agents/deconstruction-agent.md`（296 行），改造点为：
- "身份"段：改为 "你是 NovelEngine 的参考书拆解子代理"
- "工具与输出边界"段：改为 "不写文件，所有结果返回给 Skill 主流程，由 Skill 写入 拆书存档/"
- "抽象转化规则"段：保留完整
- "输出 Schema"段：保留完整 JSON schema
- "边界、确认与错误处理"段：去掉 `.webnovel/state.json` 和 `idea_bank.json` 引用

```bash
# 复制原版作为基础，然后手动修改关键段落
cp "/tmp/webnovel-writer/webnovel-writer/agents/deconstruction-agent.md" \
   "D:/占占tools/NovelEngine/agents/deconstruction-agent.md"
```

- [ ] **Step 2: 修改 agent 的头部 frontmatter 和关键段落**

修改 `agents/deconstruction-agent.md` 的：

1. 第 1 行 frontmatter description 改为：
```
description: NovelEngine 参考书拆解子代理。抽取可迁移的创作模式，不污染新书 canon。
```

2. 第 13-15 行（身份段目标描述）的开头改为：
```
你是 NovelEngine 的参考书拆解子代理。你的任务是把用户提供的参考小说文本...
```

3. 第 33 行开始的 "工具与输出边界" 段，将：
```
本 agent 是 init 前置分析器，只返回结构化结果，不写任何文件。init 早期尚未生成书项目目录，因此不得假设 `.webnovel/tmp/` 或任何项目路径存在。

严禁创建、写入或修改：
- `.story-system/`
- `.webnovel/`
- `设定集/`
```
改为：
```
本 agent 是拆书分析器，只返回结构化结果，不写任何文件。结果由 Skill 主流程写入 `拆书存档/<书名>/`。

严禁创建、写入或修改任何项目文件、设定文件或 canon 数据。
```

4. 第 208 行开始的 "边界、确认与错误处理" 段，去掉：
```
- 不写 `idea_bank.json`。只有 init 主流程在用户确认后，才能把已变形的模式写入 `idea_bank.json` 或生成项目文件。
- 不把 `.webnovel/state.json` 当作可写目标；它是 init/runtime 的项目读模型。
```

```bash
# 验证修改后的文件
head -5 "D:/占占tools/NovelEngine/agents/deconstruction-agent.md"
wc -l "D:/占占tools/NovelEngine/agents/deconstruction-agent.md"
```

- [ ] **Step 3: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add agents/deconstruction-agent.md
git commit -m "feat: add deconstruction agent (adapted from webnovel-writer)"
```

---

### Task 9: 编写 Worldbuilding Agent

**Files:**
- Create: `agents/worldbuilding-agent.md`

- [ ] **Step 1: 编写 `agents/worldbuilding-agent.md`**

```markdown
---
name: worldbuilding-agent
description: NovelEngine 世界观搭建代理。通过结构化问答帮助作者系统化搭建等级体系、货币体系、势力格局、人物关系和世界规则。
tools: Read, Bash, AskUserQuestion
model: inherit
color: blue
---

# worldbuilding-agent

## 1. 身份

你是 NovelEngine 的世界观搭建代理。你的任务是通过分阶段结构化问答，帮助作者从零到一搭建一个自洽、可用的网文世界观。你负责"思考和提问"，不直接写文件——设定文件的生成由 Skill 主流程通过 Bash 调用模板完成。

## 2. 五个子系统

你需要引导作者完成以下五个子系统的搭建。不必全部做完——根据作者的题材和需求，有些子系统可以跳过或简化。

### 2.1 等级/力量体系

根据题材自动选择预设框架：

- 修仙类：炼气 → 筑基 → 金丹 → 元婴 → 化神 → 合体 → 大乘 → 渡劫
- 高武类：武者 → 武师 → 大武师 → 武王 → 武皇 → 武宗 → 武尊 → 武圣
- 异能类：F → E → D → C → B → A → S → SS → SSS
- 系统流：Lv.1 → Lv.N（需定义每级解锁能力）
- 西幻：学徒 → 初级 → 中级 → 高级 → 大法师 → 魔导师 → 法圣 → 法神
- 自定义：作者完全自定义

对每个等级必须明确：
- 该等级的核心能力/技能解锁
- 突破条件和难度
- 在故事世界中的社会地位（稀有度）
- 战力换算规则（同级之间、越级挑战的可能性）

### 2.2 货币/经济体系

引导作者定义：
- 货币层级（如：铜币 → 银币 → 金币 → 灵石 → 灵晶）
- 兑换比例（如：1 灵石 = 100 金币）
- 购买力锚定（一章饭、一把普通武器、一件珍稀材料各多少钱）
- 资源稀缺度（哪些资源是稀缺的，如何影响剧情）

### 2.3 势力格局

引导作者定义：
- 主要势力（宗门/家族/组织/国家）
- 势力之间的关系（同盟/敌对/中立/附庸）
- 势力间的压迫结构（谁压制谁，为什么）
- 主角所属势力的定位和上升路径

### 2.4 人物关系

引导作者定义核心角色（每类 1-5 个）：
- 主角：D-F-W-N-C 五维模型（Desire 欲望 / Flaw 缺陷 / Want 表层目标 / Need 深层需求 / Core trait 核心特质）
- 女主/感情线角色：与主角的关系起点和发展方向
- 关键配角：功能定位（导师/搭档/竞争对手/搞笑担当）
- 反派层级：小反派 → 中反派 → 大反派 → 幕后黑手

### 2.5 世界规则

引导作者定义：
- 地理格局（大陆/宗门分布/禁地区域）
- 历史大事件时间线
- 世界特殊规则（如"灵气浓度决定修炼速度"）
- 限制与代价（力量体系的代价、世界规则的边界）

## 3. 交互流程

```
Step 1: 确认题材 → 加载对应等级体系预设 + 世界观模板
Step 2: 搭建等级/力量体系（逐级确认或批量接受预设）
Step 3: 搭建货币/经济体系（如有需要）
Step 4: 绘制势力格局
Step 5: 设计核心人物（主角优先，配角按需）
Step 6: 补充世界规则
Step 7: 调用 consistency-agent 做跨设定冲突检测
Step 8: 汇总所有设定，请用户最终确认
```

每步只问当前缺失且会阻塞下一步的信息。用户已明确的，不重复问。

## 4. 输出指导

设定内容由 Skill 主流程通过 Bash 调用模板文件写入 `设定集/` 目录。本 agent 只需：
- 将确认后的设定内容以结构化方式返回给 Skill
- 标注每个子系统的完成状态（done / pending / skipped）

## 5. 边界

- 不替用户做世界观的核心创意决定（如"主角叫什么名字"），只提供选项和框架
- 不做文学性描述（如"这个世界美丽而神秘..."），只做结构化设定
- 不写文件——文件写入由 Skill 编排
- 不跨过充分性闸门——关键信息未收集完毕前，不标记为 done
```

- [ ] **Step 2: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add agents/worldbuilding-agent.md
git commit -m "feat: add worldbuilding agent with 5-subsystem interactive framework"
```

---

### Task 10: 编写 Consistency Agent

**Files:**
- Create: `agents/consistency-agent.md`

- [ ] **Step 1: 编写 `agents/consistency-agent.md`**

```markdown
---
name: consistency-agent
description: NovelEngine 一致性校验代理。跨设定文件检测世界观冲突，确保等级、时间线、角色设定不自相矛盾。
tools: Read, Grep, Bash
model: inherit
color: red
---

# consistency-agent

## 1. 身份

你是 NovelEngine 的一致性校验代理。你的职责是检测世界观设定中的矛盾和不自洽之处。你只报告问题，不修改设定——修改决策由作者完成。

## 2. 校验维度

### 2.1 等级体系一致性

检查项：
- 等级命名是否统一（同一个等级在力量体系.md 和主角卡.md 中名称一致）
- 战力描述是否矛盾（如"金丹期能移山填海"但某角色金丹期却打不过一块巨石）
- 突破条件是否有循环依赖（突破 B 需要 A 物品，但 A 物品只有 B 级以上才能获取）
- 等级与社会地位是否匹配（如"筑基期修士很罕见"但主角一天遇到五个）

### 2.2 时间线一致性

检查项：
- 角色年龄是否合理（如"主角 15 岁达到金丹期"但体系规定修炼到金丹至少需要 50 年）
- 历史事件时间线是否自洽（事件 A 在事件 B 之前发生，但描述中 B 是 A 的原因）
- 不同文件中的时间标记是否一致

### 2.3 角色设定一致性

检查项：
- 同一角色在不同文件中的描述是否冲突
- 角色关系是否有逻辑矛盾（A 是 B 的师父，但 A 的年龄比 B 小）
- 角色动机与行为是否自洽（角色目标是"隐居山林"但主动参与所有江湖纷争）

### 2.4 世界规则一致性

检查项：
- 世界规则是否有例外未说明（"这个世界没有魔法"但某角色使用了魔法）
- 资源稀缺度与实际出现频率是否匹配（某种"极为罕见"的药材每章都出现）
- 地理描述是否自相矛盾（宗门 A 在东域和西域同时被提及）

### 2.5 跨文件校验

当被调用时，你需要：
1. 读取所有已完成（status=done）的设定文件
2. 逐维度的进行交叉比对
3. 输出发现问题清单，每条标出：涉及文件、矛盾描述、严重程度（P0/P1/P2）、修复建议

## 3. 严重程度定义

| 级别 | 定义 | 示例 |
|------|------|------|
| P0 | 逻辑死锁，会导致剧情无法自洽 | 突破 B 需要的物品只有 B 级以上才能获取 |
| P1 | 需要作者明确裁决的矛盾 | 同一个角色在两个文件中年龄不同 |
| P2 | 建议优化，不阻塞 | 某种"罕见"资源出现频率偏高 |

## 4. 输出格式

返回结构化 JSON：

```json
{
  "check_time": "",
  "files_checked": [],
  "issues": [
    {
      "id": "CONS-001",
      "severity": "P0 | P1 | P2",
      "dimension": "level | timeline | character | world_rule | cross_file",
      "description": "",
      "files_involved": [],
      "conflict_detail": "",
      "suggestion": ""
    }
  ],
  "summary": {
    "total_issues": 0,
    "p0_count": 0,
    "p1_count": 0,
    "p2_count": 0,
    "verdict": "pass | warning | block"
  }
}
```

## 5. 调用时机

- `/novel-worldbuild` 完成所有子系统后自动调用
- `/novel-generate` 生成白话剧情后可选调用（校验是否违反设定）
- 作者手动调用：`/novel-query --check-consistency`

## 6. 边界

- 只检测事实性矛盾，不做文学性评判（如"这个设定不够新颖"）
- 不自动修改任何文件
- 不确定的矛盾标注 P2，让作者判断
- 不重复检测已标记为"已忽略"的历史问题
```

- [ ] **Step 2: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add agents/consistency-agent.md
git commit -m "feat: add consistency agent for cross-file setting conflict detection"
```

---

### Task 11: 编写 novel-deconstruct Skill

**Files:**
- Create: `skills/novel-deconstruct/SKILL.md`

- [ ] **Step 1: 编写 `skills/novel-deconstruct/SKILL.md`**

```markdown
---
name: novel-deconstruct
description: 拆解参考小说，提取可迁移的创作模式。支持快速模式（黄金三章分析）和深度模式（逐章情节点提取）。结果为抽象条件框架，不复制原作事实。
allowed-tools: Read Write Edit Grep Bash Agent AskUserQuestion WebSearch WebFetch
argument-hint: "[书名或章节范围（可选）]"
---

# /novel-deconstruct — 拆书分析

## 目标

- 快速模式：分析黄金三章的开篇钩子、爽点铺设、世界观引入和章尾悬念策略
- 深度模式：逐章提取情节点，聚合为剧情线和故事线，抽象可迁移的创作模式
- 输出存入 `拆书存档/<书名>/`，永不污染当前书项目的 canon

## 执行原则

1. 只抽离"条件框架"，不复制原作事实（角色名、地名、金手指、具体情节）。
2. 没有文本内容时（只有书名/平台），不得猜测编造该书的黄金三章或角色设定。
3. 拆书结果由本 Skill 写入 `拆书存档/` 目录，Agent 不直接写文件。
4. 质量不达标的结果不入库——coverage <85% 触发补充分析，confidence <0.85 标记为待完善。

## 流程

### Step 1：收集输入

必须从用户获取：
- 参考书名
- 来源（平台 / 文件路径 / 章节摘录）
- 分析模式（quick / deep / auto）

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
```

如果用户只给书名和平台，没有文本：
- 先询问是否能提供文本摘录或路径
- 如果不能，将参考书仅作为"方向线索"，不得编造分析结果
- 用 WebSearch/WebFetch 尝试找到该书公开信息（如简介、读者评价），但必须在报告中标注"基于公开信息，非原文分析"

### Step 2：调用 Deconstruction Agent

```text
Agent(
  subagent_type: "novel-engine:deconstruction-agent",
  prompt: "reference_title={书名}; reference_source={来源}; reference_text_path={文本路径}; reference_text_excerpt={摘录}; analysis_mode={quick|deep|auto}; target_genre={可选的题材上下文}。只返回 init_reference_research JSON 对象，不写任何文件。"
)
```

### Step 3：校验质量

收到 Agent 返回的 JSON 后：

- 检查 `quality.passed` 是否为 true
- 检查 `quality.confidence` 是否 >= 0.85
- 检查 `canon_contamination_warnings` 是否为空
- 如果质量不过关，告知用户具体问题和建议（补充文本、降低模式到 quick 等）

### Step 4：保存到拆书存档

```bash
export BOOK_NAME_SAFE="$(echo '{书名}' | sed 's/[\/:*?"<>|]/_/g')"
export DECONSTRUCT_DIR="${WORKSPACE_ROOT}/拆书存档/${BOOK_NAME_SAFE}"
mkdir -p "${DECONSTRUCT_DIR}"

# 保存结构化 JSON
cat > "${DECONSTRUCT_DIR}/analysis.json" << 'JSONEOF'
{Agent 返回的完整 JSON}
JSONEOF

# 生成可读报告
cat > "${DECONSTRUCT_DIR}/报告.md" << 'REPORTEOF'
# {书名} 拆书分析报告

> 分析模式：{quick/deep}
> 分析时间：{timestamp}
> 质量：confidence={X} coverage={Y}%

## 读者承诺
{reader_promise 内容}

## 开篇钩子模式
{opening_hook_patterns 内容}

## 爽点循环
{cool_point_loops 内容}

## 可借鉴结构
{borrowable_structures 内容}

## 不可复制
{do_not_copy 内容}

## 差异化要求
{differentiation_requirements 内容}
REPORTEOF
```

### Step 5：更新项目状态

```bash
python -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/webnovel.py" \
  --project-root "${WORKSPACE_ROOT}" \
  deconstruct --add --title "{书名}" --file "${DECONSTRUCT_DIR}/analysis.json"
```

### Step 6：呈现结果

向用户展示摘要：
- 分析模式和质量评分
- 发现的关键模式（2-3 条）
- 不可复制的红线
- 完整的报告路径

## 跨书对比模式

当用户提供 `--compare` 参数时：

```bash
/novel-deconstruct --compare <书名A> <书名B>
```

从已有拆书存档中加载两份 analysis.json，对比分析：
- 同题材的共性规律
- 差异化策略
- 读者承诺的异同
- 输出对比报告到 `拆书存档/对比分析/`
```

- [ ] **Step 2: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add skills/novel-deconstruct/
git commit -m "feat: add novel-deconstruct skill with quick/deep mode and cross-book comparison"
```

---

### Task 12: 编写 novel-worldbuild Skill

**Files:**
- Create: `skills/novel-worldbuild/SKILL.md`
- Create: `skills/novel-worldbuild/references/currency-systems.md`

- [ ] **Step 1: 编写 `skills/novel-worldbuild/references/currency-systems.md`**

```markdown
# 货币/经济体系设计指南

## 1. 货币层级设计

### 常见模式

| 模式 | 层级示例 | 适用题材 |
|------|----------|----------|
| 凡人货币 | 铜币 → 银币 → 金币 → 银票 → 金票 | 历史、武侠、古代言情 |
| 修仙货币 | 铜币 → 银币 → 金币 → 灵石 → 灵晶 → 仙晶 | 修仙、玄幻 |
| 异能货币 | 现金 → 积分 → 功勋点 → 特殊资源 | 都市异能、系统流、末世 |
| 西幻货币 | 铜币 → 银币 → 金币 → 魔晶 → 龙晶 | 西幻 |
| 科幻货币 | 信用点 → 能量币 → 稀有元素 | 科幻、星际 |

### 设计要点

- 每层之间兑换比例要合理（通常 1:100）
- 高层货币在日常交易中很少出现（增加稀缺感）
- 主角获取上一级货币的时间点 = 剧情里程碑

## 2. 购买力锚定

给每个货币层级设定一个日常物品的参考价格：

| 物品 | 价格 | 货币 |
|------|------|------|
| 一顿饭 | 10 | 铜币 |
| 一晚住宿 | 50 | 铜币 |
| 一把普通武器 | 5 | 银币 |

这保证后续写作时物价不会前后矛盾。

## 3. 资源稀缺度

将关键资源分为四档：

| 稀缺度 | 说明 | 持有者 | 对剧情的影响 |
|--------|------|--------|-------------|
| 常见 | 随处可得 | 普通人 | 日常消耗 |
| 稀有 | 需要一定实力/渠道 | 中层势力 | 推动支线剧情 |
| 珍稀 | 只有少数人/势力拥有 | 顶层势力 | 卷级冲突焦点 |
| 传说 | 几乎不存在 | 已失传或极秘 | 全书核心麦高芬 |
```

- [ ] **Step 2: 编写 `skills/novel-worldbuild/SKILL.md`**

```markdown
---
name: novel-worldbuild
description: 系统化搭建网文世界观。分五个子系统交互式推进：等级力量体系、货币经济、势力格局、人物关系、世界规则。完成后自动触发一致性校验。
allowed-tools: Read Write Edit Grep Bash Agent AskUserQuestion
argument-hint: "[子系统名称或'all'（可选）]"
---

# /novel-worldbuild — 世界观搭建

## 目标

- 通过分阶段结构化问答，系统化搭建一个自洽的网文世界观
- 产出可落地的设定文件，存入 `设定集/`
- 自动检测跨设定冲突

## 执行原则

1. 先收集，再生成。关键信息未充分确认前不写文件。
2. 每轮只问当前缺失的关键信息——不一次抛 10 个问题。
3. 用户已明确的信息不重复问；冲突信息让用户裁决。
4. 参考 `references/` 下的设计指南，但允许用户完全自定义。

## 引用加载策略

| 触发条件 | 加载文件 |
|----------|----------|
| 每次启动 | `${SKILL_ROOT}/references/setting-consistency.md` |
| 涉及等级体系 | `${SKILL_ROOT}/references/power-systems.md` |
| 涉及势力 | `${SKILL_ROOT}/references/faction-systems.md` |
| 涉及角色 | `${SKILL_ROOT}/references/character-design.md` |
| 涉及世界规则 | `${SKILL_ROOT}/references/world-rules.md` |
| 涉及经济 | `${SKILL_ROOT}/references/currency-systems.md` |
| 选题材 | `${SKILL_ROOT}/../../references/genre-profiles.md` + `${SKILL_ROOT}/../../templates/genres/{题材}.md` |

## 交互流程

### Step 1：预检与上下文

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"

# 确认项目已初始化
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" preflight
```

如果项目未初始化：
- 先询问书名和工作标题
- 运行 `python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" init --name "{书名}" --genre "{题材}"`

### Step 2：选题材

加载题材模板和 genre-profiles.md。展示给用户当前项目已选定的题材（从 state.json 读取），确认是否要调整。

### Step 3：搭等级/力量体系

调用 Worldbuilding Agent 聚焦等级体系：

```text
Agent(
  subagent_type: "novel-engine:worldbuilding-agent",
  prompt: "聚焦子系统：等级/力量体系。题材={genre}。已确认的设定：{已收集的信息}。请引导逐级确认或批量接受预设。"
)
```

确认后写入 `设定集/力量体系.md`。

### Step 4：搭经济体系（可选）

询问用户是否需要定义货币体系。如果题材不需要（如纯悬疑），可跳过。

确认后写入 `设定集/经济体系.md`。

### Step 5：绘势力格局

确认后写入 `设定集/势力格局.md`。

### Step 6：设计人物

先主角，再配角。参考 character-design.md 的 D-F-W-N-C 五维模型。

确认后写入 `设定集/主角卡.md` 和 `设定集/配角卡.md`。

### Step 7：补世界规则

确认后写入 `设定集/世界观.md`。

### Step 8：一致性校验

```text
Agent(
  subagent_type: "novel-engine:consistency-agent",
  prompt: "校验 ${WORKSPACE_ROOT}/设定集/ 下所有已完成的设定文件。返回 issues 清单。"
)
```

展示检测结果，P0 项必须解决后才能标记 worldbuild 完成。

### Step 9：更新项目状态

```bash
python -X utf8 "${SCRIPTS_DIR}/webnovel.py" --project-root "${WORKSPACE_ROOT}" \
  preflight
```

## 单独搭建某个子系统

用户也可以只搭一个子系统：

```bash
/novel-worldbuild power    # 只搭力量体系
/novel-worldbuild economy   # 只搭经济体系
/novel-worldbuild factions # 只搭势力格局
/novel-worldbuild characters # 只搭人物关系
/novel-worldbuild world    # 只搭世界规则
```
```

- [ ] **Step 3: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add skills/novel-worldbuild/
git commit -m "feat: add novel-worldbuild skill with 5-subsystem interactive workflow and consistency check"
```

---

### Task 13: 编写 novel-query 和 novel-doctor Skill

**Files:**
- Create: `skills/novel-query/SKILL.md`
- Create: `skills/novel-doctor/SKILL.md`

- [ ] **Step 1: 编写 `skills/novel-query/SKILL.md`**

```markdown
---
name: novel-query
description: 查询当前书项目的设定、角色、势力关系、伏笔清单和项目状态。
allowed-tools: Read Grep Bash
argument-hint: "[查询内容（可选）]"
---

# /novel-query — 综合查询

## 目标

快速查询当前书项目的各类信息，不修改任何文件。

## 可用查询

| 查询方式 | 示例 | 说明 |
|----------|------|------|
| 角色查询 | `/novel-query 萧炎` | 查找角色详情（主角卡、出场记录） |
| 势力查询 | `/novel-query 宗门` | 查找势力信息 |
| 设定查询 | `/novel-query 金丹期` | 在设定文件中搜索关键词 |
| 伏笔查询 | `/novel-query --foreshadowing` | 列出所有活跃伏笔 |
| 项目状态 | `/novel-query --status` | 展示项目整体进度 |
| 一致性检查 | `/novel-query --check-consistency` | 手动触发一致性校验 |

## 流程

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
```

### 实体查询

如果用户输入的是一个名称（角色名、势力名、地名）：
1. 在 `设定集/` 中 grep 该名称
2. 提取相关段落
3. 展示角色基本信息和关联关系

### 项目状态查询

```bash
python -X utf8 "${CLAUDE_PLUGIN_ROOT}/scripts/webnovel.py" \
  --project-root "${WORKSPACE_ROOT}" preflight
```

### 一致性检查

```text
Agent(
  subagent_type: "novel-engine:consistency-agent",
  prompt: "校验 ${WORKSPACE_ROOT}/设定集/ 下所有已完成的设定文件。返回 issues 清单。"
)
```

## 输出原则

- 查询结果直接展示，不做二次分析
- 设定搜索按匹配度排序，最多展示 5 条
- 找不到时明确告知"未找到"，不编造
```

- [ ] **Step 2: 编写 `skills/novel-doctor/SKILL.md`**

```markdown
---
name: novel-doctor
description: 项目体检——检查目录完整性、设定文件格式、实体索引健康状态和依赖项。
allowed-tools: Read Bash
argument-hint: "[--chapter N 或 --format text/json（可选）]"
---

# /novel-doctor — 项目体检

## 目标

对当前书项目做全面健康检查，输出诊断报告和修复建议。只读不写。

## 检查项

### 目录完整性
- `设定集/`、`大纲/`、`正文/白话剧情/`、`拆书存档/` 是否存在
- `.novel/state.json` 是否可读

### 设定文件健康
- 每个已标记为 "done" 的设定文件是否存在
- 文件编码是否正常（UTF-8）
- 文件大小是否异常（空文件、过大文件）

### 实体索引健康
- `.novel/index.db` 是否存在和可读（如果已创建）
- 实体数量是否与设定文件中提及的一致

### 大纲健康
- 总纲是否存在
- 卷纲文件是否有对应的章纲
- 时间线是否与卷纲一致

## 流程

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"

python -X utf8 "${SCRIPTS_DIR}/webnovel.py" \
  --project-root "${WORKSPACE_ROOT}" doctor
```

## 输出

- 每个检查项的状态（PASS / WARN / FAIL）
- FAIL 项的修复建议
- 总体健康评分
```

- [ ] **Step 3: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add skills/novel-query/ skills/novel-doctor/
git commit -m "feat: add novel-query and novel-doctor skills"
```

---

### Task 14: 编写 Python 数据模块

**Files:**
- Create: `scripts/data_modules/index_manager.py`
- Create: `scripts/data_modules/relation_graph.py`
- Create: `scripts/data_modules/consistency_checker.py`
- Create: `scripts/data_modules/template_manager.py`
- Create: `scripts/data_modules/deconstruct_store.py`
- Create: `scripts/data_modules/project_phase.py`
- Create: `scripts/data_modules/placeholder_scanner.py`
- Create: `scripts/data_modules/archive_manager.py`
- Create: `scripts/data_modules/doctor.py`

- [ ] **Step 1: 编写 `scripts/data_modules/index_manager.py`**

```python
"""SQLite-based entity index for characters, factions, locations, items."""

import sqlite3
import os
import json


CREATE_ENTITIES_TABLE = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('character','faction','location','item','concept')),
    aliases TEXT DEFAULT '[]',
    attributes TEXT DEFAULT '{}',
    first_appearance TEXT,
    last_updated TEXT,
    source_file TEXT
)
"""

CREATE_APPEARANCES_TABLE = """
CREATE TABLE IF NOT EXISTS appearances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    role TEXT DEFAULT 'mentioned',
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)
"""


class IndexManager:
    """Manages the entity index stored in .novel/index.db."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "index.db")
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(CREATE_ENTITIES_TABLE)
            conn.execute(CREATE_APPEARANCES_TABLE)

    def upsert_entity(self, entity_id, name, entity_type, aliases=None, attributes=None, source_file=None):
        """Insert or update an entity."""
        import datetime
        now = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO entities (id, name, type, aliases, attributes, last_updated, source_file)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (entity_id, name, entity_type, json.dumps(aliases or [], ensure_ascii=False),
                 json.dumps(attributes or {}, ensure_ascii=False), now, source_file)
            )

    def get_entity(self, entity_id):
        """Get entity by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM entities WHERE id=?", (entity_id,)).fetchone()
        if row:
            return {
                "id": row[0], "name": row[1], "type": row[2],
                "aliases": json.loads(row[3]), "attributes": json.loads(row[4]),
                "first_appearance": row[5], "last_updated": row[6], "source_file": row[7]
            }
        return None

    def search_by_name(self, name_part):
        """Search entities by name fragment."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM entities WHERE name LIKE ?",
                (f"%{name_part}%",)
            ).fetchall()
        return [
            {"id": r[0], "name": r[1], "type": r[2],
             "aliases": json.loads(r[3]), "attributes": json.loads(r[4])}
            for r in rows
        ]

    def get_all_entities(self, entity_type=None):
        """Get all entities, optionally filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            if entity_type:
                rows = conn.execute("SELECT * FROM entities WHERE type=?", (entity_type,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM entities").fetchall()
        return [
            {"id": r[0], "name": r[1], "type": r[2],
             "aliases": json.loads(r[3]), "attributes": json.loads(r[4])}
            for r in rows
        ]
```

- [ ] **Step 2: 编写 `scripts/data_modules/relation_graph.py`**

```python
"""Simple relation graph manager using SQLite adjacency list."""

import sqlite3
import os
import json


CREATE_RELATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    description TEXT,
    strength INTEGER DEFAULT 5,
    source_file TEXT,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
)
"""


class RelationGraph:
    """Manages entity relationship graph."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "index.db")
        self._init_table()

    def _init_table(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_RELATIONS_TABLE)

    def add_relation(self, source_id, target_id, relation_type, description="", strength=5, source_file=None):
        """Add a directional relation between two entities."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO relations (source_id, target_id, relation_type, description, strength, source_file)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (source_id, target_id, relation_type, description, strength, source_file)
            )

    def get_relations(self, entity_id):
        """Get all relations for an entity (both inbound and outbound)."""
        with sqlite3.connect(self.db_path) as conn:
            outbound = conn.execute(
                "SELECT * FROM relations WHERE source_id=?", (entity_id,)
            ).fetchall()
            inbound = conn.execute(
                "SELECT * FROM relations WHERE target_id=?", (entity_id,)
            ).fetchall()
        return {
            "outbound": [self._row_to_dict(r) for r in outbound],
            "inbound": [self._row_to_dict(r) for r in inbound],
        }

    def _row_to_dict(self, row):
        return {
            "id": row[0], "source_id": row[1], "target_id": row[2],
            "relation_type": row[3], "description": row[4],
            "strength": row[5], "source_file": row[6],
        }
```

- [ ] **Step 3: 编写 `scripts/data_modules/consistency_checker.py`**

```python
"""Consistency checker for cross-file setting validation."""

import os
import re


class ConsistencyChecker:
    """Checks setting files for internal consistency issues."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.settings_dir = os.path.join(project_root, "设定集")

    def check_all(self):
        """Run all consistency checks. Returns a list of issue dicts."""
        issues = []
        issues.extend(self._check_files_exist())
        issues.extend(self._check_encoding())
        issues.extend(self._check_cross_references())
        return issues

    def _check_files_exist(self):
        """Check that all expected setting files exist."""
        issues = []
        expected = ["世界观.md", "力量体系.md", "主角卡.md"]
        for f in expected:
            path = os.path.join(self.settings_dir, f)
            if not os.path.isfile(path):
                issues.append({
                    "id": f"FILE-{len(issues)+1:03d}",
                    "severity": "P1",
                    "dimension": "file",
                    "description": f"Missing setting file: {f}",
                    "files_involved": [f],
                    "conflict_detail": f"Expected file not found at {path}",
                    "suggestion": f"Run /novel-worldbuild to create {f}"
                })
        return issues

    def _check_encoding(self):
        """Check that all setting files are valid UTF-8."""
        issues = []
        if not os.path.isdir(self.settings_dir):
            return issues
        for f in os.listdir(self.settings_dir):
            if f.endswith(".md"):
                path = os.path.join(self.settings_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        fh.read()
                except UnicodeDecodeError as e:
                    issues.append({
                        "id": f"ENC-{len(issues)+1:03d}",
                        "severity": "P0",
                        "dimension": "encoding",
                        "description": f"File {f} is not valid UTF-8",
                        "files_involved": [f],
                        "conflict_detail": str(e),
                        "suggestion": "Re-save the file as UTF-8 encoding"
                    })
        return issues

    def _check_cross_references(self):
        """Check cross-references between setting files."""
        # Phase 1 stub - full cross-reference check requires NLP
        # Will be expanded when consistency-agent is invoked
        return []
```

- [ ] **Step 4: 编写 `scripts/data_modules/template_manager.py`**

```python
"""Template management — list, copy, and validate output templates."""

import os


class TemplateManager:
    """Manages output templates located in <plugin_root>/templates/."""

    def __init__(self, plugin_root):
        self.templates_dir = os.path.join(plugin_root, "templates")
        self.genres_dir = os.path.join(self.templates_dir, "genres")
        self.outputs_dir = os.path.join(self.templates_dir, "outputs")

    def list_genres(self):
        """List available genre templates."""
        if not os.path.isdir(self.genres_dir):
            return []
        return sorted([f.replace(".md", "") for f in os.listdir(self.genres_dir) if f.endswith(".md")])

    def list_output_templates(self):
        """List available output templates."""
        if not os.path.isdir(self.outputs_dir):
            return []
        return sorted([f for f in os.listdir(self.outputs_dir) if f.endswith(".md")])

    def get_template_content(self, category, name):
        """Get the content of a template file."""
        if category == "genre":
            path = os.path.join(self.genres_dir, f"{name}.md")
        elif category == "output":
            path = os.path.join(self.outputs_dir, name)
        else:
            return None
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None
```

- [ ] **Step 5: 编写 `scripts/data_modules/deconstruct_store.py`**

```python
"""Deconstruction archive management."""

import os
import json
from datetime import datetime


class DeconstructStore:
    """Manages the deconstruction archive at 拆书存档/."""

    def __init__(self, project_root):
        self.archive_dir = os.path.join(project_root, "拆书存档")

    def add_analysis(self, title, analysis_json, report_md):
        """Save a deconstruction analysis."""
        safe_title = title.replace("/", "_").replace("\\", "_")
        dir_path = os.path.join(self.archive_dir, safe_title)
        os.makedirs(dir_path, exist_ok=True)

        analysis_path = os.path.join(dir_path, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis_json, f, ensure_ascii=False, indent=2)

        report_path = os.path.join(dir_path, "报告.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        return dir_path

    def list_archives(self):
        """List all deconstruction archives."""
        if not os.path.isdir(self.archive_dir):
            return []
        result = []
        for name in os.listdir(self.archive_dir):
            dir_path = os.path.join(self.archive_dir, name)
            analysis_path = os.path.join(dir_path, "analysis.json")
            if os.path.isfile(analysis_path):
                with open(analysis_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                result.append({
                    "title": name,
                    "mode": data.get("analysis_mode", "unknown"),
                    "quality": data.get("quality", {}),
                    "source": data.get("source", {}),
                })
        return result

    def get_analysis(self, title):
        """Retrieve a specific analysis by title."""
        safe_title = title.replace("/", "_").replace("\\", "_")
        analysis_path = os.path.join(self.archive_dir, safe_title, "analysis.json")
        if not os.path.isfile(analysis_path):
            return None
        with open(analysis_path, "r", encoding="utf-8") as f:
            return json.load(f)
```

- [ ] **Step 6: 编写 `scripts/data_modules/project_phase.py`**

```python
"""Project phase detection and transitions."""

VALID_PHASES = ["init", "worldbuilding", "outlining", "generating", "complete"]


def get_current_phase(project_root):
    """Get current project phase from state.json."""
    from data_modules.config import load_project_state
    state = load_project_state(project_root)
    return state.get("project_info", {}).get("phase", "init")


def set_phase(project_root, new_phase):
    """Transition project to a new phase."""
    if new_phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase: {new_phase}. Valid: {VALID_PHASES}")
    from data_modules.config import load_project_state, save_project_state
    state = load_project_state(project_root)
    if "project_info" not in state:
        state["project_info"] = {}
    old_phase = state["project_info"].get("phase", "init")
    state["project_info"]["phase"] = new_phase
    save_project_state(project_root, state)
    return old_phase, new_phase
```

- [ ] **Step 7: 编写 `scripts/data_modules/placeholder_scanner.py`**

```python
"""Scan project files for placeholder markers like TODO, TBD, FIXME."""

import os
import re

PLACEHOLDER_PATTERNS = [
    (r"TODO", "todo"),
    (r"TBD", "tbd"),
    (r"FIXME", "fixme"),
    (r"XXX", "xxx"),
    (r"（待补充）", "pending_cn"),
    (r"待定", "pending_cn"),
]


def scan_file(filepath):
    """Scan a single file for placeholder markers. Returns list of (line_no, marker, line_text)."""
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern, tag in PLACEHOLDER_PATTERNS:
                    if re.search(pattern, line):
                        issues.append((i, tag, line.strip()))
    except (UnicodeDecodeError, PermissionError):
        pass
    return issues


def scan_project(project_root, dirs=None):
    """Scan project directories for placeholder markers."""
    if dirs is None:
        dirs = ["设定集", "大纲"]
    all_issues = {}
    for d in dirs:
        full_dir = os.path.join(project_root, d)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for f in files:
                if f.endswith(".md"):
                    filepath = os.path.join(root, f)
                    issues = scan_file(filepath)
                    if issues:
                        rel_path = os.path.relpath(filepath, project_root)
                        all_issues[rel_path] = issues
    return all_issues
```

- [ ] **Step 8: 编写 `scripts/data_modules/archive_manager.py`**

```python
"""Project backup and archive management."""

import os
import shutil
import zipfile
from datetime import datetime


def create_backup(project_root, backup_dir=None):
    """Create a timestamped zip backup of the project."""
    if backup_dir is None:
        backup_dir = os.path.join(project_root, ".novel", "backups")

    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = os.path.basename(project_root.rstrip("/\\"))
    zip_name = f"{project_name}_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_root):
            # Skip backups directory and .novel internal dirs
            dirs[:] = [d for d in dirs if d not in ("backups", "tmp")]
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, project_root)
                zf.write(filepath, arcname)

    return zip_path


def list_backups(project_root):
    """List available backup files."""
    backup_dir = os.path.join(project_root, ".novel", "backups")
    if not os.path.isdir(backup_dir):
        return []
    return sorted([f for f in os.listdir(backup_dir) if f.endswith(".zip")], reverse=True)
```

- [ ] **Step 9: 编写 `scripts/data_modules/doctor.py`**

```python
"""Project doctor — diagnose issues and suggest fixes."""

import os
import json
from datetime import datetime


def run_doctor(project_root):
    """Run full project diagnostic. Returns a formatted report string."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"NovelEngine Doctor Report")
    lines.append(f"Project: {project_root}")
    lines.append(f"Time: {datetime.now().isoformat()}")
    lines.append("=" * 60)

    checks = [
        _check_state_json,
        _check_directories,
        _check_settings_files,
        _check_outline_files,
    ]

    total = 0
    passed = 0
    warnings = 0
    failed = 0

    for check in checks:
        result = check(project_root)
        total += 1
        status_icon = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}.get(result["status"], "[????]")
        lines.append(f"\n{status_icon} {result['name']}")
        lines.append(f"  {result['detail']}")
        if result["status"] == "pass":
            passed += 1
        elif result["status"] == "warn":
            warnings += 1
        else:
            failed += 1

    lines.append(f"\n{'=' * 60}")
    lines.append(f"Summary: {passed} pass, {warnings} warn, {failed} fail (of {total})")
    if failed > 0:
        lines.append("Action: Fix FAIL items before continuing.")
    elif warnings > 0:
        lines.append("Action: Review WARN items. You can proceed but may hit issues later.")
    else:
        lines.append("Action: All clear! Proceed with confidence.")

    return "\n".join(lines)


def _check_state_json(project_root):
    state_path = os.path.join(project_root, ".novel", "state.json")
    if not os.path.isfile(state_path):
        return {"name": "State file", "status": "fail",
                "detail": ".novel/state.json not found. Run init first."}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        phase = state.get("project_info", {}).get("phase", "unknown")
        return {"name": "State file", "status": "pass",
                "detail": f"state.json valid. Phase: {phase}"}
    except (json.JSONDecodeError, KeyError) as e:
        return {"name": "State file", "status": "fail",
                "detail": f"state.json corrupt: {e}"}


def _check_directories(project_root):
    required = ["设定集", "大纲", "正文/白话剧情", "拆书存档"]
    missing = [d for d in required if not os.path.isdir(os.path.join(project_root, d))]
    if missing:
        return {"name": "Directories", "status": "warn",
                "detail": f"Missing: {', '.join(missing)}"}
    return {"name": "Directories", "status": "pass",
            "detail": f"All {len(required)} required directories exist."}


def _check_settings_files(project_root):
    settings_dir = os.path.join(project_root, "设定集")
    if not os.path.isdir(settings_dir):
        return {"name": "Settings files", "status": "fail",
                "detail": "设定集/ directory missing."}
    files = [f for f in os.listdir(settings_dir) if f.endswith(".md")]
    if not files:
        return {"name": "Settings files", "status": "warn",
                "detail": "设定集/ is empty. Run /novel-worldbuild."}
    # Check each file for content
    empty_files = []
    for f in files:
        path = os.path.join(settings_dir, f)
        if os.path.getsize(path) < 50:
            empty_files.append(f)
    if empty_files:
        return {"name": "Settings files", "status": "warn",
                "detail": f"Files appear empty or too short: {', '.join(empty_files)}"}
    return {"name": "Settings files", "status": "pass",
            "detail": f"{len(files)} setting files found."}


def _check_outline_files(project_root):
    outline_dir = os.path.join(project_root, "大纲")
    if not os.path.isdir(outline_dir):
        return {"name": "Outline files", "status": "warn",
                "detail": "大纲/ directory missing. Run /novel-outline when ready."}
    files = [f for f in os.listdir(outline_dir) if f.endswith(".md")]
    if not files:
        return {"name": "Outline files", "status": "warn",
                "detail": "大纲/ is empty. Run /novel-outline when ready."}
    return {"name": "Outline files", "status": "pass",
            "detail": f"{len(files)} outline files found."}
```

- [ ] **Step 10: 编写数据模块测试**

```bash
cat > "D:/占占tools/NovelEngine/tests/test_index_manager.py" << 'PYEOF'
"""Tests for IndexManager."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.index_manager import IndexManager


class TestIndexManager:
    def test_init_creates_db(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        assert os.path.isfile(os.path.join(str(tmp_path), ".novel", "index.db"))

    def test_upsert_and_get_entity(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character", aliases=["炎帝"], source_file="设定集/主角卡.md")
        entity = mgr.get_entity("char_001")
        assert entity["name"] == "萧炎"
        assert "炎帝" in entity["aliases"]
        assert entity["type"] == "character"

    def test_search_by_name(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character")
        mgr.upsert_entity("char_002", "萧战", "character")
        results = mgr.search_by_name("萧")
        assert len(results) == 2

    def test_get_all_entities_filtered(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character")
        mgr.upsert_entity("fact_001", "云岚宗", "faction")
        chars = mgr.get_all_entities("character")
        assert len(chars) == 1
        assert chars[0]["name"] == "萧炎"

    def test_get_nonexistent(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        assert mgr.get_entity("nonexistent") is None
PYEOF

cat > "D:/占占tools/NovelEngine/tests/test_relation_graph.py" << 'PYEOF'
"""Tests for RelationGraph."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.relation_graph import RelationGraph


class TestRelationGraph:
    def test_add_and_get_relations(self, tmp_path):
        graph = RelationGraph(str(tmp_path))
        graph.add_relation("char_001", "char_002", "师徒", "药老是萧炎的师父", strength=9)
        relations = graph.get_relations("char_001")
        assert len(relations["outbound"]) == 1
        assert relations["outbound"][0]["relation_type"] == "师徒"

    def test_inbound_relations(self, tmp_path):
        graph = RelationGraph(str(tmp_path))
        graph.add_relation("char_001", "char_002", "师徒")
        relations = graph.get_relations("char_002")
        assert len(relations["inbound"]) == 1
        assert relations["inbound"][0]["source_id"] == "char_001"
PYEOF
```

- [ ] **Step 11: 运行数据模块测试**

```bash
cd "D:/占占tools/NovelEngine"
python -m pytest tests/test_index_manager.py tests/test_relation_graph.py -v
```

- [ ] **Step 12: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add scripts/data_modules/ tests/test_index_manager.py tests/test_relation_graph.py
git commit -m "feat: add Python data modules (index, relations, consistency, templates, deconstruct store, doctor)"
```

---

### Task 15: 端到端集成验证

- [ ] **Step 1: 创建一个测试书项目**

```bash
cd "D:/占占tools/NovelEngine"
export CLAUDE_PLUGIN_ROOT="D:/占占tools/NovelEngine"

# 创建测试项目
python -X utf8 scripts/webnovel.py \
  --project-root "/tmp/novelengine-test" \
  init --name "测试之书" --genre "修仙"
```

期望输出：
```
[NovelEngine] Book project initialized at: /tmp/novelengine-test
  Name: 测试之书
  Genre: 修仙
```

- [ ] **Step 2: 验证项目结构**

```bash
ls -la "/tmp/novelengine-test/"
ls -la "/tmp/novelengine-test/.novel/"
ls -la "/tmp/novelengine-test/设定集/"
```

期望：所有目录存在，state.json 可读，设定集目录有模板文件。

- [ ] **Step 3: 运行 preflight**

```bash
python -X utf8 scripts/webnovel.py \
  --project-root "/tmp/novelengine-test" \
  preflight
```

期望：`[OK] Project at /tmp/novelengine-test passes preflight.`（初始状态应该通过）

- [ ] **Step 4: 运行 doctor**

```bash
python -X utf8 scripts/webnovel.py \
  --project-root "/tmp/novelengine-test" \
  doctor
```

期望：显示 doctor 报告，可能有 WARN（大纲为空）但不应有 FAIL。

- [ ] **Step 5: 运行全部测试**

```bash
cd "D:/占占tools/NovelEngine"
python -m pytest tests/ -v
```

期望：全部 PASS

- [ ] **Step 6: 清理测试项目**

```bash
rm -rf "/tmp/novelengine-test"
```

- [ ] **Step 7: Commit**

```bash
cd "D:/占占tools/NovelEngine"
git add -A
git commit -m "feat: Phase 1 integration — all tests pass, CLI functional"
```

---

## Phase 1 完成检查清单

完成 Phase 1 后，你应该拥有：

- [x] 项目骨架（目录结构、plugin.json、hooks、.gitignore）
- [x] 37 个题材模板（从 webnovel-writer 移植）
- [x] 5 个世界观设计 references（从 webnovel-writer 移植）
- [x] 8 个创意/反套路 references（从 webnovel-writer 移植）
- [x] 9 个输出模板（从 webnovel-writer 移植 + 2 个新写）
- [x] Python CLI 骨架（webnovel.py + 6 个数据模块）
- [x] 新书初始化功能（init_project.py）
- [x] Deconstruction Agent（从 webnovel-writer 改造）
- [x] Worldbuilding Agent（新写）
- [x] Consistency Agent（新写）
- [x] novel-deconstruct Skill
- [x] novel-worldbuild Skill
- [x] novel-query Skill
- [x] novel-doctor Skill
- [x] 单元测试（CLI / 初始化 / 索引 / 关系图）
- [x] 端到端集成验证通过

Phase 1 之后可以立即使用：
- `/novel-deconstruct` 拆一本参考书
- `/novel-worldbuild` 搭建一个世界观
- `/novel-query` 查询设定
- `/novel-doctor` 检查项目健康
