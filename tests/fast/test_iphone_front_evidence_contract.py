import json
from pathlib import Path
import re
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "assets/device_mockups/iphone_17/generate_low_v30.py"
LEDGER = ROOT / "assets/device_mockups/iphone_17/reference/iphone_17_dimensional_ledger.json"
SCREEN = ROOT / "assets/device_mockups/iphone_17/reference/ios26_home_screen_1206x2622.png"

BODY_H_MM = 149.61
SCREEN_W_MM = 66.57
SCREEN_H_MM = 144.79
BODY_H_M = BODY_H_MM / 1000.0


def ledger_reference(element: str) -> float:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    row = next((item for item in data["dimensions"] if item["element"] == element), None)
    if row is None:
        raise AssertionError(f"missing dimensional ledger entry: {element}")
    return float(row["reference"])


def raster_dynamic_island_contract() -> tuple[float, float, float]:
    image = Image.open(SCREEN).convert("L")
    # Tight center/top crop excludes status icons and rounded display corners.
    left, top, right, bottom = 350, 0, 856, 160
    mask = image.crop((left, top, right, bottom)).point(lambda value: 255 if value < 28 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        raise AssertionError("could not locate Dynamic Island in official Apple screen raster")
    x0, y0, x1, y1 = bbox
    center_y_px = top + (y0 + y1) / 2.0
    width_mm = (x1 - x0) / image.width * SCREEN_W_MM
    height_mm = (y1 - y0) / image.height * SCREEN_H_MM
    center_from_body_top_mm = (
        (BODY_H_MM - SCREEN_H_MM) / 2.0
        + center_y_px / image.height * SCREEN_H_MM
    )
    return width_mm, height_mm, center_from_body_top_mm


class IPhoneFrontEvidenceContractTests(unittest.TestCase):
    def test_visible_dynamic_island_tracks_official_screen_raster(self):
        source = GENERATOR.read_text(encoding="utf-8")
        z_match = re.search(
            r"(?:island_visual_z|island_z)\s*=\s*H\*0\.5\s*-\s*([0-9.]+)\*MM",
            source,
        )
        self.assertIsNotNone(z_match, "visible Dynamic Island datum must remain explicit")
        size_match = re.search(
            r'DYNAMIC_ISLAND",\s*([0-9.]+)\*MM,\s*([0-9.]+)\*MM',
            source,
        )
        self.assertIsNotNone(size_match, "visible Dynamic Island dimensions must remain explicit")

        raster_w_mm, raster_h_mm, raster_center_mm = raster_dynamic_island_contract()
        geometry_center_mm = float(z_match.group(1))
        geometry_w_mm = float(size_match.group(1))
        geometry_h_mm = float(size_match.group(2))

        self.assertLessEqual(
            abs(geometry_center_mm - raster_center_mm),
            0.35,
            f"visible island detached from screen raster: geometry={geometry_center_mm:.3f}mm "
            f"raster={raster_center_mm:.3f}mm",
        )
        self.assertLessEqual(abs(geometry_w_mm - raster_w_mm), 0.35)
        self.assertLessEqual(abs(geometry_h_mm - raster_h_mm), 0.35)

    def test_front_hardware_uses_official_keepout_datum_independently(self):
        source = GENERATOR.read_text(encoding="utf-8")
        hardware_match = re.search(
            r"front_hardware_z\s*=\s*H\*0\.5\s*-\s*([0-9.]+)\*MM",
            source,
        )
        self.assertIsNotNone(
            hardware_match,
            "front hardware must use an explicit engineering datum separate from visual island",
        )
        self.assertAlmostEqual(
            float(hardware_match.group(1)),
            ledger_reference("front_camera_keepout.center_from_top"),
            places=6,
        )
        self.assertRegex(
            source,
            r'FRONT_SENSOR_PILL".*location=\(-4\.15\*MM,\s*detail_y,\s*front_hardware_z\)',
        )
        self.assertRegex(
            source,
            r'FRONT_CAMERA_RING".*\(cam_x,\s*detail_y,\s*front_hardware_z\)',
        )

    def test_front_camera_keepout_dimensions_match_official_drawing(self):
        self.assertAlmostEqual(
            ledger_reference("front_camera_keepout.width"),
            20.75,
            places=6,
        )
        self.assertAlmostEqual(
            ledger_reference("front_camera_keepout.height"),
            5.12,
            places=6,
        )

    def test_bottom_macro_camera_has_steep_enough_underside_angle(self):
        source = GENERATOR.read_text(encoding="utf-8")
        match = re.search(
            r'cam_bottom\s*=\s*persp\("CAM_BOTTOM_MACRO",\s*'
            r'\(0\.0,\s*([-0-9.]+),\s*([-0-9.]+)\),\s*'
            r'\(0,0,-H\*([0-9.]+)\)',
            source,
        )
        self.assertIsNotNone(match, "bottom macro camera contract must remain explicit")
        camera_y = float(match.group(1))
        camera_z = float(match.group(2))
        target_fraction = float(match.group(3))
        target_z = -BODY_H_M * target_fraction
        vertical = abs(camera_z - target_z)
        depth = abs(camera_y)
        self.assertGreaterEqual(
            vertical / depth,
            0.75,
            "bottom macro camera is too face-on to prove USB-C, microphones and speakers",
        )


if __name__ == "__main__":
    unittest.main()
