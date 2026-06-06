"""Tests for character tracker."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from data_modules.character_tracker import CharacterTracker


class TestCharacterTracker:
    def test_register_and_appear(self, tmp_path):
        ct = CharacterTracker(str(tmp_path))
        ct.register_character("char_001", "萧炎")
        ct.record_appearance("char_001", 1)
        ct.record_appearance("char_001", 3)
        char = ct.get_character("char_001")
        assert char["total_appearances"] == 2
        assert char["last_appearance_chapter"] == 3

    def test_evolution_record(self, tmp_path):
        ct = CharacterTracker(str(tmp_path))
        ct.register_character("char_001", "萧炎")
        ct.record_evolution("char_001", 10, "变得沉稳", "宗门大比失利")
        history = ct.get_evolution_history("char_001")
        assert len(history) == 1
        assert history[0]["change"] == "变得沉稳"

    def test_missing_detection(self, tmp_path):
        ct = CharacterTracker(str(tmp_path))
        ct.register_character("char_001", "萧炎")
        ct.record_appearance("char_001", 1)
        missing = ct.get_missing_characters(20, absence_threshold=10)
        assert len(missing) == 1
        assert missing[0]["chapters_absent"] == 19

    def test_summary(self, tmp_path):
        ct = CharacterTracker(str(tmp_path))
        ct.register_character("char_001", "萧炎")
        ct.record_appearance("char_001", 1)
        summary = ct.get_summary(20)
        assert summary["total_characters"] == 1
        assert len(summary["missing_warnings"]) == 1
