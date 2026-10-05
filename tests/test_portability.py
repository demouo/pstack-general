import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


installer = module('installer', ROOT / 'scripts/install.py')
audit = module('audit', ROOT / 'skills/poteto-mode/scripts/worktree-audit.py')


class Installation(unittest.TestCase):
    def test_idempotent_preserves_user_files_and_instruction_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'project with spaces'
            target.mkdir()
            entry = target / 'CLAUDE.md'
            entry.write_text('My project rules\n')
            installer.install(target, 'CLAUDE.md')
            first = entry.read_bytes()
            custom = target / '.pstack/models.md'
            custom.write_text('user model choices')
            installer.install(target, 'CLAUDE.md')
            self.assertEqual(entry.read_bytes(), first)
            self.assertTrue(first.startswith(b'My project rules\n'))
            self.assertEqual(custom.read_text(), 'user model choices')
            self.assertTrue((target / '.agents/skills/pstack-runtime/references/agents/comment-sicko.md').exists())

    def test_conflict_fails_before_any_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            installer.install(target)
            skill = target / '.agents/skills/how/SKILL.md'
            skill.write_text('local edits')
            manifest = target / '.pstack/install-manifest.json'
            before = manifest.read_bytes()
            with self.assertRaisesRegex(ValueError, 'Local edits conflict'):
                installer.install(target, 'AGENTS.md')
            self.assertEqual(skill.read_text(), 'local edits')
            self.assertEqual(manifest.read_bytes(), before)
            self.assertFalse((target / 'AGENTS.md').exists())

    def test_dry_run_does_not_create_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'absent'
            installer.install(target, 'GEMINI.md', True)
            self.assertFalse(target.exists())

    def test_rejects_symlink_and_manifest_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            bundle = target / '.pstack'
            bundle.mkdir()
            (bundle / 'install-manifest.json').write_text(json.dumps({'../outside': 'hash'}))
            with self.assertRaisesRegex(ValueError, 'Invalid manifest path'):
                installer.install(target)
            (bundle / 'install-manifest.json').unlink()
            (target / '.agents').symlink_to(target / 'outside')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                installer.install(target)

    def legacy_install(self, target):
        """Recreate v1's on-disk layout and manifest without its old installer."""
        installer.install(target)
        manifest = target / '.pstack/install-manifest.json'
        files = json.loads(manifest.read_text())['files']
        legacy = {}
        for name, hash_value in files.items():
            if name.startswith('.agents/skills/'):
                old_name = name.replace('.agents/skills/', 'skills/', 1)
                dest = target / '.pstack' / old_name
                dest.parent.mkdir(parents=True, exist_ok=True)
                (target / name).rename(dest)
            else:
                old_name = name.removeprefix('.pstack/')
            legacy[old_name] = hash_value
        manifest.write_text(json.dumps(legacy))
        # Empty directories would hide whether a failed migration created files.
        shutil.rmtree(target / '.agents')
        (target / 'AGENTS.md').write_text('User rules\n<!-- pstack:begin -->\nRead `.pstack/skills/how/SKILL.md`.\n<!-- pstack:end -->\nUser footer\n')

    def test_native_layout_preserves_other_skills_without_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            custom = target / '.agents/skills/my-skill/SKILL.md'
            custom.parent.mkdir(parents=True)
            custom.write_text('My independent skill')
            installer.install(target)
            self.assertEqual(custom.read_text(), 'My independent skill')
            self.assertFalse((target / 'AGENTS.md').exists())
            self.assertFalse((target / '.pstack/skills').exists())
            self.assertTrue((target / '.pstack/automations/benny/FOR_AGENTS.md').exists())
            self.assertEqual(len(list((target / '.agents/skills').glob('*/SKILL.md'))), 54)
            self.assertTrue((target / '.agents/skills/how/references/explorer-prompt.md').exists())

    def test_legacy_migration_refreshes_entrypoint_and_preserves_user_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.legacy_install(target)
            custom = target / '.pstack/skills/how/user-notes.md'
            custom.write_text('Keep my notes')
            models = target / '.pstack/models.md'
            models.write_text('My model choices')
            installer.install(target)
            self.assertTrue((target / '.agents/skills/how/SKILL.md').exists())
            self.assertFalse((target / '.pstack/skills/how/SKILL.md').exists())
            self.assertEqual(custom.read_text(), 'Keep my notes')
            self.assertEqual(models.read_text(), 'My model choices')
            entry = (target / 'AGENTS.md').read_text()
            self.assertTrue(entry.startswith('User rules\n'))
            self.assertTrue(entry.endswith('User footer\n'))
            self.assertIn('.agents/skills/how', entry.replace('<skill-name>', 'how'))
            self.assertNotIn('.pstack/skills', entry)
            self.assertEqual(json.loads((target / '.pstack/install-manifest.json').read_text())['version'], 2)
            installer.install(target)
            self.assertEqual((target / 'AGENTS.md').read_text(), entry)

    def test_legacy_edits_or_destination_collision_block_before_writes(self):
        for changed_legacy in (True, False):
            with self.subTest(changed_legacy=changed_legacy), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                self.legacy_install(target)
                if changed_legacy:
                    changed = target / '.pstack/skills/how/SKILL.md'
                else:
                    changed = target / '.agents/skills/how/SKILL.md'
                    changed.parent.mkdir(parents=True)
                changed.write_text('Keep local changes')
                before = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError, 'Local edits conflict'):
                    installer.install(target)
                after = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
                self.assertEqual(before, after)

    def test_v2_manifest_cannot_own_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / '.pstack').mkdir()
            (target / '.pstack/install-manifest.json').write_text(json.dumps({'version': 2, 'files': {'README.md': '0' * 64}}))
            with self.assertRaisesRegex(ValueError, 'Invalid manifest path'):
                installer.install(target)
            self.assertFalse((target / '.agents').exists())

    def test_legacy_dry_run_preserves_layout_and_instruction_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.legacy_install(target)
            before = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
            installer.install(target, dry_run=True)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()})
            self.assertFalse((target / '.agents').exists())

    def test_legacy_windows_manifest_separators_migrate(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.legacy_install(target)
            manifest = target / '.pstack/install-manifest.json'
            data = json.loads(manifest.read_text())
            manifest.write_text(json.dumps({name.replace('/', '\\'): value for name, value in data.items()}))
            installer.install(target)
            self.assertTrue((target / '.agents/skills/how/SKILL.md').exists())
            self.assertFalse((target / '.pstack/skills').exists())

    def test_blocked_parent_or_malformed_entrypoint_prevents_partial_install(self):
        for obstacle in ('parent', 'entrypoint'):
            with self.subTest(obstacle=obstacle), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                if obstacle == 'parent':
                    (target / '.agents').write_text('Keep this file')
                else:
                    (target / 'AGENTS.md').write_text('Rules\n<!-- pstack:begin -->')
                before = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
                with self.assertRaises(ValueError):
                    installer.install(target)
                self.assertFalse((target / '.pstack').exists())
                self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()})

    def test_retired_managed_skill_keeps_unmanaged_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            installer.install(target)
            retired = target / '.agents/skills/retired/SKILL.md'
            retired.parent.mkdir()
            retired.write_text('Old managed skill')
            notes = retired.parent / 'notes.txt'
            notes.write_text('User notes')
            manifest = target / '.pstack/install-manifest.json'
            data = json.loads(manifest.read_text())
            data['files'][retired.relative_to(target).as_posix()] = installer.digest(retired.read_bytes())
            manifest.write_text(json.dumps(data))
            installer.install(target)
            self.assertFalse(retired.exists())
            self.assertEqual(notes.read_text(), 'User notes')


class WorktreeAudit(unittest.TestCase):
    def test_space_paths_untracked_work_and_unknown_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / 'repo space'
            repo.mkdir()
            def git(*args):
                subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
            git('init')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-m', 'initial')
            work = Path(tmp) / 'worker space'
            git('worktree', 'add', '-b', 'worker', str(work.resolve()))
            row = audit.audit(repo)[0]
            self.assertEqual(row['worktree'], str(work.resolve()))
            self.assertEqual(row['last_chat'], 'unknown')
            self.assertEqual(row['bucket'], 'review')
            (work / 'untracked.txt').write_text('valuable work')
            self.assertEqual(audit.audit(repo)[0]['bucket'], 'hold-work')
            self.assertEqual((work / 'untracked.txt').read_text(), 'valuable work')


class Bundle(unittest.TestCase):
    def test_skill_identity_runtime_and_relative_links(self):
        skills = list((ROOT / 'skills').glob('*/SKILL.md'))
        self.assertGreater(len(skills), 40)
        for path in skills:
            text = path.read_text()
            self.assertTrue(text.startswith('---\n'), path)
            self.assertIn(f'name: {path.parent.name}\n', text)
            self.assertIn('\ndescription:', text)
            self.assertIn('pstack-runtime', text)
        for path in list((ROOT / 'skills').rglob('*.md')) + list((ROOT / 'automations').rglob('*.md')):
            if 'node_modules' in path.parts:
                continue
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if re.match(r'https?://|#', link) or '<' in link or link == 'url':
                    continue
                destination = link.split('#')[0]
                self.assertTrue((path.parent / destination).exists(), f'{path}: {link}')


if __name__ == '__main__':
    unittest.main()
