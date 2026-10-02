"""Source-backed MacBook Pro 14 M5 geometry calibration contract.

G1 stores source-pixel measurements plus provenance. Metric values are derived
from those inputs; production Blender geometry must not consume them before
human approval.
"""

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
import math


class SourceClass(str, Enum):
    APPLE_EXACT = "APPLE_EXACT"
    APPLE_CALIBRATED = "APPLE_CALIBRATED"
    APPLE_RELATIONAL = "APPLE_RELATIONAL"
    DERIVED = "DERIVED"
    PROVISIONAL = "PROVISIONAL"


FREEZABLE_SOURCE_CLASSES = {
    SourceClass.APPLE_EXACT,
    SourceClass.APPLE_CALIBRATED,
    SourceClass.APPLE_RELATIONAL,
    SourceClass.DERIVED,
}


@dataclass(frozen=True)
class GeometryFact:
    id: str
    value_mm: float | tuple[float, ...]
    source_class: SourceClass
    source: str
    method: str
    tolerance_mm: float
    frame: str
    confidence: str
    frozen: bool = True
    notes: str = ""


def validate_fact(fact: GeometryFact) -> None:
    if not fact.id:
        raise ValueError("geometry fact id is required")
    if not fact.source:
        raise ValueError(f"{fact.id}: source is required")
    if not fact.method:
        raise ValueError(f"{fact.id}: method is required")
    if not fact.frame:
        raise ValueError(f"{fact.id}: frame is required")
    if fact.tolerance_mm < 0:
        raise ValueError(f"{fact.id}: tolerance must be non-negative")
    if fact.frozen and fact.source_class not in FREEZABLE_SOURCE_CLASSES:
        raise ValueError(f"{fact.id}: provisional facts cannot be frozen")


def is_freezable(fact: GeometryFact) -> bool:
    validate_fact(fact)
    return fact.frozen and fact.source_class in FREEZABLE_SOURCE_CLASSES


APPLE_TECH_SPECS = "https://support.apple.com/en-gb/125405"

CHASSIS_FACTS = {
    "width": GeometryFact(
        id="chassis.width",
        value_mm=312.6,
        source_class=SourceClass.APPLE_EXACT,
        source=APPLE_TECH_SPECS,
        method="Apple-published external envelope",
        tolerance_mm=0.05,
        frame="chassis_center",
        confidence="VERIFIED",
    ),
    "depth": GeometryFact(
        id="chassis.depth",
        value_mm=221.2,
        source_class=SourceClass.APPLE_EXACT,
        source=APPLE_TECH_SPECS,
        method="Apple-published external envelope",
        tolerance_mm=0.05,
        frame="chassis_center",
        confidence="VERIFIED",
    ),
    "closed_height": GeometryFact(
        id="chassis.closed_height",
        value_mm=15.5,
        source_class=SourceClass.APPLE_EXACT,
        source=APPLE_TECH_SPECS,
        method="Apple-published external envelope",
        tolerance_mm=0.05,
        frame="chassis_center",
        confidence="VERIFIED",
    ),
}


DECK_CALIBRATION = {
    "source_class": SourceClass.PROVISIONAL.value,
    "source": "keyboard_image",
    "source_quad_px": [[119.0, 28.0], [1020.0, 32.0], [1017.0, 667.0], [113.0, 662.0]],
    "physical_size_mm": [312.6, 221.2],
    "px_per_mm": 4.0,
    "method": "manual four-corner deck-plane pick followed by projective homography",
    "control_point_fit_residual_px": 0.0,
    "corner_pick_tolerance_px": 1.0,
    "tolerance_mm": 0.25,
    "frame": "chassis_center",
    "confidence": "MEDIUM",
    "frozen": False,
}


PRELIMINARY_CALIBRATION = {
    "keyboard": {
        "key_outer_px": [67.0, 65.0],
        "pitch_px": [77.0, 75.832],
        "source_class": SourceClass.PROVISIONAL.value,
        "source": "keyboard_image",
        "method": "median key contours after chassis-plane homography",
        "tolerance_mm": 0.25,
        "frame": "chassis_center",
        "confidence": "MEDIUM",
        "frozen": False,
    },
    "trackpad": {
        "left_x_px": 363.64476210769783,
        "right_x_px": 891.4070901746444,
        "top_y_px": 542.6468469608157,
        "bottom_y_px": 873.9046196782626,
        "physical_front_edge_px": 884.8,
        "target_center_x_mm": 0.0,
        "residual_tolerance_mm": 0.75,
        "source_class": SourceClass.PROVISIONAL.value,
        "source": "keyboard_image",
        "method": "Sobel seam centroids on exact 4 px/mm rectified chassis plane",
        "tolerance_mm": 0.25,
        "frame": "chassis_center",
        "confidence": "MEDIUM",
        "frozen": False,
    },
    "touch_id": {
        "outer_bbox_px": [1113.0, 69.0, 67.0, 67.0],
        "sensor_center_px": [1145.5, 105.5],
        "sensor_diameter_px": 36.0,
        "default_appearance": "black",
        "source_class": SourceClass.PROVISIONAL.value,
        "source": "keyboard_image",
        "method": "rectified key contour plus circular sensor extent",
        "tolerance_mm": 0.5,
        "frame": "chassis_center",
        "confidence": "MEDIUM",
        "frozen": False,
    },
    "speaker": {
        "pitch_px": [4.0, 4.0],
        "left_field_bbox_px": [0.0, 80.0, 54.0, 515.0],
        "column_count": None,
        "row_count": None,
        "source_class": SourceClass.PROVISIONAL.value,
        "source": "keyboard_image",
        "method": "rectified-raster periodicity plus dark-blob field extent",
        "tolerance_mm": 0.25,
        "frame": "chassis_center",
        "confidence": "MEDIUM",
        "frozen": False,
    },
    "display": {
        "opening_origin_px": [418.0, 288.0],
        "opening_px": [3024.0, 1964.0],
        "px_per_mm": 10.0,
        "notch_relative_bbox_px": [1319.0, 0.0, 1705.0, 64.0],
        "camera_center_px": [1929.0, 304.5],
        "outer_lid_x_px": [362.0, 3496.0],
        "opening_corner_radius_px": 40.966,
        "opening_corner_fit_rms_px": 0.642,
        "notch_lower_radius_px": 21.911,
        "notch_fit_rms_px": 0.303,
        "outer_lid_radius_fit_px": 89.85,
        "outer_lid_fit_rms_px": 0.324,
        "outer_lid_frozen": False,
        "source_class": SourceClass.PROVISIONAL.value,
        "source": "product_bezel_space_black",
        "method": "Product Bezel alpha geometry at native 3024x1964 / 254 ppi scale",
        "tolerance_mm": 0.1,
        "frame": "display_active_center",
        "confidence": "HIGH",
        "frozen": False,
    },
}


def deck_px_to_mm(x_px: float, y_px: float) -> tuple[float, float]:
    width_mm, depth_mm = DECK_CALIBRATION["physical_size_mm"]
    scale = DECK_CALIBRATION["px_per_mm"]
    return x_px / scale - width_mm / 2, depth_mm / 2 - y_px / scale


def deck_warp_spec() -> dict:
    width_mm, depth_mm = DECK_CALIBRATION["physical_size_mm"]
    scale = DECK_CALIBRATION["px_per_mm"]
    physical_width_px = width_mm * scale
    physical_height_px = depth_mm * scale
    return {
        "physical_span_px": [physical_width_px, physical_height_px],
        "output_size_px": [
            math.ceil(physical_width_px) + 1,
            math.ceil(physical_height_px) + 1,
        ],
        "destination_quad": [
            [0.0, 0.0],
            [physical_width_px, 0.0],
            [physical_width_px, physical_height_px],
            [0.0, physical_height_px],
        ],
    }


def derive_metric_measurements() -> dict:
    measurements = deepcopy(PRELIMINARY_CALIBRATION)
    scale = DECK_CALIBRATION["px_per_mm"]
    _, depth_mm = DECK_CALIBRATION["physical_size_mm"]

    keyboard = measurements["keyboard"]
    keyboard["key_outer_width_mm"] = keyboard["key_outer_px"][0] / scale
    keyboard["key_outer_height_mm"] = keyboard["key_outer_px"][1] / scale
    keyboard["pitch_x_mm"] = keyboard["pitch_px"][0] / scale
    keyboard["pitch_y_mm"] = keyboard["pitch_px"][1] / scale
    keyboard["gap_x_mm"] = keyboard["pitch_x_mm"] - keyboard["key_outer_width_mm"]
    keyboard["gap_y_mm"] = keyboard["pitch_y_mm"] - keyboard["key_outer_height_mm"]

    trackpad = measurements["trackpad"]
    trackpad["left_x_mm"], _ = deck_px_to_mm(trackpad["left_x_px"], 0.0)
    trackpad["right_x_mm"], _ = deck_px_to_mm(trackpad["right_x_px"], 0.0)
    trackpad["measured_center_x_mm"] = (trackpad["left_x_mm"] + trackpad["right_x_mm"]) / 2
    trackpad["height_mm"] = (trackpad["bottom_y_px"] - trackpad["top_y_px"]) / scale
    trackpad["front_gap_mm"] = (
        trackpad["physical_front_edge_px"] - trackpad["bottom_y_px"]
    ) / scale
    trackpad["center_y_mm"] = depth_mm / 2 - (
        (trackpad["top_y_px"] + trackpad["bottom_y_px"]) / 2
    ) / scale

    touch = measurements["touch_id"]
    x, y, w, h = touch["outer_bbox_px"]
    touch["outer_width_mm"] = w / scale
    touch["outer_height_mm"] = h / scale
    touch["center_x_mm"], touch["center_y_mm"] = deck_px_to_mm(x + w / 2, y + h / 2)
    touch["sensor_diameter_mm"] = touch["sensor_diameter_px"] / scale

    speaker = measurements["speaker"]
    speaker["pitch_x_mm"] = speaker["pitch_px"][0] / scale
    speaker["pitch_y_mm"] = speaker["pitch_px"][1] / scale
    sx0, sy0, sx1, sy1 = speaker["left_field_bbox_px"]
    speaker["observed_width_mm"] = (sx1 - sx0) / scale
    speaker["observed_height_mm"] = (sy1 - sy0) / scale

    display = measurements["display"]
    display_scale = display["px_per_mm"]
    opening_w, opening_h = display["opening_px"]
    display["active_width_mm"] = opening_w / display_scale
    display["active_height_mm"] = opening_h / display_scale
    left, top, right, bottom = display["notch_relative_bbox_px"]
    display["notch_top_width_mm"] = (right - left) / display_scale
    display["notch_height_mm"] = (bottom - top) / display_scale
    camera_x, camera_y = display["camera_center_px"]
    opening_x, opening_y = display["opening_origin_px"]
    display["camera_center_x_mm"] = (
        camera_x - (opening_x + opening_w / 2)
    ) / display_scale
    display["camera_from_top_mm"] = (camera_y - opening_y) / display_scale
    outer_left, outer_right = display["outer_lid_x_px"]
    display["outer_lid_width_px"] = outer_right - outer_left + 1
    display["outer_lid_width_mm_at_display_scale"] = (
        display["outer_lid_width_px"] / display_scale
    )
    display["outer_lid_width_residual_mm"] = (
        display["outer_lid_width_mm_at_display_scale"] - CHASSIS_FACTS["width"].value_mm
    )
    display["opening_corner_radius_mm"] = display["opening_corner_radius_px"] / display_scale
    display["opening_corner_fit_rms_mm"] = display["opening_corner_fit_rms_px"] / display_scale
    display["notch_lower_radius_mm"] = display["notch_lower_radius_px"] / display_scale
    display["notch_fit_rms_mm"] = display["notch_fit_rms_px"] / display_scale
    display["outer_lid_radius_fit_mm"] = display["outer_lid_radius_fit_px"] / display_scale
    display["outer_lid_fit_rms_mm"] = display["outer_lid_fit_rms_px"] / display_scale
    return measurements
