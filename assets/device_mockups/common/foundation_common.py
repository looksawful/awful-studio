import math
import os
import bpy
from mathutils import Vector

MM = 0.001


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def setup_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.8
    scene.world.color = (0.035, 0.035, 0.035)


def make_collection(name):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to(obj, collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(name, base, metallic=0.0, roughness=0.35):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*base, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def rounded_outline(width, height, radius, segments=12):
    radius = min(radius, width * 0.5, height * 0.5)
    half_w, half_h = width * 0.5, height * 0.5
    corners = [
        (half_w - radius, half_h - radius, 0.0),
        (-half_w + radius, half_h - radius, 90.0),
        (-half_w + radius, -half_h + radius, 180.0),
        (half_w - radius, -half_h + radius, 270.0),
    ]
    points = []
    for cx, cy, start in corners:
        for step in range(segments + 1):
            angle = math.radians(start + 90.0 * step / segments)
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return points


def rounded_prism(name, width, height, depth, radius, material, collection, axis="Y", location=(0, 0, 0), edge_bevel=0.0):
    outline = rounded_outline(width, height, radius)
    count = len(outline)
    verts = []
    if axis == "Y":
        verts += [(x, -depth * 0.5, y) for x, y in outline]
        verts += [(x, depth * 0.5, y) for x, y in outline]
    else:
        verts += [(x, y, -depth * 0.5) for x, y in outline]
        verts += [(x, y, depth * 0.5) for x, y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, count + j, count + i))
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    if material:
        obj.data.materials.append(material)
    if edge_bevel > 0:
        modifier = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
        modifier.width = edge_bevel
        modifier.segments = 4
        modifier.limit_method = "ANGLE"
    return obj


def rounded_cube(name, dimensions, bevel, material, collection, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    move_to(obj, collection)
    if bevel > 0:
        modifier = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
        modifier.width = min(bevel, min(dimensions) * 0.49)
        modifier.segments = 4
        modifier.limit_method = "ANGLE"
    return obj


def cylinder(name, radius, depth, material, collection, location=(0, 0, 0), axis="Y", vertices=64):
    rotation = (math.radians(90), 0, 0) if axis == "Y" else (0, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    move_to(obj, collection)
    bevel = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
    bevel.width = min(0.00018, depth * 0.2)
    bevel.segments = 3
    return obj


def empty(name, collection, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.02
    obj.location = location
    collection.objects.link(obj)
    return obj


def add_camera(name, location, target, ortho_scale, collection):
    camera_data = bpy.data.cameras.new(name)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = ortho_scale
    camera = bpy.data.objects.new(name, camera_data)
    camera.location = location
    direction = Vector(target) - Vector(location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(camera)
    return camera


def add_area_light(name, location, energy, size, collection, target=(0, 0, 0)):
    light_data = bpy.data.lights.new(name=name, type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new(name, light_data)
    light.location = location
    light.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(light)
    return light


def add_preview_rig(scale=0.3):
    collection = make_collection("_PREVIEW_RIG")
    add_area_light("KEY", (scale, -scale, scale), 180, scale * 0.8, collection)
    add_area_light("FILL", (-scale, -scale * 0.5, scale * 0.4), 90, scale * 0.6, collection)
    add_area_light("RIM", (0, scale, scale * 0.7), 140, scale * 0.5, collection)
    return collection


def render_camera(camera, path):
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)


def save_blend(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("AWFUL_STUDIO_SAVED", path)


def write_blueprint_svg(path, label, width_mm, height_mm, depth_mm, radius_mm):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    canvas_w, canvas_h = 1600, 1000
    scale = min(900 / height_mm, 520 / width_mm)
    body_w, body_h = width_mm * scale, height_mm * scale
    x, y = 160, 110
    side_x = 1000
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">
<rect width="100%" height="100%" fill="#f7f7f4"/>
<g fill="none" stroke="#111" stroke-width="2">
<rect x="{x}" y="{y}" width="{body_w}" height="{body_h}" rx="{radius_mm*scale}"/>
<rect x="{side_x}" y="{y}" width="{depth_mm*scale*8}" height="{body_h}" rx="12"/>
<line x1="{x}" y1="{y+body_h+55}" x2="{x+body_w}" y2="{y+body_h+55}"/>
<line x1="{x-55}" y1="{y}" x2="{x-55}" y2="{y+body_h}"/>
</g>
<g font-family="Arial, sans-serif" fill="#111"><text x="80" y="65" font-size="34" font-weight="700">{label} / BLOCKOUT BLUEPRINT</text>
<text x="{x+body_w/2-60}" y="{y+body_h+95}" font-size="24">{width_mm:.2f} mm</text>
<text x="{x-145}" y="{y+body_h/2}" font-size="24" transform="rotate(-90 {x-145},{y+body_h/2})">{height_mm:.2f} mm</text>
<text x="{side_x}" y="{y+body_h+55}" font-size="24">depth {depth_mm:.2f} mm</text>
<text x="80" y="950" font-size="20">AWFUL STUDIO · metric source of truth · V = verified envelope</text></g></svg>'''
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(svg)


def make_glass_material(name, tint=(0.02, 0.025, 0.035), roughness=0.08, transmission=0.92, ior=1.46):
    material = make_material(name, tint, 0.0, roughness)
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Coat Weight"].default_value = 0.18
    bsdf.inputs["Coat Roughness"].default_value = max(0.02, roughness * 0.5)
    return material


def make_screen_material(name="MAT_SCREEN_CONTENT", color=(0.006, 0.008, 0.012), emission=0.08):
    material = make_material(name, color, 0.0, 0.18)
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission
    return material
