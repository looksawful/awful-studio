import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'device_asset_loader.py'
PRODUCT_PATH = ROOT / 'extension' / 'awful_studio' / 'product_quality.py'
INIT_PATH = ROOT / 'extension' / 'awful_studio' / '__init__.py'

EXPECTED_KEYS = {
    'DEVICE_IPHONE_17',
    'DEVICE_IPAD_PRO_11',
    'DEVICE_IPAD_PRO_13',
    'DEVICE_MACBOOK_PRO_14',
}
EXPECTED_STAGES = {
    'DEVICE_IPHONE_17': 'LOW_DRAFT',
    'DEVICE_IPAD_PRO_11': 'LOW_DRAFT',
    'DEVICE_IPAD_PRO_13': 'LOW_DRAFT',
    'DEVICE_MACBOOK_PRO_14': 'RELEASE_CANDIDATE',
}
EXPECTED_VARIANTS = {
    'DEVICE_IPHONE_17': 'low_v30',
    'DEVICE_IPAD_PRO_11': 'low_v6',
    'DEVICE_IPAD_PRO_13': 'low_v6',
    'DEVICE_MACBOOK_PRO_14': 'low_v1_release',
}
EXPECTED_FILES = {
    'DEVICE_IPHONE_17': 'iphone_17_low_v30.blend',
    'DEVICE_IPAD_PRO_11': 'ipad_pro_11_m5_low_v6.blend',
    'DEVICE_IPAD_PRO_13': 'ipad_pro_13_m5_low_v6.blend',
    'DEVICE_MACBOOK_PRO_14': 'macbook_pro_14_m5_low_v1_release.blend',
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
            default_lod = item['default_lod']
            self.assertTrue(item['lods'][default_lod]['source_revision'])
            self.assertEqual(item['lods'][default_lod]['variant'], EXPECTED_VARIANTS[key])
            self.assertEqual(Path(item['lods'][default_lod]['blend_path']).name, EXPECTED_FILES[key])

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

    def test_all_devices_declare_replaceable_screen_contract(self):
        loader = load_module()
        for key in EXPECTED_KEYS:
            item = loader.device_asset_spec(key)
            self.assertEqual(item['screen_object'], 'SCREEN_CONTENT')
            self.assertEqual(item['screen_material'], 'MAT_SCREEN_CONTENT')

    def test_macbook_hinge_presets_match_asset_contract(self):
        loader = load_module()
        self.assertEqual(loader.hinge_preset_keys('DEVICE_MACBOOK_PRO_14'),
                         ('CLOSED', '30', '60', '90', '102'))
        expected = {'CLOSED': 0.0, '30': 30.0, '60': 60.0, '90': 90.0, '102': 102.0}
        for preset, angle in expected.items():
            self.assertEqual(loader.hinge_angle_degrees('DEVICE_MACBOOK_PRO_14', preset), angle)
        with self.assertRaises(ValueError):
            loader.hinge_preset_keys('DEVICE_IPHONE_17')

    def test_phone_tablet_orientation_presets_are_explicit(self):
        loader = load_module()
        expected = {
            'PORTRAIT': 0.0,
            'LANDSCAPE_LEFT': 90.0,
            'LANDSCAPE_RIGHT': -90.0,
            'PORTRAIT_INVERTED': 180.0,
        }
        for key in ('DEVICE_IPHONE_17', 'DEVICE_IPAD_PRO_11', 'DEVICE_IPAD_PRO_13'):
            self.assertEqual(loader.device_asset_spec(key)['orientation_axis'], 'Y')
            self.assertEqual(loader.orientation_preset_keys(key), tuple(expected))
            for preset, angle in expected.items():
                self.assertEqual(loader.orientation_angle_degrees(key, preset), angle)
        with self.assertRaises(ValueError):
            loader.orientation_preset_keys('DEVICE_MACBOOK_PRO_14')

    def test_screen_states_are_explicit_for_all_devices(self):
        loader = load_module()
        self.assertEqual(loader.screen_state_keys(), ('OFF', 'ON'))
        for key in EXPECTED_KEYS:
            spec = loader.device_asset_spec(key)
            self.assertEqual(spec['screen_states'], ('OFF', 'ON'))
            self.assertEqual(loader.screen_state_spec('OFF')['emission_strength'], 0.0)
            self.assertGreater(loader.screen_state_spec('ON')['emission_strength'], 0.0)

    def test_lod_contract_is_manifest_driven(self):
        loader = load_module()
        for key in EXPECTED_KEYS:
            item = loader.device_asset_spec(key)
            self.assertEqual(item['default_lod'], 'LOW')
            self.assertEqual(loader.lod_keys(key), ('LOW',))
            self.assertEqual(loader.device_asset_path(key),
                             loader.device_asset_path(key, 'LOW'))
            self.assertIn('LOW', item['lods'])
            self.assertTrue(item['lods']['LOW']['blend_path'])
            self.assertTrue(item['lods']['LOW']['source_revision'])
        with self.assertRaises(ValueError):
            loader.device_asset_path('DEVICE_IPHONE_17', 'HIGH')

    def test_lod_does_not_promote_asset_stage(self):
        loader = load_module()
        item = loader.device_asset_spec('DEVICE_IPHONE_17')
        self.assertEqual(item['default_lod'], 'LOW')
        self.assertEqual(item['stage'], 'LOW_DRAFT')

    def test_product_ui_registers_device_catalog(self):
        source = PRODUCT_PATH.read_text(encoding='utf-8')
        self.assertIn('device_asset_loader', source)
        self.assertIn('device_asset_loader.device_asset_keys()', source)
        self.assertIn('device_asset_loader.device_asset_spec(key)', source)
        self.assertIn("annotations['device_lod']", source)
        self.assertIn("annotations['device_orientation_preset']", source)
        self.assertIn("device_orientation_preset", source)
        init_source = INIT_PATH.read_text(encoding='utf-8')
        self.assertIn("awful.apply_device_orientation", init_source)


    def test_device_capabilities_are_explicit(self):
        loader = load_module()
        for key in ('DEVICE_IPHONE_17', 'DEVICE_IPAD_PRO_11', 'DEVICE_IPAD_PRO_13'):
            caps = loader.device_capabilities(key)
            self.assertTrue({'screen', 'orientation', 'lod'}.issubset(caps))
            self.assertNotIn('hinge', caps)
        mac_caps = loader.device_capabilities('DEVICE_MACBOOK_PRO_14')
        self.assertTrue({'screen', 'hinge', 'lod'}.issubset(mac_caps))
        self.assertNotIn('orientation', mac_caps)
    def test_product_ui_uses_device_capabilities(self):
        product_source = PRODUCT_PATH.read_text(encoding='utf-8')
        init_source = INIT_PATH.read_text(encoding='utf-8')
        self.assertIn('device_asset_loader.device_capabilities(selected)', product_source)
        self.assertIn("'orientation' in capabilities", product_source)
        self.assertIn("'hinge' in capabilities", product_source)
        self.assertNotIn("if selected == 'DEVICE_MACBOOK_PRO_14':", product_source)
        self.assertIn('device_asset_loader.device_capabilities(key)', init_source)
        self.assertNotIn("product_mockup == 'DEVICE_MACBOOK_PRO_14'", init_source)
class BinaryAssetAttributesTests(unittest.TestCase):
    def test_extension_binary_assets_are_never_text_normalized(self):
        attrs = (ROOT / '.gitattributes').read_text(encoding='utf-8')
        self.assertIn('extension/awful_studio/**/*.blend -text', attrs)
        for extension in ('png', 'jpg', 'jpeg'):
            self.assertIn(f'extension/awful_studio/assets/**/*.{extension} -text', attrs)


if __name__ == '__main__':
    unittest.main()
