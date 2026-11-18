#!/usr/bin/env bash
# Install the revenue worker on a fresh Ubuntu server (a DigitalOcean droplet, or a computer that can keep a signed-in
# browser for the Skool read). Run as root from the unpacked pack:  bash worker/install.sh
# It installs nothing paid and turns every job off. Justin's steps (keys, Codex sign-in, the HTTPS name) come after.
set -euo pipefail
PACK="$(cd "$(dirname "$0")/.." && pwd)"
HOME_DIR="${WORKER_HOME:-/opt/revenue-worker}"
PORT="${WORKER_PORT:-8787}"

[ "$(date +%Z)" = "UTC" ] || { echo "Set this server to UTC first (job times are UTC): timedatectl set-timezone UTC" >&2; exit 1; }
apt-get update -qq && apt-get install -y -qq python3 python3-venv cron curl ca-certificates >/dev/null
id revworker >/dev/null 2>&1 || useradd --system --create-home --shell /usr/sbin/nologin revworker
mkdir -p "$HOME_DIR"/{context,state,orders,digest/inbox,log,tools/scrapers,.secrets}
[ -d "$HOME_DIR/gtm-box" ] || cp -r "$PACK/gtm-box" "$HOME_DIR/gtm-box"
# -L too: on a fresh server the link dangles until the list arrives, and -e alone then fails a second run.
[ -e "$HOME_DIR/gtm-box/suppression.csv" ] || [ -L "$HOME_DIR/gtm-box/suppression.csv" ] || ln -s ../context/suppression.csv "$HOME_DIR/gtm-box/suppression.csv"
[ -f "$HOME_DIR/tools/scrapers/REGISTRY.md" ] || printf '| Scraper | Owner | Target | Rung | Status | Last run | Rows |\n|---|---|---|---|---|---|---|\n' > "$HOME_DIR/tools/scrapers/REGISTRY.md"
# Every job off until Justin says which go on (context/worker-jobs-on.md).
if [ ! -f "$HOME_DIR/context/worker-jobs-on.md" ]; then
  python3 -c "import json,sys;print('\n'.join(f'{k}: off' for k in json.load(open(sys.argv[1]))['jobs']))" "$PACK/worker/jobs.json" > "$HOME_DIR/context/worker-jobs-on.md"
fi
[ -f "$HOME_DIR/context/spend-approvals.md" ] || printf 'pool scrape: daily 5   # Justin 2026-11-12: "Yes, $5 a day cap"\n' > "$HOME_DIR/context/spend-approvals.md"
touch "$HOME_DIR/context/standing-approvals.md"
# Keys: names from worker/worker.env.example; values only by Justin's hidden prompt into /etc/revenue-worker.env.
if [ ! -f /etc/revenue-worker.env ]; then
  { echo "WORKER_HOME=$HOME_DIR"; echo "WORKER_TOKEN=$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')"; } > /etc/revenue-worker.env
fi
# root owns the key file; the revworker group may read it, because the cron jobs run as revworker and source it.
# (At mode 600 root-only, every cron job ran with no keys and no WORKER_HOME.)
chown root:revworker /etc/revenue-worker.env; chmod 640 /etc/revenue-worker.env
chown -R revworker: "$HOME_DIR"; chmod 700 "$HOME_DIR/.secrets"

cat > /etc/systemd/system/revenue-worker.service <<UNIT
[Unit]
Description=Revenue worker API (GrokBot's worker)
After=network-online.target
[Service]
User=revworker
EnvironmentFile=/etc/revenue-worker.env
ExecStart=/usr/bin/python3 $PACK/worker/server.py --host 127.0.0.1 --port $PORT
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload && systemctl enable --now revenue-worker
WORKER_HOME="$HOME_DIR" python3 "$PACK/worker/run_job.py" --crontab | crontab -u revworker -
sleep 1; curl -fsS "http://127.0.0.1:$PORT/health" && echo
echo "Installed. Every job is off. Next: HTTPS in front of port $PORT (worker/README.md), the keys, then switch jobs on."
echo "Codex: install it for every user (npm install -g @openai/codex), then sign in AS revworker, or the jobs can't see the sign-in:"
echo "  sudo -u revworker -H codex login --device-auth"
echo "The bot's WORKER_TOKEN is in /etc/revenue-worker.env (root and revworker only). Give it to the bot by its hidden prompt; never paste it in chat."
