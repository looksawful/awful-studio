import pathlib
import re
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'


class Release017HygieneTests(unittest.TestCase):
    def test_release_facing_metadata_is_current_017(self):
        manifest = tomllib.loads((EXT / 'blender_manifest.toml').read_text(encoding='utf-8'))
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        state = (ROOT / 'STATE.md').read_text(encoding='utf-8')
        self.assertEqual(manifest['version'], '0.0.17')
        self.assertIn('Current target: **Alpha 0.0.17', readme)
        self.assertNotIn('0.0.16 is not public-release-ready', readme)
        self.assertIn('Current target: Alpha 0.0.17', state)
        self.assertNotIn('## Active release work', state)
        self.assertNotIn('#23:', state)

    def test_install_and_release_docs_exist_and_keep_manual_smoke_as_final_gate(self):
        install = ROOT / 'docs' / 'INSTALL_UPDATE.md'
        notes = ROOT / 'docs' / 'releases' / '0.0.17.md'
        self.assertTrue(install.is_file(), 'docs/INSTALL_UPDATE.md is required')
        self.assertTrue(notes.is_file(), 'docs/releases/0.0.17.md is required')
        install_text = install.read_text(encoding='utf-8')
        notes_text = notes.read_text(encoding='utf-8')
        self.assertIn('Install from Disk', install_text)
        self.assertIn('Extension Repository', install_text)
        self.assertIn('manual UI smoke', notes_text)
        self.assertIn('not tagged or published', notes_text)

    def test_release_tree_has_no_dev_junk_or_machine_specific_paths(self):
        forbidden_suffixes = {'.pyc', '.pyo', '.blend', '.blend1', '.exe', '.dll', '.zip'}
        for path in EXT.rglob('*'):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes, str(path.relative_to(ROOT)))

        patterns = (
            re.compile(r'[A-Za-z]:\\Users\\', re.IGNORECASE),
            re.compile(r'[A-Za-z]:\\Blender Foundation\\', re.IGNORECASE),
            re.compile(r'/home/[^/\s]+/'),
        )
        text_suffixes = {'.md', '.py', '.toml', '.yml', '.yaml', '.json', '.txt'}
        for path in ROOT.rglob('*'):
            if not path.is_file() or path.suffix.lower() not in text_suffixes:
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            for pattern in patterns:
                self.assertIsNone(pattern.search(text), f'machine-specific path in {path.relative_to(ROOT)}')


if __name__ == '__main__':
    unittest.main()
