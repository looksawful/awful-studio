import importlib.util
import pathlib
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
VERIFY = ROOT / 'tools' / 'verify_extension.py'
RUNTIME = ROOT / 'tests' / 'runtime'


def load_performance_policy():
    path = EXT / 'runtime_performance.py'
    spec = importlib.util.spec_from_file_location('awful_runtime_performance_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimePerformancePolicyTests(unittest.TestCase):
    def test_build_preserves_native_device_without_gpu_probe(self):
        policy = load_performance_policy()

        class FakeLegacy:
            pass

        legacy = FakeLegacy()
        calls = {'probe': 0, 'setup': 0}

        def probe(_scene):
            calls['probe'] += 1
            return 'GPU', 'unexpected probe'

        def setup(scene):
            calls['setup'] += 1
            return legacy.configure_cycles_gpu(scene)

        legacy.configure_cycles_gpu = probe
        legacy.setup_render = setup
        original_probe = legacy.configure_cycles_gpu
        policy.install(legacy)
        result = legacy.setup_render(object())

        self.assertEqual(result[0], 'NATIVE')
        self.assertEqual(calls, {'probe': 0, 'setup': 1})
        self.assertIs(legacy.configure_cycles_gpu, original_probe)

    def test_preview_profiles_are_explicit_bounded_and_viewport_only(self):
        policy = load_performance_policy()
        fast = policy.preview_profile('FAST')
        quality = policy.preview_profile('QUALITY')

        self.assertLess(fast['samples'], quality['samples'])
        self.assertGreaterEqual(int(fast['pixel_size']), int(quality['pixel_size']))
        self.assertGreaterEqual(fast['adaptive_threshold'], quality['adaptive_threshold'])
        for profile in (fast, quality):
            self.assertGreaterEqual(profile['samples'], 1)
            self.assertLessEqual(profile['samples'], 64)
            self.assertIn(profile['pixel_size'], {'1', '2', '4', '8'})
            self.assertTrue(profile['denoise'])
            self.assertNotIn('device', profile)
            self.assertNotIn('render_samples', profile)
            self.assertNotIn('resolution', profile)
            self.assertNotIn('light_tree', profile)

        with self.assertRaises(ValueError):
            policy.preview_profile('MAGIC')

    def test_apply_preview_profile_preserves_final_render_and_device_settings(self):
        policy = load_performance_policy()
        scene = types.SimpleNamespace(
            cycles=types.SimpleNamespace(
                device='CPU',
                samples=256,
                preview_samples=16,
                preview_adaptive_threshold=0.05,
                use_preview_denoising=True,
                use_light_tree=True,
            ),
            render=types.SimpleNamespace(
                preview_pixel_size='2',
                resolution_x=1600,
                resolution_y=2000,
                resolution_percentage=100,
            ),
        )
        final_before = (
            scene.cycles.device,
            scene.cycles.samples,
            scene.cycles.use_light_tree,
            scene.render.resolution_x,
            scene.render.resolution_y,
            scene.render.resolution_percentage,
        )

        policy.apply_preview_profile(scene, 'FAST')
        fast = policy.preview_profile('FAST')
        self.assertEqual(scene.cycles.preview_samples, fast['samples'])
        self.assertEqual(scene.render.preview_pixel_size, fast['pixel_size'])
        self.assertEqual(scene.cycles.preview_adaptive_threshold, fast['adaptive_threshold'])
        self.assertEqual(scene.cycles.use_preview_denoising, fast['denoise'])

        policy.apply_preview_profile(scene, 'QUALITY')
        quality = policy.preview_profile('QUALITY')
        self.assertEqual(scene.cycles.preview_samples, quality['samples'])
        self.assertEqual(scene.render.preview_pixel_size, quality['pixel_size'])

        final_after = (
            scene.cycles.device,
            scene.cycles.samples,
            scene.cycles.use_light_tree,
            scene.render.resolution_x,
            scene.render.resolution_y,
            scene.render.resolution_percentage,
        )
        self.assertEqual(final_after, final_before)

    def test_performance_policy_installs_before_registration(self):
        source = (EXT / '__init__.py').read_text(encoding='utf-8')
        self.assertIn('runtime_performance.install(legacy)', source)
        self.assertLess(source.index('runtime_performance.install(legacy)'),
                        source.index('class AWFUL_AddonPreferences'))

    def test_performance_ui_exposes_preview_mode_and_cpu_diagnostics(self):
        source = (EXT / 'runtime_performance.py').read_text(encoding='utf-8')
        self.assertIn("annotations['preview_mode']", source)
        self.assertIn("('FAST', 'Fast Preview'", source)
        self.assertIn("('QUALITY', 'Quality Preview'", source)
        self.assertIn('collect_diagnostics', source)
        self.assertIn('Cycles device', source)
        self.assertIn('CPU', source)

    def test_full_verifier_batches_p0_contracts_into_one_blender_process(self):
        source = VERIFY.read_text(encoding='utf-8')
        self.assertIn("tests/runtime/p0_suite.py", source)
        for name in ('p0_lighting_contract.py', 'p0_camera_contract.py',
                     'p0_studio_geometry_contract.py', 'p0_natural_light_contract.py'):
            self.assertNotIn(name, source)

    def test_local_full_runtime_requires_explicit_opt_in(self):
        source = VERIFY.read_text(encoding='utf-8')
        self.assertIn('--allow-local-blender', source)
        self.assertIn('os.environ.get(', source)
        self.assertIn("'CI'", source)
        self.assertIn('if not in_ci and not args.allow_local_blender', source)

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
