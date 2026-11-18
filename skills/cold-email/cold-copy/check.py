"""Check cold campaign copy before it goes to Justin's queue.

    python3 check.py <folder or campaign.json> ...

Exit 0 means no failures. Warnings are for a person to read. Counts use the shortest and the
longest spintax render, not just the first option. The postal address line is not counted.
"""
import json
import os
import pathlib
import re
import sys

RAND = re.compile(r"\{\{\s*RANDOM\s*\|(.*?)\}\}", re.S)
TOKEN = re.compile(r"\{\{(.*?)\}\}", re.S)
# Justin's own email goes in as he wrote it, so length and word rules don't apply to it. These must survive any edit.
CLAIMS = ("turn a struggling Sydney startup from $30k/mo to $700k/mo in less than a year", "currently ranked in the top 0.02% globally")
# The site link is the cold sending site, set at intake as COLD_SITE_URL. Unset, only the podcast link counts.
LINKS = tuple(link for link in ("https://youtu.be/ZV-JLIQ1wXw", os.environ.get("COLD_SITE_URL", "").strip()) if link)


def do_not_mention():
    """Names and products on the suppression rule: a private list, never in this file. Read from env DO_NOT_MENTION
    (comma-separated) or .secrets/do-not-mention.txt (one per line). None means the list is missing, and every
    campaign then fails, so a copy check can never pass without it."""
    raw = os.environ.get("DO_NOT_MENTION", "")
    names = [n.strip().lower() for n in raw.split(",") if n.strip()]
    if names:
        return names
    for base in [pathlib.Path.cwd(), *pathlib.Path(__file__).resolve().parents]:
        path = base / ".secrets" / "do-not-mention.txt"
        if path.is_file():
            names = [n.strip().lower() for n in path.read_text().splitlines() if n.strip() and not n.startswith("#")]
            return names or None
    return None
FALLBACK = re.compile(r"\{\{\s*fallback\s*\|\s*\{\{(\w+)\}\}\s*\|[^{}]*\}\}", re.I)
MERGE = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
BASE_VARS = {"first_line", "first_name", "company_name", "city", "sender_first_name", "postal_address"}
LABELS = ["yes", "question", "not_now", "referral", "price", "no"]
TRIGGERS = {"LEAD_MARKED_AS_INTERESTED", "LEAD_MARKED_AS_NOT_NOW"}
DASHES = chr(0x2014) + chr(0x2013)

# Rule list: words and names that must not appear in any option of any email.
BANNED = ["price", "pricing", "cost", "costs", "fee", "fees", "investment", "spend", "budget", "unlock", "10x",
          "synergy", "leverage", "innovative", "cutting-edge", "solution", "solutions", "game-changer",
          "transform", "revolutionise", "revolutionize", "scale your", "disrupt", "guarantee", "guaranteed",
          "roi", "lead generation", "automation", "opportunity", "passive income", "furthermore", "moreover",
          "delve", "landscape", "robust", "awesome", "amazing", "excited", "honored", "honoured", "reach out",
          "touch base", "hope this finds", "i'd love to", "hop on", "quick call", "risk-free", "no cost",
          "act now", "limited time", "free", "free money", "earn", "earnings", "income", "cash", "credit",
          "approved", "qualify", "qualified", "winner", "urgent", "click here", "buy now", "make money",
          "make you money", "gift card", "too good to be true", "trial", "discount", "offer", "offers",
          "just following up", "circle back", "unsubscribe here", "no catch", "no strings"]
# Plus the do-not-mention list (given at intake), added in scan_words.
AU_BANNED = ["hvac", "contractor", "contractors", "g'day", "mate", "mates", "realtor", "inquiry", "inquiries",
             "organize", "realize", "recognize", "color", "favor", "neighbor", "license"]


def spin_blocks(text):
    return [[o.strip() for o in m.group(1).split("|")] for m in RAND.finditer(text)]


def plain(text):
    return MERGE.sub("X", text)


def pick(text, how):
    def choose(match):
        opts = [o.strip() for o in match.group(1).split("|")]
        return how(opts, key=lambda o: len(re.findall(r"[\w'%]+", plain(o))))
    return RAND.sub(choose, text)


def first(text):
    return RAND.sub(lambda m: m.group(1).split("|")[0].strip(), text)


def count(text):
    return len(re.findall(r"[\w'%-]+", plain(text)))


def split_footer(body):
    lines = body.rstrip().split("\n")
    return "\n".join(lines[:-2]).rstrip(), lines[-2] if len(lines) > 1 else "", lines[-1]


def syllables(word):
    word = word.lower()
    groups = re.findall(r"[aeiouy]+", word)
    total = len(groups) - (1 if word.endswith("e") and not word.endswith("le") and len(groups) > 1 else 0)
    return max(1, total)


def grade(text):
    text = re.sub(r"\s+", " ", plain(text))
    sentences = max(1, len(re.findall(r"[.?]+(?:\s|\Z)", text)))
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return 0.0
    return 0.39 * len(words) / sentences + 11.8 * sum(syllables(w) for w in words) / len(words) - 15.59


def all_text(text):
    """Every word any render could show, with the spintax markup removed."""
    text = RAND.sub(lambda m: " . ".join(o.strip() for o in m.group(1).split("|")), text)
    return MERGE.sub(" ", text)


class Report:
    def __init__(self, name):
        self.name, self.fails, self.warns = name, [], []

    def fail(self, where, what):
        self.fails.append("%s: %s" % (where, what))

    def warn(self, where, what):
        self.warns.append("%s: %s" % (where, what))


def scan_words(rep, where, text, campaign, reply=False):
    low = all_text(text).lower()
    private = do_not_mention()
    if private is None:
        rep.fail(where, "the do-not-mention list is missing: set DO_NOT_MENTION or .secrets/do-not-mention.txt")
        private = []
    for word in BANNED + private:
        if re.search(r"\b" + re.escape(word) + r"\b", low):
            rep.fail(where, "banned word '%s'" % word)
    if campaign.startswith("au-"):
        for word in AU_BANNED:
            if re.search(r"\b" + re.escape(word) + r"\b", low):
                rep.fail(where, "not Australian '%s'" % word)
    if re.search(r"\b\w+(?:ize|izing|ization)\b", low) and campaign.startswith("au-"):
        rep.warn(where, "check spelling, -ize word")
    if campaign == "us-lenders":
        if re.search(r"\bleads?\b", low):
            rep.fail(where, "the word 'leads' with lenders")
        if re.search(r"\bai\b", low):
            rep.fail(where, "AI in a lender email")
        for hit in re.findall(r"\bmoney\b", re.sub(r"hard money", "", low)):
            rep.fail(where, "'money' outside 'hard money'")
    else:
        if re.search(r"\bleads?\b", re.sub(r"past leads and customers", "", low)):
            rep.fail(where, "'leads' outside Justin's phrase")
        if re.search(r"\bloans?\b", re.sub(r"business loan space", "", low)):
            rep.fail(where, "'loan' outside the proof line")
        if re.search(r"\bmoney\b", low):
            rep.fail(where, "'money' in an AI Guy email")
    # The product name doesn't count against the limit of two.
    if len(re.findall(r"\bai\b", first(text).lower().replace("ai revenue os", ""))) > 2:
        rep.warn(where, "AI more than twice in one render")
    for char in DASHES:
        if char in text:
            rep.fail(where, "em or en dash")
    if " - " in text:
        rep.fail(where, "spaced hyphen used as a dash")
    if chr(33) in text:
        rep.fail(where, "exclamation mark")
    if chr(36) in text:
        rep.fail(where, "dollar sign")
    if re.search(r"https?:|www\.|\.com\b", text):
        rep.fail(where, "a link in the text")
    if "{" in TOKEN.sub("", text) or "}" in TOKEN.sub("", text):
        rep.fail(where, "single brace")
    if "[" in text or "]" in text:
        rep.fail(where, "bracket placeholder")


def scan_vars(rep, where, text, allowed):
    for match in TOKEN.finditer(RAND.sub("", text)):
        name = match.group(1).strip()
        if name not in allowed:
            rep.fail(where, "merge field not allowed: %s" % name)
    for match in RAND.finditer(text):
        if "{{" in match.group(1):
            rep.fail(where, "merge field or spin inside a spin block")
    for block in spin_blocks(text):
        if len(block) < 2 or not all(block):
            rep.fail(where, "spin block with under two real options")
    leftover = RAND.sub("", text)
    if "RANDOM" in leftover:
        rep.fail(where, "malformed spin block")


def scan_footer(rep, where, body):
    copy, optout, last = split_footer(body)
    if not last.strip() == "{{postal_address}}":
        rep.fail(where, "does not end with the postal address field")
    if not re.search(r"reply|off our list", optout, re.I):
        rep.fail(where, "no opt-out line above the postal address")
    return copy


def check_campaign(path):
    data = json.loads(FALLBACK.sub(lambda m: "{{%s}}" % m.group(1), pathlib.Path(path).read_text()))
    campaign = data.get("campaign", "?")
    rep = Report(campaign)
    if not list(data.keys()) == ["campaign", "offer", "steps", "subsequences", "replies", "open_questions"]:
        rep.fail("top", "keys out of shape: %s" % list(data.keys()))
    allowed = set(BASE_VARS)
    if campaign == "us-lenders":
        allowed.add("company_sender")
    steps = data["steps"]
    if not [s["step"] for s in steps] == [1, 2, 3]:
        rep.fail("steps", "must be steps 1, 2, 3")
    expected = {1: ["A", "B", "C"], 2: ["A", "B"], 3: ["A", "B"]}
    print("\n%s" % campaign)
    openers = {}
    for step in steps:
        n = step["step"]
        if not [v["variation"] for v in step["variations"]] == expected.get(n):
            rep.fail("step %d" % n, "wrong variation labels")
        if not isinstance(step["wait_time"], int) or step["wait_time"] < 0:
            rep.fail("step %d" % n, "bad wait_time")
        for variation in step["variations"]:
            where = "step %d%s" % (n, variation["variation"])
            subject, body = variation["subject"], variation["body"]
            if n == 1:
                opts = spin_blocks(subject) or [[subject]]
                if len(opts) > 1 or len(opts[0]) < 3:
                    rep.fail(where, "subject needs one spin block with 3 or more options")
                for option in opts[0]:
                    if not option == option.lower():
                        rep.fail(where, "subject not lowercase: %s" % option)
                    if not 1 <= len(option.split()) <= 4:
                        rep.fail(where, "subject not 1 to 4 words: %s" % option)
                    if "%" in option or "{{" in option:
                        rep.fail(where, "subject has a percent or a merge field: %s" % option)
                scan_words(rep, where + " subject", subject, campaign)
            elif subject:
                rep.fail(where, "subject must be empty to chain the thread")
            mine = variation.get("justin")
            if mine:
                for claim in CLAIMS:
                    if claim not in body:
                        rep.fail(where, "Justin's words changed: %s" % claim)
                if not any(link in body for link in LINKS):
                    rep.fail(where, "no podcast or site link")
            else:
                scan_words(rep, where, body, campaign)
            scan_vars(rep, where, body, allowed)
            copy = scan_footer(rep, where, body)
            low, high = count(pick(copy + "\n" + split_footer(body)[1], min)), count(pick(copy + "\n" + split_footer(body)[1], max))
            copy_low, copy_high = count(pick(copy, min)), count(pick(copy, max))
            level = grade(pick(copy, max))
            blocks = len(spin_blocks(body))
            print("  %-8s words %3d to %3d (copy %3d to %3d)  grade %4.1f  spins %2d" % (where, low, high, copy_low, copy_high, level, blocks))
            if n == 1:
                if not mine and (low < 50 or high > 100):
                    rep.fail(where, "first email outside 50 to 100 words: %d to %d" % (low, high))
                if blocks < 8:
                    rep.warn(where, "light spintax: %d blocks" % blocks)
                words = re.findall(r"[\w'%-]+", plain(first(copy)).lower())
                openers[variation["variation"]] = {" ".join(words[i:i + 8]) for i in range(len(words) - 7)}
            else:
                if copy_low < 30 or copy_high > 62:
                    rep.warn(where, "follow-up copy outside 30 to 62 words: %d to %d" % (copy_low, copy_high))
                if blocks < 4:
                    rep.warn(where, "light spintax: %d blocks" % blocks)
            if level > 7:
                rep.warn(where, "reading grade %.1f is over the ceiling of 7" % level)
    keys = sorted(openers)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            shared = openers[a] & openers[b]
            if shared:
                rep.warn("step 1", "%s and %s share an 8-word run: %s" % (a, b, sorted(shared)[0]))
    subs = data["subsequences"]
    if not len(subs) == 2:
        rep.fail("subsequences", "need two")
    if not sorted(len(s["steps"]) for s in subs) == [1, 2]:
        rep.fail("subsequences", "need one of 2 steps and one of 1 step")
    for sub in subs:
        if sub["trigger"] not in TRIGGERS:
            rep.fail(sub["name"], "unknown trigger")
        for step in sub["steps"]:
            for variation in step["variations"]:
                where = "%s %d" % (sub["trigger"].rsplit("_", 1)[-1].lower(), step["step"])
                if variation["subject"]:
                    rep.fail(where, "subject must be empty")
                scan_words(rep, where, variation["body"], campaign)
                scan_vars(rep, where, variation["body"], allowed | {"booking_link"})
                scan_footer(rep, where, variation["body"])
                print("  %-12s copy %3d to %3d" % (where, count(pick(split_footer(variation["body"])[0], min)), count(pick(split_footer(variation["body"])[0], max))))
    replies = data["replies"]
    if not list(replies.keys()) == LABELS:
        rep.fail("replies", "labels out of shape: %s" % list(replies.keys()))
    for label, text in replies.items():
        where = "reply " + label
        scan_words(rep, where, text, campaign, reply=True)
        scan_vars(rep, where, text, allowed | {"booking_link"})
        if "RANDOM" in text:
            rep.fail(where, "no spintax in replies: the reply call sends text as written")
        scan_footer(rep, where, text)
    if "{{booking_link}}" not in replies.get("yes", ""):
        rep.fail("reply yes", "must give the booking route")
    if not re.search(r"Justin|come back to you", replies.get("price", "")):
        rep.fail("reply price", "must hand off to Justin")
    if re.search(r"\d", re.sub(r"\{\{.*?\}\}", "", replies.get("price", ""))):
        rep.fail("reply price", "has a number in it")
    if not data.get("open_questions"):
        rep.warn("open_questions", "empty")
    return rep


def main(args):
    paths = []
    for arg in args:
        target = pathlib.Path(arg)
        paths += sorted(target.glob("*.json")) if target.is_dir() else [target]
    failed = 0
    for path in paths:
        rep = check_campaign(path)
        for line in rep.warns:
            print("  warn  " + line)
        for line in rep.fails:
            print("  FAIL  " + line)
        failed += len(rep.fails)
    print("\n%s" % ("PASS" if not failed else "FAILED: %d" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
