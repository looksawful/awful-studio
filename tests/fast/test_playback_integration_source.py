import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INIT = ROOT / 'extension' / 'awful_studio' / '__init__.py'
LEGACY = ROOT / 'extension' / 'awful_studio' / 'core' / 'legacy.py'


class PlaybackIntegrationSourceTests(unittest.TestCase):
    def test_playback_policy_installs_before_registration(self):
        source = INIT.read_text(encoding='utf-8')
        self.assertIn('playback_policy.install(legacy)', source)
        self.assertLess(source.index('playback_policy.install(legacy)'),
                        source.index('class AWFUL_AddonPreferences'))

    def test_playback_is_independent_scene_state_and_visible_in_ui(self):
        source = (ROOT / 'extension' / 'awful_studio' / 'playback_policy.py').read_text(encoding='utf-8')
        self.assertIn("annotations['product_playback']", source)
        self.assertIn("annotations['camera_playback']", source)
        self.assertIn("'product_playback', text='Playback'", source)
        self.assertIn("'camera_playback', text='Playback'", source)

    def test_legacy_does_not_implement_playback_by_mutating_motion_presets(self):
        source = LEGACY.read_text(encoding='utf-8')
        self.assertNotIn('product_playback:', source)
        self.assertNotIn('camera_playback:', source)


if __name__ == '__main__':
    unittest.main()
