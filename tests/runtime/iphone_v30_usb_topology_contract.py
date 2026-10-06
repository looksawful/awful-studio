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
for name in names:
    mesh = bpy.data.objects[name].data; mesh.calc_loop_triangles()
    expected = Counter(signature((mesh.vertices[i].co.x, mesh.vertices[i].co.z, -mesh.vertices[i].co.y)
                                 for i in t.vertices) for t in mesh.loop_triangles)
    node = next(n for n in doc['nodes'] if n.get('name') == name); actual = Counter()
    for p in doc['meshes'][node['mesh']]['primitives']:
        positions = accessor_vec3(doc, blob, p['attributes']['POSITION'])
        a = doc['accessors'][p['indices']]; v = doc['bufferViews'][a['bufferView']]
        code = {5121:'B',5123:'H',5125:'I'}[a['componentType']]
        size = struct.calcsize('<'+code); offset = v.get('byteOffset',0)+a.get('byteOffset',0)
        indices = [struct.unpack_from('<'+code,blob,offset+i*size)[0] for i in range(a['count'])]
        for i in range(0,len(indices),3):
            actual[signature(positions[j] for j in indices[i:i+3])] += 1
    assert expected == actual, (name, 'authored/exported USB physical triangles differ')
print('IPHONE_USB_EXPORTED_TRIANGLES_GREEN', names)
