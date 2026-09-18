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
    def test_screen_content_is_opaque(self):
        doc, _ = read_glb(GLB)
        material = next(item for item in doc['materials'] if item.get('name') == 'MAT_SCREEN_CONTENT')
        self.assertNotEqual(material.get('alphaMode', 'OPAQUE'), 'BLEND')

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
