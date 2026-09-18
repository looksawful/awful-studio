import json
import os
import bpy
from mathutils import Vector

import sys

def cli(flag, default=None):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default

SOURCE_REVISION = cli("--source-revision", "")
SOURCE_COMMIT = cli("--source-commit", "")
if len(SOURCE_REVISION) != 64:
    raise RuntimeError("--source-revision must be a SHA-256 fingerprint")
HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(HERE, "runtime", "v30")
os.makedirs(RUNTIME, exist_ok=True)
root = bpy.data.objects.get("CTRL_IPHONE_17")
if root is None:
    raise RuntimeError("CTRL_IPHONE_17 missing")
for cname in ("_STUDIO_RIG", "_DIAGNOSTIC_CAMERAS"):
    col = bpy.data.collections.get(cname)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
for obj in list(bpy.data.objects):
    if obj.type == "MESH" and obj.hide_render and obj.parent == root:
        bpy.data.objects.remove(obj, do_unlink=True)
runtime_logo = os.path.join(HERE, "reference", "apple_logo_glb_mask.png")
logo_mat = bpy.data.materials.get("MAT_APPLE_LOGO_DECAL")
if logo_mat and logo_mat.use_nodes:
    for node in logo_mat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            node.image = bpy.data.images.load(runtime_logo, check_existing=True)
            break
for obj in [root] + list(root.children_recursive):
    if obj.type == "MESH":
        obj.data.name = obj.name
roles = {
    "BODY_ALUMINUM": "body",
    "SCREEN_CONTENT": "screen",
    "SCREEN_GLASS": "screen_glass",
    "DYNAMIC_ISLAND": "front_sensor_cluster",
    "FRONT_SENSOR_PILL": "front_sensor",
    "FRONT_CAMERA_GLASS": "front_camera_optic",
    "ACTION_BUTTON": "control",
    "VOL_UP": "control",
    "VOL_DOWN": "control",
    "SIDE_BUTTON": "control",
    "CAMERA_CONTROL": "control",
    "USB_C_CAVITY": "port",
    "CAMERA_HOUSING": "camera_housing",
    "CAMERA_1_GLASS": "camera_optic",
    "CAMERA_2_GLASS": "camera_optic",
}
for name, role in roles.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj["runtime_role"] = role
        obj["interactable"] = role in {"screen", "control"}
def anchor(name, location):
    obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if not obj.users_collection:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.location = location
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.006
    return obj
anchor("ANCHOR_CENTER", (0.0, 0.0, 0.0))
anchor("ANCHOR_BOTTOM_CENTER", (0.0, 0.0, -0.0748))
anchor("ANCHOR_SCREEN_CENTER", (0.0, -0.003975, 0.0))
anchor("SCREEN_GLOW_ANCHOR", (0.0, -0.004975, 0.0))
camera_housing = bpy.data.objects.get("CAMERA_HOUSING")
anchor("ANCHOR_REAR_CAMERA", (camera_housing.location.x, 0.003975, camera_housing.location.z))
root["runtime_format"] = "glTF 2.0 / GLB"
root["runtime_units"] = "meters"
root["source_up_axis"] = "+Z"
root["source_forward_axis"] = "-Y"
root["runtime_up_axis"] = "+Y"
root["runtime_forward_axis"] = "+Z"
root["runtime_pivot"] = "ANCHOR_CENTER"
root["runtime_bottom_anchor"] = "ANCHOR_BOTTOM_CENTER"
root["runtime_screen_anchor"] = "ANCHOR_SCREEN_CENTER"
root["runtime_camera_anchor"] = "ANCHOR_REAR_CAMERA"
root["runtime_lod"] = "LOD0"
root["delivery_version"] = "v30"
root["delivery_stage"] = "LOW_DRAFT"
root["delivery_source_revision"] = SOURCE_REVISION
root["delivery_source_commit"] = SOURCE_COMMIT
for obj in bpy.context.selected_objects:
    obj.select_set(False)
exported = []
for obj in [root] + list(root.children_recursive):
    if obj.type in {"MESH", "EMPTY"} and not obj.hide_render and obj.name != "SCREEN_GLASS":
        obj.select_set(True)
        exported.append(obj.name)
bpy.context.view_layer.objects.active = root
glb = os.path.join(RUNTIME, "iphone_17_v30_web.glb")
bpy.ops.export_scene.gltf(
    filepath=glb,
    export_format="GLB",
    use_selection=True,
    export_extras=True,
)
bpy.ops.file.pack_all()
delivery = os.path.join(RUNTIME, "iphone_17_v30_delivery.blend")
bpy.ops.wm.save_as_mainfile(filepath=delivery)
mesh_objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name in exported]
materials = sorted({m.name for o in mesh_objs for m in o.data.materials if m})
points = []
for obj in mesh_objs:
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        points.append((world.x, world.z, -world.y))
runtime_min = [min(p[i] for p in points) for i in range(3)]
runtime_max = [max(p[i] for p in points) for i in range(3)]
runtime_size_mm = [round((runtime_max[i] - runtime_min[i]) * 1000.0, 3) for i in range(3)]
manifest = {
    "asset_id": "iphone_17",
    "version": "v30",
    "stage": "LOW_DRAFT",
    "source_blend": "generated/iphone_17_low_v30.blend",
    "delivery_blend": "runtime/v30/iphone_17_v30_delivery.blend",
    "glb": "runtime/v30/iphone_17_v30_web.glb",
    "body_dimensions_mm": [71.45, 149.61, 7.95],
    "dimension_order": ["width_x", "height_y", "depth_z"],
    "runtime_bounds_mm": runtime_size_mm,
    "units": "meters",
    "source_up_axis": "+Z",
    "source_forward_axis": "-Y",
    "up_axis": "+Y",
    "forward_axis": "+Z",
    "root": "CTRL_IPHONE_17",
    "screen_object": "SCREEN_CONTENT",
    "anchors": ["ANCHOR_CENTER", "ANCHOR_BOTTOM_CENTER", "ANCHOR_SCREEN_CENTER", "ANCHOR_REAR_CAMERA", "SCREEN_GLOW_ANCHOR"],
    "screen_states": {
        "screen_off": {"emission_strength": 0.0, "glow_intensity": 0.0},
        "screen_on": {"emission_strength": 0.85, "glow_intensity": 1.0},
    },
    "screen_glow": {"anchor": "SCREEN_GLOW_ANCHOR", "type": "rect_area", "width_mm": 66.57, "height_mm": 144.79, "source_energy_w": 8.0},
    "lods": [{"name": "LOD0", "file": "iphone_17_v30_web.glb"}],
    "materials": materials,
    "exported_objects": exported,
    "runtime_roles": roles,
    "threejs_loader": "GLTFLoader",
    "requires_meshopt_decoder": False,
    "web_variants": {
        "compat": {"file": "iphone_17_v30_web.glb", "requires": []},
    },
    "camera_fit": "runtime_bounds",
    "source_reference": "Apple iPhone 17 Dimensional Drawings 2025-09-09",
    "source_revision": SOURCE_REVISION,
    "source_commit": SOURCE_COMMIT,
    "generator_version": "web_delivery_camera_logo_normals_v30",
    "delivery_profile": {"simplification": "none", "compression": "compat+meshopt", "node_preservation": "required"},
}
with open(os.path.join(RUNTIME, "iphone_17_v30.asset.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(manifest, f, indent=2)
print("AWFUL_IPHONE17_V30_RUNTIME_EXPORT", json.dumps({
    "glb": glb,
    "delivery": delivery,
    "objects": len(exported),
    "materials": len(materials),
    "glb_bytes": os.path.getsize(glb),
}, sort_keys=True))
