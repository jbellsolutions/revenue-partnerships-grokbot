#!/usr/bin/env python3
"""New Lead Radar leads, judged by the cheap brain. Reads RADAR_APP_URL /api/data with RADAR_DASHBOARD_PASSWORD.
Lead Radar never contacts anyone; neither does this. Only names, links and the judged need reach the digest."""
import json, os, urllib.request
from _common import emit, cursor, think, score


def main():
    url, pw = os.environ.get("RADAR_APP_URL"), os.environ.get("RADAR_DASHBOARD_PASSWORD")
    if not (url and pw):
        emit("radar-poll", "blocked", note="RADAR_APP_URL or RADAR_DASHBOARD_PASSWORD missing"); print("blocked: radar keys missing"); return 1
    req = urllib.request.Request(url.rstrip("/") + "/api/data", headers={"Authorization": f"Bearer {pw}"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except (OSError, ValueError) as e:
        emit("radar-poll", "blocked", note=f"Lead Radar did not answer: {str(e)[:120]}"); print("blocked: radar did not answer"); return 1
    leads = data.get("leads") or []
    seen = set(cursor("radar").get("seen", []))
    fresh = [l for l in leads if str(l.get("id") or l.get("url")) not in seen][:150]
    items = [{"id": str(l.get("id") or l.get("url")), "platform": l.get("platform"), "text": (l.get("text") or l.get("title") or "")[:600]} for l in fresh]
    res, tier = think("lead-fit", items, "radar") if items else ([], "tier none")
    by = {x.get("id"): x for x in (res or [])}
    keep = []
    for l, it in zip(fresh, items):
        j = by.get(it["id"])
        if j is None or score(j) >= 4:
            keep.append({"id": it["id"], "url": l.get("url"), "platform": l.get("platform"), "score": (j or {}).get("score"),
                         "need": (j or {}).get("need", "not judged"), "reply_angle": (j or {}).get("reply_angle", "")})
    emit("radar-poll", "leads", items=keep, counts={"new": len(fresh), "kept": len(keep)}, note=tier)
    cursor("radar", {"seen": sorted(seen | {i["id"] for i in items})[-20000:]})
    print(f"{len(fresh)} new radar leads, {len(keep)} kept; {tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
