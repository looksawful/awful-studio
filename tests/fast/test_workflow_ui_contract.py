import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'workflow_ui.py'
INIT_PATH = ROOT / 'extension' / 'awful_studio' / '__init__.py'


def load_policy():
    spec = importlib.util.spec_from_file_location('awful_workflow_ui_policy', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load workflow policy: {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkflowUIContractTests(unittest.TestCase):
    def test_workflow_module_is_scene_clean_and_declares_order(self):
        policy = load_policy()
        self.assertEqual(policy.PANEL_ORDER, (
            'STUDIO', 'PRODUCT', 'LIGHTING', 'CAMERA',
            'ENVIRONMENT', 'OUTPUT', 'DIAGNOSTICS',
        ))
        source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertNotIn('import bpy', source)
        self.assertNotIn('from bpy', source)

    def test_status_lines_are_task_oriented(self):
        policy = load_policy()
        lines = policy.status_lines({
            'built': True,
            'product': 'DEVICE_IPHONE_17',
            'lighting': 'COMMERCIAL_3LIGHT',
            'camera': 'STATIC',
            'environment': 'FISH_HOEK',
            'preview': 'FAST',
            'last_error': '',
        })
        self.assertGreaterEqual(len(lines), 3)
        self.assertEqual(lines[0], 'Studio: Ready')
        self.assertIn('Product: DEVICE_IPHONE_17', lines)
        self.assertIn('Lighting: COMMERCIAL_3LIGHT', lines)

    def test_workflow_installs_before_extension_class_registration(self):
        init_source = INIT_PATH.read_text(encoding='utf-8')
        self.assertIn('workflow_ui.install(legacy)', init_source)
        self.assertLess(
            init_source.index('workflow_ui.install(legacy)'),
            init_source.index('CLASSES ='),
        )


if __name__ == '__main__':
    unittest.main()
