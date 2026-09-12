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
    cylinder, empty, material_principled, move_to_collection, save_blend,
)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(HERE / 'generated' / 'dark_neon_v2.blend'))
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
    noise.inputs['Scale'].default_value = 160.0
    noise.inputs['Detail'].default_value = 2.0
    noise.inputs['Roughness'].default_value = 0.68
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.022
    bump.inputs['Distance'].default_value = 0.0008
    bsdf.inputs['Base Color'].default_value = (0.006, 0.008, 0.014, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['Metallic'].default_value = 0.12
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
    noise.inputs['Scale'].default_value = 2.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.78
    noise.inputs['Distortion'].default_value = 4.0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.003, 0.004, 0.008, 1.0)
    ramp.color_ramp.elements[1].position = 0.76
    ramp.color_ramp.elements[1].color = (0.040, 0.045, 0.060, 1.0)
    vein = ramp.color_ramp.elements.new(0.60)
    vein.color = (0.20, 0.23, 0.30, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.13
    bsdf.inputs['Metallic'].default_value = 0.02
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


def add_backdrop_ribs(arch, wall_mat, accent_mat):
    for i, x in enumerate((-4.2, -3.0, -1.8, -0.6, 0.6, 1.8, 3.0, 4.2)):
        depth = 0.18 if i % 2 == 0 else 0.30
        z = 2.90
        rib = box(f'ARCH_Rib_{i:02d}', (x, 5.56 - depth * 0.5, z), (0.74, depth, 4.70), arch, wall_mat, 0.035)
        if i in (1, 6):
            rib.data.materials.clear()
            rib.data.materials.append(accent_mat)


def add_practical_tube(name, x, z, height, props, material):
    tube = box(name, (x, 5.15, z), (0.055, 0.055, height), props, material, 0.018)
    return tube


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 360)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.26

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    floor_mat = glossy_floor_material()
    marble = black_marble_material()
    wall_mat = material_principled('MAT_Navy_Wall', (0.006, 0.010, 0.022), 0.46)
    rib_accent = material_principled('MAT_Rib_Accent', (0.020, 0.028, 0.050), 0.30, 0.18)
    black = material_principled('MAT_Black_Metal', (0.004, 0.005, 0.009), 0.24, 0.78)
    magenta_emit = emissive_material('MAT_Magenta_Practical', (1.0, 0.012, 0.20), 5.0)
    cyan_emit = emissive_material('MAT_Cyan_Practical', (0.010, 0.22, 1.0), 5.0)

    box('ARCH_Floor', (0.0, 0.0, -0.08), (12.0, 13.0, 0.16), arch, floor_mat)
    box('ARCH_BackWall', (0.0, 5.82, 2.90), (12.0, 0.28, 5.8), arch, wall_mat)
    box('ARCH_LeftWall', (-5.90, 0.2, 2.90), (0.28, 11.5, 5.8), arch, wall_mat)
    box('ARCH_RightWall', (5.90, 0.2, 2.90), (0.28, 11.5, 5.8), arch, wall_mat)
    add_backdrop_ribs(arch, wall_mat, rib_accent)

    # Layered marble stage reads richer than one generic block.
    box('STAGE_Lower', (0.0, 0.0, 0.16), (3.65, 2.65, 0.32), arch, marble, 0.085)
    box('STAGE_Upper', (0.0, -0.05, 0.39), (3.05, 2.12, 0.22), arch, marble, 0.070)
    anchor = empty('PRODUCT_ANCHOR', (0.0, -0.05, 1.45), guides)

    add_practical_tube('PROP_Tube_Magenta', -4.35, 2.72, 2.70, props, magenta_emit)
    add_practical_tube('PROP_Tube_Cyan', 4.35, 2.72, 2.70, props, cyan_emit)
    add_practical_tube('PROP_Tube_Magenta_Inner', -3.10, 3.15, 1.65, props, magenta_emit)
    add_practical_tube('PROP_Tube_Cyan_Inner', 3.10, 3.15, 1.65, props, cyan_emit)

    # Hidden photographic sources. No white softbox geometry can intrude into camera.
    key = area_light('LIGHT_Magenta_Key', (-4.55, -0.15, 3.25), 1120, 3.2, (1.0, 0.012, 0.19), anchor, 'RECTANGLE', 2.1)
    fill = area_light('LIGHT_Cyan_Key', (4.55, 0.10, 3.25), 1240, 3.2, (0.012, 0.22, 1.0), anchor, 'RECTANGLE', 2.1)
    back_l = area_light('LIGHT_Back_Magenta', (-2.45, 4.25, 3.10), 440, 1.8, (1.0, 0.012, 0.18), anchor, 'RECTANGLE', 0.70)
    back_r = area_light('LIGHT_Back_Cyan', (2.45, 4.25, 3.10), 470, 1.8, (0.012, 0.20, 1.0), anchor, 'RECTANGLE', 0.70)
    top = area_light('LIGHT_Top_Neutral', (0.0, 0.25, 5.40), 255, 2.8, (0.76, 0.82, 1.0), anchor, 'RECTANGLE', 1.8)
    for light in (key, fill, back_l, back_r, top):
        move_to_collection(light, lights)

    # Small black cutters remain physically present but invisible to camera.
    for side in (-1.0, 1.0):
        flag = box(
            'PROP_Flag_L' if side < 0 else 'PROP_Flag_R',
            (side * 3.25, 1.55, 2.35), (0.07, 1.25, 3.05), props, black, 0.022,
        )
        flag.visible_camera = False

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.0015, 0.003, 0.010, 1.0)
    bg.inputs['Strength'].default_value = 0.065

    cam = camera('CAM_Hero', (0.0, -12.2, 2.25), (0.0, 0.25, 1.30), 64.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 4.0

    scene.render.filepath = str(HERE / 'generated' / 'dark_neon_v2.png')
    scene['scene_lab_id'] = 'dark-neon-v2'
    scene['scene_lab_status'] = 'clean-hidden-source-lighting'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'DARK_NEON_V2_READY {options.output}')
