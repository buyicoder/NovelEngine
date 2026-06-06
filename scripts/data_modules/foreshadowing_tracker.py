"""Foreshadowing lifecycle tracker — plant, advance, resolve with overdue warnings."""

import os
import json
from datetime import datetime


CREATE_FORESHADOWING_TABLE = """
CREATE TABLE IF NOT EXISTS foreshadowing (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'planted'
        CHECK(status IN ('planted','advanced','resolved','abandoned')),
    planted_chapter INTEGER NOT NULL,
    resolved_chapter INTEGER,
    due_chapter INTEGER,
    tags TEXT DEFAULT '[]',
    related_characters TEXT DEFAULT '[]',
    related_events TEXT DEFAULT '[]',
    history TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT
)
"""

STATUS_FLOW = {
    "planted": ["advanced", "resolved", "abandoned"],
    "advanced": ["advanced", "resolved", "abandoned"],
    "resolved": [],
    "abandoned": [],
}


class ForeshadowingTracker:
    """Tracks foreshadowing lifecycle: plant → advance → resolve."""

    def __init__(self, project_root):
        import sqlite3
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "foreshadowing.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(CREATE_FORESHADOWING_TABLE)

    def plant(self, fid, name, description, chapter, due_chapter=None, tags=None,
              related_characters=None, notes=""):
        """Plant a new foreshadowing at a given chapter."""
        import sqlite3
        now = datetime.now().isoformat()
        history = json.dumps([{"action": "planted", "chapter": chapter, "time": now}])
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO foreshadowing
                   (id, name, description, status, planted_chapter, due_chapter,
                    tags, related_characters, history, notes, created_at, updated_at)
                   VALUES (?, ?, ?, 'planted', ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fid, name, description, chapter, due_chapter,
                 json.dumps(tags or [], ensure_ascii=False),
                 json.dumps(related_characters or [], ensure_ascii=False),
                 history, notes, now, now)
            )

    def advance(self, fid, chapter, note=""):
        """Record a foreshadowing advancement."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT history FROM foreshadowing WHERE id=?", (fid,)).fetchone()
            if not row:
                return False
            history = json.loads(row[0])
            history.append({"action": "advanced", "chapter": chapter, "time": now, "note": note})
            conn.execute(
                "UPDATE foreshadowing SET status='advanced', history=?, updated_at=? WHERE id=?",
                (json.dumps(history, ensure_ascii=False), now, fid)
            )
        return True

    def resolve(self, fid, chapter, note=""):
        """Mark a foreshadowing as resolved."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT history FROM foreshadowing WHERE id=?", (fid,)).fetchone()
            if not row:
                return False
            history = json.loads(row[0])
            history.append({"action": "resolved", "chapter": chapter, "time": now, "note": note})
            conn.execute(
                "UPDATE foreshadowing SET status='resolved', resolved_chapter=?, history=?, updated_at=? WHERE id=?",
                (chapter, json.dumps(history, ensure_ascii=False), now, fid)
            )
        return True

    def abandon(self, fid, reason=""):
        """Abandon a foreshadowing (author decided not to use it)."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT history FROM foreshadowing WHERE id=?", (fid,)).fetchone()
            if not row:
                return False
            history = json.loads(row[0])
            history.append({"action": "abandoned", "time": now, "reason": reason})
            conn.execute(
                "UPDATE foreshadowing SET status='abandoned', history=?, updated_at=? WHERE id=?",
                (json.dumps(history, ensure_ascii=False), now, fid)
            )
        return True

    def get_all(self, status=None):
        """Get all foreshadowings, optionally filtered by status."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            if status:
                rows = conn.execute("SELECT * FROM foreshadowing WHERE status=?", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM foreshadowing").fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_overdue(self, current_chapter):
        """Get foreshadowings that are past their due_chapter and not resolved."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM foreshadowing WHERE status != 'resolved' AND status != 'abandoned' "
                "AND due_chapter IS NOT NULL AND due_chapter < ?",
                (current_chapter,)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_stale(self, current_chapter, stale_threshold=30):
        """Get foreshadowings planted but never advanced for N chapters."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM foreshadowing WHERE status = 'planted' "
                "AND (planted_chapter + ?) < ?",
                (stale_threshold, current_chapter)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_summary(self, current_chapter):
        """Get a summary of foreshadowing health."""
        all_items = self.get_all()
        resolved = [f for f in all_items if f["status"] == "resolved"]
        active = [f for f in all_items if f["status"] in ("planted", "advanced")]
        overdue = self.get_overdue(current_chapter)
        stale = self.get_stale(current_chapter)

        return {
            "total": len(all_items),
            "resolved": len(resolved),
            "active": len(active),
            "overdue": len(overdue),
            "stale": len(stale),
            "overdue_items": overdue,
            "stale_items": stale,
            "health": "good" if not overdue and not stale else "warning" if overdue else "attention",
        }

    def _row_to_dict(self, row):
        return {
            "id": row[0], "name": row[1], "description": row[2], "status": row[3],
            "planted_chapter": row[4], "resolved_chapter": row[5], "due_chapter": row[6],
            "tags": json.loads(row[7]), "related_characters": json.loads(row[8]),
            "related_events": json.loads(row[9]), "history": json.loads(row[10]),
            "notes": row[11], "created_at": row[12], "updated_at": row[13],
        }
