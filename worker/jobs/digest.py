#!/usr/bin/env python3
"""Fold the jobs' digest records from the last 36 hours into digest/latest.json: counts per job, and the items that
need the bot's judgment, hottest first, capped. This file is the bot's whole view of the volume work."""
import json, time
from _common import HOME

ORDER = {"replies": 0, "leads": 1, "skool": 2, "shows": 3, "blocked": 4, "count": 9}

def main():
    since = time.time() - 36 * 3600
    counts, items, notes = {}, [], {}
    for f in sorted((HOME / "digest" / "inbox").glob("*.jsonl")):
        for l in f.read_text(errors="ignore").splitlines():
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if r.get("t", 0) < since:
                continue
            c = counts.setdefault(r["job"], {})
            for k, v in (r.get("counts") or {}).items():
                c[k] = c.get(k, 0) + (v if isinstance(v, int) else 0)
            if r.get("note"):
                notes[r["job"]] = r["note"]
            for it in r.get("items") or []:
                items.append({"job": r["job"], "kind": r["kind"], "t": r["t"], **it})
    items.sort(key=lambda x: (ORDER.get(x["kind"], 5), -x["t"]))
    out = {"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "window_hours": 36, "counts": counts, "notes": notes,
           "items": items[:400]}
    d = HOME / "digest"; d.mkdir(parents=True, exist_ok=True)
    tmp = d / "latest.tmp"; tmp.write_text(json.dumps(out, ensure_ascii=False)); tmp.replace(d / "latest.json")
    print(f"digest: {len(items)} items across {len(counts)} jobs")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
