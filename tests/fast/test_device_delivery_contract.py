import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    import device_delivery_contract as contract
except ImportError:
    contract = None

MANIFEST = ROOT / 'assets/device_mockups/iphone_17/runtime/v29/iphone_17_v29.asset.json'
LOADER = ROOT / 'extension/awful_studio/device_asset_loader.py'


def load_loader():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', LOADER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceDeliveryContractTests(unittest.TestCase):
    def test_v29_manifest_is_current_and_self_verifying(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v29 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        self.assertEqual(manifest['asset_id'], 'iphone_17')
        self.assertEqual(manifest['version'], 'v29')
        self.assertEqual(manifest['stage'], 'LOW_DRAFT')
        self.assertEqual(manifest['delivery_profile']['simplification'], 'none')
        self.assertEqual(contract.verify_manifest(ROOT, manifest), [])

    def test_plugin_loader_matches_delivery_revision_and_stage(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v29 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        loader = load_loader()
        item = loader.device_asset_spec('DEVICE_IPHONE_17')
        lod = item['lods'][item['default_lod']]
        self.assertEqual(item['stage'], manifest['stage'])
        self.assertEqual(lod['variant'], 'low_v29')
        self.assertEqual(lod['source_revision'], manifest['source_revision'])
        self.assertEqual(Path(lod['blend_path']).name, 'iphone_17_low_v29.blend')

    def test_wrong_stage_or_revision_is_rejected(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = {
            'asset_id': 'iphone_17',
            'stage': 'LOW_DRAFT',
            'source_revision': 'abc',
        }
        self.assertFalse(contract.delivery_matches(manifest, 'iphone_17', 'DELIVERY', 'abc'))
        self.assertFalse(contract.delivery_matches(manifest, 'iphone_17', 'LOW_DRAFT', 'def'))
        self.assertTrue(contract.delivery_matches(manifest, 'iphone_17', 'LOW_DRAFT', 'abc'))


if __name__ == '__main__':
    unittest.main()
