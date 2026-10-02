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
        "pitch_px": [77.0, 76.11428571428573],
        "row_centers_px": [105.38095238095232, 181.49523809523805, 257.6095238095238, 333.7238095238095, 409.8380952380952, 485.95238095238096],
        "bounds_px": [67.0, 69.0, 1181.0, 519.0],
        "well_bbox_px": [54.0, 58.0, 1194.0, 529.0],
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
        "column_count": 12,
        "row_count": 109,
        "hole_diameter_px": 2.0,
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


KEYBOARD_LAYOUT_PX = [
    {"name":"KEY_05_00","label":"esc","cx_px":120,"cy_px":105.38095238095232,"width_px":106,"height_px":65},
    {"name":"KEY_05_01","label":"F1","cx_px":216.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_02","label":"F2","cx_px":294.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_03","label":"F3","cx_px":372,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_04","label":"F4","cx_px":449.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_05","label":"F5","cx_px":527,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_06","label":"F6","cx_px":604.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_07","label":"F7","cx_px":682,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_08","label":"F8","cx_px":759.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_09","label":"F9","cx_px":836.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_10","label":"F10","cx_px":914.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_11","label":"F11","cx_px":991.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_05_12","label":"F12","cx_px":1069.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"TOUCH_ID","label":"Touch ID","cx_px":1146.5,"cy_px":105.38095238095232,"width_px":67,"height_px":65},
    {"name":"KEY_04_00","label":"`","cx_px":101.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_01","label":"1","cx_px":178.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_02","label":"2","cx_px":256.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_03","label":"3","cx_px":333.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_04","label":"4","cx_px":411.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_05","label":"5","cx_px":488.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_06","label":"6","cx_px":566.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_07","label":"7","cx_px":643.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_08","label":"8","cx_px":721.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_09","label":"9","cx_px":798.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_10","label":"0","cx_px":876,"cy_px":181.49523809523805,"width_px":68,"height_px":65},
    {"name":"KEY_04_11","label":"-","cx_px":953.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_12","label":"=","cx_px":1030.5,"cy_px":181.49523809523805,"width_px":67,"height_px":65},
    {"name":"KEY_04_13","label":"delete","cx_px":1127.5,"cy_px":181.49523809523805,"width_px":105,"height_px":65},
    {"name":"KEY_03_00","label":"tab","cx_px":121,"cy_px":257.6095238095238,"width_px":106,"height_px":65},
    {"name":"KEY_03_01","label":"Q","cx_px":218,"cy_px":257.6095238095238,"width_px":68,"height_px":65},
    {"name":"KEY_03_02","label":"W","cx_px":295.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_03","label":"E","cx_px":373,"cy_px":257.6095238095238,"width_px":68,"height_px":65},
    {"name":"KEY_03_04","label":"R","cx_px":450.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_05","label":"T","cx_px":528,"cy_px":257.6095238095238,"width_px":68,"height_px":65},
    {"name":"KEY_03_06","label":"Y","cx_px":605.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_07","label":"U","cx_px":683,"cy_px":257.6095238095238,"width_px":68,"height_px":65},
    {"name":"KEY_03_08","label":"I","cx_px":760.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_09","label":"O","cx_px":837.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_10","label":"P","cx_px":915.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_11","label":"[","cx_px":992.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_12","label":"]","cx_px":1069.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_03_13","label":"\\","cx_px":1147.5,"cy_px":257.6095238095238,"width_px":67,"height_px":65},
    {"name":"KEY_02_00","label":"caps","cx_px":131.5,"cy_px":333.7238095238095,"width_px":125,"height_px":65},
    {"name":"KEY_02_01","label":"A","cx_px":238.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_02","label":"S","cx_px":315.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_03","label":"D","cx_px":393.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_04","label":"F","cx_px":470.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_05","label":"G","cx_px":548,"cy_px":333.7238095238095,"width_px":68,"height_px":65},
    {"name":"KEY_02_06","label":"H","cx_px":625.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_07","label":"J","cx_px":702.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_08","label":"K","cx_px":780.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_09","label":"L","cx_px":857.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_10","label":";","cx_px":934.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_11","label":"'","cx_px":1012.5,"cy_px":333.7238095238095,"width_px":67,"height_px":65},
    {"name":"KEY_02_12","label":"return","cx_px":1118.5,"cy_px":333.7238095238095,"width_px":125,"height_px":65},
    {"name":"KEY_01_00","label":"shift","cx_px":152,"cy_px":409.8380952380952,"width_px":164,"height_px":65},
    {"name":"KEY_01_01","label":"Z","cx_px":277.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_02","label":"X","cx_px":355,"cy_px":409.8380952380952,"width_px":68,"height_px":65},
    {"name":"KEY_01_03","label":"C","cx_px":432.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_04","label":"V","cx_px":509.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_05","label":"B","cx_px":587.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_06","label":"N","cx_px":664.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_07","label":"M","cx_px":742,"cy_px":409.8380952380952,"width_px":66,"height_px":65},
    {"name":"KEY_01_08","label":",","cx_px":819.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_09","label":".","cx_px":896.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_10","label":"/","cx_px":974.5,"cy_px":409.8380952380952,"width_px":67,"height_px":65},
    {"name":"KEY_01_11","label":"shift","cx_px":1099.5,"cy_px":409.8380952380952,"width_px":163,"height_px":65},
    {"name":"KEY_00_00","label":"fn","cx_px":103.5,"cy_px":485.95238095238096,"width_px":67,"height_px":65},
    {"name":"KEY_00_01","label":"control","cx_px":181.5,"cy_px":485.95238095238096,"width_px":67,"height_px":65},
    {"name":"KEY_00_02","label":"option","cx_px":258.5,"cy_px":485.95238095238096,"width_px":67,"height_px":65},
    {"name":"KEY_00_03","label":"command","cx_px":346,"cy_px":485.95238095238096,"width_px":86,"height_px":65},
    {"name":"KEY_00_04","label":"space","cx_px":588,"cy_px":485.95238095238096,"width_px":376,"height_px":65},
    {"name":"KEY_00_05","label":"command","cx_px":829.5,"cy_px":485.95238095238096,"width_px":87,"height_px":65},
    {"name":"KEY_00_06","label":"option","cx_px":916.5,"cy_px":485.95238095238096,"width_px":67,"height_px":65},
    {"name":"KEY_ARROW_0","label":"←","cx_px":993.5,"cy_px":499.5,"width_px":67,"height_px":31},
    {"name":"KEY_ARROW_1","label":"↓","cx_px":1071.5,"cy_px":501,"width_px":67,"height_px":28},
    {"name":"KEY_ARROW_2","label":"→","cx_px":1148.5,"cy_px":500.5,"width_px":67,"height_px":33},
    {"name":"KEY_ARROW_3","label":"↑","cx_px":1071,"cy_px":466.5,"width_px":67,"height_px":31},
]


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
    bx0, by0, bx1, by1 = keyboard["bounds_px"]
    keyboard["bounds_width_mm"] = (bx1 - bx0) / scale
    keyboard["bounds_height_mm"] = (by1 - by0) / scale
    keyboard["bounds_center_x_mm"], keyboard["bounds_center_y_mm"] = deck_px_to_mm(
        (bx0 + bx1) / 2, (by0 + by1) / 2
    )
    wx0, wy0, wx1, wy1 = keyboard["well_bbox_px"]
    keyboard["well_width_mm"] = (wx1 - wx0) / scale
    keyboard["well_height_mm"] = (wy1 - wy0) / scale
    keyboard["well_center_x_mm"], keyboard["well_center_y_mm"] = deck_px_to_mm(
        (wx0 + wx1) / 2, (wy0 + wy1) / 2
    )
    keyboard["row_pitch_mm"] = keyboard["pitch_px"][1] / scale

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
    keyboard["trackpad_gap_mm"] = (
        keyboard["well_center_y_mm"] - keyboard["well_height_mm"] / 2
        - (trackpad["center_y_mm"] + trackpad["height_mm"] / 2)
    )

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
    speaker_center_x_mm, speaker["field_center_y_mm"] = deck_px_to_mm(
        (sx0 + sx1) / 2, (sy0 + sy1) / 2
    )
    speaker["field_center_abs_x_mm"] = abs(speaker_center_x_mm)
    speaker["grid_columns"] = speaker["column_count"]
    speaker["grid_rows"] = speaker["row_count"]
    speaker["hole_radius_mm"] = speaker["hole_diameter_px"] / scale / 2

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
