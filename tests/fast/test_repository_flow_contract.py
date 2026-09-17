import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / '.github' / 'workflows' / 'extension-ci.yml'
RELEASE = ROOT / '.github' / 'workflows' / 'release.yml'
VERIFY = ROOT / 'tools' / 'verify_extension.py'
MANIFEST = ROOT / 'extension' / 'awful_studio' / 'blender_manifest.toml'


class RepositoryFlowContractTests(unittest.TestCase):
    def test_extension_ci_exposes_stable_merge_gate(self):
        text = CI.read_text(encoding='utf-8')
        self.assertIn('  merge-gate:', text)
        merge_gate = text.split('  merge-gate:', 1)[1]
        self.assertIn('needs: [fast, candidate, runtime-windows]', merge_gate)
        self.assertIn('if: always()', text)

    def test_release_is_tag_driven(self):
        text = RELEASE.read_text(encoding='utf-8')
        self.assertIn("tags: ['v*']", text)
        self.assertNotIn('branches: [main]', text)
        self.assertNotIn('Publish GitHub Release v1.0.0', text)
        self.assertNotIn('gh release view v1.0.0', text)

    def test_package_identity_comes_from_manifest(self):
        manifest = MANIFEST.read_text(encoding='utf-8')
        version = re.search(r'^version = "([^"]+)"$', manifest, re.MULTILINE).group(1)
        verify = VERIFY.read_text(encoding='utf-8')
        self.assertNotIn("EXPECTED_PACKAGE = 'awful_studio-1.0.0.zip'", verify)
        self.assertIn('blender_manifest.toml', verify)
        self.assertEqual(version, '1.0.0')


if __name__ == '__main__':
    unittest.main()
