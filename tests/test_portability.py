import importlib.util
import json
from pathlib import Path
import re
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
            self.assertTrue((target / '.pstack/skills/pstack-runtime/references/agents/comment-sicko.md').exists())

    def test_conflict_fails_before_any_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            installer.install(target)
            skill = target / '.pstack/skills/how/SKILL.md'
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
            (bundle / 'skills').symlink_to(target / 'outside')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                installer.install(target)


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
