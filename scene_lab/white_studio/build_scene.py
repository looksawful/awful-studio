from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

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


def painted_white(name, base=(0.82, 0.82, 0.80, 1.0), roughness=0.48):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 95.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.8
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.68, 0.68, 0.66, 1.0)
    ramp.color_ramp.elements[1].color = base
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.0018
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def cyclorama(col, mat):
    width = 12.0
    front_y = -5.5
    curve_y = 2.2
    radius = 2.6
    top_z = 6.3
    profile = [(front_y, 0.0), (curve_y, 0.0)]
    for i in range(1, 65):
        t = i / 64.0
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
    bevel.width = 0.008
    bevel.segments = 2
    return obj


def emissive(name, color, strength=5.0):
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
    black = material_principled(name + '_Black', (0.015, 0.015, 0.018), 0.38)
    white = emissive(name + '_Diffuser', (1.0, 0.97, 0.93), 3.0)
    shell = box(name + '_Shell', (x, y, z), (0.16, width, height), props, black, 0.05)
    point_at(shell, target, track='X', up='Z')
    panel = box(name + '_Diffuser', (x * 0.985, y, z), (0.02, width * 0.91, height * 0.91), props, white, 0.025)
    point_at(panel, target, track='X', up='Z')
    light = area_light(name + '_Light', (x * 0.96, y, z), energy, height * 0.80, (1.0, 0.91, 0.82), target, 'RECTANGLE', width * 0.80)
    move_to_collection(light, lights)
    pole = cylinder(name + '_Stand', (x, y + 0.15, z * 0.47), 0.035, z * 0.92, props, black, 32)
    foot = cylinder(name + '_Foot', (x, y + 0.15, 0.055), 0.42, 0.05, props, black, 48)
    return shell, panel, pole, foot


def plant(col):
    pot_mat = material_principled('MAT_Pot', (0.055, 0.05, 0.045), 0.55)
    leaf_mat = material_principled('MAT_Leaves', (0.035, 0.16, 0.055), 0.48)
    stem_mat = material_principled('MAT_Stem', (0.08, 0.055, 0.03), 0.62)
    cylinder('PROP_Plant_Pot', (-3.65, 2.55, 0.36), 0.38, 0.72, col, pot_mat, 64, 0.035)
    cylinder('PROP_Plant_Stem', (-3.65, 2.55, 1.15), 0.055, 1.25, col, stem_mat, 32)
    for i in range(10):
        angle = math.radians(i * 137.5)
        z = 1.15 + (i % 5) * 0.22
        r = 0.34 + (i % 3) * 0.08
        x = -3.65 + math.cos(angle) * r
        y = 2.55 + math.sin(angle) * r
        bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, location=(x, y, z))
        leaf = bpy.context.object
        leaf.name = f'PROP_Plant_Leaf_{i:02d}'
        leaf.scale = (0.34, 0.12, 0.055)
        leaf.rotation_euler = (math.radians(18), math.radians(-8), angle)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to_collection(leaf, col)
        leaf.data.materials.append(leaf_mat)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 256)
    scene.render.film_transparent = False
    scene.world.color = (0.035, 0.035, 0.035)
    if scene.world and scene.world.use_nodes:
        bg = scene.world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value = (0.055, 0.055, 0.055, 1.0)
            bg.inputs['Strength'].default_value = 0.22

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    white = painted_white('MAT_Cyclorama')
    pedestal_mat = painted_white('MAT_Pedestal', (0.73, 0.72, 0.69, 1.0), 0.40)
    black = material_principled('MAT_NegativeFill', (0.004, 0.004, 0.005), 0.82)

    cyclorama(arch, white)
    cylinder('STAGE_Pedestal', (0.0, 0.0, 0.275), 1.75, 0.55, arch, pedestal_mat, 160, 0.045)
    anchor = empty('PRODUCT_ANCHOR', (0.0, 0.0, 1.40), guides)

    softbox('PROP_Softbox_L', -4.15, -0.6, 3.15, 3.15, 2.35, anchor, props, lights, 1450)
    softbox('PROP_Softbox_R', 4.35, -0.05, 3.05, 2.95, 2.10, anchor, props, lights, 980)
    box('PROP_Flag_L', (-3.05, 0.85, 2.15), (0.07, 1.65, 3.25), props, black, 0.02)
    box('PROP_Flag_R', (3.00, 1.20, 2.25), (0.07, 1.45, 3.10), props, black, 0.02)
    plant(props)

    top = area_light('LIGHT_Top', (0.0, 0.2, 5.65), 780, 3.4, (1.0, 0.95, 0.90), anchor, 'RECTANGLE', 2.2)
    move_to_collection(top, lights)
    rim = area_light('LIGHT_Back_Rim', (0.0, 3.3, 3.1), 520, 2.3, (1.0, 0.93, 0.86), anchor, 'RECTANGLE', 1.1)
    move_to_collection(rim, lights)

    cam = camera('CAM_Hero', (0.0, -10.5, 2.45), (0.0, 0.15, 1.35), 72.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 5.6

    scene.render.filepath = str(HERE / 'generated' / 'white_studio_v1.png')
    scene['scene_lab_id'] = 'white-studio-v1'
    scene['scene_lab_status'] = 'structural-builder'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'WHITE_STUDIO_READY {options.output}')
