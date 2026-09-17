import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CI = ROOT / '.github' / 'workflows' / 'extension-ci.yml'
PAGES = ROOT / '.github' / 'workflows' / 'preview-pages.yml'


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
