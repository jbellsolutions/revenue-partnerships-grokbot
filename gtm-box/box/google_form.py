#!/usr/bin/env python3
"""Submit a Google Form guest application with no model, so the same form gets the same answers every run.

    google_form.py inspect <form url>             the questions and how each would be answered, sends nothing
    google_form.py submit <case id> <form url>    runs send_guard, marks the start, posts once, records the confirmation

A required question it can't answer from goal/pitch-details.json stops the run. It never guesses, and it never posts twice:
the show is held before the post, and only a confirmation page records it as sent.
"""
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or BOX_HOME)
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else HERE))

import goal  # noqa: E402
import send_guard  # noqa: E402

AGENT = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
TEXT, PARAGRAPH, RADIO, DROPDOWN, CHECKBOX = 0, 1, 2, 3, 4
PAGE_BREAK = 8
# First match wins, so the narrow labels come before the broad ones. An optional question nobody matched stays blank.
LABELS = (("scheduling", None), ("phone", "phone"), ("hear about", "how_heard"), ("bio", "bio"), ("owner", "owner_or_founder"), ("in-house staff", "employs_in_house_staff"),
          ("professional focus", "primary_focus"), ("what does your business do", "business_summary"),
          ("big talk", "topic"), ("social media", "social_links"), ("first and last name", "full_name"),
          ("email", "email"), ("name of business", "company"), ("website", "website"), ("title", "role"), ("role", "role"))


def fetch(url, data=None):
    request = urllib.request.Request(url, data=data, headers=AGENT)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace"), response.geturl()


def parse(source):
    """The questions in page order, and how many pages there are, from the data Google puts in the form's page."""
    found = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>", source, re.S)
    if not found:
        raise ValueError("this page has no Google Form data")
    data = json.loads(found.group(1))
    questions, pages = [], 1
    for item in data[1][1]:
        kind = item[3]
        if kind == PAGE_BREAK:
            pages += 1
        elif item[4]:
            entry = item[4][0]
            options = [o[0] for o in (entry[1] or []) if o and o[0]]
            questions.append({"title": item[1] or "", "kind": kind, "entry": entry[0], "required": bool(entry[2]),
                              "options": options, "page": pages - 1})
    token = re.search(r'name="fbzx" value="(-?\d+)"', source)
    custom = data[1][2] if len(data[1]) > 2 else None
    closing = custom[0] if custom and custom[0] else "Your response has been recorded."
    return questions, pages, token.group(1) if token else "", closing


def answers():
    details = goal.read(HOME / "goal" / "pitch-details.json", {}) or {}
    return {**details, "full_name": f"{details.get('first_name', '')} {details.get('last_name', '')}".strip(),
            "email": send_guard.email(), "phone": send_guard.phone()}


def plan(questions, values):
    """Each question with its answer, and the required ones nobody can answer. Nothing here invents a value."""
    filled, missing = [], []
    for question in questions:
        title = question["title"].lower()
        key = next((name for label, name in LABELS if label in title), None)
        value = values.get(key) if key else None
        if value and question["options"] and value not in question["options"]:
            value = None
        if value:
            filled.append((question, value))
        elif question["required"]:
            missing.append(question["title"])
    return filled, missing


def body(filled, questions, token):
    """pageHistory is the pages a person would walk. A page with no questions is a branch nobody lands on."""
    walked = sorted({question["page"] for question in questions})
    fields = [(f"entry.{question['entry']}", value) for question, value in filled]
    fields += [("fvv", "1"), ("pageHistory", ",".join(str(n) for n in walked)), ("fbzx", token)]
    return urllib.parse.urlencode(fields).encode()


def load(url):
    source, final = fetch(url)
    if "docs.google.com/forms" not in final:
        raise ValueError(f"this url went to {urllib.parse.urlsplit(final).netloc}, not a Google Form")
    return (final, *parse(source))


def confirmed(page, closing):
    """A form sets its own closing words, so only those count. Any other page, an error included, isn't a confirmation."""
    text = re.sub(r"\s+", " ", html.unescape(page))
    return re.sub(r"\s+", " ", closing)[:60] in text and "FB_PUBLIC_LOAD_DATA_" not in page


def show(filled, missing, values):
    private = {values.get("email"): "[address]", values.get("phone"): "[number]"}
    for question, value in filled:
        print(f"p{question['page'] + 1} {question['title'][:70]}: {private.get(value) or value[:90]}")
    for title in missing:
        print(f"MISSING (required): {title}")


def inspect(url):
    _, questions, pages, _, _ = load(url)
    values = answers()
    filled, missing = plan(questions, values)
    print(f"{len(questions)} questions on {pages} pages")
    show(filled, missing, values)
    return 1 if missing else 0


def submit(case_id, url):
    cases = {c.get("case_id"): c for c in goal.cases()}
    who = (cases.get(case_id) or {}).get("name")
    if not who:
        print(f"refused: no case {case_id}")
        return 1
    if case_id not in {r["case_id"] for r in send_guard.ready()}:
        print(f"refused: {case_id} isn't cleared to send")
        return 1
    final, questions, pages, token, closing = load(url)
    values = answers()
    filled, missing = plan(questions, values)
    if missing:
        send_guard.main(["hold", case_id, "Required questions with no answer: " + "; ".join(missing)])
        print("held: " + "; ".join(missing))
        return 1
    send_guard.main(["start", case_id])
    target = final.split("?")[0].rsplit("/", 1)[0] + "/formResponse"
    try:
        page, _ = fetch(target, body(filled, questions, token))
    except urllib.error.HTTPError as refused:  # Google answers a post it rejects with a 400, and counts nothing.
        send_guard.main(["hold", case_id, f"Google refused the post with a {refused.code}. Nothing was submitted."])
        print(f"refused by Google: {refused.code}. Nothing was submitted, and the show is held.")
        return 1
    folder = HOME / "goal" / "evidence"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{case_id}.html").write_text(page)
    if confirmed(page, closing):
        send_guard.main(["sent", "podcast_pitch", who, "--evidence", f"Google Form: {closing[:200]}"])
        print(f"confirmed: {closing[:200]}")
        return 0
    print(f"Google answered, but not with its confirmation. The page is in {folder}, and the show stays held.")
    return 1


def main(argv):
    if len(argv) == 3 and argv[1] == "inspect":
        return inspect(argv[2])
    if len(argv) == 4 and argv[1] == "submit":
        return submit(argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
