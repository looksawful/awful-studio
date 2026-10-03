import json
import math
import os
import sys
import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.normpath(os.path.join(HERE, "..", "common"))
if COMMON not in sys.path:
    sys.path.insert(0, COMMON)
import foundation_common as fc
sys.path.insert(0, HERE)
from camera_topology_v30 import camera_mesh, attach_camera_normal

MM = fc.MM

def outward_prism(*args, **kwargs):
    """Correct the Y-axis basis reflection before booleans or bevel evaluation.

    Keep this repair iPhone-local: other released device deliveries retain their
    existing source fingerprints until their own production review.
    """
    obj = fc.rounded_prism(*args, **kwargs)
    if kwargs.get("axis", "Y") == "Y":
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bm.normal_update()
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    return obj

def smooth_sharp_boundaries(obj):
    # Booleans reorder faces. Polygon indices cannot identify caps or rails.
    # Keep planar rails separate from aperture walls and bevel transitions.
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.set_sharp_from_angle(angle=math.radians(30.0))


def apply_runtime_bevel(obj, width, segments=4):
    bevel = obj.modifiers.get("EDGE_BEVEL")
    if bevel is None:
        raise RuntimeError(f"{obj.name} is missing EDGE_BEVEL")
    bevel.width = width
    bevel.segments = segments
    bevel.harden_normals = False
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    smooth_sharp_boundaries(obj)


def ensure_box_uv(obj, tile_mm=4.0, *, replace=False):
    """Create deterministic UVs for exported PBR maps without changing geometry."""
    mesh = obj.data
    if mesh.uv_layers.active and not replace:
        return mesh.uv_layers.active
    if replace:
        while mesh.uv_layers:
            mesh.uv_layers.remove(mesh.uv_layers[0])
    uv_layer = mesh.uv_layers.new(name="UVMap")
    scale = tile_mm * MM
    for polygon in mesh.polygons:
        normal = polygon.normal
        axis = max(range(3), key=lambda index: abs(normal[index]))
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if axis == 0:
                uv = (vertex.y / scale + 0.5, vertex.z / scale + 0.5)
            elif axis == 1:
                uv = (vertex.x / scale + 0.5, vertex.z / scale + 0.5)
            else:
                uv = (vertex.x / scale + 0.5, vertex.y / scale + 0.5)
            uv_layer.data[loop_index].uv = uv
    return uv_layer


def packed_image(name, size, pixel_fn, *, non_color=True):
    image = bpy.data.images.new(name, width=size, height=size)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    pixels = []
    for row in range(size):
        for column in range(size):
            pixels.extend(pixel_fn(column, row, size))
    image.pixels.foreach_set(pixels)
    image.pack()
    return image


def height_normal_image(name, size, height_fn, strength=1.0):
    heights = [[height_fn(column, row, size) for column in range(size)] for row in range(size)]
    pixels = []
    for row in range(size):
        for column in range(size):
            left = heights[row][(column - 1) % size]
            right = heights[row][(column + 1) % size]
            down = heights[(row - 1) % size][column]
            up = heights[(row + 1) % size][column]
            dx = (right - left) * strength
            dy = (up - down) * strength
            length = math.sqrt(dx * dx + dy * dy + 1.0)
            nx, ny, nz = -dx / length, -dy / length, 1.0 / length
            pixels.extend((0.5 + 0.5 * nx, 0.5 + 0.5 * ny, 0.5 + 0.5 * nz, 1.0))
    image = bpy.data.images.new(name, width=size, height=size)
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(pixels)
    image.pack()
    return image


def attach_roughness_map(material, roughness_image):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    rough_tex = nodes.new("ShaderNodeTexImage")
    rough_tex.image = roughness_image
    rough_tex.interpolation = "Linear"
    links.new(rough_tex.outputs["Color"], bsdf.inputs["Roughness"])


def attach_pbr_maps(material, normal_image, roughness_image, normal_strength):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = normal_image
    normal_tex.interpolation = "Linear"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = normal_strength
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    attach_roughness_map(material, roughness_image)


APPLE_CORNER_EXTENT = 19.23 * MM
APPLE_CORNER_BEZIER = (
    (0.00 * MM, 19.23 * MM),
    (0.00 * MM, 3.00 * MM),
    (0.87 * MM, 7.88 * MM),
    (7.88 * MM, 0.87 * MM),
    (3.00 * MM, 0.00 * MM),
    (19.23 * MM, 0.00 * MM),
)

def iphone17_corner_profile(t):
    omt = 1.0 - t
    weights = (
        omt**5,
        5.0 * omt**4 * t,
        10.0 * omt**3 * t**2,
        10.0 * omt**2 * t**3,
        5.0 * omt * t**4,
        t**5,
    )
    return tuple(
        sum(weight * point[axis] for weight, point in zip(weights, APPLE_CORNER_BEZIER))
        for axis in (0, 1)
    )

def iphone17_body_outline(width, height, segments=48):
    half_w, half_h = width * 0.5, height * 0.5
    quarter = [iphone17_corner_profile(step / segments) for step in range(segments + 1)]
    return (
        [(half_w - dx, half_h - dy) for dx, dy in quarter]
        + [(-half_w + dx, half_h - dy) for dx, dy in reversed(quarter)]
        + [(-half_w + dx, -half_h + dy) for dx, dy in quarter]
        + [(half_w - dx, -half_h + dy) for dx, dy in reversed(quarter)]
    )

def rounded_rect_strip_prism_y(name, width, height, depth, radius, material, collection, location=(0, 0, 0), segments=16):
    """Build a clean rounded-rectangle prism with quad-strip planar caps."""
    half_w, half_h = width * 0.5, height * 0.5
    cx, cz = half_w - radius, half_h - radius
    top_rows = []
    for step in range(segments + 1):
        angle = (math.pi * 0.5) * (step / segments)
        x = cx + radius * math.sin(angle)
        z = cz + radius * math.cos(angle)
        top_rows.append((x, z))
    rows = top_rows + [(x, -z) for x, z in reversed(top_rows)]

    points = []
    row_indices = []
    for x, z in rows:
        left = len(points)
        points.extend(((-x, z), (x, z)))
        row_indices.append((left, left + 1))

    count = len(points)
    verts = (
        [(x, -depth * 0.5, z) for x, z in points]
        + [(x, depth * 0.5, z) for x, z in points]
    )
    front = [
        (a_left, b_left, b_right, a_right)
        for (a_left, a_right), (b_left, b_right) in zip(row_indices, row_indices[1:])
    ]
    faces = front + [tuple(index + count for index in reversed(face)) for face in front]

    boundary = (
        [row_indices[0][0]]
        + [right for _, right in row_indices]
        + [row_indices[-1][0]]
        + [row_indices[index][0] for index in reversed(range(1, len(row_indices) - 1))]
    )
    for index, a in enumerate(boundary):
        b = boundary[(index + 1) % len(boundary)]
        faces.append((a, b, b + count, a + count))

    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    if material:
        mesh.materials.append(material)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def iphone17_body_prism(name, width, height, depth, material, collection, segments=48):
    outline = iphone17_body_outline(width, height, segments)
    count = len(outline)
    verts = (
        [(x, -depth * 0.5, z) for x, z in outline]
        + [(x, depth * 0.5, z) for x, z in outline]
    )
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))

    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj

W, H, D = 71.45 * MM, 149.61 * MM, 7.95 * MM
BODY_R = 13.6 * MM
METAL_D = 7.25 * MM
GLASS_T = 0.35 * MM
COVER_W, COVER_H, COVER_R = 69.45 * MM, 147.61 * MM, 12.0 * MM
SCREEN_W, SCREEN_H, SCREEN_R = 66.57 * MM, 144.79 * MM, 10.55 * MM

# Apple drawing Detail D camera plateau datums, measured from product left/top.
CAM_OUTER_X0, CAM_OUTER_X1 = 1.18 * MM, 26.06 * MM
CAM_OUTER_Z0, CAM_OUTER_Z1 = 1.34 * MM, 43.62 * MM
CAM_INNER_X0, CAM_INNER_X1 = 3.79 * MM, 23.45 * MM
CAM_INNER_Z0, CAM_INNER_Z1 = 3.97 * MM, 40.99 * MM
CAM_CENTER_X_REF, CAM_CENTER_Z_REF = 13.62 * MM, 22.48 * MM
CAM_OUTER_W, CAM_OUTER_H = CAM_OUTER_X1 - CAM_OUTER_X0, CAM_OUTER_Z1 - CAM_OUTER_Z0
CAM_INNER_W, CAM_INNER_H = CAM_INNER_X1 - CAM_INNER_X0, CAM_INNER_Z1 - CAM_INNER_Z0
CAM_CENTER_X = W * 0.5 - CAM_CENTER_X_REF
CAM_CENTER_Z = H * 0.5 - CAM_CENTER_Z_REF

def cli(flag, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default

OUT = os.path.abspath(cli("--out", os.path.join(HERE, "generated", "iphone_17_low_v30.blend")))
EVIDENCE = os.path.abspath(cli("--evidence", os.path.join(HERE, "evidence", "low_v30_validation.json")))
PREVIEWS = os.path.abspath(cli("--previews", os.path.join(HERE, "previews", "low_v30")))
fc.clear_scene()
fc.setup_scene()
scene = bpy.context.scene
scene.render.resolution_x = 1600
scene.render.resolution_y = 1600
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.exposure = -1.35
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.001, 0.001, 0.001, 1.0)
bg.inputs['Strength'].default_value = 0.025
body_c = fc.make_collection("IPHONE_17_LOW_BODY")
detail_c = fc.make_collection("IPHONE_17_LOW_DETAILS")
screen_c = fc.make_collection("IPHONE_17_LOW_SCREEN")
ctrl_c = fc.make_collection("IPHONE_17_CONTROLLERS")

metal = fc.make_material("MAT_ANODIZED_ALUMINUM", (0.006, 0.007, 0.010), 1.0, 0.31)
metal_dark = fc.make_material("MAT_ALUMINUM_EDGE", (0.012, 0.014, 0.020), 1.0, 0.24)
camera_housing_mat = fc.make_material("MAT_CAMERA_HOUSING", (0.010, 0.013, 0.020), 1.0, 0.27)
back_mat = fc.make_material("MAT_BACK_GLASS", (0.00008, 0.00010, 0.00014), 0.0, 0.38)
camera_seat_mat = fc.make_material("MAT_CAMERA_HOUSING_SEAT", (0.00008, 0.00010, 0.00014), 0.0, 0.38)
back_bsdf = back_mat.node_tree.nodes.get("Principled BSDF")
back_bsdf.inputs["Coat Weight"].default_value = 0.22
back_bsdf.inputs["Coat Roughness"].default_value = 0.09
if back_bsdf.inputs.get("Specular IOR Level"):
    back_bsdf.inputs["Specular IOR Level"].default_value = 0.18
black = fc.make_material("MAT_OPTICS_BLACK", (0.0008, 0.0010, 0.0014), 0.0, 0.07)
grille_mat = fc.make_material("MAT_APERTURE_GRILLE", (0.0010, 0.0012, 0.0016), 0.0, 0.82)
# A fine woven grille is surface detail; the surrounding recess remains geometry.
# Pack the tangent-space normal so both Blender and GLB use the same microtexture.
grille_image = bpy.data.images.new("aperture_weave_normal_128", width=128, height=128)
grille_image.colorspace_settings.name = "Non-Color"
pixels = []
for row in range(128):
    for column in range(128):
        nx = 0.22 * math.sin(2 * math.pi * column / 8)
        ny = 0.22 * math.sin(2 * math.pi * row / 8)
        length = math.sqrt(nx * nx + ny * ny + 1)
        pixels.extend((0.5 + nx / length * 0.5, 0.5 + ny / length * 0.5, 0.5 + 0.5 / length, 1.0))
grille_image.pixels.foreach_set(pixels)
grille_image.pack()
grille_tex = grille_mat.node_tree.nodes.new("ShaderNodeTexImage")
grille_tex.image = grille_image
grille_normal = grille_mat.node_tree.nodes.new("ShaderNodeNormalMap")
grille_normal.inputs["Strength"].default_value = 0.45
grille_mat.node_tree.links.new(grille_tex.outputs["Color"], grille_normal.inputs["Color"])
grille_mat.node_tree.links.new(grille_normal.outputs["Normal"], grille_mat.node_tree.nodes.get("Principled BSDF").inputs["Normal"])
under_glass_mat = fc.make_material("MAT_UNDER_GLASS_BLACK", (0.000001, 0.000001, 0.000001), 0.0, 1.0)
under_glass_bsdf = under_glass_mat.node_tree.nodes.get("Principled BSDF")
if under_glass_bsdf.inputs.get("Specular IOR Level"):
    under_glass_bsdf.inputs["Specular IOR Level"].default_value = 0.0

camera_control_mat = fc.make_material("MAT_CAMERA_CONTROL_GLASS", (0.00008, 0.00009, 0.00012), 0.0, 0.16)
camera_control_bsdf = camera_control_mat.node_tree.nodes.get("Principled BSDF")
camera_control_bsdf.inputs["Coat Weight"].default_value = 0.22
camera_control_bsdf.inputs["Coat Roughness"].default_value = 0.08

front_optic = fc.make_material("MAT_FRONT_OPTIC", (0.002, 0.004, 0.009), 0.0, 0.20)
front_bsdf = front_optic.node_tree.nodes.get("Principled BSDF")
front_bsdf.inputs["Coat Weight"].default_value = 0.18
front_bsdf.inputs["Coat Roughness"].default_value = 0.08
front_bsdf.inputs["Specular IOR Level"].default_value = 0.15
front_detail_tex = front_optic.node_tree.nodes.new("ShaderNodeTexImage")
front_detail_tex.image = bpy.data.images.load(
    os.path.join(HERE, "reference", "front_camera_detail_mask.png"),
    check_existing=True,
)
front_detail_tex.image.colorspace_settings.name = "sRGB"
front_detail_tex.image.pack()
front_detail_mix = front_optic.node_tree.nodes.new("ShaderNodeMix")
front_detail_mix.data_type = "RGBA"
front_detail_mix.blend_type = "MULTIPLY"
front_detail_mix.inputs[0].default_value = 1.0
front_detail_mix.inputs[6].default_value = (0.002, 0.004, 0.009, 1.0)
front_optic.node_tree.links.new(front_detail_tex.outputs["Color"], front_detail_mix.inputs[7])
front_optic.node_tree.links.new(front_detail_mix.outputs["Result"], front_bsdf.inputs["Base Color"])
lens_glass = fc.make_material("MAT_LENS_GLASS", (0.00012, 0.00016, 0.00024), 0.0, 0.020)
lbsdf = lens_glass.node_tree.nodes.get("Principled BSDF")
lbsdf.inputs["Coat Weight"].default_value = 0.62
lbsdf.inputs["Coat Roughness"].default_value = 0.008
gap_mat = fc.make_material("MAT_ASSEMBLY_GAP", (0.0005, 0.0006, 0.0008), 0.0, 0.32)
bezel_mat = fc.make_material("MAT_DISPLAY_BEZEL", (0.001, 0.0012, 0.0015), 0.0, 0.10)
screen_mat = fc.make_material("MAT_SCREEN_CONTENT", (0.0038, 0.0052, 0.0078), 0.0, 0.085)
screen_texture_path = os.path.join(HERE, "reference", "ios26_home_screen_clean_1206x2622.png")
screen_tex = screen_mat.node_tree.nodes.new("ShaderNodeTexImage")
screen_tex.image = bpy.data.images.load(screen_texture_path, check_existing=True)
screen_tex.image.colorspace_settings.name = "sRGB"
screen_tex.image.pack()
screen_bsdf = screen_mat.node_tree.nodes.get("Principled BSDF")
screen_bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
screen_bsdf.inputs["Roughness"].default_value = 1.0
screen_bsdf.inputs["Specular IOR Level"].default_value = 0.0
screen_mat.node_tree.links.new(screen_tex.outputs["Color"], screen_bsdf.inputs["Emission Color"])
screen_bsdf.inputs["Emission Strength"].default_value = 0.85
optic_glass = fc.make_material("MAT_OPTICAL_GLASS", (0.0010, 0.0014, 0.0024), 0.0, 0.030)
flash_mat = fc.make_material("MAT_FLASH", (1.0, 1.0, 1.0), 0.0, 0.32)
flash_tex = flash_mat.node_tree.nodes.new("ShaderNodeTexImage")
flash_tex.image = bpy.data.images.load(os.path.join(HERE, "reference", "flash_diffuser_v30.png"), check_existing=True)
flash_tex.image.colorspace_settings.name = "sRGB"
flash_tex.image.pack()
flash_bsdf = flash_mat.node_tree.nodes.get("Principled BSDF")
flash_mat.node_tree.links.new(flash_tex.outputs["Color"], flash_bsdf.inputs["Base Color"])
flash_bsdf.inputs["Coat Weight"].default_value = 0.25
flash_bsdf.inputs["Coat Roughness"].default_value = 0.10
screw_mat = fc.make_material("MAT_FASTENER", (0.10, 0.11, 0.13), 0.92, 0.24)

# Embedded product-surface maps: these survive Blender -> GLB -> Three.js.
# Keep amplitudes subtle; silhouette/detail-critical forms remain geometry.
def aluminum_height(column, row, size):
    u = column / size
    v = row / size
    return (
        0.020 * math.sin(2.0 * math.pi * (u * 31.0 + v * 2.0))
        + 0.010 * math.sin(2.0 * math.pi * (u * 71.0 - v * 5.0))
        + 0.006 * math.sin(2.0 * math.pi * (u * 13.0 + v * 47.0))
    )

def aluminum_roughness(column, row, size):
    u = column / size
    v = row / size
    value = 0.29 + 0.025 * math.sin(2.0 * math.pi * (u * 19.0 + v * 3.0))
    value += 0.015 * math.sin(2.0 * math.pi * (u * 7.0 - v * 29.0))
    value = max(0.22, min(0.36, value))
    return (value, value, value, 1.0)

def glass_height(column, row, size):
    u = column / size
    v = row / size
    return (
        0.012 * math.sin(2.0 * math.pi * (u * 17.0 + v * 23.0))
        + 0.008 * math.sin(2.0 * math.pi * (u * 43.0 - v * 11.0))
    )

def glass_roughness(column, row, size):
    u = column / size
    v = row / size
    value = 0.38 + 0.018 * math.sin(2.0 * math.pi * (u * 11.0 + v * 17.0))
    value += 0.010 * math.sin(2.0 * math.pi * (u * 37.0 - v * 5.0))
    value = max(0.34, min(0.43, value))
    return (value, value, value, 1.0)

def camera_control_roughness(column, row, size):
    u = column / size
    v = row / size
    value = 0.16 + 0.018 * math.sin(2.0 * math.pi * (u * 13.0 + v * 7.0))
    value += 0.010 * math.sin(2.0 * math.pi * (u * 31.0 - v * 11.0))
    value = max(0.13, min(0.20, value))
    return (value, value, value, 1.0)

def pentalobe_height(column, row, size):
    x = ((column + 0.5) / size) * 2.0 - 1.0
    y = ((row + 0.5) / size) * 2.0 - 1.0
    radius = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x)
    socket_radius = 0.42 * (1.0 + 0.14 * math.cos(5.0 * angle))
    edge = 0.035
    signed = radius - socket_radius
    if signed <= -edge:
        return -0.55
    if signed >= edge:
        return 0.0
    t = (signed + edge) / (2.0 * edge)
    return -0.55 * 0.5 * (1.0 + math.cos(math.pi * t))

def pentalobe_roughness(column, row, size):
    x = ((column + 0.5) / size) * 2.0 - 1.0
    y = ((row + 0.5) / size) * 2.0 - 1.0
    radius = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x)
    socket_radius = 0.42 * (1.0 + 0.14 * math.cos(5.0 * angle))
    value = 0.62 if radius <= socket_radius else 0.20
    return (value, value, value, 1.0)

def pentalobe_basecolor(column, row, size):
    x = ((column + 0.5) / size) * 2.0 - 1.0
    y = ((row + 0.5) / size) * 2.0 - 1.0
    radius = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x)
    socket_radius = 0.42 * (1.0 + 0.14 * math.cos(5.0 * angle))
    edge = 0.025
    if radius <= socket_radius - edge:
        value = 0.025
    elif radius >= socket_radius + edge:
        value = 0.58
    else:
        t = (radius - (socket_radius - edge)) / (2.0 * edge)
        value = 0.025 * (1.0 - t) + 0.58 * t
    return (value, value * 1.005, value * 1.015, 1.0)

aluminum_normal = height_normal_image("anodized_aluminum_normal_128", 128, aluminum_height, strength=8.0)
aluminum_rough = packed_image("anodized_aluminum_roughness_128", 128, aluminum_roughness)
back_glass_normal = height_normal_image("back_glass_micro_normal_128", 128, glass_height, strength=6.0)
back_glass_rough = packed_image("back_glass_micro_roughness_128", 128, glass_roughness)
camera_control_rough = packed_image("camera_control_roughness_128", 128, camera_control_roughness)
pentalobe_normal = height_normal_image("pentalobe_fastener_normal_256", 256, pentalobe_height, strength=6.0)
pentalobe_rough = packed_image("pentalobe_fastener_roughness_256", 256, pentalobe_roughness)
pentalobe_color = packed_image("pentalobe_fastener_basecolor_256", 256, pentalobe_basecolor, non_color=False)

for material, strength in (
    (metal, 0.22),
    (metal_dark, 0.18),
):
    attach_pbr_maps(material, aluminum_normal, aluminum_rough, strength)
# The rounded camera plateau already carries real bevel geometry. Its bevel topology
# produces degenerate tangent vertices in glTF, so keep micro-variation in roughness only.
attach_roughness_map(camera_housing_mat, aluminum_rough)
attach_roughness_map(camera_seat_mat, back_glass_rough)
attach_pbr_maps(back_mat, back_glass_normal, back_glass_rough, 0.18)
attach_pbr_maps(camera_control_mat, back_glass_normal, camera_control_rough, 0.14)
attach_pbr_maps(screw_mat, pentalobe_normal, pentalobe_rough, 0.95)
screw_bsdf = screw_mat.node_tree.nodes.get("Principled BSDF")
screw_color_tex = screw_mat.node_tree.nodes.new("ShaderNodeTexImage")
screw_color_tex.image = pentalobe_color
screw_mat.node_tree.links.new(screw_color_tex.outputs["Color"], screw_bsdf.inputs["Base Color"])
screw_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
screw_mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)

glass = fc.make_material("MAT_DISPLAY_GLASS", (0.0015, 0.0020, 0.0030), 0.0, 0.045)
gbsdf = glass.node_tree.nodes.get("Principled BSDF")
gbsdf.inputs["IOR"].default_value = 1.46
# Portable glass layer: alpha works consistently in Blender, glTF/Three.js and Unity.
gbsdf.inputs["Transmission Weight"].default_value = 0.0
gbsdf.inputs["Alpha"].default_value = 0.10
glass.diffuse_color = (0.0015, 0.0020, 0.0030, 0.10)
try:
    glass.surface_render_method = "DITHERED"
except Exception:
    pass
gbsdf.inputs["Coat Weight"].default_value = 0.18
gbsdf.inputs["Coat Roughness"].default_value = 0.028


body = iphone17_body_prism("BODY_ALUMINUM", W, H, METAL_D, metal, body_c, segments=48)
front_y = -(D * 0.5 - GLASS_T * 0.5)
front_surface = -D * 0.5
back_y = D * 0.5 - GLASS_T * 0.5

# Official Apple drawing: cover glass 69.45 x 147.61 mm, active area 66.57 x 144.79 mm.
pocket = outward_prism("DISPLAY_POCKET_CUTTER", COVER_W + 0.12*MM, COVER_H + 0.12*MM, 0.72*MM,
                          COVER_R + 0.06*MM, None, detail_c, axis="Y",
                          location=(0, -METAL_D*0.5 + 0.16*MM, 0), outline_segments=48)
fc.boolean_difference(body, pocket, name="CUT_DISPLAY_POCKET")

back_seat = outward_prism("BACK_GLASS_SEAT", COVER_W + 0.12*MM, COVER_H + 0.12*MM, 0.07*MM,
                             COVER_R + 0.06*MM, gap_mat, body_c, axis="Y",
                             location=(0, METAL_D*0.5 + 0.012*MM, 0), outline_segments=48)
back_seat.hide_render = True
back_glass = outward_prism("BACK_GLASS", COVER_W, COVER_H, GLASS_T, COVER_R,
                              back_mat, body_c, axis="Y", location=(0, back_y, 0),
                              edge_bevel=0.0, outline_segments=48)

front_seat = outward_prism("DISPLAY_GLASS_SEAT", COVER_W + 0.10*MM, COVER_H + 0.10*MM, 0.07*MM,
                              COVER_R + 0.05*MM, gap_mat, screen_c, axis="Y",
                              location=(0, -METAL_D*0.5 - 0.010*MM, 0), outline_segments=48)
bezel = outward_prism("DISPLAY_BEZEL", SCREEN_W + 0.68*MM, SCREEN_H + 0.68*MM, 0.08*MM,
                         SCREEN_R + 0.32*MM, bezel_mat, screen_c, axis="Y",
                         location=(0, front_y + 0.08*MM, 0), outline_segments=48)

screen_glass = outward_prism("SCREEN_GLASS", COVER_W, COVER_H, GLASS_T, COVER_R,
                                glass, screen_c, axis="Y", location=(0, front_y, 0),
                                edge_bevel=0.00006, outline_segments=48)
active_cut = outward_prism("SCREEN_ACTIVE_CUTTER", SCREEN_W + 0.12*MM, SCREEN_H + 0.12*MM,
                              GLASS_T + 0.25*MM, SCREEN_R + 0.06*MM, None, detail_c, axis="Y",
                              location=(0, front_y, 0), outline_segments=48)
fc.boolean_difference(screen_glass, active_cut, name="CUT_ACTIVE_AREA")

front_hardware_z = H*0.5 - 7.79*MM
cam_x = 6.72*MM

screen_content = rounded_rect_strip_prism_y(
    "SCREEN_CONTENT",
    SCREEN_W,
    SCREEN_H,
    GLASS_T - 0.025*MM,
    SCREEN_R,
    screen_mat,
    screen_c,
    location=(0, front_y + 0.010*MM, 0),
    segments=16,
)

# SCREEN_CONTENT stays clean replaceable artwork. Physical front hardware is
# independent geometry above it at the official Apple datum.

# Planar UVs map the real raster screen image to the active display surface.
# Boolean cutters can leave empty material slots behind; normalize the screen to exactly
# two explicit slots before assigning front faces vs cut/edge walls.
screen_edge_mat = fc.make_material("MAT_SCREEN_EDGE", (0.001, 0.0012, 0.0015), 0.0, 0.36)
screen_content.data.materials.clear()
screen_content.data.materials.append(screen_mat)
screen_content.data.materials.append(screen_edge_mat)
for polygon in screen_content.data.polygons:
    # In Blender the display faces -Y; the export maps that to Three.js +Z.
    polygon.material_index = 0 if polygon.normal.y < -0.995 else 1
while screen_content.data.uv_layers:
    screen_content.data.uv_layers.remove(screen_content.data.uv_layers[0])
uv = screen_content.data.uv_layers.new(name="UVMap")
screen_content.data.uv_layers.active = uv
for loop in screen_content.data.loops:
    co = screen_content.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv = ((co.x / SCREEN_W) + 0.5, (co.z / SCREEN_H) + 0.5)
glow_anchor = fc.empty("SCREEN_GLOW_ANCHOR", ctrl_c, location=(0, front_surface - 1.0*MM, 0))
glow_anchor["screen_on_energy"] = 8.0
glow_anchor["glow_type"] = "rect_area"
glow_anchor["glow_width_m"] = SCREEN_W
glow_anchor["glow_height_m"] = SCREEN_H
screen_content["screen_state"] = "screen_on"; screen_content["screen_on_emission"] = 0.85; screen_content["screen_off_emission"] = 0.0

def hard_surface_glass(obj):
    bevel = obj.modifiers.get("EDGE_BEVEL")
    if bevel:
        bevel.harden_normals = True
    for poly in obj.data.polygons[2:]:
        poly.use_smooth = True
    weighted = obj.modifiers.new("WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    weighted.weight = 50

for poly in back_glass.data.polygons:
    poly.use_smooth = False
hard_surface_glass(screen_glass)
# Screen material doubles as the clean glossy active glass surface for the current publishable LOW asset.
sbsdf = screen_mat.node_tree.nodes.get("Principled BSDF")
sbsdf.inputs["Coat Weight"].default_value = 0.0
sbsdf.inputs["Coat Roughness"].default_value = 0.035

# The physical masks sit behind the display front plane and are revealed only through
# the two screen cutouts. The orange privacy indicator remains screen-state artwork.
screen_front_y = (front_y + 0.010*MM) - (GLASS_T - 0.025*MM) * 0.5
front_hardware_y = screen_front_y + 0.034*MM
front_optics_y = front_hardware_y + 0.040*MM
outward_prism("FRONT_SENSOR_MASK", 7.10*MM, 2.30*MM, 0.008*MM, 1.15*MM,
              under_glass_mat, detail_c, axis="Y",
              location=(-4.15*MM, front_hardware_y, front_hardware_z), outline_segments=64)
fc.cylinder("FRONT_CAMERA_MASK", 1.15*MM, 0.008*MM, under_glass_mat, detail_c,
            (cam_x, front_hardware_y, front_hardware_z), axis="Y", vertices=128)
fc.cylinder("FRONT_CAMERA_GLASS", 0.84*MM, 0.006*MM, front_optic, detail_c,
            (cam_x, front_optics_y, front_hardware_z), axis="Y", vertices=128)
fc.cylinder("FRONT_CAMERA_INNER", 0.52*MM, 0.005*MM, black, detail_c,
            (cam_x, front_hardware_y + 0.055*MM, front_hardware_z), axis="Y", vertices=96)
fc.cylinder("FRONT_CAMERA_IRIS", 0.28*MM, 0.004*MM, front_optic, detail_c,
            (cam_x, front_hardware_y + 0.070*MM, front_hardware_z), axis="Y", vertices=80)
fc.cylinder("FRONT_CAMERA_PUPIL", 0.12*MM, 0.003*MM, black, detail_c,
            (cam_x, front_hardware_y + 0.085*MM, front_hardware_z), axis="Y", vertices=64)
receiver = fc.rounded_cube("FRONT_RECEIVER_MIC", (14.02*MM, 0.020*MM, 0.30*MM), 0.14*MM, black, detail_c, location=(0, front_surface - 0.012*MM, H*0.5 - 0.62*MM))

housing_x = CAM_CENTER_X
housing_z = CAM_CENTER_Z
# Detail D is a pair of concentric vertical capsules, not a small-radius rounded rectangle.
# Apple iPhone 17 Dimensional Drawings, side view: back glass to camera plateau = 1.78 mm,
# back glass to camera glass = 3.45 mm. Keep those external surfaces authoritative.
CAMERA_PLATEAU_PROTRUSION = 1.78 * MM
CAMERA_GLASS_PROTRUSION = 3.45 * MM
housing_seat = camera_mesh("CAMERA_HOUSING_SEAT", CAM_OUTER_W, CAM_OUTER_H, 0.30*MM,
                          camera_seat_mat, detail_c, (housing_x, D*0.5 + 0.15*MM, housing_z), capsule=True)
housing = camera_mesh("CAMERA_HOUSING", CAM_INNER_W, CAM_INNER_H, CAMERA_PLATEAU_PROTRUSION,
                     camera_housing_mat, detail_c, (housing_x, D*0.5 + CAMERA_PLATEAU_PROTRUSION*0.5, housing_z), capsule=True)
attach_camera_normal(camera_seat_mat, 'seat')
attach_camera_normal(camera_housing_mat, 'housing')
# Keep shared rail/inner-optics material response independent of camera bakes.
camera_ring_mat = metal_dark.copy()
camera_ring_mat.name = 'MAT_CAMERA_RING'
camera_bevel_mat = metal.copy()
camera_bevel_mat.name = 'MAT_CAMERA_BEVEL'
for material, part in ((camera_ring_mat, 'ring'), (camera_bevel_mat, 'bevel')):
    attach_camera_normal(material, part)
for idx,(x_mm,z_mm) in enumerate((((W*0.5-CAM_CENTER_X_REF)/MM,(H*0.5-13.62*MM)/MM),((W*0.5-CAM_CENTER_X_REF)/MM,(H*0.5-31.34*MM)/MM)),1):
    seat=fc.cylinder(f"CAMERA_{idx}_SEAT",8.18*MM,0.14*MM,gap_mat,detail_c,(x_mm*MM,D*0.5+1.70*MM,z_mm*MM),axis="Y",vertices=192); seat.hide_render=True
    ring = camera_mesh(f"CAMERA_{idx}_RING",16.00*MM,16.00*MM,1.10*MM,camera_ring_mat,detail_c,(x_mm*MM,D*0.5+2.20*MM,z_mm*MM))
    ring_bevel = camera_mesh(f"CAMERA_{idx}_BEVEL",14.88*MM,14.88*MM,0.70*MM,camera_bevel_mat,detail_c,(x_mm*MM,D*0.5+2.75*MM,z_mm*MM))
    camera_glass = camera_mesh(f"CAMERA_{idx}_GLASS",13.62*MM,13.62*MM,0.70*MM,lens_glass,detail_c,(x_mm*MM,D*0.5+CAMERA_GLASS_PROTRUSION-0.35*MM,z_mm*MM))
    fc.cylinder(f"CAMERA_{idx}_INNER",5.20*MM,0.09*MM,black,detail_c,(x_mm*MM,D*0.5+3.22*MM,z_mm*MM),axis="Y",vertices=160)
    fc.cylinder(f"CAMERA_{idx}_IRIS",3.00*MM,0.070*MM,lens_glass,detail_c,(x_mm*MM,D*0.5+3.26*MM,z_mm*MM),axis="Y",vertices=128)
    fc.cylinder(f"CAMERA_{idx}_PUPIL",1.18*MM,0.045*MM,black,detail_c,(x_mm*MM,D*0.5+3.30*MM,z_mm*MM),axis="Y",vertices=96)
fc.cylinder("REAR_MIC",0.50*MM,0.14*MM,black,detail_c,((W*0.5-20.54*MM),D*0.5+1.02*MM,(H*0.5-22.48*MM)),axis="Y",vertices=80)
fc.cylinder("FLASH_RING",3.30*MM,0.12*MM,metal_dark,detail_c,((W*0.5-30.41*MM),D*0.5+0.30*MM,CAM_CENTER_Z),axis="Y",vertices=128)
flash = fc.cylinder("FLASH",3.14*MM,0.14*MM,flash_mat,detail_c,((W*0.5-30.41*MM),D*0.5+0.43*MM,CAM_CENTER_Z),axis="Y",vertices=128)
# Cylinder mesh stays in local XY; object rotation puts its face on the rear Y plane.
flash_uv = flash.data.uv_layers.active or flash.data.uv_layers.new(name="UVMap")
for loop in flash.data.loops:
    co = flash.data.vertices[loop.vertex_index].co
    flash_uv.data[loop.index].uv = (co.x / (6.28*MM) + 0.5, co.y / (6.28*MM) + 0.5)

# Apple mark decal. Bounding box and vertical datum follow the Apple dimensional drawing.
logo_img_path = os.path.join(HERE, "reference", "apple_logo_glb_mask.png")
logo_mat = bpy.data.materials.new("MAT_APPLE_LOGO_DECAL")
logo_mat.use_nodes = True
nodes = logo_mat.node_tree.nodes
links = logo_mat.node_tree.links
for node in list(nodes):
    nodes.remove(node)
out = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
tex = nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(logo_img_path, check_existing=True)
bsdf.inputs["Base Color"].default_value = (0.14, 0.15, 0.17, 1.0)
bsdf.inputs["Roughness"].default_value = 0.16
bsdf.inputs["Coat Weight"].default_value = 0.12
bsdf.inputs["Coat Roughness"].default_value = 0.045
bsdf.inputs["Metallic"].default_value = 0.86
logo_mat.use_backface_culling = True
links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
try:
    logo_mat.surface_render_method = "DITHERED"
except Exception:
    pass
lw, lh = 15.75*MM, 19.34*MM
verts = [(-lw/2,0,-lh/2),(lw/2,0,-lh/2),(lw/2,0,lh/2),(-lw/2,0,lh/2)]
mesh = bpy.data.meshes.new("APPLE_LOGO_MESH")
mesh.from_pydata(verts, [], [(0,3,2,1)])
mesh.update()
logo = bpy.data.objects.new("APPLE_LOGO_DECAL", mesh)
detail_c.objects.link(logo)
logo.location = (0, D*0.5 + 0.050*MM, (H*0.5 - 73.18*MM))
logo.data.materials.append(logo_mat)
uv = mesh.uv_layers.new(name="UVMap")
for loop, coord in zip(mesh.loops, ((1,0),(1,1),(0,1),(0,0))):
    uv.data[loop.index].uv = coord

boolean_cuts = ["DISPLAY_POCKET", "SCREEN_ACTIVE"]

def capsule_prism_x(name, face_width, length, depth, radius, material, collection):
    outline = fc.rounded_outline(face_width, length, radius, segments=20)
    n = len(outline)
    verts = [(-depth*0.5,y,z) for y,z in outline] + [(depth*0.5,y,z) for y,z in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    mesh=bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj)
    if material: obj.data.materials.append(material)
    return obj

def physical_side_button(name, edge, z_mm, length_mm, face_width_mm=2.56, protrusion_mm=0.45, material=metal):
    cw=(face_width_mm+0.38)*MM; cl=(length_mm+0.56)*MM
    cutter=capsule_prism_x(f"{name}_CUTTER",cw,cl,0.92*MM,cw*0.5,None,detail_c)
    fc.place_on_rounded_edge(cutter,W,H,BODY_R,edge,z_mm*MM,outward=-0.30*MM,local_normal=(1,0,0))
    fc.boolean_difference(body,cutter,name=f"CUT_{name}"); boolean_cuts.append(name)
    thickness=0.40*MM; fw=face_width_mm*MM
    button=capsule_prism_x(name,fw,length_mm*MM,thickness,fw*0.5,material,detail_c)
    fc.place_on_rounded_edge(button,W,H,BODY_R,edge,z_mm*MM,outward=protrusion_mm*MM-thickness*0.5,local_normal=(1,0,0))
    fc.add_bevel(button,0.025*MM,segments=3)
    return button

def camera_control(edge,z_mm,length_mm=17.10,face_width_mm=3.03,recess_mm=0.10):
    return physical_side_button("CAMERA_CONTROL",edge,z_mm,length_mm,face_width_mm,-recess_mm,camera_control_mat)

physical_side_button("ACTION_BUTTON","LEFT",40.72,6.90,2.66,0.45)
physical_side_button("VOL_UP","LEFT",26.57,11.20,2.66,0.45)
physical_side_button("VOL_DOWN","LEFT",12.37,11.20,2.66,0.45)
physical_side_button("SIDE_BUTTON","RIGHT",19.48,17.70,2.66,0.45)
camera_control("RIGHT",-23.40,17.10,3.03,0.10)
for side, edge in (("L", "LEFT"), ("R", "RIGHT")):
    for z_mm in (55.0, -55.0):
        strip = fc.rounded_cube(f"ANTENNA_SIDE_{side}_{int(z_mm)}", (0.10*MM, 1.02*MM, 4.3*MM),
                                0.06*MM, black, detail_c)
        fc.place_on_rounded_edge(strip, W, H, BODY_R, edge, z_mm*MM, outward=-0.018*MM, local_normal=(1,0,0))

usb_cutter = fc.rounded_cube("USB_C_CUTTER", (8.99*MM, 3.00*MM, 1.82*MM), 0.91*MM, None, detail_c)
fc.place_on_rounded_edge(usb_cutter, W, H, BODY_R, "BOTTOM", 0.0, outward=-0.70*MM, local_normal=(0,0,1))
fc.boolean_difference(body, usb_cutter, name="CUT_USB_C")
boolean_cuts.append("USB_C")
usb_cavity = fc.rounded_cube("USB_C_CAVITY", (8.45*MM, 2.38*MM, 0.12*MM), 0.04*MM, grille_mat, detail_c)
fc.place_on_rounded_edge(usb_cavity, W, H, BODY_R, "BOTTOM", 0.0, outward=-1.40*MM, local_normal=(0,0,1))
usb_tongue = fc.rounded_cube("USB_C_TONGUE", (5.25*MM, 0.48*MM, 0.18*MM), 0.08*MM, metal_dark, detail_c)
fc.place_on_rounded_edge(usb_tongue, W, H, BODY_R, "BOTTOM", 0.0, outward=-0.80*MM, local_normal=(0,0,1))

def bottom_aperture(name, x_mm):
    cutter = fc.cylinder(f"{name}_CUTTER", 0.675*MM, 1.80*MM, None, detail_c, vertices=40)
    fc.place_on_rounded_edge(cutter, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.52*MM, local_normal=(0,0,1))
    fc.boolean_difference(body, cutter, name=f"CUT_{name}")
    boolean_cuts.append(name)
    cavity = fc.cylinder(name, 0.675*MM, 0.12*MM, grille_mat, detail_c, vertices=40)
    fc.place_on_rounded_edge(cavity, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.98*MM, local_normal=(0,0,1))
    smooth_sharp_boundaries(cavity)

# Apple Detail C: 8 x Ø1.35 acoustic ports total = 3 microphone + 5 speaker.
# Drawing X datums are measured from product left; convert to centered model coordinates.
for idx, from_left_mm in enumerate((19.71, 21.965, 24.22), 1):
    bottom_aperture(f"BOTTOM_MIC_APERTURE_{idx:02d}", from_left_mm - 71.45*0.5)
for idx, from_left_mm in enumerate((47.23, 49.485, 51.74, 53.995, 56.25), 1):
    bottom_aperture(f"BOTTOM_SPEAKER_APERTURE_{idx:02d}", from_left_mm - 71.45*0.5)

for side, from_left_mm in (("L", 28.80), ("R", 42.65)):
    x_mm = from_left_mm - 71.45*0.5
    recess = fc.cylinder(f"BOTTOM_SCREW_{side}_RECESS", 0.78*MM, 0.90*MM, None, detail_c, vertices=48)
    fc.place_on_rounded_edge(recess, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.38*MM, local_normal=(0,0,1))
    fc.boolean_difference(body, recess, name=f"CUT_SCREW_{side}")
    boolean_cuts.append(f"SCREW_{side}")
    screw = fc.cylinder(f"BOTTOM_SCREW_{side}", 0.75*MM, 0.24*MM, screw_mat, detail_c, vertices=48)
    fc.place_on_rounded_edge(screw, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.15*MM, local_normal=(0,0,1))

bev = fc.add_bevel(body, 0.00022, segments=4)
bev.harden_normals = True
smooth_sharp_boundaries(body)
body_wn = body.modifiers.new("WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
body_wn.keep_sharp = True
body_wn.weight = 50
root = fc.empty("CTRL_IPHONE_17", ctrl_c)
glow_anchor.parent = root
for collection in (body_c, detail_c, screen_c):
    for obj in collection.objects:
        obj.parent = root
root["asset_id"] = "iphone_17"
root["asset_version"] = "low_v30_1.1"
root["stage"] = "LOW_DRAFT"
root["dimensions_mm"] = "71.5 x 149.6 x 7.95"
root["screen_object"] = "SCREEN_CONTENT"
root["screen_texture"] = "reference/ios26_home_screen_clean_1206x2622.png"
root["screen_texture_source"] = "Apple Support iPhone User Guide, iOS 26 official Home Screen"
root["screen_texture_source_url"] = "https://help.apple.com/assets/69F8EBBDF3B89A4F6E0C704C/69F8EBC43862495245036393/en_US/b86263df3b70efb72926baf8a54550bd.png"
root["screen_texture_px"] = "1206 x 2622"
root["screen_state_default"] = "screen_on"
root["screen_on_emission_strength"] = 0.85
root["screen_off_emission_strength"] = 0.0
root["screen_glow_energy"] = 8.0
root["screen_glow_type"] = "rect_area"
root["surface_aware_controls"] = True
root["surface_aware_bottom"] = True
root["real_display_pocket"] = True
root["front_camera_present"] = True
root["front_camera_keepout_mm"] = "20.75 x 5.12"
root["front_camera_center_from_top_mm"] = 7.79
root["apple_logo_decal"] = True
root["rear_camera_outer_diameter_mm"] = 16.0
root["rear_camera_optical_diameter_mm"] = 13.62
root["publish_preview_material"] = "black_anodized"
root["default_colorway"] = "black"
root["colorway_variants"] = "black,white,mist_blue,sage,lavender"
root["colorway_reference"] = "Apple iPhone 17 official finishes: Black, White, Mist Blue, Sage, Lavender"
root["colorway_tints"] = "render-calibrated approximations from official Apple product imagery; names are authoritative, RGB values are not factory colorimetry"
root["pbr_surface_maps"] = "anodized_aluminum normal+roughness; back_glass normal+roughness; pentalobe_fastener normal+roughness"
root["fastener_head_detail"] = "pentalobe tangent-space normal map"
root["source_drawing"] = "Apple iPhone 17 Dimensional Drawings 2025-09-09"
root["cover_glass_mm"] = "69.45 x 147.61"
root["display_active_area_mm"] = "66.57 x 144.79"
root["button_top_datums_mm"] = "34.08, 48.23, 62.43, 55.32, 98.20"
root["bottom_layout"] = "3_mic + usb_c + 5_speaker"
root["apple_logo_decal"] = "reference/apple_logo_glb_mask.png"

studio = fc.make_collection("_STUDIO_RIG")
fc.add_area_light("KEY_SOFTBOX", (0.30, -0.22, 0.25), 82, 0.38, studio, target=(0,0,0.020))
fc.add_area_light("FILL_SOFTBOX", (-0.24, -0.14, 0.02), 14, 0.32, studio, target=(0,0,0.0))
fc.add_area_light("RIM_STRIP", (0.22, 0.26, 0.13), 94, 0.14, studio, target=(0,0,0.015))
fc.add_area_light("TOP_STRIP", (-0.10, 0.03, 0.34), 42, 0.28, studio, target=(0,0,0.035))

camera_c = fc.make_collection("_DIAGNOSTIC_CAMERAS")
def persp(name, location, target, lens=78):
    data = bpy.data.cameras.new(name)
    data.type = "PERSP"
    data.lens = lens
    data.sensor_width = 36.0
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    cam.rotation_euler = (fc.Vector(target) - fc.Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera_c.objects.link(cam)
    return cam

cam_front = persp("CAM_FRONT", (0, -0.42, 0), (0,0,0), 92)
cam_back = persp("CAM_BACK", (0, 0.42, 0), (0,0,0), 92)
cam_three = persp("CAM_THREE_QUARTER", (0.20, -0.30, 0.15), (0,0,0.010), 82)
cam_left = persp("CAM_LEFT_SIDE", (-0.22, -0.07, 0.020), (-W*0.48,0,0.020), 92)
cam_right = persp("CAM_RIGHT_SIDE", (0.22, -0.07, -0.004), (W*0.48,0,-0.004), 92)
cam_bottom = persp("CAM_BOTTOM_MACRO", (0.0, -0.055, -0.185), (0,0,-H*0.495), 70)
cam_screen = persp("CAM_SCREEN_EDGE_MACRO", (0.095, -0.13, 0.096), (W*0.39,front_surface,H*0.40), 110)
cam_camera = persp("CAM_CAMERA_MACRO", (0.070, 0.18, 0.100), (0.020,0.004,0.052), 115)
cam_front_sensor = persp("CAM_FRONT_SENSOR_MACRO", (0.0, -0.125, 0.082), (0, front_surface, front_hardware_z), 120)
cam_back_three = persp("CAM_BACK_THREE_QUARTER", (0.18, 0.30, 0.13), (0.010,0.002,0.020), 84)

# Deterministic UVs for exported finish maps. Use local-space box projection so
# material variants can change color without invalidating surface detail.
for name, tile_mm in (
    ("BODY_ALUMINUM", 4.0),
    ("BACK_GLASS", 6.0),
    ("ACTION_BUTTON", 2.0),
    ("VOL_UP", 2.0),
    ("VOL_DOWN", 2.0),
    ("SIDE_BUTTON", 2.0),
    ("CAMERA_CONTROL", 2.0),
    ("USB_C_TONGUE", 2.0),
    ("BOTTOM_SCREW_L", 1.50),
    ("BOTTOM_SCREW_R", 1.50),
):
    ensure_box_uv(bpy.data.objects[name], tile_mm, replace=True)

bpy.context.view_layer.update()

assembly = (body, back_glass, screen_glass)
mins = [1e9, 1e9, 1e9]
maxs = [-1e9, -1e9, -1e9]
for obj in assembly:
    for corner in obj.bound_box:
        p = obj.matrix_world @ fc.Vector(corner)
        for axis in range(3):
            mins[axis] = min(mins[axis], p[axis])
            maxs[axis] = max(maxs[axis], p[axis])
actual_mm = {"width": (maxs[0]-mins[0])/MM, "depth": (maxs[1]-mins[1])/MM, "height": (maxs[2]-mins[2])/MM}
expected_mm = {"width": 71.45, "depth": 7.95, "height": 149.61}
delta_mm = {k: actual_mm[k] - expected_mm[k] for k in expected_mm}

bm = bmesh.new()
bm.from_mesh(body.data)
non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
body_vertices = len(bm.verts)
body_faces = len(bm.faces)
bm.free()
mandatory = [
    "BODY_ALUMINUM", "SCREEN_GLASS", "SCREEN_CONTENT", "DISPLAY_BEZEL", "DISPLAY_GLASS_SEAT",
    "FRONT_SENSOR_MASK", "FRONT_CAMERA_MASK", "FRONT_CAMERA_GLASS", "FRONT_CAMERA_IRIS", "FRONT_CAMERA_PUPIL", "FRONT_RECEIVER_MIC", "APPLE_LOGO_DECAL",
    "ACTION_BUTTON", "VOL_UP", "VOL_DOWN", "SIDE_BUTTON", "CAMERA_CONTROL",
    "USB_C_CAVITY", "BOTTOM_MIC_APERTURE_03", "BOTTOM_SPEAKER_APERTURE_05",
    "CAMERA_HOUSING_SEAT", "CAMERA_HOUSING", "CAMERA_1_GLASS", "CAMERA_2_GLASS", "FLASH", "REAR_MIC"
]
missing = [name for name in mandatory if bpy.data.objects.get(name) is None]
forbidden = [name for name in ("FRONT_SENSOR_L", "FRONT_SENSOR_R", "FRONT_SENSOR_DOT") if bpy.data.objects.get(name) is not None]
expected_boolean_cuts = 2 + 5 + 1 + 8 + 2
back_outer_y = back_glass.location.y + max(v.co.y for v in back_glass.data.vertices)
backing_outer_y = housing_seat.location.y + max(v.co.y for v in housing_seat.data.vertices)
camera_backing_protrusion_mm = (backing_outer_y - back_outer_y) / MM
rail_outer_x = W * 0.5
button_protrusions_mm = []
for control_name in ("ACTION_BUTTON", "VOL_UP", "VOL_DOWN", "SIDE_BUTTON"):
    control = bpy.data.objects[control_name]
    outer_x = max(abs((control.matrix_world @ fc.Vector(corner)).x) for corner in control.bound_box)
    button_protrusions_mm.append((outer_x - rail_outer_x) / MM)
button_protrusion_mm = min(button_protrusions_mm)
cc = bpy.data.objects["CAMERA_CONTROL"]
cc_outer_x = max(abs((cc.matrix_world @ fc.Vector(corner)).x) for corner in cc.bound_box)
camera_control_offset_mm = (cc_outer_x - rail_outer_x) / MM
camera_control_recess_mm = max(0.0, -camera_control_offset_mm)
front_camera_center_from_top_mm = (H * 0.5 - front_hardware_z) / MM
passed = (
    non_manifold == 0
    and not missing
    and not forbidden
    and len(boolean_cuts) == expected_boolean_cuts
    and all(abs(v) <= 0.01 for v in delta_mm.values())
    and camera_backing_protrusion_mm >= 0.25
    and button_protrusion_mm >= 0.45
    and 0.075 <= camera_control_recess_mm <= 0.125
    and abs(front_camera_center_from_top_mm - 7.79) <= 0.01
)
evidence = {
    "asset_id": "iphone_17",
    "stage": "LOW_DRAFT",
    "revision": "production_camera_controls_v30",
    "blender_version": bpy.app.version_string,
    "expected_mm": expected_mm,
    "actual_mm": {k: round(v, 6) for k, v in actual_mm.items()},
    "delta_mm": {k: round(v, 6) for k, v in delta_mm.items()},
    "body_non_manifold_edges": non_manifold,
    "body_vertices": body_vertices,
    "body_faces": body_faces,    "boolean_cuts": boolean_cuts,
    "boolean_cut_count": len(boolean_cuts),
    "mandatory_missing": missing,
    "forbidden_front_nodes": forbidden,
    "object_count": len(bpy.data.objects),
    "material_count": len(bpy.data.materials),
    "official_reference": "Apple iPhone 17 Dimensional Drawings 2025-09-09",
    "cover_glass_mm": [69.45, 147.61],
    "display_active_area_mm": [66.57, 144.79],
    "camera_backing_protrusion_mm": round(camera_backing_protrusion_mm, 4),
    "camera_backing_visible": not housing_seat.hide_render,
    "button_min_protrusion_mm": round(button_protrusion_mm, 4),
    "camera_control_protrusion_mm": max(0.0, round(camera_control_offset_mm, 4)),
    "camera_control_recess_mm": round(camera_control_recess_mm, 4),
    "front_camera_keepout_mm": [20.75, 5.12],
    "front_camera_center_from_top_mm": round(front_camera_center_from_top_mm, 4),
    "passed": passed,
}
os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
with open(EVIDENCE, "w", encoding="utf-8", newline="\n") as handle:
    json.dump(evidence, handle, indent=2)

fc.save_blend(OUT)
renders = (
    (cam_front, "iphone_17_low_v30_front.png"),
    (cam_back, "iphone_17_low_v30_back.png"),
    (cam_three, "iphone_17_low_v30_three_quarter.png"),
    (cam_left, "iphone_17_low_v30_left_side.png"),
    (cam_right, "iphone_17_low_v30_right_side.png"),
    (cam_bottom, "iphone_17_low_v30_bottom_macro.png"),
    (cam_screen, "iphone_17_low_v30_screen_edge_macro.png"),
    (cam_camera, "iphone_17_low_v30_camera_macro.png"),
    (cam_front_sensor, "iphone_17_low_v30_front_sensor_macro.png"),
    (cam_back_three, "iphone_17_low_v30_back_three_quarter.png"),
)
def set_light(name, energy):
    obj = bpy.data.objects.get(name)
    if obj and getattr(obj, "data", None):
        obj.data.energy = energy

def render_profile(cam, filename):
    if "back" in filename or "camera_macro" in filename:
        profile = {"KEY_SOFTBOX": 38, "FILL_SOFTBOX": 7, "RIM_STRIP": 32, "TOP_STRIP": 16}
    elif "front_sensor_macro" in filename:
        profile = {"KEY_SOFTBOX": 118, "FILL_SOFTBOX": 24, "RIM_STRIP": 46, "TOP_STRIP": 34}
    else:
        profile = {"KEY_SOFTBOX": 82, "FILL_SOFTBOX": 14, "RIM_STRIP": 94, "TOP_STRIP": 42}
    for light_name, energy in profile.items():
        set_light(light_name, energy)
    fc.render_camera(cam, os.path.join(PREVIEWS, filename))

if '--skip-previews' not in sys.argv:
    for cam, filename in renders:
        render_profile(cam, filename)
print("AWFUL_IPHONE17_V30_VALIDATION", json.dumps(evidence, sort_keys=True))
if not passed:
    raise RuntimeError("iPhone 17 LOW v30 validation failed")
