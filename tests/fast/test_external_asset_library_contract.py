import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
CATALOG = EXT / 'assets' / 'external_libraries.json'

spec = importlib.util.spec_from_file_location('external_asset_library', EXT / 'external_asset_library.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExternalAssetLibraryTests(unittest.TestCase):
    def test_catalog_is_local_only_and_pack_license_reviewed(self):
        data = json.loads(CATALOG.read_text(encoding='utf-8-sig'))
        self.assertEqual(data['schema_version'], 1)
        self.assertEqual(data['license_reviewed_at'], '2026-09-16')
        self.assertGreaterEqual(len(data['libraries']), 5)
        for record in data['libraries'].values():
            self.assertEqual(record['distribution'], 'user-acquired-local')
            self.assertEqual(record['license'], 'CC0-1.0')
            self.assertEqual(record['license_url'], 'https://creativecommons.org/publicdomain/zero/1.0/')
            self.assertNotIn('download_url', record)
            self.assertTrue(record['source_page'].startswith('https://quaternius.com/packs/'))

    def test_discover_returns_supported_exchange_formats_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for name in ('a.obj', 'b.FBX', 'c.gltf', 'd.glb', 'ignore.zip', 'readme.txt'):
                (root / name).write_bytes(b'x')
            self.assertEqual([p.suffix.lower() for p in module.discover(root)], ['.obj', '.fbx', '.gltf', '.glb'])

    def test_extension_exposes_explicit_registration_only(self):
        source = (EXT / '__init__.py').read_text(encoding='utf-8-sig')
        self.assertIn("bl_idname = 'awful.register_external_asset_library'", source)
        self.assertIn('external_asset_library_path', source)
        self.assertNotIn('external_asset_library.register_asset_browser_root(bpy,', source.split('def register():', 1)[1])

    def test_import_helper_uses_current_blender_52_fbx_operator(self):
        source = (EXT / 'external_asset_library.py').read_text(encoding='utf-8-sig')
        self.assertIn('bpy.ops.wm.fbx_import', source)
        self.assertNotIn('bpy.ops.import_scene.fbx', source)


if __name__ == '__main__':
    unittest.main()
