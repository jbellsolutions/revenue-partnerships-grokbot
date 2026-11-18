#!/usr/bin/env python3
"""Score new shows or Skool posts with the cheap brain; only 4s and 5s (or anything unjudged) reach the digest.

    score_items.py shows    new cases in gtm-box/speaker/cases/*.json (written by speaker_cycle.py)
    score_items.py skool    new opportunity posts in gtm-box/skool/scrape/posts.json (written by skool_scrape.py)"""
import json, sys
from _common import HOME, emit, cursor, think, score


def shows():
    seen = set(cursor("shows").get("seen", []))
    out = []
    for f in sorted((HOME / "gtm-box" / "speaker" / "cases").glob("*.json")):
        if f.stem in seen:
            continue
        try:
            c = json.loads(f.read_text())
        except ValueError:
            continue
        out.append(({"id": f.stem, "show": str(c.get("name") or c.get("title") or f.stem)[:120],
                     "about": str(c.get("description") or c.get("summary") or "")[:500], "url": c.get("url") or c.get("link")}, f.stem))
    return out, seen, "show-fit"


def skool():
    seen = set(cursor("skool").get("seen", []))
    f = HOME / "gtm-box" / "skool" / "scrape" / "posts.json"
    rows = json.loads(f.read_text()) if f.exists() else []
    out = []
    for r in rows:
        key = f"{r.get('group')}:{r.get('id')}"
        if key in seen or not r.get("isOpportunity"):
            continue
        out.append(({"id": key, "group": r.get("group"), "text": str(r.get("text") or r.get("title") or "")[:600], "url": r.get("url")}, key))
    return out, seen, "lead-fit"


def main(kind):
    rows, seen, prompt = {"shows": shows, "skool": skool}[kind]()
    rows = rows[:150]
    items = [{k: v for k, v in it.items() if k != "url"} for it, _ in rows]
    res, tier = think(prompt, items, kind) if items else ([], "tier none")
    by = {x.get("id"): x for x in (res or [])}
    keep = []
    for it, key in rows:
        j = by.get(it["id"])
        if j is None or score(j) >= 4:
            keep.append({**{k: it[k] for k in it if k in ("id", "show", "group", "url")}, "score": (j or {}).get("score"),
                         "angle": (j or {}).get("angle") or (j or {}).get("reply_angle") or "not judged", "why": (j or {}).get("why") or (j or {}).get("need", "")})
    emit(f"{kind}-score", kind, items=keep, counts={"new": len(rows), "kept": len(keep)}, note=tier)
    cursor(kind, {"seen": sorted(seen | {k for _, k in rows})[-20000:]})
    print(f"{kind}: {len(rows)} new, {len(keep)} kept; {tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "shows"))
