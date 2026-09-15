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

W, D, CLOSED_H = 312.6 * MM, 221.2 * MM, 15.5 * MM
LID_T = 4.7 * MM
CLOSED_GAP = 0.5 * MM
BASE_H = CLOSED_H - LID_T - CLOSED_GAP
LID_W, LID_H = 312.0 * MM, 212.0 * MM
SCREEN_W, SCREEN_H = 301.66 * MM, 195.92 * MM
OPEN_ANGLE_DEG = 102.0
LID_TILT_DEG = -(OPEN_ANGLE_DEG - 90.0)


def arg(flag, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default

OUT = arg("--out", os.path.join(HERE, "generated", "macbook_pro_14_m5_foundation.blend"))
EVIDENCE = os.path.join(HERE, "evidence", "foundation_validation.json")
PREVIEW = os.path.join(HERE, "previews")
BLUEPRINT = os.path.join(HERE, "blueprints", "macbook_pro_14_blockout.svg")

fc.clear_scene()
fc.setup_scene()
base_c = fc.make_collection("MACBOOK_PRO_14_BASE")
lid_c = fc.make_collection("MACBOOK_PRO_14_LID")
detail_c = fc.make_collection("MACBOOK_PRO_14_DETAILS")
screen_c = fc.make_collection("MACBOOK_PRO_14_SCREEN")
ctrl_c = fc.make_collection("MACBOOK_PRO_14_CONTROLS")

metal = fc.make_material("MAT_SPACE_BLACK_ALUMINUM", (0.13, 0.14, 0.15), 0.82, 0.24)
keymat = fc.make_material("MAT_KEYCAP", (0.015, 0.017, 0.020), 0.0, 0.30)
dark = fc.make_material("MAT_PORT_DARK", (0.008, 0.009, 0.011), 0.05, 0.22)
trackmat = fc.make_material("MAT_TRACKPAD", (0.10, 0.11, 0.12), 0.65, 0.28)
glass = fc.make_glass_material("MAT_DISPLAY_GLASS", (0.012, 0.016, 0.022), 0.06, 0.92, 1.46)
screenmat = fc.make_screen_material("MAT_SCREEN_CONTENT", (0.003, 0.005, 0.008), 0.04)

root = fc.empty("CTRL_MACBOOK_PRO_14", ctrl_c)
root["asset_id"] = "macbook_pro_14_m5"
root["stage"] = "BLOCKOUT"
root["closed_dimensions_mm"] = "312.6 x 221.2 x 15.5"

base = fc.rounded_prism("BASE_UNIBODY", W, D, BASE_H, 8.0 * MM, metal, base_c, axis="Z", location=(0, 0, BASE_H * 0.5), edge_bevel=0.0007)
base.parent = root
trackpad = fc.rounded_prism("TRACKPAD", 132 * MM, 86 * MM, 0.55 * MM, 4.0 * MM, trackmat, detail_c, axis="Z", location=(0, -48 * MM, BASE_H + 0.35 * MM), edge_bevel=0.00012)
trackpad.parent = root

hinge_y = D * 0.5 - 8.0 * MM
hinge = fc.empty("CTRL_HINGE", ctrl_c, location=(0, hinge_y, BASE_H + CLOSED_GAP))
hinge.parent = root
hinge.rotation_euler.x = math.radians(LID_TILT_DEG)
hinge["open_angle_deg"] = OPEN_ANGLE_DEG
hinge["preset"] = "PRESENTATION"

lid = fc.rounded_prism("LID_UNIBODY", LID_W, LID_H, LID_T, 7.5 * MM, metal, lid_c, axis="Y", edge_bevel=0.00055)
lid.parent = hinge
lid.location = (0, LID_T * 0.5, LID_H * 0.5)

screen_content = fc.rounded_prism("SCREEN_CONTENT", SCREEN_W, SCREEN_H, 0.35 * MM, 5.7 * MM, screenmat, screen_c, axis="Y", edge_bevel=0.00008)
screen_content.parent = hinge
screen_content.location = (0, -0.14 * MM, LID_H * 0.5 + 2.5 * MM)
screen_glass = fc.rounded_prism("SCREEN_GLASS", SCREEN_W + 0.5 * MM, SCREEN_H + 0.5 * MM, 0.40 * MM, 5.9 * MM, glass, screen_c, axis="Y", edge_bevel=0.00008)
screen_glass.parent = hinge
screen_glass.location = (0, -0.34 * MM, LID_H * 0.5 + 2.5 * MM)

notch = fc.rounded_prism("CAMERA_NOTCH", 36 * MM, 10 * MM, 0.45 * MM, 4.2 * MM, keymat, detail_c, axis="Y", edge_bevel=0.00008)
notch.parent = hinge
notch.location = (0, -0.42 * MM, LID_H - 5.6 * MM)
camera = fc.cylinder("FACETIME_CAMERA", 1.45 * MM, 0.42 * MM, dark, detail_c, axis="Y", vertices=48)
camera.parent = hinge
camera.location = (0, -0.70 * MM, LID_H - 5.6 * MM)

key_w, key_h, key_z = 16.2 * MM, 13.5 * MM, 1.0 * MM
col_gap, row_gap = 2.4 * MM, 2.6 * MM
cols, rows = 14, 6
total_w = cols * key_w + (cols - 1) * col_gap
x0 = -total_w * 0.5 + key_w * 0.5
y0 = -1.0 * MM + key_h * 0.5
for row in range(rows):
    y = y0 + row * (key_h + row_gap)
    for col in range(cols):
        if row == 0 and 4 <= col <= 9:
            continue
        key = fc.rounded_cube(f"KEY_{row:02d}_{col:02d}", (key_w, key_h, key_z), 1.8 * MM, keymat, detail_c, (x0 + col * (key_w + col_gap), y, BASE_H + key_z * 0.5 + 0.35 * MM))
        key.parent = root
space = fc.rounded_cube("KEY_SPACE", (105 * MM, key_h, key_z), 1.8 * MM, keymat, detail_c, (0, y0, BASE_H + key_z * 0.5 + 0.35 * MM))
space.parent = root

touch = fc.rounded_cube("TOUCH_ID", (16.2 * MM, 13.5 * MM, 1.0 * MM), 2.2 * MM, keymat, detail_c, (x0 + 13 * (key_w + col_gap), y0 + 5 * (key_h + row_gap), BASE_H + 0.85 * MM))
touch.parent = root

for side in (-1, 1):
    sx = side * (W * 0.5 - 19.0 * MM)
    for row in range(13):
        sy = 8.0 * MM + row * 5.8 * MM
        for col in range(3):
            hole = fc.cylinder(f"SPEAKER_{'L' if side < 0 else 'R'}_{row:02d}_{col:02d}", 0.75 * MM, 0.30 * MM, dark, detail_c, (sx + (col - 1) * 3.2 * MM, sy, BASE_H + 0.27 * MM), axis="Z", vertices=20)
            hole.parent = root

port_specs = [
    ("MAGSAFE", -1, 66, 12, 3.2), ("TB_LEFT_1", -1, 25, 12, 2.4), ("TB_LEFT_2", -1, -2, 12, 2.4),
    ("HEADPHONE", -1, -55, 7, 3.4), ("HDMI", 1, 54, 16, 4.2), ("SDXC", 1, 19, 18, 2.2),
    ("TB_RIGHT", 1, -22, 12, 2.4),
]
for name, side, y_mm, length_mm, height_mm in port_specs:
    x = side * (W * 0.5 + 0.18 * MM)
    port = fc.rounded_cube(name, (0.55 * MM, length_mm * MM, height_mm * MM), min(1.0 * MM, height_mm * MM * 0.35), dark, detail_c, (x, y_mm * MM, BASE_H * 0.53))
    port.parent = root

for x in (-W * 0.5 + 18 * MM, W * 0.5 - 18 * MM):
    for y in (-D * 0.5 + 16 * MM, D * 0.5 - 18 * MM):
        foot = fc.cylinder("FOOT", 5.0 * MM, 0.8 * MM, keymat, detail_c, (x, y, -0.30 * MM), axis="Z", vertices=48)
        foot.parent = root

fc.add_preview_rig(scale=0.48)
cam_open = fc.add_camera("CAM_OPEN", (0.40, -0.52, 0.34), (0, 0.015, 0.105), 0.39, ctrl_c)
cam_top = fc.add_camera("CAM_TOP", (0, -0.03, 0.72), (0, -0.005, 0.02), 0.37, ctrl_c)
cam_side = fc.add_camera("CAM_SIDE", (0.48, -0.08, 0.20), (0, 0.02, 0.08), 0.38, ctrl_c)

fc.render_camera(cam_open, os.path.join(PREVIEW, "macbook_pro_14_open_three_quarter.png"))
fc.render_camera(cam_side, os.path.join(PREVIEW, "macbook_pro_14_open_side.png"))

hinge.rotation_euler.x = math.radians(90.0)
bpy.context.view_layer.update()
fc.render_camera(cam_top, os.path.join(PREVIEW, "macbook_pro_14_closed_top.png"))
hinge.rotation_euler.x = math.radians(LID_TILT_DEG)
bpy.context.view_layer.update()

fc.write_blueprint_svg(BLUEPRINT, "MacBook Pro 14 M5 Pro/Max", W / MM, D / MM, CLOSED_H / MM, 8.0)

def local_dims_mm(obj):
    coords = [v.co for v in obj.data.vertices]
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    return tuple((maxs[i] - mins[i]) / MM for i in range(3))


def non_manifold_count(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    count = sum(1 for edge in bm.edges if not edge.is_manifold)
    bm.free()
    return count

base_dims = local_dims_mm(base)
lid_dims = local_dims_mm(lid)
closed_stack_mm = (BASE_H + CLOSED_GAP + LID_T) / MM
base_nm = non_manifold_count(base)
lid_nm = non_manifold_count(lid)
hinge_children = sorted(child.name for child in hinge.children)

validation = {
    "asset_id": "macbook_pro_14_m5",
    "stage": "BLOCKOUT",
    "blender_version": bpy.app.version_string,
    "expected_mm": {"width": 312.6, "depth": 221.2, "closed_height": 15.5},
    "actual_mm": {"width": round(base_dims[0], 6), "depth": round(base_dims[1], 6), "closed_height": round(closed_stack_mm, 6)},
    "lid_local_mm": {"width": round(lid_dims[0], 6), "thickness": round(lid_dims[1], 6), "height": round(lid_dims[2], 6)},
    "base_non_manifold_edges": base_nm,
    "lid_non_manifold_edges": lid_nm,
    "hinge_open_angle_deg": OPEN_ANGLE_DEG,
    "hinge_children": hinge_children,
    "object_count": len(bpy.data.objects),
    "material_count": len(bpy.data.materials),
}
validation["delta_mm"] = {
    "width": round(validation["actual_mm"]["width"] - 312.6, 6),
    "depth": round(validation["actual_mm"]["depth"] - 221.2, 6),
    "closed_height": round(validation["actual_mm"]["closed_height"] - 15.5, 6),
}
validation["passed"] = (
    max(abs(v) for v in validation["delta_mm"].values()) <= 0.01
    and base_nm == 0
    and lid_nm == 0
    and set(["LID_UNIBODY", "SCREEN_CONTENT", "SCREEN_GLASS", "CAMERA_NOTCH", "FACETIME_CAMERA"]).issubset(set(hinge_children))
)
os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
with open(EVIDENCE, "w", encoding="utf-8") as handle:
    json.dump(validation, handle, indent=2, sort_keys=True)

fc.save_blend(OUT)
print("AWFUL_FOUNDATION_VALIDATION", json.dumps(validation, sort_keys=True))
if not validation["passed"]:
    raise SystemExit(2)
