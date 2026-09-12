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


def emissive(name, color, strength=1.1):
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
    width = 12.0
    front_y = -6.6
    curve_y = 2.55
    radius = 2.9
    top_z = 6.45
    profile = [(front_y, 0.0), (curve_y, 0.0)]
    for i in range(1, 81):
        t = i / 80.0
        a = math.radians(-90.0 + 90.0 * t)
        profile.append((curve_y + radius * math.cos(a), radius + radius * math.sin(a)))
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


def add_stand(prefix, x, y, z, props, black):
    cylinder(prefix+'_Pole', (x, y, z*0.47), 0.032, z*0.90, props, black, 32)
    cylinder(prefix+'_Base', (x, y, 0.055), 0.36, 0.055, props, black, 48)
    for angle in (0.0, math.radians(120), math.radians(240)):
        leg = box(prefix+'_Leg', (x + math.cos(angle)*0.28, y + math.sin(angle)*0.28, 0.07), (0.50, 0.035, 0.035), props, black, 0.012)
        leg.rotation_euler.z = angle


def octabox(name, location, radius, depth, target, props, lights, black, diffuser, energy):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=depth, location=location)
    shell = bpy.context.object
    shell.name = name+'_Shell'
    move_to_collection(shell, props)
    shell.data.materials.append(black)
    point_at(shell, target, track='Z', up='Y')
    direction = (Vector(target.matrix_world.translation) - shell.location).normalized()
    face_loc = shell.location + direction * (depth * 0.54)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius*0.91, depth=0.024, location=face_loc)
    face = bpy.context.object
    face.name = name+'_Diffuser'
    move_to_collection(face, props)
    face.data.materials.append(diffuser)
    point_at(face, target, track='Z', up='Y')
    light = area_light(name+'_Light', tuple(face_loc), energy, radius*1.45, (1.0,0.90,0.80), target)
    move_to_collection(light, lights)
    add_stand(name+'_Stand', location[0], location[1]+0.12, location[2], props, black)
    return shell, face


def stripbox(name, location, dimensions, target, props, lights, black, diffuser, energy):
    x, y, z = location
    shell = box(name+'_Shell', location, dimensions, props, black, 0.055)
    point_at(shell, target, track='X', up='Z')
    panel = box(name+'_Diffuser', (x*0.986, y, z), (0.022, dimensions[1]*0.90, dimensions[2]*0.90), props, diffuser, 0.025)
    point_at(panel, target, track='X', up='Z')
    light = area_light(name+'_Light', (x*0.96,y,z), energy, dimensions[2]*0.80, (1.0,0.92,0.84), target, 'RECTANGLE', dimensions[1]*0.76)
    move_to_collection(light, lights)
    add_stand(name+'_Stand', x, y+0.12, z, props, black)
    return shell, panel


def plant(col):
    pot_mat = material_principled('MAT_Pot', (0.050,0.045,0.040), 0.58)
    leaf_mat = material_principled('MAT_Leaves', (0.020,0.105,0.038), 0.50)
    stem_mat = material_principled('MAT_Stem', (0.065,0.040,0.022), 0.64)
    cx, cy = -2.80, 3.25
    cylinder('PROP_Plant_Pot', (cx, cy, 0.28), 0.31, 0.56, col, pot_mat, 64, 0.035)
    for j, dx in enumerate((-0.09, 0.07, 0.15)):
        cylinder(f'PROP_Plant_Stem_{j}', (cx+dx, cy, 0.90+j*0.05), 0.032, 1.22, col, stem_mat, 24)
    for i in range(18):
        angle = math.radians(i*137.5)
        z = 0.92 + (i%7)*0.15
        r = 0.22 + (i%4)*0.07
        x = cx + math.cos(angle)*r
        y = cy + math.sin(angle)*r*0.72
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(x,y,z))
        leaf = bpy.context.object
        leaf.name = f'PROP_Plant_Leaf_{i:02d}'
        leaf.scale = (0.26 + 0.035*(i%3), 0.075, 0.035)
        leaf.rotation_euler = (math.radians(12 + (i%3)*5), math.radians(-8), angle)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        move_to_collection(leaf, col)
        leaf.data.materials.append(leaf_mat)


def build():
    clear_scene()
    scene = configure_scene((1920,1200), 256)
    scene.render.film_transparent = False
    scene.view_settings.exposure = -0.55

    arch = collection('SCENE_ARCH')
    props = collection('SCENE_PROPS')
    lights = collection('SCENE_LIGHTS')
    guides = collection('SCENE_GUIDES')

    white = painted_white('MAT_Cyclorama')
    pedestal_mat = painted_white('MAT_Pedestal', (0.50,0.49,0.46,1.0), 0.44)
    black = material_principled('MAT_Studio_Black', (0.003,0.003,0.004), 0.78)
    diffuser = emissive('MAT_Diffuser', (1.0,0.94,0.88), 1.05)

    cyclorama(arch, white)
    cylinder('STAGE_Pedestal', (0.0,0.0,0.23), 1.58, 0.46, arch, pedestal_mat, 160, 0.04)
    anchor = empty('PRODUCT_ANCHOR', (0.0,0.0,1.30), guides)

    octabox('PROP_Octabox_L', (-3.22,1.60,3.15), 1.02, 0.40, anchor, props, lights, black, diffuser, 470)
    stripbox('PROP_Stripbox_R', (3.35,1.82,3.05), (0.18,1.50,2.70), anchor, props, lights, black, diffuser, 310)
    plant(props)

    flag_l = box('PROP_Flag_L', (-3.55,1.55,2.2), (0.07,1.35,2.95), props, black, 0.02)
    flag_r = box('PROP_Flag_R', (3.60,1.65,2.2), (0.07,1.30,2.90), props, black, 0.02)
    flag_l.visible_camera = False
    flag_r.visible_camera = False

    key = area_light('LIGHT_Key_Hidden', (-3.35,-2.30,3.15), 410, 2.8, (1.0,0.91,0.82), anchor, 'RECTANGLE', 2.0)
    move_to_collection(key, lights)
    fill = area_light('LIGHT_Fill_Hidden', (3.10,-1.50,2.75), 180, 2.6, (0.92,0.95,1.0), anchor, 'RECTANGLE', 2.0)
    move_to_collection(fill, lights)
    top = area_light('LIGHT_Top', (0.0,0.3,5.7), 260, 3.4, (1.0,0.94,0.86), anchor, 'RECTANGLE', 2.1)
    move_to_collection(top, lights)
    rim = area_light('LIGHT_Back_Rim', (0.0,3.9,3.0), 160, 2.2, (1.0,0.88,0.75), anchor, 'RECTANGLE', 0.95)
    move_to_collection(rim, lights)

    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.020,0.020,0.023,1.0)
    bg.inputs['Strength'].default_value = 0.10

    cam = camera('CAM_Hero', (0.0,-11.9,2.30), (0.0,0.35,1.20), 57.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = anchor
    cam.data.dof.aperture_fstop = 2.8

    scene.render.filepath = str(HERE/'generated'/'white_studio_v1.png')
    scene['scene_lab_id'] = 'white-studio-v1'
    scene['scene_lab_status'] = 'visual-pass-4'
    return scene


if __name__ == '__main__':
    options = args()
    build()
    save_blend(options.output)
    print(f'WHITE_STUDIO_READY {options.output}')
