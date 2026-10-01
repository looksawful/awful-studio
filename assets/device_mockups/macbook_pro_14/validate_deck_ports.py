"""Runtime checks for the ANSI deck and recessed chassis openings."""
import json
import bpy
import bmesh
from mathutils import Vector

ports = {'MAGSAFE': (-1, 62), 'TB_LEFT_1': (-1, 27), 'TB_LEFT_2': (-1, -1),
         'HEADPHONE': (-1, -54), 'HDMI': (1, 53), 'SDXC': (1, 18), 'TB_RIGHT': (1, -22)}
base = bpy.data.objects['BASE_UNIBODY'].evaluated_get(bpy.context.evaluated_depsgraph_get())
for name in ('MAT_SPACE_BLACK_ALUMINUM', 'MAT_TRACKPAD'):
    material = bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
    assert max(material.inputs['Base Color'].default_value[:3]) <= .03, f'{name}: Space Black finish is too light'
depths = {}
for name, (side, y) in ports.items():
    origin = Vector((side * 0.160, y / 1000, 0.0083 / 2))
    direction = Vector((-side, 0, 0))
    hit, location, _, _ = base.ray_cast(base.matrix_world.inverted() @ origin, direction)
    assert hit, f'{name}: missing interior chassis wall'
    depth = 156.3 - abs((base.matrix_world @ location).x) * 1000
    depths[name] = round(depth, 4)
    assert depth >= 1.5, f'{name}: opening has no depth ({depth:.3f} mm)'
for side in (-1, 1):
    origin = base.matrix_world.inverted() @ Vector((side * .1463, .002, .02))
    hit, location, _, _ = base.ray_cast(origin, Vector((0, 0, -1)))
    assert hit and .0083 - (base.matrix_world @ location).z >= .0003, 'Speaker perforations must recess into the deck'
keys = [obj for obj in bpy.data.objects if obj.name.startswith('KEY_') and obj.type == 'MESH']
assert len(keys) + 1 == 78, f'ANSI deck including Touch ID must have 78 keys, got {len(keys) + 1}'
legends = [obj for obj in bpy.data.objects if obj.name.startswith('LEGEND_')]
assert len(legends) == 76, f'Expected 76 labelled keys (blank Space and Touch ID), got {len(legends)}'
for name in ('LID_UNIBODY', 'BASE_UNIBODY', 'SCREEN_GLASS'):
    bm = bmesh.new(); bm.from_mesh(bpy.data.objects[name].data)
    assert bm.calc_volume(signed=True) > 0, f'{name}: inward shell normals'
    bm.free()
print('MACBOOK_DECK_PORTS_PASS', json.dumps({'blender': bpy.app.version_string, 'port_depth_mm': depths, 'key_count': 78}))
