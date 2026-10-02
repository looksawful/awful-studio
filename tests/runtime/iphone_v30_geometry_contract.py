"""Run in Blender 5.2 with the canonical generated v30 blend loaded."""
import json
import bmesh
import bpy
from mathutils import Vector

results = {}
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ('BODY_ALUMINUM', 'BACK_GLASS', 'CAMERA_HOUSING', 'CAMERA_HOUSING_SEAT', 'FRONT_SENSOR_MASK', 'FRONT_CAMERA_MASK'):
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
assert 'clean_1206x2622' in screen_image.name, 'default screen must use clean app artwork without baked Dynamic Island'
assert 'dynamic_state_1206x2622' not in screen_image.name, 'system Dynamic Island must not be baked into SCREEN_CONTENT'

# Backings must be below the opening; specular caps cannot stand in for cavities.
for name in [obj.name for obj in bpy.data.objects if 'APERTURE_' in obj.name and not obj.name.endswith('_CUTTER')]:
    obj = bpy.data.objects[name]
    normal = (obj.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    projection = 0.14961 / 2
    if abs(normal.x) > 0.001:
        center = Vector(((1 if normal.x > 0 else -1) * (0.07145 / 2 - 0.0136), 0, -0.14961 / 2 + 0.0136))
        projection = center.dot(normal) + 0.0136
    opening = obj.location + normal * (projection - obj.location.dot(normal))
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    depth = min((opening - point).dot(normal) for point in points)
    assert depth > 0.00070, f'{name}: backing only {depth * 1000:.3f}mm below opening'
    mat = obj.data.materials[0]
    shader = mat.node_tree.nodes.get('Principled BSDF')
    assert shader.inputs['Roughness'].default_value >= 0.6, f'{name}: glossy backing'
    assert shader.inputs['Normal'].is_linked, f'{name}: grille micro-normal missing'
    image = next(node.image for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE')
    assert image.packed_file and image.colorspace_settings.name == 'Non-Color', 'normal image is not portable'
print('IPHONE_V30_GEOMETRY_GREEN', json.dumps({'blender': bpy.app.version_string, 'shells': results}))
