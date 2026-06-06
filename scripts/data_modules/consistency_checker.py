"""Consistency checker for cross-file setting validation."""

import os


class ConsistencyChecker:
    """Checks setting files for internal consistency issues."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.settings_dir = os.path.join(project_root, "设定集")

    def check_all(self):
        issues = []
        issues.extend(self._check_files_exist())
        issues.extend(self._check_encoding())
        return issues

    def _check_files_exist(self):
        issues = []
        expected = ["世界观.md", "力量体系.md", "主角卡.md"]
        for f in expected:
            path = os.path.join(self.settings_dir, f)
            if not os.path.isfile(path):
                issues.append({
                    "id": f"FILE-{len(issues)+1:03d}", "severity": "P1", "dimension": "file",
                    "description": f"Missing setting file: {f}", "files_involved": [f],
                    "conflict_detail": f"Expected file not found at {path}",
                    "suggestion": f"Run /novel-worldbuild to create {f}"
                })
        return issues

    def _check_encoding(self):
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
                        "id": f"ENC-{len(issues)+1:03d}", "severity": "P0", "dimension": "encoding",
                        "description": f"File {f} is not valid UTF-8", "files_involved": [f],
                        "conflict_detail": str(e), "suggestion": "Re-save as UTF-8"
                    })
        return issues
