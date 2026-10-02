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
    derive_metric_measurements,
    verify_sha256,
)


class MacBookCalibrationToolTests(unittest.TestCase):
    def test_deck_transform_uses_chassis_center_as_origin(self):
        x_mm, y_mm = deck_px_to_mm(625.2, 442.4)
        self.assertAlmostEqual(x_mm, 0.0, places=6)
        self.assertAlmostEqual(y_mm, 0.0, places=6)

        left, back = deck_px_to_mm(0.0, 0.0)
        self.assertAlmostEqual(left, -156.3, places=6)
        self.assertAlmostEqual(back, 110.6, places=6)

    def test_warp_spec_preserves_exact_physical_span(self):
        spec = deck_warp_spec()
        self.assertEqual(spec["output_size_px"], [1252, 886])
        self.assertEqual(spec["physical_span_px"], [1250.4, 884.8])
        self.assertEqual(spec["destination_quad"][2], [1250.4, 884.8])

    def test_report_keeps_unapproved_measurements_provisional(self):
        report = build_report()
        self.assertEqual(report["gate"], "G1")
        self.assertEqual(report["status"], "awaiting_human_overlay_approval")
        self.assertEqual(report["measurements"]["keyboard"]["source_class"], "PROVISIONAL")
        self.assertFalse(report["measurements"]["trackpad"]["frozen"])
        self.assertFalse(report["measurements"]["display"]["outer_lid_frozen"])

    def test_pixel_measurements_reproduce_metric_contract(self):
        measurements = derive_metric_measurements()
        trackpad = measurements["trackpad"]
        self.assertAlmostEqual(trackpad["left_x_mm"], -65.3888094731, places=6)
        self.assertAlmostEqual(trackpad["right_x_mm"], 66.5517725437, places=6)
        self.assertAlmostEqual(trackpad["measured_center_x_mm"], 0.5814815353, places=6)

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
