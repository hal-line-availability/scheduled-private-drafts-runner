"""Execute the workflow's result recorder without credentials or network."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


class PrivateResultTests(unittest.TestCase):
    def test_damaged_failure_record_does_not_suppress_result(self):
        workflow = yaml.safe_load((Path(__file__).resolve().parents[1] /
                                   '.github/workflows/daily-drafts.yml').read_text())
        step = next(s for s in workflow['jobs']['prepare']['steps']
                    if s.get('name') == 'Record private result')
        code = step['run'].split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON', 1)[0]
        for failure in ('{"reason":', '[]', 'null'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'generator/outputs').mkdir(parents=True)
                (root / 'generator/outputs/source-not-ready.json').write_text(failure)
                env = dict(os.environ, GENERATION_OUTCOME='failure', RUN_MODE='prepare',
                           DRAFT_NOT_BEFORE='', DRAFT_TRIGGER_EVENT='workflow_dispatch',
                           DRAFT_AT_TARGET='false', DRAFT_RUN_ID='fixture-run')
                result = subprocess.run([sys.executable, '-c', code], cwd=root,
                                        env=env, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                saved = json.loads((root / 'generator/outputs/last-run.json').read_text())
                self.assertEqual(saved['status'], 'needs_attention')
                self.assertEqual(saved['reason_code'], 'failure_record_unreadable')
                self.assertFalse(saved['customer_sent'])

    def test_invalid_manual_targets_still_persist_failure(self):
        workflow = yaml.safe_load((Path(__file__).resolve().parents[1] /
                                   '.github/workflows/daily-drafts.yml').read_text())
        step = next(s for s in workflow['jobs']['prepare']['steps']
                    if s.get('name') == 'Record private result')
        code = step['run'].split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON', 1)[0]
        for target in ('not-a-date', '2026-11-08T17:30:00',
                       '9999-12-31T23:59:59+09:00'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'generator').mkdir()
                env = dict(os.environ, GENERATION_OUTCOME='failure', RUN_MODE='prepare',
                           DRAFT_NOT_BEFORE=target, DRAFT_TRIGGER_EVENT='workflow_dispatch',
                           DRAFT_AT_TARGET='false', DRAFT_RUN_ID='fixture-run')
                result = subprocess.run([sys.executable, '-c', code], cwd=root,
                                        env=env, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                saved = json.loads((root / 'generator/outputs/last-run.json').read_text())
                self.assertEqual(saved['status'], 'needs_attention')
                self.assertEqual(saved['reason_code'], 'invalid_manual_target')
                self.assertFalse(saved['customer_sent'])
                self.assertNotIn('save_deadline', saved)


if __name__ == '__main__':
    unittest.main()
