"""Saved antenna geometry must carry its physical bevel into the web delivery."""
import bpy
import bmesh
import json

report = {}
for side in ('L', 'R'):
    for z in (55, -55):
        name = f'ANTENNA_SIDE_{side}_{z}'
        obj = bpy.data.objects[name]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        row = {'verts': len(bm.verts), 'faces': len(bm.faces),
               'ngons': sum(len(f.verts) > 4 for f in bm.faces),
               'nonmanifold': sum(not e.is_manifold for e in bm.edges),
               'zero_edges': sum(e.calc_length() < 1e-12 for e in bm.edges),
               'degenerate_faces': sum(f.calc_area() < 1e-16 for f in bm.faces),
               'modifiers': [m.type for m in obj.modifiers]}
        bm.free()
        report[name] = row
        assert not row['modifiers'], (name, 'physical antenna bevel must be saved geometry', row)
        assert not any(row[k] for k in ('ngons', 'nonmanifold', 'zero_edges', 'degenerate_faces')), report
        # The physical corner must be rounded in the saved mesh, rather than a sharp box.
        half = (0.00005, 0.00051, 0.00215)
        for vertex in obj.data.vertices:
            inset = [half[a] - abs(vertex.co[a]) for a in range(3)]
            assert sum(v < 1e-8 for v in inset) < 3, (name, 'sharp box corner', tuple(vertex.co))
        assert len(obj.data.uv_layers) == 1, name
        assert [m.name for m in obj.data.materials] == ['MAT_OPTICS_BLACK'], name
        assert abs(obj.location.z - z * .001) < 1e-8, (name, obj.location)
        assert abs(abs(obj.location.x) - .035707) < 1e-8, (name, obj.location)
        assert obj.parent.name == 'CTRL_IPHONE_17', name
print('IPHONE_ANTENNA_TOPOLOGY_GREEN', json.dumps(report, sort_keys=True))

# Match the complete actual saved triangle set to compat GLB, including local axis conversion.
from collections import Counter
from pathlib import Path
import struct
import sys
repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tests/fast'))
from test_iphone_dimensional_drawing_contract import read_glb, accessor_vec3

def signature(points):
    return tuple(sorted(tuple(round(v, 7) for v in p) for p in points))

doc, blob = read_glb(repo / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb')
for name in report:
    mesh = bpy.data.objects[name].data
    mesh.calc_loop_triangles()
    expected = Counter(signature((mesh.vertices[i].co.x, mesh.vertices[i].co.z, -mesh.vertices[i].co.y)
                                 for i in t.vertices) for t in mesh.loop_triangles)
    node = next(n for n in doc['nodes'] if n.get('name') == name)
    actual = Counter()
    for p in doc['meshes'][node['mesh']]['primitives']:
        positions = accessor_vec3(doc, blob, p['attributes']['POSITION'])
        a = doc['accessors'][p['indices']]; v = doc['bufferViews'][a['bufferView']]
        code = {5121:'B',5123:'H',5125:'I'}[a['componentType']]
        size = struct.calcsize('<'+code); offset = v.get('byteOffset',0)+a.get('byteOffset',0)
        indices = [struct.unpack_from('<'+code,blob,offset+i*size)[0] for i in range(a['count'])]
        for i in range(0,len(indices),3):
            actual[signature(positions[j] for j in indices[i:i+3])] += 1
    assert expected == actual, (name, 'saved/exported physical antenna triangles differ', len(expected),len(actual))
print('IPHONE_ANTENNA_EXPORTED_TRIANGLES_GREEN', len(report))
