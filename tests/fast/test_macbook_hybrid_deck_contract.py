import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'assets/device_mockups/macbook_pro_14/runtime/v1'
MANIFEST = RUNTIME / 'macbook_pro_14_m5_v1.asset.json'
GLB = RUNTIME / 'macbook_pro_14_m5_v1_web.glb'


def glb_doc(path: Path) -> dict:
    raw = path.read_bytes()
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        raise AssertionError(f'invalid GLB JSON chunk: {path}')
    return json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\0'))


class MacBookHybridDeckContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.doc = glb_doc(GLB)
        self.nodes = {n.get('name'): n for n in self.doc.get('nodes', []) if n.get('name')}
        self.materials = {m.get('name'): m for m in self.doc.get('materials', []) if m.get('name')}

    def position_count(self, node_name: str) -> int:
        node = self.nodes[node_name]
        mesh = self.doc['meshes'][node['mesh']]
        primitive = mesh['primitives'][0]
        accessor = primitive['attributes']['POSITION']
        return self.doc['accessors'][accessor]['count']

    def test_runtime_uses_clean_body_plus_derived_speaker_proxy(self):
        hybrid = self.manifest['hybrid_deck']
        self.assertEqual(hybrid['speaker_runtime'], 'derived_alpha_normal_proxy')
        self.assertLess(self.position_count('BASE_UNIBODY'), 30000)
        speaker_nodes = sorted(name for name in self.nodes if 'SPEAKER' in name)
        self.assertEqual(speaker_nodes, ['SPEAKER_RUNTIME_PROXY_L', 'SPEAKER_RUNTIME_PROXY_R'])
        self.assertNotIn('BASE_UNIBODY_MASTER_SOURCE', self.nodes)
        self.assertNotIn('BASE_UNIBODY_RUNTIME_SOURCE', self.nodes)
        speaker = self.materials['MAT_SPEAKER_PROXY']
        self.assertIn('baseColorTexture', speaker['pbrMetallicRoughness'])
        self.assertIn('normalTexture', speaker)
        self.assertIn(speaker.get('alphaMode'), {'BLEND', 'MASK'})

    def test_runtime_metrics_are_recorded_in_manifest(self):
        qa = self.manifest['glb_qa']
        self.assertGreater(qa['render_mesh_count'], 0)
        self.assertGreater(qa['compat_bytes'], 0)
        self.assertGreater(qa['meshopt_bytes'], 0)

    def test_trackpad_key_families_and_dark_material_hierarchy_ship(self):
        self.assertGreaterEqual(self.position_count('TRACKPAD'), 600)
        expected = {
            'KEY_03_01': 'regular',
            'KEY_00_00': 'modifier',
            'KEY_00_04': 'space',
            'KEY_ARROW_0': 'arrow',
        }
        for name, family in expected.items():
            self.assertEqual(self.nodes[name].get('extras', {}).get('key_family'), family)

        key = self.materials['MAT_KEYCAP']['pbrMetallicRoughness']
        well = self.materials['MAT_KEYBOARD_WELL']['pbrMetallicRoughness']
        port = self.materials['MAT_PORT_DARK']['pbrMetallicRoughness']
        track = self.materials['MAT_TRACKPAD']['pbrMetallicRoughness']
        self.assertGreaterEqual(key['roughnessFactor'], 0.72)
        self.assertGreaterEqual(well['roughnessFactor'], 0.62)
        self.assertGreaterEqual(port['roughnessFactor'], 0.50)
        self.assertLessEqual(track.get('metallicFactor', 0.0), 0.10)
        self.assertGreaterEqual(track['roughnessFactor'], 0.18)
        self.assertLessEqual(track['roughnessFactor'], 0.35)


if __name__ == '__main__':
    unittest.main()
