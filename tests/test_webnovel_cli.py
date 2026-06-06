"""Tests for CLI argument parsing and entry point."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_modules.cli_args import parse_args
from data_modules.config import resolve_project_root, validate_project_structure


class TestCliArgs:
    def test_parse_no_args(self):
        args = parse_args([])
        assert args["subcommand"] == "help"
        assert args["project_root"] is None

    def test_parse_subcommand_only(self):
        args = parse_args(["where"])
        assert args["subcommand"] == "where"

    def test_parse_project_root(self):
        args = parse_args(["--project-root", "/tmp/test", "preflight"])
        assert args["subcommand"] == "preflight"
        assert args["project_root"] == "/tmp/test"

    def test_parse_extra_flags(self):
        args = parse_args(["--project-root", "/tmp", "doctor", "--format", "text"])
        assert args["subcommand"] == "doctor"
        assert args["extra"]["format"] == "text"

    def test_parse_positional_args(self):
        args = parse_args(["index", "get-core-entities"])
        assert args["subcommand"] == "index"
        assert args["extra"]["_positional"] == ["get-core-entities"]


class TestConfig:
    def test_resolve_explicit_root(self):
        result = resolve_project_root("/tmp")
        assert result == os.path.abspath("/tmp")

    def test_resolve_nonexistent_returns_cwd(self, monkeypatch):
        monkeypatch.setattr(os, "getcwd", lambda: "/tmp")
        result = resolve_project_root("/nonexistent/path/xyz")
        assert os.path.isabs(result)

    def test_validate_missing_dirs(self, tmp_path):
        issues = validate_project_structure(str(tmp_path))
        assert len(issues) > 0
