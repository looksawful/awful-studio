import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VERIFIER = ROOT / 'tools' / 'verify_extension.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'extension-ci.yml'


class ReleaseCandidateIdentityTests(unittest.TestCase):
    def test_verifier_can_validate_existing_exact_package_without_rebuilding(self):
        source = VERIFIER.read_text(encoding='utf-8')
        self.assertIn("'--package', type=Path", source)
        self.assertIn('package_override', source)
        self.assertIn("'validate', str(package)", source)

    def test_ci_builds_one_candidate_then_tests_that_same_artifact_on_both_os(self):
        source = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('candidate:', source)
        self.assertIn('name: extension-candidate', source)
        self.assertIn('actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093', source)
        self.assertIn('needs: [fast, candidate]', source)
        self.assertIn('--package dist/awful_studio-0.0.17.zip', source)
        self.assertNotIn('name: extension-${{ matrix.os }}', source)


if __name__ == '__main__':
    unittest.main()
