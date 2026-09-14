import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'extension' / 'awful_studio' / 'screen_artwork.py'
PRODUCT_PATH = ROOT / 'extension' / 'awful_studio' / 'product_quality.py'
INIT_PATH = ROOT / 'extension' / 'awful_studio' / '__init__.py'


def load_module():
    spec = importlib.util.spec_from_file_location('awful_screen_artwork', MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load {MODULE_PATH}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScreenArtworkPolicyTests(unittest.TestCase):
    def test_screen_artwork_accepts_only_supported_image_formats(self):
        artwork = load_module()
        for path in ('mockup.png', 'mockup.JPG', 'mockup.jpeg', 'mockup.webp', 'mockup.tif', 'mockup.tiff', 'mockup.exr'):
            self.assertTrue(artwork.is_supported_artwork_path(path), path)
        for path in ('', 'mockup.blend', 'mockup.psd', 'mockup.txt'):
            self.assertFalse(artwork.is_supported_artwork_path(path), path)

    def test_screen_object_matching_covers_bundled_and_procedural_devices(self):
        artwork = load_module()
        for name in ('SCREEN_CONTENT', 'SCREEN_CONTENT.001', 'MOCKUP_Phone_Screen', 'MOCKUP_Tablet_Screen'):
            self.assertTrue(artwork.is_screen_object_name(name), name)
        for name in ('BODY', 'CTRL_HINGE', 'CAMERA_FRONT'):
            self.assertFalse(artwork.is_screen_object_name(name), name)

    def test_product_ui_exposes_explicit_screen_artwork_workflow(self):
        product = PRODUCT_PATH.read_text(encoding='utf-8')
        init = INIT_PATH.read_text(encoding='utf-8')
        self.assertIn("screen_artwork_path", product)
        self.assertIn("awful.apply_screen_artwork", product)
        self.assertIn("screen_artwork", init)
        self.assertIn("AWFUL_OT_ApplyScreenArtwork", init)


if __name__ == '__main__':
    unittest.main()
