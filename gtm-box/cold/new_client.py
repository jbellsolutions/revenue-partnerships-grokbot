#!/usr/bin/env python3
"""Sets up this whole cold email system for a client, in its own folder, from nothing of ours.

    new_client.py <client> --out <folder> [--campaign <slug>]...

The folder gets the tools, a blank campaign file and copy file for each campaign, a key file to fill, and the runbook.
It takes no list, no state, no lead and no key of ours. Run each tool from that folder with GTM_HOME set to it, so the
client's data stays there. TEMPLATE.md is the runbook.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
TOOLS = ("plusvibe.py", "maildoso.py", "warmup.py", "list_build.py", "crm_sync.py", "booked.py", "mailbox_csv.py", "push_mailboxes.py")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
KEYS = """# Every key here is the client's own. Mode 600. Never commit this file.
PLUSVIBE_API_KEY=
PLUSVIBE_WORKSPACE_ID=
MAILDOSO_API_KEY=
CONSULTI_API_KEY=
GHL_API_KEY=
GHL_LOCATION_ID=
# No campaign of ours to keep out of the plan.
INSTANTLY_HELD_CAMPAIGN=none
"""


def campaign(slug):
    return {"name": slug.replace("-", " ").title(), "timezone": "America/New_York", "hours": ["09:00", "17:00"], "business_type": "",
            "inboxes": 100, "per_day": 1000, "steps": 3, "target": 7300, "crm": "ai-guy", "offer": "",
            "owner_titles": True, "searches": [{"tier": 1, "note": "Who this campaign is for", "body": {"countries": [], "industries": [], "empMax": 50}}]}


def blank_copy(slug):
    step = {"variation": "A", "subject": "", "body": "{{first_name}},\n\n\n\n{{sender_first_name}}\n\n{{postal_address}}"}
    return {"campaign": slug, "offer": "", "steps": [{"step": 1, "wait_time": 3, "variations": [step]}], "subsequences": [],
            "replies": {"yes": "", "question": "", "not_now": "", "referral": "", "price": "", "no": ""},
            "open_questions": ["Everything. The copywriter profile writes this with the cold-copy skill."]}


def make(client, out, slugs):
    if not SLUG.match(client) or not all(SLUG.match(slug) for slug in slugs):
        raise SystemExit("Client and campaign names are lowercase letters, numbers and hyphens.")
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} isn't empty. Nothing was changed.")
    cold = out / "cold"
    (cold / "sequences").mkdir(parents=True)
    (cold / "lists").mkdir()
    for tool in TOOLS:
        shutil.copy(HERE / tool, cold / tool)
    shutil.copy(HERE / "TEMPLATE.md", out / "TEMPLATE.md")
    (cold / "campaigns.json").write_text(json.dumps({slug: campaign(slug) for slug in slugs}, indent=2) + "\n")
    for slug in slugs:
        (cold / "sequences" / f"{slug}.json").write_text(json.dumps(blank_copy(slug), indent=2) + "\n")
    (cold / "copy-vars.json").write_text(json.dumps({"default": {}}, indent=2) + "\n")
    keys = out / "box.env"
    keys.write_text(KEYS)
    keys.chmod(0o600)
    (out / ".gitignore").write_text("box.env\ncold/lists/\ncold/*.jsonl\ncold/state.json\ncold/mailboxes.json\ncold/copy-vars.json\n")
    print(json.dumps({"client": client, "folder": str(out), "campaigns": slugs, "tools": len(TOOLS)}))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("client")
    ap.add_argument("--out", required=True)
    ap.add_argument("--campaign", action="append", default=[])
    a = ap.parse_args(argv)
    make(a.client, a.out, a.campaign or ["first-campaign"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
