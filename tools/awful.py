#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit('AWFUL tooling requires Python 3.11+') from exc

ROOT = Path(__file__).resolve().parents[1]


def load_runtime_lock(root: Path = ROOT) -> dict:
    with (root / 'runtime' / 'blender.lock').open('rb') as stream:
        return tomllib.load(stream)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b''):
            digest.update(chunk)
    return digest.hexdigest()


def expected_blender_path(root: Path = ROOT) -> Path:
    runtime = load_runtime_lock(root)
    executable = runtime.get('executable', 'blender')
    if os.name == 'nt' and not executable.lower().endswith('.exe'):
        executable += '.exe'
    return root / '.runtime' / runtime['extracted_dir'] / executable


def find_blender(root: Path = ROOT, blender_override: str | None = None) -> Path | None:
    override = blender_override or os.environ.get('AWFUL_BLENDER')
    if override:
        candidate = Path(override).expanduser().resolve()
        if candidate.is_file():
            return candidate
    candidate = expected_blender_path(root)
    if candidate.is_file():
        return candidate
    system = shutil.which('blender')
    return Path(system).resolve() if system else None


def _write_bootstrap_evidence(root: Path, runtime: dict, status: str, **extra) -> Path:
    evidence_dir = root / '.runtime'
    evidence_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        'status': status,
        'version': runtime.get('version'),
        'platform': runtime.get('platform'),
        'archive': runtime.get('archive'),
        'official_url': runtime.get('official_url'),
        'expected_sha256': runtime.get('sha256'),
        **extra,
    }
    path = evidence_dir / ('bootstrap.json' if status == 'passed' else 'bootstrap-failure.json')
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return path


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={'User-Agent': 'AWFUL-STUDIO-runtime/0.0.16'})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open('wb') as output:
        shutil.copyfileobj(response, output)


def bootstrap_blender(root: Path = ROOT, force: bool = False) -> Path:
    runtime = load_runtime_lock(root)
    if runtime.get('platform') != 'linux-x64':
        raise RuntimeError('Canonical bootstrap currently supports the pinned linux-x64 CI runtime; use --blender/AWFUL_BLENDER for another platform')
    installed = expected_blender_path(root)
    if installed.is_file() and not force:
        _write_bootstrap_evidence(root, runtime, 'passed', executable=str(installed), source='existing')
        return installed

    cache = root / '.cache' / 'blender'
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / runtime['archive']
    temporary: Path | None = None
    try:
        if force:
            archive.unlink(missing_ok=True)
            target = root / '.runtime' / runtime['extracted_dir']
            if target.exists():
                shutil.rmtree(target)
        if not archive.is_file():
            with tempfile.NamedTemporaryFile(dir=cache, delete=False) as tmp:
                temporary = Path(tmp.name)
            _download(runtime['official_url'], temporary)
            temporary.replace(archive)
            temporary = None

        actual_sha = sha256_file(archive)
        if actual_sha.lower() != runtime['sha256'].lower():
            raise RuntimeError(f"Blender archive checksum mismatch: expected {runtime['sha256']}, got {actual_sha}")

        runtime_root = root / '.runtime'
        runtime_root.mkdir(parents=True, exist_ok=True)
        target = runtime_root / runtime['extracted_dir']
        if not target.exists():
            with tarfile.open(archive, mode='r:xz') as package:
                package.extractall(runtime_root, filter='data')
        if not installed.is_file():
            raise RuntimeError(f'Blender executable missing after extraction: {installed}')
        _write_bootstrap_evidence(root, runtime, 'passed', executable=str(installed), actual_sha256=actual_sha, source='official_url')
        return installed
    except Exception as exc:
        _write_bootstrap_evidence(root, runtime, 'failed', error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def verify_extension(root: Path = ROOT, blender_override: str | None = None, output: Path | None = None) -> int:
    blender = find_blender(root, blender_override)
    if blender is None:
        print('Blender runtime not found. Run `python tools/awful.py bootstrap` or pass --blender.', file=sys.stderr)
        return 2
    harness = root / 'tools' / 'verify_extension.py'
    output = (output or root / 'dist').resolve()
    command = [sys.executable, str(harness), '--blender', str(blender), '--output', str(output)]
    print('Running:', ' '.join(command), flush=True)
    return subprocess.run(command, cwd=root, check=False).returncode


def print_status(root: Path = ROOT) -> int:
    runtime = load_runtime_lock(root)
    print('AWFUL STUDIO')
    print('Target release: 0.0.16')
    print(f"Blender runtime: {runtime['version']} ({runtime['platform']})")
    print(f"Archive SHA-256: {runtime['sha256']}")
    return 0


def print_doctor(root: Path = ROOT, blender_override: str | None = None) -> int:
    runtime = load_runtime_lock(root)
    checks = [
        ('runtime/blender.lock', (root / 'runtime' / 'blender.lock').is_file()),
        ('tools/verify_extension.py', (root / 'tools' / 'verify_extension.py').is_file()),
        ('pinned sha256', len(runtime.get('sha256', '')) == 64),
    ]
    blender = find_blender(root, blender_override)
    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    print(f"{'PASS' if blender else 'WARN'} Blender runtime: {blender or 'not present; bootstrap or pass --blender'}")
    return 1 if any(not passed for _, passed in checks) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='AWFUL STUDIO canonical development/runtime entrypoint')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    doctor = sub.add_parser('doctor')
    doctor.add_argument('--blender')
    bootstrap = sub.add_parser('bootstrap')
    bootstrap.add_argument('--force', action='store_true')
    verify = sub.add_parser('verify-extension')
    verify.add_argument('--blender')
    verify.add_argument('--output', type=Path, default=ROOT / 'dist')
    runtime = sub.add_parser('test-runtime')
    runtime.add_argument('--blender')
    runtime.add_argument('--output', type=Path, default=ROOT / 'dist')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == 'status':
        return print_status(ROOT)
    if args.command == 'doctor':
        return print_doctor(ROOT, args.blender)
    if args.command == 'bootstrap':
        try:
            blender = bootstrap_blender(ROOT, force=args.force)
        except (OSError, RuntimeError, tarfile.TarError, urllib.error.URLError) as exc:
            print(f'FAIL bootstrap: {exc}', file=sys.stderr)
            return 1
        print(f'PASS Blender runtime: {blender}')
        return 0
    if args.command in {'verify-extension', 'test-runtime'}:
        return verify_extension(ROOT, args.blender, args.output)
    raise AssertionError(args.command)


if __name__ == '__main__':
    raise SystemExit(main())
