"""Shipping topology contracts at the exact canonical GLB seam."""
import unittest

from test_iphone_dimensional_drawing_contract import GLB, read_glb

CAMERA = ('CAMERA_HOUSING_SEAT', 'CAMERA_HOUSING') + tuple(
    f'CAMERA_{index}_{part}' for index in (1, 2) for part in ('RING', 'BEVEL', 'GLASS'))


class IPhoneTopologyContractTests(unittest.TestCase):
    def test_camera_reproduces_frozen_1288_triangle_delivery(self):
        doc, _ = read_glb(GLB)
        nodes = {node['name']: node for node in doc['nodes']}
        total = 0
        for name in CAMERA:
            primitives = doc['meshes'][nodes[name]['mesh']]['primitives']
            tris = sum(doc['accessors'][p['indices']]['count'] // 3 for p in primitives)
            self.assertEqual(tris, 164 if 'HOUSING' in name else 160, name)
            total += tris
            for primitive in primitives:
                material = doc['materials'][primitive['material']]
                self.assertIn('TEXCOORD_0', primitive['attributes'], name)
                if name.endswith('GLASS'):
                    self.assertNotIn('normalTexture', material, name)
                else:
                    self.assertIn('normalTexture', material, name)
                    self.assertIn('TANGENT', primitive['attributes'], name)
        self.assertEqual(total, 1288)


if __name__ == '__main__':
    unittest.main()
