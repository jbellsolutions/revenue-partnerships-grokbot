#!/usr/bin/env python3
"""Runs before a job's agent starts. Hermes puts this stdout in the prompt, so the agent reads the result before it does anything.

A job that lost a key, its tools or the suppression list must stop and say so. It must not finish with a status of ok and no
work done. That happened on the Funding Officers box: a config re-scan took 34 tools from cron on 2026-11-01, Opus worked
around it through the terminal, Haiku stopped, and Hermes marked every run ok.

    preflight.py                   from a profile's scripts/ folder, where every job runs it
    preflight.py <profile>         from anywhere, naming the profile
    preflight.py --charters        every profile's SOUL.md through Hermes' scan; exits 1 if one wouldn't load

Exits 0 either way, so the agent still starts, reads the failure and stops. The blocked heartbeat is written here, so the
alarm doesn't depend on the agent doing as it's told.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
GATE = os.environ.get("ANTHROPIC_BASE_URL", "http://127.0.0.1:8788")
THREATS = os.environ.get("HERMES_THREATS", "/usr/local/lib/hermes-agent/tools/threat_patterns.py")
SUPPRESSION_DAYS = 7
NO_CONTACT = {"seo-aeo", "content"}  # These reach nobody, so they don't need the list.
TOOLS_LINE = re.compile(r"(\d+) MCP tool\(s\) available")


def profile_dir(argv):
    """A profile's shell has its own HOME and may not see HERMES_HOME, so go by where this file sits."""
    here = Path(__file__).resolve()
    if len(argv) > 1:
        return Path(os.environ.get("HERMES_PROFILES", "/root/.hermes/profiles")) / argv[1]
    return here.parents[1] if here.parent.name == "scripts" else Path(os.environ.get("HERMES_HOME", "."))


def stopped(home=HOME):
    return "STOP is set" if (home / "STOP").exists() else None


def gate_down(url=GATE):
    try:
        urllib.request.urlopen(f"{url}/health", timeout=5)
    except urllib.error.HTTPError:
        return None  # Anything that answers is up. The gate refuses this route on purpose.
    except OSError:
        return "the spend gate isn't answering"
    return None


def suppression_missing(home=HOME):
    return None if (home / "suppression.csv").is_file() else "suppression.csv is missing"


def suppression_old(home=HOME, days=SUPPRESSION_DAYS, when=None):
    """A warning, not a stop: only the Mac can refresh this file today, so stopping on age would stop the working lanes."""
    path = home / "suppression.csv"
    if not path.is_file():
        return None
    age = ((when or time.time()) - path.stat().st_mtime) / 86400
    return f"suppression.csv is {age:.0f} days old, so rerun sync_suppression.sh" if age > days else None


def tools_dropped(log, floor_file):
    """The number of MCP tools a job gets should never fall. Keep the highest seen, and fail when the last line is under it."""
    if not Path(log).is_file():
        return None
    counts = TOOLS_LINE.findall(Path(log).read_text(errors="ignore"))
    if not counts:
        return None
    last = int(counts[-1])
    try:
        floor = json.loads(Path(floor_file).read_text())["floor"]
    except (FileNotFoundError, ValueError, KeyError):
        floor = 0
    if last < floor:
        return f"this profile had {floor} MCP tools and now has {last}: restart the gateway"
    Path(floor_file).write_text(json.dumps({"floor": max(last, floor)}))
    return None


def _scanner(path=THREATS):
    """Hermes' own scan, so this check can't drift from what the agent's load does. None off the box."""
    if not Path(path).is_file():
        return None
    spec = importlib.util.spec_from_file_location("hermes_threat_patterns", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scan_for_threats


def charter_blocked(hermes, scan=None):
    """Hermes drops a profile's whole SOUL.md when its scan hits one line, and the agent runs on with no rules. It only
    logs a warning. That happened to every profile on 2026-11-06, from the words "heartbeat with" in the agent charter."""
    scan = scan or _scanner()
    soul = Path(hermes) / "SOUL.md"
    if scan is None or not soul.is_file():
        return None
    hits = scan(soul.read_text(errors="ignore"), "context")
    return f"Hermes' scan blocks SOUL.md ({', '.join(hits)}), so this agent has no charter" if hits else None


def all_charters(root=None, scan=None):
    """Every profile, for install.sh. Exits 1 if any charter wouldn't load, so a push can't hide it."""
    root = Path(root or os.environ.get("HERMES_PROFILES", "/root/.hermes/profiles"))
    bad = [(p.name, why) for p in sorted(root.iterdir()) if p.is_dir() and (why := charter_blocked(p, scan))]
    for name, why in bad:
        print(f"{name}: {why}")
    print(f"charters: {len(bad)} blocked")
    return 1 if bad else 0


def blocked_beat(profile, why):
    beat = HOME / "box" / "beat.py"
    if beat.is_file():
        subprocess.run([sys.executable, str(beat), "write", profile, f"preflight failed: {why}", "blocked=1"],
                       capture_output=True, timeout=30)


def main(argv=None):
    args = sys.argv if argv is None else argv
    if args[1:] == ["--charters"]:
        return all_charters()
    hermes = profile_dir(args)
    profile = hermes.name
    checks = [stopped(), charter_blocked(hermes), gate_down(),
              tools_dropped(hermes / "logs" / "agent.log", hermes / "mcp-floor.json")]
    if profile not in NO_CONTACT:
        checks.append(suppression_missing())
    problems = [p for p in checks if p]
    if not problems:
        warning = suppression_old() if profile not in NO_CONTACT else None
        print(f"Preflight passed. Warning: {warning}." if warning else "Preflight passed.")
        return 0
    why = "; ".join(problems)
    blocked_beat(profile, why)
    print(f"PREFLIGHT FAILED: {why}. Do no work this run. Your blocked heartbeat is written. Stop here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
