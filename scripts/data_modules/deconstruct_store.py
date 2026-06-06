"""Deconstruction archive management."""

import os
import json


class DeconstructStore:
    """Manages the deconstruction archive at 拆书存档/."""

    def __init__(self, project_root):
        self.archive_dir = os.path.join(project_root, "拆书存档")

    def add_analysis(self, title, analysis_json, report_md):
        safe_title = title.replace("/", "_").replace("\\", "_")
        dir_path = os.path.join(self.archive_dir, safe_title)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "analysis.json"), "w", encoding="utf-8") as f:
            json.dump(analysis_json, f, ensure_ascii=False, indent=2)
        with open(os.path.join(dir_path, "报告.md"), "w", encoding="utf-8") as f:
            f.write(report_md)
        return dir_path

    def list_archives(self):
        if not os.path.isdir(self.archive_dir):
            return []
        result = []
        for name in os.listdir(self.archive_dir):
            analysis_path = os.path.join(self.archive_dir, name, "analysis.json")
            if os.path.isfile(analysis_path):
                with open(analysis_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                result.append({"title": name, "mode": data.get("analysis_mode", "unknown"),
                               "quality": data.get("quality", {}), "source": data.get("source", {})})
        return result

    def get_analysis(self, title):
        safe_title = title.replace("/", "_").replace("\\", "_")
        analysis_path = os.path.join(self.archive_dir, safe_title, "analysis.json")
        if not os.path.isfile(analysis_path):
            return None
        with open(analysis_path, "r", encoding="utf-8") as f:
            return json.load(f)
