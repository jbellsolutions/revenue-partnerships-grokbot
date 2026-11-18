#!/usr/bin/env python3
"""Create a local campaign scaffold. No network, workers, paid calls or scheduler."""
import argparse
import copy
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

KIT = Path(__file__).resolve().parents[1]


def normalize_website(raw):
    raw = raw.strip()
    if not raw or any(c.isspace() for c in raw):
        raise ValueError('Provide one website URL without whitespace.')
    if '://' not in raw:
        raw = 'https://' + raw
    u = urlsplit(raw)
    if u.scheme not in ('http', 'https') or not u.hostname:
        raise ValueError('The website must use http or https and include a hostname.')
    if u.username or u.password or u.query or u.fragment:
        raise ValueError('Do not include credentials, queries or fragments in the website scope.')
    host = u.hostname.encode('idna').decode('ascii').lower()
    if not host or any(c in host for c in '\\/@'):
        raise ValueError('Invalid website hostname.')
    port = u.port  # raises ValueError for an invalid port
    if ':' in host:
        host = '[' + host + ']'
    if port is not None and not ((u.scheme == 'https' and port == 443) or (u.scheme == 'http' and port == 80)):
        host += ':' + str(port)
    return urlunsplit((u.scheme, host, u.path.rstrip('/'), '', ''))


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--website', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        website = normalize_website(args.website)
        out = args.out.expanduser().resolve()
        if out == KIT or KIT in out.parents or out in KIT.parents:
            raise ValueError('Choose a separate campaign directory outside the kit.')
        if out.exists():
            cp_path = out / 'config/campaign.json'
            if not cp_path.is_file():
                raise ValueError('Destination already exists without a campaign config; choose a new directory.')
            existing = read_json(cp_path)
            if existing.get('website') != website:
                raise ValueError('Destination belongs to another website scope; no files were changed.')
            required = ['AGENTS.md', 'board.json', 'checkpoint.json', 'config/authority.json']
            missing = [x for x in required if not (out / x).is_file()]
            if missing:
                raise ValueError('Existing project is incomplete; reconcile it before reuse: ' + ', '.join(missing))
            print(json.dumps({'status': 'reused_without_changes', 'project': str(out), 'website': website}))
            return 0

        out.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.seo-campaign-init-', dir=out.parent))
        try:
            shutil.copytree(KIT, stage, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            now = datetime.now(timezone.utc).isoformat()
            cid = 'seo-' + hashlib.sha256(website.encode()).hexdigest()[:12]
            cfg = read_json(KIT / 'config/campaign.example.json')
            cfg.update(website=website, campaign_id=cid)
            # No start/expiry is invented: the owner activates the actual work window.
            write_json(stage / 'config/campaign.json', cfg)
            grant = read_json(KIT / 'config/authority.example.json')
            grant['scope']['website'] = website
            write_json(stage / 'config/authority.json', grant)
            board = read_json(KIT / 'templates/board.json')
            board['project_key'] = website
            initial = next(t for t in board['tasks'] if t['id'] == 'project-bootstrap')
            initial.update(status='DONE', outputs=['board.json', 'checkpoint.json'],
                           evidence=['operations/bootstrap-receipt.json'])
            for task in board['tasks']:
                if task['status'] == 'INBOX' and task['depends_on'] == ['project-bootstrap']:
                    task['status'] = 'READY'
            write_json(stage / 'board.json', board)
            record_shapes = read_json(KIT / 'templates/records.json')
            checkpoint = copy.deepcopy(record_shapes['checkpoint'])
            checkpoint.update(mission_id=cid, updated_at=now, owner='campaign_director',
                              outputs=['board.json', 'registry/roles.json'],
                              next_action='Read owner authority and inspect the live website; populate brief and connections. No runner configured.')
            write_json(stage / 'checkpoint.json', checkpoint)
            write_json(stage / 'registry/roles.json', read_json(KIT / 'config/roles.json'))
            write_json(stage / 'registry/workers.json', {'workers': []})
            write_json(stage / 'registry/jobs.json', {'status': 'not_configured', 'jobs': []})
            write_json(stage / 'registry/external-ids.json', {'project': None, 'tasks': {}, 'jobs': {}})
            write_json(stage / 'connections.json', {'connections': []})
            write_json(stage / 'knowledge/brief.json', {'website': website, 'business_model': None, 'verified_facts': [], 'hypotheses': [], 'unknowns': ['Owner authority, business facts, live site state and account capabilities require discovery.']})
            for name, key in [('facts', 'facts'), ('inventory', 'pages'), ('page-map', 'pages')]:
                write_json(stage / f'knowledge/{name}.json', {key: []})
            write_json(stage / 'metrics/experiments.json', {'experiments': []})
            write_json(stage / 'operations/stop.json', {'requested': False, 'reason': None, 'requested_at': None})
            write_json(stage / 'operations/budget.json', {'currency': 'USD', 'new_commitment_cap': 0, 'reservations': [], 'settled_incremental_spend': 0})
            for folder in ['research', 'work', 'releases', 'reports']:
                (stage / folder).mkdir(exist_ok=True)
            (stage / 'operations/actions.jsonl').write_text('')
            receipt = {'operation': 'local_project_bootstrap', 'campaign_id': cid,
                       'website': website, 'at': now, 'network_actions': 0,
                       'workers_started': 0, 'jobs_created': 0, 'live_changes': 0,
                       'scope': 'Local files only; live and scheduled authority ungranted.'}
            write_json(stage / 'operations/bootstrap-receipt.json', receipt)
            (stage / 'mission.md').write_text(
                '# Campaign mission\n\nWebsite: ' + website + '\n\n'
                'Objective: discover the real business and grow qualified demand through useful SEO/AEO assets. '
                'Read AGENTS.md and the current owner grant. Until activation, research and local drafts only. '
                'Infer the site brief from evidence; record unknowns.\n\n'
                'Current runner: none. Jobs: none. Business baseline: unmeasured. '
                'Initial proposed window: 90 days from owner activation. Do not invent that activation.\n')
            # A second initializer cannot replace a populated directory. No existing
            # project is merged or reset; reuse above is read-only.
            if out.exists():
                raise ValueError('Destination appeared during initialization; reconcile it and rerun.')
            stage.rename(out)
            print(json.dumps({'status': 'created_local_project', 'campaign_id': cid,
                              'project': str(out), 'website': website,
                              'tasks': len(board['tasks']), 'roles': 13,
                              'runner': None, 'installed_jobs': 0}))
            return 0
        finally:
            if stage.exists():
                shutil.rmtree(stage)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('Bootstrap stopped: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
