#!/usr/bin/env python3
"""Spend guard. Run before any paid call, pull, scrape, top-up or plan change.

    spend_guard.py <plan-id> <usd>                 one plan Justin approved
    spend_guard.py <plan-id> <usd> --pool <name>   a run under a standing daily cap
    spend_guard.py today [--pool <name>]           what each pool has spent today (UTC)

Prints approved or held. Exit 0 only for approved. STOP holds everything.

A plan is approved only if context/spend-approvals.md has a line `<plan-id>: approved <cap-usd>` and
<usd> is at or under that cap.

A pool run is approved only if context/spend-approvals.md has a line `pool <name>: daily <cap-usd>`
(Justin's standing yes, with his words beside it) and today's total for the pool plus <usd> stays at or
under the cap. An approved pool run is written to state/spend-ledger.jsonl at once (the full <usd>, as a
reservation), so the cap holds across runs and roles. Pass the provider's quoted worst case as <usd>.

Held means: write the plan with its cost into requests/justin/ and stop."""
import sys, re, json, time, datetime
from _ws import p, stopped


def approvals():
    f = p("context", "spend-approvals.md")
    return f.read_text(errors="ignore").splitlines() if f.exists() else []


def day():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def today_total(pool):
    f = p("state", "spend-ledger.jsonl")
    total = 0.0
    if f.exists():
        for l in f.read_text(errors="ignore").splitlines():
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if r.get("pool") == pool and r.get("day") == day():
                total += float(r.get("usd", 0))
    return total


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return 2
    pool = a[a.index("--pool") + 1] if "--pool" in a else None
    if a[0] == "today":
        import _ws
        if _ws.worker():
            try:
                print("\n".join(_ws.call("GET", "/v1/spend/today").get("today", []))); return 0
            except _ws.WorkerDown as e:
                print(f"unknown: worker unreachable ({e})"); return 1
        names = [pool] if pool else sorted({m.group(1) for l in approvals() for m in [re.match(r"\s*pool\s+(\S+)\s*:", l, re.I)] if m})
        for n in names:
            print(f"{n}: ${today_total(n):.4f} today")
        return 0
    if len(a) < 2:
        print(__doc__); return 2
    pid, usd = a[0], float(a[1])
    import _ws
    if _ws.worker():  # worker mode: the worker holds the pools and the ledger; unreachable means held
        try:
            r = _ws.call("POST", "/v1/spend", {"plan": pid, "usd": usd, "pool": pool})
        except _ws.WorkerDown as e:
            print(f"held: worker unreachable ({e})"); return 1
        print("approved" if r.get("result") == "approved" else "held")
        return 0 if r.get("result") == "approved" else 1
    if stopped() or usd < 0:
        print("held"); return 1
    if pool:
        for l in approvals():
            m = re.match(rf"\s*pool\s+{re.escape(pool)}\s*:\s*daily\s+\$?([0-9.]+)", l, re.I)
            if m and today_total(pool) + usd <= float(m.group(1)) + 1e-9:
                f = p("state", "spend-ledger.jsonl"); f.parent.mkdir(parents=True, exist_ok=True)
                with f.open("a") as h:
                    h.write(json.dumps({"t": int(time.time()), "day": day(), "pool": pool, "plan": pid, "usd": usd}) + "\n")
                print("approved"); return 0
        print("held"); return 1
    for l in approvals():
        m = re.match(rf"\s*{re.escape(pid)}\s*:\s*approved\s+\$?([0-9.]+)", l, re.I)
        if m and usd <= float(m.group(1)):
            print("approved"); return 0
    print("held"); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
