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
    empty, material_principled, move_to_collection, point_at, save_blend,
)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(HERE / 'generated' / 'dark_neon_v1.blend'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def glossy_floor_material():
    mat = bpy.data.materials.new('MAT_Dark_Polished_Floor')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 135.0
    noise.inputs['Detail'].default_value = 2.0
    noise.inputs['Roughness'].default_value = 0.70
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.028
    bump.inputs['Distance'].default_value = 0.0010
    bsdf.inputs['Base Color'].default_value = (0.008, 0.011, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Metallic'].default_value = 0.08
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def black_marble_material():
    mat = bpy.data.materials.new('MAT_Black_Marble')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 2.2
    noise.inputs['Detail'].default_value = 7.0
    noise.inputs['Roughness'].default_value = 0.72
    noise.inputs['Distortion'].default_value = 3.5
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.004, 0.006, 0.010, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.030, 0.035, 0.045, 1.0)
    vein = ramp.color_ramp.elements.new(0.61)
    vein.color = (0.28, 0.31, 0.36, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.14
    bsdf.inputs['Metallic'].default_value = 0.03
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def emissive_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = strength
    links.new(emission.outputs['Emission'], out.inputs['Surface'])
    return mat


def make_soft_panel(name, location, dimensions, target, shell_mat, diffuser_mat, light_color, energy, props, lights):
    x, y, z = location
    shell = box(name + '_Shell', location, dimensions, props, shell_mat, 0.05)
    point_at(shell, target, track='X', up='Z')
    panel = box(name + '_Diffuser', (x * 0.985, y, z), (0.025, dimensions[1] * 0.90, dimensions[2] * 0.90), props, diffuser_mat, 0.03)
    point_at(panel, target, track='X', up='Z')
    light = area_light(name + '_Light', (x * 0.96, y, z), energy, dimensions[2] * 0.76, light_color, target, 'RECTANGLE', dimensions[1] * 0.72)
    move_to_collection(light, lights)
    return shell, panel, light


def add_stand(prefix, x, y, height, props, steel):
    from common import cylinder
    cylinder(prefix+'_Pole', (x, y, height*0.47), 0.032, height*0.92, props, steel, 32)
    cylinder(prefix+'_Base', (x, y, 0.05), 0.36, 0.06, props, steel, 48)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 320)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.20

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    floor_mat = glossy_floor_material()
    marble = black_marble_material()
    wall_mat = material_principled('MAT_Navy_Wall', (0.008,0.014,0.028), 0.48)
    steel = material_principled('MAT_Black_Steel', (0.006,0.008,0.012), 0.28, 0.72)
    magenta_emit = emissive_material('MAT_Magenta_Diffuser', (1.0,0.012,0.26), 3.0)
    cyan_emit = emissive_material('MAT_Cyan_Diffuser', (0.012,0.22,1.0), 3.0)
    white_emit = emissive_material('MAT_White_Practical', (0.70,0.84,1.0), 3.5)

    box('ARCH_Floor', (0.0,0.0,-0.08), (12.0,13.0,0.16), arch, floor_mat)
    box('ARCH_BackWall', (0.0,5.90,2.9), (12.0,0.28,5.8), arch, wall_mat)
    box('ARCH_LeftWall', (-5.90,0.2,2.9), (0.28,11.5,5.8), arch, wall_mat)
    box('ARCH_RightWall', (5.90,0.2,2.9), (0.28,11.5,5.8), arch, wall_mat)

    box('STAGE_Plinth', (0.0,0.0,0.25), (3.05,2.15,0.50), arch, marble, 0.055)
    anchor = empty('PRODUCT_ANCHOR', (0.0,0.0,1.38), guides)

    make_soft_panel('PROP_MagentaPanel', (-4.65,-0.35,3.10), (0.16,2.20,3.15), anchor, steel, magenta_emit, (1.0,0.015,0.23), 920, props, lights)
    make_soft_panel('PROP_CyanPanel', (4.70,0.10,3.15), (0.16,2.20,3.15), anchor, steel, cyan_emit, (0.015,0.22,1.0), 980, props, lights)
    add_stand('PROP_MagentaStand', -4.65, -0.15, 3.0, props, steel)
    add_stand('PROP_CyanStand', 4.70, 0.28, 3.0, props, steel)

    for i, x in enumerate((-3.55, 3.55)):
        strip = box(f'PROP_RearStrip_{i}', (x,5.05,2.75), (0.09,0.09,3.2), props, white_emit, 0.012)
        strip.visible_camera = True

    rear_l = area_light('LIGHT_Rear_Magenta', (-2.7,3.9,2.9), 430, 1.8, (1.0,0.01,0.20), anchor, 'RECTANGLE', 0.65)
    move_to_collection(rear_l, lights)
    rear_r = area_light('LIGHT_Rear_Cyan', (2.7,3.9,2.9), 460, 1.8, (0.02,0.20,1.0), anchor, 'RECTANGLE', 0.65)
    move_to_collection(rear_r, lights)
    top = area_light('LIGHT_Top_Neutral', (0.0,0.4,5.35), 220, 2.8, (0.76,0.82,1.0), anchor, 'RECTANGLE', 1.8)
    move_to_collection(top, lights)

    floor_l = area_light('LIGHT_Floor_Magenta', (-3.2,-0.2,0.18), 180, 1.5, (1.0,0.01,0.24), (0.0,0.0,0.1), 'RECTANGLE', 0.35)
    floor_l.rotation_euler.x = math.radians(90)
    move_to_collection(floor_l, lights)
    floor_r = area_light('LIGHT_Floor_Cyan', (3.2,0.1,0.18), 190, 1.5, (0.01,0.22,1.0), (0.0,0.0,0.1), 'RECTANGLE', 0.35)
    floor_r.rotation_euler.x = math.radians(90)
    move_to_collection(floor_r, lights)

    flag_l = box('PROP_Flag_L', (-3.15,1.55,2.25), (0.08,1.45,3.15), props, steel, 0.025)
    flag_r = box('PROP_Flag_R', (3.15,1.55,2.25), (0.08,1.45,3.15), props, steel, 0.025)
    flag_l.visible_camera = False
    flag_r.visible_camera = False

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.002,0.004,0.012,1.0)
    bg.inputs['Strength'].default_value = 0.08

    cam = camera('CAM_Hero', (0.0,-11.8,2.25), (0.0,0.15,1.30), 60.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 4.2

    scene.render.filepath = str(HERE / 'generated' / 'dark_neon_v1.png')
    scene['scene_lab_id'] = 'dark-neon-v1'
    scene['scene_lab_status'] = 'visual-pass-2'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'DARK_NEON_READY {options.output}')
