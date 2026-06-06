"""Outline deviation tracker — compare planned outline vs actual writing progress."""

import os
import json
from datetime import datetime


CREATE_DEVIATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS outline_deviations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter INTEGER NOT NULL,
    planned_summary TEXT NOT NULL,
    actual_summary TEXT,
    deviation_type TEXT DEFAULT 'none'
        CHECK(deviation_type IN ('none','minor','major','rewrite')),
    reason TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT
)
"""


class OutlineDeviationTracker:
    """Tracks deviations between planned outline and actual chapter content."""

    def __init__(self, project_root):
        import sqlite3
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "foreshadowing.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_DEVIATIONS_TABLE)

    def register_planned(self, chapter, planned_summary):
        """Register the planned outline for a chapter."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT id FROM outline_deviations WHERE chapter=?", (chapter,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE outline_deviations SET planned_summary=?, updated_at=? WHERE chapter=?",
                    (planned_summary, now, chapter)
                )
            else:
                conn.execute(
                    "INSERT INTO outline_deviations (chapter, planned_summary, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (chapter, planned_summary, now, now)
                )

    def record_actual(self, chapter, actual_summary, deviation_type="none", reason=""):
        """Record what actually happened in this chapter."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT id FROM outline_deviations WHERE chapter=?", (chapter,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE outline_deviations SET actual_summary=?, deviation_type=?, "
                    "reason=?, updated_at=? WHERE chapter=?",
                    (actual_summary, deviation_type, reason, now, chapter)
                )
            else:
                conn.execute(
                    "INSERT INTO outline_deviations (chapter, planned_summary, actual_summary, "
                    "deviation_type, reason, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (chapter, "", actual_summary, deviation_type, reason, now, now)
                )

    def get_deviations(self, min_severity="minor"):
        """Get chapters with deviations at or above given severity."""
        import sqlite3
        levels = {"none": 0, "minor": 1, "major": 2, "rewrite": 3}
        threshold = levels.get(min_severity, 1)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM outline_deviations WHERE deviation_type != 'none'"
            ).fetchall()
        return [
            {
                "chapter": r[1], "planned": r[2], "actual": r[3],
                "deviation_type": r[4], "reason": r[5],
            }
            for r in rows
            if levels.get(r[4], 0) >= threshold
        ]

    def get_chapter_status(self, chapter):
        """Get the outline-vs-actual status for a specific chapter."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM outline_deviations WHERE chapter=?", (chapter,)
            ).fetchone()
        if not row:
            return None
        return {
            "chapter": row[1], "planned": row[2], "actual": row[3],
            "deviation_type": row[4], "reason": row[5],
        }

    def get_summary(self):
        """Get a deviation summary."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT deviation_type, COUNT(*) FROM outline_deviations GROUP BY deviation_type").fetchall()
        counts = {r[0]: r[1] for r in rows}
        total = sum(counts.values())
        major_and_rewrite = counts.get("major", 0) + counts.get("rewrite", 0)
        return {
            "total_chapters": total,
            "on_track": counts.get("none", 0),
            "minor_deviation": counts.get("minor", 0),
            "major_deviation": counts.get("major", 0),
            "rewrite": counts.get("rewrite", 0),
            "health": "good" if major_and_rewrite == 0 else "warning" if major_and_rewrite <= total * 0.1 else "attention",
        }
