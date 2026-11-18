#!/usr/bin/env python3
"""One file, copied into a profile's scripts/ once per job, under that job's name. Hermes runs it, and its name picks the work.

The fast jobs spend no model money. A `no_agent` job is the script alone. A gated job wakes its agent only when there's
something to do: `{"wakeAgent": false}` as the last line of output skips the agent, which is what keeps a check every few
minutes inside the $5 a day guard. Hermes doesn't run preflight for these, so this does: STOP, the gate and the list.
"""
import importlib
import os
import sys
from pathlib import Path

BOX = Path("/workspace/revenue-partnerships/gtm-box/box")
SKIP_AGENT = '{"wakeAgent": false}'
QUIET = 3
KEYS = ("GHL_API_KEY", "GHL_LOCATION_ID", "GHL_API_KEY_FUNDING", "GHL_LOCATION_ID_FUNDING", "PLUSVIBE_API_KEY", "PLUSVIBE_WORKSPACE_ID", "CAL_API_KEY")
# name: (module, arguments, the job wakes an agent, the profile that owns it)
JOBS = {"crm-drain": ("crm", ["drain", "--apply"], False, "closer"),
        "stage-sync": ("crm_stage", ["sync", "--apply"], False, "closer"),
        "open-loops": ("crm_sweep", ["--apply"], False, "closer"),
        "reply-check": ("crm_replies", ["check", "--apply"], True, "replies"),
        "log-sends": ("crm_replies", ["log", "--apply"], False, "replies"),
        "reply-close": ("crm_replies", ["close"], False, "replies"),
        "card-build": ("crm_cards", ["build"], False, "opener"),
        "opener-queue": ("crm_cards", ["queue", "--apply"], True, "opener"),
        "deal-sync": ("deal_ledger", ["sync"], False, "deals"),
        "sender-retry": ("sender_route", ["retry"], False, "closer"),
        "skool-track": ("skool_track", ["run"], False, "skool"),
        "skool-report": ("skool_track", ["report"], False, "skool"),
        "booked-stop": ("booked", ["sweep"], False, "plusvibe-operator")}


STILL_RUNS = {"sender-retry"}  # STOP stops sending. A person's no still has to reach the sender.
KEYS = ("GHL_API_KEY", "GHL_LOCATION_ID", "SENDER_URL", "SENDER_TOKEN")


def load_keys(profile_dir):
    """A script may not get the profile's .env in its environment, so read the two keys the CRM needs from the file itself."""
    env = Path(profile_dir) / ".env"
    if not env.is_file():
        return
    for line in env.read_text().splitlines():
        key, _, value = line.partition("=")
        if key in KEYS and value and not os.environ.get(key):
            os.environ[key] = value.strip()


def run(name, box=BOX, write=print):
    module, args, wakes, owner = JOBS[name]
    sys.path[:0] = [str(box), str(box.parent / "cold")]
    preflight, crm, beat = (importlib.import_module(m) for m in ("preflight", "crm", "beat"))
    beat.HOME = crm.HOME
    checks = [None if name in STILL_RUNS else preflight.stopped(crm.HOME), preflight.suppression_missing(crm.HOME)]
    if wakes:
        checks.append(preflight.gate_down())
    problems = [p for p in checks if p]
    if problems:
        why = "; ".join(problems)
        beat.write(owner, f"{name} skipped: {why}", ["blocked=1"])
        write(f"Skipped: {why}.")
        write(SKIP_AGENT)
        return 0
    code = importlib.import_module(module).main(args)
    if code in (1, 2):
        beat.write(owner, f"{name} couldn't finish: see its job log", ["blocked=1"])
    elif name == "opener-queue":  # A day with no openers wakes no agent, and it still has to show the job ran.
        beat.write(owner, "opener queue checked", [])
    if not wakes or code:  # Quiet, or failed: either way an agent has nothing to do.
        write(SKIP_AGENT)
    return 0


if __name__ == "__main__":
    here = Path(__file__).resolve()
    load_keys(here.parents[1])
    sys.exit(run(here.stem))
