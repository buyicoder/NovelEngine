"""Initialize a new book project directory with standard structure."""

import os
import json
import shutil
from datetime import datetime


BOOK_DIRS = [
    # 稳定层 — 不轻易改
    "稳定层/大纲",
    "稳定层/设定集",
    "稳定层/规则",
    # 变量层 — 每章刷新
    "变量层/作者手写库",
    "变量层/随机素材",
    "变量层/情节库",
    "变量层/脚本",
    # 动态层 — AI运行时写入
    "动态层/正文",
    "动态层/白话剧情",
    "动态层/维护",
    "动态层/归档",
    # 导出
    "导出",
    # 引擎内部
    ".novel/backups",
    ".novel/tmp",
]

DEFAULT_STATE = {
    "project_info": {
        "name": "",
        "genre": "",
        "created_at": "",
        "phase": "init",
    },
    "pipeline_version": "2.0",
    "settings": {
        "世界观": {"status": "pending", "file": "稳定层/设定集/世界观.md"},
        "力量体系": {"status": "pending", "file": "稳定层/设定集/力量体系.md"},
        "经济体系": {"status": "pending", "file": "稳定层/设定集/经济体系.md"},
        "势力格局": {"status": "pending", "file": "稳定层/设定集/势力格局.md"},
        "主角卡": {"status": "pending", "file": "稳定层/设定集/主角卡.md"},
        "配角卡": {"status": "pending", "file": "稳定层/设定集/配角卡.md"},
        "反派设计": {"status": "pending", "file": "稳定层/设定集/反派设计.md"},
    },
    "outline": {
        "总纲": {"status": "pending", "file": "稳定层/大纲/总纲.md"},
        "volumes": [],
    },
    "quality": {
        "density_target": 8,
        "pleasure_pool_size": 6,
        "idea_pool_size": 10,
    },
    "deconstruction_archive": [],
    "generated_chapters": [],
    "entity_index": {"last_synced": None},
    "relation_graph": {"last_updated": None},
}


def init_book_project(project_root, name="", genre=""):
    state_path = os.path.join(project_root, ".novel", "state.json")
    if os.path.isfile(state_path):
        raise FileExistsError(f"Project already initialized: {state_path} exists")

    for d in BOOK_DIRS:
        full = os.path.join(project_root, d)
        os.makedirs(full, exist_ok=True)

    state = dict(DEFAULT_STATE)
    state["project_info"]["name"] = name
    state["project_info"]["genre"] = genre
    state["project_info"]["created_at"] = datetime.now().isoformat()

    state_dir = os.path.join(project_root, ".novel")
    os.makedirs(state_dir, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # 复制模板
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    templates_src = os.path.join(plugin_root, "templates", "outputs")
    if os.path.isdir(templates_src):
        _copy_template_if_exists(templates_src, "设定集-世界观.md",
                                 os.path.join(project_root, "稳定层", "设定集", "世界观.md"))
        _copy_template_if_exists(templates_src, "设定集-力量体系.md",
                                 os.path.join(project_root, "稳定层", "设定集", "力量体系.md"))

    # 创建质量模板文件
    _write_quality_templates(project_root)

    print(f"[NovelEngine v2.0] Book project initialized at: {project_root}")
    print(f"  Name: {name or '(untitled)'}")
    print(f"  Genre: {genre or '(unspecified)'}")
    print(f"  Pipeline: 3-layer (stable/variable/dynamic)")


def _write_quality_templates(project_root):
    """写入质量门控模板文件"""
    import stat

    # 密度评分标准
    density_path = os.path.join(project_root, "变量层", "情节库", "density_rubric.md")
    if not os.path.isfile(density_path):
        with open(density_path, "w", encoding="utf-8") as f:
            f.write("""# 章纲密度评分标准

目标：≥ 8/10

## 评分维度
- 有效事件数（4-6条 = 满分）
- 爽点释放（至少1处 = +2）
- 人物关系位移（至少1处 = +1）
- 伏笔推进（至少1处 = +1）
- 信息增量（新设定/新人物/新冲突 = +1）

## 硬边界
- 不许拿气氛描写、停顿、车轱辘对白硬撑事件数
- 不达标不得动笔
""")

    # 违禁句词表
    forbidden_path = os.path.join(project_root, "稳定层", "规则", "forbidden_phrases.md")
    if not os.path.isfile(forbidden_path):
        with open(forbidden_path, "w", encoding="utf-8") as f:
            f.write("""# 违禁句与高危句核

## 写前预判（本章不得主动写出）
- `不是……是……` / `不是……而是……`
- `像是……` / `仿佛……`
- `这句话里` / `听出了` / `眼里有`
- `第X章` / `本章` / `下一章`（元叙事先行）

## 写后硬扫描
- `静了一下` / `顿了顿` / `沉默了一下`
- `深吸一口气` / `缓缓`
- `不知过了多久`
- `就在这时` / `突然`（连续使用）
- `只见` / `只听得`

命中必须改。不是润色——是重写句子。
""")

    # 维护文档模板
    maint_path = os.path.join(project_root, "动态层", "维护", "chapter_maintenance.md")
    if not os.path.isfile(maint_path):
        with open(maint_path, "w", encoding="utf-8") as f:
            f.write("""# 章节维护说明

## 运行态参考
- 【当前时间线】待开始
- 【运行态说明】项目初始化完成

## 轮换检查项池
- 起手骨架：待记录
- 收束方式：待记录
- 叙事距离：待记录
- 意象簇：待记录
- 高频动作：待记录

## 最近章节记录
（每章写完后自动追加）
""")

    # 作者反馈模板
    fb_path = os.path.join(project_root, "动态层", "维护", "author_feedback.md")
    if not os.path.isfile(fb_path):
        with open(fb_path, "w", encoding="utf-8") as f:
            f.write("# 作者反馈\n\n（作者对章节、流程和风格的意见在此记录）\n")

    # 随机素材占位
    brief_dir = os.path.join(project_root, "变量层", "随机素材")
    brief_path = os.path.join(brief_dir, "current_chapter_brief.md")
    if not os.path.isfile(brief_path):
        with open(brief_path, "w", encoding="utf-8") as f:
            f.write("# 当前章随机素材\n\n（由 prepare_chapter_brief.py 生成）\n")


def _copy_template_if_exists(src_dir, filename, dest_path):
    src = os.path.join(src_dir, filename)
    if os.path.isfile(src) and not os.path.isfile(dest_path):
        shutil.copy2(src, dest_path)
