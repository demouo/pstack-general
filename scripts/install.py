#!/usr/bin/env python3
"""Install pstack in .agents/skills and preserve project configuration."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1]
BEGIN = '<!-- pstack:begin -->'
END = '<!-- pstack:end -->'
SKILLS = Path('.agents/skills')
SUPPORT = Path('.pstack')


def check_path(target, relative):
    """Reject redirected destinations and blocked parents before any writes."""
    current = target
    for i, part in enumerate(relative.parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Refusing symlink destination: {current}')
        if i < len(relative.parts) - 1 and current.exists() and not current.is_dir():
            raise ValueError(f'Destination parent is not a directory: {current}')
    return current


def managed_path(name, legacy=False):
    if not isinstance(name, str):
        raise ValueError(f'Invalid manifest path: {name}')
    if legacy:
        # v1 used str(Path), so Windows inventories used backslashes.
        name = name.replace('\\', '/')
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != name:
        raise ValueError(f'Invalid manifest path: {name}')
    if legacy:
        valid = (
            (len(rel.parts) >= 3 and rel.parts[0] == 'skills')
            or (len(rel.parts) >= 2 and rel.parts[0] == 'automations')
            or name in ('LICENSE', 'UPSTREAM.md')
        )
        if valid:
            return SUPPORT / rel
    else:
        if (
            (len(rel.parts) >= 4 and rel.parts[:2] == SKILLS.parts)
            or (len(rel.parts) >= 3 and rel.parts[:2] == ('.pstack', 'automations'))
            or name in ('.pstack/LICENSE', '.pstack/UPSTREAM.md')
        ):
            return rel
    raise ValueError(f'Invalid manifest path: {name}')


def read_manifest(manifest):
    data = json.loads(manifest.read_text()) if manifest.exists() else {}
    if not isinstance(data, dict):
        raise ValueError('Install manifest must be an object')
    legacy = 'version' not in data
    if not legacy:
        if data.get('version') != 2 or set(data) != {'version', 'files'} or not isinstance(data['files'], dict):
            raise ValueError('Unsupported install manifest format')
        data = data['files']
    old = {}
    for name, hash_value in data.items():
        rel = managed_path(name, legacy)
        if not isinstance(hash_value, str) or not re.fullmatch(r'[a-f0-9]{64}', hash_value):
            raise ValueError(f'Invalid manifest hash: {name}')
        old[rel.as_posix()] = hash_value
    return old


def prepare_entrypoints(target, entrypoint):
    if entrypoint:
        rel = Path(entrypoint)
        if rel.is_absolute() or len(rel.parts) != 1 or rel.name in ('.', '..'):
            raise ValueError('--entrypoint must be a filename in the target project')
    block = f'''{BEGIN}
## pstack

For pstack workflows, read `.agents/skills/pstack-runtime/SKILL.md` first.
Read `.agents/skills/<skill-name>/SKILL.md` directly when requested by name.
Use `.agents/skills/poteto-mode/SKILL.md` when the user requests the full pstack style.
Benny setup starts at `.pstack/automations/benny/FOR_AGENTS.md`.
Follow host instructions and user authorization. Missing tools use the runtime's fallbacks.
{END}'''
    entries = {}
    for name in sorted(set(('AGENTS.md', 'CLAUDE.md', 'GEMINI.md')) | ({entrypoint} if entrypoint else set())):
        entry = target / name
        if name != entrypoint and (entry.is_symlink() or not entry.is_file()):
            continue
        check_path(target, Path(name))
        existing = entry.read_text() if entry.exists() else ''
        if BEGIN in existing or END in existing:
            if existing.count(BEGIN) != 1 or existing.count(END) != 1 or existing.index(BEGIN) > existing.index(END):
                raise ValueError(f'Malformed pstack entrypoint markers: {name}')
            start, stop = existing.index(BEGIN), existing.index(END) + len(END)
            entries[entry] = existing[:start] + block + existing[stop:]
        elif name == entrypoint:
            entries[entry] = existing + ('\n\n' if existing else '') + block + '\n'
    return entries


def digest(data):
    return hashlib.sha256(data).hexdigest()


def install(target, entrypoint=None, dry_run=False):
    target = target.resolve()
    manifest = check_path(target, SUPPORT / 'install-manifest.json')
    old = read_manifest(manifest)
    files = {}
    sources = {}
    for folder in ('skills', 'automations'):
        for src in (SOURCE / folder).rglob('*'):
            if src.is_file() and not any(x in src.parts for x in ('node_modules', '__pycache__')):
                rel = src.relative_to(SOURCE / folder)
                dest = (SKILLS / rel) if folder == 'skills' else (SUPPORT / folder / rel)
                files[dest.as_posix()] = src.read_bytes()
                sources[dest.as_posix()] = src
    for name in ('LICENSE', 'UPSTREAM.md'):
        dest = (SUPPORT / name).as_posix()
        files[dest] = (SOURCE / name).read_bytes()
        sources[dest] = SOURCE / name
    conflicts = []
    for name in set(files) | set(old):
        dest = check_path(target, Path(name))
        if dest.exists():
            if not dest.is_file():
                conflicts.append(name)
                continue
            current = dest.read_bytes()
            if current != files.get(name) and digest(current) != old.get(name):
                conflicts.append(name)
    entries = prepare_entrypoints(target, entrypoint)
    if conflicts:
        raise ValueError('Local edits conflict; inspect and merge before retrying: ' + ', '.join(sorted(conflicts)))
    if dry_run:
        return f'Would install skills into {target / SKILLS} and support files into {target / SUPPORT}'
    for name, data in files.items():
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        shutil.copymode(sources[name], dest)
    for name in set(old) - set(files):
        dest = target / name
        dest.unlink(missing_ok=True)
        # Remove only empty retired directories; leave all unmanaged files.
        parent = dest.parent
        while parent not in (target, target / SUPPORT, target / '.agents', target / SKILLS):
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    inventory = {'version': 2, 'files': {n: digest(d) for n, d in files.items()}}
    manifest.write_text(json.dumps(inventory, indent=2) + '\n')
    for entry, content in entries.items():
        entry.write_text(content)
    return f'Installed {len(files)} files: skills in {target / SKILLS}; support in {target / SUPPORT}'


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
