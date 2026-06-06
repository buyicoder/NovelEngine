"""CLI output formatting utilities."""

import sys


def print_banner(args):
    subcommand = args.get("subcommand", "help")
    project_root = args.get("project_root") or "(auto-detect)"
    print(f"[NovelEngine] subcommand={subcommand} root={project_root}", file=sys.stderr)


def format_success(msg):
    return f"[OK] {msg}"


def format_warning(msg):
    return f"[WARN] {msg}"


def format_error(msg):
    return f"[ERROR] {msg}"


def format_table(headers, rows):
    if not rows:
        return ""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    lines = []
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    for row in rows:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return "\n".join(lines)
