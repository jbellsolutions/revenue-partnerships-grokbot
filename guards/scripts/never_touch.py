#!/usr/bin/env python3
"""The never-touch guard. Run it before any write to an Orgo computer, a remote box, an agent or an organization.

    python3 never_touch.py check "<target: computer name or id, agent, org, repo>"   prints clear or refused
    python3 never_touch.py status                                                   how many names are loaded, never the names

The names are private and never in this pack. They come from env NEVER_TOUCH (comma-separated) or, failing that,
<workspace>/.secrets/never-touch.txt (one per line, # comments). Justin gives them at intake.

Fails closed: if the list is missing or empty, every check is refused, so no guarded write can run until the list is
in place. Exit 0 means clear, 1 means refused (named on the list), 2 means refused (no list).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ws  # noqa: E402


def load():
    raw = os.environ.get("NEVER_TOUCH", "")
    names = [n.strip() for n in raw.split(",") if n.strip()]
    if names:
        return names
    path = _ws.p(".secrets", "never-touch.txt")
    if path.is_file():
        return [n.strip() for n in path.read_text().splitlines() if n.strip() and not n.lstrip().startswith("#")]
    return []


def check(target):
    names = load()
    if not names:
        return 2, "refused: the never-touch list is missing (set NEVER_TOUCH or .secrets/never-touch.txt at intake)"
    have = _ws.norm(target)
    for name in names:
        want = _ws.norm(name)
        if want and want in have:
            return 1, "refused: the target is on the never-touch list"
    return 0, "clear"


def main(args):
    if len(args) == 2 and args[0] == "check":
        code, line = check(args[1])
        print(line)
        return code
    if args == ["status"]:
        print(f"{len(load())} names loaded" if load() else "no list: every guarded write is refused")
        return 0
    print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
