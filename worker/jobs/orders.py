#!/usr/bin/env python3
"""Run the bot's queued orders (orders/<id>.json, written by POST /v1/orders). One at a time, oldest first, through
run_job.py so every order gets the same switches, STOP and approval checks as a scheduled job."""
import json, subprocess, sys
from _common import HOME, PACK

def main():
    for f in sorted((HOME / "orders").glob("*.json"), key=lambda p: p.stat().st_mtime):
        o = json.loads(f.read_text())
        if o.get("status") != "queued":
            continue
        o["status"] = "running"; f.write_text(json.dumps(o))
        params = [f"{k}={v}" for k, v in (o.get("params") or {}).items()]
        r = subprocess.run([sys.executable, str(PACK / "worker" / "run_job.py"), o["type"], "--order", o["id"], *params],
                           capture_output=True, text=True, timeout=7200)
        o["result"] = (r.stdout.strip().splitlines() or [""])[-1][:300]
        # A job that was off, stopped or waiting on an approval exits 0 without running: that is held, never done.
        held = o["result"].startswith(("SKIPPED_OFF", "STOPPED", "HELD"))
        o["status"] = "held" if held else ("done" if r.returncode == 0 else "failed")
        f.write_text(json.dumps(o))
        print(f"order {o['id']} {o['type']}: {o['status']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
