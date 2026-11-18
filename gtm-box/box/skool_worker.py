#!/usr/bin/env python3
"""The hands of the Skool lane: one worker, one Chrome, one account. It spends no model money.

Lead Radar on Railway does the thinking: what to read, who is a lead, what to say, the caps, STOP and On duty. This process
calls out to it for the next step and does that step in the skool Chrome on this computer, where Justin signed the account in
by hand. So the account only ever shows up from one computer, and its cookie never leaves it: a read is a fetch from inside
the signed-in page, the way the site makes it.

It refuses these whatever the radar asks:
- anything while STOP is set, or before Justin's yes, which is the file skool/ON;
- a fetch that isn't a GET to Skool;
- a browser step outside the sender's list, or a page outside Skool;
- any browser step until send_guard has cleared this person for this message type.

A browser check, a sign-in prompt or anything else Skool puts in the way is never worked around. The radar stops reading for
the pass, this writes blocked=1, and the Watchdog tells Justin.

    skool_worker.py serve     run by supervisor
    skool_worker.py status    Chrome, the keys and the radar. Prints no key.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlsplit

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else Path(__file__).resolve().parent))

import beat  # noqa: E402
import send_guard  # noqa: E402

CHROME = os.environ.get("GTM_SKOOL_CHROME") or "http://127.0.0.1:9224"
START = "https://www.skool.com/"
READS = ("www.skool.com", "api2.skool.com")
PAGES = ("www.skool.com",)
STEPS = frozenset({"Page.enable", "Page.navigate", "Page.reload", "Page.captureScreenshot", "Runtime.evaluate",
                   "Input.insertText", "Input.dispatchKeyEvent"})
GATE_SECONDS = 360   # A send takes under a few minutes. The permission ends with it, or with this.
READ_PACE = (1.0, 3.0)  # On top of the radar's own pace: a person's speed, not a crawler's.
POLL_SECONDS = 25
FETCH = """(async (url, accept) => {
  const r = await fetch(url, {credentials: 'include', headers: {accept}});
  const waf = (r.headers.get('x-amzn-waf-action') || '').toLowerCase();
  return {status: r.status, url: r.url, challenge: waf === 'challenge', text: await r.text()};
})"""


GONE = (urllib.error.URLError, OSError, ValueError)  # The other end isn't there, or didn't answer in sense.


def http(method, url, headers=None, body=None, timeout=30):
    """(status, parsed JSON). Standard library only, like the rest of the box."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={**(headers or {}), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}


def keys(path):
    """The three settings this needs from box.env, and nothing else from that file."""
    wanted, out = ("RADAR_URL", "RADAR_DASHBOARD_PASSWORD", "SKOOL_ACCOUNT"), {}
    if Path(path).is_file():
        for line in Path(path).read_text().splitlines():
            key, _, value = line.partition("=")
            if key.strip() in wanted and value.strip():
                out[key.strip()] = value.strip().strip("\"'")
    return {k: os.environ.get(k) or out.get(k, "") for k in wanted}


class Radar:
    def __init__(self, url, password, account):
        self.url, self.account = url.rstrip("/"), account
        self.headers = {"Authorization": f"Bearer {password}"}

    def next(self):
        query = urllib.parse.urlencode({"account": self.account, "wait": POLL_SECONDS})
        return http("GET", f"{self.url}/api/bridge/next?{query}", self.headers, timeout=POLL_SECONDS + 15)[1].get("job")

    def done(self, job_id, result):
        http("POST", f"{self.url}/api/bridge/done", self.headers, {"id": job_id, "result": result}, timeout=60)


class Tab:
    """One tab of its own in the skool Chrome, over its own DevTools socket. It never touches another tab."""

    def __init__(self, base=CHROME):
        self.base, self.ws, self.n, self.target = base, None, 0, None

    def _new(self):
        return http("PUT", f"{self.base}/json/new?{START}", timeout=15)[1]

    async def open(self):
        if self.ws is None:
            import websockets
            self.target = await asyncio.to_thread(self._new)
            self.ws = await websockets.connect(self.target["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024,
                                               open_timeout=30, ping_interval=None)
            await asyncio.sleep(3)  # The first page has to load before a fetch runs from inside it.

    async def call(self, method, params=None, timeout=60):
        await self.open()
        self.n += 1
        await self.ws.send(json.dumps({"id": self.n, "method": method, "params": params or {}}))
        while True:
            m = json.loads(await asyncio.wait_for(self.ws.recv(), timeout))
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(str(m["error"].get("message"))[:200])
                return m.get("result") or {}

    async def reset(self):
        ws, self.ws = self.ws, None
        if ws is not None:
            try:
                await ws.close()
            except Exception:  # A dead socket is what brought us here.
                pass
        if self.target:
            try:
                await asyncio.to_thread(urllib.request.urlopen, f"{self.base}/json/close/{self.target['id']}", timeout=10)
            except GONE:
                pass
            self.target = None


class Worker:
    def __init__(self, radar, reader=None, hands=None, home=None, clock=time.time, sleep=asyncio.sleep, pace=READ_PACE,
                 write_beat=None):
        self.radar, self.reader, self.hands = radar, reader or Tab(), hands or Tab()
        self.home, self.clock, self.sleep, self.pace = Path(home or HOME), clock, sleep, pace
        self.beat = write_beat or beat.write
        self.gate_until = 0.0
        self.reads = 0

    def off(self):
        if (self.home / "STOP").exists():
            return "STOP is set"
        if not (self.home / "skool" / "ON").exists():
            return "Justin hasn't turned the Skool lane on"
        return None

    async def handle(self, job):
        why = self.off()
        if why:
            return {"ok": False, "why": why, "error": why}
        kind, payload = job.get("kind"), job.get("payload") or {}
        if kind == "fetch":
            return await self.fetch(payload)
        if kind == "begin":
            return self.begin(payload)
        if kind == "cdp":
            return await self.step(payload)
        if kind == "end":
            self.gate_until = 0.0
            return {"ok": True}
        return {"error": f"unknown step: {kind}"}

    async def fetch(self, p):
        url = str(p.get("url") or "")
        u = urlsplit(url)
        if u.scheme != "https" or u.hostname not in READS:
            return {"error": "not a Skool address"}
        await self.sleep(random.uniform(*self.pace))
        accept = str(p.get("accept") or "text/html")
        expression = f"{FETCH}({json.dumps(url)}, {json.dumps(accept)})"
        got = await self.reader.call("Runtime.evaluate", {"expression": expression, "awaitPromise": True,
                                                          "returnByValue": True}, timeout=90)
        if got.get("exceptionDetails"):
            return {"error": "the page could not fetch that"}
        value = (got.get("result") or {}).get("value") or {}
        self.reads += 1
        if value.get("challenge"):
            self.beat("skool", "Skool asked for a browser check. Reading stopped for this pass.", ["blocked=1"])
        return value

    def begin(self, p):
        who = str(p.get("who") or "").strip()
        if not who:
            return {"ok": False, "why": "no name to check against the suppression list"}
        why = send_guard.gate(str(p.get("type") or ""), who)
        if why:
            return {"ok": False, "why": why, "final": why.startswith("on the suppression list")}
        self.gate_until = self.clock() + GATE_SECONDS
        return {"ok": True}

    async def step(self, p):
        method, params = p.get("method"), p.get("params") or {}
        if self.clock() >= self.gate_until:
            return {"error": "the box hasn't cleared this person"}
        if method not in STEPS:
            return {"error": f"step not allowed: {method}"}
        if method == "Page.navigate":
            u = urlsplit(str(params.get("url") or ""))
            if u.scheme != "https" or u.hostname not in PAGES:
                return {"error": "not a Skool page"}
        return {"result": await self.hands.call(method, params)}

    async def once(self):
        """One turn: a step from the radar, done and answered. False when there's nothing to do."""
        if self.off():
            return False
        job = await asyncio.to_thread(self.radar.next)
        if not job:
            return False
        try:
            result = await self.handle(job)
        except Exception as exc:  # A dead tab or a slow page. The radar reads this as "couldn't", never as done.
            result = {"ok": False, "error": type(exc).__name__, "why": type(exc).__name__}
            await self.reader.reset()
            await self.hands.reset()
        await asyncio.to_thread(self.radar.done, job["id"], result)
        return True

    async def serve(self):
        while True:
            if self.off():
                await self.sleep(15)
                continue
            try:
                await self.once()
            except GONE:
                await self.sleep(10)  # The radar is redeploying. Nothing is lost: it re-reads from its last full window.


def status(cfg, base=CHROME):
    lines = [f"{k}: {'set' if cfg[k] else 'MISSING'}" for k in cfg]
    try:
        info = http("GET", f"{base}/json/version", timeout=5)[1]
        tabs = [t for t in http("GET", f"{base}/json/list", timeout=5)[1] if t.get("type") == "page"]
        lines.append(f"chrome: {info.get('Browser')}, {len(tabs)} tab(s), {sum('skool.com' in t.get('url', '') for t in tabs)} on Skool")
    except GONE:
        lines.append(f"chrome: nothing on {base}")
    try:
        code = http("GET", cfg["RADAR_URL"].rstrip("/") + "/api/send/status",
                    {"Authorization": f"Bearer {cfg['RADAR_DASHBOARD_PASSWORD']}"}, timeout=15)[0]
        lines.append(f"radar: {code}")
    except GONE:
        lines.append("radar: unreachable")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("serve", "status"))
    args = ap.parse_args(argv)
    cfg = keys(HOME / "box.env")
    if args.cmd == "status":
        print("\n".join(status(cfg)))
        return 0
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        raise SystemExit(f"box.env is missing {', '.join(missing)}")
    asyncio.run(Worker(Radar(cfg["RADAR_URL"], cfg["RADAR_DASHBOARD_PASSWORD"], cfg["SKOOL_ACCOUNT"])).serve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
