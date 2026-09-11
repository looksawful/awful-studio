import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEGACY = ROOT / 'extension' / 'awful_studio' / 'core' / 'legacy.py'
VERIFY = ROOT / 'tools' / 'verify_extension.py'
RUNTIME = ROOT / 'tests' / 'runtime'


class RuntimePerformancePolicyTests(unittest.TestCase):
    def test_build_never_auto_probes_gpu_backends(self):
        source = LEGACY.read_text(encoding='utf-8')
        setup = source.split('def setup_render(scene):', 1)[1].split('\ndef ', 1)[0]
        self.assertNotIn('configure_cycles_gpu(scene)', setup)

    def test_full_verifier_batches_p0_contracts_into_one_blender_process(self):
        source = VERIFY.read_text(encoding='utf-8')
        self.assertIn("tests/runtime/p0_suite.py", source)
        for name in ('p0_lighting_contract.py', 'p0_camera_contract.py',
                     'p0_studio_geometry_contract.py', 'p0_natural_light_contract.py'):
            self.assertNotIn(name, source)

    def test_local_full_runtime_requires_explicit_opt_in(self):
        source = VERIFY.read_text(encoding='utf-8')
        self.assertIn('--allow-local-blender', source)
        self.assertIn("os.environ.get('CI')", source)

    def test_runtime_suite_contains_no_render_invocation(self):
        offenders = []
        for path in RUNTIME.glob('*.py'):
            source = path.read_text(encoding='utf-8')
            if 'bpy.ops.render.render' in source or 'bpy.ops.render.opengl' in source:
                offenders.append(path.name)
        self.assertEqual(offenders, [])

    def test_historical_fixture_disables_legacy_gpu_probe(self):
        source = (RUNTIME / 'extension_contract.py').read_text(encoding='utf-8')
        historical = source.split('def historical(args):', 1)[1].split('\ndef ', 1)[0]
        self.assertIn('mod.configure_cycles_gpu =', historical)


if __name__ == '__main__':
    unittest.main()
