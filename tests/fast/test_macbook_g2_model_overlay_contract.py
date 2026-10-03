from pathlib import Path
import unittest

import tools.build_macbook_g2_surface_overlays as overlays

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

    def test_side_mapper_uses_native_apple_reference_pixels(self):
        for side in (-1, 1):
            mapper = overlays.side_x_mapper(side)
            for spec in overlays.PORTS:
                if spec.side != side:
                    continue
                with self.subTest(side=side, port=spec.name):
                    self.assertAlmostEqual(
                        mapper(spec.y_mm),
                        spec.center_pixel,
                        delta=1.0,
                    )

    def test_vertical_mapper_uses_fixed_apple_height_scale(self):
        self.assertTrue(
            hasattr(overlays, "fixed_height_z_mapper"),
            "overlay must expose a fixed-height Z mapper instead of normalizing model zmin..zmax",
        )
        mapper = overlays.fixed_height_z_mapper(
            model_center_z_mm=7.096998,
            reference_top_px=7.0,
            reference_bottom_px=53.0,
            exact_height_mm=15.5,
        )
        self.assertAlmostEqual(mapper(7.096998 + 15.5 / 2), 7.0, delta=1e-6)
        self.assertAlmostEqual(mapper(7.096998 - 15.5 / 2), 53.0, delta=1e-6)
        # A too-tall model must project outside the Apple silhouette instead of
        # being silently normalized back into the reference bounds.
        self.assertLess(mapper(7.096998 + 8.0), 7.0)
        self.assertGreater(mapper(7.096998 - 8.0), 53.0)


if __name__ == "__main__":
    unittest.main()
