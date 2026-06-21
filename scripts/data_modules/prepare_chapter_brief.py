"""生成当前章的随机素材、爽点候选和点子候选。"""
import os
import json
import random
import argparse
from datetime import datetime

# 爽点类型池
PLEASURE_TYPES = [
    "实力碾压", "打脸反杀", "财富暴增", "地位跃升",
    "众人震惊", "关系突破", "伏笔回收", "技术突破",
    "智谋取胜", "以弱胜强"
]

# 点子类型池
IDEA_CATEGORIES = [
    "人物关系突转", "新角色登场", "旧设定新用",
    "冲突升级", "意外发现", "代价兑现",
    "能力新应用", "势力博弈", "情感爆发点"
]

def generate_brief(project_root, chapter_num, refresh=False):
    brief_dir = os.path.join(project_root, "变量层", "随机素材")
    brief_path = os.path.join(brief_dir, "current_chapter_brief.md")

    # 不覆盖已有素材（除非强制刷新）
    if os.path.isfile(brief_path) and not refresh:
        print(f"[prepare_chapter_brief] 素材已存在: {brief_path}")
        return brief_path

    os.makedirs(brief_dir, exist_ok=True)

    # 从大纲提取上下文（简化版——实际应解析大纲文件）
    pleasure_candidates = random.sample(PLEASURE_TYPES, min(4, len(PLEASURE_TYPES)))
    idea_candidates = random.sample(IDEA_CATEGORIES, min(3, len(IDEA_CATEGORIES)))

    content = f"""# 第{chapter_num}章 随机素材
> 生成时间: {datetime.now().isoformat()}

## 爽点候选
{chr(10).join(f'- {p}' for p in pleasure_candidates)}

## 点子候选
{chr(10).join(f'- {i}' for i in idea_candidates)}

## 标签候选
根据章节位置和大纲上下文，建议标签：发展 / 爽点 / 打脸

## 密度提示
目标: 4-6 条有效事件, ≥ 8/10
"""
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[prepare_chapter_brief] 已生成: {brief_path}")
    return brief_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    generate_brief(args.project_root, args.chapter, args.refresh)
