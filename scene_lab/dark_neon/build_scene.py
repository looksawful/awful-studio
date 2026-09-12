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
    empty, marble_material, material_principled, move_to_collection, point_at,
    save_blend,
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
    noise.inputs['Scale'].default_value = 120.0
    noise.inputs['Detail'].default_value = 2.0
    noise.inputs['Roughness'].default_value = 0.72
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.035
    bump.inputs['Distance'].default_value = 0.0012
    bsdf.inputs['Base Color'].default_value = (0.012, 0.014, 0.021, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.17
    bsdf.inputs['Metallic'].default_value = 0.12
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
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
    point_at(shell, target, track='X' if abs(x) > abs(y) else '-Y', up='Z')
    thin = 0.025
    panel_dims = (thin, dimensions[1] * 0.90, dimensions[2] * 0.90) if dimensions[0] < dimensions[1] else (dimensions[0] * 0.90, thin, dimensions[2] * 0.90)
    panel_loc = (x * 0.985, y, z) if dimensions[0] < dimensions[1] else (x, y * 0.985, z)
    panel = box(name + '_Diffuser', panel_loc, panel_dims, props, diffuser_mat, 0.03)
    point_at(panel, target, track='X' if abs(x) > abs(y) else '-Y', up='Z')
    light = area_light(name + '_Light', panel_loc, energy, dimensions[2] * 0.78, light_color, target, 'RECTANGLE', dimensions[1] * 0.74)
    move_to_collection(light, lights)
    return shell, panel, light


def add_stand(prefix, x, y, height, props, steel):
    from common import cylinder
    cylinder(prefix+'_Pole', (x, y, height*0.47), 0.035, height*0.92, props, steel, 32)
    cylinder(prefix+'_Base', (x, y, 0.05), 0.42, 0.06, props, steel, 48)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 320)
    scene.render.film_transparent = False

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    floor_mat = glossy_floor_material()
    marble = marble_material('MAT_Black_Marble')
    wall_mat = material_principled('MAT_Navy_Wall', (0.010,0.017,0.032), 0.46)
    steel = material_principled('MAT_Black_Steel', (0.008,0.010,0.014), 0.26, 0.78)
    magenta_emit = emissive_material('MAT_Magenta_Diffuser', (1.0,0.015,0.32), 5.0)
    cyan_emit = emissive_material('MAT_Cyan_Diffuser', (0.015,0.26,1.0), 5.0)
    white_emit = emissive_material('MAT_White_Practical', (0.85,0.92,1.0), 7.0)

    box('ARCH_Floor', (0.0,0.0,-0.08), (12.0,13.0,0.16), arch, floor_mat)
    box('ARCH_BackWall', (0.0,5.85,2.9), (12.0,0.28,5.8), arch, wall_mat)
    box('ARCH_LeftWall', (-5.85,0.2,2.9), (0.28,11.5,5.8), arch, wall_mat)
    box('ARCH_RightWall', (5.85,0.2,2.9), (0.28,11.5,5.8), arch, wall_mat)

    box('STAGE_Plinth', (0.0,0.0,0.275), (3.4,2.5,0.55), arch, marble, 0.07)
    anchor = empty('PRODUCT_ANCHOR', (0.0,0.0,1.42), guides)

    make_soft_panel('PROP_MagentaPanel', (-4.30,-0.55,3.10), (0.18,2.05,3.10), anchor, steel, magenta_emit, (1.0,0.02,0.24), 1350, props, lights)
    make_soft_panel('PROP_CyanPanel', (4.35,0.05,3.15), (0.18,2.05,3.10), anchor, steel, cyan_emit, (0.02,0.22,1.0), 1450, props, lights)
    add_stand('PROP_MagentaStand', -4.30, -0.38, 3.0, props, steel)
    add_stand('PROP_CyanStand', 4.35, 0.22, 3.0, props, steel)

    for i, x in enumerate((-3.3, 3.3)):
        box(f'PROP_RearStrip_{i}', (x,4.85,2.65), (0.12,0.12,3.8), props, white_emit, 0.018)
    rear_l = area_light('LIGHT_Rear_Magenta', (-2.5,3.7,2.8), 620, 2.0, (1.0,0.01,0.22), anchor, 'RECTANGLE', 0.8)
    move_to_collection(rear_l, lights)
    rear_r = area_light('LIGHT_Rear_Cyan', (2.5,3.7,2.8), 680, 2.0, (0.02,0.24,1.0), anchor, 'RECTANGLE', 0.8)
    move_to_collection(rear_r, lights)
    top = area_light('LIGHT_Top_Neutral', (0.0,0.2,5.4), 420, 3.0, (0.84,0.88,1.0), anchor, 'RECTANGLE', 2.0)
    move_to_collection(top, lights)

    box('PROP_Flag_L', (-2.95,1.25,2.2), (0.08,1.6,3.3), props, steel, 0.025)
    box('PROP_Flag_R', (2.95,1.25,2.2), (0.08,1.6,3.3), props, steel, 0.025)

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.003,0.006,0.016,1.0)
    bg.inputs['Strength'].default_value = 0.10

    cam = camera('CAM_Hero', (0.0,-9.6,2.0), (0.0,0.0,1.35), 74.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 3.6

    scene.render.filepath = str(HERE / 'generated' / 'dark_neon_v1.png')
    scene['scene_lab_id'] = 'dark-neon-v1'
    scene['scene_lab_status'] = 'structural-builder'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'DARK_NEON_READY {options.output}')
