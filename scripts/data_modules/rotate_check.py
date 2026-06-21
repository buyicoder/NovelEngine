"""检查当前章与最近5章的轮换项是否重复。"""
import os
import re
import argparse


def check_rotation(project_root, chapter_num):
    maint_path = os.path.join(project_root, "动态层", "维护", "chapter_maintenance.md")
    if not os.path.isfile(maint_path):
        print("[rotate_check] 维护文档不存在，跳过")
        return []

    with open(maint_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 提取最近章节的轮换项
    recent = {}
    chapter_blocks = re.split(r'### 第(\d+)章', text)
    for i in range(1, len(chapter_blocks) - 1, 2):
        ch = int(chapter_blocks[i])
        content = chapter_blocks[i + 1]
        if abs(ch - chapter_num) <= 5 and ch != chapter_num:
            recent[ch] = content

    # 检查重复项
    dimensions = {
        "开头切入": r"开头切入[：:]\s*(.+)",
        "收束方式": r".*收束方式[：:]\s*(.+)",
        "核心意象": r"核心意象[：:]\s*(.+)",
        "高频动作": r"高频动作[：:]\s*(.+)",
    }

    duplicates = []
    for ch, content in sorted(recent.items()):
        for dim, pattern in dimensions.items():
            m = re.search(pattern, content)
            if m:
                value = m.group(1).strip()
                duplicates.append({"chapter": ch, "dimension": dim, "value": value[:80]})

    # 按维度分组
    by_dim = {}
    for d in duplicates:
        key = (d["dimension"], d["value"])
        if key not in by_dim:
            by_dim[key] = []
        by_dim[key].append(d["chapter"])

    # 输出
    repeated = {k: v for k, v in by_dim.items() if len(v) > 1}
    if repeated:
        print(f"\n⚠️  轮换检查: {len(repeated)} 项重复\n")
        for (dim, val), chapters in repeated.items():
            print(f"  [{dim}] \"{val}\" 出现在 第{','.join(map(str,chapters))}章")
    else:
        print("\n✅ 轮换检查: 无重复项")

    return repeated


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    check_rotation(args.project_root, args.chapter)
