import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
sys.path.insert(0, str(EXT))


class PlaybackPolicyContractTests(unittest.TestCase):
    def test_once_loop_pingpong_map_to_bounded_action_behavior(self):
        import playback_policy

        once = playback_policy.mode_policy('ONCE')
        loop = playback_policy.mode_policy('LOOP')
        pingpong = playback_policy.mode_policy('PING_PONG')

        self.assertEqual(once['cycles_modifier'], None)
        self.assertEqual(loop['cycles_modifier'], 'REPEAT')
        self.assertEqual(pingpong['cycles_modifier'], 'MIRROR')
        self.assertFalse(once['repeats'])
        self.assertTrue(loop['repeats'])
        self.assertTrue(pingpong['repeats'])

    def test_timeline_controls_set_current_frame_for_visible_feedback(self):
        source = (EXT / 'playback_policy.py').read_text(encoding='utf-8')
        self.assertIn('scene.frame_set(start)', source)
        self.assertIn('scene.frame_set(int(scene.frame_start))', source)

    def test_unknown_playback_mode_is_rejected(self):
        import playback_policy

        with self.assertRaises(ValueError):
            playback_policy.mode_policy('FOREVER_BUT_WEIRD')

    def test_product_and_camera_settings_are_independent(self):
        import playback_policy

        fields = playback_policy.setting_fields()
        self.assertEqual(fields['PRODUCT'], 'product_playback')
        self.assertEqual(fields['CAMERA'], 'camera_playback')
        self.assertNotEqual(fields['PRODUCT'], fields['CAMERA'])

    def test_reapply_plan_never_accumulates_cycles_modifiers(self):
        import playback_policy

        for mode in ('ONCE', 'LOOP', 'PING_PONG'):
            plan = playback_policy.modifier_plan(mode)
            self.assertEqual(plan['remove_existing_cycles'], True)
            self.assertLessEqual(plan['cycles_modifiers_to_add'], 1)

    def test_preview_span_matches_one_or_two_complete_keyed_spans(self):
        import playback_policy

        keyed = (10.0, 50.0)
        self.assertEqual(playback_policy.preview_span(keyed, 'ONCE'), (10, 50))
        self.assertEqual(playback_policy.preview_span(keyed, 'LOOP'), (10, 90))
        self.assertEqual(playback_policy.preview_span(keyed, 'PING_PONG'), (10, 90))

    def test_combined_preview_range_is_union_of_independent_targets(self):
        import playback_policy

        product = playback_policy.preview_span((1.0, 241.0), 'ONCE')
        camera = playback_policy.preview_span((20.0, 80.0), 'PING_PONG')
        self.assertEqual(camera, (20, 140))
        self.assertEqual(playback_policy.union_preview_spans(product, camera), (1, 241))
        self.assertEqual(playback_policy.union_preview_spans(None, camera), camera)
        self.assertIsNone(playback_policy.union_preview_spans(None, None))

    def test_current_frame_is_preserved_inside_preview_and_clamped_outside(self):
        import playback_policy

        self.assertEqual(playback_policy.clamp_frame_to_span(25, (10, 90)), 25)
        self.assertEqual(playback_policy.clamp_frame_to_span(1, (10, 90)), 10)
        self.assertEqual(playback_policy.clamp_frame_to_span(120, (10, 90)), 90)


if __name__ == '__main__':
    unittest.main()
