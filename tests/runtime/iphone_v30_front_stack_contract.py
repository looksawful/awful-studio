"""Front physical layers retain clean authored topology and independent hardware datum."""
import bpy
import bmesh
import json

names = ('FRONT_SENSOR_MASK', 'FRONT_CAMERA_MASK', 'FRONT_CAMERA_GLASS',
         'FRONT_CAMERA_INNER', 'FRONT_CAMERA_IRIS', 'FRONT_CAMERA_PUPIL', 'FRONT_RECEIVER_MIC')
report = {}
for name in names:
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    row = {'vertices': len(bm.verts), 'faces': len(bm.faces),
           'ngons': sum(len(f.verts) > 4 for f in bm.faces),
           'nonmanifold': sum(not e.is_manifold for e in bm.edges),
           'zero_edges': sum(e.calc_length() < 1e-12 for e in bm.edges),
           'degenerate_faces': sum(f.calc_area() < 1e-16 for f in bm.faces),
           'modifiers': [m.type for m in obj.modifiers]}
    bm.free()
    report[name] = row
    assert not any(row[k] for k in ('ngons', 'nonmanifold', 'zero_edges', 'degenerate_faces')), report
    assert not row['modifiers'], (name, 'front physical bevel must be authored', report)
    assert obj.parent.name == 'CTRL_IPHONE_17', name
    if name != 'FRONT_RECEIVER_MIC':
        assert abs(obj.location.z - (0.14961 / 2 - 0.00779)) < 1e-8, name
print('IPHONE_FRONT_STACK_TOPOLOGY_GREEN', json.dumps(report, sort_keys=True))

# Native +Y goes deeper into the device. Physical optical layers have finite gaps.
def y_bounds(name):
    obj = bpy.data.objects[name]
    values = [(obj.matrix_world @ v.co).y for v in obj.data.vertices]
    return min(values), max(values)
ordered = ('FRONT_CAMERA_MASK', 'FRONT_CAMERA_GLASS', 'FRONT_CAMERA_INNER',
           'FRONT_CAMERA_IRIS', 'FRONT_CAMERA_PUPIL')
for front, back in zip(ordered, ordered[1:]):
    assert y_bounds(front)[1] < y_bounds(back)[0], (front, back)
assert y_bounds('FRONT_SENSOR_MASK')[0] > y_bounds('SCREEN_CONTENT')[0]
assert y_bounds('FRONT_CAMERA_MASK')[0] > y_bounds('SCREEN_CONTENT')[0]
print('IPHONE_FRONT_DEPTH_ORDER_GREEN', {name: y_bounds(name) for name in ordered})

# Complete actual GLB triangles correspond to Blender's authored mesh triangles.
from collections import Counter
from pathlib import Path
import struct
import sys
repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tests/fast'))
from test_iphone_dimensional_drawing_contract import read_glb, accessor_vec3
from mathutils import Vector

def signature(points):
    return tuple(sorted(tuple(round(v, 7) for v in p) for p in points))

doc, blob = read_glb(repo / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb')
for name in names:
    mesh = bpy.data.objects[name].data
    mesh.calc_loop_triangles()
    expected = Counter(signature((mesh.vertices[i].co.x, mesh.vertices[i].co.z, -mesh.vertices[i].co.y)
                                 for i in t.vertices) for t in mesh.loop_triangles)
    node = next(n for n in doc['nodes'] if n.get('name') == name)
    actual = Counter()
    for p in doc['meshes'][node['mesh']]['primitives']:
        positions = accessor_vec3(doc, blob, p['attributes']['POSITION'])
        a = doc['accessors'][p['indices']]
        v = doc['bufferViews'][a['bufferView']]
        code = {5121: 'B', 5123: 'H', 5125: 'I'}[a['componentType']]
        size = struct.calcsize('<' + code)
        offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        indices = [struct.unpack_from('<' + code, blob, offset + i * size)[0] for i in range(a['count'])]
        for i in range(0, len(indices), 3):
            points = [Vector(positions[j]) for j in indices[i:i+3]]
            assert (points[1] - points[0]).cross(points[2] - points[0]).length > 2e-16, (name, 'exported degenerate triangle')
            actual[signature(points)] += 1
    assert expected == actual, (name, 'authored/exported front triangles differ')
print('IPHONE_FRONT_EXPORTED_TRIANGLES_GREEN', names)
