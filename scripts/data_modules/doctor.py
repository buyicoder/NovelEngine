"""Project doctor — diagnose issues and suggest fixes."""

import os
import json
from datetime import datetime


def run_doctor(project_root):
    lines = []
    lines.append("=" * 60)
    lines.append("NovelEngine Doctor Report")
    lines.append(f"Project: {project_root}")
    lines.append(f"Time: {datetime.now().isoformat()}")
    lines.append("=" * 60)

    checks = [_check_state_json, _check_directories, _check_settings_files, _check_outline_files]
    total = passed = warnings = failed = 0

    for check in checks:
        result = check(project_root)
        total += 1
        icon = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}.get(result["status"], "[????]")
        lines.append(f"\n{icon} {result['name']}")
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
    empty_files = [f for f in files if os.path.getsize(os.path.join(settings_dir, f)) < 50]
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
