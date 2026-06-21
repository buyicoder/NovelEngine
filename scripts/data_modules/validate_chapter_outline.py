"""章纲密度评分。目标 ≥ 8/10。"""
import os
import re
import argparse


def score_outline(filepath):
    if not os.path.isfile(filepath):
        print(f"[validate_outline] 文件不存在: {filepath}")
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    score = 0
    details = []

    # 1. 有效事件数（核心指标）
    events = re.findall(r'^[-*]\s', text, re.MULTILINE)
    event_count = len(events)
    if event_count >= 6:
        score += 5
        details.append(f"事件数 {event_count} (+5)")
    elif event_count >= 4:
        score += 3
        details.append(f"事件数 {event_count} (+3)")
    elif event_count >= 2:
        score += 1
        details.append(f"事件数 {event_count} (+1)")
    else:
        details.append(f"事件数 {event_count} — 严重不足")

    # 2. 爽点标记
    if re.search(r'爽点|打脸|翻盘|碾压|震惊|收割', text):
        score += 2
        details.append("爽点释放 (+2)")
    else:
        details.append("无爽点标记")

    # 3. 人物关系位移
    if re.search(r'关系|信任|结盟|分裂|离间|靠近|疏远', text):
        score += 1
        details.append("关系位移 (+1)")

    # 4. 伏笔推进
    if re.search(r'伏笔|铺垫|线索|暗线|对照', text):
        score += 1
        details.append("伏笔推进 (+1)")

    # 5. 信息增量
    if re.search(r'新\S{1,3}[人物角色设定|势力|地点|规则|能力|物品]', text):
        score += 1
        details.append("信息增量 (+1)")

    score = min(score, 10)
    return score, details


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    args = parser.parse_args()

    score, details = score_outline(args.filepath)

    status = "✅ 达标" if score >= 8 else "❌ 不达标"
    print(f"\n章纲密度评分: {score}/10 {status}\n")
    for d in details:
        print(f"  {d}")
