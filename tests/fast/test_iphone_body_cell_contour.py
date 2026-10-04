"""Pure geometry seam: authored capsule vertices survive annulus sampling."""
import ast
import math
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[2] / 'assets/device_mockups/iphone_17/body_topology_v30.py'


def geometry_functions():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    names = {'_point_in_polygon', '_matched_annulus_loops', '_capsule'}
    module = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names], type_ignores=[])
    namespace = {'math': math}
    exec(compile(module, str(SOURCE), 'exec'), namespace)
    return namespace


class BodyCellContourTests(unittest.TestCase):
    def test_authored_capsule_vertices_survive_sampling(self):
        functions = geometry_functions()
        for steps in (8, 12, 16):
            with self.subTest(steps=steps):
                hole = functions['_capsule'](.01948, .00304, .01826, steps=steps)
                outer, rebuilt = functions['_matched_annulus_loops'](-.00725 / 2, .00725 / 2, .006, .032, hole)
                loss = max(min(math.dist(vertex, sampled) for sampled in rebuilt) for vertex in hole)
                self.assertLessEqual(loss, 1e-8, 'authored capsule contour collapsed')
                self.assertEqual(len(outer), len(rebuilt))


if __name__ == '__main__':
    unittest.main()
