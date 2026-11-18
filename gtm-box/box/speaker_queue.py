"""Runs before the podcast follow-up's agent starts: preflight, the suppression scan, then the research runner's state.
Hermes puts this stdout in the job's prompt, so a held draft or a stuck runner reaches the agent without it having to look."""
import os
import subprocess
import sys
from pathlib import Path

BOX_HOME = "/workspace/revenue-partnerships/gtm-box"


def run(*args):
    done = subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=120)
    return (done.stdout + done.stderr).strip()


print(run(f"{BOX_HOME}/box/preflight.py", "podcast"))
print(run(f"{BOX_HOME}/box/preflight.py", "podcast"))
print(run(f"{BOX_HOME}/box/suppression.py", "scan"))
print("Research runner:", run(os.environ.get("SPEAKER_RUNNER") or str(Path.home() / "speakeragent" / "runtime" / "daily.py"), "status", "--workspace", f"{BOX_HOME}/speaker"))
