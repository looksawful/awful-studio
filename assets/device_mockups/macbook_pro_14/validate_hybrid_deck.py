"""Runtime gate for the hybrid deck master -> derived runtime seam."""
import bpy
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geometry_contract import derive_metric_measurements

G1 = derive_metric_measurements()
speaker_spec = G1['speaker']
expected_apertures = speaker_spec['grid_rows'] * speaker_spec['grid_columns'] * 2

master = bpy.data.objects['BASE_UNIBODY']
runtime = bpy.data.objects['BASE_UNIBODY_RUNTIME_SOURCE']
assert master.get('speaker_apertures') == expected_apertures, 'master lost physical speaker apertures'
assert runtime.get('runtime_variant') == 'clean_body_plus_speaker_proxy'
assert runtime.hide_render, 'runtime source must stay hidden in master evidence renders'
assert len(runtime.data.vertices) < len(master.data.vertices), 'runtime base still carries master speaker-hole topology'

trackpad = bpy.data.objects['TRACKPAD']
assert trackpad.get('surface_family') == 'glass_trackpad'
assert trackpad.get('profile_rings', 0) >= 6
assert any(mod.type == 'WEIGHTED_NORMAL' for mod in trackpad.modifiers), 'trackpad lost weighted-normal surface treatment'
z_values = [vertex.co.z for vertex in trackpad.data.vertices]
assert (max(z_values)-min(z_values))*1000 >= .18, 'trackpad is still a flat thin proxy'

expected_families = {
    'KEY_03_01': 'regular',
    'KEY_00_00': 'modifier',
    'KEY_00_04': 'space',
    'KEY_ARROW_0': 'arrow',
}
for name, family in expected_families.items():
    key = bpy.data.objects[name]
    assert key.get('key_family') == family, f'{name}: expected {family}, got {key.get("key_family")}'
    assert key.get('surface_family') == 'sculpted_keycap'
    assert any(mod.type == 'WEIGHTED_NORMAL' for mod in key.modifiers), f'{name}: no weighted normals'
    top_z = max(vertex.co.z for vertex in key.data.vertices)
    interior = [
        vertex.co.z for vertex in key.data.vertices
        if abs(vertex.co.x) <= key.dimensions.x * .18
        and abs(vertex.co.y) <= key.dimensions.y * .18
    ]
    assert interior, f'{name}: no interior top geometry for a real dish'
    dish_depth_mm = (top_z - min(interior)) * 1000.0
    assert dish_depth_mm >= .06, f'{name}: keycap dish too shallow ({dish_depth_mm:.3f} mm)'

for name in ('SPEAKER_RUNTIME_PROXY_L', 'SPEAKER_RUNTIME_PROXY_R'):
    proxy = bpy.data.objects[name]
    assert proxy.hide_render, f'{name}: runtime proxy must stay hidden in master renders'
    assert proxy.get('runtime_role') == 'speaker_proxy'
    assert proxy.get('speaker_rows') == speaker_spec['grid_rows']
    assert proxy.get('speaker_columns') == speaker_spec['grid_columns']

speaker = bpy.data.materials['MAT_SPEAKER_PROXY']
nodes = speaker.node_tree.nodes
rgba = nodes['SPEAKER_PROXY_RGBA'].image
normal = nodes['SPEAKER_PROXY_NORMAL'].image
assert rgba.packed_file and normal.packed_file, 'speaker proxy maps must be packed into the authoritative master'
assert tuple(rgba.size) == (128, 1024) and tuple(normal.size) == (128, 1024)
assert nodes.get('Normal Map') or any(node.bl_idname == 'ShaderNodeNormalMap' for node in nodes)

def roughness(name):
    return bpy.data.materials[name].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value

assert roughness('MAT_KEYCAP') >= .72
assert roughness('MAT_KEYBOARD_WELL') >= .62
assert roughness('MAT_PORT_DARK') >= .50
track_bsdf = bpy.data.materials['MAT_TRACKPAD'].node_tree.nodes['Principled BSDF']
assert track_bsdf.inputs['Metallic'].default_value <= .10
assert .18 <= track_bsdf.inputs['Roughness'].default_value <= .35

print(
    'MACBOOK_HYBRID_DECK_PASS',
    bpy.app.version_string,
    'master_vertices', len(master.data.vertices),
    'runtime_vertices', len(runtime.data.vertices),
    'trackpad_vertices', len(trackpad.data.vertices),
)
