"""Shared by the worker's jobs: paths, the digest inbox, guards in local mode."""
import json, os, pathlib, subprocess, sys, time

PACK = pathlib.Path(__file__).resolve().parents[2]
HOME = pathlib.Path(os.environ.get("WORKER_HOME", "/opt/revenue-worker"))
GUARDS = PACK / "guards" / "scripts"
os.environ["WORKER_LOCAL"] = "1"       # the worker reads its own guard files
os.environ.setdefault("BOT_HOME", str(HOME))
os.environ.setdefault("GTM_HOME", str(HOME / "gtm-box"))


def guard(script, *args):
    r = subprocess.run([sys.executable, str(GUARDS / script), *map(str, args)], capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


def emit(job, kind, items=None, counts=None, note=""):
    """One digest record. items: things that need judgment (short fields, no raw personal data beyond a name and link)."""
    d = HOME / "digest" / "inbox"; d.mkdir(parents=True, exist_ok=True)
    rec = {"t": int(time.time()), "job": job, "kind": kind, "counts": counts or {}, "items": items or [], "note": note[:300]}
    with (d / f"{job}.jsonl").open("a") as h:
        h.write(json.dumps(rec, ensure_ascii=False) + "\n")


def score(j):
    """A model's score as a number; anything else (missing, 'n/a', a sentence) is 0, so one odd answer can't stop a job."""
    try:
        return int(float((j or {}).get("score", 0)))
    except (TypeError, ValueError):
        return 0


def cursor(name, value=None):
    f = HOME / "state" / "cursors" / f"{name}.json"
    if value is None:
        return json.loads(f.read_text()) if f.exists() else {}
    f.parent.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(value))


def think(prompt, items, tmpname):
    """Run think.py; returns (results or None, tier line)."""
    tmp = HOME / "state" / "think"; tmp.mkdir(parents=True, exist_ok=True)
    i, o = tmp / f"{tmpname}.in.json", tmp / f"{tmpname}.out.json"
    i.write_text(json.dumps(items, ensure_ascii=False)); o.unlink(missing_ok=True)
    r = subprocess.run([sys.executable, str(PACK / "worker" / "think.py"), "--prompt", f"prompts/{prompt}.md", "--in", str(i), "--out", str(o)],
                       capture_output=True, text=True, timeout=1800)
    line = (r.stdout.strip().splitlines() or ["tier none"])[-1]
    try:
        res = json.loads(o.read_text()) if r.returncode == 0 and o.exists() else None
    except ValueError:
        res = None
    # Only objects with an id count; anything else is treated as not judged.
    return ([x for x in res if isinstance(x, dict)] if isinstance(res, list) else None), line
