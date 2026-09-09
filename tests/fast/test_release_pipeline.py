import hashlib
import importlib.util
import json
import pathlib
import tempfile
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'release_pipeline.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'release-candidate.yml'


def load_tool():
    spec = importlib.util.spec_from_file_location('release_pipeline', TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleasePipelineTests(unittest.TestCase):
    def setUp(self):
        self.release = load_tool()

    def test_manifest_version_drives_package_name(self):
        manifest = tomllib.loads((ROOT / 'extension/awful_studio/blender_manifest.toml').read_text())
        self.assertEqual(self.release.package_name(manifest), 'awful_studio-0.0.16.zip')

    def test_candidate_metadata_hashes_exact_package(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            package = root / 'awful_studio-0.0.16.zip'
            package.write_bytes(b'exact-candidate')
            metadata = self.release.candidate_metadata(
                package=package,
                source_sha='abc123',
                manifest_version='0.0.16',
                runtime_evidence=[
                    {'status': 'passed', 'platform': 'linux-x64', 'blender_version': '5.2.1', 'package': package.name,
                     'sha256': hashlib.sha256(package.read_bytes()).hexdigest()},
                    {'status': 'passed', 'platform': 'windows-x64', 'blender_version': '5.2.1', 'package': package.name,
                     'sha256': hashlib.sha256(package.read_bytes()).hexdigest()},
                ],
                license_approved=False,
            )
            self.assertEqual(metadata['package']['sha256'], hashlib.sha256(package.read_bytes()).hexdigest())
            self.assertEqual(metadata['source_commit'], 'abc123')
            self.assertFalse(metadata['release_gate']['license_approved'])
            self.assertFalse(metadata['release_gate']['publishable'])

    def test_publish_gate_requires_two_platforms_same_exact_zip_and_license_approval(self):
        sha = 'f' * 64
        good = [
            {'status': 'passed', 'platform': 'linux-x64', 'blender_version': '5.2.1', 'package': 'awful_studio-0.0.16.zip', 'sha256': sha},
            {'status': 'passed', 'platform': 'windows-x64', 'blender_version': '5.2.1', 'package': 'awful_studio-0.0.16.zip', 'sha256': sha},
        ]
        gate = self.release.evaluate_publish_gate(good, expected_package='awful_studio-0.0.16.zip', expected_sha256=sha,
                                                  license_approved=True)
        self.assertTrue(gate['publishable'])

        mismatched = [dict(good[0]), dict(good[1], sha256='e' * 64)]
        self.assertFalse(self.release.evaluate_publish_gate(mismatched, expected_package='awful_studio-0.0.16.zip',
                                                            expected_sha256=sha, license_approved=True)['publishable'])
        self.assertFalse(self.release.evaluate_publish_gate(good[:1], expected_package='awful_studio-0.0.16.zip',
                                                            expected_sha256=sha, license_approved=True)['publishable'])
        self.assertFalse(self.release.evaluate_publish_gate(good, expected_package='awful_studio-0.0.16.zip',
                                                            expected_sha256=sha, license_approved=False)['publishable'])

    def test_repository_index_must_reference_exact_candidate_zip(self):
        index = {
            'data': [
                {'id': 'awful_studio', 'version': '0.0.16', 'archive_url': './awful_studio-0.0.16.zip',
                 'archive_hash': 'sha256:' + ('a' * 64)}
            ]
        }
        self.release.validate_repository_index(index, extension_id='awful_studio', version='0.0.16',
                                               package_name='awful_studio-0.0.16.zip')
        index['data'][0]['archive_url'] = './wrong.zip'
        with self.assertRaises(ValueError):
            self.release.validate_repository_index(index, extension_id='awful_studio', version='0.0.16',
                                                   package_name='awful_studio-0.0.16.zip')

    def test_write_metadata_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / 'release-metadata.json'
            payload = {'z': 1, 'a': {'b': 2}}
            self.release.write_json(path, payload)
            first = path.read_bytes()
            self.release.write_json(path, payload)
            self.assertEqual(first, path.read_bytes())
            self.assertEqual(json.loads(first), payload)

    def test_release_workflow_is_manual_and_does_not_deploy_pages(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('workflow_dispatch:', text)
        self.assertIn('license_approved:', text)
        self.assertNotIn('push:', text)
        self.assertNotIn('actions/deploy-pages', text)
        self.assertNotIn('pages: write', text)

    def test_release_workflow_consumes_same_candidate_in_both_runtime_jobs(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('name: candidate-zip', text)
        self.assertIn('needs: candidate', text)
        self.assertIn('runtime-${{ matrix.platform }}', text)
        self.assertIn('python tools/release_pipeline.py metadata', text)
        self.assertIn('python tools/release_pipeline.py repository', text)


if __name__ == '__main__':
    unittest.main()
