#!/usr/bin/env python3
"""Run a saved scraper, or re-test them all.

    scraper_run.py <name>          runs tools/scrapers/<name>/scrape.py (its own --proxy and paid rungs go through the scrape pool)
    scraper_run.py --retest-all    runs every `ok` scraper's --test on its fixture; broken ones go to the digest

Scrapers live in <WORKER_HOME>/tools/scrapers/ (the scraper-forge skill's layout), not in the pack."""
import re, subprocess, sys
from _common import HOME, emit

ROOT = HOME / "tools" / "scrapers"

def main(a):
    if a and a[0] == "--retest-all":
        reg = (ROOT / "REGISTRY.md").read_text(errors="ignore") if (ROOT / "REGISTRY.md").exists() else ""
        names = re.findall(r"^\|\s*([a-z0-9-]+)\s*\|.*\|\s*ok\s*\|", reg, re.M)
        broken = []
        for n in names:
            r = subprocess.run([sys.executable, str(ROOT / n / "scrape.py"), "--test"], capture_output=True, text=True, timeout=300,
                               cwd=str(ROOT / n) if (ROOT / n).is_dir() else None)  # the same folder a run uses, so fixture.html resolves
            if r.returncode != 0:
                broken.append({"id": n, "why": (r.stdout.strip().splitlines() or r.stderr.strip().splitlines() or ["failed"])[-1][:120]})
        emit("scraper-retest", "blocked" if broken else "count", items=broken, counts={"tested": len(names), "broken": len(broken)})
        print(f"retested {len(names)}, broken {len(broken)}"); return 0
    if not a or not re.fullmatch(r"[a-z0-9-]+", a[0]) or not (ROOT / a[0] / "scrape.py").exists():
        print("usage: scraper_run.py <name> (a folder in tools/scrapers/)"); return 2
    r = subprocess.run([sys.executable, str(ROOT / a[0] / "scrape.py")], capture_output=True, text=True, timeout=7200, cwd=str(ROOT / a[0]))
    tail = (r.stdout.strip().splitlines() or r.stderr.strip().splitlines() or [""])[-1]
    emit("scraper-run", "count", counts={"runs": 1, "failed": int(r.returncode != 0)}, note=f"{a[0]}: {tail[:200]}")
    print(tail); return r.returncode

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
