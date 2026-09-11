import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
sys.path.insert(0, str(EXT))

SPEC = {
    'width': 14.0,
    'depth': 18.0,
    'height': 7.0,
    'camera_y': -11.0,
    'background_y': 7.0,
    'cyc': {
        'width': 12.0,
        'front_y': -9.5,
        'curve_start_y': 3.0,
        'radius': 3.0,
        'height': 6.5,
        'thickness': 0.08,
    },
    'product_envelope': {
        'target_xy': 1.40,
        'target_height': 1.60,
        'max_xy': 2.60,
        'max_height': 3.20,
    },
}


class StudioGeometryContractTests(unittest.TestCase):
    def test_default_distance_is_inside_derived_room_bounds(self):
        import studio_geometry

        low, high = studio_geometry.cyclorama_distance_bounds(SPEC)
        self.assertLessEqual(low, SPEC['cyc']['curve_start_y'])
        self.assertGreaterEqual(high, SPEC['cyc']['curve_start_y'])
        self.assertAlmostEqual(low, 1.55, places=6)
        self.assertAlmostEqual(high, 3.75, places=6)

    def test_distance_clamps_to_derived_physical_bounds(self):
        import studio_geometry

        low, high = studio_geometry.cyclorama_distance_bounds(SPEC)
        self.assertEqual(studio_geometry.clamp_cyclorama_distance(-100.0, SPEC), low)
        self.assertEqual(studio_geometry.clamp_cyclorama_distance(100.0, SPEC), high)
        self.assertEqual(studio_geometry.clamp_cyclorama_distance(3.2, SPEC), 3.2)

    def test_profile_uses_metric_tangent_and_preserves_long_floor_run(self):
        import studio_geometry

        distance = 3.25
        profile = studio_geometry.cyclorama_profile(SPEC, distance, segments=8)
        self.assertEqual(profile[0], (SPEC['cyc']['front_y'], 0.0))
        self.assertEqual(profile[1], (distance, 0.0))
        self.assertGreater(distance - profile[0][0], 10.0)
        self.assertAlmostEqual(profile[-1][0], distance + SPEC['cyc']['radius'], places=6)
        self.assertAlmostEqual(profile[-1][1], SPEC['cyc']['height'], places=6)

    def test_look_and_finish_are_orthogonal_and_bounded(self):
        import studio_geometry

        white_matte = studio_geometry.cyclorama_style('WHITE', 'MATTE')
        white_glossy = studio_geometry.cyclorama_style('WHITE', 'GLOSSY')
        black_matte = studio_geometry.cyclorama_style('BLACK', 'MATTE')
        chroma_medium = studio_geometry.cyclorama_style('CHROMA_GREEN', 'MEDIUM')

        self.assertEqual(white_matte['base_color'], white_glossy['base_color'])
        self.assertNotEqual(white_matte['roughness'], white_glossy['roughness'])
        self.assertNotEqual(white_matte['base_color'], black_matte['base_color'])
        self.assertGreater(chroma_medium['base_color'][1], chroma_medium['base_color'][0])
        self.assertGreater(chroma_medium['base_color'][1], chroma_medium['base_color'][2])
        for style in (white_matte, white_glossy, black_matte, chroma_medium):
            self.assertGreaterEqual(style['roughness'], 0.0)
            self.assertLessEqual(style['roughness'], 1.0)

    def test_unknown_look_or_finish_is_rejected(self):
        import studio_geometry

        with self.assertRaises(ValueError):
            studio_geometry.cyclorama_style('PURPLE', 'MATTE')
        with self.assertRaises(ValueError):
            studio_geometry.cyclorama_style('WHITE', 'MIRROR')

    def test_architecture_groups_are_independent_from_hidden_bounce_floor(self):
        import studio_geometry

        groups = studio_geometry.ARCHITECTURE_ROLE_GROUPS
        self.assertIn('ROOM_CEILING', groups['CEILING'])
        self.assertIn('ARCH_FLOOR_VISIBLE', groups['FLOOR'])
        self.assertIn('DOOR_LEAF', groups['DOOR'])
        self.assertIn('WINDOW_FRAME', groups['WINDOW_FRAME'])
        self.assertIn('WINDOW_GLASS', groups['WINDOW_GLASS'])
        self.assertIn('CYC', groups['CYC'])
        self.assertNotIn('ROOM_FLOOR', groups['FLOOR'])
        self.assertNotIn('ROOM_CEILING', groups['WALLS'])


if __name__ == '__main__':
    unittest.main()
