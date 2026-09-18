import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CI = ROOT / '.github' / 'workflows' / 'extension-ci.yml'
PAGES = ROOT / '.github' / 'workflows' / 'preview-pages.yml'
REVIEW = ROOT / 'tools' / 'production_pass_review.py'


class PreviewDeliveryContractTests(unittest.TestCase):
    def test_extension_ci_runs_preview_and_merge_gate_requires_it(self):
        source = CI.read_text(encoding='utf-8')
        self.assertIn('  preview:', source)
        self.assertIn('working-directory: preview', source)
        self.assertIn('npm ci', source)
        self.assertIn('npm test', source)
        self.assertIn('npm run storybook:build', source)
        self.assertIn('npm run smoke', source)
        self.assertIn('npx playwright install --with-deps chromium', source)
        self.assertIn('needs: [fast, candidate, runtime-windows, preview]', source)

    def test_production_pass_review_tool_is_explicit_bounded_and_offline(self):
        self.assertTrue(REVIEW.is_file())
        source = REVIEW.read_text(encoding='utf-8')
        self.assertIn("'--render'", source)
        self.assertIn("'--width'", source)
        self.assertIn("'--height'", source)
        self.assertIn("'--samples'", source)
        self.assertIn('default=640', source)
        self.assertIn('default=800', source)
        self.assertIn('default=16', source)
        self.assertIn('awful_studio.run_build', source)
        self.assertIn('legacy.apply_camera_view', source)
        self.assertIn('lighting_workflow.apply_look', source)
        self.assertIn('bpy.ops.wm.save_as_mainfile', source)
        self.assertIn('if args.render:', source)
        self.assertIn('bpy.ops.render.render(write_still=True)', source)
        self.assertIn('manifest.json', source)
        self.assertNotIn('requests.', source)
        self.assertNotIn('urllib.', source)

    def test_review_tool_cleans_factory_scene_and_packs_managed_images(self):
        source = REVIEW.read_text(encoding='utf-8')
        self.assertIn('def _prepare_clean_review_scene()', source)
        self.assertIn('bpy.ops.object.select_all', source)
        self.assertIn("bpy.ops.object.delete", source)
        self.assertIn('def _pack_managed_images(awful_studio)', source)
        self.assertIn('image.pack()', source)
        self.assertIn('_prepare_clean_review_scene()', source)
        self.assertIn('_pack_managed_images(awful_studio)', source)
        self.assertIn('if not bpy.app.background:', source)
    def test_pages_workflow_deploys_storybook_from_main_only(self):
        self.assertTrue(PAGES.is_file())
        source = PAGES.read_text(encoding='utf-8')
        self.assertIn('branches: [main]', source)
        self.assertIn('actions/upload-pages-artifact@', source)
        self.assertIn('actions/deploy-pages@', source)
        self.assertIn('path: preview/storybook-static', source)
        self.assertIn('npm run storybook:build', source)


if __name__ == '__main__':
    unittest.main()
