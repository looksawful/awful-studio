"""Build G2 overlays from actual Blender geometry against official Apple references."""
from __future__ import annotations

import argparse
import json
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assets.device_mockups.macbook_pro_14.geometry_contract import (
    CHASSIS_FACTS,
    DECK_CALIBRATION,
    G2_DISPLAY_FACTS,
    require_frozen_fact,
)
from assets.device_mockups.macbook_pro_14.port_layout import PORTS

W = CHASSIS_FACTS["width"].value_mm
D = CHASSIS_FACTS["depth"].value_mm
H = CHASSIS_FACTS["closed_height"].value_mm

# Calibrated body-silhouette rows in the cached Apple spec imagery.
# Front excludes the dimension bracket/shadow tail; side bounds use rows with
# broad chassis occupancy rather than isolated reflections/annotation pixels.
REFERENCE_VERTICAL_BOUNDS = {
    "front": (0.0, 20.0),
    "left": (7.0, 53.0),
    "right": (7.0, 53.0),
}

GREEN = (70, 220, 70)
CYAN = (240, 220, 40)
YELLOW = (0, 210, 255)
MAGENTA = (220, 80, 220)


def _cv2():
    import cv2
    return cv2


def _np():
    import numpy as np
    return np


def label(im, text, y=28, color=GREEN, scale=.58):
    cv2 = _cv2()
    cv2.putText(im, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(im, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)


def save(out, name, im):
    cv2 = _cv2()
    p = out / name
    cv2.imwrite(str(p), im)
    return str(p.relative_to(ROOT)).replace("\\", "/")


def draw_poly(im, pts, mapper, color=GREEN, thickness=2):
    if not pts:
        return
    cv2 = _cv2()
    np = _np()
    pixels = np.array([mapper(x, y) for x, y in pts], np.int32)
    cv2.polylines(im, [pixels], True, color, thickness, cv2.LINE_AA)


def bbox_px(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def fixed_height_z_mapper(model_center_z_mm, reference_top_px, reference_bottom_px, exact_height_mm):
    pixels_per_mm = (reference_bottom_px - reference_top_px) / exact_height_mm
    reference_center_px = (reference_top_px + reference_bottom_px) / 2.0

    def mapper(z_mm):
        return reference_center_px - (z_mm - model_center_z_mm) * pixels_per_mm

    return mapper


def project_side_point(
    map_x,
    *,
    y_mm,
    z_mm,
    model_center_z_mm,
    reference_top_px,
    reference_bottom_px,
    exact_height_mm,
):
    map_z = fixed_height_z_mapper(
        model_center_z_mm,
        reference_top_px,
        reference_bottom_px,
        exact_height_mm,
    )
    return round(map_x(y_mm)), round(map_z(z_mm))


def pair_points_by_metric_cost(actual_points, target_points, sx, sy):
    if len(actual_points) != len(target_points):
        raise ValueError("point sets must have equal cardinality")
    best = None
    for perm in permutations(target_points):
        residuals = [
            ((((actual[0] - target[0]) * sx) ** 2
              + ((actual[1] - target[1]) * sy) ** 2) ** 0.5)
            for actual, target in zip(actual_points, perm)
        ]
        score = (sum(value * value for value in residuals), max(residuals, default=0.0))
        if best is None or score < best[0]:
            best = (score, list(zip(actual_points, perm)), residuals)
    return best[1], best[2]


def top_overlay(refs, out, model):
    cv2 = _cv2()
    im = cv2.imread(str(refs / "top.jpg"))
    x0, y0, x1, y1 = 3, 2, 406, 287

    def mapper(x, y):
        return (
            round(x0 + (x + W / 2) / W * (x1 - x0)),
            round(y0 + (D / 2 - y) / D * (y1 - y0)),
        )

    hull = model["closed"]["top_xy"]
    draw_poly(im, hull, mapper, GREEN, 2)
    logo = model["closed"].get("logo_xy", {}).get("APPLE_LOGO_RELEASE", [])
    draw_poly(im, logo, mapper, CYAN, 2)
    mapped = [mapper(*p) for p in hull]
    b = bbox_px(mapped)
    residual = max(abs(b[0] - x0), abs(b[1] - y0), abs(b[2] - x1), abs(b[3] - y1))
    label(im, f"actual Blender closed top; silhouette bbox residual <= {residual:.1f}px")
    return save(out, "01_top_closed_overlay.png", im), residual


def front_overlay(refs, out, model):
    cv2 = _cv2()
    im = cv2.imread(str(refs / "front.jpg"))
    x0, x1 = 3, 406
    hull = model["closed"]["front_xz"]
    zmin = min(p[1] for p in hull)
    zmax = max(p[1] for p in hull)
    model_center_z = (zmin + zmax) / 2.0
    top_px, bottom_px = REFERENCE_VERTICAL_BOUNDS["front"]
    map_z = fixed_height_z_mapper(model_center_z, top_px, bottom_px, H)

    def mapper(x, z):
        return (
            round(x0 + (x + W / 2) / W * (x1 - x0)),
            round(map_z(z)),
        )

    draw_poly(im, hull, mapper, GREEN, 1)
    mapped = [mapper(*p) for p in hull]
    b = bbox_px(mapped)
    residual = max(
        abs(b[0] - x0),
        abs(b[1] - top_px),
        abs(b[2] - x1),
        abs(b[3] - bottom_px),
    )
    label(im, f"actual Blender closed-front; fixed Apple-height scale; bbox residual {residual:.1f}px", im.shape[0]-4, GREEN, .27)
    return save(out, "02_front_overlay.png", im), residual


def side_x_mapper(side):
    specs = [p for p in PORTS if p.side == side]
    ys = [float(p.y_mm) for p in specs]
    px = [float(p.center_pixel) for p in specs]
    if len(specs) >= 2:
        mean_y = sum(ys) / len(ys)
        mean_px = sum(px) / len(px)
        denom = sum((y - mean_y) ** 2 for y in ys)
        if denom > 0:
            slope = sum((y - mean_y) * (p - mean_px) for y, p in zip(ys, px)) / denom
            intercept = mean_px - slope * mean_y
            return lambda y: float(slope * y + intercept)
    return lambda y: float((y + D / 2) / D * 408)


def side_overlay(refs, out, model, side):
    cv2 = _cv2()
    view = "left" if side < 0 else "right"
    name = f"{view}.jpg"
    im = cv2.imread(str(refs / name))
    key = f"{view}_yz"
    hull = model["closed"][key]
    zmin = min(p[1] for p in hull)
    zmax = max(p[1] for p in hull)
    model_center_z = (zmin + zmax) / 2.0
    map_x = side_x_mapper(side)
    top_px, bottom_px = REFERENCE_VERTICAL_BOUNDS[view]
    map_z = fixed_height_z_mapper(model_center_z, top_px, bottom_px, H)

    def mapper(y, z):
        return (
            round(map_x(y)),
            round(map_z(z)),
        )

    draw_poly(im, hull, mapper, GREEN, 1)
    actual_centers = []
    for spec in PORTS:
        if spec.side != side or spec.name not in model["ports"]:
            continue
        center = model["ports"][spec.name]["center_xyz_mm"]
        q = project_side_point(
            map_x,
            y_mm=center[1],
            z_mm=center[2],
            model_center_z_mm=model_center_z,
            reference_top_px=top_px,
            reference_bottom_px=bottom_px,
            exact_height_mm=H,
        )
        actual_centers.append((spec.name, q[0], spec.center_pixel))
        cv2.drawMarker(im, q, CYAN, cv2.MARKER_CROSS, 9, 1)

    reprojection_res = max((abs(actual - target) for _, actual, target in actual_centers), default=0.0)
    mapped = [mapper(*p) for p in hull]
    b = bbox_px(mapped)
    z_residual = max(abs(b[1] - top_px), abs(b[3] - bottom_px))

    label(
        im,
        f"actual Blender {view}; fixed Apple-height scale; port reprojection {reprojection_res:.1f}px; Z bbox {z_residual:.1f}px",
        im.shape[0]-7, GREEN, .28,
    )
    return (
        save(out, "03_left_ports_overlay.png" if side < 0 else "04_right_ports_overlay.png", im),
        reprojection_res,
        z_residual,
    )


def bottom_overlay(refs, out, model):
    cv2 = _cv2()
    im = cv2.imread(str(refs / "bottom.png"), cv2.IMREAD_COLOR)
    xL, xR, yR, yF = 44.0, 842.0, 20.0, 582.0
    sx = W / (xR - xL)
    sy = D / (yF - yR)
    cx = (xL + xR) / 2
    cy = (yR + yF) / 2

    def mapper(x, y):
        return (round(cx + x / sx), round(cy - y / sy))

    draw_poly(im, model["closed"]["bottom_xy"], mapper, GREEN, 2)

    target_feet = [(94, 79), (788, 77), (95, 523), (785, 524)]
    actual_feet = []
    for name, data in sorted(model["bottom_features"].items()):
        if not name.startswith("FOOT_"):
            continue
        x, y, _ = data["center_xyz_mm"]
        q = mapper(x, y)
        actual_feet.append(q)
        cv2.drawMarker(im, q, GREEN, cv2.MARKER_CROSS, 12, 2)
        draw_poly(im, data["hull_xy"], mapper, GREEN, 1)

    # Detection rows are not stable enough for lexicographic pairing: the two
    # rear Apple centers differ by two source pixels while the generated pair shares
    # one rounded Y. Solve the four-point one-to-one assignment in metric space.
    pairs, raw_residuals = pair_points_by_metric_cost(actual_feet, target_feet, sx, sy)
    residuals = [round(value, 3) for value in raw_residuals]
    for actual, target in pairs:
        cv2.circle(im, target, 5, CYAN, 2)

    for name, data in sorted(model["bottom_features"].items()):
        if name.startswith("BOTTOM_SCREW_"):
            x, y, _ = data["center_xyz_mm"]
            cv2.drawMarker(im, mapper(x, y), GREEN, cv2.MARKER_CROSS, 9, 1)

    label(im, "bottom: green=actual Blender; cyan=Apple repair detected foot centers", 30, GREEN, .50)
    label(im, "foot residual mm: " + ", ".join(map(str, residuals)), 54, GREEN, .44)
    return save(out, "05_bottom_overlay.png", im), residuals


def deck_overlay(refs, out, model):
    cv2 = _cv2()
    src = cv2.imread(str(refs / "deck2x.jpg"))
    e = DECK_CALIBRATION["source_edges_px"]
    x0, x1, y0, y1 = map(round, (e["left"], e["right"], e["rear"], e["front"]))
    im = src[y0:y1+1, x0:x1+1].copy()
    sx, sy = DECK_CALIBRATION["mm_per_px"]
    cx = (e["left"] + e["right"]) / 2
    cy = (e["rear"] + e["front"]) / 2

    def mapper(x, y):
        source_x = cx + x / sx
        source_y = cy - y / sy
        return (round(source_x - e["left"]), round(source_y - e["rear"]))

    for name, hull in model["deck"].items():
        color = CYAN if name == "TRACKPAD" else GREEN
        if name.startswith("SPEAKER_MASTER_PROXY"):
            color = YELLOW
        draw_poly(im, hull, mapper, color, 1)

    label(im, "deck: actual Blender key/well/trackpad/speaker geometry projected into Apple raster", 26, GREEN, .48)
    return save(out, "06_deck_overlay.png", im)


def hinge_overlay(refs, out, model):
    cv2 = _cv2()
    im = cv2.imread(str(refs / "repair" / "hingeLocator.png"), cv2.IMREAD_COLOR)
    left, right = 51.0, 832.0
    center = (left + right) / 2
    pxmm = (right - left) / W

    for name in ("HINGE_COVER_L", "HINGE_COVER_R"):
        data = model["hinge"].get(name)
        if not data:
            continue
        xs = [p[0] for p in data["top_xy"]]
        x0 = center + min(xs) * pxmm
        x1 = center + max(xs) * pxmm
        cv2.rectangle(im, (round(x0), 29), (round(x1), 63), GREEN, 2)
        if data.get("geometry_authority") == "UNVERIFIED_VISUAL":
            cv2.putText(im, "U", (round((x0+x1)/2)-4, 25), cv2.FONT_HERSHEY_SIMPLEX, .5, YELLOW, 1, cv2.LINE_AA)

    label(im, "hinge: X span from actual Blender covers; depth/thickness explicitly UNVERIFIED", 28, GREEN, .48)
    return save(out, "07_hinge_cover_overlay.png", im)


def display_overlay(product_bezel, out, model):
    cv2 = _cv2()
    im = cv2.imread(str(product_bezel), cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(product_bezel)

    opening_x, opening_y = 418.0, 288.0
    opening_w, opening_h = 3024.0, 1964.0
    scale = 10.0
    screen = model["display"]["SCREEN_CONTENT"]
    screen_center = screen["center_xyz_mm"]

    def mapper(x, z):
        return (
            round(opening_x + opening_w / 2 + (x - screen_center[0]) * scale),
            round(opening_y + opening_h / 2 - (z - screen_center[2]) * scale),
        )

    for name, data in model["display"].items():
        color = GREEN
        if name == "DISPLAY_SURROUND_VISUAL":
            color = YELLOW
        elif name == "FACETIME_CAMERA":
            color = CYAN
        draw_poly(im, data["hull_xz"], mapper, color, 2)

    notch_pixels = [mapper(*p) for p in model["display"]["CAMERA_NOTCH"]["hull_xz"]]
    nb = bbox_px(notch_pixels)
    expected_notch = [
        opening_x + 1319.0,
        opening_y,
        opening_x + 1705.0,
        opening_y + 64.0,
    ]
    notch_residual = max(abs(a-b) for a, b in zip(nb, expected_notch))

    camera_center = model["display"]["FACETIME_CAMERA"]["center_xyz_mm"]
    camera_px = mapper(camera_center[0], camera_center[2])
    expected_camera = (1929.0, 304.5)
    camera_residual = ((camera_px[0]-expected_camera[0])**2 + (camera_px[1]-expected_camera[1])**2) ** .5

    label(im, f"display: actual Blender -> official Apple Product Bezel; notch max residual {notch_residual:.1f}px", im.shape[0]-58, GREEN, .58)
    label(im, f"camera center residual {camera_residual:.1f}px; yellow outer surround is RELATIONAL_VISUAL", im.shape[0]-28, YELLOW, .52)
    return save(out, "08_display_overlay.png", im), notch_residual, camera_residual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs-root", type=Path, required=True)
    ap.add_argument("--projection-json", type=Path, required=True)
    ap.add_argument("--product-bezel", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "assets/device_mockups/macbook_pro_14/evidence/g2_surface_overlays")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    model = json.loads(a.projection_json.read_text(encoding="utf-8"))
    if model.get("source") != "actual evaluated Blender geometry":
        raise ValueError("projection JSON is not actual Blender geometry evidence")

    files = {}
    files["top"], top_residual = top_overlay(a.refs_root, a.out_dir, model)
    files["front"], front_residual = front_overlay(a.refs_root, a.out_dir, model)
    files["left"], left_port_res, left_z_res = side_overlay(a.refs_root, a.out_dir, model, -1)
    files["right"], right_port_res, right_z_res = side_overlay(a.refs_root, a.out_dir, model, 1)
    files["bottom"], foot_residuals = bottom_overlay(a.refs_root, a.out_dir, model)
    files["deck"] = deck_overlay(a.refs_root, a.out_dir, model)
    files["hinge"] = hinge_overlay(a.refs_root, a.out_dir, model)
    files["display"], notch_residual_px, camera_residual_px = display_overlay(a.product_bezel, a.out_dir, model)

    report = {
        "gate": "G2_MODEL_TO_APPLE_OVERLAY",
        "status": "HUMAN_REVIEW_REQUIRED",
        "projection_source": str(a.projection_json),
        "blender_version": model.get("blender_version"),
        "files": files,
        "residuals": {
            "closed_top_bbox_px_max": round(top_residual, 3),
            "front_silhouette_bbox_px_max": round(front_residual, 3),
            "left_port_reprojection_px_max": round(left_port_res, 3),
            "right_port_reprojection_px_max": round(right_port_res, 3),
            "left_silhouette_z_px_max": round(left_z_res, 3),
            "right_silhouette_z_px_max": round(right_z_res, 3),
            "foot_center_mm": foot_residuals,
            "display_notch_bbox_px_max": round(notch_residual_px, 3),
            "display_camera_center_px": round(camera_residual_px, 3),
        },
        "notes": {
            "geometry": "green/cyan contours come from evaluated Blender geometry exported by Blender 5.2.1",
            "display_outer": "yellow surround is RELATIONAL_VISUAL; unsupported glass/gasket/lower-rail manufacturing dimensions are not encoded",
            "hinge": "cover X span is model-derived; depth/thickness remain UNVERIFIED_VISUAL",
            "ports": "port X reprojection reuses the Apple side-image calibration that drives LOW port placement; it checks projection/export consistency, not independent geometry truth",
            "vertical_scale": "front/side Z uses Apple exact 15.5 mm closed height and fixed reference silhouette rows; model Z extent is not normalized to fit",
        },
    }
    (a.out_dir / "overlay_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
