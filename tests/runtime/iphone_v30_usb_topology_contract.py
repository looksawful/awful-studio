"""USB cavity/tongue production surfaces are explicit saved/exported geometry."""
import bpy
import bmesh
import json

names = ('USB_C_CAVITY', 'USB_C_TONGUE')
report = {}
for name in names:
    obj = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(obj.data)
    row = {'vertices': len(bm.verts), 'faces': len(bm.faces),
           'ngons': sum(len(f.verts) > 4 for f in bm.faces),
           'nonmanifold': sum(not e.is_manifold for e in bm.edges),
           'zero_edges': sum(e.calc_length() < 1e-12 for e in bm.edges),
           'degenerate_faces': sum(f.calc_area() < 1e-16 for f in bm.faces),
           'modifiers': [m.type for m in obj.modifiers]}
    bm.free(); report[name] = row
    assert not row['modifiers'], (name, 'USB physical bevel must be saved geometry', report)
    assert not any(row[k] for k in ('ngons','nonmanifold','zero_edges','degenerate_faces')), report
    assert len(obj.data.uv_layers) == 1, name
    assert obj.parent.name == 'CTRL_IPHONE_17', name
    expected_material = 'MAT_APERTURE_GRILLE' if name == 'USB_C_CAVITY' else 'MAT_ALUMINUM_EDGE'
    assert [m.name for m in obj.data.materials] == [expected_material], name
print('IPHONE_USB_TOPOLOGY_GREEN', json.dumps(report, sort_keys=True))

from pathlib import Path
import struct
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tests/fast'))
from test_iphone_dimensional_drawing_contract import read_glb, accessor_vec3


def point_key(point):
    return tuple(round(value, 7) for value in point)


def mapped_source_point(vertex):
    return point_key((vertex.co.x, vertex.co.z, -vertex.co.y))


def triangle_area(points):
    first = tuple(points[1][axis] - points[0][axis] for axis in range(3))
    second = tuple(points[2][axis] - points[0][axis] for axis in range(3))
    cross = (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )
    return 0.5 * sum(value * value for value in cross) ** 0.5


doc, blob = read_glb(repo / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb')
for name in names:
    mesh = bpy.data.objects[name].data
    authored = []
    for polygon in mesh.polygons:
        vertices = frozenset(mapped_source_point(mesh.vertices[index]) for index in polygon.vertices)
        authored.append({
            'vertices': vertices,
            'expected_triangles': len(polygon.vertices) - 2,
            'area': polygon.area,
            'exported_triangles': 0,
            'exported_area': 0.0,
        })

    node = next(n for n in doc['nodes'] if n.get('name') == name)
    exported_count = 0
    for primitive in doc['meshes'][node['mesh']]['primitives']:
        positions = accessor_vec3(doc, blob, primitive['attributes']['POSITION'])
        accessor = doc['accessors'][primitive['indices']]
        view = doc['bufferViews'][accessor['bufferView']]
        code = {5121:'B',5123:'H',5125:'I'}[accessor['componentType']]
        size = struct.calcsize('<' + code)
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        indices = [
            struct.unpack_from('<' + code, blob, offset + index * size)[0]
            for index in range(accessor['count'])
        ]
        for index in range(0, len(indices), 3):
            points = [positions[vertex] for vertex in indices[index:index + 3]]
            triangle = frozenset(point_key(point) for point in points)
            candidates = [face for face in authored if triangle <= face['vertices']]
            assert len(candidates) == 1, (
                name,
                'exported triangle does not map uniquely to one authored face',
                tuple(sorted(triangle)),
                len(candidates),
            )
            face = candidates[0]
            face['exported_triangles'] += 1
            face['exported_area'] += triangle_area(points)
            exported_count += 1

    for face in authored:
        assert face['exported_triangles'] == face['expected_triangles'], (
            name, 'authored face triangulation count changed', face,
        )
        # GLB positions are float32; tiny physical bevel faces need a small absolute area floor.
        tolerance = max(2e-12, face['area'] * 1e-5)
        assert abs(face['exported_area'] - face['area']) <= tolerance, (
            name, 'exported triangles do not cover authored face area', face,
        )

    assert exported_count == sum(face['expected_triangles'] for face in authored), name
    print('IPHONE_USB_EXPORTED_SURFACE_GREEN', name, {
        'authored_faces': len(authored),
        'exported_triangles': exported_count,
    })

print('IPHONE_USB_EXPORTED_TRIANGLES_GREEN', names)
