#!/usr/bin/env python3
"""Hermes job script for `content`: bring the newest drafted posts into the box's content queue, from the box itself.

The box keeps its own clone of the content repo (CONTENT_REPO_REMOTE, set at intake), reached through a deploy key, and
copies drafts/<newest>/posts.md to queue/content/<date>-posts.md. It is a copy for the report: the repo stays the source,
and nothing here publishes. Its stdout is the job's whole report.

    python3 content_pull.py            # pull, then queue the newest posts.md
    python3 content_pull.py setup      # print the one-time steps for the deploy key
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("GTM_HOME") or "/workspace/revenue-partnerships/gtm-box")
REPO = Path(os.environ.get("AI_GUY_CONTENT") or HOME / "content-repo")
REMOTE = os.environ.get("CONTENT_REPO_REMOTE") or os.environ.get("AI_GUY_CONTENT_REMOTE") or ""  # git URL, set at intake
SSH_HOST = os.environ.get("CONTENT_REPO_SSH_HOST") or "github.com-content"  # the SSH config Host alias for the deploy key
SETUP = f"""One-time, after Justin's yes:
1. On the box: ssh-keygen -t ed25519 -N '' -C gtm-box-content -f ~/.ssh/content-repo
2. Add ~/.ssh/content-repo.pub to the content repo as a deploy key, with write access (the Daily content job pushes)
3. In ~/.ssh/config, a Host {SSH_HOST} block with HostName github.com and IdentityFile ~/.ssh/content-repo
4. Set CONTENT_REPO_REMOTE to git@{SSH_HOST}:<owner>/<repo>.git, run this script once, then turn on Content pull"""


def git(*args, cwd=None, run=subprocess.run):
    done = run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=120)
    if done.returncode:
        raise RuntimeError(f"git {args[0]} failed: {(done.stderr or done.stdout).strip()[:300]}")
    return done.stdout


def sync(run=subprocess.run):
    if (REPO / ".git").is_dir():
        git("pull", "--ff-only", "--quiet", cwd=REPO, run=run)
    else:
        if not REMOTE:
            raise RuntimeError("CONTENT_REPO_REMOTE isn't set: set it at intake (see setup)")
        REPO.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--quiet", REMOTE, str(REPO), run=run)


def queue_newest():
    folders = sorted(p for p in (REPO / "drafts").glob("20*") if p.is_dir())
    if not folders:
        return "no drafts folder in the content repo"
    newest = folders[-1]
    posts = newest / "posts.md"
    if not posts.is_file():
        return f"no posts in {newest.name}"
    target = HOME / "queue" / "content" / f"{newest.name}-posts.md"
    if target.exists():
        return f"already there: {target.name}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(posts, target)
    return f"queued {target.name}"


def main(argv, run=subprocess.run):
    if argv[:1] == ["setup"]:
        print(SETUP)
        return 0
    if (HOME / "STOP").exists():
        print("STOP is set: nothing pulled")
        return 0
    try:
        sync(run=run)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"blocked: {error}. Run `content_pull.py setup` for the deploy key steps")
        return 1
    print(queue_newest())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
