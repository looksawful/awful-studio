"""Verify Blender's native static Extension repository flow against one exact ZIP.

This is CI/release infrastructure. It does not render and it never touches the
real user profile because BLENDER_USER_RESOURCES is isolated in a temp folder.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def run(command, env, log):
    result = subprocess.run(
        command, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    log.append({'command': command[1:], 'returncode': result.returncode, 'output': result.stdout})
    if result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout


def verify(blender, package, output):
    package = Path(package).resolve()
    if not package.is_file():
        raise FileNotFoundError(package)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    evidence = {'status': 'failed', 'package': package.name, 'render_tests': False, 'steps': []}

    with tempfile.TemporaryDirectory(prefix='awful-repository-') as temporary:
        root = Path(temporary)
        repo = root / 'repository'
        profile = root / 'user-resources'
        repo.mkdir()
        profile.mkdir()
        shutil.copy2(package, repo / package.name)
        env = dict(os.environ, BLENDER_USER_RESOURCES=str(profile))

        try:
            run([
                blender, '--background', '--factory-startup', '--command', 'extension',
                'server-generate', '--repo-dir', str(repo),
            ], env, evidence['steps'])
            index = repo / 'index.json'
            if not index.is_file():
                raise RuntimeError('Blender server-generate did not create index.json')
            index_data = json.loads(index.read_text(encoding='utf-8'))
            if 'awful_studio' not in index.read_text(encoding='utf-8'):
                raise RuntimeError('Generated Extension repository does not list awful_studio')

            # Blender's own manual documents file:// repositories as the local
            # test path for a generated static repository.
            repository_url = index.resolve().as_uri()
            run([
                blender, '--background', '--factory-startup', '--command', 'extension',
                'repo-add', 'awful_ci', '--name', 'AWFUL CI', '--url', repository_url,
                '--clear-all',
            ], env, evidence['steps'])
            run([
                blender, '--background', '--command', 'extension', 'sync',
            ], env, evidence['steps'])
            listing = run([
                blender, '--background', '--command', 'extension', 'list',
            ], env, evidence['steps'])
            if 'awful_studio' not in listing:
                raise RuntimeError('Synced native repository does not expose awful_studio')
            installed = run([
                blender, '--background', '--command', 'extension',
                'install', '-s', '-e', 'awful_studio',
            ], env, evidence['steps'])
            if 'awful_studio' not in installed.lower():
                # Exact CLI wording can change; final state below remains authoritative.
                evidence['install_output_without_name'] = installed
            final_listing = run([
                blender, '--background', '--command', 'extension', 'list',
            ], env, evidence['steps'])
            if 'awful_studio' not in final_listing:
                raise RuntimeError('Native repository install did not leave awful_studio available')

            evidence.update({
                'status': 'passed',
                'repository_url_scheme': 'file',
                'index_generated': True,
                'package_listed': True,
                'native_install_command_passed': True,
                'index_top_level_type': type(index_data).__name__,
            })
        finally:
            (output / 'repository.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')

    if evidence['status'] != 'passed':
        raise RuntimeError('AWFUL static Extension repository verification failed')
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('dist'))
    args = parser.parse_args()
    verify(args.blender, args.package, args.output)
