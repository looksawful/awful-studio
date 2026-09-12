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
    parser.add_argument('--output', default=str(HERE / 'generated' / 'loft_daylight_v1.blend'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def leather_material():
    mat = bpy.data.materials.new('MAT_Black_Leather')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 420.0
    noise.inputs['Detail'].default_value = 2.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.10
    bump.inputs['Distance'].default_value = 0.0008
    bsdf.inputs['Base Color'].default_value = (0.015, 0.016, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def wood_material():
    mat = bpy.data.materials.new('MAT_Walnut')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.5
    noise.inputs['Detail'].default_value = 3.0
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 5.2
    wave.inputs['Distortion'].default_value = 6.5
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.55
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.06, 0.025, 0.012, 1.0)
    ramp.color_ramp.elements[1].color = (0.32, 0.12, 0.035, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.36
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs[1])
    links.new(wave.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def add_window(props, steel, glass):
    x = -5.72
    center_y = 1.10
    width_y = 6.3
    bottom = 0.45
    top = 5.15
    frame = 0.095
    depth = 0.16
    mid_z = (bottom + top) * 0.5
    box('ARCH_Window_Glass', (x, center_y, mid_z), (0.018, width_y, top-bottom), props, glass)
    for y in (center_y - width_y/2, center_y + width_y/2):
        box('ARCH_Window_Jamb', (x+0.03, y, mid_z), (depth, frame, top-bottom), props, steel, 0.01)
    for z in (bottom, top):
        box('ARCH_Window_Rail', (x+0.03, center_y, z), (depth, width_y, frame), props, steel, 0.01)
    for i in range(1, 4):
        y = center_y - width_y/2 + width_y * i/4
        box(f'ARCH_Window_Mullion_V{i}', (x+0.03, y, mid_z), (depth, frame*0.72, top-bottom-frame*2), props, steel, 0.008)
    for i in range(1, 3):
        z = bottom + (top-bottom) * i/3
        box(f'ARCH_Window_Mullion_H{i}', (x+0.03, center_y, z), (depth, width_y-frame*2, frame*0.72), props, steel, 0.008)


def add_sofa(props, leather, steel):
    x, y = -3.45, 2.65
    box('PROP_Sofa_Base', (x, y, 0.48), (2.7, 1.05, 0.32), props, leather, 0.10)
    box('PROP_Sofa_Seat', (x, y-0.08, 0.72), (2.48, 0.88, 0.22), props, leather, 0.11)
    box('PROP_Sofa_Back', (x, y+0.39, 1.28), (2.55, 0.20, 1.12), props, leather, 0.10)
    box('PROP_Sofa_Arm_L', (x-1.23, y, 0.90), (0.20, 1.03, 0.78), props, leather, 0.09)
    box('PROP_Sofa_Arm_R', (x+1.23, y, 0.90), (0.20, 1.03, 0.78), props, leather, 0.09)
    for dx in (-1.05, 1.05):
        for dy in (-0.34, 0.34):
            cylinder('PROP_Sofa_Leg', (x+dx, y+dy, 0.18), 0.035, 0.34, props, steel, 32)


def add_shelf(props, steel, wood):
    x, y = 3.95, 2.85
    for dx in (-1.05, 1.05):
        for dy in (-0.27, 0.27):
            box('PROP_Shelf_Post', (x+dx, y+dy, 2.0), (0.055, 0.055, 4.0), props, steel, 0.008)
    for z in (0.75, 1.55, 2.35, 3.15):
        box('PROP_Shelf_Board', (x, y, z), (2.25, 0.68, 0.08), props, wood, 0.025)


def add_plant(props, center, scale, pot_mat, leaf_mat, stem_mat, prefix):
    x, y = center
    cylinder(prefix+'_Pot', (x, y, 0.32*scale), 0.34*scale, 0.64*scale, props, pot_mat, 64, 0.025*scale)
    cylinder(prefix+'_Stem', (x, y, 0.95*scale), 0.038*scale, 1.0*scale, props, stem_mat, 24)
    for i in range(9):
        angle = math.radians(i*137.5)
        r = (0.28 + 0.08*(i%3))*scale
        z = (0.98 + 0.17*(i%4))*scale
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(x+math.cos(angle)*r, y+math.sin(angle)*r, z))
        leaf = bpy.context.object
        leaf.name = f'{prefix}_Leaf_{i:02d}'
        leaf.scale = (0.28*scale, 0.095*scale, 0.045*scale)
        leaf.rotation_euler = (math.radians(18), math.radians(-8), angle)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to_collection(leaf, props)
        leaf.data.materials.append(leaf_mat)


def add_city(props, concrete):
    for i, (y, z, sy, sz) in enumerate((
        (-1.5, 1.7, 1.2, 3.4), (0.0, 2.3, 1.5, 4.6), (1.8, 1.4, 1.1, 2.8), (3.2, 2.0, 1.3, 4.0)
    )):
        box(f'EXT_City_{i}', (-8.4-i*0.3, y, z), (0.8, sy, sz), props, concrete, 0.02)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 320)
    scene.render.film_transparent = False

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    concrete = concrete_material('MAT_Raw_Concrete', warm=True, polished=False)
    floor_mat = concrete_material('MAT_Polished_Concrete', warm=True, polished=True)
    pedestal_mat = concrete_material('MAT_Pedestal_Concrete', warm=True, polished=True)
    steel = material_principled('MAT_Dark_Steel', (0.025,0.027,0.03), 0.28, 0.72)
    glass = material_principled('MAT_Window_Glass', (0.80,0.90,1.0), 0.06, 0.0, 0.85, 1.47)
    leather = leather_material()
    wood = wood_material()
    chrome = material_principled('MAT_Chrome', (0.48,0.50,0.53), 0.12, 1.0)
    pot = material_principled('MAT_Pot', (0.03,0.032,0.028), 0.52)
    leaf = material_principled('MAT_Leaf', (0.02,0.16,0.055), 0.46)
    stem = material_principled('MAT_Stem', (0.07,0.035,0.018), 0.60)

    box('ARCH_Floor', (0.0, 0.0, -0.10), (12.0, 12.0, 0.20), arch, floor_mat)
    box('ARCH_BackWall', (0.0, 5.85, 2.8), (12.0, 0.30, 5.6), arch, concrete)
    box('ARCH_RightWall', (5.85, 0.0, 2.8), (0.30, 12.0, 5.6), arch, concrete)
    box('ARCH_LeftWallRear', (-5.85, 4.9, 2.8), (0.30, 1.9, 5.6), arch, concrete)
    box('ARCH_LeftWallFront', (-5.85, -3.1, 2.8), (0.30, 3.4, 5.6), arch, concrete)
    box('ARCH_LeftWallBottom', (-5.85, 1.1, 0.22), (0.30, 6.3, 0.44), arch, concrete)
    box('ARCH_LeftWallTop', (-5.85, 1.1, 5.38), (0.30, 6.3, 0.44), arch, concrete)

    add_window(arch, steel, glass)
    cylinder('STAGE_Pedestal', (0.0, -0.15, 0.24), 1.65, 0.48, arch, pedestal_mat, 160, 0.045)
    anchor = empty('PRODUCT_ANCHOR', (0.0, -0.15, 1.30), guides)

    add_sofa(props, leather, steel)
    add_shelf(props, steel, wood)
    add_plant(props, (-4.65, 3.8), 1.15, pot, leaf, stem, 'PROP_Plant_Left')
    add_plant(props, (5.0, 3.9), 1.25, pot, leaf, stem, 'PROP_Plant_Right')
    add_plant(props, (4.2, 2.8), 0.55, pot, leaf, stem, 'PROP_Plant_Shelf')
    add_city(props, concrete)

    cylinder('PROP_ChromeLamp_Base', (4.25, 2.55, 0.13), 0.38, 0.26, props, chrome, 96, 0.02)
    cylinder('PROP_ChromeLamp_Stem', (4.25, 2.55, 0.85), 0.055, 1.2, props, chrome, 48)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, location=(4.25, 2.55, 1.55))
    dome = bpy.context.object
    dome.name = 'PROP_ChromeLamp_Dome'
    dome.scale = (0.56,0.56,0.38)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(dome, props)
    dome.data.materials.append(chrome)

    key = area_light('LIGHT_Window_Soft', (-5.20, -0.2, 3.25), 1650, 4.2, (1.0,0.82,0.62), anchor, 'RECTANGLE', 3.2)
    move_to_collection(key, lights)
    fill = area_light('LIGHT_Right_Bounce', (4.6, -1.0, 2.6), 340, 3.0, (0.76,0.84,1.0), anchor, 'RECTANGLE', 2.6)
    move_to_collection(fill, lights)
    practical = area_light('LIGHT_ChromeLamp', (4.25,2.55,1.28), 120, 0.7, (1.0,0.48,0.20), (3.6,1.9,1.0))
    move_to_collection(practical, lights)

    sun_data = bpy.data.lights.new('LIGHT_Sun', 'SUN')
    sun_data.energy = 2.2
    sun_data.angle = math.radians(4.0)
    sun_data.color = (1.0,0.63,0.38)
    sun = bpy.data.objects.new('LIGHT_Sun', sun_data)
    lights.objects.link(sun)
    sun.rotation_euler = (math.radians(53), math.radians(-20), math.radians(-72))

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.22,0.27,0.34,1.0)
    bg.inputs['Strength'].default_value = 0.38

    cam = camera('CAM_Hero', (0.0,-9.3,1.85), (0.0,0.0,1.25), 68.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 4.0

    scene.render.filepath = str(HERE / 'generated' / 'loft_daylight_v1.png')
    scene['scene_lab_id'] = 'loft-daylight-v1'
    scene['scene_lab_status'] = 'structural-builder'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'LOFT_DAYLIGHT_READY {options.output}')
