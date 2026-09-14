import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

MM = 0.001
ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "spec.json").read_text(encoding="utf-8"))
OUT_BLEND = ROOT / "generated" / "studio_rig_v01.blend"
PREVIEW_DIR = ROOT / "previews"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights):
        for block in list(blocks):
            if block.users == 0:
                blocks.remove(block)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def setup_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = SPEC["preview"]["resolution"][0]
    scene.render.resolution_y = SPEC["preview"]["resolution"][1]
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.25
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    return scene


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def make_material(name, base, metallic=0.0, roughness=0.4,
                  noise_scale=None, bump_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if noise_scale and bump_strength:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.55
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.00025
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def add_empty(name, col, location=(0, 0, 0), size=0.04):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = size
    obj.location = location
    col.objects.link(obj)
    return obj


def add_cube(name, dims, loc, mat, col, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to(obj, col)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
        mod.width = min(bevel, min(dims) * 0.45)
        mod.segments = 4
    obj.parent = parent
    return obj


def add_cylinder(name, radius, depth, loc, mat, col,
                 axis="Z", vertices=64, parent=None, bevel=0.001):
    rot = (0, 0, 0)
    if axis == "Y":
        rot = (math.radians(90), 0, 0)
    elif axis == "X":
        rot = (0, math.radians(90), 0)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    move_to(obj, col)
    if mat:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if bevel:
        mod = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
        mod.width = min(bevel, radius * 0.25, depth * 0.2)
        mod.segments = 3
    obj.parent = parent
    return obj


def add_torus(name, major_radius, minor_radius, loc, rot, mat, col, parent=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, minor_radius=minor_radius,
        major_segments=96, minor_segments=16, location=loc, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    move_to(obj, col)
    if mat:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.parent = parent
    return obj


def add_cone_shell(name, r_back, r_front, depth, loc, mat, col, parent=None):
    bpy.ops.mesh.primitive_cone_add(
        vertices=128, radius1=r_back, radius2=r_front, depth=depth,
        end_fill_type="NOTHING", location=loc,
        rotation=(math.radians(-90), 0, 0)
    )
    obj = bpy.context.object
    obj.name = name
    move_to(obj, col)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    solid = obj.modifiers.new("SHELL_THICKNESS", "SOLIDIFY")
    solid.thickness = 0.0012
    solid.offset = 0.0
    bevel = obj.modifiers.new("RIM_BEVEL", "BEVEL")
    bevel.width = 0.0008
    bevel.segments = 3
    obj.parent = parent
    return obj



def add_profile_shell(name, profile, loc, mat, col, parent=None, segments=128, thickness=0.0012):
    verts, faces = [], []
    count = len(profile)
    for seg in range(segments):
        angle = math.tau * seg / segments
        c, s = math.cos(angle), math.sin(angle)
        for y, radius in profile:
            verts.append((radius * c, y, radius * s))
    for seg in range(segments):
        nxt = (seg + 1) % segments
        for idx in range(count - 1):
            a = seg * count + idx
            b = nxt * count + idx
            faces.append((a, b, b + 1, a + 1))
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    solid = obj.modifiers.new("SHELL_THICKNESS", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0.0
    bevel = obj.modifiers.new("RIM_BEVEL", "BEVEL")
    bevel.width = 0.0007
    bevel.segments = 3
    obj.parent = parent
    return obj

def add_sphere(name, radius, loc, scale, mat, col, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, radius=radius, location=loc
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to(obj, col)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.parent = parent
    return obj


def rod_between(name, a, b, radius, mat, col, parent=None, vertices=48):
    a = Vector(a)
    b = Vector(b)
    delta = b - a
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=delta.length, location=mid
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    move_to(obj, col)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    bevel = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
    bevel.width = min(0.001, radius * 0.15)
    bevel.segments = 3
    obj.parent = parent
    return obj


def build_materials():
    return {
        "chrome": make_material("MAT_CHROME", (0.42, 0.46, 0.50), 0.92, 0.13, 70, 0.025),
        "black_metal": make_material("MAT_BLACK_POWDER", (0.025, 0.028, 0.032), 0.48, 0.31, 55, 0.035),
        "black_plastic": make_material("MAT_BLACK_PLASTIC", (0.018, 0.020, 0.023), 0.0, 0.42, 110, 0.045),
        "silver": make_material("MAT_REFLECTOR_SILVER", (0.72, 0.76, 0.79), 0.94, 0.10, 180, 0.018),
        "aluminum": make_material("MAT_ALUMINUM", (0.34, 0.37, 0.40), 0.86, 0.22, 90, 0.025),
        "rubber": make_material("MAT_RUBBER", (0.012, 0.014, 0.016), 0.0, 0.68, 95, 0.055),
        "fabric": make_material("MAT_SANDBAG_FABRIC", (0.025, 0.027, 0.029), 0.0, 0.86, 220, 0.11),
        "label": make_material("MAT_LABEL_WHITE", (0.82, 0.82, 0.80), 0.0, 0.44),
    }


def tag_root(root, asset_id, identity_class):
    root["awful_asset_id"] = asset_id
    root["awful_identity_class"] = identity_class
    root["awful_schema_version"] = 1
    return root


def build_cstand(mats, sem):
    col = collection("AS_SUPPORT_CSTAND_01")
    root = tag_root(add_empty("ROOT_SUPPORT_CSTAND", col),
                    "AS_SUPPORT_CSTAND_01", "REPRESENTATIVE_STANDARD")
    floor = add_empty("FLOOR_CONTACT", sem, (0, 0, 0), 0.06)
    floor.parent = root
    # Turtle base with staggered folding legs.
    add_cylinder("CSTAND_BASE_HUB_LOW", 0.043, 0.048, (0, 0, 0.040), mats["black_metal"], col, parent=root)
    add_cylinder("CSTAND_BASE_HUB_HIGH", 0.035, 0.052, (0, 0, 0.082), mats["chrome"], col, parent=root)
    leg_data = ((5, 0.60, 0.030), (125, 0.54, 0.050), (245, 0.48, 0.070))
    for idx, (angle_deg, length, z) in enumerate(leg_data, start=1):
        angle = math.radians(angle_deg)
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        start = radial * 0.048 + Vector((0, 0, z))
        end = radial * length + Vector((0, 0, 0.035))
        hinge = start + radial * 0.025
        add_cube(f"CSTAND_LEG_HINGE_{idx}", (0.060, 0.038, 0.025), hinge, mats["black_metal"], col, 0.006, root)
        rod_between(f"CSTAND_LEG_{idx}", start + radial * 0.035, end, 0.0115, mats["chrome"], col, root)
        add_cylinder(f"CSTAND_FOOT_{idx}", 0.017, 0.058, (end.x, end.y, 0.029), mats["rubber"], col, axis="Z", parent=root)
    # Three telescoping risers with decreasing diameters.
    add_cylinder("CSTAND_RISER_01", 0.0175, 0.700, (0, 0, 0.445), mats["chrome"], col, parent=root)
    add_cylinder("CSTAND_RISER_02", 0.0145, 0.590, (0, 0, 1.070), mats["chrome"], col, parent=root)
    add_cylinder("CSTAND_RISER_03", 0.0115, 0.355, (0, 0, 1.535), mats["chrome"], col, parent=root)
    # Riser collars and T-handle knobs.
    for idx, z in enumerate((0.785, 1.365), start=1):
        add_cylinder(f"CSTAND_COLLAR_{idx}", 0.027, 0.046, (0, 0, z), mats["black_metal"], col, parent=root)
        rod_between(f"CSTAND_KNOB_STEM_{idx}", (0.025, 0, z), (0.070, 0, z), 0.0048, mats["black_metal"], col, root, vertices=32)
        add_cylinder(f"CSTAND_KNOB_{idx}", 0.0135, 0.022, (0.082, 0, z), mats["black_plastic"], col, axis="X", parent=root)
        rod_between(f"CSTAND_TBAR_{idx}", (0.082, -0.022, z), (0.082, 0.022, z), 0.0045, mats["black_metal"], col, root, vertices=24)
    # Top grip head, rosette faces and baby pin.
    add_cylinder("CSTAND_TOP_GRIP_BODY", 0.034, 0.034, (0, 0, 1.695), mats["black_metal"], col, parent=root)
    add_cylinder("CSTAND_TOP_GRIP_FACE_L", 0.029, 0.010, (-0.021, 0, 1.695), mats["aluminum"], col, axis="X", parent=root)
    add_cylinder("CSTAND_TOP_GRIP_FACE_R", 0.029, 0.010, (0.021, 0, 1.695), mats["aluminum"], col, axis="X", parent=root)
    rod_between("CSTAND_TOP_HANDLE_STEM", (0.032, 0, 1.695), (0.085, 0, 1.695), 0.0050, mats["black_metal"], col, root, vertices=32)
    add_cylinder("CSTAND_TOP_HANDLE", 0.014, 0.024, (0.097, 0, 1.695), mats["black_plastic"], col, axis="X", parent=root)
    rod_between("CSTAND_TOP_TBAR", (0.097, -0.024, 1.695), (0.097, 0.024, 1.695), 0.0045, mats["black_metal"], col, root, vertices=24)
    add_cylinder("CSTAND_BABY_PIN", 0.008, 0.055, (0, 0, 1.7225), mats["chrome"], col, parent=root, bevel=0.0006)
    mount = add_empty("MOUNT_SUPPORT", sem, (0, 0, 1.750), 0.05)
    mount.parent = root
    return root, mount


def build_d1(mats, sem, support_mount):
    col = collection("AS_FIX_PROFOTO_D1_500")
    root = tag_root(add_empty("ROOT_FIX_PROFOTO_D1_500", col, support_mount.location),
                    "AS_FIX_PROFOTO_D1_500", "VERIFIED_MODEL")
    root.location = (0, 0, 0)
    z = 1.835
    reference = add_cube("D1_REFERENCE_ENVELOPE", (0.130, 0.300, 0.170), (0, 0, z), None, col, 0.0, root)
    reference.display_type = "WIRE"
    reference.hide_render = True
    reference.hide_viewport = True
    add_cylinder("D1_MAIN_SHELL", 0.057, 0.190, (0, -0.015, z), mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0012)
    add_cylinder("D1_REAR_RING", 0.065, 0.034, (0, -0.132, z), mats["black_metal"], col, axis="Y", parent=root, bevel=0.0010)
    add_cylinder("D1_FRONT_RING", 0.065, 0.036, (0, 0.088, z), mats["black_metal"], col, axis="Y", parent=root, bevel=0.0010)
    add_cylinder("D1_FRONT_NECK", 0.052, 0.026, (0, 0.119, z), mats["black_metal"], col, axis="Y", parent=root, bevel=0.0008)
    add_cylinder("D1_FRONT_BAYONET", 0.048, 0.018, (0, 0.141, z), mats["aluminum"], col, axis="Y", parent=root, bevel=0.0006)
    add_torus("D1_LOCK_RING", 0.050, 0.004, (0, 0.146, z), (math.radians(90), 0, 0), mats["black_metal"], col, root)
    add_cylinder("D1_REAR_PANEL", 0.052, 0.010, (0, -0.145, z), mats["black_metal"], col, axis="Y", parent=root, bevel=0.0004)
    add_cube("D1_DISPLAY", (0.050, 0.006, 0.024), (0, -0.151, z + 0.024), mats["label"], col, 0.0025, root)
    add_cylinder("D1_REAR_DIAL", 0.017, 0.012, (0.027, -0.151, z - 0.021), mats["black_plastic"], col, axis="Y", parent=root)
    for i, x in enumerate((-0.034, -0.018, -0.002, 0.014), start=1):
        add_cube(f"D1_REAR_BUTTON_{i}", (0.009, 0.005, 0.007), (x, -0.151, z - 0.025), mats["black_plastic"], col, 0.0016, root)
    for side_y in (-0.100, 0.072):
        for idx in range(12):
            a = math.tau * idx / 12.0
            x = math.cos(a) * 0.058
            zz = z + math.sin(a) * 0.058
            slot = add_cube(f"D1_VENT_{'R' if side_y < 0 else 'F'}_{idx:02d}", (0.006, 0.014, 0.017), (x, side_y, zz), mats["black_metal"], col, 0.0010, root)
            slot.rotation_euler.y = -a
    rod_between("D1_BRACKET_LEFT", (-0.056, -0.020, z - 0.010), (-0.056, -0.020, z - 0.060), 0.0065, mats["black_metal"], col, root)
    rod_between("D1_BRACKET_RIGHT", (0.056, -0.020, z - 0.010), (0.056, -0.020, z - 0.060), 0.0065, mats["black_metal"], col, root)
    rod_between("D1_BRACKET_BOTTOM", (-0.056, -0.020, z - 0.060), (0.056, -0.020, z - 0.060), 0.0075, mats["black_metal"], col, root)
    add_cylinder("D1_TILT_PIVOT_L", 0.021, 0.018, (-0.066, -0.020, z - 0.012), mats["black_metal"], col, axis="X", parent=root)
    add_cylinder("D1_TILT_PIVOT_R", 0.021, 0.018, (0.066, -0.020, z - 0.012), mats["black_metal"], col, axis="X", parent=root)
    add_cylinder("D1_TILT_KNOB", 0.018, 0.028, (0.086, -0.020, z - 0.012), mats["black_plastic"], col, axis="X", parent=root)
    add_cylinder("D1_STAND_SOCKET", 0.015, 0.050, (0, -0.020, z - 0.060), mats["black_metal"], col, parent=root, bevel=0.0007)
    rod_between("D1_HANDLE_LEFT", (-0.040, -0.075, z + 0.055), (-0.040, -0.105, z + 0.085), 0.006, mats["black_metal"], col, root)
    rod_between("D1_HANDLE_RIGHT", (0.040, -0.075, z + 0.055), (0.040, -0.105, z + 0.085), 0.006, mats["black_metal"], col, root)
    rod_between("D1_HANDLE_TOP", (-0.040, -0.105, z + 0.085), (0.040, -0.105, z + 0.085), 0.007, mats["black_metal"], col, root)
    mount_fixture = add_empty("MOUNT_FIXTURE", sem, (0, -0.020, z - 0.085), 0.045)
    mount_fixture.parent = root
    mount_modifier = add_empty("MOUNT_MODIFIER", sem, (0, 0.146, z), 0.045)
    mount_modifier.parent = root
    emitter = add_empty("EMITTER_ORIGIN", sem, (0, 0.154, z), 0.035)
    emitter.parent = root
    target = add_empty("LIGHT_TARGET", sem, (0, 2.5, 1.55), 0.08)
    light_data = bpy.data.lights.new("LIGHT_D1_NATIVE", type="AREA")
    light_data.shape = "DISK"
    light_data.size = 0.085
    light_data.energy = 0.0
    light_obj = bpy.data.objects.new("LIGHT_D1_NATIVE", light_data)
    light_obj.location = emitter.location
    light_obj.rotation_euler = (math.radians(90), 0, 0)
    col.objects.link(light_obj)
    light_obj.parent = root
    return root, mount_modifier


def build_magnum(mats, sem, mount_modifier):
    col = collection("AS_MOD_PROFOTO_MAGNUM")
    root = tag_root(add_empty("ROOT_MOD_PROFOTO_MAGNUM", col),
                    "AS_MOD_PROFOTO_MAGNUM", "VERIFIED_MODEL")
    back_y = mount_modifier.location.y + 0.004
    depth = SPEC["magnum_100624"]["depth_mm"] * MM
    profile = [
        (0.000, 0.054),
        (0.020, 0.058),
        (0.050, 0.065),
        (0.085, 0.077),
        (0.125, 0.096),
        (0.165, 0.119),
        (0.205, 0.143),
        (0.238, 0.161),
        (depth, 0.1725),
    ]
    outer = add_profile_shell("MAGNUM_OUTER_SHELL", profile, (0, back_y, 1.90), mats["black_metal"], col, root, thickness=0.0011)
    inner_profile = [(y + 0.0015, max(0.001, r - 0.0035)) for y, r in profile]
    add_profile_shell("MAGNUM_INNER_REFLECTOR", inner_profile, (0, back_y, 1.90), mats["silver"], col, root, thickness=0.00055)
    add_cylinder("MAGNUM_COLLAR_01", 0.060, 0.026, (0, back_y - 0.010, 1.90), mats["black_metal"], col, axis="Y", parent=root)
    add_cylinder("MAGNUM_COLLAR_02", 0.056, 0.020, (0, back_y + 0.010, 1.90), mats["aluminum"], col, axis="Y", parent=root)
    add_torus("MAGNUM_COLLAR_GROOVE_01", 0.057, 0.0025, (0, back_y + 0.001, 1.90), (math.radians(90), 0, 0), mats["black_metal"], col, root)
    add_torus("MAGNUM_COLLAR_GROOVE_02", 0.059, 0.0023, (0, back_y + 0.020, 1.90), (math.radians(90), 0, 0), mats["black_metal"], col, root)
    add_torus("MAGNUM_FRONT_RIM", 0.169, 0.0045, (0, back_y + depth, 1.90), (math.radians(90), 0, 0), mats["black_metal"], col, root)
    add_torus("MAGNUM_INNER_RIM", 0.163, 0.0020, (0, back_y + depth - 0.001, 1.90), (math.radians(90), 0, 0), mats["silver"], col, root)
    return root, outer


def build_sandbag(mats):
    col = collection("AS_ACC_SANDBAG_01")
    root = tag_root(add_empty("ROOT_ACC_SANDBAG", col),
                    "AS_ACC_SANDBAG_01", "REPRESENTATIVE_STANDARD")
    left = add_cube("SANDBAG_POUCH_1", (0.150, 0.235, 0.072), (0.175, 0.0, 0.060), mats["fabric"], col, 0.032, root)
    right = add_cube("SANDBAG_POUCH_2", (0.150, 0.235, 0.072), (0.325, 0.0, 0.060), mats["fabric"], col, 0.032, root)
    left.rotation_euler.z = math.radians(2.5)
    right.rotation_euler.z = math.radians(-2.5)
    add_cube("SANDBAG_CENTER_STRAP", (0.060, 0.250, 0.025), (0.250, 0.0, 0.087), mats["black_metal"], col, 0.009, root)
    add_cube("SANDBAG_SEAM_LEFT", (0.006, 0.220, 0.008), (0.248, 0.0, 0.098), mats["fabric"], col, 0.002, root)
    add_cube("SANDBAG_SEAM_RIGHT", (0.006, 0.220, 0.008), (0.252, 0.0, 0.098), mats["fabric"], col, 0.002, root)
    rod_between("SANDBAG_HANDLE_A", (0.225, -0.115, 0.100), (0.225, -0.165, 0.150), 0.006, mats["fabric"], col, root)
    rod_between("SANDBAG_HANDLE_B", (0.275, -0.115, 0.100), (0.275, -0.165, 0.150), 0.006, mats["fabric"], col, root)
    rod_between("SANDBAG_HANDLE_TOP", (0.225, -0.165, 0.150), (0.275, -0.165, 0.150), 0.006, mats["fabric"], col, root)
    return root


def add_camera(name, location, target, lens, col):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    col.objects.link(cam)
    return cam


def add_area(name, location, energy, size, target, col):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    col.objects.link(obj)
    return obj


def build_preview_rig():
    col = collection("_PREVIEW_RIG")
    target = (0, 0.10, 1.05)
    add_area("PREVIEW_KEY", (2.8, -1.8, 3.8), 1200, 2.0, target, col)
    add_area("PREVIEW_FILL", (-2.5, -0.8, 2.4), 650, 2.3, target, col)
    add_area("PREVIEW_RIM", (0.4, 2.8, 3.1), 900, 1.6, target, col)
    add_area("PREVIEW_TOP", (0.0, 0.0, 4.5), 500, 1.8, target, col)
    cameras = {
        "front": add_camera("CAM_FRONT", (0.0, 4.4, 1.45), target, 62, col),
        "three_quarter": add_camera("CAM_THREE_QUARTER", (3.4, 3.5, 2.35), target, 58, col),
        "side": add_camera("CAM_SIDE", (4.3, 0.15, 1.48), target, 62, col),
        "rear": add_camera("CAM_REAR", (0.0, -4.2, 1.50), target, 62, col),
    }
    return cameras


def render_previews(scene, cameras):
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for name, cam in cameras.items():
        scene.camera = cam
        scene.render.filepath = str(PREVIEW_DIR / f"studio_rig_v01_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("AWFUL_PREVIEW", name, scene.render.filepath)


def main():
    clear_scene()
    scene = setup_scene()
    mats = build_materials()
    rig_col = collection("AS_RIG_STUDIO_V01")
    sem = collection("SEMANTICS")
    rig_root = tag_root(add_empty("ROOT_AWFUL_STUDIO_RIG", rig_col),
                        "AS_RIG_STUDIO_V01", "COMPOSITE_ASSET")
    cstand_root, support_mount = build_cstand(mats, sem)
    d1_root, modifier_mount = build_d1(mats, sem, support_mount)
    magnum_root, _ = build_magnum(mats, sem, modifier_mount)
    sandbag_root = build_sandbag(mats)
    for root in (cstand_root, d1_root, magnum_root, sandbag_root):
        root.parent = rig_root
    scene["awful_asset_id"] = "AS_RIG_STUDIO_V01"
    scene["awful_asset_version"] = "0.1.0"
    scene["awful_blender_target"] = SPEC["blender_target"]
    cameras = build_preview_rig()
    OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    print("AWFUL_STUDIO_SAVED", OUT_BLEND)
    render_previews(scene, cameras)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))


if __name__ == "__main__":
    main()


