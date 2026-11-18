#!/usr/bin/env python3
"""The caller's side of the guarded sender. One file, standard library only: copy it onto the GTM box or into the Factory.

A caller holds exactly two things: SENDER_URL and SENDER_TOKEN. No email, Slack, GHL or Notion key. With them it can
create drafts (Approve off), read where a draft stands, and record an opt-out. It cannot approve or send.

    python3 sender_client.py draft  --client "Acme" --channel email --to ada@acme.test --subject "Hi" --body-file msg.txt
    python3 sender_client.py bundle --client "Acme" --bundle onboarding --file bundle.json
    python3 sender_client.py status <draft id>
    python3 sender_client.py optout ada@acme.test --reason "replied STOP"

bundle.json: {"drafts": [{"channel": "email", "recipient": "...", "subject": "...", "body": "..."}, ...]}
Pass --key so a retry never creates a second draft. Exit codes: 0 ok, 1 refused by the sender (reason printed), 2 unreachable.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


class SenderError(Exception):
    def __init__(self, status, payload):
        super().__init__(f"{status}: {payload}")
        self.status, self.payload = status, payload


def call(method, path, body=None, *, url=None, token=None, key=None, timeout=30):
    url = (url or os.environ.get("SENDER_URL", "")).rstrip("/")
    token = token or os.environ.get("SENDER_TOKEN", "")
    if not url or not token:
        raise SystemExit("set SENDER_URL and SENDER_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "sender-client/1"}
    if key:
        headers["Idempotency-Key"] = key
    req = urllib.request.Request(url + path, method=method, headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read() or b"{}")
        except ValueError:
            payload = {}
        raise SenderError(exc.code, payload) from None


def draft(client, channel, recipient, body, *, bundle="", subject="", type="", key=None, **conn):
    return call("POST", "/v1/drafts", {"client": client, "channel": channel, "recipient": recipient, "body": body,
                                       "bundle": bundle, "subject": subject, "type": type}, key=key, **conn)


def bundle(client, name, drafts, *, type="", key=None, **conn):
    return call("POST", "/v1/bundles", {"client": client, "bundle": name, "type": type, "drafts": drafts}, key=key, **conn)


def status(draft_id, **conn):
    return call("GET", f"/v1/drafts/{draft_id}", **conn)


def optout(value, reason="opted-out", **conn):
    return call("POST", "/v1/optouts", {"value": value, "reason": reason}, **conn)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draft")
    d.add_argument("--client", required=True)
    d.add_argument("--channel", required=True, choices=["email", "slack", "ghl"])
    d.add_argument("--to", required=True)
    d.add_argument("--subject", default="")
    d.add_argument("--body-file", required=True)
    d.add_argument("--bundle", default="")
    d.add_argument("--type", default="")
    d.add_argument("--key")
    b = sub.add_parser("bundle")
    b.add_argument("--client", required=True)
    b.add_argument("--bundle", required=True)
    b.add_argument("--file", required=True)
    b.add_argument("--type", default="")
    b.add_argument("--key")
    s = sub.add_parser("status")
    s.add_argument("draft_id")
    o = sub.add_parser("optout")
    o.add_argument("value")
    o.add_argument("--reason", default="opted-out")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "draft":
            body = open(args.body_file, encoding="utf-8").read()
            out = draft(args.client, args.channel, args.to, body, bundle=args.bundle, subject=args.subject,
                        type=args.type, key=args.key)
        elif args.cmd == "bundle":
            payload = json.load(open(args.file, encoding="utf-8"))
            out = bundle(args.client, args.bundle, payload["drafts"], type=args.type, key=args.key)
        elif args.cmd == "status":
            out = status(args.draft_id)
        else:
            out = optout(args.value, args.reason)
    except SenderError as exc:
        print(json.dumps({"refused": exc.status, **exc.payload}))
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"sender unreachable: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
