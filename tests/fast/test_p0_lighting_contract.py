import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEGACY = ROOT / 'extension' / 'awful_studio' / 'core' / 'legacy.py'


class P0LightingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = LEGACY.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)

    def test_photographic_regime_constants(self):
        self.assertIn('FLASH_SCENE_EXPOSURE = -3.0', self.source)
        self.assertIn('FLASH_APERTURE_FSTOP = 11.0', self.source)
        self.assertIn('FLASH_CCT = 6500.0', self.source)
        self.assertIn('CONTINUOUS_CCT = 4300.0', self.source)

    def test_neutral_ambient_flash_is_reachable(self):
        self.assertIn('"DIRECT_FLASH_AMBIENT"', self.source)
        self.assertIn('"FLASH", "Neutral Ambient Flash"', self.source)
        self.assertIn('Expected 17 lighting presets', self.source)

    def test_flash_is_off_axis_camera_left(self):
        self.assertIn('local_offset=(-0.090, 0.075, 0.0)', self.source)

    def test_preset_application_applies_photographic_regime(self):
        function = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'apply_lighting_preset')
        calls = [ast.unparse(n.func) for n in ast.walk(function) if isinstance(n, ast.Call)]
        self.assertIn('apply_photographic_regime', calls)


if __name__ == '__main__':
    unittest.main()
