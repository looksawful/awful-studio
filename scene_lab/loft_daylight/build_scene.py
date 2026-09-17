from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import (
    area_light, box, camera, clear_scene, collection, configure_scene,
    concrete_material, cylinder, empty, material_principled, move_to_collection,
    save_blend,
)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(HERE / 'generated' / 'loft_daylight_v2.blend'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def leather_material():
    mat = bpy.data.materials.new('MAT_Charcoal_Leather')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 430.0
    noise.inputs['Detail'].default_value = 2.0
    noise.inputs['Roughness'].default_value = 0.72
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.00055
    bsdf.inputs['Base Color'].default_value = (0.014, 0.016, 0.019, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.31
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def walnut_material():
    mat = bpy.data.materials.new('MAT_Walnut')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.65
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 7.5
    wave.inputs['Distortion'].default_value = 7.0
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.55
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.035, 0.012, 0.005, 1.0)
    ramp.color_ramp.elements[1].color = (0.26, 0.075, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.34
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs[1])
    links.new(wave.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def add_back_window(arch, steel, glass, concrete):
    y = 5.72
    left, right = -5.55, -0.45
    bottom, top = 0.55, 5.10
    cx = (left + right) * 0.5
    width = right - left
    height = top - bottom
    frame = 0.085
    depth = 0.18

    box('ARCH_Back_RightWall', ((right + 5.85) * 0.5, 5.85, 2.8), (5.85 - right, 0.30, 5.6), arch, concrete)
    box('ARCH_Back_LeftPier', ((-5.85 + left) * 0.5, 5.85, 2.8), (left + 5.85, 0.30, 5.6), arch, concrete)
    box('ARCH_Back_WindowBottom', (cx, 5.85, bottom * 0.5), (width, 0.30, bottom), arch, concrete)
    box('ARCH_Back_WindowTop', (cx, 5.85, top + (5.6 - top) * 0.5), (width, 0.30, 5.6 - top), arch, concrete)

    glass_obj = box('ARCH_Window_Glass', (cx, y, (bottom + top) * 0.5), (width - frame * 2, 0.018, height - frame * 2), arch, glass)
    glass_obj.visible_shadow = False
    for x in (left, right):
        box('ARCH_Window_Jamb', (x, y - 0.03, (bottom + top) * 0.5), (frame, depth, height), arch, steel, 0.008)
    for z in (bottom, top):
        box('ARCH_Window_Rail', (cx, y - 0.03, z), (width, depth, frame), arch, steel, 0.008)
    for i in range(1, 4):
        x = left + width * i / 4
        box(f'ARCH_Window_Mullion_V{i}', (x, y - 0.03, (bottom + top) * 0.5), (frame * 0.70, depth, height - frame * 2), arch, steel, 0.006)
    for i in range(1, 3):
        z = bottom + height * i / 3
        box(f'ARCH_Window_Mullion_H{i}', (cx, y - 0.03, z), (width - frame * 2, depth, frame * 0.70), arch, steel, 0.006)


def rounded_box(name, location, dimensions, props, material, bevel):
    obj = box(name, location, dimensions, props, material, bevel)
    return obj


def add_sofa(props, leather, steel):
    x, y = -3.72, 3.56
    rounded_box('PROP_Sofa_Frame', (x, y, 0.47), (2.72, 1.02, 0.28), props, leather, 0.13)
    for dx in (-0.60, 0.60):
        rounded_box('PROP_Sofa_Seat', (x + dx, y - 0.07, 0.72), (1.12, 0.82, 0.20), props, leather, 0.10)
        back = rounded_box('PROP_Sofa_Back', (x + dx, y + 0.30, 1.24), (1.12, 0.24, 0.95), props, leather, 0.10)
        back.rotation_euler.x = math.radians(-6.0)
    rounded_box('PROP_Sofa_Arm_L', (x - 1.29, y, 0.88), (0.18, 0.98, 0.72), props, leather, 0.09)
    rounded_box('PROP_Sofa_Arm_R', (x + 1.29, y, 0.88), (0.18, 0.98, 0.72), props, leather, 0.09)
    for dx in (-1.03, 1.03):
        for dy in (-0.32, 0.32):
            cylinder('PROP_Sofa_Leg', (x + dx, y + dy, 0.16), 0.027, 0.30, props, steel, 32)


def add_console(props, steel, wood, ceramic):
    x, y = 3.95, 4.55
    for dx in (-0.96, 0.96):
        box('PROP_Console_Post', (x + dx, y, 1.45), (0.05, 0.05, 2.90), props, steel, 0.008)
    for z in (0.72, 1.52, 2.32):
        box('PROP_Console_Shelf', (x, y, z), (2.05, 0.62, 0.075), props, wood, 0.025)
    cylinder('PROP_Vase_A', (3.55, 4.50, 1.78), 0.18, 0.46, props, ceramic, 64, 0.025)
    cylinder('PROP_Vase_B', (4.35, 4.50, 2.62), 0.13, 0.52, props, ceramic, 64, 0.025)
    for i, z in enumerate((0.92, 1.02, 1.12)):
        book = box(f'PROP_Book_{i}', (4.25, 4.50, z), (0.55, 0.28, 0.08), props, wood, 0.012)
        book.rotation_euler.z = math.radians((-4, 2, -2)[i])


def add_arc_lamp(props, chrome, black):
    x, y = 4.75, 3.20
    cylinder('PROP_ArcLamp_Base', (x, y, 0.10), 0.34, 0.20, props, chrome, 96, 0.022)
    cylinder('PROP_ArcLamp_Stem', (x, y, 1.50), 0.035, 2.85, props, chrome, 48)
    # Thin boom, angled toward the stage.
    boom = box('PROP_ArcLamp_Boom', (3.88, 2.95, 3.05), (1.95, 0.055, 0.055), props, chrome, 0.020)
    boom.rotation_euler.y = math.radians(-18.0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=72, ring_count=36, location=(2.95, 2.68, 2.72))
    shade = bpy.context.object
    shade.name = 'PROP_ArcLamp_Shade'
    shade.scale = (0.45, 0.45, 0.30)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(shade, props)
    shade.data.materials.append(black)


def add_city(props, concrete):
    towers = (
        (-5.1, 1.8, 0.78, 3.6), (-4.25, 2.55, 0.68, 5.1), (-3.35, 1.45, 0.64, 2.9),
        (-2.55, 2.10, 0.72, 4.2), (-1.65, 1.70, 0.62, 3.4), (-0.75, 2.45, 0.74, 4.9),
    )
    for i, (x, z, sx, sz) in enumerate(towers):
        mat = concrete
        box(f'EXT_City_{i}', (x, 8.45 + (i % 2) * 0.25, z), (sx, 0.78, sz), props, mat, 0.018)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 360)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.32

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    concrete = concrete_material('MAT_Raw_Concrete', warm=True, polished=False)
    floor_mat = concrete_material('MAT_Polished_Concrete', warm=True, polished=True)
    pedestal_mat = concrete_material('MAT_Pedestal_Concrete', warm=True, polished=True)
    steel = material_principled('MAT_Dark_Steel', (0.018, 0.020, 0.024), 0.24, 0.82)
    glass = material_principled('MAT_Window_Glass', (0.74, 0.84, 1.0), 0.07, 0.0, 0.72, 1.47)
    leather = leather_material()
    wood = walnut_material()
    chrome = material_principled('MAT_Chrome', (0.46, 0.48, 0.52), 0.10, 1.0)
    ceramic = material_principled('MAT_Ceramic', (0.20, 0.18, 0.15), 0.34)
    black = material_principled('MAT_Lamp_Black', (0.008, 0.009, 0.012), 0.26, 0.60)

    box('ARCH_Floor', (0.0, 0.0, -0.10), (12.0, 12.0, 0.20), arch, floor_mat)
    box('ARCH_RightWall', (5.85, 0.0, 2.8), (0.30, 12.0, 5.6), arch, concrete)
    box('ARCH_LeftWall', (-5.85, 0.0, 2.8), (0.30, 12.0, 5.6), arch, concrete)
    add_back_window(arch, steel, glass, concrete)

    cylinder('STAGE_Pedestal', (0.0, -0.28, 0.23), 1.58, 0.46, arch, pedestal_mat, 192, 0.045)
    anchor = empty('PRODUCT_ANCHOR', (0.0, -0.28, 1.30), guides)

    add_sofa(props, leather, steel)
    add_console(props, steel, wood, ceramic)
    add_arc_lamp(props, chrome, black)
    add_city(props, concrete)

    key = area_light('LIGHT_Window_Soft', (-3.25, 5.05, 3.15), 1180, 4.2, (1.0, 0.80, 0.62), anchor, 'RECTANGLE', 3.5)
    fill = area_light('LIGHT_Right_Bounce', (4.65, -0.55, 2.70), 205, 3.2, (0.72, 0.82, 1.0), anchor, 'RECTANGLE', 2.4)
    practical = area_light('LIGHT_ArcLamp', (2.95, 2.68, 2.58), 95, 0.70, (1.0, 0.54, 0.30), anchor, 'DISK')
    for light in (key, fill, practical):
        move_to_collection(light, lights)

    sun_data = bpy.data.lights.new('LIGHT_Sun', 'SUN')
    sun_data.energy = 1.50
    sun_data.angle = math.radians(2.0)
    sun_data.color = (1.0, 0.60, 0.36)
    sun = bpy.data.objects.new('LIGHT_Sun', sun_data)
    lights.objects.link(sun)
    sun.rotation_euler = (math.radians(57.0), math.radians(-18.0), math.radians(144.0))

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.13, 0.20, 0.31, 1.0)
    bg.inputs['Strength'].default_value = 0.24

    cam = camera('CAM_Hero', (0.55, -10.9, 2.10), (0.0, 0.45, 1.26), 58.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 5.0

    scene.render.filepath = str(HERE / 'generated' / 'loft_daylight_v2.png')
    scene['scene_lab_id'] = 'loft-daylight-v2'
    scene['scene_lab_status'] = 'architectural-polish'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'LOFT_DAYLIGHT_V2_READY {options.output}')
