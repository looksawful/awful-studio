#!/usr/bin/env python3
"""Small agent/human entrypoint over the canonical AWFUL tooling.

`status` and `doctor` never launch Blender or use the network. `bootstrap` is an
explicit network operation. `test-runtime` delegates to the canonical exact-ZIP
verifier and preserves its local Blender opt-in policy.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'runtime' / 'blender.lock'
MANIFEST = ROOT / 'extension' / 'awful_studio' / 'blender_manifest.toml'
HISTORICAL = ROOT / 'historical' / '0.0.15' / 'awful_studio_v4_2_gpu_perf.py'
HISTORICAL_SHA256 = '5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b'


def load_lock():
    return json.loads(LOCK.read_text(encoding='utf-8'))


def manifest_version():
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if line.startswith('version = '):
            return line.split('=', 1)[1].strip().strip('"')
    raise RuntimeError('Extension manifest version is missing')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def status():
    lock = load_lock()
    payload = {
        'project': 'AWFUL STUDIO',
        'extension_version': manifest_version(),
        'blender_target': lock['version'],
        'blender_build_hash': lock['build_hash'],
        'historical_sha256': sha256(HISTORICAL) if HISTORICAL.is_file() else None,
        'runtime_policy': 'cloud-first; local full Blender runtime is explicit opt-in only',
        'render_tests_required': False,
        'canonical_verifier': 'tools/verify_extension.py',
        'canonical_ci': '.github/workflows/extension-ci.yml',
    }
    print(json.dumps(payload, indent=2))
    return 0


def doctor():
    checks = []

    def add(name, ok, detail):
        checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

    try:
        lock = load_lock()
        add('runtime lock', lock.get('version') == '5.2.1', f"Blender {lock.get('version')}")
        distributions = lock.get('distributions', {})
        add('Windows distribution pin', len(distributions.get('windows-x64', {}).get('sha256', '')) == 64,
            distributions.get('windows-x64', {}).get('filename', 'missing'))
        add('Linux distribution pin', len(distributions.get('linux-x64', {}).get('sha256', '')) == 64,
            distributions.get('linux-x64', {}).get('filename', 'missing'))
    except Exception as exc:
        add('runtime lock', False, str(exc))

    add('manifest', MANIFEST.is_file() and manifest_version() == '0.0.17',
        str(MANIFEST.relative_to(ROOT)))
    historical_ok = HISTORICAL.is_file() and sha256(HISTORICAL) == HISTORICAL_SHA256
    add('historical baseline', historical_ok, HISTORICAL_SHA256)
    for relative in (
        'AGENTS.md', 'STATE.md', 'tools/setup_blender.py', 'tools/verify_extension.py',
        'tests/runtime/extension_contract.py', '.github/workflows/extension-ci.yml',
    ):
        path = ROOT / relative
        add(relative, path.is_file(), 'present' if path.is_file() else 'missing')

    failed = [item for item in checks if item['status'] == 'FAIL']
    print(json.dumps({'status': 'FAIL' if failed else 'PASS', 'checks': checks}, indent=2))
    return 1 if failed else 0


def bootstrap(destination):
    from setup_blender import install
    executable = install(destination.resolve())
    print(executable)
    return 0


def test_runtime(blender, output, allow_local_blender):
    command = [
        sys.executable, str(ROOT / 'tools' / 'verify_extension.py'),
        '--blender', str(blender), '--output', str(output),
    ]
    if allow_local_blender:
        command.append('--allow-local-blender')
    return subprocess.run(command, cwd=ROOT).returncode


def fast():
    return subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/fast', '-v'],
        cwd=ROOT,
    ).returncode


def main():
    parser = argparse.ArgumentParser(prog='awful')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status', help='Print pinned project/runtime state without Blender')
    sub.add_parser('doctor', help='Run pure filesystem/metadata checks without Blender')
    sub.add_parser('fast', help='Run the pure/static test suite')

    boot = sub.add_parser('bootstrap', help='Explicitly download/verify the pinned official Blender runtime')
    boot.add_argument('--destination', type=Path, default=ROOT / '.blender')

    runtime = sub.add_parser('test-runtime', help='Run the canonical exact-ZIP Blender verifier')
    runtime.add_argument('--blender', type=Path, required=True)
    runtime.add_argument('--output', type=Path, default=ROOT / 'dist')
    runtime.add_argument('--allow-local-blender', action='store_true')

    args = parser.parse_args()
    if args.command == 'status':
        return status()
    if args.command == 'doctor':
        return doctor()
    if args.command == 'fast':
        return fast()
    if args.command == 'bootstrap':
        return bootstrap(args.destination)
    if args.command == 'test-runtime':
        return test_runtime(args.blender, args.output, args.allow_local_blender)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
