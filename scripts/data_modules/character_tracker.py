"""Character appearance and evolution tracker."""

import os
import json
from datetime import datetime


CREATE_CHARACTER_TRACKER_TABLE = """
CREATE TABLE IF NOT EXISTS character_tracker (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    appearances TEXT DEFAULT '[]',
    setting_snapshots TEXT DEFAULT '[]',
    current_status TEXT DEFAULT 'active',
    last_appearance_chapter INTEGER,
    total_appearances INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
"""


class CharacterTracker:
    """Tracks character appearances and setting evolution over chapters."""

    def __init__(self, project_root):
        import sqlite3
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "foreshadowing.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_CHARACTER_TRACKER_TABLE)

    def register_character(self, char_id, name):
        """Register a character for tracking."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT id FROM character_tracker WHERE id=?", (char_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO character_tracker (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (char_id, name, now, now)
                )

    def record_appearance(self, char_id, chapter, role="present", scene_note=""):
        """Record a character appearance in a chapter."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT appearances, total_appearances FROM character_tracker WHERE id=?",
                (char_id,)
            ).fetchone()
            if not row:
                return False
            appearances = json.loads(row[0])
            appearances.append({
                "chapter": chapter, "role": role, "scene_note": scene_note, "time": now
            })
            total = row[1] + 1
            conn.execute(
                "UPDATE character_tracker SET appearances=?, last_appearance_chapter=?, "
                "total_appearances=?, updated_at=? WHERE id=?",
                (json.dumps(appearances, ensure_ascii=False), chapter, total, now, char_id)
            )
        return True

    def record_evolution(self, char_id, chapter, change_description, reason_event):
        """Record a character setting change due to story events."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT setting_snapshots FROM character_tracker WHERE id=?",
                (char_id,)
            ).fetchone()
            if not row:
                return False
            snapshots = json.loads(row[0])
            snapshots.append({
                "chapter": chapter,
                "change": change_description,
                "reason": reason_event,
                "time": now,
            })
            conn.execute(
                "UPDATE character_tracker SET setting_snapshots=?, updated_at=? WHERE id=?",
                (json.dumps(snapshots, ensure_ascii=False), now, char_id)
            )
        return True

    def get_character(self, char_id):
        """Get full character tracking data."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM character_tracker WHERE id=?", (char_id,)
            ).fetchone()
        if not row:
            return None
        return {
            "id": row[0], "name": row[1],
            "appearances": json.loads(row[2]),
            "setting_snapshots": json.loads(row[3]),
            "current_status": row[4],
            "last_appearance_chapter": row[5],
            "total_appearances": row[6],
            "created_at": row[7], "updated_at": row[8],
        }

    def get_missing_characters(self, current_chapter, absence_threshold=15):
        """Get characters who haven't appeared for N chapters."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, name, last_appearance_chapter, total_appearances "
                "FROM character_tracker WHERE last_appearance_chapter IS NOT NULL "
                "AND (? - last_appearance_chapter) > ? AND total_appearances > 0",
                (current_chapter, absence_threshold)
            ).fetchall()
        return [
            {
                "id": r[0], "name": r[1],
                "last_chapter": r[2],
                "chapters_absent": current_chapter - r[2],
                "total_appearances": r[3],
            }
            for r in rows
        ]

    def get_overexposed(self, recent_window=5, appearance_min=4):
        """Get characters appearing too frequently in recent chapters."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, name, appearances FROM character_tracker").fetchall()
        overexposed = []
        for r in rows:
            appearances = json.loads(r[2])
            if not appearances:
                continue
            max_ch = max(a["chapter"] for a in appearances)
            recent = [a for a in appearances if a["chapter"] > max_ch - recent_window]
            if len(recent) >= appearance_min:
                overexposed.append({
                    "id": r[0], "name": r[1],
                    "recent_appearances": len(recent),
                    "window": recent_window,
                })
        return overexposed

    def get_evolution_history(self, char_id):
        """Get the full evolution history for a character."""
        char = self.get_character(char_id)
        if not char:
            return []
        return char["setting_snapshots"]

    def get_all_characters(self):
        """List all tracked characters."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, name, current_status, last_appearance_chapter, total_appearances FROM character_tracker"
            ).fetchall()
        return [
            {"id": r[0], "name": r[1], "status": r[2],
             "last_chapter": r[3], "appearances": r[4]}
            for r in rows
        ]

    def get_summary(self, current_chapter):
        """Get character tracking summary with warnings."""
        missing = self.get_missing_characters(current_chapter)
        overexposed = self.get_overexposed()
        all_chars = self.get_all_characters()

        return {
            "total_characters": len(all_chars),
            "active": sum(1 for c in all_chars if c["appearances"] > 0),
            "dormant": sum(1 for c in all_chars if c["appearances"] == 0),
            "missing_warnings": missing,
            "overexposed_warnings": overexposed,
            "health": "good" if not missing and not overexposed else "warning",
        }
