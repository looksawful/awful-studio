"""Run all structural Blender contracts in one process.

Each contract reopens the saved studio fixture itself, so they stay isolated at
scene level while avoiding separate Blender startups. No render is invoked.
"""
import argparse
import json
from pathlib import Path
import runpy
import sys
import time

CONTRACTS = (
    ('lighting', 'p0_lighting_contract.py'),
    ('camera', 'p0_camera_contract.py'),
    ('studio_geometry', 'p0_studio_geometry_contract.py'),
    ('natural_light', 'p0_natural_light_contract.py'),
    ('playback', 'p0_playback_contract.py'),
    ('product_quality', 'product_quality_contract.py'),
)


def run_contract(path, work):
    previous = list(sys.argv)
    started = time.perf_counter()
    sys.argv = [str(path), '--', '--work', str(work)]
    try:
        runpy.run_path(str(path), run_name='__main__')
    finally:
        sys.argv = previous
    return time.perf_counter() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)

    root = Path(__file__).resolve().parent
    report = {'status': 'failed', 'contracts': [], 'render_tests': False}
    try:
        for name, filename in CONTRACTS:
            seconds = run_contract(root / filename, args.work)
            contract_report = json.loads((args.work / f'{name}.json').read_text(encoding='utf-8'))
            if contract_report.get('status') != 'passed':
                raise RuntimeError(f'{name} report did not pass')
            report['contracts'].append({'name': name, 'wall_seconds': seconds})
        report['status'] = 'passed'
    finally:
        (args.work / 'p0_suite.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

    if report['status'] != 'passed':
        raise RuntimeError('AWFUL structural runtime suite failed')


if __name__ == '__main__':
    main()
