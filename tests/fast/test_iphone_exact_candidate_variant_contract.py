from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import device_delivery_contract as contract

MANIFEST = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json'


class IphoneExactCandidateVariantContractTests(unittest.TestCase):
    def test_compat_and_meshopt_preserve_all_exported_mesh_semantics(self):
        manifest = contract.load_manifest(MANIFEST)
        runtime = MANIFEST.parent
        documents = {
            variant: contract.load_glb_document(runtime / manifest['web_variants'][variant]['file'])
            for variant in ('compat', 'meshopt')
        }

        def parents(document):
            return {
                document['nodes'][child].get('name'): node.get('name')
                for node in document['nodes']
                for child in node.get('children', [])
            }

        def materials(document):
            names = [material.get('name') for material in document.get('materials', [])]
            return {
                node['name']: sorted({
                    names[primitive['material']]
                    for primitive in document['meshes'][node['mesh']].get('primitives', [])
                    if 'material' in primitive
                })
                for node in document['nodes']
                if 'mesh' in node
            }

        compat, meshopt = documents['compat'], documents['meshopt']
        compat_meshes = materials(compat)
        meshopt_meshes = materials(meshopt)
        self.assertEqual(len(compat_meshes), 51)
        self.assertEqual(compat_meshes, meshopt_meshes)
        self.assertEqual(parents(compat), parents(meshopt))

        compat_world = contract._world_matrices(compat)
        meshopt_world = contract._world_matrices(meshopt)
        compat_indices = {node.get('name'): index for index, node in enumerate(compat['nodes'])}
        meshopt_indices = {node.get('name'): index for index, node in enumerate(meshopt['nodes'])}

        for name in compat_meshes:
            expected = contract._node_mesh_bounds(compat, compat_world, compat_indices[name])
            actual = contract._node_mesh_bounds(meshopt, meshopt_world, meshopt_indices[name])
            with self.subTest(mesh=name):
                for expected_edge, actual_edge in zip(expected, actual):
                    for expected_value, actual_value in zip(expected_edge, actual_edge):
                        self.assertAlmostEqual(expected_value, actual_value, delta=0.00001)


if __name__ == '__main__':
    unittest.main()
