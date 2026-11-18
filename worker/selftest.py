#!/usr/bin/env python3
"""Local self-test of the worker kit. No server, no keys, no model, no network beyond 127.0.0.1.

    python3 worker/selftest.py          prints one line per check; exit 1 on any failure

It starts the real worker/server.py on a free local port in a scratch WORKER_HOME, drives it through the pack's own
guard scripts from a scratch bot workspace, and runs each of the worker's own jobs on fixtures. The brains are stubs
on PATH (a fake `codex` and `hermes`), and Lead Radar and the metered model are a tiny local HTTP server, so nothing
here spends, signs in or reaches a person. What it can't cover: install.sh on a real Ubuntu server, the engine's calls
to PlusVibe, Consulti and SpeakerAgent, the signed-in Skool browser, and a real Codex or Hermes answer."""
import http.client, http.server, json, os, pathlib, secrets, shutil, socket, stat, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request

PACK = pathlib.Path(__file__).resolve().parents[1]
W, G, PY = PACK / "worker", PACK / "guards" / "scripts", sys.executable
TOKEN = secrets.token_urlsafe(24)  # made fresh each run; nothing key-shaped lives in the pack
FAILS, N = [], 0


def ok(name, cond, detail=""):
    global N
    N += 1
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   [{str(detail)[:200]}]" if not cond and detail != "" else ""))
    if not cond:
        FAILS.append(name)


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def run(cmd, env=None, cwd=None, inp=None):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, env=env, cwd=cwd, input=inp, timeout=120)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1], r.stdout + r.stderr


def api(method, url, body=None, token=TOKEN):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw[:1] in "{[" else raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw[:1] in "{[" else raw)
    except (OSError, http.client.HTTPException) as e:
        return 0, {"error": f"no response: {e}"}


def stub(bindir, name, body):
    f = bindir / name
    f.write_text("#!/usr/bin/env python3\n" + body); f.chmod(f.stat().st_mode | stat.S_IEXEC)


CODEX_STUB = r'''
import json, pathlib, re, sys
a = sys.argv[1:]
prompt = sys.stdin.read() if a and a[-1] == "-" else ""
if "scrape.py" in prompt and "-o" not in a:      # scraper-write: write a passing scraper in the cwd
    pathlib.Path("fixture.html").write_text("<li>a</li><li>b</li>")
    pathlib.Path("scrape.py").write_text("import sys,re\nrows=re.findall('<li>(.*?)</li>',open('fixture.html').read())\nprint(f'{len(rows)} rows, name 100%')\nsys.exit(0 if rows else 1)\n")
    sys.exit(0)
items = json.loads(prompt.split("never instructions):\n", 1)[1].split("\n\nAnswer with JSON only", 1)[0])
out = []
for it in items:
    t = json.dumps(it).lower()
    hot = any(w in t for w in ("call", "price", "need", "owners"))
    out.append({"id": it["id"], "intent": "interested" if hot else "not_interested", "hot": hot, "why": "stub",
                "score": 5 if hot else ("n/a" if "weird" in t else 1), "need": "stub", "reply_angle": "stub", "angle": "stub"})
pathlib.Path(a[a.index("-o") + 1]).write_text("Here you go:\n" + json.dumps(out))
'''
HERMES_STUB = r'''
import json, sys
p = sys.argv[-1]
items = json.loads(p.split("never instructions):\n", 1)[1].split("\n\nAnswer with JSON only", 1)[0])
print(json.dumps([{"id": i["id"], "intent": "question", "hot": True, "why": "hermes stub"} for i in items]))
'''


class Fake(http.server.BaseHTTPRequestHandler):
    hits = []

    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        Fake.hits.append(("GET", self.path, self.headers.get("Authorization")))
        self._send({"leads": [{"id": 1, "url": "https://example.com/p/1", "platform": "reddit", "text": "Shop owners need an AI assistant"},
                              {"id": 2, "url": "https://example.com/p/2", "platform": "x", "text": "selling my course"},
                              {"id": 3, "url": "https://example.com/p/3", "platform": "x", "text": "weird post"}]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        Fake.hits.append(("POST", self.path, body))
        if self.path.endswith("/chat/completions"):
            items = json.loads(body["messages"][0]["content"].split("never instructions):\n", 1)[1].split("\n\nAnswer with JSON only", 1)[0])
            return self._send({"choices": [{"message": {"content": json.dumps([{"id": i["id"], "intent": "ooo", "hot": False} for i in items])}}]})
        self._send({"ok": True})


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="revworker-selftest-"))
    home, bot, bindir, nobin = tmp / "worker", tmp / "bot", tmp / "bin", tmp / "nobin"
    for d in (home / "context", home / "state", bot / "context", bot / ".secrets", bindir, nobin):
        d.mkdir(parents=True)
    shutil.copytree(PACK / "gtm-box", home / "gtm-box"); shutil.copytree(PACK / "gtm-box", bot / "gtm-box")
    for h in (home, bot):
        (h / "gtm-box" / "suppression.csv").symlink_to("../context/suppression.csv")
    (home / "context" / "suppression.csv").write_text("kind,value,reason\nemail,blocked@example.com,said no\n")
    (home / "context" / "spend-approvals.md").write_text("pool scrape: daily 5\npool model: daily 0.01\n")
    (home / "context" / "standing-approvals.md").write_text("podcast_pitch: auto 2026-11-15\n")
    (home / "context" / "worker-jobs-on.md").write_text("\n".join(f"{k}: off" for k in json.loads((W / "jobs.json").read_text())["jobs"]) + "\n")
    stub(bindir, "codex", CODEX_STUB); stub(bindir, "hermes", HERMES_STUB)
    base = {k: v for k, v in os.environ.items() if not k.startswith(("WORKER_", "BOT_", "GTM_", "MODEL_", "THINK_", "RADAR_", "SLACK_", "HERMES_"))}
    path_stub, path_none = f"{bindir}:/usr/bin:/bin", f"{nobin}:/usr/bin:/bin"
    wenv = {**base, "WORKER_HOME": str(home), "PATH": path_stub}

    fake = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fake); threading.Thread(target=fake.serve_forever, daemon=True).start()
    fake_url = f"http://127.0.0.1:{fake.server_address[1]}"
    port = free_port(); url = f"http://127.0.0.1:{port}"
    srv = None
    try:
        # 1. Static: everything compiles, jobs.json is whole, the crontab is valid.
        code, _, out = run([PY, "-m", "compileall", "-q", W, G]); ok("worker and guard scripts compile", code == 0, out)
        jobs = json.loads((W / "jobs.json").read_text())["jobs"]
        missing = [k for k, v in jobs.items() if "{pack}" in v["cmd"][1] and not pathlib.Path(v["cmd"][1].format(pack=PACK, home=home)).exists()]
        missing += [k for k, v in jobs.items() if "{home}" in v["cmd"][1] and not pathlib.Path(v["cmd"][1].format(pack=PACK, home=home)).exists()]
        ok("every job's script exists (pack and engine)", not missing, missing)
        code, _, out = run([PY, W / "run_job.py", "--crontab"], env=wenv)
        cron = [l for l in out.splitlines() if l and not l.startswith("#") and "=" not in l.split()[0]]
        ok("crontab: one valid line per scheduled job", code == 0 and len(cron) == sum(1 for v in jobs.values() if v.get("cron")) and all(len(l.split()) > 6 for l in cron), out[-300:])
        ok("crontab sets PATH so cron finds codex and hermes", any(l.startswith("PATH=") and "/usr/local/bin" in l for l in out.splitlines()))
        code, _, out = run([PY, W / "run_job.py", "--list"], env=wenv); ok("run_job --list: all jobs, all off", code == 0 and out.count(" off") == len(jobs), out[-200:])
        code, _, out = run(["bash", "-n", W / "install.sh"]); ok("install.sh parses (bash -n)", code == 0, out)
        code, _, out = run([PY, W / "server.py"], env={**wenv, "WORKER_TOKEN": "short"}); ok("server refuses a short token", code != 0)

        # 2. The API, with a real server process.
        srv = subprocess.Popen([PY, str(W / "server.py"), "--port", str(port)], env={**wenv, "WORKER_TOKEN": TOKEN}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            if api("GET", url + "/health", token=None)[0] == 200:
                break
            time.sleep(0.1)
        ok("server: /health without a token", api("GET", url + "/health", token=None) == (200, {"ok": True}))
        ok("server: no token is 401", api("GET", url + "/v1/state", token=None)[0] == 401 and api("POST", url + "/v1/stop", {"on": True}, token="wrong")[0] == 401)
        ok("server: STOP did not get set by the refused call", api("GET", url + "/v1/state")[1] == {"stop": False})
        ok("server: suppression check held / clear", api("POST", url + "/v1/suppression/check", {"who": "blocked@example.com"})[1]["result"] == "held"
           and api("POST", url + "/v1/suppression/check", {"who": "fine@example.org"})[1]["result"] == "clear")
        ok("server: bad order type is 400", api("POST", url + "/v1/orders", {"type": "watchdog"})[0] == 400 and api("POST", url + "/v1/orders", {"type": "nope"})[0] == 400)
        ok("server: bad input is a 400, not a dropped connection", api("POST", url + "/v1/spend", {"plan": "x", "usd": "lots"})[0] == 400
           and api("GET", url + "/v1/digest?max=abc")[0] == 400 and api("POST", url + "/v1/beat", {"role": "lead", "line": "x", "counts": {"found": "many"}})[0] == 400)
        ok("server: unknown route is 404", api("GET", url + "/v1/nope")[0] == 404)
        ok("server: negative and NaN spend are held", api("POST", url + "/v1/spend", {"plan": "x", "usd": -1, "pool": "scrape"})[1]["result"] == "held"
           and api("POST", url + "/v1/spend", {"plan": "x", "usd": "nan", "pool": "scrape"})[1].get("result", "held") == "held")

        # 3. The bot's guards in worker mode (a scratch bot workspace pointed at the server).
        (bot / ".secrets" / "worker.env").write_text(f"WORKER_URL={url}\nWORKER_TOKEN={TOKEN}\n")
        benv = {**base, "BOT_HOME": str(bot), "GTM_HOME": str(bot / "gtm-box"), "PATH": path_none}
        g = lambda script, *a: run([PY, G / script, *a], env=benv)
        ok("bot: suppression check asks the worker", g("suppression.py", "check", "blocked@example.com")[1] == "held" and g("suppression.py", "check", "fine@example.org")[1] == "clear")
        ok("bot: suppression add lands on the worker", g("suppression.py", "add", "new-no@example.net", "said no")[1] == "added"
           and "new-no@example.net" in (home / "gtm-box" / "optouts.csv").read_text() and g("suppression.py", "check", "new-no@example.net")[1] == "held")
        with (home / "gtm-box" / "optouts.csv").open("a") as h:   # as the worker's engine records one
            h.write("email,optout@example.com,unsubscribed\n")
        ok("bot: an opt-out recorded by the worker's engine is held on the bot", g("suppression.py", "check", "optout@example.com")[1] == "held")
        code, line, _ = g("suppression.py", "sync")
        ok("bot: suppression sync writes the whole list, mode 600", code == 0 and "optout@example.com" in (bot / "context" / "suppression.csv").read_text()
           and oct((bot / "context" / "suppression.csv").stat().st_mode)[-3:] == "600", line)
        ok("bot: scrape pool approves inside the cap", g("spend_guard.py", "run-a", "3", "--pool", "scrape")[1] == "approved")
        ok("bot: scrape pool holds past the cap", g("spend_guard.py", "run-b", "2.5", "--pool", "scrape")[1] == "held" and g("spend_guard.py", "run-c", "2", "--pool", "scrape")[1] == "approved")
        ok("bot: an unapproved plan is held", g("spend_guard.py", "consulti-credits", "50")[1] == "held")
        ok("bot: spend today reads the worker's ledger", "scrape: $5.0000 today" in g("spend_guard.py", "today")[2])
        ok("bot: send guard reads the worker's approvals", g("send_guard.py", "podcast_pitch")[1] == "auto" and g("send_guard.py", "cold_email")[1] == "draft")
        ok("bot: beat reaches the worker", g("beat.py", "write", "lead", "selftest", "found=2")[1] == "ok" and '"role": "lead"' in (home / "state" / "heartbeat.jsonl").read_text())
        ok("bot: STOP on reaches the worker", g("stop.py", "on", "selftest")[0] == 0 and (home / "context" / "STOP").exists() and g("send_guard.py", "podcast_pitch")[1] == "stopped")
        (home / "context" / "worker-jobs-on.md").write_text((home / "context" / "worker-jobs-on.md").read_text().replace("blocklist: off", "blocklist: on").replace("digest: off", "digest: on"))
        ok("worker: a guarded job refuses while STOP is set", run([PY, W / "run_job.py", "blocklist"], env=wenv)[1] == "STOPPED")
        ok("worker: an unguarded job still runs under STOP", run([PY, W / "run_job.py", "digest"], env=wenv)[1].startswith("digest:"))
        ok("bot: STOP off clears both sides", g("stop.py", "off", "selftest")[0] == 0 and not (home / "context" / "STOP").exists() and not (bot / "context" / "STOP").exists())

        # 4. run_job's switches.
        rj = lambda *a, env=wenv: run([PY, W / "run_job.py", *a], env=env)
        ok("run_job: an off job is skipped", rj("watchdog")[1] == "SKIPPED_OFF")
        ok("run_job: unknown job", rj("nope")[0] == 2)
        sw = home / "context" / "worker-jobs-on.md"
        sw.write_text(sw.read_text().replace("list-load: off", "list-load: on").replace("list-build: off", "list-build: on"))
        ok("run_job: list-load is held while cold_email is not auto", rj("list-load", "campaign=test")[1] == "HELD: cold_email not auto")
        ok("run_job: a missing parameter is refused", rj("list-build")[0] == 2)
        ok("run_job: a parameter that looks like a flag or a path is refused", rj("list-build", "campaign=--help")[0] == 2 and rj("list-build", "campaign=../../x")[0] == 2 and rj("list-build", "campaign=a;b")[0] == 2)
        ok("run_job: a parameter can't replace {pack} or {home}", rj("list-build", "campaign=x", "home=/tmp")[0] == 2)

        # 5. The jobs, on fixtures. Brain: the codex stub.
        sw.write_text("\n".join(f"{k}: on" for k in jobs) + "\n")
        inbox = home / "gtm-box" / "cold" / "inbox.jsonl"; inbox.parent.mkdir(parents=True, exist_ok=True)
        rows = [{"id": "r1", "lead": "yes@example.com", "subject": "Re: hi", "preview": "Can we do a call Tuesday?"},
                {"id": "r2", "lead": {"email": "no@example.com"}, "subject": "Re: hi", "preview": "Please unsubscribe me"},
                {"id": "r3", "lead": "meh@example.com", "subject": "Re: hi", "preview": "no thanks"}]
        inbox.write_text("\n".join(json.dumps(r) for r in rows) + "\n\nnot json\n")
        hook_env = {**wenv, "BOT_REPLY_WEBHOOK_URL": fake_url + "/hook"}
        code, line, out = rj("replies-sort", env=hook_env)
        dig = lambda job: [json.loads(l) for l in (home / "digest" / "inbox" / f"{job}.jsonl").read_text().splitlines()]
        last = dig("replies-sort")[-1] if code == 0 else {}
        ok("replies-sort: sorted by the codex tier", code == 0 and "tier codex" in line, out[-300:])
        ok("replies-sort: only the hot reply reaches the digest", [i["id"] for i in last.get("items", [])] == ["r1"] and last.get("counts", {}).get("unsubscribe") == 1, last)
        ok("replies-sort: the opt-out is suppressed at once", "no@example.com" in (home / "gtm-box" / "optouts.csv").read_text() + (home / "context" / "suppression.csv").read_text())
        ok("replies-sort: the digest carries no email address or reply text", "example.com" not in json.dumps(last) and "Tuesday" not in json.dumps(last))
        ok("replies-sort: the bot's webhook gets ids only", ("POST", "/hook", {"hot_reply_ids": ["r1"]}) in Fake.hits)
        ok("replies-sort: a second run finds nothing new (a bad line doesn't wedge it)", rj("replies-sort", env=hook_env)[0] == 0 and dig("replies-sort")[-1]["counts"] == {"new": 0})
        with inbox.open("a") as h:
            h.write(json.dumps({"id": "r4", "lead": "q@example.com", "subject": "Re", "preview": "what is the price"}) + "\n")
        code, line, _ = rj("replies-sort", env={**wenv, "PATH": path_none})
        ok("replies-sort: with no brain the reply goes to the bot unjudged", code == 0 and dig("replies-sort")[-1]["items"][0]["intent"] == "unjudged", line)

        renv = {**wenv, "RADAR_APP_URL": fake_url, "RADAR_DASHBOARD_PASSWORD": "selftest-pw"}
        code, line, out = rj("radar-poll", env=renv)
        last = dig("radar-poll")[-1] if code == 0 else {}
        ok("radar-poll: reads /api/data with the bearer password", ("GET", "/api/data", "Bearer selftest-pw") in Fake.hits)
        ok("radar-poll: keeps the 5, drops the 1, survives a non-number score", code == 0 and [i["id"] for i in last.get("items", [])] == ["1"] and last["counts"] == {"new": 3, "kept": 1}, out[-300:])
        ok("radar-poll: second run sees no new leads", rj("radar-poll", env=renv)[0] == 0 and dig("radar-poll")[-1]["counts"]["new"] == 0)
        ok("radar-poll: blocked without keys, and says so in the digest", rj("radar-poll")[0] == 1 and dig("radar-poll")[-1]["kind"] == "blocked")

        cases = home / "gtm-box" / "speaker" / "cases"; cases.mkdir(parents=True)
        (cases / "show-a.json").write_text(json.dumps({"name": "Main Street Owners", "description": "Interviews business owners", "url": "https://example.com/a"}))
        (cases / "show-b.json").write_text(json.dumps({"name": "Dev tool reviews", "description": "solo reviews"}))
        code, line, out = rj("show-score"); last = dig("shows-score")[-1] if code == 0 else {}
        ok("show-score: keeps the fit show with an angle", code == 0 and [i["id"] for i in last.get("items", [])] == ["show-a"] and last["items"][0]["angle"] == "stub", out[-300:])
        posts = home / "gtm-box" / "skool" / "scrape"; posts.mkdir(parents=True)
        (posts / "posts.json").write_text(json.dumps([{"group": "g", "id": 1, "text": "I need help automating intake", "isOpportunity": True, "url": "https://example.com/s/1"},
                                                      {"group": "g", "id": 2, "text": "hello all", "isOpportunity": False}]))
        code, line, out = rj("skool-score"); last = dig("skool-score")[-1] if code == 0 else {}
        ok("skool-score: scores only the opportunity posts", code == 0 and last.get("counts") == {"new": 1, "kept": 1}, out[-300:])

        sc = home / "tools" / "scrapers" / "demo"; sc.mkdir(parents=True)
        (sc / "SPEC.md").write_text("Target: example list. Fields: name. Rows: 2. Rung: 0.\n")
        code, line, out = rj("scraper-write", "scraper=demo")
        ok("scraper-write: codex writes a scraper whose test passes", code == 0 and (sc / "scrape.py").exists() and "test passes" in line, out[-300:])
        ok("scraper-write: blocked without codex, and says so", rj("scraper-write", "scraper=demo", env={**wenv, "PATH": path_none})[0] == 1 and dig("scraper-write")[-1]["kind"] == "blocked")
        ok("scraper-run: runs the saved scraper", rj("scraper-run", "scraper=demo")[0] == 0 and "demo: 2 rows" in dig("scraper-run")[-1]["note"])
        (home / "tools" / "scrapers" / "REGISTRY.md").write_text("| Scraper | Owner | Target | Rung | Status | Last run | Rows |\n|---|---|---|---|---|---|---|\n| demo | lead | x | 0 | ok | - | 2 |\n| gone | lead | x | 0 | ok | - | 0 |\n")
        code, line, _ = rj("scraper-retest")
        ok("scraper-retest: the missing scraper is reported broken", code == 0 and line == "retested 2, broken 1" and dig("scraper-retest")[-1]["items"][0]["id"] == "gone", line)

        # 6. Orders, the digest, the watchdog.
        st, o = api("POST", url + "/v1/orders", {"type": "scraper-run", "params": {"scraper": "demo"}, "by": "lead"})
        code, line, out = rj("orders")
        ok("orders: a queued order runs and reports done", st == 202 and code == 0 and api("GET", url + f"/v1/orders/{o['id']}")[1].get("status") == "done", out[-300:])
        _, o2 = api("POST", url + "/v1/orders", {"type": "list-load", "params": {"campaign": "test"}, "by": "cold-email"}); rj("orders")
        r2 = api("GET", url + f"/v1/orders/{o2['id']}")[1]
        ok("orders: a held order says held, never done", r2.get("status") == "held" and "cold_email" in r2.get("result", ""), r2)
        _, o3 = api("POST", url + "/v1/orders", {"type": "scraper-run", "params": {"scraper": "x; rm -rf /"}}); rj("orders")
        ok("orders: a hostile parameter fails the order", api("GET", url + f"/v1/orders/{o3['id']}")[1].get("status") == "failed")
        code, line, _ = rj("digest"); st, d = api("GET", url + "/v1/digest?max=5")
        ok("digest: the bot reads counts and hottest-first items", code == 0 and st == 200 and d["items"] and d["items"][0]["kind"] == "replies" and len(d["items"]) <= 5 and "replies-sort" in d["counts"], line)
        ok("digest: no personal data beyond ids and links", "@example.com" not in json.dumps(d))
        code, line, out = rj("watchdog", env={**wenv, "SLACK_ALARM_WEBHOOK_URL": fake_url + "/slack"})
        slack = [h for h in Fake.hits if h[1] == "/slack"]
        ok("watchdog: alarms once on silent roles and the failing job", code == 0 and len(slack) == 1 and "SILENT" in slack[0][2]["text"] and "JOB FAILING radar-poll" not in slack[0][2]["text"], out[-300:])
        rj("radar-poll"); rj("radar-poll")
        (home / "state" / "spend-ledger.jsonl").open("a").write(json.dumps({"t": 0, "day": time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)), "pool": "scrape", "plan": "y", "usd": 5}) + "\n")
        rj("watchdog", env={**wenv, "SLACK_ALARM_WEBHOOK_URL": fake_url + "/slack"})
        slack = [h for h in Fake.hits if h[1] == "/slack"]
        ok("watchdog: second alarm carries only the new problems", len(slack) == 2 and "JOB FAILING radar-poll" in slack[1][2]["text"] and "SILENT" not in slack[1][2]["text"], slack[-1][2] if slack else "")
        ok("watchdog: a pool at its cap two days running alarms", len(slack) == 2 and "POOL SPENT scrape" in slack[1][2]["text"])
        ok("run_job: every run is logged", all((home / "state" / "jobs" / f"{j}.jsonl").exists() for j in ("replies-sort", "radar-poll", "digest", "orders")))

        # 7. think.py's tiers.
        items = tmp / "items.json"; items.write_text(json.dumps([{"id": "a", "text": "hello"}])); outf = tmp / "out.json"
        th = lambda env, *a: run([PY, W / "think.py", "--prompt", "prompts/reply-sort.md", "--in", items, "--out", outf, *a], env=env)
        ok("think: codex first", th(wenv)[1] == "tier codex: 1 judged")
        ok("think: falls to hermes when codex is not asked", th(wenv, "--tiers", "hermes")[1] == "tier hermes: 1 judged" and json.loads(outf.read_text())[0]["why"] == "hermes stub")
        aenv = {**wenv, "PATH": path_none, "MODEL_API_URL": fake_url, "MODEL_API_KEY": "selftest", "MODEL_NAME": "stub", "MODEL_USD_PER_MTOK": "1"}
        ok("think: the metered tier runs under the model pool", th(aenv)[1] == "tier api: 1 judged" and '"pool": "model"' in (home / "state" / "spend-ledger.jsonl").read_text())
        ok("think: the metered tier is held once the pool is spent", th({**aenv, "MODEL_USD_PER_MTOK": "100000"})[0] == 3)
        ok("think: no brain exits 3", th({**wenv, "PATH": path_none})[0] == 3)
        ok("think: an unknown tier name never reaches the metered tier", th(aenv, "--tiers", "grok")[0] == 3)

        # 8. Fail closed: the server dies, every bot guard holds.
        srv.terminate(); srv.wait(timeout=10); srv = None
        ok("server down: suppression held", g("suppression.py", "check", "fine@example.org")[0] == 1)
        ok("server down: spend held", g("spend_guard.py", "run-z", "0.1", "--pool", "scrape")[0] == 1)
        ok("server down: sends stopped", g("send_guard.py", "podcast_pitch")[1] == "stopped")
    finally:
        if srv:
            srv.terminate()
        fake.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{N - len(FAILS)} of {N} checks passed" + (f"; FAILED: {', '.join(FAILS)}" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
