"""Build with official Blender tooling and test that exact ZIP in isolated processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify(blender, output):
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'extension/awful_studio'
    subprocess.run([blender, '--background', '--factory-startup', '--command', 'extension',
                    'validate', str(source)], check=True)
    subprocess.run([blender, '--background', '--factory-startup', '--command', 'extension',
                    'build', '--source-dir', str(source), '--output-dir', str(output)], check=True)
    package = output / 'awful_studio-0.0.16.zip'
    if not package.is_file():
        raise FileNotFoundError('Official build did not create the expected package')
    with tempfile.TemporaryDirectory(prefix='awful-runtime-') as temporary:
        work = Path(temporary)
        user_resources = work / 'user-resources'
        user_resources.mkdir()
        # Blender 5.2 uses BLENDER_USER_RESOURCES as the supported override for
        # preferences, scripts, extensions and other per-user state. Keeping the
        # whole runtime profile under the temporary work directory prevents QA
        # from touching the developer's real Blender profile.
        env = dict(os.environ, BLENDER_USER_RESOURCES=str(user_resources))
        (work/'installed').mkdir()
        phases = ['historical', 'install', 'reopen', 'migrate']
        try:
            for phase in phases:
                command = [blender, '--background', '--disable-autoexec', '--offline-mode']
                if phase in ('historical', 'install'):
                    command.append('--factory-startup')
                command += ['--python-exit-code', '1', '--python', str(ROOT/'tests/runtime/extension_contract.py'),
                            '--', '--phase', phase, '--work', str(work), '--zip', str(package),
                            '--source', str(ROOT/'historical/0.0.15/awful_studio_v4_2_gpu_perf.py')]
                result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
                (output/f'{phase}.log').write_text(result.stdout, encoding='utf-8')
                print(result.stdout)
                if result.returncode:
                    raise RuntimeError(f'{phase} exited {result.returncode}')
                report = json.loads((work/f'{phase}.json').read_text())
                if report['status'] != 'passed':
                    raise RuntimeError(f'{phase} report did not pass')

            contracts = (
                ('lighting', ROOT/'tests/runtime/p0_lighting_contract.py'),
                ('camera', ROOT/'tests/runtime/p0_camera_contract.py'),
                ('studio_geometry', ROOT/'tests/runtime/p0_studio_geometry_contract.py'),
                ('natural_light', ROOT/'tests/runtime/p0_natural_light_contract.py'),
            )
            for name, script in contracts:
                command = [
                    blender, '--background', '--disable-autoexec', '--offline-mode',
                    '--python-exit-code', '1', '--python', str(script),
                    '--', '--work', str(work),
                ]
                result = subprocess.run(command, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
                (output/f'{name}.log').write_text(result.stdout, encoding='utf-8')
                print(result.stdout)
                if result.returncode:
                    raise RuntimeError(f'{name} exited {result.returncode}')
                report = json.loads((work/f'{name}.json').read_text())
                if report['status'] != 'passed':
                    raise RuntimeError(f'{name} report did not pass')
                phases.append(name)
        finally:
            for report in work.glob('*.json'):
                (output/report.name).write_bytes(report.read_bytes())
    summary = {'status': 'passed', 'package': package.name,
               'sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
               'phases': phases}
    (output/'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return package


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    verify(args.blender, args.output.resolve())
