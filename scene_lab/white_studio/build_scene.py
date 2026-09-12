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


def painted_white(name, base=(0.62, 0.62, 0.60, 1.0), roughness=0.50):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 125.0
    noise.inputs['Detail'].default_value = 2.5
    noise.inputs['Roughness'].default_value = 0.70
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.44, 0.44, 0.43, 1.0)
    ramp.color_ramp.elements[1].color = base
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.035
    bump.inputs['Distance'].default_value = 0.0010
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def emissive(name, color=(1.0, 0.95, 0.90), strength=0.8):
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
    front_y = -7.0
    curve_start_y = 2.20
    radius = 2.40
    wall_top = 7.20

    profile = [(front_y, 0.0), (curve_start_y, 0.0)]
    for i in range(1, 97):
        t = i / 96.0
        angle = -math.pi * 0.5 + (math.pi * 0.5) * t
        y = curve_start_y + radius * math.cos(angle)
        z = radius + radius * math.sin(angle)
        profile.append((y, z))
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


def add_stand(prefix, x, y, height, props, black):
    cylinder(prefix + '_Pole', (x, y, height * 0.48), 0.030, height * 0.92, props, black, 32)
    cylinder(prefix + '_Base', (x, y, 0.045), 0.31, 0.050, props, black, 48)
    for angle in (0.0, math.radians(120.0), math.radians(240.0)):
        leg = box(
            prefix + '_Leg',
            (x + math.cos(angle) * 0.24, y + math.sin(angle) * 0.24, 0.065),
            (0.43, 0.030, 0.030), props, black, 0.010,
        )
        leg.rotation_euler.z = angle


def octabox(name, location, radius, depth, target, props, lights, black, diffuser, energy):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=depth, location=location)
    shell = bpy.context.object
    shell.name = name + '_Shell'
    move_to_collection(shell, props)
    shell.data.materials.append(black)
    point_at(shell, target, track='Z', up='Y')

    direction = (Vector(target.matrix_world.translation) - shell.location).normalized()
    face_loc = shell.location + direction * (depth * 0.52)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius * 0.91, depth=0.022, location=face_loc)
    face = bpy.context.object
    face.name = name + '_Diffuser'
    move_to_collection(face, props)
    face.data.materials.append(diffuser)
    point_at(face, target, track='Z', up='Y')

    light = area_light(
        name + '_Light', tuple(face_loc), energy, radius * 1.40,
        (1.0, 0.93, 0.86), target,
    )
    move_to_collection(light, lights)
    add_stand(name + '_Stand', location[0], location[1] + 0.10, location[2], props, black)
    return shell, face


def build():
    clear_scene()
    scene = configure_scene((1920, 1200), 256)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.45

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    white = painted_white('MAT_Cyclorama')
    pedestal_mat = painted_white('MAT_Pedestal', (0.52, 0.51, 0.49, 1.0), 0.42)
    black = material_principled('MAT_Studio_Black', (0.004, 0.004, 0.005), 0.76)
    diffuser = emissive('MAT_Diffuser')

    cyclorama(arch, white)
    cylinder('STAGE_Pedestal', (0.0, 0.0, 0.25), 1.55, 0.50, arch, pedestal_mat, 192, 0.035)
    anchor = empty('PRODUCT_ANCHOR', (0.0, 0.0, 1.30), guides)

    # Bilateral set. Matching fixtures remove accidental visual tilt.
    for side in (-1.0, 1.0):
        x = side * 3.65
        octabox(
            'PROP_Octabox_L' if side < 0 else 'PROP_Octabox_R',
            (x, 1.65, 3.15), 0.94, 0.34, anchor,
            props, lights, black, diffuser, 360,
        )
        flag = box(
            'PROP_Flag_L' if side < 0 else 'PROP_Flag_R',
            (side * 3.15, 1.90, 2.25), (0.06, 1.20, 2.75), props, black, 0.018,
        )
        flag.visible_camera = False

    key = area_light('LIGHT_Key', (-2.80, -1.40, 3.20), 310, 2.8, (1.0, 0.91, 0.83), anchor, 'RECTANGLE', 2.1)
    fill = area_light('LIGHT_Fill', (2.80, -1.40, 3.20), 250, 2.8, (0.94, 0.96, 1.0), anchor, 'RECTANGLE', 2.1)
    top = area_light('LIGHT_Top', (0.0, 0.25, 5.65), 240, 3.2, (1.0, 0.95, 0.89), anchor, 'RECTANGLE', 2.0)
    rim = area_light('LIGHT_Rim', (0.0, 3.65, 2.90), 135, 2.0, (1.0, 0.90, 0.80), anchor, 'RECTANGLE', 0.90)
    for light in (key, fill, top, rim):
        move_to_collection(light, lights)

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.018, 0.018, 0.020, 1.0)
    bg.inputs['Strength'].default_value = 0.085

    # Long lens + centered target keeps verticals and bilateral staging visually straight.
    cam = camera('CAM_Hero', (0.0, -14.2, 2.05), (0.0, 0.35, 1.15), 78.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 5.6
    cam.data.shift_x = 0.0
    cam.data.shift_y = 0.0

    scene.render.filepath = str(HERE / 'generated' / 'white_studio_v1.png')
    scene['scene_lab_id'] = 'white-studio-v1'
    scene['scene_lab_status'] = 'geometry-rebuild-1'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'WHITE_STUDIO_READY {options.output}')
