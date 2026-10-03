"""Generate G2 MacBook Pro 14 M5 calibration evidence from pinned Apple assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assets.device_mockups.macbook_pro_14.geometry_contract import (
    CHASSIS_FACTS,
    DECK_CALIBRATION,
    PRELIMINARY_CALIBRATION,
    deck_px_to_mm,
    deck_warp_spec,
    derive_metric_measurements,
    rectified_deck_px_to_source,
    source_deck_px_to_mm,
)

ASSET_DIR = ROOT / "assets" / "device_mockups" / "macbook_pro_14"
REGISTER = ASSET_DIR / "calibration_sources.json"


def verify_sha256(path: Path, expected: str) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected.lower():
        raise ValueError(f"hash mismatch for {path}: {digest} != {expected}")
    return digest


def _fact_dict(fact) -> dict:
    return {
        "id": fact.id,
        "value_mm": fact.value_mm,
        "source_class": fact.source_class.value,
        "source": fact.source,
        "method": fact.method,
        "tolerance_mm": fact.tolerance_mm,
        "frame": fact.frame,
        "confidence": fact.confidence,
        "frozen": fact.frozen,
    }


def build_report() -> dict:
    return {
        "gate": "G2",
        "status": "calibrated_geometry_active_human_model_approval_pending",
        "coordinate_frame": {
            "origin": "chassis plan center",
            "x": "positive right",
            "y": "positive toward hinge",
            "z": "positive upward",
        },
        "deck_calibration": DECK_CALIBRATION,
        "exact_datums": {k: _fact_dict(v) for k, v in CHASSIS_FACTS.items()},
        "measurements": derive_metric_measurements(),
    }


def _load_register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def _source_record(source_id: str) -> dict:
    for record in _load_register()["sources"]:
        if record["id"] == source_id:
            return record
    raise KeyError(f"unknown calibration source: {source_id}")


def _cache_path(cache_root: Path, source_id: str) -> Path:
    record = _source_record(source_id)
    cache_key = record.get("cache_key")
    if not cache_key:
        raise ValueError(f"source has no cache_key: {source_id}")
    return cache_root / Path(cache_key)


def verify_cache(cache_root: Path) -> list[dict]:
    verified = []
    for record in _load_register()["sources"]:
        cache_key = record.get("cache_key")
        if not cache_key:
            continue
        path = cache_root / Path(cache_key)
        digest = verify_sha256(path, record["sha256"])
        verified.append(
            {
                "id": record["id"],
                "cache_key": cache_key,
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
    return verified


def _rectified_deck(cache_root: Path):
    import cv2
    import numpy as np

    source = _cache_path(cache_root, DECK_CALIBRATION["source"])
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(source)
    edges = DECK_CALIBRATION["source_edges_px"]
    left, right = round(edges["left"]), round(edges["right"])
    rear, front = round(edges["rear"]), round(edges["front"])
    crop = image[rear : front + 1, left : right + 1].copy()
    matrix = np.array([[1.0, 0.0, -left], [0.0, 1.0, -rear], [0.0, 0.0, 1.0]])
    return crop, matrix


def render_deck_overlay(cache_root: Path, out_dir: Path) -> dict:
    import cv2

    image, matrix = _rectified_deck(cache_root)
    h, w = image.shape[:2]
    edges = DECK_CALIBRATION["source_edges_px"]
    left, rear = edges["left"], edges["rear"]
    measurements = derive_metric_measurements()
    track = measurements["trackpad"]
    touch = measurements["touch_id"]
    speaker = measurements["speaker"]

    def local_source(x, y):
        return round(x - left), round(y - rear)

    cv2.rectangle(
        image,
        local_source(track["left_x_px"], track["top_y_px"]),
        local_source(track["right_x_px"], track["bottom_y_px"]),
        (0, 255, 255),
        3,
    )

    tx, ty, tw, th = touch["outer_bbox_px"]
    corners = [
        rectified_deck_px_to_source(tx, ty),
        rectified_deck_px_to_source(tx + tw, ty + th),
    ]
    cv2.rectangle(
        image,
        local_source(*corners[0]),
        local_source(*corners[1]),
        (0, 180, 255),
        3,
    )
    sensor_source = rectified_deck_px_to_source(*touch["sensor_center_px"])
    sensor_radius_px = round(touch["sensor_diameter_mm"] / DECK_CALIBRATION["mm_per_px"][0] / 2)
    cv2.circle(image, local_source(*sensor_source), sensor_radius_px, (255, 180, 0), 3)

    first_x, first_y = speaker["first_center_px"]
    last_x, last_y = speaker["last_center_px"]
    half_hole = speaker["hole_diameter_px"] / 2
    cv2.rectangle(
        image,
        local_source(first_x - half_hole, first_y - half_hole),
        local_source(last_x + half_hole, last_y + half_hole),
        (255, 0, 255),
        3,
    )
    center = (edges["left"] + edges["right"]) / 2
    mirror_first = 2 * center - last_x
    mirror_last = 2 * center - first_x
    cv2.rectangle(
        image,
        local_source(mirror_first - half_hole, first_y - half_hole),
        local_source(mirror_last + half_hole, last_y + half_hole),
        (255, 0, 255),
        3,
    )

    cv2.putText(
        image,
        "G2 APPLE-CALIBRATED chassis plane",
        (24, h - 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )
    path = out_dir / "deck_calibration_overlay.png"
    cv2.imwrite(str(path), image)
    return {
        "path": str(path.relative_to(ROOT)),
        "size_px": [w, h],
        "source_crop_px": [edges["left"], edges["rear"], edges["right"], edges["front"]],
        "source_to_crop_matrix": matrix.tolist(),
        "scale_mm_per_px": DECK_CALIBRATION["mm_per_px"],
    }


def _checker_rgba(width: int, height: int):
    import numpy as np

    tile = 64
    yy, xx = np.indices((height, width))
    mask = ((xx // tile) + (yy // tile)) % 2
    base = np.where(mask[..., None] == 0, 210, 245).astype(np.uint8)
    return np.concatenate(
        [
            np.repeat(base, 3, axis=2),
            np.full((height, width, 1), 255, dtype=np.uint8),
        ],
        axis=2,
    )


def render_display_overlay(cache_root: Path, out_dir: Path) -> dict:
    import cv2
    import numpy as np

    display = derive_metric_measurements()["display"]
    source = _cache_path(cache_root, display["source"])
    rgba = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)
    if rgba is None or rgba.shape[2] != 4:
        raise ValueError(f"expected RGBA Product Bezel: {source}")
    h, w = rgba.shape[:2]

    bg = _checker_rgba(w, h)
    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
    comp = (
        rgba[:, :, :3].astype(np.float32) * alpha
        + bg[:, :, :3] * (1.0 - alpha)
    ).astype(np.uint8)

    ox, oy = map(round, display["opening_origin_px"])
    ow, oh = map(round, display["opening_px"])
    cv2.rectangle(comp, (ox, oy), (ox + ow, oy + oh), (0, 255, 255), 5)

    left, top, right, bottom = display["notch_relative_bbox_px"]
    cv2.rectangle(
        comp,
        (round(ox + left), round(oy + top)),
        (round(ox + right), round(oy + bottom)),
        (255, 0, 255),
        5,
    )

    cv2.circle(comp, tuple(map(round, display["camera_center_px"])), 18, (0, 180, 255), 5)
    outer_left, outer_right = map(round, display["outer_lid_x_px"])
    cv2.line(comp, (outer_left, 350), (outer_right, 350), (255, 255, 0), 5)

    cv2.putText(
        comp,
        f"active display {ow}x{oh} = {display['active_width_mm']:.1f}x{display['active_height_mm']:.1f} mm",
        (460, 2380),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 255),
        3,
        cv2.LINE_AA,
    )
    exact_width = CHASSIS_FACTS["width"].value_mm
    cv2.putText(
        comp,
        f"outer lid cross-check: {display['outer_lid_width_mm_at_display_scale']:.1f} mm vs Apple {exact_width:.1f} mm ({display['outer_lid_width_residual_mm']:+.1f} mm)",
        (460, 2430),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 0),
        3,
        cv2.LINE_AA,
    )
    cv2.putText(
        comp,
        "G2 display: active matrix exact; outer assembly still provisional",
        (460, 2480),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 255),
        3,
        cv2.LINE_AA,
    )

    path = out_dir / "display_calibration_overlay.png"
    cv2.imwrite(str(path), comp)
    return {"path": str(path.relative_to(ROOT)), "size_px": [w, h]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ASSET_DIR / "evidence" / "g2_calibration",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report()
    report["source_verification"] = verify_cache(args.cache_root)
    report["overlays"] = {
        "deck": render_deck_overlay(args.cache_root, args.out_dir),
        "display": render_display_overlay(args.cache_root, args.out_dir),
    }
    report_path = args.out_dir / "calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
