import json
import pathlib
import struct
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLB = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb'


def read_glb(path):
    raw = path.read_bytes()
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        raise AssertionError('first GLB chunk is not JSON')
    doc = json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\0'))
    offset = 20 + json_len
    bin_len, bin_type = struct.unpack_from('<II', raw, offset)
    if bin_type != 0x004E4942:
        raise AssertionError('second GLB chunk is not BIN')
    return doc, raw[offset + 8:offset + 8 + bin_len]


def accessor_vec3(doc, blob, accessor_index):
    accessor = doc['accessors'][accessor_index]
    view = doc['bufferViews'][accessor['bufferView']]
    self_offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', 12)
    values = []
    for index in range(accessor['count']):
        start = self_offset + index * stride
        values.append(struct.unpack_from('<fff', blob, start))
    return values


class IPhoneWebShadingContractTests(unittest.TestCase):
    def test_closed_shells_have_outward_winding(self):
        doc, blob = read_glb(GLB)
        for name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_HOUSING', 'CAMERA_HOUSING_SEAT', 'DYNAMIC_ISLAND'):
            mesh = next(mesh for mesh in doc['meshes'] if mesh.get('name') == name)
            volume = 0.0
            for primitive in mesh['primitives']:
                positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])
                accessor = doc['accessors'][primitive['indices']]
                view = doc['bufferViews'][accessor['bufferView']]
                offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                fmt = {5121: 'B', 5123: 'H', 5125: 'I'}[accessor['componentType']]
                indices = struct.unpack_from('<' + fmt * accessor['count'], blob, offset)
                for i in range(0, len(indices), 3):
                    a, b, c = (positions[indices[i+j]] for j in range(3))
                    cross = (b[1]*c[2]-b[2]*c[1], b[2]*c[0]-b[0]*c[2], b[0]*c[1]-b[1]*c[0])
                    volume += sum(a[k]*cross[k] for k in range(3)) / 6.0
            self.assertGreater(volume, 0.0, f'{name}: inverted or mixed triangle winding')

    def test_back_glass_vertex_normals_face_outward(self):
        doc, blob = read_glb(GLB)
        mesh = next(mesh for mesh in doc['meshes'] if mesh.get('name') == 'BACK_GLASS')
        for primitive in mesh['primitives']:
            positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])
            normals = accessor_vec3(doc, blob, primitive['attributes']['NORMAL'])
            inward = sum(sum(p[k]*n[k] for k in range(3)) < -1e-7 for p, n in zip(positions, normals))
            self.assertEqual(inward, 0, f'BACK_GLASS has {inward} inward vertex normals')

    def test_flash_has_embedded_image_and_uvs(self):
        doc, blob = read_glb(GLB)
        material_index = next(i for i, item in enumerate(doc['materials']) if item.get('name') == 'MAT_FLASH')
        material = doc['materials'][material_index]
        texture = material.get('pbrMetallicRoughness', {}).get('baseColorTexture')
        self.assertIsNotNone(texture, 'flash diffuser is an untextured white disk')
        image_index = doc['textures'][texture['index']]['source']
        self.assertIn('bufferView', doc['images'][image_index], 'flash image must be embedded')
        primitives = [p for mesh in doc['meshes'] for p in mesh['primitives'] if p.get('material') == material_index]
        self.assertTrue(primitives)
        self.assertTrue(all('TEXCOORD_0' in p['attributes'] for p in primitives))

    def test_screen_content_is_opaque(self):
        doc, _ = read_glb(GLB)
        material = next(item for item in doc['materials'] if item.get('name') == 'MAT_SCREEN_CONTENT')
        self.assertNotEqual(material.get('alphaMode', 'OPAQUE'), 'BLEND')

    def test_grille_normal_is_embedded_and_uv_mapped(self):
        doc, _ = read_glb(GLB)
        material_index = next((i for i, material in enumerate(doc['materials']) if material.get('name') == 'MAT_APERTURE_GRILLE'), None)
        self.assertIsNotNone(material_index, 'cavities still reuse reflective lens material')
        material = doc['materials'][material_index]
        texture = material.get('normalTexture')
        self.assertIsNotNone(texture, 'grille normal missing from GLB')
        image = doc['images'][doc['textures'][texture['index']]['source']]
        self.assertIn('bufferView', image, 'normal image must travel inside GLB')
        for mesh in doc['meshes']:
            for primitive in mesh['primitives']:
                if primitive.get('material') == material_index:
                    self.assertIn('TEXCOORD_0', primitive['attributes'])
                    self.assertIn('TANGENT', primitive['attributes'], 'normal mapped grilles need portable tangent space')

    def test_canonical_screen_edges_do_not_sample_or_emit_screen_pixels(self):
        doc, _ = read_glb(GLB)
        screen = next(mesh for mesh in doc['meshes'] if mesh.get('name') == 'SCREEN_CONTENT')
        material_names = {doc['materials'][primitive['material']]['name'] for primitive in screen['primitives']}
        self.assertIn('MAT_SCREEN_EDGE', material_names, 'screen texture wraps around the edge')
        edge = next(material for material in doc['materials'] if material.get('name') == 'MAT_SCREEN_EDGE')
        self.assertNotIn('baseColorTexture', edge.get('pbrMetallicRoughness', {}))
        self.assertNotIn('emissiveTexture', edge)

    def test_web_delivery_has_one_screen_surface(self):
        doc, _ = read_glb(GLB)
        names = [node.get("name") for node in doc.get("nodes", [])]
        self.assertEqual(names.count("SCREEN_CONTENT"), 1)
        self.assertNotIn("SCREEN_GLASS", names, "web preview must not stack a second cover-glass mesh over the active screen")

    def test_apple_logo_normals_face_outward(self):
        doc, blob = read_glb(GLB)
        mesh = next(mesh for mesh in doc['meshes'] if mesh.get('name') == 'APPLE_LOGO_DECAL')
        primitive = mesh['primitives'][0]
        normals = accessor_vec3(doc, blob, primitive['attributes']['NORMAL'])
        self.assertTrue(normals)
        self.assertLess(
            sum(normal[2] for normal in normals) / len(normals),
            -0.99,
            'rear Apple decal must face outward (-Z in glTF)',
        )


if __name__ == '__main__':
    unittest.main()
