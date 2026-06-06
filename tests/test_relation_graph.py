"""Tests for RelationGraph."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.relation_graph import RelationGraph


class TestRelationGraph:
    def test_add_and_get_relations(self, tmp_path):
        graph = RelationGraph(str(tmp_path))
        graph.add_relation("char_001", "char_002", "师徒", "药老是萧炎的师父", strength=9)
        relations = graph.get_relations("char_001")
        assert len(relations["outbound"]) == 1
        assert relations["outbound"][0]["relation_type"] == "师徒"

    def test_inbound_relations(self, tmp_path):
        graph = RelationGraph(str(tmp_path))
        graph.add_relation("char_001", "char_002", "师徒")
        relations = graph.get_relations("char_002")
        assert len(relations["inbound"]) == 1
        assert relations["inbound"][0]["source_id"] == "char_001"
