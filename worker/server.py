#!/usr/bin/env python3
"""The worker's door: one small authenticated HTTP API the GrokBot calls. Standard library only.

    WORKER_HOME=/opt/revenue-worker WORKER_TOKEN=... python3 worker/server.py [--port 8787] [--host 127.0.0.1]

The worker is the one home of the guard state when the bot runs in worker mode: the suppression list (and the engine's
opt-out overlay), the spend pools and ledger, STOP, and the standing approvals. The bot's guard scripts call this API
and hold when it can't be reached. Guard logic is the pack's own guards/scripts, run here in local mode.

Routes (all but /health need `Authorization: Bearer $WORKER_TOKEN`):
    GET  /health                         {"ok": true}
    GET  /v1/state                       {"stop": bool}
    POST /v1/stop                        {"on": true|false, "by": "..."}
    POST /v1/suppression/check           {"who": "..."}                 -> {"result": "clear"|"held"}
    POST /v1/suppression/add             {"who": "...", "reason": "..."}
    GET  /v1/suppression.csv             the list, for the bot's engine cache (never printed by the bot)
    POST /v1/spend                       {"plan": "...", "usd": 0.5, "pool": "scrape"|null} -> {"result": "approved"|"held"}
    GET  /v1/spend/today                 what each pool spent today
    GET  /v1/approvals                   context/standing-approvals.md as text
    POST /v1/beat                        {"role": "...", "line": "...", "counts": {...}}
    POST /v1/orders                      {"type": "<job in jobs.json>", "params": {...}, "by": "<role>"} -> {"id": ...}
    GET  /v1/orders/<id>                 the order and its result summary; status queued, running, done, failed, or
                                         held (the job was off, stopped, or waiting on an approval: it did not run)
    GET  /v1/digest?max=N                the compact digest the bot reads (counts plus items needing judgment)
"""
import hmac, json, os, re, subprocess, sys, time, uuid, pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOME = pathlib.Path(os.environ.get("WORKER_HOME", "/opt/revenue-worker"))
PACK = pathlib.Path(__file__).resolve().parents[1]
GUARDS = PACK / "guards" / "scripts"
TOKEN = os.environ.get("WORKER_TOKEN", "")
JOBS = json.loads((PACK / "worker" / "jobs.json").read_text())["jobs"]
MAX_BODY = 64 * 1024


def guard(script, *args):
    env = {k: v for k, v in os.environ.items() if k not in ("WORKER_URL", "WORKER_TOKEN")}
    env["BOT_HOME"] = str(HOME)
    env.setdefault("GTM_HOME", str(HOME / "gtm-box"))
    r = subprocess.run([sys.executable, str(GUARDS / script), *map(str, args)], capture_output=True, text=True, env=env, timeout=60)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


class H(BaseHTTPRequestHandler):
    server_version = "revenue-worker/1"

    def log_message(self, fmt, *a):  # one line per call, no bodies
        sys.stderr.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), fmt % a))

    def send(self, code, obj, ctype="application/json"):
        body = obj.encode() if isinstance(obj, str) else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authed(self):
        got = self.headers.get("Authorization", "")
        return bool(TOKEN) and hmac.compare_digest(got.encode(), f"Bearer {TOKEN}".encode())

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("body too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        try:
            return self._get()
        except (ValueError, TypeError, AttributeError):  # bad input is a 400, never a dropped connection
            return self.send(400, {"error": "bad request"})

    def do_POST(self):
        try:
            return self._post()
        except (ValueError, TypeError, AttributeError):
            return self.send(400, {"error": "bad request"})

    def _get(self):
        u = urlparse(self.path)
        if u.path == "/health":
            return self.send(200, {"ok": True})
        if not self.authed():
            return self.send(401, {"error": "unauthorized"})
        if u.path == "/v1/state":
            return self.send(200, {"stop": (HOME / "context" / "STOP").exists()})
        if u.path == "/v1/suppression.csv":
            # The list plus the engine's opt-out overlay (gtm-box/optouts.csv), merged, so the bot's engine copy is whole.
            f, o = HOME / "context" / "suppression.csv", HOME / "gtm-box" / "optouts.csv"
            lines = f.read_text().splitlines() if f.exists() else []
            if not lines or not lines[0].lower().startswith("kind,"):
                lines = ["kind,value,reason"] + lines
            if o.exists():
                lines += [l for l in o.read_text().splitlines()[1:] if l.strip()]
            return self.send(200, "\n".join(lines) + "\n", "text/csv")
        if u.path == "/v1/approvals":
            f = HOME / "context" / "standing-approvals.md"
            return self.send(200, f.read_text() if f.exists() else "", "text/plain")
        if u.path == "/v1/spend/today":
            env = {k: v for k, v in os.environ.items() if k not in ("WORKER_URL", "WORKER_TOKEN")}
            r = subprocess.run([sys.executable, str(GUARDS / "spend_guard.py"), "today"], capture_output=True, text=True,
                               env={**env, "BOT_HOME": str(HOME)}, timeout=60)
            return self.send(200, {"today": r.stdout.strip().splitlines()})
        if u.path.startswith("/v1/orders/"):
            oid = u.path.rsplit("/", 1)[1]
            if not re.fullmatch(r"[0-9a-f]{12}", oid):
                return self.send(400, {"error": "bad id"})
            f = HOME / "orders" / f"{oid}.json"
            return self.send(200, json.loads(f.read_text())) if f.exists() else self.send(404, {"error": "no such order"})
        if u.path == "/v1/digest":
            n = int((parse_qs(u.query).get("max") or ["40"])[0])
            f = HOME / "digest" / "latest.json"
            d = json.loads(f.read_text()) if f.exists() else {"built": None, "counts": {}, "items": []}
            d["items"] = d.get("items", [])[:max(1, min(n, 200))]
            return self.send(200, d)
        return self.send(404, {"error": "not found"})

    def _post(self):
        u = urlparse(self.path)
        if not self.authed():
            return self.send(401, {"error": "unauthorized"})
        try:
            b = self.body()
        except (ValueError, json.JSONDecodeError):
            return self.send(400, {"error": "bad json"})
        if not isinstance(b, dict):
            return self.send(400, {"error": "body must be a JSON object"})
        if u.path == "/v1/stop":
            f = HOME / "context" / "STOP"
            if b.get("on"):
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(f"stopped by {str(b.get('by', 'bot'))[:60]} at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
            elif f.exists():
                f.unlink()  # only the switch file; Justin's word, relayed by the bot
            return self.send(200, {"stop": f.exists()})
        if u.path == "/v1/suppression/check":
            code, out = guard("suppression.py", "check", str(b.get("who", ""))[:500])
            return self.send(200, {"result": "clear" if code == 0 else "held"})
        if u.path == "/v1/suppression/add":
            code, out = guard("suppression.py", "add", str(b.get("who", ""))[:500], str(b.get("reason", "said no"))[:200])
            return self.send(200 if code == 0 else 500, {"result": "added" if code == 0 else "failed"})
        if u.path == "/v1/spend":
            args = [str(b.get("plan", "plan"))[:80], str(float(b.get("usd", 0)))]
            if b.get("pool"):
                args += ["--pool", str(b["pool"])[:40]]
            code, out = guard("spend_guard.py", *args)
            return self.send(200, {"result": "approved" if code == 0 else "held"})
        if u.path == "/v1/beat":
            counts = [f"{k}={int(v)}" for k, v in (b.get("counts") or {}).items() if re.fullmatch(r"[a-z_]{1,20}", k)]
            code, _ = guard("beat.py", "write", str(b.get("role", "?"))[:40], str(b.get("line", ""))[:300], *counts)
            return self.send(200, {"result": "ok" if code == 0 else "failed"})
        if u.path == "/v1/orders":
            t = str(b.get("type", ""))
            if t not in JOBS or not JOBS[t].get("orderable"):
                return self.send(400, {"error": "unknown or not orderable job", "orderable": sorted(k for k, v in JOBS.items() if v.get("orderable"))})
            oid = uuid.uuid4().hex[:12]
            d = HOME / "orders"; d.mkdir(parents=True, exist_ok=True)
            (d / f"{oid}.json").write_text(json.dumps({"id": oid, "type": t, "params": b.get("params") if isinstance(b.get("params"), dict) else {}, "by": str(b.get("by", "bot"))[:40],
                                                      "status": "queued", "t": int(time.time())}))
            return self.send(202, {"id": oid, "status": "queued"})
        return self.send(404, {"error": "not found"})


def main():
    if not TOKEN or len(TOKEN) < 24:
        sys.exit("WORKER_TOKEN must be set (24+ characters)")
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8787
    host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "127.0.0.1"
    for d in ("context", "state", "orders", "digest/inbox", "log"):
        (HOME / d).mkdir(parents=True, exist_ok=True)
    print(f"revenue-worker on {host}:{port}, home {HOME}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()


if __name__ == "__main__":
    main()
