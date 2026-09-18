import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'studio_diagnostics.py'


def load_policy():
    spec = importlib.util.spec_from_file_location('awful_studio_diagnostics_policy', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load diagnostics policy: {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StudioDiagnosticsContractTests(unittest.TestCase):
    def test_summary_counts_levels(self):
        policy = load_policy()
        items = (
            policy.Diagnostic('studio.ready', 'Studio', 'OK', 'Ready'),
            policy.Diagnostic('asset.optional', 'Assets', 'WARNING', 'Optional HDRI missing'),
            policy.Diagnostic('camera.missing', 'Camera', 'ERROR', 'Camera missing'),
        )
        self.assertEqual(
            policy.summarize(items),
            {'OK': 1, 'WARNING': 1, 'ERROR': 1},
        )

    def test_diagnostics_module_is_blender_independent(self):
        policy = load_policy()
        self.assertTrue(callable(policy.collect))
        source = MODULE_PATH.read_text(encoding='utf-8')
        self.assertNotIn('import bpy', source)
        self.assertNotIn('from bpy', source)

    def test_unknown_diagnostic_level_is_rejected(self):
        policy = load_policy()
        with self.assertRaises(ValueError):
            policy.make_diagnostic('x', 'Studio', 'MAYBE', 'Nope')

    def test_summary_rejects_unknown_item_level(self):
        policy = load_policy()
        bad = policy.Diagnostic('x', 'Studio', 'MAYBE', 'Nope')
        with self.assertRaises(ValueError):
            policy.summarize((bad,))


if __name__ == '__main__':
    unittest.main()
