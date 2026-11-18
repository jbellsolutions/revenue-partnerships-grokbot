#!/usr/bin/env python3
"""Maildoso from the GTM box: the account, which mailboxes each campaign uses, and pushing them into PlusVibe.

    maildoso.py status              plans, mailboxes, domains, the PlusVibe connection and blocklist hits. Counts only
    maildoso.py plan                every mailbox except the held campaign's senders, shared across the campaigns. No passwords
    maildoso.py prewarmed           pre-warmed domains for sale, with what they cost. Buys nothing

Maildoso's sequencer export only takes Google mailboxes, so its SMTP mailboxes reach PlusVibe with their passwords. Justin
moves them himself, on his Mac: push_mailboxes.py sends them API to API with no file (mailbox_csv.py is the CSV fallback).
Nothing on this computer touches a password. Maildoso's list call returns each one, so accounts() drops that field first.
"""
import collections
import json
import os
from pathlib import Path
import socket
import sys
import time
import urllib.error
import urllib.request

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
HERE = Path(__file__).resolve().parent
API = "https://api.maildoso.com"
PLAN = HOME / "cold" / "mailboxes.json"
KEEP = ("id", "email_account", "domain_id", "status", "is_active", "cancellation_at", "exported_to_sequencers")


class Blocked(Exception):
    """Something this tool can't get past on its own."""


def env(name):
    value = os.environ.get(name, "")
    path = HOME / "box.env"
    for line in path.read_text().splitlines() if not value and path.is_file() else []:
        if line.startswith(name + "="):
            value = line.split("=", 1)[1].strip()
    return value


def call(method, path, body=None, opener=urllib.request.urlopen):
    token = env("MAILDOSO_API_KEY")
    if not token:
        raise Blocked("MAILDOSO_API_KEY isn't on this computer.")
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
    try:
        with opener(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise Blocked(f"Maildoso said {error.code} on {path}: {error.read()[:200].decode(errors='ignore')}")


def accounts(fetch=call):
    """Every mailbox, without its password."""
    out, offset = [], 0
    while True:
        page = fetch("GET", f"/v1/user/accounts-lookup?limit=200&offset={offset}")
        out += [{key: row.get(key) for key in KEEP} for row in page["items"]]
        offset += 200
        if offset >= page["meta"]["total"]:
            return out


def held_campaign_senders():
    """The inboxes the held campaign (INSTANTLY_HELD_CAMPAIGN, set at intake) sends from. A failed read stops the plan,
    so nobody takes one by accident. Unset stops the plan too. A client's setup holds nothing back: new_client.py sets
    INSTANTLY_HELD_CAMPAIGN to none."""
    held = env("INSTANTLY_HELD_CAMPAIGN")
    if not held:
        raise Blocked("INSTANTLY_HELD_CAMPAIGN isn't set (the held campaign's id, or none). Set it at intake.")
    if held == "none":
        return set()
    key = env("INSTANTLY_API_KEY")
    if not key:
        raise Blocked("INSTANTLY_API_KEY is needed to keep the held campaign's inboxes out.")
    request = urllib.request.Request(f"https://api.instantly.ai/api/v2/campaigns/{held}", headers={
        "Authorization": f"Bearer {key}", "User-Agent": "gtm-box/1.0"})
    with urllib.request.urlopen(request, timeout=40) as response:
        return {address.lower() for address in json.load(response).get("email_list", [])}


def listed(domain):
    try:
        return socket.gethostbyname(f"{domain}.multi.surbl.org")
    except OSError:
        return None


def domain_of(row):
    return row["email_account"].split("@")[1].lower()


def choose(rows, held, needs, listed_fn=listed):
    """Clean domains first, then domains the held campaign doesn't send from, then the rest evenly. Each campaign stays on as
    few domains as it can, so one campaign's trouble doesn't spread to another."""
    by_domain = collections.defaultdict(list)
    for row in rows:
        if row["email_account"].lower() not in held and row.get("is_active") and not row.get("cancellation_at"):
            by_domain[domain_of(row)].append(row)
    shared = collections.Counter(address.split("@")[1] for address in held)
    order = sorted(by_domain, key=lambda d: (bool(listed_fn(d)), shared[d], d))
    pool = [row for domain in order for row in sorted(by_domain[domain], key=lambda r: r["email_account"])]
    plan, start = {}, 0
    for slug, count in needs.items():
        plan[slug] = pool[start:start + count]
        start += count
    return plan, {"available": len(pool), "domains_used": len({domain_of(r) for r in pool[:start]}),
                  "clean_domains_used": len({domain_of(r) for r in pool[:start] if not listed_fn(domain_of(r))})}


def needs(available=None):
    """Justin, 2026-11-07: add every inbox and use them while we have them. Each campaign keeps its share of the total,
    and its daily limit stays where he set it, so more inboxes means fewer emails from each one."""
    specs = json.loads((HERE / "campaigns.json").read_text())
    total = sum(spec["inboxes"] for spec in specs.values())
    if available is None:
        return {slug: spec["inboxes"] for slug, spec in specs.items()}
    shares = {slug: available * spec["inboxes"] // total for slug, spec in specs.items()}
    biggest = max(shares, key=shares.get)
    shares[biggest] += available - sum(shares.values())
    return shares


def plan():
    rows, held = accounts(), held_campaign_senders()
    chosen, summary = choose(rows, held, needs(sum(1 for row in rows if row["email_account"].lower() not in held)))
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps({"campaigns": {slug: [row["id"] for row in rows] for slug, rows in chosen.items()},
                                "emails": {slug: [row["email_account"] for row in rows] for slug, rows in chosen.items()},
                                "summary": summary}, indent=2))
    print(json.dumps({**summary, "planned": {slug: len(rows) for slug, rows in chosen.items()}}))


def status():
    rows = accounts()
    domains = {domain_of(row) for row in rows}
    plans = call("GET", "/v1/billing/subscriptions")
    link = [row for row in call("GET", "/v1/sequencers") if row.get("platform") == "plusvibe"]
    print(json.dumps({"mailboxes": len(rows), "domains": len(domains), "on_surbl": sum(1 for d in domains if listed(d)),
                      "plans": [{"name": p.get("name"), "status": p.get("status"), "renews": p.get("renewal_date")} for p in plans],
                      "plusvibe_connected": bool(link and link[0].get("id")), "exported_rows": sum(1 for r in rows if r.get("exported_to_sequencers"))}, indent=2))


def prewarmed():
    print(json.dumps(call("GET", "/v1/user/prewarmed-domains/catalog"))[:1500])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        if argv[:1] == ["status"]:
            status()
        elif argv[:1] == ["plan"]:
            plan()
        elif argv[:1] == ["prewarmed"]:
            prewarmed()
        else:
            print(__doc__)
            return 1
    except Blocked as why:
        print(f"BLOCKED: {why}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
