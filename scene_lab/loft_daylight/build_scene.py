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
    noise.inputs['Scale'].default_value = 360.0
    noise.inputs['Detail'].default_value = 2.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.0007
    bsdf.inputs['Base Color'].default_value = (0.012, 0.014, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.30
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
    noise.inputs['Scale'].default_value = 4.5
    noise.inputs['Detail'].default_value = 3.0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.035, 0.014, 0.007, 1.0)
    ramp.color_ramp.elements[1].color = (0.27, 0.10, 0.025, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.34
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def add_back_window(arch, steel, glass, concrete):
    y = 5.72
    left, right = -5.70, -1.10
    bottom, top = 0.50, 5.10
    cx = (left + right) * 0.5
    width = right - left
    height = top - bottom
    frame = 0.10
    depth = 0.16
    # Real wall substrate around the opening.
    box('ARCH_Back_Right', (2.45, 5.85, 2.8), (7.10, 0.30, 5.6), arch, concrete)
    box('ARCH_Back_LeftPier', (-5.85, 5.85, 2.8), (0.30, 0.30, 5.6), arch, concrete)
    box('ARCH_Back_WindowBottom', (cx, 5.85, bottom * 0.5), (width, 0.30, bottom), arch, concrete)
    box('ARCH_Back_WindowTop', (cx, 5.85, top + (5.6-top)*0.5), (width, 0.30, 5.6-top), arch, concrete)
    glass_obj = box('ARCH_Window_Glass', (cx, y, (bottom+top)*0.5), (width-frame*2, 0.018, height-frame*2), arch, glass)
    glass_obj.visible_shadow = False
    for x in (left, right):
        box('ARCH_Window_Jamb', (x, y-0.03, (bottom+top)*0.5), (frame, depth, height), arch, steel, 0.008)
    for z in (bottom, top):
        box('ARCH_Window_Rail', (cx, y-0.03, z), (width, depth, frame), arch, steel, 0.008)
    for i in range(1, 4):
        x = left + width * i / 4
        box(f'ARCH_Window_Mullion_V{i}', (x, y-0.03, (bottom+top)*0.5), (frame*0.72, depth, height-frame*2), arch, steel, 0.006)
    for i in range(1, 3):
        z = bottom + height * i / 3
        box(f'ARCH_Window_Mullion_H{i}', (cx, y-0.03, z), (width-frame*2, depth, frame*0.72), arch, steel, 0.006)


def add_sofa(props, leather, steel):
    x, y = -3.60, 3.45
    box('PROP_Sofa_Base', (x, y, 0.47), (2.65, 0.98, 0.30), props, leather, 0.10)
    box('PROP_Sofa_Seat', (x, y-0.06, 0.70), (2.42, 0.82, 0.20), props, leather, 0.10)
    box('PROP_Sofa_Back', (x, y+0.35, 1.23), (2.48, 0.18, 1.02), props, leather, 0.09)
    box('PROP_Sofa_Arm_L', (x-1.20, y, 0.86), (0.18, 0.96, 0.70), props, leather, 0.08)
    box('PROP_Sofa_Arm_R', (x+1.20, y, 0.86), (0.18, 0.96, 0.70), props, leather, 0.08)
    for dx in (-1.0, 1.0):
        for dy in (-0.31, 0.31):
            cylinder('PROP_Sofa_Leg', (x+dx, y+dy, 0.17), 0.032, 0.32, props, steel, 28)


def add_shelf(props, steel, wood):
    x, y = 4.05, 4.55
    for dx in (-0.92, 0.92):
        for dy in (-0.24, 0.24):
            box('PROP_Shelf_Post', (x+dx, y+dy, 2.0), (0.05, 0.05, 4.0), props, steel, 0.006)
    for z in (0.75, 1.55, 2.35, 3.15):
        box('PROP_Shelf_Board', (x, y, z), (2.0, 0.62, 0.075), props, wood, 0.02)


def add_plant(props, center, scale, pot_mat, leaf_mat, stem_mat, prefix):
    x, y = center
    cylinder(prefix+'_Pot', (x, y, 0.30*scale), 0.31*scale, 0.60*scale, props, pot_mat, 56, 0.025*scale)
    cylinder(prefix+'_Stem', (x, y, 0.90*scale), 0.034*scale, 0.95*scale, props, stem_mat, 24)
    for i in range(10):
        angle = math.radians(i*137.5)
        r = (0.25 + 0.075*(i%3))*scale
        z = (0.90 + 0.16*(i%4))*scale
        bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=14, location=(x+math.cos(angle)*r, y+math.sin(angle)*r, z))
        leaf = bpy.context.object
        leaf.name = f'{prefix}_Leaf_{i:02d}'
        leaf.scale = (0.26*scale, 0.085*scale, 0.042*scale)
        leaf.rotation_euler = (math.radians(16), math.radians(-6), angle)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to_collection(leaf, props)
        leaf.data.materials.append(leaf_mat)


def add_city(props, concrete):
    for i, (x, z, sx, sz) in enumerate((
        (-4.9, 2.0, 1.0, 4.0), (-3.7, 2.6, 0.9, 5.2), (-2.5, 1.6, 0.8, 3.2), (-1.5, 2.2, 0.7, 4.4)
    )):
        box(f'EXT_City_{i}', (x, 8.6 + i*0.25, z), (sx, 0.9, sz), props, concrete, 0.02)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 320)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.45

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    concrete = concrete_material('MAT_Raw_Concrete', warm=True, polished=False)
    floor_mat = concrete_material('MAT_Polished_Concrete', warm=True, polished=True)
    pedestal_mat = concrete_material('MAT_Pedestal_Concrete', warm=True, polished=True)
    steel = material_principled('MAT_Dark_Steel', (0.018,0.020,0.024), 0.26, 0.78)
    glass = material_principled('MAT_Window_Glass', (0.76,0.86,1.0), 0.08, 0.0, 0.72, 1.47)
    leather = leather_material()
    wood = wood_material()
    chrome = material_principled('MAT_Chrome', (0.42,0.45,0.48), 0.10, 1.0)
    pot = material_principled('MAT_Pot', (0.025,0.028,0.025), 0.54)
    leaf = material_principled('MAT_Leaf', (0.018,0.13,0.045), 0.48)
    stem = material_principled('MAT_Stem', (0.06,0.03,0.015), 0.62)

    box('ARCH_Floor', (0.0, 0.0, -0.10), (12.0, 12.0, 0.20), arch, floor_mat)
    box('ARCH_RightWall', (5.85, 0.0, 2.8), (0.30, 12.0, 5.6), arch, concrete)
    box('ARCH_LeftWall', (-5.85, 0.0, 2.8), (0.30, 12.0, 5.6), arch, concrete)
    add_back_window(arch, steel, glass, concrete)

    cylinder('STAGE_Pedestal', (0.0, -0.35, 0.22), 1.52, 0.44, arch, pedestal_mat, 160, 0.04)
    anchor = empty('PRODUCT_ANCHOR', (0.0, -0.35, 1.28), guides)

    add_sofa(props, leather, steel)
    add_shelf(props, steel, wood)
    add_plant(props, (-4.85, 4.25), 1.02, pot, leaf, stem, 'PROP_Plant_Left')
    add_plant(props, (5.00, 4.05), 1.08, pot, leaf, stem, 'PROP_Plant_Right')
    add_plant(props, (4.10, 4.48), 0.48, pot, leaf, stem, 'PROP_Plant_Shelf')
    add_city(props, concrete)

    cylinder('PROP_ChromeLamp_Base', (4.45, 3.55, 0.12), 0.34, 0.24, props, chrome, 80, 0.02)
    cylinder('PROP_ChromeLamp_Stem', (4.45, 3.55, 0.76), 0.046, 1.05, props, chrome, 40)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=72, ring_count=36, location=(4.45, 3.55, 1.38))
    dome = bpy.context.object
    dome.name = 'PROP_ChromeLamp_Dome'
    dome.scale = (0.50,0.50,0.32)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(dome, props)
    dome.data.materials.append(chrome)

    key = area_light('LIGHT_Window_Soft', (-3.45, 5.15, 3.25), 920, 4.0, (1.0,0.78,0.58), anchor, 'RECTANGLE', 3.2)
    move_to_collection(key, lights)
    fill = area_light('LIGHT_Right_Bounce', (4.8, -0.8, 2.8), 220, 3.2, (0.72,0.82,1.0), anchor, 'RECTANGLE', 2.4)
    move_to_collection(fill, lights)
    practical = area_light('LIGHT_ChromeLamp', (4.45,3.55,1.16), 85, 0.55, (1.0,0.48,0.20), (3.9,3.0,1.0))
    move_to_collection(practical, lights)

    sun_data = bpy.data.lights.new('LIGHT_Sun', 'SUN')
    sun_data.energy = 1.25
    sun_data.angle = math.radians(2.2)
    sun_data.color = (1.0,0.56,0.31)
    sun = bpy.data.objects.new('LIGHT_Sun', sun_data)
    lights.objects.link(sun)
    sun.rotation_euler = (math.radians(58), math.radians(-16), math.radians(146))

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.16,0.22,0.32,1.0)
    bg.inputs['Strength'].default_value = 0.22

    cam = camera('CAM_Hero', (0.45,-10.8,2.05), (0.0,0.45,1.28), 58.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 4.5

    scene.render.filepath = str(HERE / 'generated' / 'loft_daylight_v1.png')
    scene['scene_lab_id'] = 'loft-daylight-v1'
    scene['scene_lab_status'] = 'visual-pass-2'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'LOFT_DAYLIGHT_READY {options.output}')
