import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
sys.path.insert(0, str(EXT))


class AssetWorkflowContractTests(unittest.TestCase):
    def test_bulk_plan_is_exactly_the_five_reviewed_hdris(self):
        import asset_workflow

        records = asset_workflow.reviewed_hdri_records()
        self.assertEqual(len(records), 5)
        self.assertEqual(len({record['asset_id'] for record in records}), 5)
        self.assertTrue(all(record['active'] for record in records))
        self.assertTrue(all(record['distribution'] == 'remote-only' for record in records))
        self.assertTrue(all(record.get('media_type') == 'image/vnd.radiance' for record in records))
        self.assertTrue(all(record['filename'].endswith('.hdr') for record in records))

    def test_blender_online_access_and_awful_consent_are_distinct_permissions(self):
        import asset_workflow

        blender_off = asset_workflow.permission_state(
            blender_online=False, awful_consent=False)
        self.assertEqual(blender_off['code'], 'BLENDER_ONLINE_ACCESS_OFF')
        self.assertFalse(blender_off['ready'])
        self.assertIn('Blender Online Access', blender_off['message'])

        consent_missing = asset_workflow.permission_state(
            blender_online=True, awful_consent=False)
        self.assertEqual(consent_missing['code'], 'AWFUL_CONSENT_REQUIRED')
        self.assertFalse(consent_missing['ready'])
        self.assertIn('AWFUL', consent_missing['message'])

        ready = asset_workflow.permission_state(
            blender_online=True, awful_consent=True)
        self.assertEqual(ready['code'], 'READY')
        self.assertTrue(ready['ready'])

    def test_missing_hdri_falls_back_without_mutating_selected_intent(self):
        import asset_workflow

        missing = asset_workflow.environment_resolution(
            selected_preset='FISH_HOEK', asset_ready=False)
        self.assertEqual(missing['selected_intent'], 'FISH_HOEK')
        self.assertEqual(missing['effective_preset'], 'NISHITA_DAY')
        self.assertTrue(missing['fallback'])

        ready = asset_workflow.environment_resolution(
            selected_preset='FISH_HOEK', asset_ready=True)
        self.assertEqual(ready['selected_intent'], 'FISH_HOEK')
        self.assertEqual(ready['effective_preset'], 'FISH_HOEK')
        self.assertFalse(ready['fallback'])

        physical = asset_workflow.environment_resolution(
            selected_preset='NISHITA_SUNSET', asset_ready=False)
        self.assertEqual(physical['effective_preset'], 'NISHITA_SUNSET')
        self.assertFalse(physical['fallback'])

    def test_download_all_imports_legacy_cache_and_rebuilds_when_studio_exists(self):
        import asset_workflow

        source = (ROOT / 'extension' / 'awful_studio' / 'asset_workflow.py').read_text(encoding='utf-8')
        cache_source = (ROOT / 'extension' / 'awful_studio' / 'asset_cache.py').read_text(encoding='utf-8')
        self.assertIn('migrate_legacy_asset(record)', source)
        self.assertIn('legacy.build_studio(True)', source)
        self.assertIn('refresh_material_assets()', source)
        self.assertIn('legacy_root()', cache_source)

    def test_open_online_preferences_switches_section_after_window_open(self):
        source = (ROOT / 'extension' / 'awful_studio' / 'asset_workflow.py').read_text(encoding='utf-8')
        self.assertIn("_set_preferences_section('SYSTEM')", source)
        self.assertLess(source.index("userpref_show('INVOKE_DEFAULT')"), source.rindex("_set_preferences_section('SYSTEM')"))

    def test_unknown_environment_intent_is_rejected(self):
        import asset_workflow

        with self.assertRaises(ValueError):
            asset_workflow.environment_resolution(
                selected_preset='MAGENTA_MISSING_TEXTURE', asset_ready=False)


if __name__ == '__main__':
    unittest.main()
