"""Turn a campaign JSON into the readable page Justin approves.

    python3 render.py <campaign>.json [why.json]

why.json holds the plain-language reasons: {"big": "...", "steps": {"1A": ["name", "why"], ...},
"subsequences": "...", "replies": "..."}. Without it the page shows the copy alone.
"""
import json
import pathlib
import re
import sys

RAND = re.compile(r"\{\{\s*RANDOM\s*\|(.*?)\}\}", re.S)
NAMES = {"first_line": "[a line written for them from their own website]", "first_name": "[first name]", "company_name": "[company]", "city": "[city]",
         "company_sender": "[our company]", "sender_first_name": "[sender]",
         "postal_address": "[postal address]", "booking_link": "[booking link]"}


def options(match):
    return [part.strip() for part in match.group(1).split("|")]


def first(text):
    return RAND.sub(lambda m: options(m)[0], text)


def friendly(text):
    text = re.sub(r"\{\{\s*fallback\s*\|\s*\{\{(\w+)\}\}\s*\|[^{}]*\}\}", lambda m: "{{%s}}" % m.group(1), text, flags=re.I)
    for key, value in NAMES.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def quoted(text):
    return "\n".join(("> " + line).rstrip() for line in friendly(first(text)).split("\n"))


def swaps(text):
    out = []
    for match in RAND.finditer(text):
        out.append("- " + " / ".join(friendly(o) for o in options(match)))
    return out


def email(lines, body):
    lines.append(quoted(body))
    lines.append("")
    rows = swaps(body)
    if rows:
        lines.append("Rotates through:")
        lines.append("")
        lines.extend(rows)
        lines.append("")


def render(data, why=None):
    why = why or {}
    reasons = why.get("steps", {})
    lines = ["# %s" % data["campaign"], "", "**Offer:** %s" % data["offer"], "",
             "**Status:** draft for Justin's one-time approval. Nothing is loaded and nothing sends.", ""]
    if why.get("big"):
        lines += ["## The thinking", "", why["big"], ""]
    lines += ["## How to read this", "",
              "Each email shows the first version of every line. The list under it is what each spot rotates "
              "through, in order, so no two sends match. Words in square brackets fill in per person. Steps 2 and "
              "3 are written to follow any version of step 1.", ""]
    for step in data["steps"]:
        lines += ["## Step %d (wait %d days after it)" % (step["step"], step["wait_time"]), ""]
        for variation in step["variations"]:
            key = "%d%s" % (step["step"], variation["variation"])
            name, reason = reasons.get(key, ("", ""))
            lines += ["### %s%s" % (variation["variation"], ": " + name if name else ""), ""]
            if reason:
                lines += ["**Why:** %s" % reason, ""]
            if variation["subject"]:
                subject = RAND.search(variation["subject"])
                shown = options(subject) if subject else [variation["subject"]]
                lines += ["**Subject:** " + " / ".join("`%s`" % s for s in shown), ""]
            else:
                lines += ["**Subject:** none, it stays in the same thread", ""]
            email(lines, variation["body"])
    lines += ["## Follow-ups for people who replied", ""]
    if why.get("subsequences"):
        lines += [why["subsequences"], ""]
    for sub in data["subsequences"]:
        lines += ["### %s" % sub["name"], "",
                  "Trigger `%s`, first email %d days after the label." % (sub["trigger"], sub["first_wait_time"]), ""]
        for step in sub["steps"]:
            lines += ["**Email %d** (wait %d days after it)" % (step["step"], step["wait_time"]), ""]
            for variation in step["variations"]:
                email(lines, variation["body"])
    lines += ["## Replies", ""]
    if why.get("replies"):
        lines += [why["replies"], ""]
    for label, text in data["replies"].items():
        lines += ["### %s" % label.replace("_", " "), "", quoted(text), ""]
    lines += ["## Open questions for Justin", ""]
    lines += ["%d. %s" % (i, q) for i, q in enumerate(data["open_questions"], 1)]
    return "\n".join(lines) + "\n"


def write(data, why, folder):
    folder = pathlib.Path(folder)
    (folder / ("%s.json" % data["campaign"])).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (folder / ("%s.md" % data["campaign"])).write_text(render(data, why))


if __name__ == "__main__":
    source = pathlib.Path(sys.argv[1])
    loaded = json.loads(source.read_text())
    extra = json.loads(pathlib.Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    source.with_suffix(".md").write_text(render(loaded, extra))
