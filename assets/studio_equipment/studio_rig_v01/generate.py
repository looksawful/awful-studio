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

def add_arc_band(name, center, outer_radius, inner_radius, depth_y,
                 start_deg, end_deg, mat, col, parent=None, segments=64):
    verts, faces = [], []
    cx, cy, cz = center
    for i in range(segments + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / segments)
        c, s = math.cos(a), math.sin(a)
        for yoff in (-depth_y * 0.5, depth_y * 0.5):
            verts.append((cx + outer_radius * c, cy + yoff, cz + outer_radius * s))
            verts.append((cx + inner_radius * c, cy + yoff, cz + inner_radius * s))
    for i in range(segments):
        a = i * 4
        b = (i + 1) * 4
        faces += [
            (a, b, b + 2, a + 2),
            (a + 1, a + 3, b + 3, b + 1),
            (a, a + 1, b + 1, b),
            (a + 2, b + 2, b + 3, a + 3),
        ]
    faces += [(0, 2, 3, 1)]
    end = segments * 4
    faces += [(end, end + 1, end + 3, end + 2)]
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
    bevel.width = 0.0015
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


def make_glass_material(name, tint=(0.78, 0.82, 0.86), roughness=0.28):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*tint, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.82
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.46
    return mat


def make_emission_material(name, color, strength=2.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def apply_boolean_difference(target, cutter, name):
    mod = target.modifiers.new(name, "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    target.select_set(False)
    mesh = cutter.data
    bpy.data.objects.remove(cutter, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

def build_materials():
    return {
        "chrome": make_material("MAT_CHROME", (0.48, 0.52, 0.56), 1.0, 0.16, 90, 0.018),
        "black_metal": make_material("MAT_BLACK_POWDER", (0.018, 0.020, 0.023), 0.0, 0.34, 70, 0.025),
        "black_plastic": make_material("MAT_BLACK_PLASTIC", (0.015, 0.017, 0.020), 0.0, 0.40, 120, 0.035),
        "silver": make_material("MAT_REFLECTOR_SILVER", (0.78, 0.80, 0.82), 1.0, 0.075, 220, 0.012),
        "aluminum": make_material("MAT_ALUMINUM", (0.40, 0.43, 0.46), 1.0, 0.22, 120, 0.020),
        "rubber": make_material("MAT_RUBBER", (0.010, 0.011, 0.013), 0.0, 0.72, 110, 0.050),
        "fabric": make_material("MAT_SANDBAG_FABRIC", (0.020, 0.022, 0.025), 0.0, 0.88, 240, 0.12),
        "webbing": make_material("MAT_WEBBING", (0.012, 0.014, 0.017), 0.0, 0.72, 180, 0.07),
        "label": make_material("MAT_LABEL_WHITE", (0.88, 0.88, 0.86), 0.0, 0.46),
        "glass": make_glass_material("MAT_FROSTED_GLASS"),
        "flash": make_emission_material("MAT_FLASH_TUBE", (0.88, 0.94, 1.0), 2.4),
        "lamp": make_emission_material("MAT_MODELING_LAMP", (1.0, 0.72, 0.42), 1.2),
        "indicator": make_emission_material("MAT_INDICATOR", (0.30, 0.78, 0.42), 1.5),
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
        rod_between(f"CSTAND_LEG_{idx}", start + radial * 0.035, end, 0.0125, mats["chrome"], col, root)
        add_cylinder(f"CSTAND_FOOT_{idx}", 0.017, 0.058, (end.x, end.y, 0.029), mats["rubber"], col, axis="Z", parent=root)
    # Three telescoping risers with decreasing diameters.
    add_cylinder("CSTAND_RISER_01", 0.0175, 0.700, (0, 0, 0.445), mats["chrome"], col, parent=root)
    add_cylinder("CSTAND_RISER_02", 0.0150, 0.590, (0, 0, 1.070), mats["chrome"], col, parent=root)
    add_cylinder("CSTAND_RISER_03", 0.0125, 0.355, (0, 0, 1.535), mats["chrome"], col, parent=root)
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
    reference = add_cube("D1_REFERENCE_ENVELOPE", (0.130, 0.300, 0.170),
                         (0, 0, z), None, col, 0.0, root)
    reference.display_type = "WIRE"
    reference.hide_render = True
    reference.hide_viewport = True

    # Main housing: stepped cylindrical Profoto D1 silhouette.
    body = add_cylinder("D1_MAIN_SHELL", 0.055, 0.190, (0, -0.015, z),
                      mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0)
    add_cylinder("D1_REAR_SHOULDER", 0.065, 0.042, (0, -0.129, z),
                 mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0012)
    add_cylinder("D1_FRONT_SHOULDER", 0.065, 0.040, (0, 0.086, z),
                 mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0012)
    add_cylinder("D1_FRONT_BARREL", 0.052, 0.036, (0, 0.124, z),
                 mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0009)
    add_cylinder("D1_FRONT_BAYONET", 0.049, 0.016, (0, 0.142, z),
                 mats["aluminum"], col, axis="Y", parent=root, bevel=0.0006)
    add_torus("D1_LOCK_RING", 0.050, 0.0036, (0, 0.147, z),
              (math.radians(90), 0, 0), mats["black_metal"], col, root)

    # Optical assembly behind the flat-front cover.
    add_cylinder("D1_GLASS_PLATE", 0.043, 0.0022, (0, 0.148, z),
                 mats["glass"], col, axis="Y", parent=root, bevel=0.0002)
    add_torus("D1_FLASHTUBE", 0.030, 0.0022, (0, 0.147, z),
              (math.radians(90), 0, 0), mats["flash"], col, root)
    add_sphere("D1_MODELING_LAMP", 0.013, (0, 0.1405, z),
               (1.0, 0.72, 1.0), mats["lamp"], col, root)

    # Five true recessed cooling slots on each side of the housing.
    for side_name, x, liner_x in (("L", -0.0545, -0.0477), ("R", 0.0545, 0.0477)):
        for idx, zz in enumerate((z + 0.026, z + 0.013, z, z - 0.013, z - 0.026), start=1):
            cutter = add_cube(f"CUT_D1_VENT_{side_name}_{idx:02d}",
                              (0.014, 0.054, 0.0065), (x, -0.035, zz),
                              None, col, 0.0006, root)
            apply_boolean_difference(body, cutter, f"VENT_{side_name}_{idx:02d}")
            add_cube(f"D1_SIDE_VENT_{side_name}_{idx:02d}",
                     (0.0010, 0.050, 0.0052), (liner_x, -0.035, zz),
                     mats["black_metal"], col, 0.0004, root)
    shell_bevel = body.modifiers.new("EDGE_BEVEL", "BEVEL")
    shell_bevel.width = 0.0010
    shell_bevel.segments = 3
    shell_bevel.limit_method = "ANGLE"

    # Molded ergonomic yoke/handle wraps around the lower rear housing.
    add_arc_band("D1_YOKE_BAND", (0, -0.020, z), 0.080, 0.062, 0.032,
                 130, 410, mats["black_plastic"], col, root, segments=72)
    # Recessed circular rear control panel. The outer shoulder remains the deepest surface.
    add_cylinder("D1_REAR_PANEL", 0.055, 0.006, (0, -0.145, z),
                 mats["black_metal"], col, axis="Y", parent=root, bevel=0.0005)
    add_cube("D1_REAR_DISPLAY", (0.040, 0.0015, 0.020),
             (0, -0.1490, z + 0.035), mats["black_plastic"], col, 0.0018, root)
    for idx, x in enumerate((-0.010, 0.000, 0.010), start=1):
        add_cube(f"D1_DISPLAY_SEG_{idx}", (0.005, 0.0008, 0.011),
                 (x, -0.14985, z + 0.035), mats["indicator"], col, 0.00025, root)
    add_cylinder("D1_SETTING_KNOB", 0.0155, 0.0020, (0, -0.1490, z - 0.002),
                 mats["black_plastic"], col, axis="Y", parent=root, bevel=0.0005)

    button_positions = [
        (-0.032, z + 0.013), (0.032, z + 0.013),
        (-0.032, z - 0.007), (0.032, z - 0.007),
        (-0.032, z - 0.027), (0.032, z - 0.027),
    ]
    for idx, (x, zz) in enumerate(button_positions, start=1):
        add_cube(f"D1_REAR_BUTTON_{idx}", (0.022, 0.0014, 0.012),
                 (x, -0.1490, zz), mats["black_plastic"], col, 0.0015, root)
    add_cylinder("D1_READY_INDICATOR", 0.0032, 0.0012,
                 (-0.043, -0.1494, z + 0.015), mats["indicator"], col,
                 axis="Y", parent=root, bevel=0.00015)
    # Side pivots, stand adapter and locking hardware.
    add_cylinder("D1_TILT_PIVOT_L", 0.021, 0.018,
                 (-0.071, -0.020, z - 0.018), mats["black_metal"], col,
                 axis="X", parent=root)
    add_cylinder("D1_TILT_PIVOT_R", 0.021, 0.018,
                 (0.071, -0.020, z - 0.018), mats["black_metal"], col,
                 axis="X", parent=root)
    add_cylinder("D1_TILT_KNOB", 0.022, 0.032,
                 (0.092, -0.020, z - 0.018), mats["black_plastic"], col,
                 axis="X", parent=root)
    add_cylinder("D1_STAND_SOCKET", 0.016, 0.050,
                 (0, 0.0, z - 0.060), mats["black_metal"], col,
                 parent=root, bevel=0.0008)
    add_cylinder("D1_STAND_LOCK_KNOB", 0.011, 0.026,
                 (0.027, 0.0, z - 0.070), mats["black_plastic"], col,
                 axis="X", parent=root)

    # Mains/sync interfaces are kept near the lower stand-adapter area.
    add_cube("D1_AC_CONNECTOR", (0.022, 0.016, 0.014),
             (-0.030, -0.010, z - 0.065), mats["black_plastic"], col, 0.0020, root)
    add_cylinder("D1_FUSE_HOLDER", 0.0065, 0.008,
                 (-0.054, -0.010, z - 0.060), mats["black_plastic"], col,
                 axis="X", parent=root, bevel=0.00025)
    add_cylinder("D1_SYNC_PORT", 0.0060, 0.008,
                 (0.054, -0.010, z - 0.060), mats["black_plastic"], col,
                 axis="X", parent=root, bevel=0.00025)
    add_cylinder("D1_UMBRELLA_TUBE", 0.005, 0.100,
                 (0.034, 0.018, z - 0.055), mats["aluminum"], col,
                 axis="Y", parent=root, bevel=0.00035)
    add_torus("D1_UMBRELLA_TUBE_RIM", 0.0062, 0.0012,
              (0.034, 0.068, z - 0.055), (math.radians(90), 0, 0),
              mats["black_metal"], col, root)

    # Physical scale marks for Profoto's reflector zoom position.
    for idx, yy in enumerate((0.102, 0.111, 0.120, 0.129, 0.138), start=1):
        add_cube(f"D1_ZOOM_TICK_{idx:02d}", (0.0022, 0.0045, 0.011),
                 (-0.052, yy, z + 0.022), mats["label"], col, 0.00035, root)

    mount_fixture = add_empty("MOUNT_FIXTURE", sem, (0, 0.0, z - 0.085), 0.045)
    mount_fixture.parent = root
    mount_modifier = add_empty("MOUNT_MODIFIER", sem, (0, 0.150, z), 0.045)
    mount_modifier.parent = root
    emitter = add_empty("EMITTER_ORIGIN", sem, (0, 0.149, z), 0.035)
    emitter.parent = root
    add_empty("LIGHT_TARGET", sem, (0, 2.5, 1.55), 0.08).parent = root

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
    overall_start = mount_modifier.location.y
    z = mount_modifier.location.z
    depth = SPEC["magnum_100624"]["depth_mm"] * MM
    collar_len = 0.040
    bowl_start = overall_start + collar_len
    front = overall_start + depth
    bowl_depth = depth - collar_len
    reference = add_cube(
        "MAGNUM_REFERENCE_ENVELOPE", (0.345, depth, 0.345),
        (0, overall_start + depth * 0.5, z), None, col, 0.0, root
    )
    reference.display_type = "WIRE"
    reference.hide_render = True
    reference.hide_viewport = True
    profile = [
        (0.000, 0.0540), (0.020, 0.0580), (0.050, 0.0670),
        (0.085, 0.0810), (0.120, 0.1010), (0.155, 0.1250),
        (0.188, 0.1490), (0.218, 0.1685),
    ]
    outer = add_profile_shell(
        "MAGNUM_OUTER_SHELL", profile, (0, bowl_start, z),
        mats["black_metal"], col, root, thickness=0.0011
    )
    inner_profile = [(y + 0.0015, max(0.001, r - 0.0035)) for y, r in profile]
    add_profile_shell(
        "MAGNUM_INNER_REFLECTOR", inner_profile, (0, bowl_start, z),
        mats["silver"], col, root, thickness=0.00055
    )
    add_cylinder(
        "MAGNUM_COLLAR_REAR", 0.060, 0.020,
        (0, overall_start + 0.010, z), mats["black_metal"], col,
        axis="Y", parent=root, bevel=0.0006
    )
    add_cylinder(
        "MAGNUM_COLLAR_FRONT", 0.057, 0.020,
        (0, overall_start + 0.030, z), mats["aluminum"], col,
        axis="Y", parent=root, bevel=0.0005
    )
    add_torus(
        "MAGNUM_COLLAR_GROOVE_01", 0.0575, 0.0022,
        (0, overall_start + 0.019, z), (math.radians(90), 0, 0),
        mats["black_metal"], col, root
    )
    add_torus(
        "MAGNUM_FRONT_RIM", 0.1690, 0.0035,
        (0, front - 0.0035, z), (math.radians(90), 0, 0),
        mats["black_metal"], col, root
    )
    add_torus(
        "MAGNUM_INNER_RIM", 0.1630, 0.0018,
        (0, front - 0.0038, z), (math.radians(90), 0, 0),
        mats["silver"], col, root
    )
    root["awful_mount_start_y_m"] = overall_start
    root["awful_front_y_m"] = front
    return root, outer

def build_sandbag(mats):
    col = collection("AS_ACC_SANDBAG_01")
    root = tag_root(add_empty("ROOT_ACC_SANDBAG", col),
                    "AS_ACC_SANDBAG_01", "REPRESENTATIVE_STANDARD")
    ref = add_cube("SANDBAG_REFERENCE_ENVELOPE", (0.360, 0.250, 0.070),
                   (0.250, 0.0, 0.035), None, col, 0.0, root)
    ref.display_type = "WIRE"
    ref.hide_render = True
    ref.hide_viewport = True

    for idx, (x, angle) in enumerate(((0.160, 1.8), (0.340, -1.8)), start=1):
        pouch = add_cube(f"SANDBAG_POUCH_{idx}", (0.180, 0.245, 0.064),
                         (x, 0.0, 0.052), mats["fabric"], col, 0.024, root)
        pouch.rotation_euler.z = math.radians(angle)
        bevel = pouch.modifiers.get("EDGE_BEVEL")
        bevel.name = "SOFT_BEVEL"
        bevel.segments = 8
        bevel.width = 0.024
        subdiv = pouch.modifiers.new("SOFT_SUBDIV", "SUBSURF")
        subdiv.subdivision_type = "CATMULL_CLARK"
        subdiv.levels = 2
        subdiv.render_levels = 2
        tex = bpy.data.textures.new(f"TEX_SANDBAG_SAG_{idx}", type="CLOUDS")
        tex.noise_scale = 0.045
        disp = pouch.modifiers.new("MICRO_SAG", "DISPLACE")
        disp.texture = tex
        disp.strength = 0.0022
        disp.mid_level = 0.5
        for poly in pouch.data.polygons:
            poly.use_smooth = True
        # Raised stitched seam guides on the top perimeter.
        for sy in (-0.116, 0.116):
            add_cube(f"SANDBAG_SEAM_{idx}_Y_{'A' if sy < 0 else 'B'}",
                     (0.150, 0.004, 0.003), (x, sy, 0.083),
                     mats["fabric"], col, 0.0012, root)
        for sx in (x - 0.083, x + 0.083):
            add_cube(f"SANDBAG_SEAM_{idx}_X_{'A' if sx < x else 'B'}",
                     (0.004, 0.210, 0.003), (sx, 0.0, 0.083),
                     mats["fabric"], col, 0.0012, root)

    add_cube("SANDBAG_CENTER_STRAP", (0.058, 0.252, 0.020),
             (0.250, 0.0, 0.088), mats["webbing"], col, 0.008, root)
    add_cube("SANDBAG_LABEL_PATCH", (0.044, 0.070, 0.004),
             (0.250, 0.020, 0.101), mats["label"], col, 0.002, root)
    rod_between("SANDBAG_HANDLE_A", (0.225, -0.118, 0.092),
                (0.225, -0.170, 0.145), 0.006, mats["webbing"], col, root)
    rod_between("SANDBAG_HANDLE_B", (0.275, -0.118, 0.092),
                (0.275, -0.170, 0.145), 0.006, mats["webbing"], col, root)
    rod_between("SANDBAG_HANDLE_TOP", (0.225, -0.170, 0.145),
                (0.275, -0.170, 0.145), 0.006, mats["webbing"], col, root)
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
        "fixture_detail": add_camera("CAM_FIXTURE_DETAIL", (1.05, 0.80, 2.08), (0.0, 0.02, 1.84), 85, col),
        "fixture_rear_detail": add_camera("CAM_FIXTURE_REAR_DETAIL", (0.35, -0.82, 1.93), (0.0, -0.11, 1.835), 95, col),
        "magnum_profile_detail": add_camera("CAM_MAGNUM_PROFILE_DETAIL", (0.95, 0.28, 1.90), (0.0, 0.29, 1.835), 90, col),
        "base_detail": add_camera("CAM_BASE_DETAIL", (1.45, 1.30, 0.72), (0.0, 0.0, 0.10), 70, col),
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


