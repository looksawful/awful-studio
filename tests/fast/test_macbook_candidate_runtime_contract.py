from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "assets" / "device_mockups" / "macbook_pro_14" / "export_runtime_v1.py"
OPTIMIZE = ROOT / "assets" / "device_mockups" / "macbook_pro_14" / "optimize_runtime_v1.py"
BUILD = ROOT / "tools" / "build_macbook_v1_web.py"


class MacBookCandidateRuntimeContractTests(unittest.TestCase):
    def test_export_supports_isolated_candidate_runtime(self):
        source = EXPORT.read_text(encoding="utf-8")
        self.assertIn("--runtime-dir", source)
        self.assertIn("--prefix", source)
        self.assertIn("--version", source)
        self.assertIn("--source-blend-label", source)
        self.assertNotIn("'width_mm': 301.66", source)
        self.assertNotIn("'height_mm': 195.92", source)

    def test_optimizer_supports_candidate_runtime_arguments(self):
        source = OPTIMIZE.read_text(encoding="utf-8")
        self.assertIn("--runtime-dir", source)
        self.assertIn("--prefix", source)

    def test_geometry_contract_participates_in_delivery_fingerprint(self):
        source = BUILD.read_text(encoding="utf-8")
        self.assertIn(
            "'assets/device_mockups/macbook_pro_14/geometry_contract.py'",
            source,
        )


if __name__ == "__main__":
    unittest.main()
