import ast
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[2]
LEGACY_PATH = REPO / 'extension' / 'awful_studio' / 'core' / 'legacy.py'


class LegacyAssetGateTests(unittest.TestCase):
    def test_hdri_loader_requires_valid_cache_provenance(self):
        tree = ast.parse(LEGACY_PATH.read_text(encoding='utf-8'))
        helper = next(
            (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'load_hdri_asset'),
            None,
        )
        self.assertIsNotNone(helper, 'legacy HDRI loading needs a provenance-aware helper')

        calls = [node for node in ast.walk(helper) if isinstance(node, ast.Call)]
        self.assertTrue(
            any(
                isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == 'asset_cache'
                and call.func.attr == 'read_valid'
                for call in calls
            ),
            'load_hdri_asset must validate the cache sidecar before decoding the file',
        )

    def test_environment_paths_do_not_bypass_hdri_cache_validation(self):
        source = LEGACY_PATH.read_text(encoding='utf-8')
        self.assertNotIn('env.image = load_image(hdri_asset_path(', source)
        self.assertGreaterEqual(source.count('env.image = load_hdri_asset('), 2)


if __name__ == '__main__':
    unittest.main()
