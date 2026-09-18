import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
sys.path.insert(0, str(EXT))


class CameraFramingContractTests(unittest.TestCase):
    def test_wide_tall_and_deep_products_fit_with_requested_margin(self):
        import camera_policy

        angle_x = math.radians(33.0)
        angle_y = math.radians(25.0)
        tan_x = math.tan(angle_x * 0.5)
        tan_y = math.tan(angle_y * 0.5)
        cases = (
            (4.0, 0.6, 1.0),
            (1.0, 0.8, 4.0),
            (1.2, 5.0, 1.5),
        )
        for width, depth, height in cases:
            zoff = height * 0.08
            distance = camera_policy.required_distance_for_bounds(
                width, depth, height, tan_x, tan_y, 1.25, zoff
            )
            self.assertTrue(camera_policy.bounds_fit(
                width, depth, height, distance, zoff,
                tan_x, tan_y, 1.25
            ), (width, depth, height, distance))

    def test_deeper_product_never_gets_closer_camera(self):
        import camera_policy

        tan_x = math.tan(math.radians(33.0) * 0.5)
        tan_y = math.tan(math.radians(25.0) * 0.5)
        shallow = camera_policy.required_distance_for_bounds(1.5, 0.5, 1.5, tan_x, tan_y, 1.2, 0.12)
        deep = camera_policy.required_distance_for_bounds(1.5, 4.0, 1.5, tan_x, tan_y, 1.2, 0.12)
        self.assertGreater(deep, shallow)

    def test_no_legacy_ten_meter_clamp_remains_in_policy(self):
        import camera_policy

        distance = camera_policy.required_distance_for_bounds(
            10.0, 10.0, 10.0, 0.2, 0.2, 1.4, 0.8
        )
        self.assertGreater(distance, 10.0)


if __name__ == '__main__':
    unittest.main()


class CameraStillViewContractTests(unittest.TestCase):
    def test_still_view_inventory_is_photographic(self):
        import camera_policy

        self.assertEqual(set(camera_policy.CAMERA_VIEW_PRESETS), {
            'HERO_85',
            'THREE_QUARTER_LEFT_85',
            'THREE_QUARTER_RIGHT_85',
            'SIDE_85',
            'WIDE_50',
            'DETAIL_120',
            'TOP_THREE_QUARTER_85',
        })
        self.assertEqual(
            camera_policy.camera_view_spec('WIDE_50')['lens'],
            50.0,
        )
        self.assertEqual(
            camera_policy.camera_view_spec('HERO_85')['lens'],
            85.0,
        )
        self.assertEqual(
            camera_policy.camera_view_spec('DETAIL_120')['lens'],
            120.0,
        )

    def test_still_view_specs_are_defensive_copies(self):
        import camera_policy

        first = camera_policy.camera_view_spec('HERO_85')
        first['lens'] = 1.0
        second = camera_policy.camera_view_spec('HERO_85')
        self.assertEqual(second['lens'], 85.0)

    def test_unknown_still_view_is_rejected(self):
        import camera_policy

        with self.assertRaises(ValueError):
            camera_policy.camera_view_spec('DRONE_FROM_SPACE')
