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
    parser.add_argument('--output', default=str(HERE / 'generated' / 'white_studio_v2.blend'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def painted_white(name, base=(0.68, 0.68, 0.665, 1.0), roughness=0.48):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 145.0
    noise.inputs['Detail'].default_value = 2.4
    noise.inputs['Roughness'].default_value = 0.68
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.50, 0.50, 0.49, 1.0)
    ramp.color_ramp.elements[1].color = base
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.028
    bump.inputs['Distance'].default_value = 0.0009
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def emissive(name, color=(1.0, 0.955, 0.91), strength=1.15):
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


def cyclorama(col, mat):
    width = 14.0
    front_y = -7.2
    curve_start_y = 2.15
    radius = 2.55
    wall_top = 7.3
    profile = [(front_y, 0.0), (curve_start_y, 0.0)]
    for i in range(1, 121):
        t = i / 120.0
        angle = -math.pi * 0.5 + (math.pi * 0.5) * t
        profile.append((
            curve_start_y + radius * math.cos(angle),
            radius + radius * math.sin(angle),
        ))
    profile.append((curve_start_y + radius, wall_top))

    verts = []
    for x in (-width * 0.5, width * 0.5):
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
    return obj


def local_box(name, parent, loc, dims, col, material, bevel=0.0):
    obj = box(name, (0.0, 0.0, 0.0), dims, col, material, bevel)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = (0.0, 0.0, 0.0)
    return obj


def local_cylinder(name, parent, loc, radius, depth, col, material, vertices=64, bevel=0.0, rotation=(0.0, 0.0, 0.0)):
    obj = cylinder(name, (0.0, 0.0, 0.0), radius, depth, col, material, vertices, bevel)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rotation
    return obj


def tripod_stand(name, x, y, height, props, black, metal):
    cylinder(name + '_BaseHub', (x, y, 0.085), 0.105, 0.12, props, metal, 48, 0.012)
    for angle in (0.0, math.radians(120.0), math.radians(240.0)):
        length = 0.62
        cx = x + math.cos(angle) * length * 0.46
        cy = y + math.sin(angle) * length * 0.46
        leg = box(name + '_Leg', (cx, cy, 0.055), (length, 0.035, 0.032), props, black, 0.012)
        leg.rotation_euler.z = angle
    cylinder(name + '_LowerPole', (x, y, 0.93), 0.031, 1.68, props, metal, 40)
    cylinder(name + '_UpperPole', (x, y, 2.28), 0.024, 1.22, props, metal, 40)
    cylinder(name + '_CollarA', (x, y, 1.68), 0.050, 0.09, props, black, 48, 0.008)
    cylinder(name + '_CollarB', (x, y, 2.88), 0.046, 0.085, props, black, 48, 0.008)
    box(name + '_TopBracket', (x, y, height - 0.10), (0.34, 0.12, 0.10), props, black, 0.025)


def softbox_fixture(name, side, target, props, lights, black, metal, diffuser, energy):
    stand_x = side * 3.18
    head_x = side * 2.72
    y = 0.95
    head_z = 3.10
    tripod_stand(name + '_Stand', stand_x, y + 0.10, 3.12, props, black, metal)

    # Straight fixed boom connects the vertical stand to an independently aimed lamp head.
    boom_mid_x = (stand_x + head_x) * 0.5
    box(name + '_Boom', (boom_mid_x, y, 3.02), (abs(stand_x - head_x) + 0.18, 0.095, 0.095), props, metal, 0.022)

    root = empty(name + '_HeadRig', (head_x, y, head_z), props)
    root.empty_display_size = 0.08
    point_at(root, target, track='-Z', up='Y')

    # Rectangular softbox body. Local Z is depth; local Y stays visually vertical.
    local_box(name + '_Shell', root, (0.0, 0.0, 0.0), (1.22, 1.58, 0.30), props, black, 0.045)
    local_box(name + '_RearHousing', root, (0.0, 0.0, 0.22), (0.88, 1.08, 0.18), props, metal, 0.035)
    local_box(name + '_Diffuser', root, (0.0, 0.0, -0.165), (1.10, 1.44, 0.025), props, diffuser, 0.025)

    # Realistic yoke/pivots. They rotate with the head, not with the stand.
    local_box(name + '_YokeL', root, (-0.66, 0.0, 0.11), (0.055, 0.13, 0.92), props, black, 0.018)
    local_box(name + '_YokeR', root, (0.66, 0.0, 0.11), (0.055, 0.13, 0.92), props, black, 0.018)
    local_box(name + '_YokeBack', root, (0.0, 0.0, 0.48), (1.36, 0.13, 0.055), props, black, 0.018)
    local_cylinder(name + '_PivotL', root, (-0.68, 0.0, 0.0), 0.075, 0.11, props, metal, 48, 0.008, rotation=(0.0, math.radians(90.0), 0.0))
    local_cylinder(name + '_PivotR', root, (0.68, 0.0, 0.0), 0.075, 0.11, props, metal, 48, 0.008, rotation=(0.0, math.radians(90.0), 0.0))

    data = bpy.data.lights.new(name + '_Light', 'AREA')
    data.energy = energy
    data.color = (1.0, 0.93, 0.86)
    data.shape = 'RECTANGLE'
    data.size = 1.05
    data.size_y = 1.38
    light = bpy.data.objects.new(name + '_Light', data)
    lights.objects.link(light)
    light.parent = root
    light.location = (0.0, 0.0, -0.19)
    light.rotation_euler = (0.0, 0.0, 0.0)


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 320)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.16

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    white = painted_white('MAT_Cyclorama')
    pedestal_mat = painted_white('MAT_Pedestal', (0.58, 0.57, 0.55, 1.0), 0.40)
    black = material_principled('MAT_Studio_Black', (0.005, 0.005, 0.006), 0.70)
    metal = material_principled('MAT_Studio_Metal', (0.08, 0.085, 0.095), 0.24, 0.82)
    diffuser = emissive('MAT_Diffuser')

    cyclorama(arch, white)
    cylinder('STAGE_Pedestal', (0.0, 0.0, 0.26), 1.62, 0.52, arch, pedestal_mat, 192, 0.042)
    anchor = empty('PRODUCT_ANCHOR', (0.0, 0.0, 1.34), guides)

    softbox_fixture('PROP_KeyFixture', -1.0, anchor, props, lights, black, metal, diffuser, 700)
    softbox_fixture('PROP_FillFixture', 1.0, anchor, props, lights, black, metal, diffuser, 500)

    top = area_light('LIGHT_Top', (0.0, 0.20, 5.85), 255, 3.4, (1.0, 0.96, 0.91), anchor, 'RECTANGLE', 2.3)
    rim = area_light('LIGHT_Rim', (0.0, 3.75, 3.05), 135, 2.2, (1.0, 0.90, 0.82), anchor, 'RECTANGLE', 1.0)
    front = area_light('LIGHT_Front_Bounce', (0.0, -3.8, 2.4), 125, 4.2, (0.94, 0.96, 1.0), anchor, 'RECTANGLE', 3.2)
    for light in (top, rim, front):
        move_to_collection(light, lights)

    for side in (-1.0, 1.0):
        flag = box(
            'PROP_Flag_L' if side < 0 else 'PROP_Flag_R',
            (side * 2.95, 1.70, 2.35), (0.06, 1.10, 2.75), props, black, 0.018,
        )
        flag.visible_camera = False

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.022, 0.022, 0.024, 1.0)
    bg.inputs['Strength'].default_value = 0.11

    cam = camera('CAM_Hero', (0.0, -10.15, 2.18), (0.0, 0.28, 1.18), 58.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 5.0
    cam.data.shift_x = 0.0
    cam.data.shift_y = 0.0

    scene.render.filepath = str(HERE / 'generated' / 'white_studio_v2.png')
    scene['scene_lab_id'] = 'white-studio-v2'
    scene['scene_lab_status'] = 'straight-softbox-rigs'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'WHITE_STUDIO_V2_READY {options.output}')
