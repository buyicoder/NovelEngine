"""Tests for project initialization."""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from init_project import init_book_project, DEFAULT_STATE


class TestInitProject:
    def test_init_creates_state_json(self, tmp_path):
        init_book_project(str(tmp_path), name="测试书", genre="修仙")
        state_path = os.path.join(str(tmp_path), ".novel", "state.json")
        assert os.path.isfile(state_path)
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        assert state["project_info"]["name"] == "测试书"
        assert state["project_info"]["genre"] == "修仙"
        assert state["project_info"]["phase"] == "init"

    def test_init_creates_directories(self, tmp_path):
        init_book_project(str(tmp_path))
        for d in ["设定集", "大纲", "正文/白话剧情", "拆书存档"]:
            assert os.path.isdir(os.path.join(str(tmp_path), d))

    def test_init_raises_if_exists(self, tmp_path):
        init_book_project(str(tmp_path))
        with pytest.raises(FileExistsError):
            init_book_project(str(tmp_path))

    def test_default_state_has_required_keys(self):
        assert "project_info" in DEFAULT_STATE
        assert "settings" in DEFAULT_STATE
        assert "outline" in DEFAULT_STATE
        assert "entity_index" in DEFAULT_STATE
        assert "relation_graph" in DEFAULT_STATE
