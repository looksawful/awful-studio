import json
import pathlib
import struct
import unittest

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLB = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb'
MANIFEST = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json'
EVIDENCE = ROOT / 'assets/device_mockups/iphone_17/evidence/low_v30_validation.json'
SCREEN_STATE = ROOT / 'assets/device_mockups/iphone_17/reference/ios26_home_screen_dynamic_state_1206x2622.png'
SCREEN_W_MM = 66.57


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


def accessor_indices(doc, blob, accessor_index):
    accessor = doc['accessors'][accessor_index]
    view = doc['bufferViews'][accessor['bufferView']]
    offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    fmt = {5121: 'B', 5123: 'H', 5125: 'I'}[accessor['componentType']]
    return struct.unpack_from('<' + fmt * accessor['count'], blob, offset)


def point_in_triangle_2d(point, a, b, c):
    def side(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = side(point, a, b)
    d2 = side(point, b, c)
    d3 = side(point, c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


class IPhoneWebShadingContractTests(unittest.TestCase):
    def test_manifest_exposes_official_iphone17_colorway_variants(self):
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.assertEqual(manifest['default_colorway'], 'black')
        self.assertEqual(
            [variant['id'] for variant in manifest['colorways']],
            ['black', 'white', 'mist_blue', 'sage', 'lavender'],
        )
        self.assertEqual(
            [variant['label'] for variant in manifest['colorways']],
            ['Black', 'White', 'Mist Blue', 'Sage', 'Lavender'],
        )

    def test_visible_finish_materials_export_real_pbr_maps(self):
        doc, _ = read_glb(GLB)
        materials = {material.get('name'): material for material in doc['materials']}
        images = doc.get('images', [])
        textures = doc.get('textures', [])

        def image_name(texture_ref):
            texture = textures[texture_ref['index']]
            return images[texture['source']].get('name', '')

        expected = {
            'MAT_FASTENER': ('pentalobe_fastener_normal', 'pentalobe_fastener_roughness'),
            'MAT_ANODIZED_ALUMINUM': ('anodized_aluminum_normal', 'anodized_aluminum_roughness'),
            'MAT_ALUMINUM_EDGE': ('anodized_aluminum_normal', 'anodized_aluminum_roughness'),
            'MAT_BACK_GLASS': ('back_glass_micro_normal', 'back_glass_micro_roughness'),
            'MAT_CAMERA_CONTROL_GLASS': ('camera_control_normal', 'camera_control_roughness'),
        }
        for material_name, (normal_name, roughness_name) in expected.items():
            material = materials[material_name]
            if material_name == 'MAT_FASTENER':
                pbr = material['pbrMetallicRoughness']
                self.assertIn('baseColorTexture', pbr, material_name)
                self.assertIn('pentalobe_fastener_basecolor', image_name(pbr['baseColorTexture']), material_name)
            self.assertIn('normalTexture', material, material_name)
            self.assertIn(normal_name, image_name(material['normalTexture']), material_name)
            pbr = material['pbrMetallicRoughness']
            self.assertIn('metallicRoughnessTexture', pbr, material_name)
            self.assertIn(roughness_name, image_name(pbr['metallicRoughnessTexture']), material_name)

        camera_housing = materials['MAT_CAMERA_HOUSING']['pbrMetallicRoughness']
        self.assertIn('metallicRoughnessTexture', camera_housing)
        self.assertIn(
            'anodized_aluminum_roughness',
            image_name(camera_housing['metallicRoughnessTexture']),
        )

        nodes = {node.get('name'): node for node in doc['nodes']}
        for node_name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_HOUSING', 'CAMERA_1_RING',
                          'ACTION_BUTTON', 'VOL_UP', 'VOL_DOWN', 'SIDE_BUTTON', 'CAMERA_CONTROL',
                          'BOTTOM_SCREW_L'):
            mesh = doc['meshes'][nodes[node_name]['mesh']]
            self.assertTrue(
                all('TEXCOORD_0' in primitive['attributes'] for primitive in mesh['primitives']),
                f'{node_name} must export UVs for PBR maps',
            )
            if node_name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_1_RING',
                             'ACTION_BUTTON', 'VOL_UP', 'VOL_DOWN', 'SIDE_BUTTON', 'CAMERA_CONTROL',
                             'BOTTOM_SCREW_L'):
                self.assertTrue(
                    all('TANGENT' in primitive['attributes'] for primitive in mesh['primitives']),
                    f'{node_name} must export tangents for normal mapping',
                )

    def test_closed_shells_have_outward_winding(self):
        doc, blob = read_glb(GLB)
        for name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_HOUSING', 'CAMERA_HOUSING_SEAT'):
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

    def test_body_corner_profile_tracks_apple_detail_a(self):
        doc, blob = read_glb(GLB)
        mesh = next(mesh for mesh in doc['meshes'] if mesh.get('name') == 'BODY_ALUMINUM')
        primitive = mesh['primitives'][0]
        positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])

        max_x = max(position[0] for position in positions)
        max_y = max(position[1] for position in positions)
        max_z = max(position[2] for position in positions)
        front_quadrant = [
            position
            for position in positions
            if abs(position[2] - max_z) < 1e-7
            and position[0] >= 0.0
            and position[1] >= 0.0
        ]
        self.assertTrue(front_quadrant)

        # Apple iPhone 17 Dimensional Drawings, Corner Profile Detail A.
        detail_a_mm = (
            (0.00, 19.23),
            (0.02, 14.53),
            (0.48, 9.87),
            (2.26, 5.56),
            (5.56, 2.26),
            (9.87, 0.48),
            (14.53, 0.02),
            (19.23, 0.00),
        )
        for inset_x_mm, inset_y_mm in detail_a_mm:
            target_x = max_x - inset_x_mm / 1000.0
            target_y = max_y - inset_y_mm / 1000.0
            nearest_mm = min(
                (
                    (position[0] - target_x) ** 2
                    + (position[1] - target_y) ** 2
                ) ** 0.5
                * 1000.0
                for position in front_quadrant
            )
            self.assertLessEqual(
                nearest_mm,
                0.5,
                f'BODY_ALUMINUM misses Apple Detail A point '
                f'({inset_x_mm:.2f}, {inset_y_mm:.2f}) mm by {nearest_mm:.3f} mm',
            )

    def test_dynamic_island_inner_hardware_has_balanced_edge_padding(self):
        image = Image.open(SCREEN_STATE).convert('L')
        crop_left, crop_top, crop_right, crop_bottom = 350, 0, 856, 180
        crop = image.crop((crop_left, crop_top, crop_right, crop_bottom))
        width, height = crop.size
        pixels = crop.load()
        seen = set()
        components = []

        for y in range(height):
            for x in range(width):
                if (x, y) in seen or pixels[x, y] >= 28:
                    continue
                stack = [(x, y)]
                seen.add((x, y))
                xs, ys = [], []
                while stack:
                    px, py = stack.pop()
                    xs.append(px)
                    ys.append(py)
                    for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and pixels[nx, ny] < 28:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
                components.append((len(xs), min(xs) + crop_left, max(xs) + 1 + crop_left))

        _, island_left_px, island_right_px = max(components)
        island_left_mm = (island_left_px / image.width - 0.5) * SCREEN_W_MM
        island_right_mm = (island_right_px / image.width - 0.5) * SCREEN_W_MM

        doc, blob = read_glb(GLB)

        def x_bounds_mm(name):
            node = next(node for node in doc['nodes'] if node.get('name') == name)
            mesh = doc['meshes'][node['mesh']]
            xs = []
            for primitive in mesh['primitives']:
                xs.extend(position[0] for position in accessor_vec3(doc, blob, primitive['attributes']['POSITION']))
            tx = node.get('translation', [0, 0, 0])[0]
            return (tx + min(xs)) * 1000.0, (tx + max(xs)) * 1000.0

        sensor_left_mm, sensor_right_mm = x_bounds_mm('FRONT_SENSOR_MASK')
        camera_left_mm, camera_right_mm = x_bounds_mm('FRONT_CAMERA_MASK')
        left_padding = sensor_left_mm - island_left_mm
        right_padding = island_right_mm - camera_right_mm

        self.assertLessEqual(abs(left_padding - right_padding), 0.15)
        self.assertLessEqual(max(left_padding, right_padding), 3.20)

        rgb = Image.open(SCREEN_STATE).convert('RGB')
        orange_x = []
        for y in range(70, 125):
            for x in range(560, 720):
                r, g, b = rgb.getpixel((x, y))
                if r > 220 and 80 <= g <= 180 and b < 40:
                    orange_x.append(x)
        self.assertTrue(orange_x, 'privacy indicator missing from screen state')
        orange_center_mm = ((sum(orange_x) / len(orange_x)) / rgb.width - 0.5) * SCREEN_W_MM
        gap_midpoint_mm = (sensor_right_mm + camera_left_mm) * 0.5
        self.assertLessEqual(abs(orange_center_mm - gap_midpoint_mm), 0.20)

    def test_front_sensor_masks_and_camera_stack_recede_behind_screen_front(self):
        doc, _ = read_glb(GLB)
        names = {node.get('name') for node in doc.get('nodes', [])}
        self.assertNotIn('DYNAMIC_ISLAND', names, 'front hardware must not be one glossy external capsule')

        masks = []
        for name in ('FRONT_SENSOR_MASK', 'FRONT_CAMERA_MASK'):
            node = next((node for node in doc['nodes'] if node.get('name') == name), None)
            self.assertIsNotNone(node, f'missing {name}')
            mesh = doc['meshes'][node['mesh']]
            indices = {primitive['material'] for primitive in mesh['primitives']}
            self.assertEqual(len(indices), 1)
            material = doc['materials'][indices.pop()]
            self.assertEqual(material.get('name'), 'MAT_UNDER_GLASS_BLACK')
            pbr = material.get('pbrMetallicRoughness', {})
            self.assertLess(max(pbr.get('baseColorFactor', [1, 1, 1, 1])[:3]), 0.001)
            self.assertEqual(pbr.get('metallicFactor', 0), 0)
            self.assertGreaterEqual(pbr.get('roughnessFactor', 1.0), 0.9)
            self.assertNotIn('KHR_materials_clearcoat', material.get('extensions', {}))
            masks.append(node)

        screen = next(node for node in doc['nodes'] if node.get('name') == 'SCREEN_CONTENT')
        screen_front_z = screen['translation'][2] + (0.35 - 0.025) / 2000.0
        for node in masks:
            self.assertLess(
                node['translation'][2],
                screen_front_z,
                f"{node['name']} must sit behind the screen front plane",
            )

        camera_mask = next(node for node in doc['nodes'] if node.get('name') == 'FRONT_CAMERA_MASK')
        camera_stack = [
            next(node for node in doc['nodes'] if node.get('name') == name)
            for name in ('FRONT_CAMERA_GLASS', 'FRONT_CAMERA_INNER', 'FRONT_CAMERA_IRIS', 'FRONT_CAMERA_PUPIL')
        ]
        for node in camera_stack:
            self.assertAlmostEqual(node['translation'][0], camera_mask['translation'][0], places=6)
            self.assertAlmostEqual(node['translation'][1], camera_mask['translation'][1], places=6)

        depths = [camera_mask['translation'][2], *(node['translation'][2] for node in camera_stack)]
        self.assertTrue(
            all(outer > inner for outer, inner in zip(depths, depths[1:])),
            f'camera stack must recede inward monotonically: {depths}',
        )
        self.assertGreaterEqual(
            (camera_mask['translation'][2] - camera_stack[0]['translation'][2]) * 1000.0,
            0.03,
            'front camera optic needs a visible recess behind the camera aperture',
        )

    def test_screen_front_stays_clean_under_independent_front_hardware(self):
        doc, blob = read_glb(GLB)
        mesh = next(mesh for mesh in doc['meshes'] if mesh.get('name') == 'SCREEN_CONTENT')
        targets = {}
        for name in ('FRONT_SENSOR_MASK', 'FRONT_CAMERA_MASK'):
            node = next(node for node in doc['nodes'] if node.get('name') == name)
            targets[name] = (node['translation'][0], node['translation'][1])
        covered = {name: 0 for name in targets}

        for primitive in mesh['primitives']:
            material = doc['materials'][primitive['material']]
            if material.get('name') != 'MAT_SCREEN_CONTENT':
                continue
            positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])
            normals = accessor_vec3(doc, blob, primitive['attributes']['NORMAL'])
            indices = accessor_indices(doc, blob, primitive['indices'])
            for offset in range(0, len(indices), 3):
                tri = indices[offset:offset + 3]
                if min(normals[index][2] for index in tri) < 0.99:
                    continue
                points = [(positions[index][0], positions[index][1]) for index in tri]
                for name, target in targets.items():
                    if point_in_triangle_2d(target, *points):
                        covered[name] += 1

        self.assertTrue(
            all(count > 0 for count in covered.values()),
            f'clean SCREEN_CONTENT must remain continuous under independent front hardware: {covered}',
        )

    def test_rear_camera_protrusions_preserve_depth_and_baked_edge_response(self):
        # Human-PASS representation: physical silhouette/depth plus tangent bakes.
        # Counting bevel depth planes would force the rejected dense delivery.
        from test_iphone_dimensional_drawing_contract import node_world_bounds_mm
        from test_iphone_topology_contract import CAMERA
        doc, blob = read_glb(GLB)
        nodes = {node['name']: node for node in doc['nodes']}
        back_min, _ = node_world_bounds_mm(doc, blob, 'BACK_GLASS')
        total = 0
        for name in CAMERA:
            primitives = doc['meshes'][nodes[name]['mesh']]['primitives']
            total += sum(doc['accessors'][p['indices']]['count'] // 3 for p in primitives)
            mins, maxs = node_world_bounds_mm(doc, blob, name)
            expected_depth = (.30 if name.endswith('SEAT') else 1.78) if 'HOUSING' in name else (1.10 if name.endswith('RING') else .70)
            self.assertAlmostEqual(maxs[2] - mins[2], expected_depth, delta=.001, msg=name)
            if name == 'CAMERA_HOUSING' or name.endswith('GLASS'):
                self.assertAlmostEqual(back_min[2] - mins[2], 1.78 if name == 'CAMERA_HOUSING' else 3.45, delta=.001, msg=name)
            part = ('seat' if name.endswith('SEAT') else 'housing') if 'HOUSING' in name else name.rsplit('_', 1)[1].lower()
            for primitive in primitives:
                material = doc['materials'][primitive['material']]
                self.assertIn('TEXCOORD_0', primitive['attributes'], name)
                if part == 'glass':
                    self.assertNotIn('normalTexture', material, name)
                else:
                    self.assertIn('normalTexture', material, name)
                    texture = doc['textures'][material['normalTexture']['index']]
                    image = doc['images'][texture['source']]
                    self.assertEqual(image['name'], f'{part}_40_normal', name)
                    view = doc['bufferViews'][image['bufferView']]
                    png = blob[view.get('byteOffset', 0):view.get('byteOffset', 0) + view['byteLength']]
                    self.assertEqual(struct.unpack_from('>II', png, 16), (512, 512), name)
                    self.assertIn('TANGENT', primitive['attributes'], name)
        self.assertEqual(total, 1288, 'frozen eight-mesh camera scope')

    def test_camera_control_is_separate_dark_glass_and_recessed(self):
        doc, _ = read_glb(GLB)
        node = next(node for node in doc['nodes'] if node.get('name') == 'CAMERA_CONTROL')
        mesh = doc['meshes'][node['mesh']]
        indices = {primitive['material'] for primitive in mesh['primitives']}
        self.assertEqual(len(indices), 1, 'CAMERA_CONTROL must use exactly one material')
        material = doc['materials'][indices.pop()]
        self.assertEqual(material.get('name'), 'MAT_CAMERA_CONTROL_GLASS')

        pbr = material.get('pbrMetallicRoughness', {})
        color = pbr.get('baseColorFactor', [1, 1, 1, 1])
        self.assertLess(max(color[:3]), 0.003, 'Camera Control glass is too light')
        self.assertEqual(pbr.get('metallicFactor', 0), 0, 'Camera Control must remain dielectric')
        roughness_texture = pbr.get('metallicRoughnessTexture')
        self.assertIsNotNone(roughness_texture, 'Camera Control lost its roughness texture')
        image_index = doc['textures'][roughness_texture['index']]['source']
        self.assertIn('camera_control_roughness', doc['images'][image_index].get('name', ''))

        evidence = json.loads(EVIDENCE.read_text(encoding='utf-8'))
        self.assertAlmostEqual(evidence['camera_control_recess_mm'], 0.10, delta=0.025)

    def test_front_camera_optic_has_embedded_detail_mask_without_replacing_base_tint(self):
        doc, _ = read_glb(GLB)
        material_index = next(i for i, item in enumerate(doc['materials']) if item.get('name') == 'MAT_FRONT_OPTIC')
        material = doc['materials'][material_index]
        pbr = material.get('pbrMetallicRoughness', {})
        texture = pbr.get('baseColorTexture')
        self.assertIsNotNone(texture, 'front camera lost its image detail mask')
        self.assertLess(max(pbr.get('baseColorFactor', [1, 1, 1, 1])[:3]), 0.02, 'detail mask replaced the dark optic base tint')

        image_index = doc['textures'][texture['index']]['source']
        self.assertIn('bufferView', doc['images'][image_index], 'front camera detail mask must be embedded')

        primitives = [
            primitive
            for mesh in doc['meshes']
            for primitive in mesh['primitives']
            if primitive.get('material') == material_index
        ]
        self.assertTrue(primitives)
        self.assertTrue(all('TEXCOORD_0' in primitive['attributes'] for primitive in primitives))

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
