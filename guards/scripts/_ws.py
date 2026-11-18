"""Shared: find the workspace, and the worker when the bot runs in worker mode.

The pack lives at <workspace>/repo/, so the workspace is three levels up from repo/guards/scripts/. BOT_HOME overrides it
(tests use a scratch folder).

Worker mode: when WORKER_URL and WORKER_TOKEN are set (env, or <workspace>/.secrets/worker.env), the worker is the one
home of the guard state (suppression, spend pools, STOP, standing approvals) and the guards ask it. Anything that goes
wrong talking to it counts as held or stopped: the guards fail closed. WORKER_LOCAL=1 forces local mode (the worker's
own server sets it, so the worker reads its own files)."""
import json, os, pathlib, urllib.request, urllib.error

WS = pathlib.Path(os.environ.get("BOT_HOME") or pathlib.Path(__file__).resolve().parents[3])


def p(*parts): return WS.joinpath(*parts)


def norm(s): return " ".join("".join(c.lower() if c.isalnum() or c in "@." else " " for c in s).split())


class WorkerDown(Exception):
    pass


def worker():
    """(url, token) in worker mode, else None."""
    if os.environ.get("WORKER_LOCAL") == "1":
        return None
    url, tok = os.environ.get("WORKER_URL", ""), os.environ.get("WORKER_TOKEN", "")
    f = p(".secrets", "worker.env")
    if not (url and tok) and f.is_file():
        for line in f.read_text(errors="ignore").splitlines():
            k, _, v = line.partition("=")
            if k.strip() == "WORKER_URL" and not url: url = v.strip().strip('"')
            if k.strip() == "WORKER_TOKEN" and not tok: tok = v.strip().strip('"')
    return (url.rstrip("/"), tok) if url and tok else None


def call(method, path, payload=None, timeout=15, raw=False):
    w = worker()
    if not w:
        raise WorkerDown("not in worker mode")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(w[0] + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {w[1]}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return body if raw else json.loads(body or "{}")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise WorkerDown(str(e)[:120])


def stopped():
    """Local STOP, or the worker's STOP, or a worker that can't be reached (fail closed)."""
    if p("context", "STOP").exists():
        return True
    if worker():
        try:
            return bool(call("GET", "/v1/state").get("stop"))
        except WorkerDown:
            return True
    return False
