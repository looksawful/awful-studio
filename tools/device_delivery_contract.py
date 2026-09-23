"""Deterministic device-delivery provenance and stale-artifact checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def source_fingerprint(root: Path, relative_paths: Iterable[str]) -> tuple[str, dict[str, str]]:
    hashes: dict[str, str] = {}
    for relative in sorted(relative_paths):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        hashes[relative] = sha256_file(path)
    canonical = json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest(), hashes


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'Device delivery manifest must be an object: {path}')
    return data


def delivery_matches(manifest: dict, asset_id: str, stage: str, source_revision: str) -> bool:
    return (
        manifest.get('asset_id') == asset_id
        and manifest.get('stage') == stage
        and manifest.get('source_revision') == source_revision
    )


def verify_manifest(root: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    source_files = manifest.get('source_files')
    if not isinstance(source_files, dict) or not source_files:
        return ['source_files missing or empty']
    for relative, expected in sorted(source_files.items()):
        path = root / relative
        if not path.is_file():
            errors.append(f'missing source file: {relative}')
        elif sha256_file(path) != expected:
            errors.append(f'source hash mismatch: {relative}')
    fingerprint, _ = source_fingerprint(root, source_files.keys())
    if manifest.get('source_revision') != fingerprint:
        errors.append('source_revision mismatch')
    artifacts = manifest.get('artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append('artifacts missing or empty')
        return errors
    for name, item in sorted(artifacts.items()):
        if not isinstance(item, dict) or 'path' not in item or 'sha256' not in item:
            errors.append(f'invalid artifact entry: {name}')
            continue
        path = root / item['path']
        if not path.is_file():
            errors.append(f'missing artifact: {item["path"]}')
        elif sha256_file(path) != item['sha256']:
            errors.append(f'artifact hash mismatch: {name}')
    return errors
