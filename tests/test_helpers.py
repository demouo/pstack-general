from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RULE = 'Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.'


class DecisionLog(unittest.TestCase):
    def test_empty_log_initialized_and_existing_rows_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'decision log.tsv'
            log.touch()
            command = ['bash', str(ROOT / 'skills/show-me-your-work/scripts/log.sh'), str(log)]
            subprocess.run(command + ['start', 'first', 'reason', 'receipt', 'ok'], check=True)
            first = log.read_bytes()
            subprocess.run(command + ['fix', '=formula', 'tab\tline\nbreak', '@evidence', 'supersedes row 1'], check=True)
            self.assertTrue(log.read_bytes().startswith(first))
            rows = log.read_text().splitlines()
            self.assertEqual(rows[0], 'ts\tphase\tdecision\twhy\tevidence\tresult')
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[2].split('\t')[1:], ['fix', "'=formula", 'tab line break', "'@evidence", 'supersedes row 1'])


@unittest.skipUnless(shutil.which('node'), 'Node is required for the optional plan checker')
class PlanChecker(unittest.TestCase):
    def plan(self, model='inherit-parent'):
        intro = f'''# Export plan
Add JSON export with a visible result.
## How to read this
One box is one unit of work and names the evidence.
Check a box only when its evidence exists. Use `playbooks/autopilot-full.md`.
{RULE}
## Program checklist
### Arm the program
- [ ] Persist a run goal and read installed skills. Arm the hourly audit with a status message only for changes.
### Spawn owners
### PR mechanics
### Verdict and merge
### Boot recipe
## Add JSON export (PR1)
**Depends on.** None.
**Files.**
- [ ] Edit `export.py`.
**Build.**
- [ ] Implement JSON output.
**You see.**
- [ ] The output matches the requested rows.
**Verify, unit.** {RULE}
- [ ] Run `python -m unittest`.
**Verify, live.** {RULE} Ten lanes on `{model}` at the PR head.
'''
        lanes = '\n'.join(f'- [ ] Lane {i}. Export scenario {i}. Save `lane-{i}.png`. Pass when output is correct.' for i in range(1, 11))
        return intro + lanes + f'''
**Verify, perf.** {RULE}
- [ ] Metric. End-to-end export latency.
- [ ] Probe. Interleaved trunk and head runs.
- [ ] Baseline. Record trunk first.
- [ ] Rule. Head must stay within the budget.
**Review gate.** None. PR1 is not review-gated.
**Merge.**
- [ ] All evidence at the current head.
## Close the program
- [ ] Report receipts.
## Appendix A. Prototype evidence
The prototype exports the fixture.
'''

    def check(self, plan):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.md'
            path.write_text(plan)
            return subprocess.run(['node', str(ROOT / 'skills/poteto-mode/scripts/check-plan.mjs'), str(path)], capture_output=True, text=True)

    def test_inherited_and_configured_models_pass(self):
        for model in ('inherit-parent', 'team-review-model'):
            result = self.check(self.plan(model))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_unfilled_model_and_missing_lane_receipt_fail(self):
        for model in ('', '<model>'):
            result = self.check(self.plan(model))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('filled model', result.stderr)
        result = self.check(self.plan().replace('Save `lane-7.png`.', ''))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('lane 7 names no screenshot', result.stderr)
