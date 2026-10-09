"""The opaque iPhone screen must leave both front-optic apertures unobstructed."""
import bpy
import json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
SCREEN = bpy.data.objects["SCREEN_CONTENT"]
TARGETS = {
    "front_sensor": (-0.00415, 0.14961 / 2 - 0.00779, "FRONT_SENSOR_MASK"),
    "front_camera": (0.00672, 0.14961 / 2 - 0.00779, "FRONT_CAMERA_GLASS"),
}

def hit(name, x, z):
    obj = bpy.data.objects[name]
    origin = obj.matrix_world.inverted() @ Vector((x, -0.03, z))
    direction = obj.matrix_world.inverted().to_3x3() @ Vector((0, 1, 0))
    tree = BVHTree.FromObject(obj, depsgraph)
    result = tree.ray_cast(origin, direction.normalized(), 0.08)
    return result[0] is not None

assert hit("SCREEN_CONTENT", 0, 0), "center screen unexpectedly absent"
report = {}
for name, (x, z, optical_node) in TARGETS.items():
    screen_hit = hit("SCREEN_CONTENT", x, z)
    optic_hit = hit(optical_node, x, z)
    report[name] = {"opaque_screen_hit": screen_hit, "optics_hit": optic_hit, "x_mm": x*1000, "z_mm": z*1000}
    assert optic_hit, f"{name}: physical optic not at expected datum: {report[name]}"
    assert not screen_hit, f"{name}: screen occludes the optic: {report[name]}"
print("IPHONE_FRONT_OPTICS_VISIBILITY_GREEN", json.dumps(report,sort_keys=True))
