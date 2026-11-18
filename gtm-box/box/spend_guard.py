#!/usr/bin/env python3
"""The box's daily spend cap and Haiku-only rule.

Anthropic offers monthly limits per organization or workspace, not a daily limit on a key. So every profile talks to
this gate on 127.0.0.1 instead of Anthropic, and only this process uses the real key. It sends every request as
Haiku 5.5, adds up each reply's cost from the usage Anthropic returns, and refuses once the day's cap is reached. The
count resets at midnight UTC. If the gate is down, nothing reaches Anthropic.

    python3 spend_guard.py serve     # run by supervisor on the box
    python3 spend_guard.py status    # today's spend
"""
import http.client
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME = Path(os.environ.get("GTM_HOME") or Path.home() / ".gtm-box")
PORT = int(os.environ.get("GTM_GUARD_PORT") or 8788)
CAP = float(os.environ.get("GTM_DAILY_CAP") or 5)
MODEL = "claude-haiku-5-5"
UPSTREAM = "api.anthropic.com"
# Dollars per million tokens, Haiku 5.5 published rates. Prompts over 100K tokens cost the higher pair.
RATES = (0.10, 0.50)
LONG_RATES = (0.50, 2.50)
LONG_PROMPT = 100_000
# Anything else, batches above all, would spend money the count can't see.
ALLOWED = ("/v1/messages", "/v1/messages/count_tokens")
DROP = {"host", "x-api-key", "authorization", "content-length", "accept-encoding", "connection", "transfer-encoding"}
HOP = {"connection", "content-length", "content-encoding", "transfer-encoding", "keep-alive"}


def cost(usage):
    """Dollars for one reply. Cache writes are 1.25x input (2x for the 1 hour cache), cache reads 0.1x."""
    fresh = usage.get("input_tokens") or 0
    wrote = usage.get("cache_creation_input_tokens") or 0
    read = usage.get("cache_read_input_tokens") or 0
    detail = usage.get("cache_creation") or {}
    hour = detail.get("ephemeral_1h_input_tokens") or 0
    in_rate, out_rate = LONG_RATES if fresh + wrote + read > LONG_PROMPT else RATES
    units = fresh + (wrote - hour) * 1.25 + hour * 2 + read * 0.1
    return (units * in_rate + (usage.get("output_tokens") or 0) * out_rate) / 1_000_000


class Ledger:
    """One small JSON file a day, so a restart keeps the count."""

    def __init__(self, folder, cap=CAP):
        self.folder = Path(folder)
        self.cap = cap
        self.lock = threading.Lock()

    def path(self, when=None):
        return self.folder / f"{time.strftime('%Y-%m-%d', time.gmtime(when))}.json"

    def read(self, when=None):
        try:
            return json.loads(self.path(when).read_text())
        except (OSError, ValueError):
            return {"spent": 0.0, "requests": 0, "refused": 0}

    def spent(self, when=None):
        return self.read(when)["spent"]

    def _save(self, day, when):
        self.folder.mkdir(parents=True, exist_ok=True)
        target = self.path(when)
        scratch = target.with_suffix(".tmp")
        scratch.write_text(json.dumps(day))
        scratch.replace(target)

    def add(self, dollars, when=None):
        with self.lock:
            day = self.read(when)
            day["spent"] = round(day["spent"] + dollars, 6)
            day["requests"] += 1
            self._save(day, when)

    def refuse(self, when=None):
        with self.lock:
            day = self.read(when)
            day["refused"] += 1
            self._save(day, when)


class Usage:
    """Reads the usage out of a reply as it passes, streamed or not."""

    def __init__(self):
        self.usage = {}
        self.buffer = b""

    def feed(self, chunk):
        self.buffer += chunk
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            if line.startswith(b"data:"):
                self.event(line[5:])

    def event(self, raw):
        try:
            data = json.loads(raw)
        except ValueError:
            return
        if not isinstance(data, dict):
            return
        found = (data.get("message") or {}).get("usage") if data.get("type") == "message_start" else data.get("usage")
        if isinstance(found, dict):
            self.usage.update({k: v for k, v in found.items() if v is not None})

    def finish(self):
        if self.buffer.strip():
            self.event(self.buffer)
            self.buffer = b""
        return self.usage


def allowed(route):
    return route in ALLOWED or route == "/v1/models" or route.startswith("/v1/models/")


def keep_only_haiku(body):
    """Whatever a profile asks for, this box runs Haiku 5.5. Hermes' side jobs ask for an older Haiku by default."""
    request = json.loads(body)
    asked = request.get("model")
    if asked == MODEL:
        return body, asked
    request["model"] = MODEL
    return json.dumps(request).encode(), asked


def handler(ledger, key):
    class Gate(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def refuse(self, status, kind, message):
            body = json.dumps({"type": "error", "error": {"type": kind, "message": message}}).encode()
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.send_header("retry-after", "3600")
            self.end_headers()
            self.wfile.write(body)

        def forward(self):
            size = int(self.headers.get("content-length") or 0)
            body = self.rfile.read(size) if size else b""
            route = self.path.split("?")[0]
            if not allowed(route):
                return self.refuse(403, "permission_error", f"the GTM box gate doesn't allow {route}")
            counted = route == "/v1/messages"
            if body and route.startswith("/v1/messages"):
                body, asked = keep_only_haiku(body)
                if asked != MODEL:
                    print(f"{time.strftime('%H:%M:%S')} {asked} sent as {MODEL}", flush=True)
            if counted and ledger.spent() >= ledger.cap:
                ledger.refuse()
                return self.refuse(429, "rate_limit_error", f"the GTM box daily cap of ${ledger.cap:g} is reached")
            headers = {k: v for k, v in self.headers.items() if k.lower() not in DROP}
            headers["x-api-key"] = key
            upstream = http.client.HTTPSConnection(UPSTREAM, timeout=600)
            try:
                upstream.request(self.command, self.path, body, headers)
                reply = upstream.getresponse()
                self.send_response(reply.status)
                for name, value in reply.getheaders():
                    if name.lower() not in HOP:
                        self.send_header(name, value)
                self.send_header("transfer-encoding", "chunked")
                self.end_headers()
                usage = Usage()
                while chunk := reply.read1(65536):
                    usage.feed(chunk)
                    self.wfile.write(b"%x\r\n%s\r\n" % (len(chunk), chunk))
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                seen = usage.finish()
                if counted and seen:
                    ledger.add(cost(seen))
            finally:
                upstream.close()

        do_POST = do_GET = forward

    return Gate


def read_key(path):
    for line in Path(path).read_text().splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def main():
    ledger = Ledger(HOME / "spend")
    if sys.argv[1:] == ["status"]:
        day = ledger.read()
        print(f"today ${day['spent']:.4f} of ${ledger.cap:g}, {day['requests']} requests, {day['refused']} refused")
        return 0
    key = read_key(HOME / "box.env")
    if not key:
        raise SystemExit("no ANTHROPIC_API_KEY in box.env")
    ThreadingHTTPServer(("127.0.0.1", PORT), handler(ledger, key)).serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
