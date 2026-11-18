#!/usr/bin/env python3
"""Check portable structures and bootstrap behavior; no external services."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    checks = []
    for path in ROOT.rglob('*.json'):
        json.loads(path.read_text())
    checks.append('All bundled JSON parses.')
    roles = json.loads((ROOT / 'config/roles.json').read_text())['roles']
    ids = {r['id'] for r in roles}
    assert len(ids) == len(roles) == 13
    for role in roles:
        assert (ROOT / role['prompt_path']).is_file(), role['id']
    checks.append('13 distinct roles resolve to individual prompts.')
    board = json.loads((ROOT / 'templates/board.json').read_text())
    tasks = {t['id']: t for t in board['tasks']}
    assert len(tasks) == len(board['tasks'])
    epics = {e['id'] for e in board['epics']}
    seen, active = set(), set()

    def visit(tid):
        assert tid in tasks, 'Missing task ' + tid
        assert tid not in active, 'Dependency cycle ' + tid
        if tid in seen:
            return
        active.add(tid)
        task = tasks[tid]
        assert task['owner_role'] in ids and task['epic'] in epics
        assert task['acceptance'] and task['outputs']
        assert len(task['depends_on']) == len(set(task['depends_on']))
        for dep in task['depends_on']:
            visit(dep)
        active.remove(tid)
        seen.add(tid)

    for tid in tasks:
        visit(tid)
    checks.append(f'{len(tasks)} tasks have valid owners, epics, checks and acyclic dependencies.')
    grant = json.loads((ROOT / 'config/authority.example.json').read_text())
    assert grant['status'] == 'ungranted'
    assert all(not allowed for key, allowed in grant['operations'].items()
               if key not in ('public_research', 'local_project_and_drafts'))
    cfg = json.loads((ROOT / 'config/campaign.example.json').read_text())
    assert cfg['runtime']['runner'] is None and not cfg['runtime']['scheduler_verified']
    assert cfg['limits']['campaign_incremental_spend'] == 0
    checks.append('Default grant, budget and runtime do not imply live execution.')
    schedules = json.loads((ROOT / 'templates/schedules.json').read_text())
    assert len(schedules['jobs']) == 1 and not schedules['jobs'][0]['enabled']
    checks.append('One desired dispatcher is disabled and has no native job ID.')
    with tempfile.TemporaryDirectory(prefix='seo-kit-check-') as tmp:
        dest = Path(tmp) / 'campaign'
        cmd = [sys.executable, str(ROOT / 'scripts/bootstrap.py'), '--website',
               'https://Example.com/', '--out', str(dest)]
        first = subprocess.run(cmd, capture_output=True, text=True)
        assert first.returncode == 0, first.stderr
        assert json.loads(first.stdout)['website'] == 'https://example.com'
        state = json.loads((dest / 'checkpoint.json').read_text())
        assert state['runner'] is None and not state['pending_actions']
        generated = json.loads((dest / 'board.json').read_text())
        assert sum(t['status'] == 'DONE' for t in generated['tasks']) == 1
        assert (dest / 'registry/roles.json').is_file()
        assert (dest / 'reference/RESEARCH-PLAYBOOK.txt').is_file()
        assert not json.loads((dest / 'registry/jobs.json').read_text())['jobs']
        checks.append('Website-only bootstrap produces portable project, truthful state and no active jobs.')
        state['cycle'] = 7
        (dest / 'checkpoint.json').write_text(json.dumps(state))
        (dest / 'work/owner-note.txt').write_text('Preserve this work.')

        def snapshot():
            return {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in dest.rglob('*') if p.is_file()}

        before = snapshot()
        again = subprocess.run(cmd, capture_output=True, text=True)
        assert again.returncode == 0 and json.loads(again.stdout)['status'] == 'reused_without_changes'
        assert snapshot() == before
        other = cmd.copy()
        other[other.index('https://Example.com/')] = 'https://another.example'
        rejected = subprocess.run(other, capture_output=True, text=True)
        assert rejected.returncode == 2 and snapshot() == before
        checks.append('Rerun preserves every project byte; another website is rejected without mutation.')
        for bad in ['https://user:password@example.com', 'https://example.com/?key=private', 'ftp://example.com', 'https://example.com:wrong']:
            bad_cmd = [sys.executable, str(ROOT / 'scripts/bootstrap.py'), '--website', bad, '--out', str(Path(tmp) / 'bad')]
            result = subprocess.run(bad_cmd, capture_output=True, text=True)
            assert result.returncode == 2 and not (Path(tmp) / 'bad').exists()
        checks.append('Credential-bearing, query-bearing and malformed input rejected before project creation.')
    required = ['START-HERE.txt', 'LAUNCH-PROMPT.txt', 'AGENTS.md', 'TOOLS-AND-PROJECT.md',
                'CAMPAIGN-PLAYBOOK.md', 'RUNTIME.md', 'ACCEPTANCE.md',
                'reference/CURRENT-NOTES.md', 'reference/RESEARCH-PLAYBOOK.txt',
                'reference/TACTICAL-SOURCE-MAP.txt', 'adapters/HERMES.md', 'adapters/GROK-BOT.md']
    assert all((ROOT / name).is_file() for name in required)
    checks.append('All required standalone instructions, adapters and research references exist.')
    return {'status': 'passed', 'checks': checks, 'not_tested': [
        'No live website, project SaaS, account grant or SEO/AEO outcome tested.',
        'No Hermes/Grok Bot deployment, worker, schedule, runtime lock, cost cap or cancellation drill executed.',
        'Runtime and campaign scenarios are specified/reviewed contracts, not empirical host verification.'
    ]}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
