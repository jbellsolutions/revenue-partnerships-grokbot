#!/usr/bin/env python3
"""No-model watchdog: alarms Slack (SLACK_ALARM_WEBHOOK_URL) on any bot role silent over 26 hours, any worker job that
failed twice running, and the scrape or model pool spent two days running. One alarm per problem per day."""
import json, os, re, subprocess, sys, time, urllib.request
from _common import HOME, GUARDS, cursor

def post(text):
    url = os.environ.get("SLACK_ALARM_WEBHOOK_URL")
    if url:
        urllib.request.urlopen(urllib.request.Request(url, method="POST", data=json.dumps({"text": text}).encode(),
                                                      headers={"Content-Type": "application/json"}), timeout=20)
    print(text)

def pools_spent():
    """Pools that reached their daily cap both yesterday and the day before: the cap is too small or something loops."""
    f, led = HOME / "context" / "spend-approvals.md", HOME / "state" / "spend-ledger.jsonl"
    caps = {m.group(1): float(m.group(2)) for l in (f.read_text(errors="ignore").splitlines() if f.exists() else [])
            for m in [re.match(r"\s*pool\s+(\S+)\s*:\s*daily\s+\$?([0-9.]+)", l, re.I)] if m}
    days = [time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400 * n)) for n in (0, 1)]
    spent = {}
    for l in (led.read_text(errors="ignore").splitlines() if led.exists() else []):
        try:
            r = json.loads(l); spent[(r.get("pool"), r.get("day"))] = spent.get((r.get("pool"), r.get("day")), 0.0) + float(r.get("usd", 0))
        except (ValueError, TypeError, AttributeError):
            continue
    return [f"POOL SPENT {p}: at its ${cap:g} daily cap two days running" for p, cap in caps.items()
            if cap > 0 and all(spent.get((p, d), 0.0) >= cap - 1e-9 for d in days)]


def main():
    alarms = []
    r = subprocess.run([sys.executable, str(GUARDS / "beat.py"), "status", "--hours", "26"], capture_output=True, text=True)
    alarms += [l for l in r.stdout.splitlines() if l.startswith("SILENT")]
    for f in sorted((HOME / "state" / "jobs").glob("*.jsonl")):
        last = [json.loads(l) for l in f.read_text().splitlines()[-2:] if l.strip()]
        if len(last) == 2 and all(x.get("code") not in (0, None) for x in last):
            alarms.append(f"JOB FAILING {f.stem}: {last[-1].get('tail', '')[:120]}")
    alarms += pools_spent()
    day = time.strftime("%Y-%m-%d", time.gmtime())
    sent = cursor("watchdog"); today = set(sent.get(day, []))
    fresh = [a for a in alarms if a not in today]
    if fresh:
        post("Revenue worker alarms:\n" + "\n".join(fresh[:20]))
    cursor("watchdog", {day: sorted(today | set(fresh))})
    if not alarms:
        print("all quiet")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
