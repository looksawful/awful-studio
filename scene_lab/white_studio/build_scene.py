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
    cylinder, empty, material_principled, move_to_collection, point_at, save_blend,
)


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(HERE / 'generated' / 'white_studio_v1.blend'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def painted_white(name, base=(0.64, 0.64, 0.62, 1.0), roughness=0.52):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 105.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.75
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.46, 0.46, 0.45, 1.0)
    ramp.color_ramp.elements[1].color = base
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.045
    bump.inputs['Distance'].default_value = 0.0012
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def cyclorama(col, mat):
    width = 12.0
    front_y = -6.4
    curve_y = 2.4
    radius = 2.8
    top_z = 6.4
    profile = [(front_y, 0.0), (curve_y, 0.0)]
    for i in range(1, 81):
        t = i / 80.0
        a = math.radians(-90.0 + 90.0 * t)
        y = curve_y + radius * math.cos(a)
        z = radius + radius * math.sin(a)
        profile.append((y, z))
    profile.append((curve_y + radius, top_z))
    verts = []
    for x in (-width / 2.0, width / 2.0):
        verts.extend((x, y, z) for y, z in profile)
    n = len(profile)
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    mesh = bpy.data.meshes.new('MESH_Cyclorama')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('ARCH_Cyclorama', mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    bevel = obj.modifiers.new('Micro Bevel', 'BEVEL')
    bevel.width = 0.006
    bevel.segments = 2
    return obj


def emissive(name, color, strength=1.2):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = strength
    links.new(emission.outputs['Emission'], out.inputs['Surface'])
    return mat


def softbox(name, x, y, z, height, width, target, props, lights, energy):
    black = material_principled(name + '_Black', (0.012, 0.012, 0.015), 0.40)
    white = emissive(name + '_Diffuser', (1.0, 0.94, 0.87), 1.15)
    shell = box(name + '_Shell', (x, y, z), (0.16, width, height), props, black, 0.055)
    point_at(shell, target, track='X', up='Z')
    panel = box(name + '_Diffuser', (x * 0.988, y, z), (0.02, width * 0.91, height * 0.91), props, white, 0.025)
    point_at(panel, target, track='X', up='Z')
    light = area_light(name + '_Light', (x * 0.965, y, z), energy, height * 0.80, (1.0, 0.88, 0.77), target, 'RECTANGLE', width * 0.80)
    move_to_collection(light, lights)
    cylinder(name + '_Stand', (x, y + 0.15, z * 0.47), 0.032, z * 0.92, props, black, 32)
    cylinder(name + '_Foot', (x, y + 0.15, 0.052), 0.38, 0.05, props, black, 48)


def plant(col):
    pot_mat = material_principled('MAT_Pot', (0.055, 0.048, 0.043), 0.58)
    leaf_mat = material_principled('MAT_Leaves', (0.025, 0.12, 0.042), 0.52)
    stem_mat = material_principled('MAT_Stem', (0.07, 0.045, 0.025), 0.64)
    cx, cy = -3.0, 3.05
    cylinder('PROP_Plant_Pot', (cx, cy, 0.30), 0.32, 0.60, col, pot_mat, 64, 0.035)
    cylinder('PROP_Plant_Stem', (cx, cy, 1.00), 0.045, 1.18, col, stem_mat, 32)
    for i in range(12):
        angle = math.radians(i * 137.5)
        z = 1.02 + (i % 5) * 0.18
        r = 0.28 + (i % 3) * 0.09
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(x, y, z))
        leaf = bpy.context.object
        leaf.name = f'PROP_Plant_Leaf_{i:02d}'
        leaf.scale = (0.30, 0.10, 0.045)
        leaf.rotation_euler = (math.radians(15), math.radians(-6), angle)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to_collection(leaf, col)
        leaf.data.materials.append(leaf_mat)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 256)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.65
    scene.world.color = (0.025, 0.025, 0.025)
    if scene.world and scene.world.use_nodes:
        bg = scene.world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value = (0.025, 0.025, 0.028, 1.0)
            bg.inputs['Strength'].default_value = 0.13

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    white = painted_white('MAT_Cyclorama')
    pedestal_mat = painted_white('MAT_Pedestal', (0.50, 0.49, 0.46, 1.0), 0.44)
    black = material_principled('MAT_NegativeFill', (0.003, 0.003, 0.004), 0.86)

    cyclorama(arch, white)
    cylinder('STAGE_Pedestal', (0.0, 0.0, 0.23), 1.58, 0.46, arch, pedestal_mat, 160, 0.04)
    anchor = empty('PRODUCT_ANCHOR', (0.0, 0.0, 1.30), guides)

    softbox('PROP_Softbox_L', -4.85, -0.15, 3.30, 3.25, 2.30, anchor, props, lights, 720)
    softbox('PROP_Softbox_R', 4.95, 0.40, 3.15, 3.00, 2.10, anchor, props, lights, 430)
    flag_l = box('PROP_Flag_L', (-4.15, 1.15, 2.20), (0.07, 1.55, 3.10), props, black, 0.02)
    flag_r = box('PROP_Flag_R', (4.15, 1.35, 2.25), (0.07, 1.45, 3.05), props, black, 0.02)
    flag_l.visible_camera = False
    flag_r.visible_camera = False
    plant(props)

    top = area_light('LIGHT_Top', (0.0, 0.25, 5.65), 320, 3.5, (1.0, 0.94, 0.86), anchor, 'RECTANGLE', 2.2)
    move_to_collection(top, lights)
    rim = area_light('LIGHT_Back_Rim', (0.0, 3.7, 3.0), 220, 2.2, (1.0, 0.88, 0.75), anchor, 'RECTANGLE', 1.0)
    move_to_collection(rim, lights)

    cam = camera('CAM_Hero', (0.0, -12.4, 2.30), (0.0, 0.20, 1.20), 61.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 5.0

    scene.render.filepath = str(HERE / 'generated' / 'white_studio_v1.png')
    scene['scene_lab_id'] = 'white-studio-v1'
    scene['scene_lab_status'] = 'visual-pass-2'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'WHITE_STUDIO_READY {options.output}')
