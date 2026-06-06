#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NovelEngine CLI 统一入口。

Usage:
    python -X utf8 webnovel.py --project-root <path> <subcommand> [args]
"""

import sys
import os


def main():
    """CLI 主入口，路由到各子命令处理模块。"""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from data_modules.cli_args import parse_args
    from data_modules.cli_output import print_banner

    args = parse_args()
    print_banner(args)

    subcommand = args.get("subcommand", "help")
    routes = {
        "where": _cmd_where,
        "preflight": _cmd_preflight,
        "index": _cmd_index,
        "relations": _cmd_relations,
        "templates": _cmd_templates,
        "deconstruct": _cmd_deconstruct,
        "outline": _cmd_outline,
        "generate": _cmd_generate,
        "archive": _cmd_archive,
        "doctor": _cmd_doctor,
        "init": _cmd_init,
        "help": _cmd_help,
    }

    handler = routes.get(subcommand, _cmd_help)
    handler(args)


def _cmd_where(args):
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    print(root)


def _cmd_preflight(args):
    from data_modules.config import resolve_project_root, validate_project_structure
    root = resolve_project_root(args.get("project_root"))
    issues = validate_project_structure(root)
    if issues:
        for issue in issues:
            print(f"[WARN] {issue}")
        sys.exit(1)
    print(f"[OK] Project at {root} passes preflight.")


def _cmd_index(args):
    print("index subcommand — not yet implemented in Phase 1 core.")


def _cmd_relations(args):
    print("relations subcommand — not yet implemented in Phase 1 core.")


def _cmd_templates(args):
    print("templates subcommand — not yet implemented in Phase 1 core.")


def _cmd_deconstruct(args):
    print("deconstruct subcommand — not yet implemented in Phase 1 core.")


def _cmd_outline(args):
    print("outline subcommand — use /novel-outline skill for interactive planning.")


def _cmd_generate(args):
    print("generate subcommand — use /novel-generate skill for vernacular chapter generation.")


def _cmd_archive(args):
    print("archive subcommand — not yet implemented in Phase 1 core.")


def _cmd_doctor(args):
    from data_modules.doctor import run_doctor
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    report = run_doctor(root)
    print(report)


def _cmd_init(args):
    from init_project import init_book_project
    from data_modules.config import resolve_project_root
    root = resolve_project_root(args.get("project_root"))
    extra = args.get("extra", {})
    name = extra.get("name", extra.get("_positional", [""])[0] if extra.get("_positional") else "")
    genre = extra.get("genre", extra.get("_positional", ["", ""])[1] if len(extra.get("_positional", [])) > 1 else "")
    init_book_project(root, name, genre)


def _cmd_help(args):
    print(__doc__)
    print("Available subcommands:")
    print("  where        Print resolved project root")
    print("  preflight    Run project health preflight")
    print("  doctor       Diagnose project issues")
    print("  init         Initialize new book project")
    print("  outline      Manage story outlines")
    print("  generate     Generate vernacular chapter content")
    print("  index        Entity index management")
    print("  relations    Relation graph management")
    print("  templates    Template management")
    print("  deconstruct  Deconstruction archive management")
    print("  archive      Project backup and archive")


if __name__ == "__main__":
    main()
