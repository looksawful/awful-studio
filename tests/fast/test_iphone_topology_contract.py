"""Shipping topology contracts at the exact canonical GLB seam."""
import unittest
from collections import Counter

from test_iphone_dimensional_drawing_contract import GLB, read_glb
from test_iphone_web_shading_contract import accessor_vec3, accessor_indices

CAMERA = ('CAMERA_HOUSING_SEAT', 'CAMERA_HOUSING') + tuple(
    f'CAMERA_{index}_{part}' for index in (1, 2) for part in ('RING', 'BEVEL', 'GLASS'))


class IPhoneTopologyContractTests(unittest.TestCase):
    def test_body_delivery_carries_verified_authored_topology(self):
        doc, blob = read_glb(GLB)
        body = next(node for node in doc['nodes'] if node.get('name') == 'BODY_ALUMINUM')
        # GLB triangles alone cannot prove authored cap/rail topology.
        # Exporter records its own inspection of the exact mesh it exports.
        topology = body.get('extras', {}).get('source_topology', {})
        self.assertEqual(topology.get('ngons'), 0, 'BODY_ALUMINUM authored n-gons')
        self.assertEqual(topology.get('nonmanifold_edges'), 0, 'BODY_ALUMINUM shell')
        primitives = doc['meshes'][body['mesh']]['primitives']
        triangles = sum(doc['accessors'][p['indices']]['count'] // 3 for p in primitives)
        self.assertEqual(topology.get('triangles'), triangles)
        edges = Counter()
        for primitive in primitives:
            positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])
            indices = accessor_indices(doc, blob, primitive['indices'])
            for start in range(0, len(indices), 3):
                points = [positions[i] for i in indices[start:start + 3]]
                self.assertEqual(len(set(points)), 3, 'BODY_ALUMINUM degenerate runtime triangle')
                for a, b in ((0, 1), (1, 2), (2, 0)):
                    edges[tuple(sorted((points[a], points[b])))] += 1
        self.assertTrue(all(count == 2 for count in edges.values()), 'BODY_ALUMINUM runtime edge incidence')

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
