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
