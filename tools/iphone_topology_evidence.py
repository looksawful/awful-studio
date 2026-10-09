"""Fixed-condition v30 topology evidence. Run in Blender on a generated blend.

Arguments after --: --output DIR [--views camera,rail,controls,bottom,front,back].
Does not save changes to the source blend.
"""
import json
import sys
from pathlib import Path

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
output = Path(args[args.index('--output') + 1]).resolve()
output.mkdir(parents=True, exist_ok=True)
views = args[args.index('--views') + 1].split(',') if '--views' in args else ['camera', 'rail', 'controls', 'bottom', 'front', 'back']
cameras = {'camera': 'CAM_CAMERA_MACRO', 'rail': 'CAM_BACK_THREE_QUARTER',
           'controls': 'CAM_RIGHT_SIDE', 'bottom': 'CAM_BOTTOM_MACRO',
           'front': 'CAM_FRONT_SENSOR_MACRO', 'back': 'CAM_BACK'}
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
# Same production material/lighting on both sides of each comparison.
for name, energy in {'KEY_SOFTBOX': 38, 'FILL_SOFTBOX': 7, 'RIM_STRIP': 32, 'TOP_STRIP': 16}.items():
    light = bpy.data.objects.get(name)
    if light:
        light.data.energy = energy
        light.data.use_shadow = name == 'KEY_SOFTBOX'
settings = {'blender': bpy.app.version_string, 'engine': scene.render.engine,
            'size': [1000, 1000], 'look': scene.view_settings.look,
            'exposure': scene.view_settings.exposure, 'shadows': 'KEY_SOFTBOX only', 'cameras': {}}
wire = bpy.data.materials.new('TOPOLOGY_EVIDENCE_WIRE')
wire.use_nodes = True
nodes, links = wire.node_tree.nodes, wire.node_tree.links
bsdf = nodes.get('Principled BSDF')
bsdf.inputs['Roughness'].default_value = .65
wire_node = nodes.new('ShaderNodeWireframe')
wire_node.use_pixel_size = True
wire_node.inputs['Size'].default_value = .7
mix = nodes.new('ShaderNodeMixRGB')
mix.inputs[1].default_value = (.45, .55, .65, 1)
mix.inputs[2].default_value = (.008, .012, .018, 1)
links.new(wire_node.outputs['Fac'], mix.inputs[0])
links.new(mix.outputs[0], bsdf.inputs['Base Color'])
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and o.parent]
original = [(obj, list(obj.data.materials)) for obj in meshes]
for view in views:
    camera = bpy.data.objects[cameras[view]]
    scene.camera = camera
    settings['cameras'][view] = {'matrix': [list(row) for row in camera.matrix_world], 'lens': camera.data.lens}
    scene.render.filepath = str(output / f'{view}-beauty.png')
    bpy.ops.render.render(write_still=True)
    for obj, _ in original:
        obj.data.materials.clear()
        obj.data.materials.append(wire)
    scene.render.filepath = str(output / f'{view}-wire.png')
    bpy.ops.render.render(write_still=True)
    for obj, materials in original:
        obj.data.materials.clear()
        for material in materials:
            obj.data.materials.append(material)
(output / 'conditions.json').write_text(json.dumps(settings, indent=2) + '\n', encoding='utf-8')
