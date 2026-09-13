import hashlib
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'release_pipeline.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'release-candidate.yml'


def load_tool():
    spec = importlib.util.spec_from_file_location('release_pipeline_hardening', TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleasePipelineHardeningTests(unittest.TestCase):
    def setUp(self):
        self.release = load_tool()

    def test_publish_gate_rejects_duplicate_platform_evidence(self):
        sha = 'f' * 64
        evidence = [
            {
                'status': 'passed',
                'platform': 'linux-x64',
                'blender_version': '5.2.1',
                'package': 'awful_studio-0.0.16.zip',
                'sha256': sha,
            },
            {
                'status': 'passed',
                'platform': 'linux-x64',
                'blender_version': '5.2.1',
                'package': 'awful_studio-0.0.16.zip',
                'sha256': sha,
            },
            {
                'status': 'passed',
                'platform': 'windows-x64',
                'blender_version': '5.2.1',
                'package': 'awful_studio-0.0.16.zip',
                'sha256': sha,
            },
        ]
        gate = self.release.evaluate_publish_gate(
            evidence,
            expected_package='awful_studio-0.0.16.zip',
            expected_sha256=sha,
            license_approved=True,
        )
        self.assertFalse(gate['publishable'])
        self.assertTrue(any('duplicate runtime evidence' in reason for reason in gate['reasons']))

    def test_repository_index_hash_must_match_exact_candidate(self):
        digest = hashlib.sha256(b'exact-candidate').hexdigest()
        index = {
            'data': [
                {
                    'id': 'awful_studio',
                    'version': '0.0.16',
                    'archive_url': './awful_studio-0.0.16.zip',
                    'archive_hash': 'sha256:' + ('0' * 64),
                }
            ]
        }
        with self.assertRaises(ValueError):
            self.release.validate_repository_index(
                index,
                extension_id='awful_studio',
                version='0.0.16',
                package_name='awful_studio-0.0.16.zip',
                expected_sha256=digest,
            )

    def test_license_approval_is_restricted_to_repository_owner(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('github.actor == github.repository_owner', text)
        self.assertIn('license approval may only be asserted by the repository owner', text)


if __name__ == '__main__':
    unittest.main()
