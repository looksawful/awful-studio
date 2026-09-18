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
RUNTIME = ROOT / 'assets/device_mockups/ipad_pro/runtime/v6'
CASES = {
    '11': ('ipad_pro_11_m5', 'DEVICE_IPAD_PRO_11', 'CTRL_IPAD_PRO_11'),
    '13': ('ipad_pro_13_m5', 'DEVICE_IPAD_PRO_13', 'CTRL_IPAD_PRO_13'),
}


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


class IPadWebDeliveryContractTests(unittest.TestCase):
    def test_v6_runtime_manifests_are_current_and_match_plugin_sources(self):
        loader = load_loader()
        for size, (asset_id, key, root_name) in CASES.items():
            manifest_path = RUNTIME / f'{asset_id}_v6.asset.json'
            self.assertTrue(manifest_path.is_file(), f'missing iPad {size} runtime manifest')
            manifest = contract.load_manifest(manifest_path)
            self.assertEqual(manifest['asset_id'], asset_id)
            self.assertEqual(manifest['version'], 'v6')
            self.assertEqual(manifest['stage'], 'LOW_DRAFT')
            self.assertEqual(contract.verify_manifest(ROOT, manifest), [])
            lod = loader.device_asset_spec(key)['lods']['LOW']
            self.assertEqual(manifest['plugin_source_revision'], lod['source_revision'])
            self.assertEqual(manifest['root'], root_name)
            self.assertEqual(set(manifest['screen_states']), {'screen_off', 'screen_on'})
            self.assertEqual(manifest['screen_states']['screen_off']['emission_strength'], 0.0)
            self.assertGreater(manifest['screen_states']['screen_on']['emission_strength'], 0.0)
            self.assertEqual(manifest['screen_glow']['anchor'], 'SCREEN_GLOW_ANCHOR')
            self.assertEqual(manifest['screen_glow']['type'], 'rect_area')
            self.assertLessEqual(manifest['screen_states']['screen_on']['emission_strength'], 1.0)
            self.assertIn(
                'developer.apple.com/download/files/accessories/dimensional-drawings/',
                manifest['dimensional_drawing_url'],
            )

    def test_v6_glbs_preserve_web_critical_nodes(self):
        for size, (asset_id, _key, root_name) in CASES.items():
            manifest = contract.load_manifest(RUNTIME / f'{asset_id}_v6.asset.json')
            compat = RUNTIME / manifest['web_variants']['compat']['file']
            meshopt = RUNTIME / manifest['web_variants']['meshopt']['file']
            required = {
                root_name, 'SCREEN_CONTENT', 'SCREEN_GLASS', 'FRONT_CAMERA_GLASS',
                'APPLE_LOGO_DECAL', 'CAMERA_HOUSING', 'REAR_CAMERA_GLASS', 'LIDAR',
                'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
                'ANCHOR_REAR_CAMERA', 'SCREEN_GLOW_ANCHOR',
            }
            self.assertTrue(required <= glb_node_names(compat))
            self.assertTrue(required <= glb_node_names(meshopt))
            self.assertEqual(manifest['default_web_variant'], 'compat')
            self.assertEqual(manifest['preferred_web_variant'], 'meshopt')
            doc = glb_doc(compat)
            screen_material = next(m for m in doc['materials'] if m.get('name') == 'MAT_SCREEN_CONTENT')
            self.assertIn('baseColorTexture', screen_material['pbrMetallicRoughness'])
            self.assertIn('emissiveTexture', screen_material)


if __name__ == '__main__':
    unittest.main()
