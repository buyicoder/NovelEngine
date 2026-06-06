"""Template management — list, copy, and validate output templates."""

import os


class TemplateManager:
    """Manages output templates located in <plugin_root>/templates/."""

    def __init__(self, plugin_root):
        self.templates_dir = os.path.join(plugin_root, "templates")
        self.genres_dir = os.path.join(self.templates_dir, "genres")
        self.outputs_dir = os.path.join(self.templates_dir, "outputs")

    def list_genres(self):
        if not os.path.isdir(self.genres_dir):
            return []
        return sorted([f.replace(".md", "") for f in os.listdir(self.genres_dir) if f.endswith(".md")])

    def list_output_templates(self):
        if not os.path.isdir(self.outputs_dir):
            return []
        return sorted([f for f in os.listdir(self.outputs_dir) if f.endswith(".md")])

    def get_template_content(self, category, name):
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
