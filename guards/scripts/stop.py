#!/usr/bin/env python3
"""The STOP switch, on both sides.

    stop.py on "<who said so>"     creates context/STOP here and on the worker (worker mode)
    stop.py off "<who said so>"    removes both. Only on Justin's word in chat
    stop.py status                 here and on the worker

If the worker can't be reached, the local STOP still stops the bot (and every guard already holds while the worker is
unreachable); the bot then tells Justin in Slack that the worker's STOP wasn't delivered, so he can pause the sending
tools by hand."""
import sys, time
import _ws


def main(a):
    if not a:
        print(__doc__); return 2
    f = _ws.p("context", "STOP")
    if a[0] in ("on", "off"):
        who = a[1] if len(a) > 1 else "bot"
        if a[0] == "on":
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"stopped by {who} at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        elif f.exists():
            f.unlink()
        if _ws.worker():
            try:
                r = _ws.call("POST", "/v1/stop", {"on": a[0] == "on", "by": who})
                print(f"local: {a[0]}; worker: {'on' if r.get('stop') else 'off'}"); return 0
            except _ws.WorkerDown as e:
                print(f"local: {a[0]}; worker: NOT DELIVERED ({e}). Tell Justin in Slack now."); return 1
        print(f"local: {a[0]}"); return 0
    if a[0] == "status":
        local = f.exists()
        if _ws.worker():
            try:
                print(f"local: {'on' if local else 'off'}; worker: {'on' if _ws.call('GET', '/v1/state').get('stop') else 'off'}")
            except _ws.WorkerDown as e:
                print(f"local: {'on' if local else 'off'}; worker: unreachable ({e}), guards hold")
        else:
            print(f"local: {'on' if local else 'off'}")
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
