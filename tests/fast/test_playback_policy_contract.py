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


if __name__ == '__main__':
    unittest.main()
