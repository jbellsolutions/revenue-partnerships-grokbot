#!/usr/bin/env python3
"""RankSpot for the seo-aeo profile: the article gate and the month's count.

The profile reads and plans through RankSpot's MCP (one server per site, since a key covers one workspace). Writing an
article costs $3, so the MCP tool that does it is left out of the profile's tool list and the only way to write one is
this script, which holds the month's cap. RankSpot's own daily runs (AI visibility prompts, keyword and backlink
updates) bill the prepaid credit directly, so the credit Justin tops up is the hard cap on those.

    python3 rankspot.py status                        # this month's articles and estimate, per site, and each key's check
    python3 rankspot.py generate <site> <action id>   # write one article, if the month's cap allows
    python3 rankspot.py article <site> <article id> <out.html>   # save one article's HTML, for a pull request

Sites: findmemoney (findmemoneyapp.com) and aiguy (truerevenuepartnerships.com). Nothing here publishes: an article is
saved in RankSpot and goes to a site only through a pull request Justin merges. No email tools are used, ever.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("GTM_HOME") or Path.home() / ".gtm-box")
API = "https://api.rankspot.ai/v1"
SITES = {"findmemoney": ("RANKSPOT_KEY_FINDMEMONEY", "findmemoneyapp.com"),
         "aiguy": ("RANKSPOT_API_KEY", "truerevenuepartnerships.com")}
ARTICLE_COST = 3.00
# Articles a month per site. Justin's yes sets these; the env can only lower them.
DEFAULT_CAP = {"findmemoney": 4, "aiguy": 4}


def month(now=None):
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m")


def ledger_path(now=None):
    return HOME / "spend" / f"rankspot-{month(now)}.json"


def read_ledger(now=None):
    path = ledger_path(now)
    return json.loads(path.read_text()) if path.exists() else {"articles": []}


def save_ledger(data, now=None):
    path = ledger_path(now)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def cap(site, env=os.environ):
    raw = env.get(f"RANKSPOT_ARTICLES_{site.upper()}")
    try:
        return min(DEFAULT_CAP[site], int(raw)) if raw not in (None, "") else DEFAULT_CAP[site]
    except ValueError:
        return DEFAULT_CAP[site]


def key(site, env=os.environ):
    if site not in SITES:
        raise ValueError(f"site is one of {', '.join(SITES)}")
    value = env.get(SITES[site][0], "")
    if not value:
        raise RuntimeError(f"{SITES[site][0]} isn't on this box yet")
    return value


def call(method, path, token, body=None, opener=urllib.request.urlopen):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                                          "Accept": "application/json", "User-Agent": "gtm-box-seo-aeo"})
    try:
        with opener(req, timeout=30) as resp:
            text = resp.read().decode()
    except urllib.error.HTTPError as error:
        detail = error.read().decode()[:300]
        raise RuntimeError(f"RankSpot answered {error.code}: {detail}") from None
    return json.loads(text) if text.strip() else {}


def used(site, now=None):
    return sum(1 for a in read_ledger(now)["articles"] if a["site"] == site)


def generate(site, action_id, env=os.environ, opener=urllib.request.urlopen, now=None):
    if (HOME / "STOP").exists():
        return "STOP is set: no article written"
    token = key(site, env)
    if used(site, now) >= cap(site, env):
        return f"cap reached: {used(site, now)} of {cap(site, env)} articles for {site} this month. Nothing written"
    action = call("GET", f"/actions/{action_id}", token, opener=opener)
    action = action.get("data", action)
    if action.get("type") != "write_article" or action.get("status") != "new":
        return f"not written: action {action_id} is {action.get('type')} / {action.get('status')}, and only a new write_article can be"
    call("POST", f"/actions/{action_id}/generate", token, body={}, opener=opener)
    data = read_ledger(now)
    data["articles"].append({"site": site, "action": action_id, "title": action.get("title"),
                             "at": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"), "cost": ARTICLE_COST})
    save_ledger(data, now)
    return (f"article started for {site}: {action.get('title')!r}, {used(site, now)} of {cap(site, env)} this month. "
            "It appears in about 10 minutes; nothing is published")


def article(site, article_id, out, env=os.environ, opener=urllib.request.urlopen):
    got = call("GET", f"/articles/{article_id}", key(site, env), opener=opener)
    got = got.get("data", got)
    html = got.get("contentHtml") or ""
    if not html:
        return f"article {article_id} has no content yet"
    Path(out).write_text(html)
    return f"saved {len(html)} characters of {got.get('title')!r} to {out}"


def status(env=os.environ, opener=urllib.request.urlopen, now=None):
    lines = []
    for site, (name, domain) in SITES.items():
        n = used(site, now)
        line = f"{site} ({domain}): articles {n} of {cap(site, env)} this month, about ${n * ARTICLE_COST:.2f}"
        if not env.get(name):
            line += f"; {name} not set"
        else:
            try:
                ws = call("GET", "/workspace", env[name], opener=opener)
                ws = ws.get("data", ws)
                seen = str(ws.get("domain") or ws.get("website") or "?")
                line += f"; key reads workspace {seen}" + ("" if domain in seen else f", NOT {domain}: check the key")
            except (RuntimeError, OSError) as error:
                line += f"; key check failed: {error}"
        lines.append(line)
    return "\n".join(lines)


def main(argv):
    try:
        if argv[:1] == ["status"]:
            print(status())
        elif argv[:1] == ["generate"] and len(argv) == 3:
            print(generate(argv[1], argv[2]))
        elif argv[:1] == ["article"] and len(argv) == 4:
            print(article(argv[1], argv[2], argv[3]))
        else:
            print(__doc__.strip())
            return 2
    except (ValueError, RuntimeError, OSError) as error:
        print(f"blocked: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
