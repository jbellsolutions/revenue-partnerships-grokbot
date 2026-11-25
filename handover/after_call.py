#!/usr/bin/env python3
"""Take the Operator's "call.followup_ready" post (repo/handover/HANDOVER.md, part 5).

Checks, in order: the switch is on, the signature, the age, a repeat. Then it saves the
post to the person's note and puts one notice in Justin's queue. It sends nothing, rewrites
nothing and never writes the CRM.

  after_call.py take <file> [--signature "sha256=<hex>"] [--workspace DIR] [--settings FILE]
  after_call.py selftest

<file> holds either the post's raw body (pass the X-Hub-Signature-256 value with --signature),
or an envelope {"payload": "<the body as one string>", "signature": "sha256=<hex>"} for a
webhook that does not hand the raw bytes and headers to the agent.

The shared secret is read from the environment (AFTER_CALL_SECRET) or .secrets/after-call
in the workspace. It is never printed or written anywhere.

Exit: 0 saved, 2 bad signature, 3 too old, 4 already taken, 5 switched off, 6 not a post this takes.
"""
import argparse, hashlib, hmac, json, os, re, sys, tempfile, time

MAX_AGE = 600
CODES = {"saved": 0, "bad_signature": 2, "too_old": 3, "repeat": 4, "off": 5, "not_taken": 6}


def sign(secret: bytes, body: bytes) -> str:
    return "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()


def verify(secret: bytes, body: bytes, signature: str) -> bool:
    return bool(signature) and hmac.compare_digest(sign(secret, body), signature.strip())


def secret_for(ws):
    s = os.environ.get("AFTER_CALL_SECRET", "")
    p = os.path.join(ws, ".secrets", "after-call")
    if not s and os.path.exists(p):
        s = open(p).read().strip()
    return s.encode()


def slug(name):
    return re.sub(r"[^A-Za-z0-9 ._-]", "", name or "").strip()[:80]


def note_lines(p):
    call, person, page, crm = p.get("call", {}), p.get("person", {}), p.get("page", {}), p.get("crm", {})
    out = ["", f"## After-call hand-over, call of {call.get('date', '?')} (from the Operator; everything is a draft, nothing sent)", ""]
    if person.get("business"):
        out.append(f"- Business: {person['business']}")
    if person.get("brain_folder"):
        out.append(f"- Single brain: {person['brain_folder']}")
    if page.get("url"):
        out.append(f"- Page: {page['url']} ({page.get('state', '')})")
    for kind, d in (p.get("drafts") or {}).items():
        if d.get("drafted"):
            subj = f" \"{d['subject']}\"" if d.get("subject") else ""
            out.append(f"- Draft, {kind}{subj}: " + "; ".join(d.get("where", [])))
    if crm:
        out.append(f"- CRM ({crm.get('state', '')}, writer: {crm.get('writer', '')}). Stage: {crm.get('stage', '')}")
        if crm.get("note"):
            out.append(f"- CRM note prepared: {crm['note']}")
        for t in crm.get("next_tasks", []):
            out.append(f"- Next: {t.get('what', '')} (due {t.get('due', '?')}, {t.get('owner', '?')})")
    for c in p.get("check_before_sending", []):
        out.append(f"- Check before sending: {c}")
    out.append(f"- Post id: {p.get('id', '')}")
    return out


def take(path, signature, ws, settings, now=None):
    now = now or time.time()
    cfg = json.load(open(settings)).get("after_call", {})
    if not cfg.get("on"):
        return "off", "after_call.on is false in handover.json"
    raw = open(path, "rb").read()
    try:
        env = json.loads(raw)
    except ValueError:
        return "not_taken", "the file is not JSON"
    if isinstance(env, dict) and isinstance(env.get("payload"), str) and "signature" in env:
        body, signature = env["payload"].encode(), env["signature"]
    else:
        body = raw
    secret = secret_for(ws)
    if not secret or not verify(secret, body, signature or ""):
        return "bad_signature", "no secret on this bot" if not secret else "the signature does not match"
    try:
        p = json.loads(body)
    except ValueError:
        return "not_taken", "the signed body is not JSON"
    if p.get("event") != "call.followup_ready" or p.get("to") != "sales-crm" or not p.get("id"):
        return "not_taken", "not a call.followup_ready post for sales-crm"
    if abs(now - float(p.get("sent_at", 0))) > cfg.get("max_age_seconds", MAX_AGE):
        return "too_old", "sent more than the allowed age ago"
    seen_path = os.path.join(ws, "state", "after-call-seen.json")
    seen = json.load(open(seen_path)) if os.path.exists(seen_path) else {}
    if p["id"] in seen:
        return "repeat", "this id was already taken"
    name = slug(p.get("person", {}).get("name"))
    if not name:
        return "not_taken", "no person's name in the post"
    if p.get("test"):
        return "saved", f"test post for {name}: checked, nothing written"
    people = os.path.join(ws, "vault", "People")
    os.makedirs(people, exist_ok=True)
    note = os.path.join(people, name + ".md")
    new = not os.path.exists(note)
    with open(note, "a") as f:
        if new:
            f.write(f"# {name}\n")
        f.write("\n".join(note_lines(p)) + "\n")
    q = os.path.join(ws, "requests", "justin")
    os.makedirs(q, exist_ok=True)
    kinds = [k for k, d in (p.get("drafts") or {}).items() if d.get("drafted")]
    with open(os.path.join(q, f"after-call-{slug(p['id'])}.md"), "w") as f:
        f.write(f"# Ready after your call with {name}\n\nThe Operator made the page and the drafts ({', '.join(kinds) or 'none'}). Nothing was sent and the CRM was not written.\n\n"
                f"- Page: {p.get('page', {}).get('url', 'none')}\n- Where the drafts are: the person's note, vault/People/{name}.md\n\n"
                "Say what you want done (send, change, hold) and it goes to the Operator as a request.\n")
    os.makedirs(os.path.dirname(seen_path), exist_ok=True)
    seen[p["id"]] = int(now)
    json.dump(seen, open(seen_path, "w"))
    return "saved", f"saved to vault/People/{name}.md and Justin's queue"


def selftest():
    ok = 0
    with tempfile.TemporaryDirectory() as ws:
        os.environ["AFTER_CALL_SECRET"] = "selftest-secret"
        st = os.path.join(ws, "h.json")
        post = {"event": "call.followup_ready", "version": 1, "test": False, "id": "T1", "sent_at": 1000, "to": "sales-crm",
                "call": {"date": "2026-01-01"}, "person": {"name": "Pat Example", "business": "Example Co"},
                "page": {"url": "https://example.test/", "state": "unlisted"},
                "drafts": {"email": {"drafted": True, "subject": "Hi", "where": ["x"]}, "text": {"drafted": False}},
                "crm": {"writer": "operator", "state": "prepared, not written", "stage": "Call held", "note": "n"}}
        body = json.dumps(post).encode()
        f = os.path.join(ws, "p.json"); open(f, "wb").write(body)
        e = os.path.join(ws, "e.json"); json.dump({"payload": body.decode(), "signature": sign(b"selftest-secret", body)}, open(e, "w"))
        good = sign(b"selftest-secret", body)
        def case(label, want, on=True, file=f, sig=good, now=1100):
            nonlocal ok
            json.dump({"after_call": {"on": on}}, open(st, "w"))
            got = take(file, sig, ws, st, now)[0]
            print(("ok  " if got == want else "FAIL") + f" {label}: {got}"); ok += got == want
        case("switched off", "off", on=False)
        case("bad signature", "bad_signature", sig="sha256=00")
        case("no signature", "bad_signature", sig=None)
        case("too old", "too_old", now=1000 + 601)
        case("good post saved", "saved")
        case("repeat refused", "repeat")
        note = open(os.path.join(ws, "vault", "People", "Pat Example.md")).read()
        queued = os.path.exists(os.path.join(ws, "requests", "justin", "after-call-T1.md"))
        print(("ok  " if "Draft, email" in note and queued else "FAIL") + " note and queue written"); ok += "Draft, email" in note and queued
        os.remove(os.path.join(ws, "state", "after-call-seen.json"))
        case("envelope form saved", "saved", file=e, sig=None)
    print(f"{ok} of 8 passed")
    return 0 if ok == 8 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("take"); t.add_argument("file"); t.add_argument("--signature")
    t.add_argument("--workspace", default=os.environ.get("WORKSPACE", "/workspace/revenue-partnerships"))
    t.add_argument("--settings")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(selftest())
    settings = a.settings or os.path.join(a.workspace, "context", "functions", "handover.json")
    result, why = take(a.file, a.signature, a.workspace, settings)
    print(json.dumps({"result": result, "why": why}))
    sys.exit(CODES[result])
