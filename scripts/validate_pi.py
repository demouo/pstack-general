#!/usr/bin/env python3
"""Run real pi sessions against isolated pstack fixtures. Uses the configured model."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pstack_install', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

CASES = {
    'how': 'Read .pstack/skills/how/SKILL.md and use that workflow to explain how checkout.py computes the total. Cite source lines. Do not edit files.',
    'interrogate': 'Use the interrogate skill to review checkout.py against its documented contract. Return the review verdict with evidence. Do not modify code.',
    'tdd': 'Read .pstack/skills/tdd/SKILL.md and follow it to fix checkout.py so shipping follows the documented contract. Add focused regression tests and verify the fix. Limit edits to checkout.py and test_checkout.py.',
    'recall': 'Read .pstack/skills/recall/SKILL.md. Recall the decision I made last week about this checkout module and its rationale. I have not supplied an earlier conversation or history export.',
    'scheduler': 'Read .pstack/skills/poteto-mode/playbooks/autonomous-run.md and the pstack runtime contract. I need you to check whether approval.txt contains APPROVED every ten minutes and continue after this session ends until it does. Do not change approval.txt. Save enough state to resume this task.',
}


def summarize(path):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    calls = [e for e in events if e.get('type') == 'tool_execution_start']
    messages = [e['message'] for e in events if e.get('type') == 'message_end' and e.get('message', {}).get('role') == 'assistant']
    finals = [''.join(part.get('text', '') for part in m.get('content', []) if part.get('type') == 'text') for m in messages]
    return {
        'model': next((m.get('model') for m in messages if m.get('model')), None),
        'provider': next((m.get('provider') for m in messages if m.get('provider')), None),
        'tools': [{'name': e['toolName'], 'args': e.get('args', {})} for e in calls],
        'errors': [m.get('errorMessage') for m in messages if m.get('stopReason') in ('error', 'aborted')],
        'final': '\n\n'.join(text for text in finals if text),
        'completed': any(e.get('type') == 'agent_end' for e in events),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory for isolated projects and session evidence')
    parser.add_argument('--node', help='Explicit Node binary when pi needs a newer Node than the shell default')
    parser.add_argument('--pi', default=shutil.which('pi'), help='pi executable or JavaScript entrypoint')
    parser.add_argument('--case', choices=list(CASES), action='append', dest='cases')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.pi:
        parser.error('pi is not installed')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    executable = [str(Path(args.pi).resolve())]
    if args.node:
        executable.insert(0, args.node)
    results = {}
    for name in args.cases or CASES:
        project = output / name
        if project.exists():
            parser.error(f'Refusing to reuse an existing case directory: {project}')
        project.mkdir()
        installer.install(project, 'AGENTS.md')
        for fixture in (ROOT / 'tests/fixtures/pi').glob('*.py'):
            shutil.copy2(fixture, project / fixture.name)
        command = executable + ['--offline', '--no-extensions', '--no-skills', '--no-prompt-templates', '--no-themes', '--approve', '--session-dir', str(project / 'sessions'), '--mode', 'json', '--print']
        if name == 'interrogate':
            command += ['--skill', str(project / '.pstack/skills')]
        if name in ('recall', 'scheduler'):
            command += ['--tools', 'read,write,grep,find,ls']
        command += [CASES[name]]
        (project / 'invocation.json').write_text(json.dumps({'cwd': str(project), 'command': command}, indent=2) + '\n')
        print(f'Running {name} in {project}', flush=True)
        with (project / 'events.jsonl').open('w') as stdout, (project / 'stderr.txt').open('w') as stderr:
            try:
                result = subprocess.run(command, cwd=project, stdout=stdout, stderr=stderr, timeout=args.timeout)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = 124
        summary = summarize(project / 'events.jsonl')
        summary['exit_code'] = code
        summary['case'] = name
        (project / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
        results[name] = {'exit_code': code, 'completed': summary['completed'], 'errors': summary['errors']}
        print(json.dumps(results[name]), flush=True)
        if code != 0 or summary['errors']:
            break
    (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(r['exit_code'] or r['errors'] or not r['completed'] for r in results.values()))


if __name__ == '__main__':
    sys.exit(main())
