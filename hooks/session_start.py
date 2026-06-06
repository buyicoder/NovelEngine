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
