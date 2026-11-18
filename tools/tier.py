#!/usr/bin/env python3
"""Which routines and worker jobs an offer tier gets.

    python3 tools/tier.py list                      the tiers, their prices and functions
    python3 tools/tier.py <tier>                    routines to create, routines left out, worker jobs
    python3 tools/tier.py <tier> --routines-on      the starting context/routines-on.md for that tier (every line off)
    python3 tools/tier.py --check                   tiers.json, routines.json, agents.json and worker/jobs.json agree

Reads tiers.json (tier -> functions), routines.json (routine -> function, written by tools/gen_roles.py),
agents.json (the nine functions) and worker/jobs.json. `core` routines and jobs are on every tier.
A function left out of a tier stays in the pack: adding it later is one line in context/owner.md and the
routines this prints under "left out"."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    return json.load(open(os.path.join(ROOT, name)))


def split(tier):
    t = load("tiers.json")
    if tier not in t["tiers"]:
        raise SystemExit(f"tier.py: no tier '{tier}'. Tiers: {', '.join(t['tiers'])}")
    fns = set(t["tiers"][tier]["functions"]) | {"core"}
    rs = load("routines.json")["routines"]
    jobs = {k: v for k, v in t["worker_jobs"].items() if not k.startswith("_")}
    return ([r for r in rs if r["function"] in fns], [r for r in rs if r["function"] not in fns],
            sorted(j for j, f in jobs.items() if f in fns), sorted(j for j, f in jobs.items() if f not in fns))


def check():
    t, bad = load("tiers.json"), []
    agents = set(load("agents.json")["agents"])
    for name, tier in t["tiers"].items():
        bad += [f"tier {name}: '{f}' is not a function in agents.json" for f in tier["functions"] if f not in agents]
    if t.get("default") not in t["tiers"]:
        bad.append("default tier is not a tier")
    for r in load("routines.json")["routines"]:
        if r["function"] != "core" and r["function"] not in agents:
            bad.append(f"routine '{r['routine']}': function '{r['function']}' is not in agents.json")
    used = {r["function"] for r in load("routines.json")["routines"]}
    bad += [f"function '{a}' has no routine" for a in sorted(agents - used)]
    real = set(load("worker/jobs.json")["jobs"])
    mapped = {k for k in t["worker_jobs"] if not k.startswith("_")}
    bad += [f"worker job '{j}' has no function in tiers.json" for j in sorted(real - mapped)]
    bad += [f"tiers.json names worker job '{j}', which worker/jobs.json does not have" for j in sorted(mapped - real)]
    for j, f in t["worker_jobs"].items():
        if not j.startswith("_") and f != "core" and f not in agents:
            bad.append(f"worker job '{j}': function '{f}' is not in agents.json")
    biggest = max(len(split(n)[0]) for n in t["tiers"])
    if biggest > 50:
        bad.append(f"{biggest} routines is over the 50 a bot allows")
    print("\n".join("FAIL " + b for b in bad) if bad else f"ok: {len(t['tiers'])} tiers, {len(agents)} functions, largest tier {biggest} routines")
    return 1 if bad else 0


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 0
    if a[0] == "--check":
        return check()
    t = load("tiers.json")
    if a[0] == "list":
        for name, tier in t["tiers"].items():
            mark = " (default)" if name == t.get("default") else ""
            print(f"{name}{mark}: {tier['name']}, {tier['price']}\n  functions: {', '.join(tier['functions'])}")
        for name, add in t.get("add_ons", {}).items():
            print(f"add-on {name}: {add['name']}, {add['price']}")
        return 0
    on, off, jobs_on, jobs_off = split(a[0])
    if "--routines-on" in a:
        print(f"# Tier: {a[0]}. Every routine starts off; test or on is set one line at a time.")
        for r in on:
            print(f"{r['routine']}: off")
        print("crm-writes: off")
        return 0
    tier = t["tiers"][a[0]]
    print(f"{tier['name']} ({tier['price']})")
    print(f"\nCreate these {len(on)} routines, paused:")
    for r in on:
        print(f"  [{r['function']}] Role: {r['role']}. {r['routine']}  ({r.get('cron') or 'event'})")
    print(f"\nLeft out on this tier ({len(off)}):")
    for r in off:
        print(f"  [{r['function']}] {r['role']}: {r['routine']}")
    print(f"\nWorker jobs for this tier: {', '.join(jobs_on)}")
    print(f"Worker jobs left off: {', '.join(jobs_off) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
