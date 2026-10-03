from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEVICE = ROOT / "assets" / "device_mockups" / "macbook_pro_14"
sys.path.insert(0, str(DEVICE))

from geometry_contract import (
    DECK_CALIBRATION,
    SourceClass,
    derive_metric_measurements,
)


class MacBookG2GeometryContractTests(unittest.TestCase):
    def test_deck_transform_is_apple_calibrated_and_reproduces_outer_chassis(self):
        self.assertEqual(DECK_CALIBRATION["source_class"], SourceClass.APPLE_CALIBRATED.value)
        self.assertTrue(DECK_CALIBRATION["frozen"])
        self.assertEqual(DECK_CALIBRATION["source"], "keyboard_image")
        self.assertAlmostEqual(DECK_CALIBRATION["source_edges_px"]["left"], 108.0, places=6)
        self.assertAlmostEqual(DECK_CALIBRATION["source_edges_px"]["right"], 1027.0, places=6)
        self.assertAlmostEqual(DECK_CALIBRATION["source_edges_px"]["rear"], 23.0, places=6)
        self.assertAlmostEqual(DECK_CALIBRATION["source_edges_px"]["front"], 673.0, places=6)
        sx, sy = DECK_CALIBRATION["mm_per_px"]
        self.assertAlmostEqual(sx, 312.6 / 919.0, places=9)
        self.assertAlmostEqual(sy, 221.2 / 650.0, places=9)
        self.assertLess(abs(sx - sy) / ((sx + sy) / 2), 0.001)
    def test_keyboard_and_well_use_corrected_g2_transform(self):
        keyboard = derive_metric_measurements()["keyboard"]
        self.assertAlmostEqual(keyboard["bounds_width_mm"], 274.1241, delta=0.35)
        self.assertAlmostEqual(keyboard["bounds_height_mm"], 111.0074, delta=0.35)
        self.assertAlmostEqual(keyboard["bounds_center_x_mm"], -0.2620, delta=0.25)
        self.assertAlmostEqual(keyboard["bounds_center_y_mm"], 36.5467, delta=0.25)
        self.assertAlmostEqual(keyboard["well_width_mm"], 280.5396, delta=0.35)
        self.assertAlmostEqual(keyboard["well_height_mm"], 116.1566, delta=0.35)
        self.assertAlmostEqual(keyboard["well_center_x_mm"], -0.2649, delta=0.25)
        self.assertAlmostEqual(keyboard["well_center_y_mm"], 36.6614, delta=0.25)
        self.assertEqual(keyboard["source_class"], SourceClass.APPLE_CALIBRATED.value)
        self.assertTrue(keyboard["frozen"])

    def test_trackpad_uses_independent_source_seams_and_center_datum(self):
        trackpad = derive_metric_measurements()["trackpad"]
        self.assertAlmostEqual(trackpad["width_mm"], 129.5980, delta=0.35)
        self.assertAlmostEqual(trackpad["height_mm"], 80.9932, delta=0.35)
        self.assertAlmostEqual(trackpad["center_x_mm"], 0.0, delta=0.20)
        self.assertAlmostEqual(trackpad["center_y_mm"], -64.6585, delta=0.30)
        self.assertAlmostEqual(trackpad["front_gap_mm"], 5.4449, delta=0.35)
        self.assertEqual(trackpad["source_class"], SourceClass.APPLE_CALIBRATED.value)
        self.assertTrue(trackpad["frozen"])
    def test_touch_id_is_reprojected_through_corrected_chassis_datum(self):
        touch = derive_metric_measurements()["touch_id"]
        self.assertAlmostEqual(touch["outer_width_mm"], 16.5330, delta=0.30)
        self.assertAlmostEqual(touch["outer_height_mm"], 16.3946, delta=0.30)
        self.assertAlmostEqual(touch["center_x_mm"], 128.2881, delta=0.30)
        self.assertAlmostEqual(touch["center_y_mm"], 82.6924, delta=0.30)
        self.assertEqual(touch["source_class"], SourceClass.APPLE_CALIBRATED.value)
        self.assertTrue(touch["frozen"])

    def test_speaker_lattice_matches_official_deck_raster(self):
        speaker = derive_metric_measurements()["speaker"]
        self.assertEqual(speaker["grid_columns"], 15)
        self.assertEqual(speaker["grid_rows"], 114)
        self.assertAlmostEqual(speaker["pitch_x_mm"], 0.9210, delta=0.03)
        self.assertAlmostEqual(speaker["pitch_y_mm"], 0.9264, delta=0.03)
        self.assertAlmostEqual(speaker["field_center_abs_x_mm"], 148.0523, delta=0.30)
        self.assertAlmostEqual(speaker["field_center_y_mm"], 36.4999, delta=0.30)
        self.assertGreater(speaker["first_hole_center_side_inset_mm"], 1.4)
        self.assertEqual(speaker["source_class"], SourceClass.APPLE_CALIBRATED.value)
        self.assertTrue(speaker["frozen"])
    def test_release_generator_cannot_consume_provisional_g2_groups(self):
        measurements = derive_metric_measurements()
        for name in ("keyboard", "trackpad", "touch_id", "speaker"):
            with self.subTest(group=name):
                self.assertNotEqual(
                    measurements[name]["source_class"],
                    SourceClass.PROVISIONAL.value,
                )
                self.assertTrue(measurements[name]["frozen"])


if __name__ == "__main__":
    unittest.main()
