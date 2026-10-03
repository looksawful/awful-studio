"""Body topology and preservation seam. Run on the canonical source blend.

--baseline-mode records RED metrics. --baseline PATH tests the frozen surface.
"""
import json
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
obj = bpy.data.objects['BODY_ALUMINUM']
evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
report = {'blender': bpy.app.version_string, 'source_vertices': len(obj.data.vertices),
          'source_faces': len(obj.data.polygons),
          'source_ngons': sum(len(p.vertices) > 4 for p in obj.data.polygons),
          'evaluated_vertices': len(mesh.vertices), 'evaluated_faces': len(mesh.polygons),
          'triangles': len(mesh.loop_triangles), 'ngons': sum(len(f.verts) > 4 for f in bm.faces),
          'nonmanifold_edges': sum(not e.is_manifold for e in bm.edges), 'volume': bm.calc_volume(signed=True)}
if '--baseline' in args:
    baseline_path = str(Path(args[args.index('--baseline') + 1]).resolve())
    with bpy.data.libraries.load(baseline_path, link=False) as (available, loaded):
        loaded.objects = ['BODY_ALUMINUM']
    baseline = loaded.objects[0]
    bpy.context.scene.collection.objects.link(baseline)
    bpy.context.view_layer.update()
    reference_obj = baseline.evaluated_get(bpy.context.evaluated_depsgraph_get())
    reference = reference_obj.to_mesh()
    ref_bm = bmesh.new()
    ref_bm.from_mesh(reference)
    current_tree, reference_tree = BVHTree.FromBMesh(bm), BVHTree.FromBMesh(ref_bm)
    # Samples must lie on triangles: a nonplanar quad's arithmetic center may
    # float off its tessellated surface and is not a valid distance probe.
    def samples(surface):
        return [v.co for v in surface.verts] + [
            (triangle[0].vert.co + triangle[1].vert.co + triangle[2].vert.co) / 3
            for triangle in surface.calc_loop_triangles()]
    probes = [(tree.find_nearest(p), p) for tree, points in (
        (reference_tree, samples(bm)), (current_tree, samples(ref_bm))) for p in points]
    distance = max(hit[3] for hit, _ in probes)
    normal_distance = max(abs((point - hit[0]).dot(hit[1])) for hit, point in probes)
    report['surface_max_distance_mm'] = distance * 1000
    report['surface_max_normal_displacement_mm'] = normal_distance * 1000
    report['volume_delta'] = report['volume'] - ref_bm.calc_volume(signed=True)
    source_vertices = {tuple(v.co) for v in obj.data.vertices}
    baseline_vertices = {tuple(v.co) for v in baseline.data.vertices}
    report['source_boundary_vertices_unchanged'] = source_vertices == baseline_vertices
    def edge_coordinates(data):
        return {tuple(sorted(tuple(data.vertices[i].co) for i in edge.vertices)) for edge in data.edges}
    report['original_edges_preserved'] = edge_coordinates(baseline.data) <= edge_coordinates(obj.data)
    ref_bm.free()
    reference_obj.to_mesh_clear()
    assert report['source_boundary_vertices_unchanged'], report
    assert report['original_edges_preserved'], report
    # Closest-point distance includes tangential gaps in the old large n-gon's
    # tessellation. Preserve actual depth and every original physical boundary;
    # evaluated tolerance is half the existing 0.01 mm body envelope tolerance.
    # The source datums and boundary edges above are checked with exact equality.
    assert normal_distance < 5e-6, report
    assert abs(report['volume_delta']) < 1e-11, report
if '--report' in args:
    path = Path(args[args.index('--report') + 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
bm.free()
evaluated.to_mesh_clear()
if '--baseline-mode' not in args:
    assert report['source_ngons'] == report['ngons'] == 0, report
    assert report['nonmanifold_edges'] == 0 and report['volume'] > 0, report
    print('IPHONE_BODY_TOPOLOGY_GREEN', json.dumps(report))
else:
    print('IPHONE_BODY_BASELINE', json.dumps(report))
