import json
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

SPECS = {
    "11": dict(w=177.5, h=249.7, d=5.3, sw=160.13, sh=232.32, body_r=9.0, screen_r=6.8),
    "13": dict(w=215.5, h=281.6, d=5.1, sw=199.14, sh=265.19, body_r=9.5, screen_r=7.3),
}


def arg(flag, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default
SIZE = arg("--size", "13")
if SIZE not in SPECS:
    raise ValueError(f"Unsupported iPad Pro size: {SIZE}")
spec = SPECS[SIZE]
W, H, D = spec["w"] * MM, spec["h"] * MM, spec["d"] * MM
SW, SH = spec["sw"] * MM, spec["sh"] * MM
BODY_R, SCREEN_R = spec["body_r"] * MM, spec["screen_r"] * MM
OUT = os.path.abspath(arg("--out", os.path.join(HERE, "generated", f"ipad_pro_{SIZE}_m5_foundation.blend")))
EVIDENCE = os.path.abspath(arg("--evidence", os.path.join(HERE, "evidence", f"ipad_pro_{SIZE}_m5_validation.json")))
PREVIEWS = os.path.abspath(arg("--previews", os.path.join(HERE, "previews", SIZE)))
BLUEPRINT = os.path.abspath(arg("--blueprint", os.path.join(HERE, "blueprints", f"ipad_pro_{SIZE}_m5_blockout.svg")))

fc.clear_scene()
fc.setup_scene()
body_c = fc.make_collection(f"IPAD_PRO_{SIZE}_BODY")
detail_c = fc.make_collection(f"IPAD_PRO_{SIZE}_DETAILS")
screen_c = fc.make_collection(f"IPAD_PRO_{SIZE}_SCREEN")
rig_c = fc.make_collection(f"IPAD_PRO_{SIZE}_CONTROLLERS")

metal = fc.make_material("MAT_SPACE_BLACK_ALUMINUM", (0.15, 0.16, 0.18), 0.82, 0.25)
black = fc.make_material("MAT_CAMERA_BLACK", (0.007, 0.008, 0.012), 0.10, 0.08)
glass = fc.make_glass_material("MAT_DISPLAY_GLASS", (0.016, 0.020, 0.028), 0.07, 0.90, 1.46)
screen_mat = fc.make_screen_material("MAT_SCREEN_CONTENT", (0.004, 0.006, 0.010), 0.05)
flash_mat = fc.make_material("MAT_FLASH", (0.90, 0.85, 0.72), 0.0, 0.18)
body = fc.rounded_prism("BODY_ALUMINUM", W, H, D, BODY_R, metal, body_c, axis="Y", edge_bevel=0.00038)
screen_content = fc.rounded_prism("SCREEN_CONTENT", SW, SH, 0.20 * MM, SCREEN_R, screen_mat, screen_c, axis="Y", location=(0, -D * 0.5 - 0.16 * MM, 0))
screen_glass = fc.rounded_prism("SCREEN_GLASS", SW + 0.45 * MM, SH + 0.45 * MM, 0.38 * MM, SCREEN_R + 0.18 * MM, glass, screen_c, axis="Y", location=(0, -D * 0.5 - 0.31 * MM, 0), edge_bevel=0.00009)

housing_size = 36.0 * MM
hx = -W * 0.5 + housing_size * 0.5 + 6.0 * MM
hz = H * 0.5 - housing_size * 0.5 - 10.0 * MM
fc.rounded_prism("CAMERA_HOUSING", housing_size, housing_size, 2.05 * MM, 7.0 * MM, metal, detail_c, axis="Y", location=(hx, D * 0.5 + 1.02 * MM, hz), edge_bevel=0.00018)
fc.cylinder("REAR_CAMERA_RING", 5.415 * MM, 1.75 * MM, metal, detail_c, (hx - 7 * MM, D * 0.5 + 2.02 * MM, hz + 7 * MM), axis="Y", vertices=96)
fc.cylinder("REAR_CAMERA_GLASS", 4.20 * MM, 0.42 * MM, glass, detail_c, (hx - 7 * MM, D * 0.5 + 2.95 * MM, hz + 7 * MM), axis="Y", vertices=96)
fc.cylinder("FLASH", 3.35 * MM, 0.52 * MM, flash_mat, detail_c, (hx + 7 * MM, D * 0.5 + 2.25 * MM, hz + 7 * MM), axis="Y", vertices=64)
fc.cylinder("LIDAR", 4.20 * MM, 0.55 * MM, black, detail_c, (hx - 7 * MM, D * 0.5 + 2.24 * MM, hz - 7 * MM), axis="Y", vertices=64)
fc.cylinder("REAR_MIC", 1.80 * MM, 0.45 * MM, black, detail_c, (hx + 7 * MM, D * 0.5 + 2.22 * MM, hz - 7 * MM), axis="Y", vertices=48)
fc.rounded_cube("USB_C_PORT", (13.0 * MM, 3.2 * MM, 0.62 * MM), 0.52 * MM, black, detail_c, (0, 0, -H * 0.5 - 0.22 * MM))
for i, x_mm in enumerate((-52, -48, -44, 44, 48, 52), 1):
    if abs(x_mm) * MM < W * 0.5 - 4 * MM:
        fc.cylinder(f"BOTTOM_SPEAKER_{i:02}", 0.72 * MM, 0.50 * MM, black, detail_c, (x_mm * MM, 0, -H * 0.5 - 0.16 * MM), axis="Z", vertices=32)
for i, x_mm in enumerate((-52, -48, -44, 44, 48, 52), 1):
    if abs(x_mm) * MM < W * 0.5 - 4 * MM:
        fc.cylinder(f"TOP_SPEAKER_{i:02}", 0.72 * MM, 0.50 * MM, black, detail_c, (x_mm * MM, 0, H * 0.5 + 0.16 * MM), axis="Z", vertices=32)

fc.rounded_cube("TOP_BUTTON", (18.0 * MM, 0.80 * MM, 0.95 * MM), 0.28 * MM, metal, detail_c, (-W * 0.5 + 23 * MM, 0, H * 0.5 + 0.18 * MM))
fc.rounded_cube("VOL_UP", (0.85 * MM, 0.72 * MM, 12.0 * MM), 0.28 * MM, metal, detail_c, (W * 0.5 + 0.17 * MM, 0, H * 0.5 - 28 * MM))
fc.rounded_cube("VOL_DOWN", (0.85 * MM, 0.72 * MM, 12.0 * MM), 0.28 * MM, metal, detail_c, (W * 0.5 + 0.17 * MM, 0, H * 0.5 - 44 * MM))
for idx, x_mm in enumerate((-5.27, 0.0, 5.27), 1):
    fc.cylinder(f"SMART_CONNECTOR_{idx}", 1.70 * MM, 0.36 * MM, metal, detail_c, (x_mm * MM, D * 0.5 + 0.24 * MM, -H * 0.5 + 12 * MM), axis="Y", vertices=32)
root = fc.empty(f"CTRL_IPAD_PRO_{SIZE}", rig_c)
for collection in (body_c, detail_c, screen_c):
    for obj in collection.objects:
        obj.parent = root
root["asset_id"] = f"ipad_pro_{SIZE}_m5"
root["asset_version"] = "foundation_0.1"
root["stage"] = "BLOCKOUT"
root["size_variant"] = SIZE
root["dimensions_mm"] = f"{spec['w']} x {spec['h']} x {spec['d']}"
root["screen_object"] = "SCREEN_CONTENT"

fc.add_preview_rig(scale=max(W, H) * 1.30)
camera_c = fc.make_collection("_DIAGNOSTIC_CAMERAS")
cam_front = fc.add_camera("CAM_FRONT", (0, -0.72, 0), (0, 0, 0), H * 1.12, camera_c)
cam_back = fc.add_camera("CAM_BACK", (0, 0.72, 0), (0, 0, 0), H * 1.12, camera_c)
cam_three = fc.add_camera("CAM_THREE_QUARTER", (W * 1.1, -H * 0.95, H * 0.50), (0, 0, 0), H * 1.18, camera_c)

bpy.context.view_layer.update()
actual_mm = {"width": body.dimensions.x / MM, "height": body.dimensions.z / MM, "depth": body.dimensions.y / MM}
expected_mm = {"width": spec["w"], "height": spec["h"], "depth": spec["d"]}
delta_mm = {key: actual_mm[key] - expected_mm[key] for key in expected_mm}
bm = bmesh.new()
bm.from_mesh(body.data)
non_manifold_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
bm.free()
passed = non_manifold_edges == 0 and all(abs(value) <= 0.001 for value in delta_mm.values())

evidence = {
    "asset_id": f"ipad_pro_{SIZE}_m5",
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
fc.write_blueprint_svg(BLUEPRINT, f"iPad Pro {SIZE}-inch M5", spec["w"], spec["h"], spec["d"], spec["body_r"])
fc.save_blend(OUT)
fc.render_camera(cam_front, os.path.join(PREVIEWS, f"ipad_pro_{SIZE}_front.png"))
fc.render_camera(cam_back, os.path.join(PREVIEWS, f"ipad_pro_{SIZE}_back.png"))
fc.render_camera(cam_three, os.path.join(PREVIEWS, f"ipad_pro_{SIZE}_three_quarter.png"))
print("AWFUL_FOUNDATION_VALIDATION", json.dumps(evidence, sort_keys=True))
if not passed:
    raise RuntimeError(f"iPad Pro {SIZE} foundation validation failed")
