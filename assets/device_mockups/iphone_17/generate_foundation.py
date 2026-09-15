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

MM = fc.MM
W, H, D = 71.5 * MM, 149.6 * MM, 7.95 * MM
SCREEN_W, SCREEN_H = 66.55 * MM, 144.69 * MM
BODY_R, SCREEN_R = 13.6 * MM, 10.8 * MM


def cli_value(flag, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default
OUT = os.path.abspath(cli_value("--out", os.path.join(HERE, "generated", "iphone_17_foundation.blend")))
EVIDENCE = os.path.abspath(cli_value("--evidence", os.path.join(HERE, "evidence", "foundation_validation.json")))
PREVIEWS = os.path.abspath(cli_value("--previews", os.path.join(HERE, "previews")))
BLUEPRINT = os.path.abspath(cli_value("--blueprint", os.path.join(HERE, "blueprints", "iphone_17_blockout.svg")))

fc.clear_scene()
fc.setup_scene()
body_c = fc.make_collection("IPHONE_17_BODY")
detail_c = fc.make_collection("IPHONE_17_DETAILS")
screen_c = fc.make_collection("IPHONE_17_SCREEN")
rig_c = fc.make_collection("IPHONE_17_CONTROLLERS")

metal = fc.make_material("MAT_ANODIZED_ALUMINUM", (0.56, 0.57, 0.59), 0.78, 0.24)
back = fc.make_material("MAT_BACK_GLASS", (0.57, 0.56, 0.61), 0.0, 0.29)
glass = fc.make_glass_material("MAT_DISPLAY_GLASS", (0.018, 0.022, 0.030), 0.07, 0.90, 1.46)
screen_mat = fc.make_screen_material("MAT_SCREEN_CONTENT", (0.004, 0.006, 0.010), 0.05)
black = fc.make_material("MAT_CAMERA_BLACK", (0.008, 0.009, 0.012), 0.10, 0.07)
flash_mat = fc.make_material("MAT_FLASH", (0.91, 0.86, 0.72), 0.0, 0.18)
body = fc.rounded_prism("BODY_ALUMINUM", W, H, D, BODY_R, metal, body_c, axis="Y", edge_bevel=0.00045)
back_glass = fc.rounded_prism("BACK_GLASS", W - 1.6 * MM, H - 1.6 * MM, 0.55 * MM, 12.6 * MM, back, body_c, axis="Y", location=(0, D * 0.5 + 0.22 * MM, 0), edge_bevel=0.00015)
screen_content = fc.rounded_prism("SCREEN_CONTENT", SCREEN_W, SCREEN_H, 0.22 * MM, SCREEN_R, screen_mat, screen_c, axis="Y", location=(0, -D * 0.5 - 0.18 * MM, 0))
screen_glass = fc.rounded_prism("SCREEN_GLASS", SCREEN_W + 0.35 * MM, SCREEN_H + 0.35 * MM, 0.42 * MM, SCREEN_R + 0.15 * MM, glass, screen_c, axis="Y", location=(0, -D * 0.5 - 0.34 * MM, 0), edge_bevel=0.00010)

for idx, (x_mm, z_mm) in enumerate(((-22.1, 60.9), (-22.1, 43.2)), 1):
    fc.cylinder(f"CAMERA_{idx}_RING", 8.0 * MM, 2.15 * MM, metal, detail_c, (x_mm * MM, D * 0.5 + 1.00 * MM, z_mm * MM), axis="Y", vertices=96)
    fc.cylinder(f"CAMERA_{idx}_GLASS", 5.76 * MM, 0.55 * MM, glass, detail_c, (x_mm * MM, D * 0.5 + 2.20 * MM, z_mm * MM), axis="Y", vertices=96)
    fc.cylinder(f"CAMERA_{idx}_INNER", 3.75 * MM, 0.20 * MM, black, detail_c, (x_mm * MM, D * 0.5 + 2.58 * MM, z_mm * MM), axis="Y", vertices=96)

fc.cylinder("FLASH", 3.14 * MM, 0.70 * MM, flash_mat, detail_c, (-13.0 * MM, D * 0.5 + 1.35 * MM, 52.0 * MM), axis="Y", vertices=64)
fc.rounded_prism("DYNAMIC_ISLAND", 21.0 * MM, 6.3 * MM, 0.25 * MM, 3.15 * MM, black, detail_c, axis="Y", location=(0, -D * 0.5 - 0.58 * MM, H * 0.5 - 14.0 * MM))
for name, z_mm, length_mm in (("ACTION_BUTTON", 40.72, 12.0), ("VOL_UP", 26.57, 9.0), ("VOL_DOWN", 12.37, 9.0)):
    fc.rounded_cube(name, (0.90 * MM, 0.72 * MM, length_mm * MM), 0.30 * MM, metal, detail_c, (-W * 0.5 - 0.18 * MM, 0, z_mm * MM))
fc.rounded_cube("SIDE_BUTTON", (0.90 * MM, 0.72 * MM, 18.0 * MM), 0.30 * MM, metal, detail_c, (W * 0.5 + 0.18 * MM, 0, 30.8 * MM))
fc.rounded_cube("CAMERA_CONTROL", (0.82 * MM, 0.62 * MM, 20.0 * MM), 0.24 * MM, black, detail_c, (W * 0.5 + 0.20 * MM, 0, -31.0 * MM))

fc.rounded_cube("USB_C_PORT", (10.2 * MM, 3.4 * MM, 0.65 * MM), 0.55 * MM, black, detail_c, (0, 0, -H * 0.5 - 0.24 * MM))
for i, x_mm in enumerate((-25.0, -22.0, -19.0, 19.0, 22.0, 25.0), 1):
    fc.cylinder(f"BOTTOM_APERTURE_{i:02}", 0.62 * MM, 0.55 * MM, black, detail_c, (x_mm * MM, 0, -H * 0.5 - 0.18 * MM), axis="Z", vertices=32)

root = fc.empty("CTRL_IPHONE_17", rig_c)
for collection in (body_c, detail_c, screen_c):
    for obj in collection.objects:
        obj.parent = root
root["asset_id"] = "iphone_17"
root["asset_version"] = "foundation_0.1"
root["stage"] = "BLOCKOUT"
root["dimensions_mm"] = "71.5 x 149.6 x 7.95"
root["screen_object"] = "SCREEN_CONTENT"
preview_rig = fc.add_preview_rig(scale=0.24)
camera_c = fc.make_collection("_DIAGNOSTIC_CAMERAS")
cam_front = fc.add_camera("CAM_FRONT", (0, -0.42, 0), (0, 0, 0), 0.172, camera_c)
cam_back = fc.add_camera("CAM_BACK", (0, 0.42, 0), (0, 0, 0), 0.172, camera_c)
cam_three = fc.add_camera("CAM_THREE_QUARTER", (0.19, -0.28, 0.12), (0, 0, 0), 0.185, camera_c)

bpy.context.view_layer.update()
actual_mm = {
    "width": body.dimensions.x / MM,
    "height": body.dimensions.z / MM,
    "depth": body.dimensions.y / MM,
}
bm = bmesh.new()
bm.from_mesh(body.data)
non_manifold_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
bm.free()

expected_mm = {"width": 71.5, "height": 149.6, "depth": 7.95}
delta_mm = {key: actual_mm[key] - expected_mm[key] for key in expected_mm}
passed = non_manifold_edges == 0 and all(abs(value) <= 0.001 for value in delta_mm.values())
evidence = {
    "asset_id": "iphone_17",
    "stage": "BLOCKOUT",
    "blender_version": bpy.app.version_string,
    "expected_mm": expected_mm,
    "actual_mm": {key: round(value, 6) for key, value in actual_mm.items()},
    "delta_mm": {key: round(value, 6) for key, value in delta_mm.items()},
    "body_non_manifold_edges": non_manifold_edges,
    "object_count": len(bpy.data.objects),
    "material_count": len(bpy.data.materials),
    "passed": passed,
}
os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
with open(EVIDENCE, "w", encoding="utf-8") as handle:
    json.dump(evidence, handle, indent=2)

fc.write_blueprint_svg(BLUEPRINT, "iPhone 17", 71.5, 149.6, 7.95, 13.6)
fc.save_blend(OUT)
fc.render_camera(cam_front, os.path.join(PREVIEWS, "iphone_17_front.png"))
fc.render_camera(cam_back, os.path.join(PREVIEWS, "iphone_17_back.png"))
fc.render_camera(cam_three, os.path.join(PREVIEWS, "iphone_17_three_quarter.png"))
print("AWFUL_FOUNDATION_VALIDATION", json.dumps(evidence, sort_keys=True))
if not passed:
    raise RuntimeError("iPhone 17 foundation validation failed")
