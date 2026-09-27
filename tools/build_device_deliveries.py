"""Rebuild and verify all canonical AWFUL STUDIO device deliveries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from device_delivery_contract import load_manifest, verify_glb_provenance, verify_glb_round_trip, verify_manifest

PLAN = (
    {
        'asset_id': 'iphone_17',
        'generator_version': 'web_delivery_camera_logo_normals_v30',
        'manifest': 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json',
    },
    {
        'asset_id': 'ipad_pro_11_m5',
        'generator_version': 'ipad_v6_packaged_blend_web_delivery',
        'manifest': 'assets/device_mockups/ipad_pro/runtime/v6/ipad_pro_11_m5_v6.asset.json',
    },
    {
        'asset_id': 'ipad_pro_13_m5',
        'generator_version': 'ipad_v6_packaged_blend_web_delivery',
        'manifest': 'assets/device_mockups/ipad_pro/runtime/v6/ipad_pro_13_m5_v6.asset.json',
    },
    {
        'asset_id': 'macbook_pro_14_m5',
        'generator_version': 'macbook_v1_packaged_blend_web_delivery',
        'manifest': 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1.asset.json',
    },
)


def run(*args) -> None:
    subprocess.run([str(value) for value in args], cwd=ROOT, check=True)


def verify_delivery(item: dict) -> dict:
    manifest_path = ROOT / item['manifest']
    manifest = load_manifest(manifest_path)
    errors = verify_manifest(ROOT, manifest)
    if manifest.get('generator_version') != item['generator_version']:
        errors.append('generator_version mismatch')
    runtime = manifest_path.parent
    for variant in ('compat', 'meshopt'):
        glb = runtime / manifest['web_variants'][variant]['file']
        errors.extend(verify_glb_provenance(glb, manifest))
        errors.extend(verify_glb_round_trip(glb, manifest))
    if errors:
        raise RuntimeError(f"{item['asset_id']} delivery verification failed: {errors}")
    return {
        'asset_id': item['asset_id'],
        'source_revision': manifest['source_revision'],
        'source_commit': manifest['source_commit'],
        'generator_version': manifest['generator_version'],
        'stage': manifest['stage'],
        'manifest': item['manifest'],
    }


def build_all(blender: Path) -> list[dict]:
    run(sys.executable, ROOT / 'tools/build_iphone17_v30.py', '--blender', blender)
    run(sys.executable, ROOT / 'tools/build_ipad_v6_web.py', '--blender', blender, '--size', 'all')
    run(sys.executable, ROOT / 'tools/build_macbook_v1_web.py', '--blender', blender)
    return [verify_delivery(item) for item in PLAN]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--blender', type=Path)
    args = parser.parse_args()
    if args.plan:
        print(json.dumps(PLAN, indent=2))
        return 0
    if args.blender is None:
        parser.error('--blender is required unless --plan is used')
    print(json.dumps(build_all(args.blender.resolve()), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
