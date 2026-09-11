import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'product_quality.py'
PLACEMENT_PATH = ROOT / 'extension' / 'awful_studio' / 'product_placement.py'
INIT_PATH = ROOT / 'extension' / 'awful_studio' / '__init__.py'
EXPECTED_MOCKUPS = {'BOTTLE', 'JAR', 'BOX', 'CAN', 'PHONE', 'TABLET'}
EXPECTED_MATERIALS = {
    'PLASTIC_MATTE', 'PLASTIC_GLOSSY', 'METAL_ANODIZED',
    'GLASS_CLEAR', 'GLASS_DARK', 'CERAMIC', 'CARDBOARD',
    'PAPER_LABEL', 'SCREEN',
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load policy module: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_policy():
    return load_module('awful_product_quality_policy', MODULE_PATH)


def load_placement_policy():
    return load_module('awful_product_placement_policy', PLACEMENT_PATH)


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
            self.assertEqual(set(spec['material_slots']), set(spec['slot_materials']))
            self.assertTrue(set(spec['slot_materials'].values()).issubset(EXPECTED_MATERIALS))

    def test_notion_material_starters_are_bounded_and_offline(self):
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

        self.assertGreater(policy.material_spec('GLASS_CLEAR')['transmission'], 0.8)
        self.assertGreater(policy.material_spec('GLASS_DARK')['transmission'], 0.8)
        self.assertGreater(policy.material_spec('SCREEN')['emission_strength'], 0.0)
        self.assertEqual(policy.material_spec('METAL_ANODIZED')['metallic'], 1.0)

    def test_support_surface_offset_places_bottom_exactly_on_support(self):
        policy = load_placement_policy()
        self.assertAlmostEqual(policy.support_surface_offset(0.125, 0.500), 0.375)
        self.assertAlmostEqual(policy.support_surface_offset(0.500, 0.500), 0.0)
        self.assertAlmostEqual(policy.support_surface_offset(0.750, 0.500), -0.250)

    def test_mount_delta_centers_xy_and_places_bottom_on_support(self):
        policy = load_placement_policy()
        self.assertEqual(
            policy.mount_delta(
                center_x=2.0,
                center_y=-3.0,
                bottom_z=1.09,
                target_x=0.0,
                target_y=0.0,
                support_z=0.50,
            ),
            (-2.0, 3.0, -0.59),
        )

    def test_policy_modules_remain_blender_independent(self):
        for path in (MODULE_PATH, PLACEMENT_PATH):
            source = path.read_text(encoding='utf-8')
            self.assertNotIn('import bpy', source)
            self.assertNotIn('from bpy', source)

    def test_unknown_catalog_keys_are_rejected(self):
        policy = load_policy()
        with self.assertRaises(ValueError):
            policy.mockup_spec('VAGUE_HUMAN_OBJECT')
        with self.assertRaises(ValueError):
            policy.material_spec('MAGIC')

    def test_product_quality_installs_before_registration_and_exposes_one_action(self):
        init_source = INIT_PATH.read_text(encoding='utf-8')
        policy_source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertIn('product_quality.install(legacy)', init_source)
        self.assertLess(init_source.index('product_quality.install(legacy)'),
                        init_source.index('CLASSES ='))
        self.assertIn("bl_idname = 'awful.generate_mockup'", init_source)
        self.assertIn("annotations['product_mockup']", policy_source)
        self.assertIn("row.operator('awful.generate_mockup'", policy_source)
        self.assertIn('create_diagnostic_or_selected_mockup', policy_source)


if __name__ == '__main__':
    unittest.main()
