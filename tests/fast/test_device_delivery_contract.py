from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    import device_delivery_contract as contract
except ImportError:
    contract = None

MANIFEST = ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json'
CANONICAL_MANIFESTS = (
    MANIFEST,
    ROOT / 'assets/device_mockups/ipad_pro/runtime/v6/ipad_pro_11_m5_v6.asset.json',
    ROOT / 'assets/device_mockups/ipad_pro/runtime/v6/ipad_pro_13_m5_v6.asset.json',
    ROOT / 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1.asset.json',
)
LOADER = ROOT / 'extension/awful_studio/device_asset_loader.py'


def load_loader():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', LOADER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceDeliveryContractTests(unittest.TestCase):
    def test_all_canonical_device_manifests_are_current_and_self_verifying(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        for manifest_path in CANONICAL_MANIFESTS:
            with self.subTest(manifest=manifest_path):
                self.assertTrue(manifest_path.is_file(), f'missing canonical manifest: {manifest_path}')
                manifest = contract.load_manifest(manifest_path)
                self.assertEqual(contract.verify_manifest(ROOT, manifest), [])

    def test_all_canonical_web_glbs_preserve_manifest_provenance(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        for manifest_path in CANONICAL_MANIFESTS:
            manifest = contract.load_manifest(manifest_path)
            runtime = manifest_path.parent
            for variant in ('compat', 'meshopt'):
                with self.subTest(manifest=manifest_path, variant=variant):
                    glb = runtime / manifest['web_variants'][variant]['file']
                    self.assertEqual(
                        contract.verify_glb_provenance(glb, manifest),
                        [],
                    )

    def test_all_canonical_web_glbs_match_round_trip_contract(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        for manifest_path in CANONICAL_MANIFESTS:
            manifest = contract.load_manifest(manifest_path)
            runtime = manifest_path.parent
            for variant in ('compat', 'meshopt'):
                with self.subTest(manifest=manifest_path, variant=variant):
                    glb = runtime / manifest['web_variants'][variant]['file']
                    self.assertEqual(
                        contract.verify_glb_round_trip(glb, manifest),
                        [],
                    )

    def test_round_trip_rejects_wrong_runtime_bounds(self):
        manifest = contract.load_manifest(MANIFEST)
        broken = deepcopy(manifest)
        broken['glb_qa']['runtime_bounds_mm'] = [0.0, 0.0, 0.0]
        glb = MANIFEST.parent / manifest['web_variants']['compat']['file']
        self.assertEqual(
            contract.verify_glb_round_trip(glb, broken),
            ['GLB runtime bounds mismatch'],
        )

    def test_v30_glb_qa_records_camera_backing_protrusion(self):
        validation = json.loads(
            (ROOT / 'assets/device_mockups/iphone_17/evidence/low_v30_validation.json').read_text(
                encoding='utf-8'
            )
        )
        manifest = contract.load_manifest(MANIFEST)
        self.assertEqual(
            manifest['glb_qa']['camera_backing_protrusion_mm'],
            validation['camera_backing_protrusion_mm'],
        )

    def test_round_trip_rejects_wrong_camera_backing_protrusion(self):
        manifest = contract.load_manifest(MANIFEST)
        broken = deepcopy(manifest)
        broken['glb_qa']['camera_backing_protrusion_mm'] = 99.0
        glb = MANIFEST.parent / manifest['web_variants']['compat']['file']
        self.assertEqual(
            contract.verify_glb_round_trip(glb, broken),
            ['GLB camera backing protrusion mismatch'],
        )

    def test_v30_manifest_is_current_and_self_verifying(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v30 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        self.assertEqual(manifest['asset_id'], 'iphone_17')
        self.assertEqual(manifest['version'], 'v30')
        self.assertEqual(manifest['stage'], 'LOW_DRAFT')
        self.assertEqual(manifest['delivery_profile']['simplification'], 'none')
        self.assertEqual(contract.verify_manifest(ROOT, manifest), [])
        self.assertEqual(set(manifest['screen_states']), {'screen_off', 'screen_on'})
        self.assertEqual(manifest['screen_states']['screen_off']['emission_strength'], 0.0)
        self.assertGreater(manifest['screen_states']['screen_on']['emission_strength'], 0.0)
        self.assertEqual(manifest['screen_glow']['anchor'], 'SCREEN_GLOW_ANCHOR')

    def test_v30_provenance_text_files_are_pinned_to_lf(self):
        paths = [
            'assets/device_mockups/iphone_17/generate_low_v30.py',
            'assets/device_mockups/iphone_17/evidence/low_v30_validation.json',
            'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json',
        ]
        for relative in paths:
            result = subprocess.check_output(
                ['git', 'check-attr', 'eol', '--', relative],
                cwd=ROOT, text=True,
            ).strip()
            self.assertTrue(result.endswith(': eol: lf'), result)

    def test_v30_tracked_delivery_text_is_lf_only(self):
        paths = [
            ROOT / 'assets/device_mockups/iphone_17/generate_low_v30.py',
            ROOT / 'assets/device_mockups/iphone_17/export_runtime_v30.py',
            ROOT / 'assets/device_mockups/iphone_17/evidence/low_v30_validation.json',
            ROOT / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json',
            ROOT / 'tools/build_iphone17_v30.py',
        ]
        for path in paths:
            self.assertNotIn(b'\r\n', path.read_bytes(), str(path))

    def test_plugin_loader_matches_delivery_revision_and_stage(self):
        self.assertTrue(MANIFEST.is_file(), f'missing canonical v30 manifest: {MANIFEST}')
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = contract.load_manifest(MANIFEST)
        loader = load_loader()
        item = loader.device_asset_spec('DEVICE_IPHONE_17')
        lod = item['lods'][item['default_lod']]
        self.assertEqual(item['stage'], manifest['stage'])
        self.assertEqual(lod['variant'], 'low_v30')
        self.assertEqual(lod['source_revision'], manifest['source_revision'])
        self.assertEqual(Path(lod['blend_path']).name, 'iphone_17_low_v30.blend')

    def test_manifest_without_artifacts_is_rejected(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'generator.py'
            source.write_text('print("device")\n', encoding='utf-8')
            revision, source_hashes = contract.source_fingerprint(root, ['generator.py'])
            manifest = {
                'source_files': source_hashes,
                'source_revision': revision,
            }
            self.assertEqual(
                contract.verify_manifest(root, manifest),
                ['artifacts missing or empty'],
            )

    def test_wrong_stage_or_revision_is_rejected(self):
        self.assertIsNotNone(contract, 'device delivery contract helper is missing')
        manifest = {
            'asset_id': 'iphone_17',
            'stage': 'LOW_DRAFT',
            'source_revision': 'abc',
        }
        self.assertFalse(contract.delivery_matches(manifest, 'iphone_17', 'DELIVERY', 'abc'))
        self.assertFalse(contract.delivery_matches(manifest, 'iphone_17', 'LOW_DRAFT', 'def'))
        self.assertTrue(contract.delivery_matches(manifest, 'iphone_17', 'LOW_DRAFT', 'abc'))


if __name__ == '__main__':
    unittest.main()
