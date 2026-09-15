#!/usr/bin/env python3
"""Read-only worktree inventory. No network requests or inferred transcript paths."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def audit(repo, transcript_root=None):
    raw = git(repo, 'worktree', 'list', '--porcelain', '-z')
    if raw is None:
        raise ValueError('Not a Git repository')
    paths = [Path(field[9:]) for field in raw.split('\0') if field.startswith('worktree ')]
    base = git(repo, 'symbolic-ref', '--quiet', 'refs/remotes/origin/HEAD') or 'HEAD'
    rows = []
    for path in paths[1:]:
        dirty = git(path, 'status', '--porcelain')
        ancestor = git(repo, 'merge-base', '--is-ancestor', git(path, 'rev-parse', 'HEAD') or '', base)
        last = 'unknown'
        if transcript_root:
            matches = []
            for file in transcript_root.rglob('*'):
                if file.is_file():
                    try:
                        if str(path) in file.read_text(errors='replace'):
                            matches.append(file.stat().st_mtime)
                    except OSError:
                        continue
            if matches:
                last = datetime.fromtimestamp(max(matches), timezone.utc).isoformat()
        rows.append({'worktree': str(path), 'base': base, 'merged': ancestor is not None,
                     'dirty': dirty is None or bool(dirty), 'last_chat': last,
                     'bucket': 'hold-work' if dirty is None or dirty else 'review'})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', nargs='?', type=Path, default=Path.cwd())
    parser.add_argument('--transcripts', type=Path, help='Explicit workspace-scoped text export directory')
    args = parser.parse_args()
    if args.transcripts and not args.transcripts.is_dir():
        parser.error('--transcripts must be an existing workspace-scoped directory')
    try:
        rows = audit(args.repo, args.transcripts)
    except ValueError as error:
        parser.error(str(error))
    print('MERGED\tDIRTY\tLAST_CHAT\tBUCKET\tWORKTREE')
    for row in rows:
        print('\t'.join(str(row[key]) for key in ('merged', 'dirty', 'last_chat', 'bucket', 'worktree')))


if __name__ == '__main__':
    main()
