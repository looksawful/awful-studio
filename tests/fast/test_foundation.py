import ast
import hashlib
import pathlib
import unittest
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'


class FoundationTests(unittest.TestCase):
    def test_historical_baseline(self):
        source = ROOT / 'historical/0.0.15/awful_studio_v4_2_gpu_perf.py'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         '5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b')

    def test_manifest(self):
        data = tomllib.loads((EXT / 'blender_manifest.toml').read_text())
        self.assertEqual(data['version'], '0.0.17')
        self.assertEqual(data['blender_version_min'], '5.2.0')
        self.assertEqual(data['license'], ['SPDX:GPL-3.0-or-later'])

    def test_product_quality_version_boundary_is_consistent(self):
        init_source = (EXT / '__init__.py').read_text(encoding='utf-8')
        ownership_source = (EXT / 'ownership.py').read_text(encoding='utf-8')
        verifier_source = (ROOT / 'tools' / 'verify_extension.py').read_text(encoding='utf-8')
        workflow_source = (ROOT / '.github' / 'workflows' / 'extension-ci.yml').read_text(encoding='utf-8')
        self.assertIn('VERSION = (0, 0, 17)', init_source)
        self.assertIn("block[VERSION_KEY] = '0.0.17'", ownership_source)
        self.assertIn("awful_studio-0.0.17.zip", verifier_source)
        self.assertIn("awful_studio-0.0.17.zip", workflow_source)

    def test_no_eager_scene_registry(self):
        tree = ast.parse((EXT / 'core/legacy.py').read_text())
        registry = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'StudioRegistry')
        init = next(n for n in registry.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
        self.assertNotIn('bpy.context', ast.unparse(init))

    def test_first_build_can_clear_factory_scene_without_touching_user_edits(self):
        source = (EXT / '__init__.py').read_text(encoding='utf-8')
        self.assertIn('clear_factory_scene_objects(scene)', source)
        self.assertIn("{'Cube', 'Camera', 'Light'}", source)
        self.assertIn('not scene.awful_state.built', source)

    def test_build_never_fetches_assets(self):
        tree = ast.parse((EXT / 'core/legacy.py').read_text())
        build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build_studio')
        calls = [ast.unparse(n.func) for n in ast.walk(build) if isinstance(n, ast.Call)]
        self.assertNotIn('ensure_assets', calls)

    def test_all_python_parses(self):
        for file in EXT.rglob('*.py'):
            ast.parse(file.read_text(), filename=str(file))


if __name__ == '__main__':
    unittest.main()
