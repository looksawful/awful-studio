import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AWFUL = ROOT / 'tools' / 'awful.py'
LOCK = ROOT / 'runtime' / 'blender.lock'


class AgentRuntimeEntrypointTests(unittest.TestCase):
    def run_awful(self, *args):
        return subprocess.run(
            [sys.executable, str(AWFUL), *args], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

    def test_status_is_pure_and_reports_pins(self):
        result = self.run_awful('status')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['extension_version'], '0.0.17')
        self.assertEqual(data['blender_target'], '5.2.1')
        self.assertEqual(data['blender_build_hash'], '9e2066aef7ef')
        self.assertFalse(data['render_tests_required'])
        self.assertIn('cloud-first', data['runtime_policy'])

    def test_doctor_is_pure_and_passes_repository_contract(self):
        result = self.run_awful('doctor')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'PASS')
        self.assertTrue(all(item['status'] == 'PASS' for item in data['checks']))

    def test_runtime_lock_matches_setup_tool_and_verified_archives(self):
        lock = json.loads(LOCK.read_text(encoding='utf-8'))
        setup = (ROOT / 'tools' / 'setup_blender.py').read_text(encoding='utf-8')
        self.assertEqual(lock['version'], '5.2.1')
        self.assertIn("VERSION = '5.2.1'", setup)
        self.assertEqual(
            lock['distributions']['windows-x64']['sha256'],
            '0e631dad7d0cad6d5d18abdd2e2550f6c0213215334eda00ddbd3d22b96ecb2c',
        )
        self.assertEqual(
            lock['distributions']['linux-x64']['sha256'],
            'a31f524fa99a527d3d52b7f5aaa68c34e1a19d5a1c9473f79c5cc610fd5b10e9',
        )

    def test_test_runtime_delegates_to_canonical_verifier_and_preserves_opt_in(self):
        source = AWFUL.read_text(encoding='utf-8')
        self.assertIn("'tools' / 'verify_extension.py'", source)
        self.assertIn("command.append('--allow-local-blender')", source)
        verifier = (ROOT / 'tools' / 'verify_extension.py').read_text(encoding='utf-8')
        self.assertIn('--allow-local-blender', verifier)
        self.assertIn("os.environ.get('CI', '')", verifier)


if __name__ == '__main__':
    unittest.main()
