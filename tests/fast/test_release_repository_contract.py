import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VERIFY_REPO = ROOT / 'tools' / 'verify_repository.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'extension-ci.yml'


class ReleaseRepositoryContractTests(unittest.TestCase):
    def test_static_repository_uses_official_blender_cli(self):
        source = VERIFY_REPO.read_text(encoding='utf-8')
        self.assertIn("'server-generate'", source)
        self.assertIn("'repo-add'", source)
        self.assertIn("'sync'", source)
        self.assertIn("'install'", source)
        self.assertIn("'awful_studio'", source)
        self.assertIn('.as_uri()', source)

    def test_repository_sync_explicitly_enables_blender_online_access(self):
        source = VERIFY_REPO.read_text(encoding='utf-8')
        self.assertIn(
            "blender, '--background', '--online-mode', '--command', 'extension', 'sync'",
            source,
        )
        self.assertIn(
            "blender, '--background', '--online-mode', '--command', 'extension',",
            source,
        )
        self.assertIn("'install', '-s', '-e', 'awful_studio'", source)

    def test_repository_verification_is_profile_isolated_and_render_free(self):
        source = VERIFY_REPO.read_text(encoding='utf-8')
        self.assertIn('BLENDER_USER_RESOURCES', source)
        self.assertIn("'render_tests': False", source)
        self.assertNotIn('bpy.ops.render.', source)

    def test_ci_runs_repository_gate_after_exact_zip_verifier(self):
        source = WORKFLOW.read_text(encoding='utf-8')
        package = 'dist/awful_studio-0.0.17.zip'
        self.assertIn('python tools/verify_extension.py --blender "$BLENDER"', source)
        self.assertIn('python tools/verify_repository.py --blender "$BLENDER"', source)
        self.assertIn(package, source)
        self.assertLess(source.index('python tools/verify_extension.py'),
                        source.index('python tools/verify_repository.py'))


if __name__ == '__main__':
    unittest.main()
