"""Rebuild and verify all canonical AWFUL STUDIO device deliveries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
KHRONOS_EVIDENCE = ROOT / 'assets/device_mockups/device_delivery_khronos_validation.json'
sys.path.insert(0, str(ROOT / 'tools'))
from device_delivery_contract import load_manifest, sha256_file, verify_glb_provenance, verify_glb_round_trip, verify_manifest

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


def summarize_khronos_report(report: dict) -> dict:
    issues = report.get('issues')
    if not isinstance(issues, dict):
        raise RuntimeError('Khronos validation report is missing issues')
    summary = {
        'validator_version': report.get('validatorVersion'),
        'errors': int(issues.get('numErrors', 0)),
        'warnings': int(issues.get('numWarnings', 0)),
        'infos': int(issues.get('numInfos', 0)),
        'hints': int(issues.get('numHints', 0)),
    }
    summary['pass'] = summary['errors'] == 0 and summary['warnings'] == 0
    if not summary['pass']:
        raise RuntimeError(
            f"Khronos validation failed: {summary['errors']} errors, {summary['warnings']} warnings"
        )
    return summary


def run_khronos_validator(validator: Path, glb: Path) -> dict:
    process = subprocess.run(
        [
            str(validator),
            '--stdout',
            '--no-write-timestamp',
            '--no-absolute-path',
            str(glb),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if not process.stdout.strip():
        raise RuntimeError(f'Khronos validator produced no JSON report for {glb}')
    report = json.loads(process.stdout)
    summary = summarize_khronos_report(report)
    if process.returncode != 0:
        raise RuntimeError(f'Khronos validator failed for {glb} with exit code {process.returncode}')
    summary['file'] = str(glb.relative_to(ROOT)).replace('\\', '/')
    summary['sha256'] = sha256_file(glb)
    return summary


def validate_all_with_khronos(validator: Path) -> dict:
    assets: dict[str, dict[str, dict]] = {}
    versions: set[str] = set()
    for item in PLAN:
        manifest_path = ROOT / item['manifest']
        manifest = load_manifest(manifest_path)
        runtime = manifest_path.parent
        variants: dict[str, dict] = {}
        for variant in ('compat', 'meshopt'):
            glb = runtime / manifest['web_variants'][variant]['file']
            summary = run_khronos_validator(validator, glb)
            versions.add(summary['validator_version'])
            variants[variant] = summary
        assets[item['asset_id']] = variants
    evidence = {
        'schema_version': 1,
        'validator_versions': sorted(versions),
        'assets': assets,
        'pass': True,
    }
    KHRONOS_EVIDENCE.write_text(
        json.dumps(evidence, indent=2) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    return evidence


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


def build_all(blender: Path, validator: Path) -> list[dict]:
    run(sys.executable, ROOT / 'tools/build_iphone17_v30.py', '--blender', blender)
    run(sys.executable, ROOT / 'tools/build_ipad_v6_web.py', '--blender', blender, '--size', 'all')
    run(sys.executable, ROOT / 'tools/build_macbook_v1_web.py', '--blender', blender)
    deliveries = [verify_delivery(item) for item in PLAN]
    validate_all_with_khronos(validator)
    return deliveries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--validator', type=Path)
    args = parser.parse_args()
    if args.plan:
        print(json.dumps(PLAN, indent=2))
        return 0
    if args.blender is None or args.validator is None:
        parser.error('--blender and --validator are required unless --plan is used')
    print(json.dumps(build_all(args.blender.resolve(), args.validator.resolve()), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
