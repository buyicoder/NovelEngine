"""Unified story evolution tracker — combines foreshadowing, character, and outline tracking."""

import os
from data_modules.foreshadowing_tracker import ForeshadowingTracker
from data_modules.character_tracker import CharacterTracker
from data_modules.outline_deviation import OutlineDeviationTracker


class StoryEvolutionTracker:
    """Unified tracker for all story evolution dimensions."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.foreshadowing = ForeshadowingTracker(project_root)
        self.characters = CharacterTracker(project_root)
        self.outline = OutlineDeviationTracker(project_root)

    def get_full_report(self, current_chapter=None):
        """Generate a full story evolution health report."""
        lines = []
        lines.append("=" * 60)
        lines.append("NovelEngine Story Evolution Report")
        lines.append(f"Project: {self.project_root}")
        lines.append(f"Chapter: {current_chapter or 'N/A'}")
        lines.append("=" * 60)

        # Foreshadowing
        fs = self.foreshadowing.get_summary(current_chapter or 9999)
        lines.append(f"\n[伏笔追踪]")
        lines.append(f"  总计: {fs['total']} | 已回收: {fs['resolved']} | 活跃: {fs['active']}")
        lines.append(f"  逾期未回收: {fs['overdue']} | 长期未推进: {fs['stale']}")
        lines.append(f"  健康度: {fs['health']}")
        if fs.get("overdue_items"):
            for item in fs["overdue_items"]:
                lines.append(f"    ⚠️  {item['name']} — 应在第{item['due_chapter']}章回收, 已逾期")
        if fs.get("stale_items"):
            for item in fs["stale_items"]:
                lines.append(f"    ⚠️  {item['name']} — 自第{item['planted_chapter']}章埋设后无推进")

        # Characters
        cs = self.characters.get_summary(current_chapter or 9999)
        lines.append(f"\n[人物追踪]")
        lines.append(f"  总计: {cs['total_characters']} | 活跃: {cs['active']} | 未出场: {cs['dormant']}")
        lines.append(f"  长期缺席: {len(cs['missing_warnings'])} | 出场过密: {len(cs['overexposed_warnings'])}")
        lines.append(f"  健康度: {cs['health']}")
        if cs.get("missing_warnings"):
            for item in cs["missing_warnings"]:
                lines.append(f"    ⚠️  {item['name']} — 已 {item['chapters_absent']} 章未出场")
        if cs.get("overexposed_warnings"):
            for item in cs["overexposed_warnings"]:
                lines.append(f"    ⚠️  {item['name']} — 近{item['window']}章出场{item['recent_appearances']}次, 可能过密")

        # Outline deviations
        od = self.outline.get_summary()
        lines.append(f"\n[大纲偏离追踪]")
        lines.append(f"  已记录章数: {od['total_chapters']} | 按计划: {od['on_track']}")
        lines.append(f"  轻微偏离: {od['minor_deviation']} | 重大偏离: {od['major_deviation']} | 重写: {od['rewrite']}")
        lines.append(f"  健康度: {od['health']}")

        lines.append(f"\n{'=' * 60}")
        return "\n".join(lines)

    def get_warnings_only(self, current_chapter):
        """Get only active warnings."""
        warnings = []

        fs_summary = self.foreshadowing.get_summary(current_chapter)
        for item in fs_summary.get("overdue_items", []):
            warnings.append({
                "type": "foreshadowing_overdue",
                "severity": "P1",
                "message": f"伏笔「{item['name']}」应在第{item['due_chapter']}章回收, 已超期",
            })
        for item in fs_summary.get("stale_items", []):
            warnings.append({
                "type": "foreshadowing_stale",
                "severity": "P1",
                "message": f"伏笔「{item['name']}」自第{item['planted_chapter']}章后无推进",
            })

        cs_summary = self.characters.get_summary(current_chapter)
        for item in cs_summary.get("missing_warnings", []):
            warnings.append({
                "type": "character_missing",
                "severity": "P2",
                "message": f"角色「{item['name']}」已 {item['chapters_absent']} 章未出场",
            })
        for item in cs_summary.get("overexposed_warnings", []):
            warnings.append({
                "type": "character_overexposed",
                "severity": "P2",
                "message": f"角色「{item['name']}」近{item['window']}章出场{item['recent_appearances']}次",
            })

        return warnings
