import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'lighting_workflow.py'
INIT_PATH = ROOT / 'extension' / 'awful_studio' / '__init__.py'


def load_policy():
    spec = importlib.util.spec_from_file_location(
        'awful_lighting_workflow',
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load lighting workflow: {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LightingWorkflowContractTests(unittest.TestCase):
    def test_production_looks_route_to_existing_presets(self):
        policy = load_policy()
        self.assertEqual(policy.PRODUCTION_LOOKS, {
            'PRODUCT': 'COMMERCIAL_3LIGHT',
            'SOFT_BEAUTY': 'TOP_SOFT_PACKSHOT',
            'HARD_FLASH': 'DIRECT_FLASH',
            'EDGE': 'DUAL_STRIP_HERO',
            'ACCENT': 'DUAL_COLOR_STRIP',
            'GOBO': 'HARD_GOBO',
            'WINDOW': 'WINDOW_BALANCED',
            'GLASS': 'BACKLIT_GLASS',
        })

    def test_labels_cover_every_production_look(self):
        policy = load_policy()
        self.assertEqual(set(policy.PRODUCTION_LOOK_LABELS), set(policy.PRODUCTION_LOOKS))
        self.assertTrue(all(policy.PRODUCTION_LOOK_LABELS[key] for key in policy.PRODUCTION_LOOKS))

    def test_unknown_look_is_rejected(self):
        policy = load_policy()

        class FakeLegacy:
            def apply_lighting_preset(self, *args, **kwargs):
                raise AssertionError('must not call runtime for unknown look')

        with self.assertRaises(ValueError):
            policy.apply_look(FakeLegacy(), object(), 'DISCO_CHAOS')

    def test_operator_property_uses_runtime_annotation_assignment(self):
        source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertNotIn('look: legacy.EnumProperty', source)
        self.assertIn("AWFUL_OT_ApplyProductionLook.__annotations__['look']", source)
    def test_module_is_blender_independent_and_installed_before_registration(self):
        source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertNotIn('import bpy', source)
        self.assertNotIn('from bpy', source)
        init_source = INIT_PATH.read_text(encoding='utf-8')
        self.assertIn('lighting_workflow.install(legacy)', init_source)
        self.assertLess(
            init_source.index('lighting_workflow.install(legacy)'),
            init_source.index('CLASSES ='),
        )


if __name__ == '__main__':
    unittest.main()
