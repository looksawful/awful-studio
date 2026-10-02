"""MacBook delivery must regenerate and validate the actual source geometry."""
import sys
from pathlib import Path
from unittest import TestCase, mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import build_macbook_v1_web as build


class MacBookBuildPipelineTests(TestCase):
    def test_current_generator_and_hinge_validation_precede_packaging(self):
        calls = []
        def run(*args):
            calls.append(tuple(map(str, args)))
            if len(calls) == 6:
                raise RuntimeError('stop before packaging')
        with mock.patch.object(sys, 'argv', ['build', '--blender', 'blender']), \
             mock.patch.object(build, 'source_fingerprint', return_value=('a' * 64, {})), \
             mock.patch.object(build.subprocess, 'check_output', return_value='commit') as check_output, \
             mock.patch.object(build, 'update_loader_revision'), \
             mock.patch.object(build, 'run', side_effect=run):
            with self.assertRaisesRegex(RuntimeError, 'stop before packaging'):
                build.main()
        check_output.assert_called_once_with(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True)
        self.assertIn(str(build.DEVICE / 'generate_low.py'), calls[0])
        self.assertIn(str(build.DEVICE / 'validate_hinge_clearance.py'), calls[1])
        self.assertIn(str(build.DEVICE / 'validate_deck_ports.py'), calls[2])
        self.assertIn(str(build.DEVICE / 'validate_construction.py'), calls[3])
        self.assertIn(str(build.DEVICE / 'validate_hybrid_deck.py'), calls[4])
        self.assertIn(str(ROOT / 'tools/package_device_asset.py'), calls[5])
        for call in calls:
            self.assertIn('--python-exit-code', call)
            self.assertIn('--factory-startup', call)

    def test_runtime_export_visibility_is_scoped_to_macbook_ownership(self):
        source = (ROOT / 'assets/device_mockups/macbook_pro_14/export_runtime_v1.py').read_text(encoding='utf-8')
        self.assertNotIn('for obj in bpy.data.objects:', source)
        self.assertIn('owned_objects = [root] + list(root.children_recursive)', source)
        self.assertIn('for obj in owned_objects:', source)

    def test_hinge_failure_stops_packaging(self):
        calls = []
        def run(*args):
            calls.append(tuple(map(str, args)))
            if len(calls) == 2:
                raise RuntimeError('hinge validation failed')
        with mock.patch.object(sys, 'argv', ['build', '--blender', 'blender']), \
             mock.patch.object(build, 'source_fingerprint', return_value=('a' * 64, {})), \
             mock.patch.object(build.subprocess, 'check_output', return_value='commit'), \
             mock.patch.object(build, 'update_loader_revision'), \
             mock.patch.object(build, 'run', side_effect=run):
            with self.assertRaisesRegex(RuntimeError, 'hinge validation failed'):
                build.main()
        self.assertFalse(any(str(ROOT / 'tools/package_device_asset.py') in call for call in calls))
