import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
POLICY = EXT / 'photography.py'
INIT = EXT / '__init__.py'


class P0LightingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = POLICY.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.init_source = INIT.read_text(encoding='utf-8')

    def test_photographic_regime_constants(self):
        self.assertIn('FLASH_SCENE_EXPOSURE = -3.0', self.source)
        self.assertIn('FLASH_APERTURE_FSTOP = 11.0', self.source)
        self.assertIn('FLASH_CCT = 6500.0', self.source)
        self.assertIn('CONTINUOUS_CCT = 4300.0', self.source)

    def test_neutral_ambient_flash_is_reachable(self):
        self.assertIn("'DIRECT_FLASH_AMBIENT'", self.source)
        self.assertIn("'FLASH', 'Neutral Ambient Flash'", self.source)
        self.assertIn('Expected 17 lighting presets', self.source)

    def test_flash_is_off_axis_camera_left(self):
        self.assertIn('FLASH_LOCAL_OFFSET = (-0.090, 0.075, 0.0)', self.source)

    def test_policy_is_installed_before_registration(self):
        self.assertIn('photography.install(legacy)', self.init_source)
        install_pos = self.init_source.index('photography.install(legacy)')
        register_pos = self.init_source.index('def register():')
        self.assertLess(install_pos, register_pos)

    def test_preset_wrapper_applies_photographic_regime(self):
        install = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'install')
        nested = next(n for n in ast.walk(install)
                      if isinstance(n, ast.FunctionDef) and n.name == 'apply_lighting_preset')
        calls = [ast.unparse(n.func) for n in ast.walk(nested) if isinstance(n, ast.Call)]
        self.assertIn('apply_photographic_regime', calls)


if __name__ == '__main__':
    unittest.main()
