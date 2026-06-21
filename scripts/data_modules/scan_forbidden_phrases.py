"""扫描正文中的违禁句，输出命中报告。"""
import os
import re
import argparse

# 默认违禁句词表
DEFAULT_FORBIDDEN = [
    # 高优先级 — 写前预判
    (r"不是[^，。；]*是[^，。；]", "不是...是..."),
    (r"不是[^，。；]*而是", "不是...而是..."),
    (r"像是\S", "像是..."),
    (r"仿佛\S", "仿佛..."),
    (r"这句话里", "这句话里"),
    (r"听出了", "听出了"),
    (r"眼里有", "眼里有"),
    (r"第\S+章", "第X章(元叙事)"),
    (r"本章", "本章(元叙事)"),
    # 中优先级 — 写后扫描
    (r"静了一下", "静了一下"),
    (r"顿了顿", "顿了顿"),
    (r"沉默了一下", "沉默了一下"),
    (r"深吸一口气", "深吸一口气"),
    (r"缓缓\S", "缓缓..."),
    (r"不知过了多久", "不知过了多久"),
    (r"就在这时", "就在这时"),
    (r"只见\S", "只见..."),
    (r"只听得", "只听得"),
    # AI高频句式
    (r"似乎\S", "似乎...(模糊表达)"),
    (r"或许\S", "或许...(模糊表达)"),
    (r"也许\S", "也许...(模糊表达)"),
]


def scan_file(filepath, forbidden_path=None):
    if not os.path.isfile(filepath):
        print(f"[scan_forbidden] 文件不存在: {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # 加载自定义词表
    phrases = list(DEFAULT_FORBIDDEN)
    if forbidden_path and os.path.isfile(forbidden_path):
        # 从稳定层/规则/forbidden_phrases.md 加载额外规则
        with open(forbidden_path, "r", encoding="utf-8") as f:
            custom = f.read()
            for line in custom.split("\n"):
                line = line.strip()
                if line.startswith("- `") and line.endswith("`"):
                    phrase = line[3:-1]
                    phrases.append((re.escape(phrase), phrase))

    hits = []
    for pattern, label in phrases:
        matches = re.findall(pattern, text)
        for m in matches:
            # 找上下文
            idx = text.find(m if isinstance(m, str) else m)
            start = max(0, idx - 30)
            end = min(len(text), idx + len(m) + 30)
            ctx = text[start:end].replace("\n", " ")
            hits.append({"label": label, "match": m if isinstance(m, str) else str(m), "context": ctx})

    # 去重
    seen = set()
    unique = []
    for h in hits:
        key = (h["label"], str(h["match"]))
        if key not in seen:
            seen.add(key)
            unique.append(h)

    return unique


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="正文文件路径")
    parser.add_argument("--forbidden", default=None, help="自定义违禁句词表路径")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    # 默认找稳定层/规则/forbidden_phrases.md
    fb_path = args.forbidden
    if not fb_path:
        default_fb = os.path.join(args.project_root, "稳定层", "规则", "forbidden_phrases.md")
        if os.path.isfile(default_fb):
            fb_path = default_fb

    hits = scan_file(args.filepath, fb_path)

    if hits:
        print(f"\n⚠️  违禁句扫描: {len(hits)} 处命中\n")
        for h in hits:
            print(f"  [{h['label']}] ...{h['context']}...")
    else:
        print("\n✅ 违禁句扫描: 0 处命中")
