import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.calibrate_macbook_m5_geometry import (
    build_report,
    deck_px_to_mm,
    deck_warp_spec,
    source_deck_px_to_mm,
    derive_metric_measurements,
    verify_sha256,
)


class MacBookCalibrationToolTests(unittest.TestCase):
    def test_deck_transform_uses_chassis_center_as_origin(self):
        x_mm, y_mm = source_deck_px_to_mm(567.5, 348.0)
        self.assertAlmostEqual(x_mm, 0.0, places=6)
        self.assertAlmostEqual(y_mm, 0.0, places=6)

        left, back = source_deck_px_to_mm(108.0, 23.0)
        self.assertAlmostEqual(left, -156.3, places=6)
        self.assertAlmostEqual(back, 110.6, places=6)

    def test_warp_spec_preserves_exact_physical_span(self):
        spec = deck_warp_spec()
        self.assertEqual(spec["output_size_px"], [920, 651])
        self.assertEqual(spec["physical_span_px"], [919.0, 650.0])
        self.assertEqual(spec["destination_quad"][2], [919.0, 650.0])

    def test_report_marks_g2_calibrated_groups_and_keeps_display_outer_provisional(self):
        report = build_report()
        self.assertEqual(report["gate"], "G2")
        self.assertEqual(
            report["status"],
            "calibrated_geometry_active_human_model_approval_pending",
        )
        self.assertEqual(report["measurements"]["keyboard"]["source_class"], "APPLE_CALIBRATED")
        self.assertTrue(report["measurements"]["trackpad"]["frozen"])
        self.assertFalse(report["measurements"]["display"]["outer_lid_frozen"])

    def test_pixel_measurements_reproduce_metric_contract(self):
        measurements = derive_metric_measurements()
        trackpad = measurements["trackpad"]
        self.assertAlmostEqual(trackpad["left_x_mm"], -64.7990206746, places=6)
        self.assertAlmostEqual(trackpad["right_x_mm"], 64.7990206746, places=6)
        self.assertAlmostEqual(trackpad["measured_center_x_mm"], 0.0, places=6)

        display = measurements["display"]
        self.assertAlmostEqual(display["notch_top_width_mm"], 38.6, places=6)
        self.assertAlmostEqual(display["notch_height_mm"], 6.4, places=6)
        self.assertAlmostEqual(display["camera_center_x_mm"], -0.1, places=6)
        self.assertAlmostEqual(display["camera_from_top_mm"], 1.65, places=6)

    def test_calibration_dependencies_are_pinned(self):
        requirements = (
            Path(__file__).resolve().parents[2]
            / "tools"
            / "requirements-calibration.txt"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(requirements, ["numpy==2.5.3", "opencv-python==5.0.0.93"])

    def test_hash_verifier_rejects_cache_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "asset.bin"
            path.write_bytes(b"apple-reference")
            expected = hashlib.sha256(b"apple-reference").hexdigest()
            self.assertEqual(verify_sha256(path, expected), expected)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_sha256(path, "0" * 64)

    def test_direct_cli_invocation_can_import_repo_modules(self):
        script = Path(__file__).resolve().parents[2] / "tools" / "calibrate_macbook_m5_geometry.py"
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=script.parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--cache-root", result.stdout)


if __name__ == "__main__":
    unittest.main()
