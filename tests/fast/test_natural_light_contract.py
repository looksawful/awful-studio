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

    def test_commercial_defaults_to_hybrid_world_fill_but_flash_and_cinema_do_not(self):
        import natural_light

        commercial = natural_light.lighting_regime('COMMERCIAL')
        natural = natural_light.lighting_regime('NATURAL')
        flash = natural_light.lighting_regime('FLASH')
        cinema = natural_light.lighting_regime('CINEMA')

        self.assertEqual(commercial['regime'], 'HYBRID')
        self.assertTrue(commercial['world_default'])
        self.assertGreaterEqual(commercial['world_factor'], 0.20)
        self.assertLessEqual(commercial['world_factor'], 0.30)

        self.assertTrue(natural['world_default'])
        self.assertEqual(natural['world_factor'], 1.0)

        for policy in (flash, cinema):
            self.assertFalse(policy['world_default'])
            self.assertEqual(policy['world_factor'], 0.0)

    def test_world_light_and_camera_background_strength_are_independent(self):
        import natural_light

        base = 0.8
        world = natural_light.effective_world_strength(
            base_strength=base,
            user_strength=1.5,
            family='COMMERCIAL',
        )
        camera = natural_light.camera_background_strength(
            base_strength=base,
            brightness=1.5,
        )
        self.assertAlmostEqual(world, base * 1.5 * 0.25)
        self.assertAlmostEqual(camera, base * 1.5)
        self.assertNotEqual(world, camera)

        # Background brightness must never feed back into illumination energy.
        darker_camera = natural_light.camera_background_strength(
            base_strength=base,
            brightness=0.25,
        )
        self.assertAlmostEqual(
            natural_light.effective_world_strength(
                base_strength=base,
                user_strength=1.5,
                family='COMMERCIAL',
            ),
            world,
        )
        self.assertLess(darker_camera, camera)

    def test_strength_controls_are_bounded_and_unknown_family_is_rejected(self):
        import natural_light

        self.assertEqual(
            natural_light.effective_world_strength(
                base_strength=1.0, user_strength=-10.0, family='COMMERCIAL'),
            0.0,
        )
        self.assertEqual(
            natural_light.camera_background_strength(base_strength=1.0, brightness=-1.0),
            0.0,
        )
        with self.assertRaises(ValueError):
            natural_light.lighting_regime('ALIEN_PRODUCT_PHOTOGRAPHY')


if __name__ == '__main__':
    unittest.main()
