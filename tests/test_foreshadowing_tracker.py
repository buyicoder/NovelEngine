"""Tests for foreshadowing tracker."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import pytest
from data_modules.foreshadowing_tracker import ForeshadowingTracker


class TestForeshadowingTracker:
    def test_plant_and_get(self, tmp_path):
        ft = ForeshadowingTracker(str(tmp_path))
        ft.plant("fs_001", "神秘戒指", "主角获得神秘戒指", 10, due_chapter=50)
        items = ft.get_all()
        assert len(items) == 1
        assert items[0]["status"] == "planted"
        assert items[0]["due_chapter"] == 50

    def test_advance_and_resolve(self, tmp_path):
        ft = ForeshadowingTracker(str(tmp_path))
        ft.plant("fs_001", "测试伏笔", "描述", 5, due_chapter=20)
        ft.advance("fs_001", 10, note="推进一次")
        ft.resolve("fs_001", 20, note="回收完成")
        item = ft.get_all()[0]
        assert item["status"] == "resolved"
        assert len(item["history"]) == 3

    def test_overdue_detection(self, tmp_path):
        ft = ForeshadowingTracker(str(tmp_path))
        ft.plant("fs_001", "逾期伏笔", "应该在第10章回收", 5, due_chapter=10)
        overdue = ft.get_overdue(15)
        assert len(overdue) == 1
        assert overdue[0]["id"] == "fs_001"

    def test_stale_detection(self, tmp_path):
        ft = ForeshadowingTracker(str(tmp_path))
        ft.plant("fs_001", "陈旧伏笔", "很久没推进", 5)
        stale = ft.get_stale(40, stale_threshold=30)
        assert len(stale) == 1

    def test_summary_health(self, tmp_path):
        ft = ForeshadowingTracker(str(tmp_path))
        ft.plant("fs_001", "正常伏笔", "描述", 5, due_chapter=100)
        ft.plant("fs_002", "逾期伏笔", "已经超了", 5, due_chapter=10)
        summary = ft.get_summary(20)
        assert summary["total"] == 2
        assert summary["overdue"] == 1
        assert summary["health"] == "warning"
