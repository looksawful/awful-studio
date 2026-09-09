"""Release-candidate metadata and static Blender Extension repository gates.

This module deliberately does not build or test Blender itself. It consumes the exact
candidate ZIP and runtime evidence produced by the canonical runtime tooling, then
refuses repository generation unless the release evidence is complete and licensing
has been explicitly approved for that run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'extension' / 'awful_studio' / 'blender_manifest.toml'
REQUIRED_PLATFORMS = ('linux-x64', 'windows-x64')


def read_manifest(path: Path = MANIFEST) -> dict:
    return tomllib.loads(path.read_text(encoding='utf-8'))


def package_name(manifest: dict) -> str:
    return f"{manifest['id']}-{manifest['version']}.zip"


def sha256_file(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def _blender_52(version: str) -> bool:
    parts = version.split('.')
    return len(parts) >= 2 and parts[0] == '5' and parts[1] == '2'


def evaluate_publish_gate(runtime_evidence: list[dict], *, expected_package: str,
                          expected_sha256: str, license_approved: bool) -> dict:
    reasons: list[str] = []
    by_platform = {entry.get('platform'): entry for entry in runtime_evidence}

    for platform in REQUIRED_PLATFORMS:
        entry = by_platform.get(platform)
        if entry is None:
            reasons.append(f'missing runtime evidence for {platform}')
            continue
        if entry.get('status') != 'passed':
            reasons.append(f'runtime evidence for {platform} is not passed')
        if entry.get('package') != expected_package:
            reasons.append(f'{platform} tested a different package')
        if entry.get('sha256') != expected_sha256:
            reasons.append(f'{platform} tested a different package SHA-256')
        if not _blender_52(str(entry.get('blender_version', ''))):
            reasons.append(f'{platform} did not report Blender 5.2.x')

    extras = sorted(set(by_platform) - set(REQUIRED_PLATFORMS) - {None})
    if extras:
        reasons.append('unexpected runtime platforms: ' + ', '.join(extras))
    if not license_approved:
        reasons.append('public release license approval is unresolved')

    return {
        'publishable': not reasons,
        'license_approved': bool(license_approved),
        'required_platforms': list(REQUIRED_PLATFORMS),
        'reasons': reasons,
    }


def candidate_metadata(*, package: Path, source_sha: str, manifest_version: str,
                       runtime_evidence: list[dict], license_approved: bool) -> dict:
    digest = sha256_file(package)
    gate = evaluate_publish_gate(
        runtime_evidence,
        expected_package=package.name,
        expected_sha256=digest,
        license_approved=license_approved,
    )
    evidence = sorted(runtime_evidence, key=lambda entry: str(entry.get('platform', '')))
    return {
        'schema_version': 1,
        'extension_id': 'awful_studio',
        'version': manifest_version,
        'source_commit': source_sha,
        'package': {
            'filename': package.name,
            'sha256': digest,
            'size_bytes': package.stat().st_size,
        },
        'runtime_evidence': evidence,
        'release_gate': gate,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def validate_repository_index(index: dict, *, extension_id: str, version: str,
                              package_name: str) -> dict:
    entries = [entry for entry in index.get('data', [])
               if entry.get('id') == extension_id and entry.get('version') == version]
    if len(entries) != 1:
        raise ValueError(f'Expected exactly one {extension_id} {version} repository entry')
    entry = entries[0]
    archive_url = str(entry.get('archive_url', ''))
    if Path(archive_url).name != package_name:
        raise ValueError('Repository index does not reference the exact candidate ZIP')
    return entry


def prepare_repository(*, blender: str, package: Path, metadata_path: Path,
                       output_dir: Path) -> Path:
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    if not metadata.get('release_gate', {}).get('publishable'):
        reasons = metadata.get('release_gate', {}).get('reasons', [])
        raise RuntimeError('Release gate is closed: ' + '; '.join(reasons))

    expected = metadata.get('package', {})
    if package.name != expected.get('filename') or sha256_file(package) != expected.get('sha256'):
        raise RuntimeError('Candidate ZIP does not match release metadata')

    manifest = read_manifest()
    if metadata.get('version') != manifest.get('version'):
        raise RuntimeError('Release metadata version does not match manifest')

    if output_dir.exists():
        if output_dir.is_symlink() or not output_dir.is_dir() or any(output_dir.iterdir()):
            raise FileExistsError(f'Repository output must be a new or empty directory: {output_dir}')
    else:
        output_dir.mkdir(parents=True)

    staged_package = output_dir / package.name
    shutil.copy2(package, staged_package)
    subprocess.run([
        blender, '--command', 'extension', 'server-generate',
        f'--repo-dir={output_dir}', '--html',
    ], check=True)

    index_path = output_dir / 'index.json'
    if not index_path.is_file():
        raise FileNotFoundError('Blender server-generate did not create index.json')
    index = json.loads(index_path.read_text(encoding='utf-8'))
    validate_repository_index(
        index,
        extension_id=manifest['id'],
        version=manifest['version'],
        package_name=package.name,
    )
    shutil.copy2(metadata_path, output_dir / 'release-metadata.json')
    return index_path


def _load_evidence(paths: list[Path]) -> list[dict]:
    return [json.loads(path.read_text(encoding='utf-8')) for path in paths]


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)

    metadata_parser = sub.add_parser('metadata')
    metadata_parser.add_argument('--package', type=Path, required=True)
    metadata_parser.add_argument('--source-sha', required=True)
    metadata_parser.add_argument('--evidence', type=Path, action='append', required=True)
    metadata_parser.add_argument('--output', type=Path, required=True)
    metadata_parser.add_argument('--license-approved', action='store_true')

    repo_parser = sub.add_parser('repository')
    repo_parser.add_argument('--blender', required=True)
    repo_parser.add_argument('--package', type=Path, required=True)
    repo_parser.add_argument('--metadata', type=Path, required=True)
    repo_parser.add_argument('--output-dir', type=Path, required=True)

    args = parser.parse_args()
    manifest = read_manifest()

    if args.command == 'metadata':
        expected = package_name(manifest)
        if args.package.name != expected:
            raise SystemExit(f'Expected package {expected}, got {args.package.name}')
        payload = candidate_metadata(
            package=args.package,
            source_sha=args.source_sha,
            manifest_version=manifest['version'],
            runtime_evidence=_load_evidence(args.evidence),
            license_approved=args.license_approved,
        )
        write_json(args.output, payload)
        if not payload['release_gate']['publishable']:
            print('Release gate CLOSED: ' + '; '.join(payload['release_gate']['reasons']))
            return 2
        print('Release gate OPEN')
        return 0

    prepare_repository(
        blender=args.blender,
        package=args.package,
        metadata_path=args.metadata,
        output_dir=args.output_dir,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
