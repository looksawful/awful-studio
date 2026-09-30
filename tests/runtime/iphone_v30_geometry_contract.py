"""Run in Blender 5.2 with the canonical generated v30 blend loaded."""
import json
import bmesh
import bpy

results = {}
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_HOUSING', 'CAMERA_HOUSING_SEAT', 'DYNAMIC_ISLAND'):
    obj = bpy.data.objects[name].evaluated_get(depsgraph)
    mesh = obj.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    volume = bm.calc_volume(signed=True)
    non_manifold = sum(not edge.is_manifold for edge in bm.edges)
    results[name] = {'signed_volume': volume, 'non_manifold_edges': non_manifold}
    bm.free()
    obj.to_mesh_clear()
    assert volume > 0, f'{name}: inward shell'
    assert non_manifold == 0, f'{name}: non-manifold evaluated geometry'
flash = bpy.data.objects['FLASH']
material = flash.data.materials[0]
bsdf = material.node_tree.nodes.get('Principled BSDF')
assert bsdf.inputs['Base Color'].is_linked, 'flash texture missing'
assert flash.data.uv_layers.active, 'flash UV missing'
screen_material = bpy.data.objects['SCREEN_CONTENT'].data.materials[0]
screen_image = next(n.image for n in screen_material.node_tree.nodes if n.type == 'TEX_IMAGE')
assert 'clean_1206x2622' in screen_image.name, 'baked island reference is still used'
print('IPHONE_V30_GEOMETRY_GREEN', json.dumps({'blender': bpy.app.version_string, 'shells': results}))
