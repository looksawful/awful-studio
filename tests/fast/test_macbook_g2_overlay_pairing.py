import unittest

from tools.build_macbook_g2_surface_overlays import pair_points_by_metric_cost


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
        self.assertEqual(sorted(round(v, 6) for v in residuals),
                         sorted(round(v, 6) for v in reversed_residuals))

    def test_pairing_stays_red_for_real_geometry_shift(self):
        actual = [(97, 524), (789, 524), (197, 78), (789, 78)]
        targets = [(94, 79), (788, 77), (95, 523), (785, 524)]
        sx = 312.6 / 798.0
        sy = 221.2 / 562.0
        _, residuals = pair_points_by_metric_cost(actual, targets, sx, sy)
        self.assertGreater(max(residuals), 20.0)


if __name__ == "__main__":
    unittest.main()
