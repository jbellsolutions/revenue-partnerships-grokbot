#!/usr/bin/env python3
"""Hermes job script for `skool`: the daily read of each group's active members and newest posts. No model money.

It replaces the Mac's local Hermes job 950c1000a639, "Daily Lead Pipeline Scrape", which drove the Mac's Chrome with a
copied Skool cookie and wrote ~/skool_members_daily.json and ~/skool_posts_daily.json (paused on the Mac 2026-11-09).
Here it reads through its own tab in the skool Chrome on this box (port 9224), where Justin signs the account in by hand,
so the sign-in never leaves this computer and no token is copied anywhere. It only reads, with GETs to Skool from inside
the signed-in page, at a person's pace.

It writes to the profile's own folder, not a home folder:
    /workspace/revenue-partnerships/gtm-box/skool/scrape/members.json   active in the last 9 days, deduped by Skool user id, with new since last run
    /workspace/revenue-partnerships/gtm-box/skool/scrape/posts.json     each group's newest posts, with the opportunity signals
    /workspace/revenue-partnerships/gtm-box/skool/scrape/<date>/        that day's copy of both

It refuses while STOP is set or before Justin's yes (the file skool/ON), and stops for the day at the first browser check,
403 or 429. A run that reads nothing writes blocked=1, and the Watchdog tells Justin.

    python3 skool_scrape.py           # one run; the last line is the summary
"""
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
import random
import re
import sys
import time

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else Path(__file__).resolve().parent))

import beat  # noqa: E402
import skool_worker  # noqa: E402

# The 13 groups the Mac job read, with the member count it expected.
GROUPS = [
    ("ai-automation-society", 427000), ("learn-ai", 329000), ("skoolers", 163000), ("chase-ai-community", 73000),
    ("robonuggets-free", 59000), ("cliefnotes", 42000), ("aiworkshop-lite", 40000), ("thestrongerhuman", 28000),
    ("brendan", 26000), ("ai-automations-by-kia-7318", 21000), ("ai-automation-agency", 21000),
    ("systems-to-scale-9517", 20000), ("the-ai-automation-circle", 12000),
]
PAGES = 5
ACTIVE_DAYS = 9
STOPS = (403, 429, 202)
SIGNALS = {
    "partnership": ("partner", "partnership", "collab", "affiliate", "referral program"),
    "hiring": ("hiring", "hire", "looking for a va", "contractor", "job opening", "need an expert"),
    "client_acquisition": ("new client", "clients", "client win", "closed a deal", "booked", "revenue", "first client"),
    "help_request": ("help", "stuck", "recommend", "feedback", "looking for advice", "need advice"),
    "commercial_opportunity": ("opportunity", "paid", "commission", "promote", "launch", "offer", "seeking customers"),
}


def out_dir():
    return HOME / "skool" / "scrape"


def first(*values):
    for v in values:
        if v not in (None, ""):
            return v
    return ""


def scalar(value):
    if isinstance(value, dict):
        return first(*(value.get(k) for k in ("url", "value", "href", "link")))
    if isinstance(value, list):
        return first(*(scalar(v) for v in value))
    return value if isinstance(value, (str, int, float)) else ""


def find_link(obj, wanted):
    wanted = wanted.lower().replace("_", "")
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower().replace("_", "") in (wanted, wanted + "url", wanted + "profile") and scalar(value):
                return str(scalar(value))
        for value in obj.values():
            if found := find_link(value, wanted):
                return found
    elif isinstance(obj, list):
        for value in obj:
            if found := find_link(value, wanted):
                return found
    return ""


def seconds(value):
    """Skool's lastOffline in seconds. 0 means online now. Its unit varies, so it's read from the size."""
    if value in (None, ""):
        return None
    try:
        raw = float(value)
    except (TypeError, ValueError):
        try:
            return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    for limit, scale in ((1e17, 1e9), (1e14, 1e6), (1e11, 1e3)):
        if raw > limit:
            return raw / scale
    return raw


def member(user, slug, cutoff):
    if not isinstance(user, dict) or not first(user.get("id"), user.get("userId")):
        return None
    meta = user.get("metadata") if isinstance(user.get("metadata"), dict) else {}
    details = user.get("profile") if isinstance(user.get("profile"), dict) else {}
    seen = seconds(first(meta.get("lastOffline"), user.get("lastOffline"), user.get("last_offline")))
    if seen is None or (seen != 0 and seen < cutoff):
        return None
    name = " ".join(str(x) for x in (user.get("firstName") or "", user.get("lastName") or "") if x)
    website = scalar(first(user.get("website"), meta.get("website"), meta.get("linkWebsite"), details.get("website"),
                           find_link(user, "website"), find_link(user, "linkWebsite")))
    linkedin = scalar(first(user.get("linkedin"), user.get("linkedinUrl"), meta.get("linkLinkedin"), details.get("linkedin"),
                            find_link(user, "linkedin"), find_link(user, "linkLinkedin")))
    return {"id": str(first(user.get("id"), user.get("userId"))),
            "name": str(first(user.get("fullName"), user.get("displayName"), name, user.get("name"))),
            "username": str(first(user.get("username"), user.get("name"))), "website": str(website or ""),
            "linkedin": str(linkedin or ""), "headline": str(first(user.get("headline"), meta.get("bio"), "")),
            "groups": [slug],
            "lastSeenUtc": dt.datetime.fromtimestamp(seen, dt.timezone.utc).isoformat() if seen else "online"}


def next_data(html):
    m = re.search(r'<script\s+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script\s*>', html or "", re.I | re.S)
    try:
        return ((json.loads(m.group(1)).get("props") or {}).get("pageProps") or {}) if m else None
    except ValueError:
        return None


def users(props):
    for key in ("users", "members", "userList"):
        value = props.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for sub in ("users", "members", "items", "results"):
                if isinstance(value.get(sub), list):
                    return value[sub]
    return []


def posts(props, slug):
    rows = []
    for tree in props.get("postTrees") or []:
        post = tree.get("post") if isinstance(tree, dict) and isinstance(tree.get("post"), dict) else tree
        if not isinstance(post, dict) or not post.get("id"):
            continue
        meta = post.get("metadata") if isinstance(post.get("metadata"), dict) else {}
        title = str(first(meta.get("title"), post.get("title"), post.get("name")))
        text = f"{title} {meta.get('content', '')}".lower()
        signals = [k for k, words in SIGNALS.items() if any(w in text for w in words)]
        rows.append({"id": str(post["id"]), "title": title, "userId": str(first(post.get("userId"), "")),
                     "createdAt": first(post.get("createdAt"), meta.get("createdAt")), "group": slug,
                     "url": f"https://www.skool.com/{slug}/{post.get('name') or 'post/' + str(post['id'])}",
                     "signals": signals, "isOpportunity": bool(signals)})
    return rows


def prior_ids(path, key):
    try:
        return {key(r) for r in json.loads(path.read_text()).get("rows", [])}
    except (OSError, ValueError, AttributeError):
        return set()


async def scrape(fetch, groups=GROUPS, now=None, sleep=asyncio.sleep, pace=skool_worker.READ_PACE):
    """fetch(url) gives {status, text, challenge}. Returns (members, posts, groups, stopped)."""
    cutoff = (now or time.time()) - ACTIVE_DAYS * 86400
    found, found_posts, stats, stopped = {}, {}, [], None

    async def get(url):
        await sleep(random.uniform(*pace))
        return await fetch(url)

    for slug, expected in groups:
        stat = {"slug": slug, "expected": expected, "pages": 0, "active": 0, "posts": 0, "status": "ok"}
        stats.append(stat)
        for n in range(1, PAGES + 1):
            got = await get(f"https://www.skool.com/{slug}/-/members?p={n}")
            status = got.get("status")
            if got.get("challenge") or status in STOPS:
                stopped = f"{slug} page {n}: " + ("a browser check" if got.get("challenge") else f"HTTP {status}")
                break
            if "/about" in str(got.get("url", "")):  # Skool shows a group's About page to anyone who isn't a member.
                stat["status"] = "not a member"
                break
            props = next_data(got.get("text")) if status == 200 else None
            if props is None:
                stat["status"] = f"page {n} unreadable (HTTP {status})"
                if "/login" in str(got.get("url", "")):
                    stopped = "signed out: Skool sent the page to its login"
                break
            rows = users(props)
            stat["pages"] += 1
            seen_here = stat.setdefault("_ids", set())
            for row in rows:
                rec = member(row, slug, cutoff)
                if rec:
                    if rec["id"] not in seen_here:
                        seen_here.add(rec["id"])
                        stat["active"] += 1
                    old = found.setdefault(rec["id"], rec)
                    if old is not rec:
                        old["groups"] = sorted(set(old["groups"]) | {slug})
                        for k in ("website", "linkedin", "name"):
                            old[k] = old[k] or rec[k]
            if not rows:
                break
        if stopped:
            stat["status"] = "stopped"
            break
        if stat["status"] == "not a member":
            continue
        got = await get(f"https://www.skool.com/{slug}")
        if got.get("challenge") or got.get("status") in STOPS:
            stopped = f"{slug} posts: " + ("a browser check" if got.get("challenge") else f"HTTP {got.get('status')}")
            stat["status"] = "stopped"
            break
        props = next_data(got.get("text")) if got.get("status") == 200 else None
        for row in posts(props or {}, slug):
            found_posts[(slug, row["id"])] = row
            stat["posts"] += 1
    for stat in stats:
        stat.pop("_ids", None)
    return list(found.values()), list(found_posts.values()), stats, stopped


def save(members, post_rows, stats, stopped, today=None):
    folder = out_dir()
    day = folder / (today or dt.date.today().isoformat())
    day.mkdir(parents=True, exist_ok=True)
    old_m = prior_ids(folder / "members.json", lambda r: r["id"])
    old_p = prior_ids(folder / "posts.json", lambda r: (r["group"], r["id"]))
    for r in members:
        r["new"] = r["id"] not in old_m
    for r in post_rows:
        r["new"] = (r["group"], r["id"]) not in old_p
    at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    counts = {"groups": len(GROUPS), "groupsRead": sum(1 for g in stats if g["pages"] and g.get("status") != "not a member"), "members": len(members),
              "newMembers": sum(r["new"] for r in members),
              "withLinks": sum(1 for r in members if r["website"] or r["linkedin"]), "posts": len(post_rows),
              "newPosts": sum(r["new"] for r in post_rows),
              "newOpportunities": sum(1 for r in post_rows if r["new"] and r["isOpportunity"])}
    for name, rows in (("members.json", members), ("posts.json", post_rows)):
        body = json.dumps({"at": at, "stopped": stopped, "counts": counts, "groups": stats, "rows": rows}, indent=1)
        for target in (folder / name, day / name):
            tmp = target.with_suffix(".tmp")
            tmp.write_text(body)
            tmp.replace(target)
    return counts


def off(home=None):
    home = Path(home or HOME)
    if (home / "STOP").exists():
        return "STOP is set"
    if not (home / "skool" / "ON").exists():
        return "Justin hasn't turned the Skool lane on (skool/ON)"
    return None


async def run(tab=None):
    why = off()
    if why:
        print(f"skipped: {why}")
        return 0
    tab = tab or skool_worker.Tab()

    async def fetch(url):
        got = await tab.call("Runtime.evaluate", {"expression": f"{skool_worker.FETCH}({json.dumps(url)}, 'text/html')",
                                                   "awaitPromise": True, "returnByValue": True}, timeout=90)
        return {} if got.get("exceptionDetails") else ((got.get("result") or {}).get("value") or {})

    try:
        members, post_rows, stats, stopped = await scrape(fetch)
    except (OSError, RuntimeError, asyncio.TimeoutError) as error:
        beat.write("skool", f"Daily scrape: the skool Chrome didn't answer ({error})", ["blocked=1"])
        print(f"blocked: the skool Chrome on 9224 didn't answer: {error}")
        return 1
    finally:
        await tab.reset()
    counts = save(members, post_rows, stats, stopped)
    blocked = counts["groupsRead"] == 0
    outside = [g["slug"] for g in stats if g["status"] == "not a member"]
    line = (f"Daily scrape: {counts['groupsRead']} of {counts['groups']} groups, {counts['members']} active members "
            f"({counts['newMembers']} new, {counts['withLinks']} with a website or LinkedIn), {counts['posts']} posts "
            f"({counts['newOpportunities']} new opportunities)" + (f". Stopped: {stopped}" if stopped else "")
            + (f". Not a member of {len(outside)}: {', '.join(outside)}" if outside else ""))
    beat.write("skool", line, [f"found={counts['newMembers']}", f"blocked={int(blocked)}"])
    print(line)
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
