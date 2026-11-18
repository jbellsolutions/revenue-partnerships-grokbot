#!/usr/bin/env python3
"""Build a campaign's verified list on the GTM box.

    list_build.py build <campaign>              pull, dedupe, suppress, verify, write
    list_build.py import <campaign> <file.csv>  same, from a list Justin uploaded
    list_build.py prune <campaign>              drop leads the owner rule refuses, here and in PlusVibe
    list_build.py clean <file.csv> [--name N]   a database for no campaign yet: suppressed, one lane, verified, to data/clean
    list_build.py report                        counts only, never a row

Consulti returns only leads it has labelled verified, at 1 prepaid lead credit a row. Every address is then checked again
through Consulti's verifier, 1 prepaid verification credit each, and only `good`, deliverable, non-role, non-catch-all
addresses are kept. Lists are in $GTM_HOME/cold/lists at mode 600 and never go in a note, a commit or a Slack post.

Running build again tops a list up to its target. A saved Consulti list holds everyone already bought, and searches exclude
it, so nobody is paid for twice and nobody lands in two campaigns.
"""
import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
LISTS = HOME / "cold" / "lists"
HERE = Path(__file__).resolve().parent
OVER_PULL = 1.25  # Some rows fail the title check, suppression or verification.
PAGE = 100
MAX_COST = 4  # Credits per row wanted. Past this a pull is buying the same people or the wrong ones.
DAILY_CAP = 3000  # Lead credits a day, all pulls together, unless LEAD_CREDIT_CAP says otherwise. Justin raises it.
WORKERS = 16
API = "https://www.consulti.ai/api/v1"
FIELDS = ["email", "first_name", "last_name", "job_title", "company_name", "company_domain", "city", "state", "country",
          "industry", "annual_revenue", "employees", "linkedin_url", "tier", "source"]
OWNER = re.compile(r"\b(owner|co-?\s?founder|founder|ceo|chief executive|managing director|principal|proprietor|president|"
                   r"managing partner|managing member|partner|broker|director)\b", re.I)
NOT_OWNER = re.compile(r"\b(product owner|account owner|process owner|business owner assistant|vice president|vp|assistant|associate|"
                       r"intern|student|former|retired|director of|sales director|marketing director|regional|branch manager|"
                       r"loan officer|senior partner manager|channel partner|partner manager|deputy)\b", re.I)
# Principal, Director, Partner and Broker are also staff grades: Oracle's principal engineers, a school's principal.
STRONG = re.compile(r"\b(owner|co-?\s?founder|founder|ceo|chief executive|managing director|proprietor|president|managing partner|"
                    r"managing member)\b", re.I)
STAFF = re.compile(r"\b(engineer|engineering|developer|software|product|project|program|programme|scientist|analyst|teacher|school|"
                   r"ict|officer|manager)\b", re.I)
INSTITUTION = re.compile(r"^(primary/secondary education|higher education|government administration|military|judiciary|legislative office|"
                         r"law enforcement|public safety|political organization|international affairs)$", re.I)


def campaigns():
    return json.loads((HERE / "campaigns.json").read_text())


def fits_title(title, industry=""):
    """An owner, not a senior employee whose title shares a word with one."""
    title, industry = title or "", (industry or "").strip()
    if not OWNER.search(title) or NOT_OWNER.search(title) or INSTITUTION.match(industry):
        return False
    if STRONG.search(title):
        return True
    return not STAFF.search(title) and not re.search(r"educat", industry, re.I)


def fits(spec, row):
    return not spec.get("owner_titles") or fits_title(row.get("job_title"), row.get("industry"))


def consulti(*args, timeout=90, tries=4, wait=20):
    """A failed network call on page 40 mustn't throw away the 39 pages already paid for, so transient errors retry."""
    for attempt in range(1, tries + 1):
        try:
            done = subprocess.run(["consulti", *args], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            done = None
        if done and done.returncode == 0:
            data = json.loads(done.stdout)
            return data.get("data", data)
        if attempt == tries:
            raise RuntimeError(f"consulti {args[0]} failed: {(done.stderr.strip() if done else 'timed out')[:200]}")
        time.sleep(wait * attempt)


def api(path, body):
    """Verification is thousands of calls, and starting the CLI for each one would take hours on this computer."""
    key = os.environ.get("CONSULTI_API_KEY", "")
    request = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    return data.get("data", data)


def seen_list(lists=LISTS):
    """The saved Consulti list of everyone already bought. Created once, then seeded from the lists on this computer."""
    path = HOME / "cold" / "consulti-seen.json"
    if path.is_file():
        return json.loads(path.read_text())["id"]
    made = consulti("lists-create", "--name", "gtm-cold-seen", "--kind", "lead")
    found = made.get("id") or (made.get("list") or {}).get("id")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"id": found}))
    emails = []
    for csv_path in lists.glob("*.csv"):
        with csv_path.open(newline="") as handle:
            emails += [row["email"] for row in csv.DictReader(handle)]
    for start in range(0, len(emails), 500):
        mark_seen(found, emails[start:start + 500])
    return found


def mark_seen(list_id, emails):
    if emails:
        consulti("lists-add-leads", list_id, "--body", json.dumps({"emails": emails}))


def expand(search):
    """One search can name several queries or company words. Each becomes its own request."""
    body = dict(search["body"])
    for query in search.get("queries", []):
        yield {**body, "q": query}
    for word in search.get("company", []):
        yield {**body, "company": word}
    if not search.get("queries") and not search.get("company"):
        yield body


def keeps_industry(spec, lead):
    """Some industries mix real trades with factories. There, the company name has to show the trade."""
    rule = spec.get("needs_trade_word")
    if not rule:
        return True
    industry = lead.get("industry") or ""
    if industry in rule.get("drop", []):
        return False
    if industry in rule.get("check", []):
        return bool(re.search(rule["word"], lead.get("company_name") or "", re.I))
    return True


def pull(spec, want, search_fn=None, mark=None, exclude=None):
    """Rows in tier order until enough pass the checks. With a seen list every search stays on page 1, because each batch
    joins that list and leaves the results before the next call. Consulti's own rule for exclusions. The search has to
    name that list in excludeListId: without it page 1 is the same rows, paid for again. A batch with nothing new stops
    the search, and MAX_COST stops the whole pull, so a change on Consulti's side can't run the credits down."""
    search_fn = search_fn or (lambda body: consulti("search", "--body", json.dumps(body)))
    drop = re.compile(spec["drop_company"], re.I) if spec.get("drop_company") else None
    rows, seen = [], set()
    credits = 0
    for search in spec["searches"]:
        for body in expand(search):
            page = 1
            while len(rows) < want:
                request = {**body, "page": 1 if exclude else page, "size": PAGE}
                if exclude:
                    request["excludeListId"] = exclude
                data = search_fn(request)
                leads = data.get("leads") or []
                credits += int(data.get("credits_used") or len(leads))
                if credits > want * MAX_COST:
                    print(f"stopped at {credits} credits for {want} rows wanted, {len(rows)} kept")
                    return rows, credits
                if leads and not any((lead.get("email") or "").strip().lower() not in seen for lead in leads):
                    break
                if mark:
                    mark([(lead.get("email") or "").strip().lower() for lead in leads if lead.get("email")])
                for lead in leads:
                    email = (lead.get("email") or "").strip().lower()
                    if not email or email in seen:
                        continue
                    seen.add(email)
                    if not fits(spec, lead):
                        continue
                    if drop and drop.search(lead.get("company_name") or ""):
                        continue
                    if not keeps_industry(spec, lead):
                        continue
                    rows.append({**{f: lead.get(f, "") for f in FIELDS}, "email": email, "tier": search["tier"], "source": "consulti"})
                if not data.get("has_more") or not leads:
                    break
                page += 1
    return rows, credits


def suppression():
    sys.path.insert(0, str(HOME / "box"))
    sys.path.insert(0, str(HERE.parent / "box"))
    import suppression as module
    return module


def already_used(slug):
    """One lane per person: anyone on another campaign's list stays there."""
    used = set()
    for path in LISTS.glob("*.csv"):
        if path.stem == slug:
            continue
        with path.open(newline="") as handle:
            used |= {row["email"].lower() for row in csv.DictReader(handle)}
    return used


def clear(rows, slug, reason_fn):
    used = already_used(slug)
    kept, held = [], {}
    for row in rows:
        if row["email"] in used:
            held["other campaign"] = held.get("other campaign", 0) + 1
            continue
        reason = reason_fn(f"{row['email']} {row.get('company_domain') or ''}")
        if reason:
            held[reason] = held.get(reason, 0) + 1
            continue
        kept.append(row)
    return kept, held


def passes(result):
    return (result.get("status") == "good" and result.get("is_deliverable") is True and not result.get("is_catch_all")
            and not result.get("is_role_account") and not result.get("is_disposable"))


def verify_one(email):
    for attempt in range(3):
        try:
            return email, api("/verify", {"email": email})
        except (OSError, ValueError, urllib.error.URLError):
            time.sleep(3 * (attempt + 1))
    return email, {"status": "error"}


def verify(rows, check=verify_one, workers=WORKERS):
    kept, counts = [], {}
    by_email = {row["email"]: row for row in rows}
    with cf.ThreadPoolExecutor(workers) as pool:
        for email, result in pool.map(check, list(by_email)):
            if passes(result):
                kept.append(by_email[email])
                counts["good"] = counts.get("good", 0) + 1
            else:
                key = "catch-all" if result.get("is_catch_all") else "role" if result.get("is_role_account") else result.get("status") or "unknown"
                counts[key] = counts.get(key, 0) + 1
    return kept, counts


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    scratch = path.with_suffix(".tmp")
    with os.fdopen(os.open(scratch, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(scratch, path)


def write(slug, rows):
    write_rows(LISTS / f"{slug}.csv", rows)


def spend_path():
    return HOME / "cold" / "credits-spent.json"


def room(day=None):
    """Lead credits left under today's cap. The cap is a safety guard on prepaid credits, set in LEAD_CREDIT_CAP."""
    day = day or dt.date.today().isoformat()
    path = spend_path()
    spent_today = (json.loads(path.read_text()) if path.is_file() else {}).get(day, 0)
    return max(0, int(os.environ.get("LEAD_CREDIT_CAP") or DAILY_CAP) - spent_today)


def spent(credits, day=None):
    day = day or dt.date.today().isoformat()
    path = spend_path()
    data = json.loads(path.read_text()) if path.is_file() else {}
    data = {k: v for k, v in data.items() if k >= (dt.date.fromisoformat(day) - dt.timedelta(days=30)).isoformat()}
    data[day] = data.get(day, 0) + int(credits or 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def record(slug, entry):
    path = HOME / "cold" / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(path.read_text()) if path.is_file() else {}
    manifest[slug] = {**entry, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    path.write_text(json.dumps(manifest, indent=2))


def tiers(rows):
    counts = {}
    for row in rows:
        counts[str(row.get("tier"))] = counts.get(str(row.get("tier")), 0) + 1
    return counts


def finish(slug, spec, rows, credits, source):
    lists = suppression().load()
    if lists is None:
        raise SystemExit("No suppression list on this computer, so nothing was written. Run sync_suppression.sh from the Mac.")
    kept, held = clear(rows, slug, lists.reason)
    good, checks = verify(kept)
    final = existing(slug) + good  # The target is a floor. A verified row past it was paid for and can't be bought again.
    write(slug, final)
    entry = {"source": source, "pulled": len(rows), "held": held, "verification": checks, "verified": len(final),
             "target": spec["target"], "tiers": tiers(final), "lead_credits": credits}
    record(slug, entry)
    print(json.dumps({slug: entry}, indent=2))
    return entry


def existing(slug):
    path = LISTS / f"{slug}.csv"
    if not path.is_file():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def prune(slug, spec, pv=None):
    """Takes leads the owner rule now refuses off a list and out of PlusVibe. They stay on the seen list, so a top-up never buys
    them again. A lead leaves the list only once PlusVibe has stopped it; any it couldn't stop stay for the next run."""
    if pv is None:
        import plusvibe as pv
    rows = existing(slug)
    out = [row for row in rows if not fits(spec, row)]
    stopped, failed = [], []
    for row in out:
        if not pv.ACCEPTED.match(row["email"]):
            stopped.append(row)  # PlusVibe never had it.
            continue
        try:
            pv.stop(row["email"], slug)
            stopped.append(row)
        except pv.Blocked:
            failed.append(row)  # Stays on the list, so a lead still live in PlusVibe is never lost from view. Run prune again.
    gone = {row["email"] for row in stopped}
    keep = [row for row in rows if row["email"] not in gone]
    out = stopped
    if out:
        removed = LISTS / f"{slug}.removed.csv"
        new = not removed.is_file()
        with os.fdopen(os.open(removed, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "a", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
            if new:
                writer.writeheader()
            writer.writerows(out)
        write(slug, keep)
        saved = pv.state()
        done = saved.get("crm_queued", {}).get(slug)
        if done is not None:  # load() queues rows past this count, so it has to count kept rows only, or a top-up skips the CRM.
            pv.save({**saved, "crm_queued": {**saved["crm_queued"], slug: sum(1 for row in rows[:done] if row["email"] not in gone)}})
        path = HOME / "cold" / "manifest.json"
        manifest = json.loads(path.read_text()) if path.is_file() else {}
        entry = manifest.get(slug, {})
        manifest[slug] = {**entry, "verified": len(keep), "pruned": entry.get("pruned", 0) + len(out)}
        path.write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"campaign": slug, "kept": len(keep), "removed": len(out), "failed": len(failed)}))
    return 1 if failed else 0


def clean(path, name=None, limit=None, check=None):
    """A database Justin hands over, for no campaign yet: suppression, one lane and Consulti's verifier, as for a list. The
    good rows go to data/clean/<name>.csv. Each address checked costs one prepaid verification credit."""
    lists = suppression().load()
    if lists is None:
        raise SystemExit("No suppression list on this computer, so nothing was checked. Run sync_suppression.sh from the Mac.")
    rows = read_upload(path)[:limit] if limit else read_upload(path)
    kept, held = clear(rows, "", lists.reason)
    good, checks = verify(kept, check or verify_one)
    name = re.sub(r"[^a-z0-9]+", "-", (name or Path(path).stem).lower()).strip("-") or "upload"
    target = HOME / "data" / "clean" / f"{name}.csv"
    write_rows(target, good)
    result = {"file": str(target), "read": len(rows), "held": held, "verification": checks, "good": len(good)}
    print(json.dumps(result))
    return result


def read_upload(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    out = {}
    for row in rows:
        low = {re.sub(r"[^a-z]", "", k.lower()): (v or "").strip() for k, v in row.items() if k}
        email = (low.get("email") or low.get("emailaddress") or low.get("workemail") or "").lower()
        if "@" not in email or email in out:
            continue
        out[email] = {"email": email, "first_name": low.get("firstname", ""), "last_name": low.get("lastname", ""),
                      "job_title": low.get("title") or low.get("jobtitle", ""), "company_name": low.get("company") or low.get("companyname", ""),
                      "company_domain": low.get("domain") or low.get("website", ""), "city": low.get("city", ""), "state": low.get("state", ""),
                      "country": low.get("country", ""), "industry": low.get("industry", ""), "tier": 0, "source": "upload"}
    return list(out.values())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("campaign")
    i = sub.add_parser("import")
    i.add_argument("campaign")
    i.add_argument("file")
    p = sub.add_parser("prune")
    p.add_argument("campaign")
    c = sub.add_parser("clean")
    c.add_argument("file")
    c.add_argument("--name")
    c.add_argument("--limit", type=int)
    sub.add_parser("report")
    a = ap.parse_args(argv)
    if a.cmd == "report":
        path = HOME / "cold" / "manifest.json"
        print(path.read_text() if path.is_file() else "no lists yet")
        return 0
    if a.cmd == "clean":
        clean(a.file, a.name, a.limit)
        return 0
    spec = campaigns()[a.campaign]
    if a.cmd == "prune":
        return prune(a.campaign, spec)
    if a.cmd == "build":
        short = spec["target"] - len(existing(a.campaign))
        if short <= 0:
            print(f"{a.campaign} is already at its target")
            return 0
        left = room()
        if left <= 0:
            print(json.dumps({"campaign": a.campaign, "stopped": "today's lead credit cap is used", "cap": int(os.environ.get("LEAD_CREDIT_CAP") or DAILY_CAP)}))
            return 1
        list_id = seen_list()
        want = min(int(short * OVER_PULL), max(1, left // MAX_COST))
        rows, credits = pull(spec, want, mark=lambda emails: mark_seen(list_id, emails), exclude=list_id)
        spent(credits)
        finish(a.campaign, spec, rows, credits, "consulti")
    else:
        spec = {**spec, "target": 10 ** 6}
        finish(a.campaign, spec, read_upload(a.file), 0, "upload")
    return 0


if __name__ == "__main__":
    sys.exit(main())
