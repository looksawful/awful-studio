"""Build with official Blender tooling and test that exact ZIP in isolated processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def _run(command, env, log, timeout=300):
    result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout)
    log.write_text(result.stdout, encoding='utf-8')
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(f'{log.stem} exited {result.returncode}')


def verify(blender, output):
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'extension/awful_studio'
    historical_source = ROOT / 'historical/0.0.15/awful_studio_v4_2_gpu_perf.py'
    subprocess.run([blender, '--background', '--factory-startup', '--command', 'extension',
                    'validate', str(source)], check=True)
    subprocess.run([blender, '--background', '--factory-startup', '--command', 'extension',
                    'build', '--source-dir', str(source), '--output-dir', str(output)], check=True)
    package = output / 'awful_studio-0.0.16.zip'
    if not package.is_file():
        raise FileNotFoundError('Official build did not create the expected package')
    with tempfile.TemporaryDirectory(prefix='awful-runtime-') as temporary:
        work = Path(temporary)
        env = dict(os.environ, BLENDER_USER_CONFIG=str(work/'config'),
                   BLENDER_USER_SCRIPTS=str(work/'scripts'), BLENDER_USER_DATAFILES=str(work/'datafiles'),
                   BLENDER_USER_EXTENSIONS=str(work/'extensions'))
        (work/'installed').mkdir()
        animated_historical = work / 'historical-animated.blend'
        try:
            _run([
                blender, '--background', '--factory-startup', '--disable-autoexec', '--offline-mode',
                '--python-exit-code', '1', '--python', str(ROOT/'tests/runtime/build_animated_historical.py'),
                '--', '--source', str(historical_source), '--output', str(animated_historical),
            ], env, output/'historical-animated.log')

            for phase in ('historical', 'install', 'reopen', 'migrate'):
                command = [blender, '--background', '--disable-autoexec', '--offline-mode']
                if phase in ('historical', 'install'):
                    command.append('--factory-startup')
                command += ['--python-exit-code', '1', '--python', str(ROOT/'tests/runtime/extension_contract.py'),
                            '--', '--phase', phase, '--work', str(work), '--zip', str(package),
                            '--source', str(historical_source)]
                result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=300)
                (output/f'{phase}.log').write_text(result.stdout, encoding='utf-8')
                print(result.stdout)
                if result.returncode:
                    raise RuntimeError(f'{phase} exited {result.returncode}')
                report = json.loads((work/f'{phase}.json').read_text())
                if report['status'] != 'passed':
                    raise RuntimeError(f'{phase} report did not pass')

            _run([
                blender, '--background', '--disable-autoexec', '--offline-mode', '--python-exit-code', '1',
                '--python', str(ROOT/'tests/runtime/migrate_animated_historical.py'),
                '--', '--input', str(animated_historical),
            ], env, output/'migrate-animated.log')
        finally:
            for report in work.glob('*.json'):
                (output/report.name).write_bytes(report.read_bytes())
    summary = {'status': 'passed', 'package': package.name,
               'sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
               'phases': ['historical-animated', 'historical', 'install', 'reopen', 'migrate', 'migrate-animated']}
    (output/'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return package


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    verify(args.blender, args.output.resolve())
