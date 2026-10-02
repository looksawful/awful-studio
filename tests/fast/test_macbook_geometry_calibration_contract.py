import json
from pathlib import Path
import unittest

from assets.device_mockups.macbook_pro_14.geometry_contract import (
    CHASSIS_FACTS,
    DECK_CALIBRATION,
    PRELIMINARY_CALIBRATION,
    SourceClass,
    derive_metric_measurements,
    is_freezable,
    validate_fact,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTER = (
    ROOT
    / "assets"
    / "device_mockups"
    / "macbook_pro_14"
    / "calibration_sources.json"
)


class MacBookGeometryCalibrationContractTests(unittest.TestCase):
    def test_source_register_pins_primary_apple_assets(self):
        payload = json.loads(REGISTER.read_text(encoding="utf-8"))
        sources = {entry["id"]: entry for entry in payload["sources"]}
        expected = {
            "keyboard_image": ("bbe7b727a9c9ee9ada1b8ffd5bfedcdeb0853832d9d1277bbd53381932759788", [1138, 746]),
            "dimensions_top": ("f616b65191e3c598e6a8da966ef30770673baef9d60d60b63995b8ba9dadeaf2", [874, 634]),
            "dimensions_side": ("03154bf670cec4dd417e6c8f08f365df0071fc6fc01192d9a3489de1d0768afa", [874, 52]),
            "display_image": ("1e7050f7cdf8408769860581e370f837ce6ba450655f5f3a082c8fd22062a18c", [1092, 668]),
            "ports_1": ("202e8ea94e459b13c4bf3cdf254985d54f0671ba1dce7afc7858c2b0984a53b7", [818, 274]),
            "ports_2": ("7fd56f7e465e52ec27b51999be3a512952c7b3d99df54aa5ab024fc3d17149a7", [818, 182]),
            "ports_3": ("353e8ea0e34eb448dd472c9db42b7b83d642824f45adcea22b63f34bc1278d0f", [818, 274]),
            "ports_4": ("b578807d7bed1d3df6188fcfd6747609afa1c18ab0de951a98066709c9b866cc", [818, 182]),
            "product_bezel_space_black": ("1863c54dd9464f198ca5b83ff8c3d7b0168cebf8d7028d92b5e6d7d2298c6d57", [3860, 2540]),
        }
        for source_id, (sha256, dimensions) in expected.items():
            record = sources[source_id]
            self.assertEqual(record["source_class"], SourceClass.APPLE_CALIBRATED.value)
            self.assertTrue(record["source_url"].startswith("https://"))
            self.assertEqual(record["sha256"], sha256)
            self.assertEqual(record["pixel_dimensions"], dimensions)
            self.assertTrue(record["intended_use"])

    def test_may_reference_is_never_geometry_authority(self):
        payload = json.loads(REGISTER.read_text(encoding="utf-8"))
        reference = payload["visual_references"][0]
        self.assertEqual(reference["id"], "may_jestei_macbook")
        self.assertEqual(reference["role"], "VISUAL_ONLY")
        self.assertFalse(reference["geometry_authority"])
    def test_exact_chassis_datums_are_freezable_and_traceable(self):
        expected = {"width": 312.6, "depth": 221.2, "closed_height": 15.5}
        for key, value in expected.items():
            fact = CHASSIS_FACTS[key]
            validate_fact(fact)
            self.assertEqual(fact.value_mm, value)
            self.assertEqual(fact.source_class, SourceClass.APPLE_EXACT)
            self.assertEqual(fact.frame, "chassis_center")
            self.assertLessEqual(fact.tolerance_mm, 0.05)
            self.assertTrue(is_freezable(fact))

    def test_deck_calibration_records_provenance_and_uncertainty(self):
        self.assertEqual(DECK_CALIBRATION["source_class"], SourceClass.PROVISIONAL.value)
        self.assertEqual(DECK_CALIBRATION["source"], "keyboard_image")
        self.assertEqual(DECK_CALIBRATION["control_point_fit_residual_px"], 0.0)
        self.assertGreater(DECK_CALIBRATION["corner_pick_tolerance_px"], 0)
        self.assertGreater(DECK_CALIBRATION["tolerance_mm"], 0)
        self.assertFalse(DECK_CALIBRATION["frozen"])

    def test_preliminary_groups_carry_g1_provenance_metadata(self):
        payload = json.loads(REGISTER.read_text(encoding="utf-8"))
        source_ids = {entry["id"] for entry in payload["sources"]}
        required = {"source_class", "source", "method", "tolerance_mm", "frame", "confidence", "frozen"}
        for name, group in PRELIMINARY_CALIBRATION.items():
            with self.subTest(group=name):
                self.assertTrue(required.issubset(group))
                self.assertEqual(group["source_class"], SourceClass.PROVISIONAL.value)
                self.assertIn(group["source"], source_ids)
                self.assertGreater(group["tolerance_mm"], 0)
                self.assertTrue(group["frame"])
                self.assertTrue(group["confidence"])
                self.assertFalse(group["frozen"])

    def test_preliminary_keyboard_lattice_math_is_explicit_but_not_frozen(self):
        keyboard = derive_metric_measurements()["keyboard"]
        self.assertAlmostEqual(
            keyboard["pitch_x_mm"],
            keyboard["key_outer_width_mm"] + keyboard["gap_x_mm"],
            places=6,
        )
        self.assertAlmostEqual(
            keyboard["pitch_y_mm"],
            keyboard["key_outer_height_mm"] + keyboard["gap_y_mm"],
            places=6,
        )
        self.assertEqual(keyboard["source_class"], SourceClass.PROVISIONAL.value)
        self.assertFalse(keyboard["frozen"])

    def test_trackpad_center_is_chassis_relation_not_a_shifted_origin(self):
        trackpad = derive_metric_measurements()["trackpad"]
        measured_center = (trackpad["left_x_mm"] + trackpad["right_x_mm"]) / 2
        self.assertAlmostEqual(measured_center, trackpad["measured_center_x_mm"], places=6)
        self.assertEqual(trackpad["target_center_x_mm"], 0.0)
        self.assertLessEqual(abs(measured_center), trackpad["residual_tolerance_mm"])
        self.assertFalse(trackpad["frozen"])

    def test_speaker_periodicity_is_recorded_without_freezing_count(self):
        speaker = derive_metric_measurements()["speaker"]
        self.assertAlmostEqual(speaker["pitch_x_mm"], speaker["pitch_y_mm"], delta=0.15)
        self.assertAlmostEqual(speaker["pitch_x_mm"], 1.0, delta=0.15)
        self.assertIsNone(speaker["column_count"])
        self.assertIsNone(speaker["row_count"])
        self.assertFalse(speaker["frozen"])

    def test_trackpad_y_is_separate_from_front_chassis_edge(self):
        trackpad = derive_metric_measurements()["trackpad"]
        self.assertAlmostEqual(trackpad["physical_front_edge_px"], 884.8, places=6)
        self.assertAlmostEqual(trackpad["top_y_px"], 542.646847, delta=0.01)
        self.assertAlmostEqual(trackpad["bottom_y_px"], 873.904620, delta=0.01)
        self.assertAlmostEqual(trackpad["height_mm"], 82.814439, delta=0.01)
        self.assertAlmostEqual(trackpad["front_gap_mm"], 2.723846, delta=0.01)
        self.assertAlmostEqual(trackpad["center_y_mm"], -66.468935, delta=0.01)
        self.assertFalse(trackpad["frozen"])

    def test_touch_id_geometry_is_measured_as_distinct_control(self):
        touch = derive_metric_measurements()["touch_id"]
        self.assertAlmostEqual(touch["outer_width_mm"], 16.75, delta=0.25)
        self.assertAlmostEqual(touch["outer_height_mm"], 16.75, delta=0.25)
        self.assertAlmostEqual(touch["sensor_diameter_mm"], 9.0, delta=0.5)
        self.assertEqual(touch["default_appearance"], "black")
        self.assertFalse(touch["frozen"])

    def test_display_pixel_measurements_reproduce_metric_values(self):
        display = derive_metric_measurements()["display"]
        left, top, right, bottom = display["notch_relative_bbox_px"]
        self.assertAlmostEqual((right - left) / display["px_per_mm"], display["notch_top_width_mm"], places=6)
        self.assertAlmostEqual((bottom - top) / display["px_per_mm"], display["notch_height_mm"], places=6)
        camera_x, camera_y = display["camera_center_px"]
        opening_x, opening_y = display["opening_origin_px"]
        self.assertAlmostEqual(
            (camera_x - (opening_x + display["opening_px"][0] / 2)) / display["px_per_mm"],
            display["camera_center_x_mm"],
            places=6,
        )
        self.assertAlmostEqual(
            (camera_y - opening_y) / display["px_per_mm"],
            display["camera_from_top_mm"],
            places=6,
        )

    def test_product_bezel_uses_native_display_scale_and_records_outer_residual(self):
        display = derive_metric_measurements()["display"]
        self.assertEqual(display["opening_px"], [3024.0, 1964.0])
        self.assertAlmostEqual(display["px_per_mm"], 10.0, places=6)
        self.assertAlmostEqual(display["notch_top_width_mm"], 38.6, delta=0.1)
        self.assertAlmostEqual(display["notch_height_mm"], 6.4, delta=0.1)
        self.assertAlmostEqual(display["opening_corner_radius_mm"], 4.10, delta=0.10)
        self.assertAlmostEqual(display["notch_lower_radius_mm"], 2.19, delta=0.10)
        self.assertAlmostEqual(display["outer_lid_width_residual_mm"], 0.9, delta=0.15)
        self.assertFalse(display["outer_lid_frozen"])


if __name__ == "__main__":
    unittest.main()
