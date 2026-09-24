import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "assets/device_mockups/iphone_17/generate_low_v30.py"
LEDGER = ROOT / "assets/device_mockups/iphone_17/reference/iphone_17_dimensional_ledger.json"

BODY_H_M = 0.14961


def ledger_reference(element: str) -> float:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    row = next((item for item in data["dimensions"] if item["element"] == element), None)
    if row is None:
        raise AssertionError(f"missing dimensional ledger entry: {element}")
    return float(row["reference"])


class IPhoneFrontEvidenceContractTests(unittest.TestCase):
    def test_dynamic_island_uses_official_front_camera_keepout_center(self):
        source = GENERATOR.read_text(encoding="utf-8")
        match = re.search(r"island_z\s*=\s*H\*0\.5\s*-\s*([0-9.]+)\*MM", source)
        self.assertIsNotNone(match, "front camera keepout datum must remain explicit")
        self.assertAlmostEqual(
            float(match.group(1)),
            ledger_reference("front_camera_keepout.center_from_top"),
            places=6,
        )

    def test_dynamic_island_keepout_size_matches_official_drawing(self):
        source = GENERATOR.read_text(encoding="utf-8")
        match = re.search(
            r'DYNAMIC_ISLAND",\s*([0-9.]+)\*MM,\s*([0-9.]+)\*MM',
            source,
        )
        self.assertIsNotNone(match, "front camera keepout size must remain explicit")
        self.assertAlmostEqual(
            float(match.group(1)),
            ledger_reference("front_camera_keepout.width"),
            places=6,
        )
        self.assertAlmostEqual(
            float(match.group(2)),
            ledger_reference("front_camera_keepout.height"),
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
