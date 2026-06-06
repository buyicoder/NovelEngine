"""CLI argument parsing for webnovel.py."""

import sys


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = {"project_root": None, "subcommand": "help", "extra": {}}
    i = 0
    positional = []
    while i < len(argv):
        arg = argv[i]
        if arg == "--project-root" and i + 1 < len(argv):
            i += 1
            args["project_root"] = argv[i]
        elif arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                i += 1
                args["extra"][key] = argv[i]
            else:
                args["extra"][key] = True
        else:
            positional.append(arg)
        i += 1
    if positional:
        args["subcommand"] = positional[0]
        args["extra"]["_positional"] = positional[1:]
    return args
