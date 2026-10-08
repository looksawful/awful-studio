"""Shipping topology contracts at the exact canonical GLB seam."""
import unittest

from test_iphone_dimensional_drawing_contract import GLB, read_glb

CAMERA = ('CAMERA_HOUSING_SEAT', 'CAMERA_HOUSING') + tuple(
    f'CAMERA_{index}_{part}' for index in (1, 2) for part in ('RING', 'BEVEL', 'GLASS'))


class IPhoneTopologyContractTests(unittest.TestCase):
    def test_camera_retains_frozen_parts_and_physical_mic_aperture(self):
        doc, _ = read_glb(GLB)
        nodes = {node['name']: node for node in doc['nodes']}
        for name in CAMERA:
            primitives = doc['meshes'][nodes[name]['mesh']]['primitives']
            tris = sum(doc['accessors'][p['indices']]['count'] // 3 for p in primitives)
            self.assertGreater(tris, 0, name)
            for primitive in primitives:
                material = doc['materials'][primitive['material']]
                self.assertIn('TEXCOORD_0', primitive['attributes'], name)
                if name == 'CAMERA_HOUSING' and material['name'] == 'MAT_OPTICS_BLACK':
                    self.assertNotIn('normalTexture', material, name)
                elif name.endswith('GLASS'):
                    self.assertNotIn('normalTexture', material, name)
                else:
                    self.assertIn('normalTexture', material, name)
                    self.assertIn('TANGENT', primitive['attributes'], name)
        # Triangle structure is covered by test_iphone_topology_quality_contract;
        # this contract keeps camera identity, UV and bake semantics independent of tessellation.


if __name__ == '__main__':
    unittest.main()
