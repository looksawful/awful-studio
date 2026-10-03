from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"


class MacBookG2ModelOverlayContractTests(unittest.TestCase):
    def test_overlay_pipeline_consumes_actual_blender_projection(self):
        exporter = (TOOLS / "export_macbook_g2_model_projection.py").read_text(encoding="utf-8")
        overlay = (TOOLS / "build_macbook_g2_surface_overlays.py").read_text(encoding="utf-8")
        self.assertIn("actual evaluated Blender geometry", exporter)
        self.assertIn("--projection-json", overlay)
        self.assertIn("actual evaluated Blender geometry", overlay)
        self.assertNotIn("KEYBOARD_LAYOUT_PX", overlay)
        self.assertNotIn("rectified_deck_px_to_source", overlay)
        self.assertNotIn("derive_metric_measurements", overlay)


if __name__ == "__main__":
    unittest.main()
