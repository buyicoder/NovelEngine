"""SQLite-based entity index for characters, factions, locations, items."""

import sqlite3
import os
import json


CREATE_ENTITIES_TABLE = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('character','faction','location','item','concept')),
    aliases TEXT DEFAULT '[]',
    attributes TEXT DEFAULT '{}',
    first_appearance TEXT,
    last_updated TEXT,
    source_file TEXT
)
"""

CREATE_APPEARANCES_TABLE = """
CREATE TABLE IF NOT EXISTS appearances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    role TEXT DEFAULT 'mentioned',
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)
"""


class IndexManager:
    """Manages the entity index stored in .novel/index.db."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "index.db")
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(CREATE_ENTITIES_TABLE)
            conn.execute(CREATE_APPEARANCES_TABLE)

    def upsert_entity(self, entity_id, name, entity_type, aliases=None, attributes=None, source_file=None):
        import datetime
        now = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO entities (id, name, type, aliases, attributes, last_updated, source_file)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (entity_id, name, entity_type, json.dumps(aliases or [], ensure_ascii=False),
                 json.dumps(attributes or {}, ensure_ascii=False), now, source_file)
            )

    def get_entity(self, entity_id):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM entities WHERE id=?", (entity_id,)).fetchone()
        if row:
            return {
                "id": row[0], "name": row[1], "type": row[2],
                "aliases": json.loads(row[3]), "attributes": json.loads(row[4]),
                "first_appearance": row[5], "last_updated": row[6], "source_file": row[7]
            }
        return None

    def search_by_name(self, name_part):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM entities WHERE name LIKE ?", (f"%{name_part}%",)
            ).fetchall()
        return [
            {"id": r[0], "name": r[1], "type": r[2],
             "aliases": json.loads(r[3]), "attributes": json.loads(r[4])}
            for r in rows
        ]

    def get_all_entities(self, entity_type=None):
        with sqlite3.connect(self.db_path) as conn:
            if entity_type:
                rows = conn.execute("SELECT * FROM entities WHERE type=?", (entity_type,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM entities").fetchall()
        return [
            {"id": r[0], "name": r[1], "type": r[2],
             "aliases": json.loads(r[3]), "attributes": json.loads(r[4])}
            for r in rows
        ]
