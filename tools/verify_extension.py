"""Build and verify the exact Extension ZIP.

Full Blender runtime is intentionally CI/release-oriented. Local execution is
blocked by default because structural development must not consume the user's
GPU merely to prove non-rendering contracts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def _timing_summary(operations):
    grouped = {}
    for sample in operations:
        name = sample.get('operation')
        seconds = sample.get('wall_seconds')
        if name and isinstance(seconds, (int, float)):
            grouped.setdefault(name, []).append(float(seconds))
    return {
        name: {
            'count': len(values),
            'median_seconds': statistics.median(values),
            'max_seconds': max(values),
        }
        for name, values in sorted(grouped.items())
    }


def _run(command, env, log_path, timeout=300):
    result = subprocess.run(
        command, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout,
    )
    log_path.write_text(result.stdout, encoding='utf-8')
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(f'{log_path.stem} exited {result.returncode}')


def verify(blender, output):
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'extension/awful_studio'
    subprocess.run([
        blender, '--background', '--factory-startup', '--command', 'extension',
        'validate', str(source),
    ], check=True)
    subprocess.run([
        blender, '--background', '--factory-startup', '--command', 'extension',
        'build', '--source-dir', str(source), '--output-dir', str(output),
    ], check=True)

    package = output / 'awful_studio-0.0.16.zip'
    if not package.is_file():
        raise FileNotFoundError('Official build did not create the expected package')

    phases = []
    operations = []
    blender_processes = 2  # official validate + official build

    with tempfile.TemporaryDirectory(prefix='awful-runtime-') as temporary:
        work = Path(temporary)
        user_resources = work / 'user-resources'
        user_resources.mkdir()
        env = dict(os.environ, BLENDER_USER_RESOURCES=str(user_resources))
        (work / 'installed').mkdir()

        try:
            for phase in ('historical', 'install', 'reopen', 'migrate'):
                command = [blender, '--background', '--disable-autoexec', '--offline-mode']
                if phase in ('historical', 'install'):
                    command.append('--factory-startup')
                command += [
                    '--python-exit-code', '1',
                    '--python', str(ROOT / 'tests/runtime/extension_contract.py'),
                    '--', '--phase', phase, '--work', str(work),
                    '--zip', str(package),
                    '--source', str(ROOT / 'historical/0.0.15/awful_studio_v4_2_gpu_perf.py'),
                ]
                _run(command, env, output / f'{phase}.log')
                blender_processes += 1
                report = json.loads((work / f'{phase}.json').read_text(encoding='utf-8'))
                if report.get('status') != 'passed':
                    raise RuntimeError(f'{phase} report did not pass')
                operations.extend(report.get('operations', []))
                phases.append(phase)

            suite_command = [
                blender, '--background', '--disable-autoexec', '--offline-mode',
                '--python-exit-code', '1',
                '--python', str(ROOT / 'tests/runtime/p0_suite.py'),
                '--', '--work', str(work),
            ]
            _run(suite_command, env, output / 'p0_suite.log')
            blender_processes += 1
            suite = json.loads((work / 'p0_suite.json').read_text(encoding='utf-8'))
            if suite.get('status') != 'passed':
                raise RuntimeError('P0 structural suite did not pass')
            phases.extend(item['name'] for item in suite.get('contracts', []))
        finally:
            for report in work.glob('*.json'):
                (output / report.name).write_bytes(report.read_bytes())

    summary = {
        'status': 'passed',
        'package': package.name,
        'sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
        'phases': phases,
        'blender_processes': blender_processes,
        'render_tests': False,
        'gpu_autoconfig_during_build': False,
        'performance': _timing_summary(operations),
    }
    (output / 'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return package


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument(
        '--allow-local-blender', action='store_true',
        help='Explicitly allow the full Blender runtime outside CI.',
    )
    args = parser.parse_args()
    in_ci = os.environ.get('CI', '').lower() == 'true'
    if not in_ci and not args.allow_local_blender:
        parser.error(
            'Local full Blender runtime is disabled by default. '
            'Run fast tests locally and use CI for packaged runtime; '
            'pass --allow-local-blender only for an intentional release check.'
        )
    verify(args.blender, args.output.resolve())
