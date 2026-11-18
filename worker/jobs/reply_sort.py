#!/usr/bin/env python3
"""Sort new replies with the cheapest brain. Opt-outs go to suppression at once (protective, no approval needed).
Hot replies (interested, question, referral, angry) go to the digest and, if BOT_REPLY_WEBHOOK_URL is set, wake the
bot's Reply webhook routine with ids only. Everything else is a count. Nothing here sends to a person."""
import json, os, re, urllib.request
from _common import HOME, emit, cursor, guard, think

OPT_OUT = re.compile(r"\b(unsubscribe|remove me|take me off|stop emailing|do not (?:contact|email)|don't (?:contact|email))\b", re.I)


def main():
    box = HOME / "gtm-box" / "cold" / "inbox.jsonl"
    if not box.exists():
        emit("replies-sort", "count", counts={"new": 0}); return 0
    lines = box.read_text(errors="ignore").splitlines()
    c = cursor("reply-sort"); start = c.get("line", 0)
    batch, new = lines[start:start + 200], []   # the cursor counts raw lines, so a blank or broken line can't wedge the job
    for l in batch:
        try:
            r = json.loads(l) if l.strip() else None
        except ValueError:
            r = None
        if isinstance(r, dict):
            new.append(r)
    if not new:
        cursor("reply-sort", {"line": start + len(batch)})
        emit("replies-sort", "count", counts={"new": 0}); return 0
    items, counts, hot = [], {"new": len(new)}, []
    for r in new:
        email = ((r.get("lead") or {}).get("email") if isinstance(r.get("lead"), dict) else r.get("lead")) or ""
        text = f"{r.get('subject') or ''} {r.get('preview') or ''}"
        if OPT_OUT.search(text) and email:
            guard("suppression.py", "add", email, "unsubscribed by reply"); counts["unsubscribe"] = counts.get("unsubscribe", 0) + 1
            continue
        items.append({"id": r.get("id"), "subject": (r.get("subject") or "")[:120], "text": (r.get("preview") or "")[:600]})
    res, tier = think("reply-sort", items, "reply-sort") if items else ([], "tier none")
    by = {x.get("id"): x for x in (res or [])}
    for it in items:
        j = by.get(it["id"])
        intent = str((j or {}).get("intent") or "unjudged")[:20]
        counts[intent] = counts.get(intent, 0) + 1
        if j is None or j.get("hot") or intent in ("interested", "question", "referral", "angry"):
            hot.append({"id": it["id"], "intent": intent, "why": str((j or {}).get("why") or "not judged: needs the bot")[:80]})
    emit("replies-sort", "replies", items=hot, counts=counts, note=tier)
    cursor("reply-sort", {"line": start + len(batch)})
    url = os.environ.get("BOT_REPLY_WEBHOOK_URL")
    if hot and url:
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="POST", data=json.dumps({"hot_reply_ids": [h["id"] for h in hot]}).encode(),
                                                          headers={"Content-Type": "application/json"}), timeout=20)
        except OSError:
            pass  # the bot's Reply check poll still reads the digest
    print(f"{len(new)} replies: {counts}; {tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
