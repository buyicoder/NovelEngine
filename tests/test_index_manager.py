"""Tests for IndexManager."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.index_manager import IndexManager


class TestIndexManager:
    def test_init_creates_db(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        assert os.path.isfile(os.path.join(str(tmp_path), ".novel", "index.db"))

    def test_upsert_and_get_entity(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character", aliases=["炎帝"], source_file="设定集/主角卡.md")
        entity = mgr.get_entity("char_001")
        assert entity["name"] == "萧炎"
        assert "炎帝" in entity["aliases"]
        assert entity["type"] == "character"

    def test_search_by_name(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character")
        mgr.upsert_entity("char_002", "萧战", "character")
        results = mgr.search_by_name("萧")
        assert len(results) == 2

    def test_get_all_entities_filtered(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        mgr.upsert_entity("char_001", "萧炎", "character")
        mgr.upsert_entity("fact_001", "云岚宗", "faction")
        chars = mgr.get_all_entities("character")
        assert len(chars) == 1
        assert chars[0]["name"] == "萧炎"

    def test_get_nonexistent(self, tmp_path):
        mgr = IndexManager(str(tmp_path))
        assert mgr.get_entity("nonexistent") is None
