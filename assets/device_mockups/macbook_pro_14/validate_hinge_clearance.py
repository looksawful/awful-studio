import bmesh
import bpy
import json
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(flag, default):
    return argv[argv.index(flag) + 1] if flag in argv else default


OUT = os.path.abspath(
    arg(
        "--out",
        os.path.join(os.path.dirname(bpy.data.filepath), "hinge_clearance.json"),
    )
)
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
ANGLES = (0, 30, 60, 90, 102)
MAX_INTERSECTION_MM3 = 0.01
PAIRS = (
    ("barrel_l_base", "HINGE_BARREL_L", "BASE_UNIBODY"),
    ("barrel_r_base", "HINGE_BARREL_R", "BASE_UNIBODY"),
    ("cover_l_base", "HINGE_COVER_L", "BASE_UNIBODY"),
    ("cover_r_base", "HINGE_COVER_R", "BASE_UNIBODY"),
    ("cover_l_barrel", "HINGE_COVER_L", "HINGE_BARREL_L"),
    ("cover_r_barrel", "HINGE_COVER_R", "HINGE_BARREL_R"),
)
scene = bpy.context.scene
hinge = bpy.data.objects["CTRL_HINGE"]


def baked_copy(name, suffix):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    source = bpy.data.objects[name].evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(source, depsgraph=depsgraph)
    mesh.transform(source.matrix_world)
    obj = bpy.data.objects.new(f"_HINGE_CHECK_{suffix}", mesh)
    scene.collection.objects.link(obj)
    return obj


def intersection_volume_mm3(a_name, b_name, suffix):
    a = baked_copy(a_name, suffix + "_a")
    b = baked_copy(b_name, suffix + "_b")
    modifier = a.modifiers.new("HINGE_INTERSECT", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "EXACT"
    modifier.object = b
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = a.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    volume = abs(bm.calc_volume(signed=False)) * 1e9 if bm.faces else 0.0
    bm.free()
    bpy.data.meshes.remove(mesh)
    bpy.data.objects.remove(a, do_unlink=True)
    bpy.data.objects.remove(b, do_unlink=True)
    return round(volume, 6)


source_path = os.path.relpath(bpy.data.filepath, REPO_ROOT).replace(os.sep, "/")
result = {"source": source_path, "states": []}
failed = False
for angle in ANGLES:
    if hinge.animation_data:
        hinge.animation_data.action = None
    hinge.rotation_euler.x = math.radians(90.0 - angle)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    volumes = {
        key: intersection_volume_mm3(a, b, f"{angle}_{key}")
        for key, a, b in PAIRS
    }
    state_pass = all(value <= MAX_INTERSECTION_MM3 for value in volumes.values())
    failed = failed or not state_pass
    result["states"].append(
        {
            "angle_deg": angle,
            "pass": state_pass,
            "intersection_mm3": volumes,
        }
    )

result["passed"] = not failed
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2)
print("MACBOOK_HINGE_CLEARANCE", json.dumps(result, sort_keys=True))
if failed:
    raise RuntimeError("MacBook hinge solid collision detected")
