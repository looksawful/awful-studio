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


APPLE_DISPLAY_REPAIR = "https://support.apple.com/en-us/123164"
APPLE_BOTTOM_CASE_REPAIR = "https://support.apple.com/en-us/123157"
APPLE_CLOSED_TOP_IMAGE = "https://www.apple.com/v/macbook-pro/specs/c/images/specs/14-inch/dimensions_1_14_inch__da8sc3fnv0cy_large.jpg"
APPLE_CLOSED_FRONT_IMAGE = "https://www.apple.com/v/macbook-pro/specs/c/images/specs/14-inch/dimensions_2_14_inch__fllye8os816y_large.jpg"


def _g2_fact(
    fact_id: str,
    value_mm: float | tuple[float, ...],
    source_class: SourceClass,
    source: str,
    method: str,
    tolerance_mm: float,
    confidence: str,
    *,
    frozen: bool = True,
    frame: str = "chassis_center",
    notes: str = "",
) -> GeometryFact:
    fact = GeometryFact(
        id=fact_id,
        value_mm=value_mm,
        source_class=source_class,
        source=source,
        method=method,
        tolerance_mm=tolerance_mm,
        frame=frame,
        confidence=confidence,
        frozen=frozen,
        notes=notes,
    )
    validate_fact(fact)
    return fact


G2_RELATIONS = {
    "closed_display_assembly": "flush_with_top_case",
    "hinge_cover_semantics": "small_corner_plate",
}


G2_EXTERNAL_FACTS = {
    "hinge_cover_width_mm": _g2_fact(
        "hinge.cover.width", 19.9, SourceClass.APPLE_CALIBRATED,
        APPLE_DISPLAY_REPAIR,
        "calibrated Apple display-repair image; approximate corner-cover width",
        2.0, "MEDIUM_HIGH",
    ),
    "hinge_cover_center_abs_x_mm": _g2_fact(
        "hinge.cover.center_abs_x", 130.1, SourceClass.APPLE_CALIBRATED,
        APPLE_DISPLAY_REPAIR,
        "calibrated Apple display-repair image relative to exact chassis width",
        2.0, "MEDIUM_HIGH",
    ),
    "front_finger_recess_width_mm": _g2_fact(
        "base.front_finger_recess.width", 54.2, SourceClass.APPLE_CALIBRATED,
        APPLE_CLOSED_FRONT_IMAGE,
        "calibrated official closed-front orthographic",
        1.5, "HIGH",
    ),
    "foot_diameter_mm": _g2_fact(
        "bottom.foot.diameter", 17.3, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR,
        "representative value inside calibrated 16.5-18.1 mm repair-image range",
        0.8, "MEDIUM_HIGH",
    ),
    "foot_side_inset_mm": _g2_fact(
        "bottom.foot.side_inset", 20.8, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR,
        "calibrated bottom-case repair image; target inside 19.5-22.5 mm range",
        1.5, "MEDIUM_HIGH",
    ),
    "foot_edge_inset_mm": _g2_fact(
        "bottom.foot.edge_inset", 23.0, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR,
        "calibrated bottom-case repair image; target inside 22.0-23.5 mm range",
        0.75, "MEDIUM_HIGH",
    ),
    "rear_outer_screw_side_inset_mm": _g2_fact(
        "bottom.screw.rear_outer_side_inset", 4.0, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR, "calibrated bottom-case repair image", 1.5, "MEDIUM_HIGH",
    ),
    "rear_screw_edge_inset_mm": _g2_fact(
        "bottom.screw.rear_edge_inset", 7.0, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR, "calibrated bottom-case repair image", 1.0, "MEDIUM_HIGH",
    ),
    "front_outer_screw_side_inset_mm": _g2_fact(
        "bottom.screw.front_outer_side_inset", 7.0, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR, "calibrated bottom-case repair image", 2.0, "MEDIUM_HIGH",
    ),
    "front_screw_edge_inset_mm": _g2_fact(
        "bottom.screw.front_edge_inset", 9.5, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR, "calibrated bottom-case repair image", 1.0, "MEDIUM_HIGH",
    ),
    "inner_screw_center_abs_x_mm": _g2_fact(
        "bottom.screw.inner_center_abs_x", 52.0, SourceClass.APPLE_CALIBRATED,
        APPLE_BOTTOM_CASE_REPAIR, "calibrated bottom-case repair image", 2.75, "MEDIUM_HIGH",
    ),
    "logo_width_mm": _g2_fact(
        "lid.logo.visual_width", 37.2, SourceClass.APPLE_CALIBRATED,
        APPLE_CLOSED_TOP_IMAGE, "calibrated official closed-top orthographic", 2.0, "MEDIUM",
    ),
}


G2_PROVISIONAL_FACTS = {
    "hinge_cover_depth_mm": _g2_fact(
        "hinge.cover.depth", 11.5, SourceClass.PROVISIONAL,
        APPLE_DISPLAY_REPAIR, "visual LOW placeholder; public evidence does not freeze depth",
        0.0, "LOW", frozen=False,
    ),
    "hinge_cover_thickness_mm": _g2_fact(
        "hinge.cover.thickness", 0.8, SourceClass.PROVISIONAL,
        APPLE_DISPLAY_REPAIR, "visual LOW placeholder; public evidence does not freeze thickness",
        0.0, "LOW", frozen=False,
    ),
}


APPLE_PRODUCT_BEZEL_M5 = "https://devimages-cdn.apple.com/design/resources/download/Bezel-MacBook-Pro-M5.dmg"

G2_DISPLAY_FACTS = {
    "active_width_mm": _g2_fact(
        "display.active.width", 302.4, SourceClass.DERIVED,
        APPLE_TECH_SPECS,
        "3024 px at Apple-published 254 ppi: 3024 / 254 * 25.4",
        0.05, "VERIFIED", frame="display_active_center",
    ),
    "active_height_mm": _g2_fact(
        "display.active.height", 196.4, SourceClass.DERIVED,
        APPLE_TECH_SPECS,
        "1964 px at Apple-published 254 ppi: 1964 / 254 * 25.4",
        0.05, "VERIFIED", frame="display_active_center",
    ),
    "opening_corner_radius_mm": _g2_fact(
        "display.active.corner_radius", 4.0966, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "official MacBook Pro M5 Product Bezel alpha contour calibrated by the exact active-display scale",
        0.15, "HIGH", frame="display_active_center",
    ),
    "notch_top_width_mm": _g2_fact(
        "display.notch.top_width", 38.6, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "official Product Bezel notch alpha width at 10 px/mm active-display scale",
        0.15, "HIGH", frame="display_active_center",
    ),
    "notch_height_mm": _g2_fact(
        "display.notch.height", 6.4, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "official Product Bezel notch alpha height at 10 px/mm active-display scale",
        0.15, "HIGH", frame="display_active_center",
    ),
    "notch_lower_radius_mm": _g2_fact(
        "display.notch.lower_radius", 2.1911, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "fitted official Product Bezel lower notch corner at 10 px/mm active-display scale",
        0.20, "HIGH", frame="display_active_center",
    ),
    "camera_center_x_mm": _g2_fact(
        "display.camera.center_x", -0.1, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "official Product Bezel camera center relative to active-display center at 10 px/mm",
        0.20, "HIGH", frame="display_active_center",
    ),
    "camera_from_top_mm": _g2_fact(
        "display.camera.from_top", 1.65, SourceClass.APPLE_CALIBRATED,
        APPLE_PRODUCT_BEZEL_M5,
        "official Product Bezel camera center offset from active-display top at 10 px/mm",
        0.20, "HIGH", frame="display_active_center",
    ),
}


def release_display_measurements() -> dict:
    return {
        key: require_frozen_fact(G2_DISPLAY_FACTS, key)
        for key in G2_DISPLAY_FACTS
    }


def require_frozen_fact(facts: dict[str, GeometryFact], key: str) -> float | tuple[float, ...]:
    fact = facts[key]
    validate_fact(fact)
    if not is_freezable(fact):
        raise ValueError(f"{fact.id}: authoritative geometry requires a frozen non-provisional fact")
    return fact.value_mm


DECK_CALIBRATION = {
    "source_class": SourceClass.APPLE_CALIBRATED.value,
    "source": "keyboard_image",
    "physical_size_mm": [312.6, 221.2],
    "source_edges_px": {
        "left": 108.0,
        "right": 1027.0,
        "rear": 23.0,
        "front": 673.0,
    },
    "mm_per_px": [312.6 / 919.0, 221.2 / 650.0],
    "legacy_rectified_to_source_matrix": [
        [0.7190545146860062, -0.007203154014282462, 118.95837442605284],
        [0.003158238843481908, 0.7138095658027966, 27.990205747306547],
        [-1.2380761460417667e-06, -3.755154471900609e-06, 0.9996502052609483],
    ],
    "method": "official Apple 2x deck raster; straight external chassis edges calibrated to 312.6 x 221.2 mm",
    "tolerance_mm": 0.35,
    "frame": "chassis_center",
    "confidence": "HIGH",
    "frozen": True,
}


PRELIMINARY_CALIBRATION = {
    "keyboard": {
        "key_outer_px": [67.0, 65.0],
        "pitch_px": [77.0, 76.11428571428573],
        "row_centers_px": [105.38095238095232, 181.49523809523805, 257.6095238095238, 333.7238095238095, 409.8380952380952, 485.95238095238096],
        "bounds_px": [67.0, 69.0, 1181.0, 519.0],
        "well_bbox_px": [54.0, 58.0, 1194.0, 529.0],
        "source_class": SourceClass.APPLE_CALIBRATED.value,
        "source": "keyboard_image",
        "method": "G1 key contours reprojected into the official Apple 2x deck raster, then calibrated to the exact chassis envelope",
        "tolerance_mm": 0.35,
        "frame": "chassis_center",
        "confidence": "HIGH",
        "frozen": True,
    },
    "trackpad": {
        "left_x_px": 377.0,
        "right_x_px": 758.0,
        "top_y_px": 419.0,
        "bottom_y_px": 657.0,
        "physical_front_edge_px": 673.0,
        "target_center_x_mm": 0.0,
        "residual_tolerance_mm": 0.25,
        "coordinate_space": "apple_keyboard_image",
        "source_class": SourceClass.APPLE_CALIBRATED.value,
        "source": "keyboard_image",
        "method": "independent seam-edge measurement in the official Apple 2x deck raster calibrated to the external chassis edges",
        "tolerance_mm": 0.35,
        "frame": "chassis_center",
        "confidence": "HIGH",
        "frozen": True,
    },
    "touch_id": {
        "outer_bbox_px": [1113.0, 69.0, 67.0, 67.0],
        "sensor_center_px": [1145.5, 105.5],
        "sensor_diameter_px": 36.0,
        "default_appearance": "black",
        "source_class": SourceClass.APPLE_CALIBRATED.value,
        "source": "keyboard_image",
        "method": "G1 Touch ID contour reprojected into the official Apple 2x deck raster and calibrated to the external chassis edges",
        "tolerance_mm": 0.5,
        "frame": "chassis_center",
        "confidence": "HIGH",
        "frozen": True,
    },
    "speaker": {
        "pitch_px": [2.7076023391812925, 2.7222222222222143],
        "first_center_px": [113.0, 85.45555555555555],
        "last_center_px": [151.49415204678363, 396.03333333333336],
        "column_count": 15,
        "row_count": 114,
        "hole_diameter_px": 1.2,
        "coordinate_space": "apple_keyboard_image",
        "source_class": SourceClass.APPLE_CALIBRATED.value,
        "source": "keyboard_image",
        "method": "periodic dark-dot lattice detected directly in the official Apple 2x deck raster and calibrated to external chassis edges",
        "tolerance_mm": 0.35,
        "frame": "chassis_center",
        "confidence": "HIGH",
        "frozen": True,
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


def source_deck_px_to_mm(x_px: float, y_px: float) -> tuple[float, float]:
    edges = DECK_CALIBRATION["source_edges_px"]
    sx, sy = DECK_CALIBRATION["mm_per_px"]
    center_x = (edges["left"] + edges["right"]) / 2
    center_y = (edges["rear"] + edges["front"]) / 2
    return (x_px - center_x) * sx, (center_y - y_px) * sy


def rectified_deck_px_to_source(x_px: float, y_px: float) -> tuple[float, float]:
    matrix = DECK_CALIBRATION["legacy_rectified_to_source_matrix"]
    hx = matrix[0][0] * x_px + matrix[0][1] * y_px + matrix[0][2]
    hy = matrix[1][0] * x_px + matrix[1][1] * y_px + matrix[1][2]
    hw = matrix[2][0] * x_px + matrix[2][1] * y_px + matrix[2][2]
    return hx / hw, hy / hw


def deck_px_to_mm(x_px: float, y_px: float) -> tuple[float, float]:
    """Map legacy G1 rectified deck coordinates through the corrected G2 datum."""
    return source_deck_px_to_mm(*rectified_deck_px_to_source(x_px, y_px))


def rectified_bbox_to_mm(x0: float, y0: float, x1: float, y1: float) -> dict:
    points = [
        deck_px_to_mm(x0, y0),
        deck_px_to_mm(x1, y0),
        deck_px_to_mm(x0, y1),
        deck_px_to_mm(x1, y1),
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {
        "min_x_mm": min(xs),
        "max_x_mm": max(xs),
        "min_y_mm": min(ys),
        "max_y_mm": max(ys),
        "width_mm": max(xs) - min(xs),
        "height_mm": max(ys) - min(ys),
        "center_x_mm": (min(xs) + max(xs)) / 2,
        "center_y_mm": (min(ys) + max(ys)) / 2,
    }


def _raw_keyboard_item_mm(item: dict) -> dict:
    half_w = item["width_px"] / 2
    half_h = item["height_px"] / 2
    return rectified_bbox_to_mm(
        item["cx_px"] - half_w,
        item["cy_px"] - half_h,
        item["cx_px"] + half_w,
        item["cy_px"] + half_h,
    )


def _keyboard_layout_affine() -> dict:
    """Reconcile the 78-key contour layout to the independently measured G2 aggregate."""
    raw = [_raw_keyboard_item_mm(item) for item in KEYBOARD_LAYOUT_PX]
    raw_min_x = min(box["min_x_mm"] for box in raw)
    raw_max_x = max(box["max_x_mm"] for box in raw)
    raw_min_y = min(box["min_y_mm"] for box in raw)
    raw_max_y = max(box["max_y_mm"] for box in raw)
    raw_center_x = (raw_min_x + raw_max_x) / 2
    raw_center_y = (raw_min_y + raw_max_y) / 2

    x0, y0, x1, y1 = PRELIMINARY_CALIBRATION["keyboard"]["bounds_px"]
    target = rectified_bbox_to_mm(x0, y0, x1, y1)
    return {
        "scale_x": target["width_mm"] / (raw_max_x - raw_min_x),
        "scale_y": target["height_mm"] / (raw_max_y - raw_min_y),
        "raw_center_x_mm": raw_center_x,
        "raw_center_y_mm": raw_center_y,
        "target_center_x_mm": target["center_x_mm"],
        "target_center_y_mm": target["center_y_mm"],
        "source_class": SourceClass.DERIVED.value,
        "method": "affine reconcile of the reprojected 78-key contour layout to the independently measured G2 keyboard aggregate",
    }


def keyboard_item_to_mm(item: dict) -> dict:
    raw = _raw_keyboard_item_mm(item)
    correction = _keyboard_layout_affine()
    sx, sy = correction["scale_x"], correction["scale_y"]
    cx0, cy0 = correction["raw_center_x_mm"], correction["raw_center_y_mm"]
    cx1, cy1 = correction["target_center_x_mm"], correction["target_center_y_mm"]

    min_x = cx1 + (raw["min_x_mm"] - cx0) * sx
    max_x = cx1 + (raw["max_x_mm"] - cx0) * sx
    min_y = cy1 + (raw["min_y_mm"] - cy0) * sy
    max_y = cy1 + (raw["max_y_mm"] - cy0) * sy
    return {
        "min_x_mm": min_x,
        "max_x_mm": max_x,
        "min_y_mm": min_y,
        "max_y_mm": max_y,
        "width_mm": max_x - min_x,
        "height_mm": max_y - min_y,
        "center_x_mm": (min_x + max_x) / 2,
        "center_y_mm": (min_y + max_y) / 2,
    }


def deck_warp_spec() -> dict:
    edges = DECK_CALIBRATION["source_edges_px"]
    width = edges["right"] - edges["left"]
    height = edges["front"] - edges["rear"]
    return {
        "source_rect_px": [edges["left"], edges["rear"], edges["right"], edges["front"]],
        "physical_span_px": [width, height],
        "output_size_px": [math.ceil(width) + 1, math.ceil(height) + 1],
        "destination_quad": [[0.0, 0.0], [width, 0.0], [width, height], [0.0, height]],
    }


def derive_metric_measurements() -> dict:
    measurements = deepcopy(PRELIMINARY_CALIBRATION)
    sx, sy = DECK_CALIBRATION["mm_per_px"]

    keyboard = measurements["keyboard"]
    regular = keyboard_item_to_mm(KEYBOARD_LAYOUT_PX[1])
    keyboard["key_outer_width_mm"] = regular["width_mm"]
    keyboard["key_outer_height_mm"] = regular["height_mm"]
    f1 = deck_px_to_mm(KEYBOARD_LAYOUT_PX[1]["cx_px"], KEYBOARD_LAYOUT_PX[1]["cy_px"])
    f2 = deck_px_to_mm(KEYBOARD_LAYOUT_PX[2]["cx_px"], KEYBOARD_LAYOUT_PX[2]["cy_px"])
    row2 = deck_px_to_mm(KEYBOARD_LAYOUT_PX[15]["cx_px"], KEYBOARD_LAYOUT_PX[15]["cy_px"])
    keyboard["pitch_x_mm"] = abs(f2[0] - f1[0])
    keyboard["pitch_y_mm"] = abs(row2[1] - f1[1])
    keyboard["gap_x_mm"] = keyboard["pitch_x_mm"] - keyboard["key_outer_width_mm"]
    keyboard["gap_y_mm"] = keyboard["pitch_y_mm"] - keyboard["key_outer_height_mm"]
    bx0, by0, bx1, by1 = keyboard["bounds_px"]
    bounds = rectified_bbox_to_mm(bx0, by0, bx1, by1)
    wx0, wy0, wx1, wy1 = keyboard["well_bbox_px"]
    well = rectified_bbox_to_mm(wx0, wy0, wx1, wy1)
    for key, value in bounds.items():
        keyboard["bounds_" + key.replace("_mm", "") + "_mm"] = value
    keyboard["bounds_width_mm"] = bounds["width_mm"]
    keyboard["bounds_height_mm"] = bounds["height_mm"]
    keyboard["bounds_center_x_mm"] = bounds["center_x_mm"]
    keyboard["bounds_center_y_mm"] = bounds["center_y_mm"]
    keyboard["well_width_mm"] = well["width_mm"]
    keyboard["well_height_mm"] = well["height_mm"]
    keyboard["well_center_x_mm"] = well["center_x_mm"]
    keyboard["well_center_y_mm"] = well["center_y_mm"]
    keyboard["row_pitch_mm"] = keyboard["pitch_y_mm"]

    trackpad = measurements["trackpad"]
    left_x, _ = source_deck_px_to_mm(trackpad["left_x_px"], trackpad["top_y_px"])
    right_x, _ = source_deck_px_to_mm(trackpad["right_x_px"], trackpad["top_y_px"])
    _, top_y = source_deck_px_to_mm(trackpad["left_x_px"], trackpad["top_y_px"])
    _, bottom_y = source_deck_px_to_mm(trackpad["left_x_px"], trackpad["bottom_y_px"])
    trackpad["left_x_mm"] = left_x
    trackpad["right_x_mm"] = right_x
    trackpad["width_mm"] = right_x - left_x
    trackpad["center_x_mm"] = (left_x + right_x) / 2
    trackpad["measured_center_x_mm"] = trackpad["center_x_mm"]
    trackpad["height_mm"] = top_y - bottom_y
    trackpad["center_y_mm"] = (top_y + bottom_y) / 2
    trackpad["front_gap_mm"] = (trackpad["physical_front_edge_px"] - trackpad["bottom_y_px"]) * sy
    keyboard["trackpad_gap_mm"] = (
        keyboard["well_center_y_mm"] - keyboard["well_height_mm"] / 2
        - (trackpad["center_y_mm"] + trackpad["height_mm"] / 2)
    )

    touch = measurements["touch_id"]
    x, y, w, h = touch["outer_bbox_px"]
    touch_box = rectified_bbox_to_mm(x, y, x + w, y + h)
    touch["outer_width_mm"] = touch_box["width_mm"]
    touch["outer_height_mm"] = touch_box["height_mm"]
    touch["center_x_mm"] = touch_box["center_x_mm"]
    touch["center_y_mm"] = touch_box["center_y_mm"]
    sensor_x, sensor_y = touch["sensor_center_px"]
    sensor_left = deck_px_to_mm(sensor_x - touch["sensor_diameter_px"] / 2, sensor_y)
    sensor_right = deck_px_to_mm(sensor_x + touch["sensor_diameter_px"] / 2, sensor_y)
    touch["sensor_diameter_mm"] = abs(sensor_right[0] - sensor_left[0])

    speaker = measurements["speaker"]
    speaker["pitch_x_mm"] = speaker["pitch_px"][0] * sx
    speaker["pitch_y_mm"] = speaker["pitch_px"][1] * sy
    first_x, first_y = speaker["first_center_px"]
    last_x, last_y = speaker["last_center_px"]
    center_x_mm, center_y_mm = source_deck_px_to_mm((first_x + last_x) / 2, (first_y + last_y) / 2)
    hole_diameter_mm = speaker["hole_diameter_px"] * (sx + sy) / 2
    speaker["hole_radius_mm"] = hole_diameter_mm / 2
    speaker["observed_width_mm"] = (last_x - first_x) * sx + hole_diameter_mm
    speaker["observed_height_mm"] = (last_y - first_y) * sy + hole_diameter_mm
    speaker["field_center_abs_x_mm"] = abs(center_x_mm)
    speaker["field_center_y_mm"] = center_y_mm
    speaker["first_hole_center_side_inset_mm"] = (first_x - DECK_CALIBRATION["source_edges_px"]["left"]) * sx
    speaker["grid_columns"] = speaker["column_count"]
    speaker["grid_rows"] = speaker["row_count"]

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
