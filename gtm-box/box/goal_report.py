"""Hermes job script: the evening report, with no model. Its stdout goes to Slack as it stands."""
import subprocess
import sys

raise SystemExit(subprocess.call([sys.executable, "/workspace/revenue-partnerships/gtm-box/box/goal.py", "report"]))
