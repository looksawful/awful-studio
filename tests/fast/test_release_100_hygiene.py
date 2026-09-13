import pathlib
import re
import subprocess
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
THIS_FILE = pathlib.Path(__file__).resolve()


def tracked_files():
    result = subprocess.run(
        ['git', 'ls-files', '-z'], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return [ROOT / item.decode('utf-8') for item in result.stdout.split(b'\0') if item]


class Release100HygieneTests(unittest.TestCase):
    def test_release_facing_metadata_is_stable_100(self):
        manifest = tomllib.loads((EXT / 'blender_manifest.toml').read_text(encoding='utf-8'))
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        state = (ROOT / 'STATE.md').read_text(encoding='utf-8')
        self.assertEqual(manifest['version'], '1.0.0')
        self.assertIn('Current release: **1.0.0**', readme)
        self.assertIn('Current release: 1.0.0', state)
        self.assertNotIn('Current target: **Alpha 0.0.17', readme)
        self.assertNotIn('Current target: Alpha 0.0.17', state)

    def test_install_and_release_docs_exist(self):
        install = ROOT / 'docs' / 'INSTALL_UPDATE.md'
        notes = ROOT / 'docs' / 'releases' / '1.0.0.md'
        self.assertTrue(install.is_file(), 'docs/INSTALL_UPDATE.md is required')
        self.assertTrue(notes.is_file(), 'docs/releases/1.0.0.md is required')
        install_text = install.read_text(encoding='utf-8')
        notes_text = notes.read_text(encoding='utf-8')
        self.assertIn('Install from Disk', install_text)
        self.assertIn('AWFUL STUDIO 1.0.0', notes_text)
        self.assertIn('Known limitations', notes_text)

    def test_release_tree_has_no_dev_junk_or_machine_specific_paths(self):
        forbidden_suffixes = {'.pyc', '.pyo', '.blend', '.blend1', '.exe', '.dll', '.zip'}
        tracked = tracked_files()
        violations = []

        for path in tracked:
            try:
                relative = path.relative_to(ROOT)
            except ValueError:
                continue
            if relative.parts[:2] == ('extension', 'awful_studio') and path.suffix.lower() in forbidden_suffixes:
                violations.append(f'dev junk in Extension package: {relative}')

        patterns = (
            ('user-home', re.compile(r'[A-Za-z]:\\Users\\', re.IGNORECASE)),
            ('blender-install', re.compile(r'[A-Za-z]:\\Blender Foundation\\', re.IGNORECASE)),
            ('posix-home', re.compile(r'/home/[^/\s]+/')),
        )
        text_suffixes = {'.md', '.py', '.toml', '.yml', '.yaml', '.json', '.txt'}
        for path in tracked:
            if path.resolve() == THIS_FILE:
                continue
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            for label, pattern in patterns:
                if pattern.search(text):
                    violations.append(f'{label} machine-specific path in {path.relative_to(ROOT)}')

        self.assertEqual(violations, [], '\n' + '\n'.join(violations))


if __name__ == '__main__':
    unittest.main()
