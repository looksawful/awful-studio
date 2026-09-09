import importlib.util
import pathlib
import re
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'awful.py'
LOCK = ROOT / 'runtime' / 'blender.lock'
WORKFLOW = ROOT / '.github' / 'workflows' / 'extension-ci.yml'
VERIFY = ROOT / 'tools' / 'verify_extension.py'


class RuntimeCanonicalContract(unittest.TestCase):
    def load_tool(self):
        self.assertTrue(TOOL.is_file(), 'tools/awful.py must be the canonical runtime entrypoint')
        spec = importlib.util.spec_from_file_location('awful_runtime_tool', TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_runtime_lock_pins_exact_archive_checksum(self):
        awful = self.load_tool()
        runtime = awful.load_runtime_lock(ROOT)
        self.assertEqual(runtime['version'], '5.2.1')
        self.assertEqual(runtime['platform'], 'linux-x64')
        self.assertEqual(len(runtime['sha256']), 64)
        self.assertTrue(runtime['official_url'].endswith(runtime['archive']))
        self.assertNotIn('checksum_url', runtime)

    def test_bootstrap_uses_pinned_checksum_without_remote_checksum_lookup(self):
        self.load_tool()
        source = TOOL.read_text(encoding='utf-8')
        self.assertIn("runtime['sha256']", source)
        self.assertIn("runtime['official_url']", source)
        self.assertNotIn('checksum_url', source)
        self.assertNotIn('sha256_url', source)

    def test_bootstrap_failure_writes_evidence(self):
        awful = self.load_tool()
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / 'runtime').mkdir()
            (root / 'runtime' / 'blender.lock').write_text(
                'schema_version = "1.0"\n'
                'version = "5.2.1"\n'
                'series = "5.2"\n'
                'platform = "linux-x64"\n'
                'archive = "blender-5.2.1-linux-x64.tar.xz"\n'
                'sha256 = "' + ('0' * 64) + '"\n'
                'official_url = "https://127.0.0.1:1/blender.tar.xz"\n'
                'extracted_dir = "blender-5.2.1-linux-x64"\n'
                'executable = "blender"\n',
                encoding='utf-8',
            )
            with self.assertRaises(Exception):
                awful.bootstrap_blender(root)
            evidence = root / '.runtime' / 'bootstrap-failure.json'
            self.assertTrue(evidence.is_file())
            text = evidence.read_text(encoding='utf-8')
            self.assertIn('5.2.1', text)
            self.assertIn('failed', text)

    def test_blender_52_validate_uses_positional_source_path(self):
        source = VERIFY.read_text(encoding='utf-8')
        self.assertRegex(source, re.compile(r"'validate',\s*str\(source\)"))
        validate_call = source.split("'validate'", 1)[1].split('subprocess.run', 1)[0]
        self.assertNotIn("'--source-dir'", validate_call)

    def test_extension_ci_uses_only_canonical_runtime_entrypoint(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('python tools/awful.py bootstrap', workflow)
        self.assertIn('python tools/awful.py verify-extension', workflow)
        self.assertNotIn('tools/setup_blender.py', workflow)


if __name__ == '__main__':
    unittest.main()
