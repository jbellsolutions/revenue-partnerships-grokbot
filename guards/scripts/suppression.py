#!/usr/bin/env python3
"""Suppression guard. Run before any draft to a person.

    suppression.py check "<name, business, email, profile url or domain>"   prints clear or held; exit 0 clear, 1 held
    suppression.py add "<who>" "<reason>"                                    someone said no: done for every role
    suppression.py sync                                                      worker mode: refresh the engine's local copy

One list for the whole bot: context/suppression.csv, in the engine's format (header `kind,value,reason`; kind is
email, linkedin, domain or term), plus the engine's opt-out overlay gtm-box/optouts.csv. gtm-box/suppression.csv is
a link to context/suppression.csv, so the guard and the engine (gtm-box/box/suppression.py) read the same rows with
the same matcher. Never print the list."""
import sys, csv, re, importlib.util
from _ws import p

LIST = p("context", "suppression.csv")
ENGINE = p("gtm-box", "box", "suppression.py")
EMAIL = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")


def engine():
    if not ENGINE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("gtm_suppression", ENGINE)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ENGINE.parent))
    spec.loader.exec_module(m)
    return m


def lists():
    """The engine's matcher over the list and its overlay. The overlay sits next to the path given, so pass the
    engine's own path (the link in gtm-box/) when it exists: then both read gtm-box/optouts.csv."""
    m = engine()
    if m is None:
        return None
    link = p("gtm-box", "suppression.csv")
    return m.load(link if link.exists() else LIST)


def kind_of(v):
    v = v.strip().lower()
    if EMAIL.fullmatch(v):
        return "email", v
    if "linkedin.com/in/" in v:
        return "linkedin", "linkedin.com/in/" + v.split("linkedin.com/in/")[1].split("?")[0].strip("/")
    if re.fullmatch(r"(?:[a-z0-9-]+\.)+[a-z]{2,}", v):
        return "domain", v
    return "term", v


def remote(a):
    """Worker mode: the worker holds the one list. Unreachable means held."""
    import _ws
    try:
        if a[0] == "check":
            r = _ws.call("POST", "/v1/suppression/check", {"who": a[1]})
            print("clear" if r.get("result") == "clear" else "held"); return 0 if r.get("result") == "clear" else 1
        r = _ws.call("POST", "/v1/suppression/add", {"who": a[1], "reason": a[2] if len(a) > 2 else "said no"})
        if r.get("result") != "added": raise _ws.WorkerDown("add failed")
        print("added"); return 0
    except _ws.WorkerDown as e:
        print(f"held: worker unreachable ({e})" if a[0] == "check" else f"failed: worker unreachable ({e}); retry, and tell lead")
        return 1


def sync():
    """Worker mode: refresh the local copy the engine (gtm-box) reads, once at the start of a run. The guard's own
    check always asks the worker; this copy is only the engine's second check."""
    import _ws, os
    try:
        body = _ws.call("GET", "/v1/suppression.csv", raw=True, timeout=30)
    except _ws.WorkerDown as e:
        print(f"failed: worker unreachable ({e}); the engine keeps its last copy, the guard holds"); return 1
    LIST.parent.mkdir(parents=True, exist_ok=True)
    tmp = LIST.with_suffix(".tmp"); tmp.write_text(body); os.chmod(tmp, 0o600); tmp.replace(LIST)
    print(f"synced {max(0, body.count(chr(10)) - 1)} rows"); return 0


def main(a):
    import _ws
    if a and a[0] == "sync":
        return sync() if _ws.worker() else (print("local mode: nothing to sync") or 0)
    if len(a) >= 2 and a[0] in ("check", "add") and _ws.worker():
        return remote(a)
    if len(a) >= 2 and a[0] == "check":
        if not LIST.exists():
            print("held: no suppression list yet (context/suppression.csv); ask Justin"); return 1
        ls = lists()
        if ls is None:
            print("held: the engine (gtm-box/box/suppression.py) is missing; HANDOFF Part 2 step 1"); return 1
        print("held" if ls.reason(a[1]) else "clear")
        return 1 if ls.reason(a[1]) else 0
    if len(a) >= 2 and a[0] == "add":
        kind, value = kind_of(a[1])
        reason = (a[2] if len(a) > 2 else "said no").replace(",", " ")
        m = engine()
        if m and kind in ("email", "linkedin"):
            link = p("gtm-box", "suppression.csv")
            m.record_opt_out(value, reason, link if link.exists() else LIST)  # also tells the sender
        else:
            LIST.parent.mkdir(parents=True, exist_ok=True)
            fresh = not LIST.exists() or not LIST.read_text(errors="ignore").strip()
            with LIST.open("a", newline="") as h:
                w = csv.writer(h)
                if fresh:
                    w.writerow(["kind", "value", "reason"])
                w.writerow([kind, value, reason])
            if kind == "term" and " " not in value and "/" not in value:
                print("note: a bare single word holds everyone who matches it; add their email or profile url too")
        print("added"); return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
