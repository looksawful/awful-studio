"""Blender seam: run on a generated/reopened canonical blend, -- --report PATH.

Report mode records the baseline without applying acceptance assertions.
"""
import json
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Quaternion, Vector

CAMERA = ('CAMERA_HOUSING_SEAT', 'CAMERA_HOUSING') + tuple(
    f'CAMERA_{index}_{part}' for index in (1, 2) for part in ('RING', 'BEVEL', 'GLASS'))
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
report_path = Path(args[args.index('--report') + 1]) if '--report' in args else None
report = {'blender': bpy.app.version_string, 'meshes': {}}
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in CAMERA:
    obj = bpy.data.objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    report['meshes'][name] = {
        'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
        'triangles': len(mesh.loop_triangles),
        'ngons': sum(len(face.verts) > 4 for face in bm.faces),
        'nonmanifold_edges': sum(not edge.is_manifold for edge in bm.edges),
        'signed_volume': bm.calc_volume(signed=True),
        'source_ngons': sum(len(p.vertices) > 4 for p in obj.data.polygons),
    }
    bm.free()
    evaluated.to_mesh_clear()
if report_path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
if '--baseline' not in args:
    for name, metrics in report['meshes'].items():
        assert metrics['source_ngons'] == metrics['ngons'] == 0, (name, metrics)
        assert metrics['nonmanifold_edges'] == 0, (name, metrics)
        assert metrics['signed_volume'] > 0, (name, metrics)
        if name != 'CAMERA_HOUSING':
            assert metrics['triangles'] == (164 if 'HOUSING' in name else 160), (name, metrics)
        else:
            # The independently tested physical microphone opening changes this cap.
            # Its topology and authored/export coverage belong to the rear contract.
            assert metrics['triangles'] == 2 * metrics['vertices'] - 4, (name, metrics)
        obj = bpy.data.objects[name]
        if name == 'CAMERA_HOUSING_SEAT':
            # Accepted caps span horizontal rows; no pole in the lens junction.
            assert not any(abs(v.co.x) < 1e-8 and abs(v.co.z) < 1e-8 for v in obj.data.vertices), name
            assert sum(len(p.vertices) == 4 and abs(p.normal.y) > .99 for p in obj.data.polygons) == 38, name
        for material in obj.data.materials:
            shader = material.node_tree.nodes.get('Principled BSDF')
            if name == 'CAMERA_HOUSING' and material.name == 'MAT_OPTICS_BLACK':
                # Newly authored cavity walls use the existing unmapped mic material.
                assert not shader.inputs['Normal'].is_linked, name
            else:
                assert shader.inputs['Normal'].is_linked == (not name.endswith('GLASS')), name
        assert obj.data.uv_layers.active, name
    if '--glb' in args:
        raw = Path(args[args.index('--glb') + 1]).read_bytes()
        json_length = struct.unpack_from('<I', raw, 12)[0]
        doc = json.loads(raw[20:20 + json_length])
        blob = raw[28 + json_length:]
        nodes = {node['name']: node for node in doc['nodes']}
        for name in CAMERA:
            obj = bpy.data.objects[name]
            source = [obj.matrix_world @ v.co for v in obj.data.vertices]
            node = nodes[name]
            rotation = node.get('rotation', [0, 0, 0, 1])
            q = Quaternion((rotation[3], *rotation[:3]))
            translation = Vector(node.get('translation', [0, 0, 0]))
            scale = node.get('scale', [1, 1, 1])
            exported = []
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                accessor = doc['accessors'][primitive['attributes']['POSITION']]
                view = doc['bufferViews'][accessor['bufferView']]
                offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                for i in range(accessor['count']):
                    xyz = struct.unpack_from('<fff', blob, offset + i * view.get('byteStride', 12))
                    point = q @ Vector(tuple(xyz[j] * scale[j] for j in range(3))) + translation
                    exported.append(Vector((point.x, -point.z, point.y)))
            assert max(min((p - v).length for v in source) for p in exported) < 1e-7, name
            assert max(min((p - v).length for p in exported) for v in source) < 1e-7, name
        report['export_equivalence'] = 'PASS (bidirectional world vertex distance < 0.0001 mm)'
    print('IPHONE_V30_TOPOLOGY_GREEN', json.dumps(report))
else:
    print('IPHONE_V30_TOPOLOGY_BASELINE', json.dumps(report))
