import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'product_quality.py'
EXPECTED_MOCKUPS = {'BOTTLE', 'JAR', 'BOX', 'CAN', 'PHONE', 'TABLET'}
EXPECTED_MATERIALS = {'COATED', 'GLASS', 'METAL', 'PAPER', 'SCREEN'}


def load_policy():
    spec = importlib.util.spec_from_file_location('awful_product_quality_policy', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError('Unable to load product-quality policy module')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductQualityContractTests(unittest.TestCase):
    def test_catalog_has_six_real_world_mockups(self):
        policy = load_policy()
        self.assertEqual(set(policy.mockup_keys()), EXPECTED_MOCKUPS)
        for key in EXPECTED_MOCKUPS:
            spec = policy.mockup_spec(key)
            dimensions = tuple(spec['dimensions_m'])
            self.assertEqual(len(dimensions), 3)
            self.assertGreaterEqual(min(dimensions), 0.004)
            self.assertLessEqual(max(dimensions), 0.40)
            self.assertGreaterEqual(spec['max_mesh_parts'], 1)
            self.assertLessEqual(spec['max_mesh_parts'], 8)
            self.assertGreaterEqual(spec['bevel_segments'], 3)
            self.assertLessEqual(spec['bevel_segments'], 6)
            self.assertTrue(spec['material_slots'])
            self.assertEqual(len(spec['material_slots']), len(set(spec['material_slots'])))

    def test_material_starters_are_bounded_and_offline(self):
        policy = load_policy()
        self.assertEqual(set(policy.MATERIAL_STARTERS), EXPECTED_MATERIALS)
        for key in EXPECTED_MATERIALS:
            spec = policy.material_spec(key)
            self.assertGreaterEqual(spec['roughness'], 0.0)
            self.assertLessEqual(spec['roughness'], 1.0)
            self.assertGreaterEqual(spec['metallic'], 0.0)
            self.assertLessEqual(spec['metallic'], 1.0)
            self.assertNotIn('url', repr(spec).lower())
            self.assertNotIn('path', repr(spec).lower())

    def test_policy_module_remains_blender_independent(self):
        source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertNotIn('import bpy', source)
        self.assertNotIn('from bpy', source)

    def test_unknown_catalog_keys_are_rejected(self):
        policy = load_policy()
        with self.assertRaises(ValueError):
            policy.mockup_spec('VAGUE_HUMAN_OBJECT')
        with self.assertRaises(ValueError):
            policy.material_spec('MAGIC')


if __name__ == '__main__':
    unittest.main()
