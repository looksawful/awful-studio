from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEVICE = ROOT / "assets" / "device_mockups" / "macbook_pro_14"
sys.path.insert(0, str(DEVICE))

from geometry_contract import (
    KEYBOARD_LAYOUT_PX,
    derive_metric_measurements,
)


class MacBookG2ModelContractTests(unittest.TestCase):
    def test_keyboard_layout_is_complete_78_key_ansi(self):
        self.assertEqual(len(KEYBOARD_LAYOUT_PX), 78)
        names = [item["name"] for item in KEYBOARD_LAYOUT_PX]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("TOUCH_ID", names)
        self.assertEqual(
            {name for name in names if name.startswith("KEY_ARROW_")},
            {"KEY_ARROW_0", "KEY_ARROW_1", "KEY_ARROW_2", "KEY_ARROW_3"},
        )

    def test_keyboard_bounds_and_row_pitch_come_from_g2_apple_calibration(self):
        keyboard = derive_metric_measurements()["keyboard"]
        self.assertAlmostEqual(keyboard["bounds_width_mm"], 274.1241, delta=0.35)
        self.assertAlmostEqual(keyboard["bounds_height_mm"], 111.0074, delta=0.35)
        self.assertAlmostEqual(keyboard["bounds_center_x_mm"], -0.2620, delta=0.25)
        self.assertAlmostEqual(keyboard["bounds_center_y_mm"], 36.5467, delta=0.25)
        self.assertAlmostEqual(keyboard["row_pitch_mm"], 18.4800, delta=0.03)

    def test_speaker_grid_matches_g2_apple_raster(self):
        speaker = derive_metric_measurements()["speaker"]
        self.assertEqual(speaker["grid_columns"], 15)
        self.assertEqual(speaker["grid_rows"], 114)
        self.assertAlmostEqual(speaker["pitch_x_mm"], 0.9210, delta=0.03)
        self.assertAlmostEqual(speaker["pitch_y_mm"], 0.9264, delta=0.03)
        self.assertAlmostEqual(speaker["field_center_abs_x_mm"], 148.0523, delta=0.25)
        self.assertAlmostEqual(speaker["field_center_y_mm"], 36.4999, delta=0.25)

    def test_generator_consumes_geometry_contract_instead_of_old_magic_layout(self):
        generate = (DEVICE / "generate_low.py").read_text(encoding="utf-8")
        deck = (DEVICE / "deck_details.py").read_text(encoding="utf-8")
        construction = (DEVICE / "construction_details.py").read_text(encoding="utf-8")
        self.assertIn("derive_metric_measurements", generate)
        self.assertIn("KEYBOARD_LAYOUT_PX", deck)
        self.assertNotIn("SPEAKER_ROWS = 88", deck)
        self.assertNotIn("SPEAKER_COLS = 9", deck)
        self.assertNotIn("CUT_SPEAKER_FIELDS", deck)
        self.assertIn("SPEAKER_MASTER_PROXY_", deck)
        self.assertNotIn("location=(0, -57*mm", deck)
        self.assertNotIn("32*mm, 8.2*mm", construction)


if __name__ == "__main__":
    unittest.main()
