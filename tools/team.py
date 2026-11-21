#!/usr/bin/env python3
"""The team: the lead agent and one agent per function, and the routines each one runs.

    python3 tools/team.py list [--tier <tier>]      the agents on the tier, their bot names and routine counts
    python3 tools/team.py <agent> [--tier <tier>]   that agent's routines to create (paused), its roles, inboxes and accounts
    python3 tools/team.py --check                   team.json, routines.json, agents.json, tiers.json and team/*.md agree

Reads team.json and routines.json (both written by tools/gen_roles.py) and tiers.json. The tier defaults to
the one in tiers.json. An agent whose function is not on the tier is not created; a core routine it would
have run (the data lane) moves to the lead."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = 50


def load(name):
    return json.load(open(os.path.join(ROOT, name)))


def plan(tier=None):
    """agent id -> the routines it runs on this tier, in routines.json order."""
    t, team = load("tiers.json"), load("team.json")
    tier = tier or t["default"]
    if tier not in t["tiers"]:
        raise SystemExit(f"team.py: no tier '{tier}'. Tiers: {', '.join(t['tiers'])}")
    fns = set(t["tiers"][tier]["functions"])
    out = {a: [] for a in team["agents"] if a == team["lead"] or a in fns}
    for r in load("routines.json")["routines"]:
        if r["function"] != "core" and r["function"] not in fns:
            continue
        out[r["agent"] if r["agent"] in out else team["lead"]].append(r)
    return tier, out


def check():
    team, bad = load("team.json"), []
    agents = team["agents"]
    fns = set(load("agents.json")["agents"])
    if set(agents) != fns | {team["lead"]}:
        bad.append("team.json is not the lead plus the nine functions in agents.json")
    known = {r["routine"]: r for r in load("routines.json")["routines"]}
    listed = [n for a in agents.values() for n in a["routines"]]
    bad += [f"routine '{n}' is on more than one agent" for n in sorted({n for n in listed if listed.count(n) > 1})]
    bad += [f"routine '{n}' is on no agent" for n in sorted(set(known) - set(listed))]
    for aid, a in agents.items():
        bad += [f"agent {aid}: routine '{n}' is not in routines.json" for n in a["routines"] if n not in known]
        bad += [f"agent {aid}: routines.json puts '{n}' on {known[n]['agent']}" for n in a["routines"] if n in known and known[n]["agent"] != aid]
        if not os.path.exists(os.path.join(ROOT, "team", aid + ".md")):
            bad.append(f"team/{aid}.md is missing")
        bad += [f"agent {aid}: no roles/{r}.md" for r in a["roles"] if not os.path.exists(os.path.join(ROOT, "roles", r + ".md"))]
    most = 0
    for tier in load("tiers.json")["tiers"]:
        _, p = plan(tier)
        bad += [f"tier {tier}: agent {a} has no routine" for a, rs in p.items() if not rs]
        bad += [f"tier {tier}: agent {a} has {len(rs)} routines, over the {CAP} a bot allows" for a, rs in p.items() if len(rs) > CAP]
        most = max([most] + [len(rs) for rs in p.values()])
    print("\n".join("FAIL " + b for b in bad) if bad else f"ok: {len(agents)} agents (the lead and {len(agents) - 1} functions), {len(known)} routines, the most on one agent {most} of {CAP}")
    return 1 if bad else 0


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 0
    if a[0] == "--check":
        return check()
    tier, p = plan(a[a.index("--tier") + 1] if "--tier" in a else None)
    team = load("team.json")["agents"]
    if a[0] == "list":
        print(f"Tier {tier}: {len(p)} agents, {sum(len(v) for v in p.values())} routines")
        for aid, rs in p.items():
            print(f"  {aid}: bot \"{team[aid]['bot_name']}\", {len(rs)} routines, roles {', '.join(team[aid]['roles'])}, engine {team[aid]['engine']}")
        left = [x for x in team if x not in p]
        if left:
            print(f"Not created on this tier: {', '.join(left)}")
        return 0
    if a[0] not in team:
        raise SystemExit(f"team.py: no agent '{a[0]}'. Agents: {', '.join(team)}")
    if a[0] not in p:
        print(f"{a[0]} is not on tier {tier}: do not create it."); return 0
    t = team[a[0]]
    print(f"{t['name']} (agent id {a[0]}, bot \"{t['bot_name']}\"), tier {tier}")
    print(f"Set-up page: repo/team/{a[0]}.md")
    print(f"\nCreate these {len(p[a[0]])} routines on this agent, paused:")
    for r in p[a[0]]:
        print(f"  Agent: {a[0]}. Role: {r['role']}. {r['routine']}  ({r.get('cron') or 'event'})")
    print(f"\nReads: {t['reads']}")
    print(f"Accounts: {', '.join(t['accounts'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
