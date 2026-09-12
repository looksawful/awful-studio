from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def collection(name: str):
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if col.name not in bpy.context.scene.collection.children:
        try:
            bpy.context.scene.collection.children.link(col)
        except Exception:
            pass
    return col


def move_to_collection(obj, col):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def add_bevel(obj, width=0.02, segments=3):
    mod = obj.modifiers.new('Bevel', 'BEVEL')
    mod.width = width
    mod.segments = segments
    return obj


def box(name, location, dimensions, col, material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, col)
    if bevel > 0:
        add_bevel(obj, bevel, 4)
    if material:
        obj.data.materials.append(material)
    return obj


def cylinder(name, location, radius, depth, col, material=None, vertices=128, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, col)
    if bevel > 0:
        add_bevel(obj, bevel, 4)
    if material:
        obj.data.materials.append(material)
    return obj


def plane(name, size, location, col, material=None):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, col)
    if material:
        obj.data.materials.append(material)
    return obj


def empty(name, location, col):
    obj = bpy.data.objects.new(name, None)
    obj.location = location
    obj.empty_display_type = 'SPHERE'
    obj.empty_display_size = 0.18
    col.objects.link(obj)
    return obj


def material_principled(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, ior=1.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['IOR'].default_value = ior
    for socket in ('Transmission Weight', 'Transmission'):
        if socket in bsdf.inputs:
            bsdf.inputs[socket].default_value = transmission
            break
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def concrete_material(name='MAT_Concrete', warm=False, polished=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 7.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.7
    fine = nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 180.0
    fine.inputs['Detail'].default_value = 2.0
    ramp = nodes.new('ShaderNodeValToRGB')
    c0 = (0.20, 0.19, 0.18, 1.0) if warm else (0.22, 0.23, 0.24, 1.0)
    c1 = (0.52, 0.50, 0.46, 1.0) if warm else (0.54, 0.55, 0.56, 1.0)
    ramp.color_ramp.elements[0].color = c0
    ramp.color_ramp.elements[1].color = c1
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.18 if not polished else 0.05
    bump.inputs['Distance'].default_value = 0.025
    bsdf.inputs['Roughness'].default_value = 0.22 if polished else 0.62
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def marble_material(name='MAT_Black_Marble'):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 2.6
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.8
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.36
    ramp.color_ramp.elements[0].color = (0.006, 0.008, 0.012, 1.0)
    ramp.color_ramp.elements[1].position = 0.63
    ramp.color_ramp.elements[1].color = (0.16, 0.18, 0.22, 1.0)
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 3.5
    wave.inputs['Distortion'].default_value = 8.0
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'SCREEN'
    mix.inputs['Fac'].default_value = 0.22
    mix.inputs[2].default_value = (0.38, 0.40, 0.44, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['Metallic'].default_value = 0.02
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs[1])
    links.new(wave.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def area_light(name, location, energy, size, color=(1.0, 1.0, 1.0), target=None, shape='RECTANGLE', size_y=None):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = shape
    data.size = size
    if shape == 'RECTANGLE' and size_y is not None:
        data.size_y = size_y
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    if target is not None:
        point_at(obj, target)
    return obj


def point_at(obj, target, track='-Z', up='Y'):
    target_vec = Vector(target) if not hasattr(target, 'matrix_world') else target.matrix_world.translation
    direction = target_vec - obj.location
    obj.rotation_euler = direction.to_track_quat(track, up).to_euler()
    return obj


def camera(name, location, target, lens=70.0, sensor=36.0):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = sensor
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    bpy.context.scene.camera = obj
    return obj


def configure_scene(resolution=(1920, 1080), samples=256, transparent=False):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if not hasattr(scene, 'cycles') else 'CYCLES'
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.max_bounces = 8
        scene.cycles.diffuse_bounces = 3
        scene.cycles.glossy_bounces = 5
        scene.cycles.transmission_bounces = 8
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    scene.render.film_transparent = transparent
    for transform in ('AgX', 'Khronos PBR Neutral'):
        try:
            scene.view_settings.view_transform = transform
            break
        except Exception:
            pass
    scene.view_settings.look = 'AgX - Medium High Contrast' if scene.view_settings.view_transform == 'AgX' else scene.view_settings.look
    return scene


def save_blend(path):
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return path
