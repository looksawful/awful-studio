import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(HERE, 'runtime', 'v6')
os.makedirs(RUNTIME, exist_ok=True)
SPECS = {
    '11': {'asset_id': 'ipad_pro_11_m5', 'root': 'CTRL_IPAD_PRO_11', 'w': 177.5, 'h': 249.7, 'd': 5.3, 'sw': 160.13, 'sh': 232.32},
    '13': {'asset_id': 'ipad_pro_13_m5', 'root': 'CTRL_IPAD_PRO_13', 'w': 215.5, 'h': 281.6, 'd': 5.1, 'sw': 199.14, 'sh': 265.19},
}


def cli(flag, default=None):
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default


SIZE = cli('--size', '')
SOURCE_REVISION = cli('--source-revision', '')
SOURCE_COMMIT = cli('--source-commit', '')
PLUGIN_SOURCE_REVISION = cli('--plugin-source-revision', '')
if SIZE not in SPECS:
    raise RuntimeError('--size must be 11 or 13')
if len(SOURCE_REVISION) != 64 or len(PLUGIN_SOURCE_REVISION) != 64:
    raise RuntimeError('source revisions must be SHA-256 fingerprints')
spec = SPECS[SIZE]
root = bpy.data.objects.get(spec['root'])
if root is None:
    raise RuntimeError(f"{spec['root']} missing")
for cname in ('_STUDIO_RIG', '_DIAGNOSTIC_CAMERAS'):
    col = bpy.data.collections.get(cname)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

logo_path = os.path.join(HERE, 'reference', 'apple_logo_alpha.png')
logo_mat = bpy.data.materials.get('MAT_APPLE_LOGO_DECAL')
if logo_mat and logo_mat.use_nodes:
    for node in logo_mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            node.image = bpy.data.images.load(logo_path, check_existing=True)
            break

for obj in [root] + list(root.children_recursive):
    if obj.type == 'MESH':
        obj.data.name = obj.name

roles = {
    'BODY_ALUMINUM': 'body', 'SCREEN_CONTENT': 'screen', 'SCREEN_GLASS': 'screen_glass',
    'FRONT_CAMERA_GLASS': 'front_camera_optic', 'TOP_BUTTON': 'control',
    'VOL_UP': 'control', 'VOL_DOWN': 'control', 'USB_C_CAVITY': 'port',
    'CAMERA_HOUSING': 'camera_housing', 'REAR_CAMERA_GLASS': 'camera_optic',
    'LIDAR': 'depth_sensor', 'APPLE_LOGO_DECAL': 'branding',
}
for name, role in roles.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj['runtime_role'] = role
        obj['interactable'] = role in {'screen', 'control'}


def anchor(name, location):
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if not obj.users_collection:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.location = location
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = 0.008
    return obj

camera_housing = bpy.data.objects.get('CAMERA_HOUSING')
camera_location = tuple(camera_housing.location) if camera_housing else (0.0, spec['d'] / 2000.0, spec['h'] / 3000.0)
anchor('ANCHOR_CENTER', (0.0, 0.0, 0.0))
anchor('ANCHOR_BOTTOM_CENTER', (0.0, 0.0, -spec['h'] / 2000.0))
anchor('ANCHOR_SCREEN_CENTER', (0.0, -spec['d'] / 2000.0, 0.0))
anchor('ANCHOR_REAR_CAMERA', camera_location)
anchor('SCREEN_GLOW_ANCHOR', (0.0, -spec['d'] / 2000.0 - 0.001, 0.0))

root['runtime_format'] = 'glTF 2.0 / GLB'
root['runtime_units'] = 'meters'
root['source_up_axis'] = '+Z'
root['source_forward_axis'] = '-Y'
root['runtime_up_axis'] = '+Y'
root['runtime_forward_axis'] = '+Z'
root['runtime_pivot'] = 'ANCHOR_CENTER'
root['runtime_bottom_anchor'] = 'ANCHOR_BOTTOM_CENTER'
root['runtime_screen_anchor'] = 'ANCHOR_SCREEN_CENTER'
root['runtime_camera_anchor'] = 'ANCHOR_REAR_CAMERA'
root['runtime_lod'] = 'LOD0'
root['delivery_version'] = 'v6'
root['delivery_stage'] = 'LOW_DRAFT'
root['delivery_source_revision'] = SOURCE_REVISION
root['delivery_source_commit'] = SOURCE_COMMIT
root['plugin_source_revision'] = PLUGIN_SOURCE_REVISION

for obj in bpy.context.selected_objects:
    obj.select_set(False)
exported = []
for obj in [root] + list(root.children_recursive):
    if obj.type in {'MESH', 'EMPTY'} and not obj.hide_render and obj.name != 'SCREEN_GLASS':
        obj.select_set(True)
        exported.append(obj.name)
bpy.context.view_layer.objects.active = root

prefix = f"{spec['asset_id']}_v6"
glb = os.path.join(RUNTIME, prefix + '_web.glb')
bpy.ops.export_scene.gltf(
    filepath=glb,
    export_format='GLB',
    use_selection=True,
    export_extras=True,
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
    'asset_id': spec['asset_id'],
    'version': 'v6',
    'stage': 'LOW_DRAFT',
    'source_blend': f"generated/{spec['asset_id']}_low_v6.blend",
    'delivery_blend': f"runtime/v6/{prefix}_delivery.blend",
    'glb': f"runtime/v6/{prefix}_web.glb",
    'body_dimensions_mm': [spec['w'], spec['h'], spec['d']],
    'dimension_order': ['width_x', 'height_y', 'depth_z'],
    'runtime_bounds_mm': runtime_size_mm,
    'units': 'meters',
    'source_up_axis': '+Z', 'source_forward_axis': '-Y',
    'up_axis': '+Y', 'forward_axis': '+Z',
    'root': spec['root'],
    'screen_object': 'SCREEN_CONTENT',
    'anchors': ['ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER', 'ANCHOR_REAR_CAMERA', 'SCREEN_GLOW_ANCHOR'],
    'dimensional_drawing_url': f"https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-{SIZE}-inch-m5.pdf",
    'screen_states': {
        'screen_off': {'emission_strength': 0.0, 'glow_intensity': 0.0},
        'screen_on': {'emission_strength': 0.85, 'glow_intensity': 1.0},
    },
    'screen_glow': {'anchor': 'SCREEN_GLOW_ANCHOR', 'type': 'rect_area', 'width_mm': spec['sw'], 'height_mm': spec['sh'], 'source_energy_w': 8.0},
    'lods': [{'name': 'LOD0', 'file': prefix + '_web.glb'}],
    'materials': materials,
    'exported_objects': exported,
    'runtime_roles': roles,
    'threejs_loader': 'GLTFLoader',
    'requires_meshopt_decoder': False,
    'web_variants': {'compat': {'file': prefix + '_web.glb', 'requires': []}},
    'camera_fit': 'runtime_bounds',
    'source_revision': SOURCE_REVISION,
    'source_commit': SOURCE_COMMIT,
    'plugin_source_revision': PLUGIN_SOURCE_REVISION,
    'generator_version': 'ipad_v6_packaged_blend_web_delivery',
    'delivery_profile': {'simplification': 'none', 'compression': 'compat+meshopt', 'node_preservation': 'required'},
}
manifest_path = os.path.join(RUNTIME, prefix + '.asset.json')
with open(manifest_path, 'w', encoding='utf-8', newline='\n') as handle:
    json.dump(manifest, handle, indent=2)
    handle.write('\n')

print('AWFUL_IPAD_V6_RUNTIME_EXPORT', json.dumps({
    'size': SIZE,
    'asset_id': spec['asset_id'],
    'glb': glb,
    'delivery': delivery,
    'objects': len(exported),
    'materials': len(materials),
    'glb_bytes': os.path.getsize(glb),
    'manifest': manifest_path,
}, sort_keys=True))
