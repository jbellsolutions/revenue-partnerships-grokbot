#!/usr/bin/env python3
"""The suppression list, and the check a draft passes before it reaches Justin.

  suppression.py check "<show, host, email or url>"   prints clear or held, never the list itself
  suppression.py scan                                 checks SpeakerAgent's drafts and fills Justin's podcast queue
  suppression.py status                               rows by reason, and when the list was synced

The podcast follow-up job runs `scan` before its agent starts, so no draft can skip it. With no list, nothing is queued.
The file is private/suppression.csv on the Mac (build_suppression.py) and suppression.csv in the box's data folder.
"""
import csv
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

BOX_HOME = Path(os.environ.get("GTM_HOME") or "/workspace/revenue-partnerships/gtm-box")
EMAIL = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
HOST = re.compile(r"(?:[a-z0-9-]+\.)+[a-z]{2,}")
CLAIM = re.compile(r"\$\s?\d[\d,.]*\d[kKmM]?|\$\s?\d[kKmM]?|\b\d[\d,.]*\s?%|\b\d+x\b")
LINKEDIN = re.compile(r"linkedin\.com/in/([^/?#\s\"'<>]+)")
OPT_OUTS = "optouts.csv"
SQUASHED_REASONS = ("client", "do-not-contact")  # current-clients.txt: "squashed inside a domain when 6+ letters"


def squash(term):
    return re.sub(r"[^a-z0-9]", "", term)


class Lists:
    def __init__(self, rows):
        self.size = len(rows)
        self.counts = {}
        self.exact, self.domains, self.terms, self.squashed = {}, {}, {}, {}
        for row in rows:
            kind, value, reason = row["kind"], row["value"].strip().lower(), row["reason"]
            self.counts[reason] = self.counts.get(reason, 0) + 1
            if kind in ("email", "linkedin"):
                self.exact[value] = reason
            elif kind == "domain":
                self.domains[value] = reason
            else:
                self.terms[value] = reason
                if reason in SQUASHED_REASONS and len(squash(value)) >= 6:
                    self.squashed[squash(value)] = reason
        names = sorted(self.terms, key=len, reverse=True)
        self.pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, names)) + r")(?!\w)") if names else None

    def reason(self, text):
        """Why this text is held, or None. Returns the reason only, so the list stays out of what an agent reads."""
        text = text.lower()
        for address in EMAIL.findall(text):
            if address in self.exact:
                return self.exact[address]
        for slug in LINKEDIN.findall(text):
            key = "linkedin.com/in/" + slug
            if key in self.exact:
                return self.exact[key]
        for host in HOST.findall(EMAIL.sub(lambda found: found.group().split("@")[1], text)):
            labels = host.split(".")
            for start in range(len(labels) - 1):
                parent = ".".join(labels[start:])
                if parent in self.domains:
                    return self.domains[parent]
            for term, reason in self.squashed.items():
                if term in host.replace("-", ""):
                    return reason
        found = self.pattern.search(text) if self.pattern else None
        return self.terms[found.group(1)] if found else None


def waiting(path=None):
    """The opt-outs the guarded sender hasn't heard yet. On disk before any attempt, so a crash can't lose a STOP."""
    target = Path(path or BOX_HOME / "suppression.csv").parent / "sender-optouts.sqlite3"
    db = sqlite3.connect(target, timeout=30)
    db.execute("CREATE TABLE IF NOT EXISTS pending (value TEXT PRIMARY KEY, reason TEXT NOT NULL, tries INTEGER NOT NULL DEFAULT 0, "
               "why TEXT NOT NULL DEFAULT '', added TEXT NOT NULL)")
    target.chmod(0o600)
    return db


def flush_opt_outs(path=None):
    """Tell the sender everything waiting. A row leaves only when the sender has it. Refused or unreachable, it stays."""
    db = waiting(path)
    rows = db.execute("SELECT value, reason FROM pending ORDER BY added").fetchall()
    if not rows or not (os.environ.get("SENDER_URL", "").strip() and os.environ.get("SENDER_TOKEN", "").strip()):
        return 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sender_client
    told = 0
    for value, reason in rows:
        try:
            sender_client.optout(value, reason, timeout=10)
        except Exception as exc:  # noqa: BLE001  Whatever went wrong here, the person's no is already safe on disk.
            with db:
                db.execute("UPDATE pending SET tries = tries + 1, why = ? WHERE value = ?", (type(exc).__name__, value))
            if not isinstance(exc, sender_client.SenderError):
                break  # It's down. Don't wait out a timeout per row.
            continue
        with db:
            db.execute("DELETE FROM pending WHERE value = ?", (value,))
        told += 1
    return told


def tell_sender(value, reason, path=None):
    """Keep it first, then try. The local opt-out is already written by the time this runs, and this can't undo it."""
    db = waiting(path)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    with db:
        db.execute("INSERT OR IGNORE INTO pending (value, reason, added) VALUES (?, ?, ?)", (value.strip().lower(), reason, stamp))
    try:
        flush_opt_outs(path)
    except Exception:  # noqa: BLE001  The retry job tries again. A no is never lost to a network error.
        pass


def opt_outs_waiting(path=None):
    db = waiting(path)
    count, oldest = db.execute("SELECT COUNT(*), MIN(added) FROM pending").fetchone()
    return {"count": count, "oldest": oldest}


def record_opt_out(value, reason, path=None):
    """Someone said no. Every lane sees it on its next check, and the sync can't overwrite it. Exact identifiers only: a
    bare name would hold everyone who shares it, the way a bare "dave" would hold every Dave on every show. The sender hears
    about it after the local list has it, and a sender that's unset or down leaves it in a durable queue."""
    value = value.strip().lower()
    if "@" in value:
        kind = "email"
    elif "linkedin.com/in/" in value:
        kind, value = "linkedin", "linkedin.com/in/" + value.split("linkedin.com/in/")[1].split("?")[0].strip("/")
    else:
        return False
    overlay = Path(path or BOX_HOME / "suppression.csv").parent / OPT_OUTS
    fresh = not overlay.exists()
    with overlay.open("a", newline="") as handle:
        out = csv.writer(handle)
        if fresh:
            out.writerow(["kind", "value", "reason"])
        out.writerow([kind, value, reason])
    overlay.chmod(0o600)
    tell_sender(value, reason, path)
    return True


def load(path=None):
    path = Path(path or BOX_HOME / "suppression.csv")
    if not path.is_file():
        return None
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return None
    overlay = path.parent / OPT_OUTS  # Written on the box the moment someone says no, because the sync only runs on the Mac.
    if overlay.is_file():
        with overlay.open(newline="") as handle:
            rows += list(csv.DictReader(handle))
    return Lists(rows)


def who(case):
    """Who a pitch would reach: the show, its site, its route and its people. Not the notes, which name other guests."""
    route = case.get("route") or {}
    return " ".join([str(case.get("name") or ""), str(case.get("official_url") or ""), str(route.get("url") or ""),
                     str(route.get("email") or ""), json.dumps(case.get("contacts") or [])])


def card(case, draft):
    route = case.get("route") or {}
    fit = case.get("fit") or {}
    return "\n".join([f"# {case.get('name')}", "", "Nothing has been sent yet. pitch-submit sends it when send_guard.py ready lists it.",
                      f"Why it fits: {fit.get('reason') or 'not recorded'}",
                      f"Best topic: {fit.get('best_topic') or 'not recorded'}",
                      f"Route: {route.get('type') or 'none'} {route.get('url') or route.get('email') or ''}".rstrip(),
                      f"Standing: {case.get('qualification')}", "Suppression list: clear", "", "---", "", draft])


def unapproved(draft, persona):
    """Figures in a pitch that Justin never stated. A draft with one stays out of the queue: no invented results."""
    body = draft.split("Subject:", 1)[-1]
    approved = json.dumps(persona, ensure_ascii=False)
    return [figure for figure in CLAIM.findall(body) if figure not in approved]


def scan(workspace=None, queue=None, path=None):
    workspace = Path(workspace or BOX_HOME / "speaker").resolve()
    queue = Path(queue or BOX_HOME / "queue" / "podcast")
    lists = load(path)
    if lists is None:
        return "SUPPRESSION LIST MISSING. Nothing was queued. Tell gtm-lead, and put no draft in the queue."
    queue.mkdir(parents=True, exist_ok=True)
    persona = json.loads((workspace / "persona.json").read_text()) if (workspace / "persona.json").is_file() else {}
    added, waiting, held, broken = [], 0, [], []
    for file in sorted((workspace / "cases").glob("*.json")):
        case = json.loads(file.read_text())
        draft = case.get("draft") or {}
        # SpeakerAgent writes "drafted" too. Until 2026-11-09 those drafts never reached the queue.
        if not draft.get("path") or draft.get("status") not in ("draft", "drafted", "reviewed"):
            continue
        target = queue / f"{file.stem}.md"
        why = lists.reason(who(case))
        if why:
            held.append({"case_id": file.stem, "show": case.get("name"), "reason": why})
            target.unlink(missing_ok=True)
            continue
        source = (workspace / draft["path"]).resolve()
        if not source.is_relative_to(workspace) or not source.is_file():
            broken.append(file.stem)
            continue
        figures = unapproved(source.read_text(), persona)
        if figures:
            held.append({"case_id": file.stem, "show": case.get("name"),
                         "reason": "a figure Justin hasn't stated: " + ", ".join(figures)})
            target.unlink(missing_ok=True)
            continue
        text = card(case, source.read_text())
        if not target.exists() or target.read_text() != text:
            target.write_text(text)
            added.append(file.stem)
        waiting += 1
    (queue / "held.json").write_text(json.dumps(held, indent=2) + "\n")
    lines = [f"Suppression scan: {waiting} drafts in Justin's queue, {len(added)} new or changed, {len(held)} held back, "
             f"against {lists.size} list rows. The queue is {queue}."]
    lines += [f"Held: {item['show']} ({item['reason']})" for item in held]
    lines += [f"Draft file missing or outside the workspace, not queued: {name}" for name in broken]
    return "\n".join(lines)


def status(path=None):
    path = Path(path or BOX_HOME / "suppression.csv")
    lists = load(path)
    if lists is None:
        return "no list"
    synced = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"{lists.size} rows, synced {synced}: " + ", ".join(f"{k} {v}" for k, v in sorted(lists.counts.items()))


def main(argv):
    if len(argv) == 3 and argv[1] == "check":
        lists = load()
        if lists is None:
            print("no list: hold everything")
            return 2
        why = lists.reason(argv[2])
        print(f"held: {why}" if why else "clear")
        return 1 if why else 0
    if len(argv) == 2 and argv[1] == "scan":
        print(scan())
        return 0
    if len(argv) == 2 and argv[1] == "status":
        print(status())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
