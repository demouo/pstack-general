#!/usr/bin/env python3
"""Install a self-contained pstack bundle without overwriting local changes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1]
BEGIN = '<!-- pstack:begin -->'
END = '<!-- pstack:end -->'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def install(target, entrypoint=None, dry_run=False):
    target = target.resolve()
    bundle = target / '.pstack'
    if bundle.is_symlink():
        raise ValueError('Refusing a symlinked .pstack directory')
    manifest = bundle / 'install-manifest.json'
    if manifest.is_symlink():
        raise ValueError('Refusing a symlinked install manifest')
    old = json.loads(manifest.read_text()) if manifest.exists() else {}
    if not isinstance(old, dict):
        raise ValueError('Install manifest must be an object')
    files = {}
    for folder in ('skills', 'automations'):
        for src in (SOURCE / folder).rglob('*'):
            if src.is_file() and not any(x in src.parts for x in ('node_modules', '__pycache__')):
                files[str(src.relative_to(SOURCE))] = src.read_bytes()
    for name in ('LICENSE', 'UPSTREAM.md'):
        files[name] = (SOURCE / name).read_bytes()
    conflicts = []
    for name in set(files) | set(old):
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('skills', 'automations', 'LICENSE', 'UPSTREAM.md'):
            raise ValueError(f'Invalid manifest path: {name}')
        dest = bundle / rel
        if any(p.is_symlink() for p in (dest, *dest.parents) if p != target.parent):
            raise ValueError(f'Refusing symlink destination: {dest}')
        if dest.exists():
            if not dest.is_file():
                conflicts.append(name)
                continue
            current = dest.read_bytes()
            if current != files.get(name) and digest(current) != old.get(name):
                conflicts.append(name)
    entry = None
    content = None
    if entrypoint:
        rel = Path(entrypoint)
        if rel.is_absolute() or len(rel.parts) != 1:
            raise ValueError('--entrypoint must be a filename in the target project')
        entry = target / rel
        if entry.is_symlink():
            raise ValueError('Refusing a symlinked entrypoint')
        existing = entry.read_text() if entry.exists() else ''
        block = f'''{BEGIN}
## pstack

For pstack workflows, read `.pstack/skills/pstack-runtime/SKILL.md` first.
Read `.pstack/skills/<skill-name>/SKILL.md` directly when requested by name.
Use `.pstack/skills/poteto-mode/SKILL.md` when the user requests the full pstack style.
Benny setup starts at `.pstack/automations/benny/FOR_AGENTS.md`.
Follow host instructions and user authorization. Missing tools use the runtime's fallbacks.
{END}'''
        if BEGIN in existing or END in existing:
            if existing.count(BEGIN) != 1 or existing.count(END) != 1 or existing.index(BEGIN) > existing.index(END):
                raise ValueError('Malformed pstack entrypoint markers')
            start, stop = existing.index(BEGIN), existing.index(END) + len(END)
            content = existing[:start] + block + existing[stop:]
        else:
            content = existing + ('\n\n' if existing else '') + block + '\n'
    if conflicts:
        raise ValueError('Local edits conflict; inspect and merge before retrying: ' + ', '.join(sorted(conflicts)))
    if dry_run:
        return f'Would install {len(files)} files into {bundle}'
    for name, data in files.items():
        dest = bundle / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        shutil.copymode(SOURCE / name, dest)
    for name in set(old) - set(files):
        (bundle / name).unlink(missing_ok=True)
    manifest.write_text(json.dumps({n: digest(d) for n, d in files.items()}, indent=2) + '\n')
    if entry:
        entry.write_text(content)
    return f'Installed {len(files)} files into {bundle}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='Destination project')
    parser.add_argument('--entrypoint', help='Host instruction filename, e.g. AGENTS.md, CLAUDE.md or GEMINI.md')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        print(install(args.target, args.entrypoint, args.dry_run))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
