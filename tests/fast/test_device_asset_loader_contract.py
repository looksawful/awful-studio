import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'device_asset_loader.py'
PRODUCT_PATH = ROOT / 'extension' / 'awful_studio' / 'product_quality.py'

EXPECTED_KEYS = {
    'DEVICE_IPHONE_17',
    'DEVICE_IPAD_PRO_11',
    'DEVICE_IPAD_PRO_13',
    'DEVICE_MACBOOK_PRO_14',
}
EXPECTED_STAGES = {
    'DEVICE_IPHONE_17': 'LOW_DRAFT',
    'DEVICE_IPAD_PRO_11': 'RELEASE_CANDIDATE',
    'DEVICE_IPAD_PRO_13': 'RELEASE_CANDIDATE',
    'DEVICE_MACBOOK_PRO_14': 'RELEASE_CANDIDATE',
}


def load_module():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceAssetLoaderContractTests(unittest.TestCase):
    def test_catalog_exposes_four_bundled_device_assets(self):
        loader = load_module()
        self.assertEqual(set(loader.device_asset_keys()), EXPECTED_KEYS)
        for key in EXPECTED_KEYS:
            item = loader.device_asset_spec(key)
            self.assertEqual(item['stage'], EXPECTED_STAGES[key])
            self.assertTrue(item['asset_id'])
            self.assertTrue(item['label'])
            self.assertEqual(len(tuple(item['dimensions_m'])), 3)
            self.assertGreater(min(item['dimensions_m']), 0.0)
            self.assertTrue(item['source_revision'])

    def test_catalog_is_offline_and_bundled(self):
        loader = load_module()
        for key in EXPECTED_KEYS:
            item = loader.device_asset_spec(key)
            path = loader.device_asset_path(key)
            self.assertTrue(path.is_file(), f'{key} missing bundled .blend: {path}')
            self.assertEqual(path.suffix.lower(), '.blend')
            self.assertTrue(str(path).startswith(str(MODULE_PATH.parent)))
            self.assertNotIn('http', repr(item).lower())

    def test_unknown_asset_key_is_rejected(self):
        loader = load_module()
        with self.assertRaises(ValueError):
            loader.device_asset_spec('DEVICE_IMAGINARY')

    def test_product_ui_registers_device_catalog(self):
        source = PRODUCT_PATH.read_text(encoding='utf-8')
        self.assertIn('device_asset_loader', source)
        self.assertIn('device_asset_loader.device_asset_keys()', source)
        self.assertIn('device_asset_loader.device_asset_spec(key)', source)


class BinaryAssetAttributesTests(unittest.TestCase):
    def test_extension_binary_assets_are_never_text_normalized(self):
        attrs = (ROOT / '.gitattributes').read_text(encoding='utf-8')
        self.assertIn('extension/awful_studio/**/*.blend -text', attrs)
        for extension in ('png', 'jpg', 'jpeg'):
            self.assertIn(f'extension/awful_studio/assets/**/*.{extension} -text', attrs)


if __name__ == '__main__':
    unittest.main()
