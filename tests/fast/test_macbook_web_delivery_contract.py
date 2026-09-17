import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import device_delivery_contract as contract

LOADER_PATH = ROOT / 'extension/awful_studio/device_asset_loader.py'
RUNTIME = ROOT / 'assets/device_mockups/macbook_pro_14/runtime/v1'
MANIFEST = RUNTIME / 'macbook_pro_14_m5_v1.asset.json'


def load_loader():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', LOADER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def glb_doc(path: Path) -> dict:
    raw = path.read_bytes()
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        raise AssertionError(f'invalid GLB JSON chunk: {path}')
    return json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\0'))


def glb_node_names(path: Path) -> set[str]:
    doc = glb_doc(path)
    return {node.get('name') for node in doc.get('nodes', []) if node.get('name')}


class MacBookWebDeliveryContractTests(unittest.TestCase):
    def test_v1_runtime_manifest_is_current_and_matches_plugin_source(self):
        self.assertTrue(MANIFEST.is_file(), 'missing MacBook v1 runtime manifest')
        manifest = contract.load_manifest(MANIFEST)
        self.assertEqual(manifest['asset_id'], 'macbook_pro_14_m5')
        self.assertEqual(manifest['version'], 'v1')
        self.assertEqual(manifest['stage'], 'RELEASE_CANDIDATE')
        self.assertEqual(contract.verify_manifest(ROOT, manifest), [])
        loader = load_loader()
        lod = loader.device_asset_spec('DEVICE_MACBOOK_PRO_14')['lods']['LOW']
        self.assertEqual(manifest['plugin_source_revision'], lod['source_revision'])
        self.assertEqual(manifest['root'], 'CTRL_MACBOOK_PRO_14')
        self.assertEqual(manifest['hinge_control'], 'CTRL_HINGE')
        source_paths = set(manifest['source_files'])
        self.assertIn('assets/device_mockups/macbook_pro_14/reference/macos26_official_screen.png', source_paths)
        self.assertEqual(set(manifest['screen_states']), {'screen_off', 'screen_on'})
        self.assertGreater(manifest['screen_states']['screen_on']['emission_strength'], 0.0)
        self.assertLessEqual(manifest['screen_states']['screen_on']['emission_strength'], 1.0)
        self.assertEqual(manifest['screen_states']['screen_off']['emission_strength'], 0.0)
        self.assertEqual(manifest['screen_glow']['anchor'], 'SCREEN_GLOW_ANCHOR')
        self.assertEqual(manifest['screen_glow']['type'], 'rect_area')
        self.assertGreater(manifest['screen_glow']['source_energy_w'], 0.0)
        self.assertLessEqual(manifest['screen_glow']['source_energy_w'], 10.0)

    def test_v1_glbs_preserve_hinge_and_web_critical_nodes(self):
        manifest = contract.load_manifest(MANIFEST)
        compat = RUNTIME / manifest['web_variants']['compat']['file']
        meshopt = RUNTIME / manifest['web_variants']['meshopt']['file']
        required = {
            'CTRL_MACBOOK_PRO_14', 'CTRL_HINGE', 'BASE_UNIBODY', 'LID_UNIBODY',
            'SCREEN_CONTENT', 'SCREEN_GLASS', 'FACETIME_CAMERA', 'TRACKPAD',
            'TOUCH_ID', 'MAGSAFE', 'HDMI', 'SDXC', 'APPLE_LOGO_RELEASE',
            'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
            'SCREEN_GLOW_ANCHOR',
        }
        self.assertTrue(required <= glb_node_names(compat))
        self.assertTrue(required <= glb_node_names(meshopt))
        self.assertEqual(manifest['default_web_variant'], 'compat')
        self.assertEqual(manifest['preferred_web_variant'], 'meshopt')
        doc = glb_doc(compat)
        screen_material = next(m for m in doc['materials'] if m.get('name') == 'MAT_SCREEN_CONTENT')
        self.assertIn('baseColorTexture', screen_material['pbrMetallicRoughness'])
        self.assertIn('emissiveTexture', screen_material)
        animation_names = {a.get('name') for a in doc.get('animations', [])}
        self.assertTrue({'lid_open', 'lid_close'} <= animation_names)


if __name__ == '__main__':
    unittest.main()
