import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(HERE, 'runtime', 'v1')
os.makedirs(RUNTIME, exist_ok=True)


def cli(flag, default=None):
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default


SOURCE_REVISION = cli('--source-revision', '')
SOURCE_COMMIT = cli('--source-commit', '')
PLUGIN_SOURCE_REVISION = cli('--plugin-source-revision', '')
if len(SOURCE_REVISION) != 64 or len(PLUGIN_SOURCE_REVISION) != 64:
    raise RuntimeError('source revisions must be SHA-256 fingerprints')

root = bpy.data.objects.get('CTRL_MACBOOK_PRO_14')
hinge = bpy.data.objects.get('CTRL_HINGE')
if root is None or hinge is None:
    raise RuntimeError('MacBook root or hinge control missing')

for cname in ('_STUDIO_RIG', '_DIAGNOSTIC_CAMERAS'):
    col = bpy.data.collections.get(cname)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

for obj in [root] + list(root.children_recursive):
    if obj.type == 'MESH':
        obj.data.name = obj.name

roles = {
    'BASE_UNIBODY': 'body', 'LID_UNIBODY': 'lid',
    'SCREEN_CONTENT': 'screen', 'SCREEN_GLASS': 'screen_glass',
    'FACETIME_CAMERA': 'front_camera_optic', 'TRACKPAD': 'trackpad',
    'TOUCH_ID': 'control', 'MAGSAFE': 'port', 'TB_LEFT_1': 'port',
    'TB_LEFT_2': 'port', 'TB_RIGHT': 'port', 'HEADPHONE': 'port',
    'HDMI': 'port', 'SDXC': 'port', 'APPLE_LOGO_RELEASE': 'branding',
}
for name, role in roles.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj['runtime_role'] = role
        obj['interactable'] = role in {'screen', 'trackpad', 'control'}


def anchor(name, location, parent):
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if not obj.users_collection:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = 0.01
    return obj

screen = bpy.data.objects.get('SCREEN_CONTENT')
anchor('ANCHOR_CENTER', (0.0, 0.0, 0.0), root)
anchor('ANCHOR_BOTTOM_CENTER', (0.0, 0.0, 0.0), root)
anchor('ANCHOR_SCREEN_CENTER', tuple(screen.location) if screen else (0.0, 0.0, 0.106), hinge)
root['runtime_format'] = 'glTF 2.0 / GLB'
root['runtime_units'] = 'meters'
root['source_up_axis'] = '+Z'
root['source_forward_axis'] = '-Y'
root['runtime_up_axis'] = '+Y'
root['runtime_forward_axis'] = '+Z'
root['runtime_pivot'] = 'ANCHOR_CENTER'
root['runtime_bottom_anchor'] = 'ANCHOR_BOTTOM_CENTER'
root['runtime_screen_anchor'] = 'ANCHOR_SCREEN_CENTER'
root['runtime_lod'] = 'LOD0'
root['delivery_version'] = 'v1'
root['delivery_stage'] = 'RELEASE_CANDIDATE'
root['delivery_source_revision'] = SOURCE_REVISION
root['delivery_source_commit'] = SOURCE_COMMIT
root['plugin_source_revision'] = PLUGIN_SOURCE_REVISION
root['hinge_control'] = 'CTRL_HINGE'

for obj in bpy.context.selected_objects:
    obj.select_set(False)
exported = []
for obj in [root] + list(root.children_recursive):
    if obj.type in {'MESH', 'EMPTY'} and not obj.hide_render and obj.name != 'SCREEN_GLASS':
        obj.select_set(True)
        exported.append(obj.name)
bpy.context.view_layer.objects.active = root

prefix = 'macbook_pro_14_m5_v1'
glb = os.path.join(RUNTIME, prefix + '_web.glb')
bpy.ops.export_scene.gltf(
    filepath=glb,
    export_format='GLB',
    use_selection=True,
    export_extras=True,
    export_animations=True,
    export_animation_mode='ACTIONS',
)
bpy.ops.file.pack_all()
delivery = os.path.join(RUNTIME, prefix + '_delivery.blend')
bpy.ops.wm.save_as_mainfile(filepath=delivery)

mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name in exported]
materials = sorted({m.name for o in mesh_objs for m in o.data.materials if m})
points = []
for obj in mesh_objs:
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        points.append((world.x, world.z, -world.y))
runtime_min = [min(p[i] for p in points) for i in range(3)]
runtime_max = [max(p[i] for p in points) for i in range(3)]
runtime_size_mm = [round((runtime_max[i] - runtime_min[i]) * 1000.0, 3) for i in range(3)]

manifest = {
    'asset_id': 'macbook_pro_14_m5',
    'version': 'v1',
    'stage': 'RELEASE_CANDIDATE',
    'source_blend': 'extension/awful_studio/assets/devices/macbook_pro_14_m5_low_v1_release.blend',
    'delivery_blend': 'runtime/v1/macbook_pro_14_m5_v1_delivery.blend',
    'glb': 'runtime/v1/macbook_pro_14_m5_v1_web.glb',
    'body_dimensions_mm': [312.6, 221.2, 15.5],
    'dimension_order': ['width_x', 'depth_y', 'closed_height_z'],
    'runtime_bounds_mm': runtime_size_mm,
    'units': 'meters',
    'source_up_axis': '+Z', 'source_forward_axis': '-Y',
    'up_axis': '+Y', 'forward_axis': '+Z',
    'root': 'CTRL_MACBOOK_PRO_14',
    'hinge_control': 'CTRL_HINGE',
    'animations': ['lid_open', 'lid_close'],
    'screen_states': {
        'screen_off': {'emission_strength': 0.0, 'glow_energy': 0.0},
        'screen_on': {'emission_strength': 0.65, 'glow_energy': 8.0},
    },
    'screen_glow': {'anchor': 'SCREEN_GLOW_ANCHOR', 'type': 'rect_area', 'width_mm': 301.66, 'height_mm': 195.92, 'source_energy_w': 8.0},
    'screen_object': 'SCREEN_CONTENT',
    'anchors': ['ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER', 'SCREEN_GLOW_ANCHOR'],
    'lods': [{'name': 'LOD0', 'file': 'macbook_pro_14_m5_v1_web.glb'}],
    'materials': materials,
    'exported_objects': exported,
    'runtime_roles': roles,
    'threejs_loader': 'GLTFLoader',
    'requires_meshopt_decoder': False,
    'web_variants': {'compat': {'file': 'macbook_pro_14_m5_v1_web.glb', 'requires': []}},
    'camera_fit': 'runtime_bounds',
    'source_revision': SOURCE_REVISION,
    'source_commit': SOURCE_COMMIT,
    'plugin_source_revision': PLUGIN_SOURCE_REVISION,
    'generator_version': 'macbook_v1_packaged_blend_web_delivery',
    'delivery_profile': {
        'simplification': 'none',
        'compression': 'compat+meshopt',
        'node_preservation': 'required',
        'hinge_control': 'preserved',
    },
}
manifest_path = os.path.join(RUNTIME, prefix + '.asset.json')
with open(manifest_path, 'w', encoding='utf-8', newline='\n') as handle:
    json.dump(manifest, handle, indent=2)
    handle.write('\n')
print('AWFUL_MACBOOK_V1_RUNTIME_EXPORT', json.dumps({
    'glb': glb,
    'delivery': delivery,
    'objects': len(exported),
    'materials': len(materials),
    'glb_bytes': os.path.getsize(glb),
    'manifest': manifest_path,
}, sort_keys=True))
