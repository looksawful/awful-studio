import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    import device_delivery_contract as contract
except ImportError:
    contract = None

MANIFEST = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json'
LOADER = ROOT / 'extension/awful_studio/device_asset_loader.py'


def load_loader():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', LOADER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceDeliveryContractTests(unittest.TestCase):
    def test_v30_manifest_is_current_and_self_verifying(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v30 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        self.assertEqual(manifest['asset_id'], 'iphone_17')
        self.assertEqual(manifest['version'], 'v30')
        self.assertEqual(manifest['stage'], 'LOW_DRAFT')
        self.assertEqual(manifest['delivery_profile']['simplification'], 'none')
        self.assertEqual(contract.verify_manifest(ROOT, manifest), [])
        self.assertEqual(set(manifest['screen_states']), {'screen_off', 'screen_on'})
        self.assertEqual(manifest['screen_states']['screen_off']['emission_strength'], 0.0)
        self.assertGreater(manifest['screen_states']['screen_on']['emission_strength'], 0.0)
        self.assertEqual(manifest['screen_glow']['anchor'], 'SCREEN_GLOW_ANCHOR')

    def test_v30_provenance_text_files_are_pinned_to_lf(self):
        paths = [
            'assets/device_mockups/iphone_17/generate_low_v30.py',
            'assets/device_mockups/iphone_17/evidence/low_v30_validation.json',
            'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json',
        ]
        for relative in paths:
            result = subprocess.check_output(
                ['git', 'check-attr', 'eol', '--', relative],
                cwd=ROOT, text=True,
            ).strip()
            self.assertTrue(result.endswith(': eol: lf'), result)

    def test_v30_tracked_delivery_text_is_lf_only(self):
        paths = [
            ROOT / 'assets/device_mockups/iphone_17/generate_low_v30.py',
            ROOT / 'assets/device_mockups/iphone_17/export_runtime_v30.py',
            ROOT / 'assets/device_mockups/iphone_17/evidence/low_v30_validation.json',
            ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json',
            ROOT / 'tools/build_iphone17_v30.py',
        ]
        for path in paths:
            self.assertNotIn(b'\r\n', path.read_bytes(), str(path))

    def test_plugin_loader_matches_delivery_revision_and_stage(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v30 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        loader = load_loader()
        item = loader.device_asset_spec('DEVICE_IPHONE_17')
        lod = item['lods'][item['default_lod']]
        self.assertEqual(item['stage'], manifest['stage'])
        self.assertEqual(lod['variant'], 'low_v30')
        self.assertEqual(lod['source_revision'], manifest['source_revision'])
        self.assertEqual(Path(lod['blend_path']).name, 'iphone_17_low_v30.blend')

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
