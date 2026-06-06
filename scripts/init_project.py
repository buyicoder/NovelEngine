"""Initialize a new book project directory with standard structure."""

import os
import json
import shutil
from datetime import datetime


BOOK_DIRS = [
    "设定集",
    "大纲",
    "正文/白话剧情",
    "拆书存档",
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
    src = os.path.join(src_dir, filename)
    if os.path.isfile(src) and not os.path.isfile(dest_path):
        shutil.copy2(src, dest_path)
