"""A source fingerprint must describe the geometry actually packaged."""
import sys
from pathlib import Path
from unittest import TestCase, mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import build_ipad_v6_web as build


class IPadBuildPipelineTests(TestCase):
    def test_generation_and_control_validation_precede_packaging(self):
        calls = []

        def run(*args):
            calls.append(tuple(map(str, args)))
            if len(calls) == 4:
                raise RuntimeError('stop before writing package')

        with mock.patch.object(build, 'run', side_effect=run), mock.patch.object(build, 'update_loader_revision'):
            with self.assertRaisesRegex(RuntimeError, 'stop before writing package'):
                build.build_one(Path('blender'), '11', None)

        generation = next(call for call in calls if str(build.DEVICE / 'generate_low_v6.py') in call)
        controls = next(call for call in calls if str(ROOT / 'tests/runtime/ipad_control_geometry_contract.py') in call)
        optics = next(call for call in calls if str(build.DEVICE / 'validate_optics_ports.py') in call)
        packaging = next(call for call in calls if str(ROOT / 'tools/package_device_asset.py') in call)
        self.assertIn('--skip-previews', generation)
        self.assertIn(str(build.DEVICE / 'generated/ipad_pro_11_m5_low_v6.blend'), controls)
        self.assertLess(calls.index(generation), calls.index(packaging))
        self.assertLess(calls.index(controls), calls.index(packaging))
        self.assertLess(calls.index(optics), calls.index(packaging))

    def test_invalid_controls_stop_before_packaging(self):
        calls = []

        def run(*args):
            calls.append(tuple(map(str, args)))
            if len(calls) == 2:
                raise RuntimeError('control validation failed')

        with mock.patch.object(build, 'run', side_effect=run), mock.patch.object(build, 'update_loader_revision'):
            with self.assertRaisesRegex(RuntimeError, 'control validation failed'):
                build.build_one(Path('blender'), '13', None)
        self.assertFalse(any(str(ROOT / 'tools/package_device_asset.py') in c for c in calls))
