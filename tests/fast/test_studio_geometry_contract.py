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

    def test_window_frame_layout_is_inside_opening_and_non_overlapping(self):
        import studio_geometry

        window = {
            'width': 8.5, 'bottom_z': 0.55, 'top_z': 6.15,
            'frame_width': 0.12, 'frame_depth': 0.24,
        }
        layout = studio_geometry.window_frame_layout(window)
        ymin, ymax = -window['width'] * 0.5, window['width'] * 0.5
        bottom, top = window['bottom_z'], window['top_z']
        for item in layout['bars']:
            y, z = item['center_yz']
            width_y, height_z = item['size_yz']
            self.assertGreaterEqual(y - width_y * 0.5, ymin - 1e-9)
            self.assertLessEqual(y + width_y * 0.5, ymax + 1e-9)
            self.assertGreaterEqual(z - height_z * 0.5, bottom - 1e-9)
            self.assertLessEqual(z + height_z * 0.5, top + 1e-9)
        self.assertEqual(len(layout['bars']), 7)
        self.assertGreater(layout['glass_size_yz'][0], 0.0)
        self.assertGreater(layout['glass_size_yz'][1], 0.0)

    def test_floor_is_camera_physical_independently_of_reflective_room(self):
        import studio_geometry

        self.assertTrue(studio_geometry.architecture_camera_physical('FLOOR', reflective_room=False))
        self.assertTrue(studio_geometry.architecture_camera_physical('WINDOW_FRAME', reflective_room=False))
        self.assertTrue(studio_geometry.architecture_camera_physical('DOOR', reflective_room=False))
        self.assertFalse(studio_geometry.architecture_camera_physical('WALLS', reflective_room=False))
        self.assertTrue(studio_geometry.architecture_camera_physical('WALLS', reflective_room=True))

    def test_visible_floor_uses_dedicated_pbr_material(self):
        legacy_source = (ROOT / 'extension' / 'awful_studio' / 'core' / 'legacy.py').read_text(encoding='utf-8')
        geom_source = (ROOT / 'extension' / 'awful_studio' / 'studio_geometry.py').read_text(encoding='utf-8')
        self.assertIn('"floor": build_painted_material("MAT_Studio_Floor", "MAT_FLOOR"', legacy_source)
        self.assertIn('mats["floor"]', legacy_source)
        self.assertIn('_build_visible_floor(legacy, room_col, floor_mat)', geom_source)

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
