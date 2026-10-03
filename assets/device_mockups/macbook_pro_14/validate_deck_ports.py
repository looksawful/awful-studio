"""Runtime checks for the ANSI deck and recessed chassis openings."""
import json
import bpy
import bmesh
import os,sys
from mathutils import Vector
sys.path.insert(0,os.path.dirname(__file__))
from port_layout import PORTS
from geometry_contract import derive_metric_measurements

for name in ('TB_LEFT_1','TB_LEFT_2','TB_RIGHT'):
    contacts=[o for o in bpy.data.objects if o.name.startswith(name+'_CONTACT_')]
    assert len(contacts)==24, f'{name}: missing two twelve-contact rows'
    tongue=bpy.data.objects[name+'_TONGUE']
    bounds=[tongue.matrix_world@Vector(p) for p in tongue.bound_box]
    z_min,z_max=min(p.z for p in bounds),max(p.z for p in bounds)
    for row,sign in (('A',1),('B',-1)):
        points=[o.matrix_world.translation for o in contacts if '_CONTACT_'+row in o.name]
        assert len({round(p.y,7) for p in points})==12, 'USB-C contacts overlap within a row'
        assert all(p.z>z_max if sign>0 else p.z<z_min for p in points), 'Contacts are buried in the tongue'
        assert all(.1538<abs(p.x)<.1563 for p in points), 'Contacts are outside the recessed cavity'
assert all(bpy.data.objects[name].location.y>.025 for name in ('MAGSAFE','TB_LEFT_1','TB_LEFT_2','HEADPHONE','HDMI','SDXC','TB_RIGHT')), 'Ports are spread toward the front instead of the rear reference cluster'

ports = {p.name:(p.side,p.y_mm) for p in PORTS}
base = bpy.data.objects['BASE_UNIBODY'].evaluated_get(bpy.context.evaluated_depsgraph_get())
for port in (p for p in PORTS if p.name.startswith('TB_')):
    origin=Vector((port.side*.155,(port.y_mm+port.width_mm/2-.65)/1000,.00415))
    hit,_,_,face=base.ray_cast(base.matrix_world.inverted()@origin,Vector((0,0,1)))
    assert hit and base.data.polygons[face].use_smooth, f'{port.name}: faceted rounded socket wall'
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
speaker = derive_metric_measurements()['speaker']
for suffix, side in (('L', -1), ('R', 1)):
    proxy = bpy.data.objects[f'SPEAKER_MASTER_PROXY_{suffix}']
    assert not proxy.hide_render, f'{suffix} speaker master proxy is hidden'
    assert proxy.get('surface_family') == 'speaker_alpha_normal'
    assert proxy.get('speaker_rows') == speaker['grid_rows']
    assert proxy.get('speaker_columns') == speaker['grid_columns']
    assert abs(proxy.location.x * 1000 - side * speaker['field_center_abs_x_mm']) <= .25
    assert abs(proxy.location.y * 1000 - speaker['field_center_y_mm']) <= .25
    assert abs(proxy.dimensions.x * 1000 - speaker['observed_width_mm']) <= .25
    assert abs(proxy.dimensions.y * 1000 - speaker['observed_height_mm']) <= .25
speaker_material = bpy.data.materials['MAT_SPEAKER_PROXY']
speaker_nodes = speaker_material.node_tree.nodes
assert speaker_nodes['SPEAKER_PROXY_RGBA'].image.packed_file
assert speaker_nodes['SPEAKER_PROXY_NORMAL'].image.packed_file
keys = [obj for obj in bpy.data.objects if obj.name.startswith('KEY_') and obj.type == 'MESH']
assert len(keys) + 1 == 78, f'ANSI deck including Touch ID must have 78 keys, got {len(keys) + 1}'
legends = [obj for obj in bpy.data.objects if obj.name.startswith('LEGEND_')]
assert len(legends) == 76, f'Expected 76 labelled keys (blank Space and Touch ID), got {len(legends)}'
for name in ('LID_UNIBODY', 'BASE_UNIBODY', 'DISPLAY_SURROUND_VISUAL'):
    bm = bmesh.new(); bm.from_mesh(bpy.data.objects[name].data)
    assert bm.calc_volume(signed=True) > 0, f'{name}: inward shell normals'
    bm.free()
print('MACBOOK_DECK_PORTS_PASS', json.dumps({'blender': bpy.app.version_string, 'port_depth_mm': depths, 'key_count': 78}))
