import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
sys.path.insert(0, str(EXT))


class NaturalLightPolicyContractTests(unittest.TestCase):
    def test_hdri_presets_are_helper_free_pure_hdri(self):
        import natural_light

        for preset in ('FISH_HOEK', 'BLOUBERG', 'KLOPPENHEIM', 'BELFAST', 'ROGLAND'):
            policy = natural_light.mode_policy(preset)
            self.assertEqual(policy['source'], 'HDRI')
            self.assertTrue(policy['requires_asset'])
            self.assertFalse(policy['sun'])
            self.assertFalse(policy['portal'])
            self.assertFalse(policy['allow_fallback'])

    def test_physical_sky_presets_use_real_sun_and_sampling_portal(self):
        import natural_light

        for preset in ('NISHITA_DAY', 'NISHITA_SUNSET'):
            policy = natural_light.mode_policy(preset)
            self.assertEqual(policy['source'], 'PHYSICAL_SKY')
            self.assertFalse(policy['requires_asset'])
            self.assertTrue(policy['sun'])
            self.assertTrue(policy['portal'])
            self.assertFalse(policy['allow_fallback'])

    def test_unknown_environment_is_rejected(self):
        import natural_light

        with self.assertRaises(ValueError):
            natural_light.mode_policy('MAGIC_DAYLIGHT')

    def test_sun_settings_are_bounded_and_differ_between_day_and_sunset(self):
        import natural_light

        day = natural_light.sun_settings('NISHITA_DAY')
        sunset = natural_light.sun_settings('NISHITA_SUNSET')
        for settings in (day, sunset):
            self.assertGreater(settings['energy'], 0.0)
            self.assertLessEqual(settings['energy'], 10.0)
            self.assertGreaterEqual(settings['angle_deg'], 0.1)
            self.assertLessEqual(settings['angle_deg'], 10.0)
        self.assertNotEqual(day['elevation_deg'], sunset['elevation_deg'])
        self.assertNotEqual(day['rotation_deg'], sunset['rotation_deg'])


if __name__ == '__main__':
    unittest.main()
