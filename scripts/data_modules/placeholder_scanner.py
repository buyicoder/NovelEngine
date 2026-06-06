"""Scan project files for placeholder markers like TODO, TBD, FIXME."""

import os
import re

PLACEHOLDER_PATTERNS = [
    (r"TODO", "todo"), (r"TBD", "tbd"), (r"FIXME", "fixme"),
    (r"XXX", "xxx"), (r"（待补充）", "pending_cn"), (r"待定", "pending_cn"),
]


def scan_file(filepath):
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
