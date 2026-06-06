"""Configuration management for NovelEngine."""

import os
import json

REQUIRED_DIRS = ["设定集", "大纲", "正文/白话剧情", "拆书存档"]
REQUIRED_SYSTEM_DIRS = [".novel"]
REQUIRED_SYSTEM_FILES = [".novel/state.json"]


def resolve_project_root(explicit_root=None):
    if explicit_root:
        return os.path.abspath(explicit_root)
    cwd = os.getcwd()
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
    state_path = os.path.join(project_root, ".novel", "state.json")
    if not os.path.isfile(state_path):
        return {}
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project_state(project_root, state):
    state_dir = os.path.join(project_root, ".novel")
    os.makedirs(state_dir, exist_ok=True)
    state_path = os.path.join(state_dir, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def validate_project_structure(project_root):
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
    state = load_project_state(project_root)
    return state.get("project_info", {}).get("phase", "init")
