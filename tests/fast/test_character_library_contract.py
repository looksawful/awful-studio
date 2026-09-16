import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'character_library.py'
CATALOG = ROOT / 'extension' / 'awful_studio' / 'character_assets' / 'catalog.json'

spec = importlib.util.spec_from_file_location('character_library', MODULE_PATH)
character_library = importlib.util.module_from_spec(spec)
spec.loader.exec_module(character_library)


class CharacterLibraryContractTests(unittest.TestCase):
    def test_catalog_has_expected_reviewed_sources(self):
        data = json.loads(CATALOG.read_text(encoding='utf-8-sig'))
        libraries = data['libraries']
        self.assertEqual(data['schema_version'], 1)
        for key in ('cmu_mocap', 'makehuman_core', 'makehuman_community_assets',
                    'quaternius_modular_men', 'quaternius_modular_women',
                    'quaternius_universal_characters', 'quaternius_fantasy_outfits',
                    'actorcore_free'):
            self.assertIn(key, libraries)
            self.assertTrue(libraries[key]['source_page'].startswith('https://'))
        self.assertEqual(libraries['makehuman_core']['license'], 'CC0-1.0')
        self.assertEqual(libraries['quaternius_modular_men']['license'], 'CC0-1.0')
        self.assertNotEqual(libraries['actorcore_free']['license'], 'CC0-1.0')
        self.assertTrue(libraries['actorcore_free']['requires_account'])

    def test_catalog_separates_library_formats_from_direct_import_formats(self):
        libraries = character_library.libraries()
        for record in libraries.values():
            self.assertIn('import_formats', record)
            self.assertTrue(set(record['import_formats']).issubset(set(record['formats'])))
        self.assertEqual(libraries['cmu_mocap']['import_formats'], [])
        self.assertEqual(libraries['makehuman_community_assets']['import_formats'], [])
        self.assertEqual(libraries['actorcore_free']['import_formats'], ['fbx', 'bvh'])

    def test_discovery_is_offline_and_non_mutating(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            before = set(root.rglob('*'))
            status = character_library.discover(root)
            self.assertTrue(status)
            self.assertFalse(any(item['present'] for item in status.values()))
            self.assertEqual(before, set(root.rglob('*')))

    def test_import_candidates_are_scoped_by_declared_formats(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            library = character_library.library_root(root, 'quaternius_modular_women')
            library.mkdir(parents=True)
            (library / 'woman.glb').write_bytes(b'glTF')
            (library / 'woman.fbx').write_bytes(b'fbx')
            (library / 'notes.txt').write_text('not importable', encoding='utf-8')
            candidates = character_library.import_candidates(root, 'quaternius_modular_women')
            self.assertEqual([p.name for p in candidates], ['woman.fbx'])

    def test_non_blender_library_files_are_not_direct_import_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            cmu = character_library.library_root(root, 'cmu_mocap')
            cmu.mkdir(parents=True)
            (cmu / 'walk.asf').write_text('skeleton', encoding='utf-8')
            (cmu / 'walk.amc').write_text('motion', encoding='utf-8')
            makehuman = character_library.library_root(root, 'makehuman_community_assets')
            makehuman.mkdir(parents=True)
            (makehuman / 'coat.mhclo').write_text('clothing', encoding='utf-8')
            self.assertEqual(character_library.import_candidates(root, 'cmu_mocap'), [])
            self.assertEqual(character_library.import_candidates(root, 'makehuman_community_assets'), [])

    def test_import_plan_matches_blender_52_boundaries(self):
        self.assertEqual(character_library.import_plan('character.fbx')['operator'], 'wm.fbx_import')
        self.assertEqual(character_library.import_plan('character.obj')['operator'], 'wm.obj_import')
        self.assertEqual(character_library.import_plan('character.gltf')['operator'], 'import_scene.gltf')
        self.assertEqual(character_library.import_plan('motion.bvh')['operator'], 'import_anim.bvh')
        self.assertEqual(character_library.import_plan('library.blend')['strategy'], 'blend-library')
        self.assertEqual(character_library.import_plan('character.mhx2')['strategy'], 'external-addon')
        with self.assertRaises(ValueError):
            character_library.import_plan('motion.amc')

    def test_import_candidates_reject_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            library = character_library.library_root(root, 'actorcore_free')
            library.mkdir(parents=True)
            direct = library / 'actor.fbx'
            direct.write_bytes(b'fbx')
            outside = root / 'outside.fbx'
            outside.write_bytes(b'outside')
            link = library / 'escape.fbx'
            try:
                link.symlink_to(outside)
            except OSError:
                self.skipTest('symlink creation unavailable on this platform')
            candidates = character_library.import_candidates(root, 'actorcore_free')
            self.assertEqual([p.name for p in candidates], ['actor.fbx'])

    def test_repository_does_not_vendor_character_binaries(self):
        forbidden = {'.blend', '.fbx', '.bvh', '.amc', '.asf', '.mhclo', '.obj', '.glb', '.gltf'}
        asset_dir = ROOT / 'extension' / 'awful_studio' / 'character_assets'
        bundled = [p for p in asset_dir.rglob('*') if p.is_file() and p.suffix.lower() in forbidden]
        self.assertEqual(bundled, [])


if __name__ == '__main__':
    unittest.main()
