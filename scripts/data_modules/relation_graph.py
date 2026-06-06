"""Simple relation graph manager using SQLite adjacency list."""

import sqlite3
import os


CREATE_RELATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    description TEXT,
    strength INTEGER DEFAULT 5,
    source_file TEXT,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
)
"""


class RelationGraph:
    """Manages entity relationship graph."""

    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, ".novel", "index.db")
        self._init_table()

    def _init_table(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_RELATIONS_TABLE)

    def add_relation(self, source_id, target_id, relation_type, description="", strength=5, source_file=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO relations (source_id, target_id, relation_type, description, strength, source_file)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (source_id, target_id, relation_type, description, strength, source_file)
            )

    def get_relations(self, entity_id):
        with sqlite3.connect(self.db_path) as conn:
            outbound = conn.execute("SELECT * FROM relations WHERE source_id=?", (entity_id,)).fetchall()
            inbound = conn.execute("SELECT * FROM relations WHERE target_id=?", (entity_id,)).fetchall()
        return {
            "outbound": [self._row_to_dict(r) for r in outbound],
            "inbound": [self._row_to_dict(r) for r in inbound],
        }

    def _row_to_dict(self, row):
        return {"id": row[0], "source_id": row[1], "target_id": row[2],
                "relation_type": row[3], "description": row[4],
                "strength": row[5], "source_file": row[6]}
