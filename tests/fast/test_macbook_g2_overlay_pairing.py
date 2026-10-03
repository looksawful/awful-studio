import unittest

from assets.device_mockups.macbook_pro_14.port_layout import PORTS
import tools.build_macbook_g2_surface_overlays as overlays
from tools.build_macbook_g2_surface_overlays import D, H, pair_points_by_metric_cost, side_x_mapper


class MacBookG2OverlayPairingTests(unittest.TestCase):
    def test_foot_pairing_is_order_independent_and_metric_minimal(self):
        actual = [(97, 524), (789, 524), (97, 78), (789, 78)]
        targets = [(94, 79), (788, 77), (95, 523), (785, 524)]
        sx = 312.6 / (842.0 - 44.0)
        sy = 221.2 / (582.0 - 20.0)

        pairs, residuals = pair_points_by_metric_cost(actual, targets, sx, sy)
        self.assertEqual(len(pairs), 4)
        self.assertLess(max(residuals), 2.0)

        _, reversed_residuals = pair_points_by_metric_cost(
            list(reversed(actual)), list(reversed(targets)), sx, sy
        )
        self.assertEqual(
            sorted(round(v, 6) for v in residuals),
            sorted(round(v, 6) for v in reversed_residuals),
        )

    def test_pairing_stays_red_for_real_geometry_shift(self):
        actual = [(97, 524), (789, 524), (197, 78), (789, 78)]
        targets = [(94, 79), (788, 77), (95, 523), (785, 524)]
        sx = 312.6 / 798.0
        sy = 221.2 / 562.0
        _, residuals = pair_points_by_metric_cost(actual, targets, sx, sy)
        self.assertGreater(max(residuals), 20.0)

    def test_side_mapper_roundtrips_apple_reference_pixels(self):
        for side in (-1, 1):
            specs = [port for port in PORTS if port.side == side]
            mapper = side_x_mapper(side)

            for spec in specs:
                with self.subTest(side=side, port=spec.name):
                    self.assertAlmostEqual(mapper(spec.y_mm), spec.center_pixel, delta=0.51)

            self.assertAlmostEqual(
                mapper(D / 2),
                specs[0].rear_pixel,
                delta=0.51,
                msg=f"side {side} rear chassis datum must stay in Apple source-image pixels",
            )

    def test_side_marker_projection_uses_fixed_apple_height_scale(self):
        self.assertTrue(
            hasattr(overlays, "project_side_point"),
            "side overlay needs a testable 2D projection seam",
        )
        projected = overlays.project_side_point(
            lambda _y: 42.0,
            y_mm=10.0,
            z_mm=7.5,
            model_center_z_mm=5.0,
            reference_top_px=0.0,
            reference_bottom_px=100.0,
            exact_height_mm=10.0,
        )
        self.assertEqual(projected, (42, 25))

        spec = next(port for port in PORTS if port.name == "MAGSAFE")
        production_projection = overlays.project_side_point(
            side_x_mapper(-1),
            y_mm=spec.y_mm,
            z_mm=7.5,
            model_center_z_mm=5.0,
            reference_top_px=7.0,
            reference_bottom_px=53.0,
            exact_height_mm=H,
        )
        self.assertEqual(production_projection, (86, 23))


if __name__ == "__main__":
    unittest.main()
