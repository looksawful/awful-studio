import argparse
import json
import os
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLTF_TRANSFORM_VERSION = '4.5.0'
CRITICAL_NODES = {
    'CTRL_MACBOOK_PRO_14', 'CTRL_HINGE', 'BASE_UNIBODY', 'LID_UNIBODY',
    'SCREEN_CONTENT', 'FACETIME_CAMERA', 'TRACKPAD',
    'TOUCH_ID', 'MAGSAFE', 'HDMI', 'SDXC', 'APPLE_LOGO_RELEASE',
    'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
    'SPEAKER_RUNTIME_PROXY_L', 'SPEAKER_RUNTIME_PROXY_R',
}


def read_glb_json(path: Path):
    data = path.read_bytes()
    if data[:4] != b'glTF':
        raise RuntimeError(f'Not a GLB: {path}')
    json_len, json_type = struct.unpack_from('<II', data, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError(f'First GLB chunk is not JSON: {path}')
    return json.loads(data[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\x00'))


def node_names(doc):
    return {node.get('name') for node in doc.get('nodes', []) if node.get('name')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime-dir', default='runtime/v1')
    parser.add_argument('--prefix', default='macbook_pro_14_m5_v1')
    args = parser.parse_args()

    runtime = (HERE / args.runtime_dir).resolve()
    if HERE.resolve() not in runtime.parents and runtime != HERE.resolve():
        raise RuntimeError('runtime dir must stay inside the MacBook asset directory')
    compat = runtime / f'{args.prefix}_web.glb'
    meshopt = runtime / f'{args.prefix}_web_meshopt.glb'
    manifest_path = runtime / f'{args.prefix}.asset.json'

    for path in (compat, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    npx = 'npx.cmd' if os.name == 'nt' else 'npx'
    subprocess.run([
        npx, '--yes', f'@gltf-transform/cli@{GLTF_TRANSFORM_VERSION}',
        'meshopt', str(compat), str(meshopt), '--level', 'high',
    ], check=True, cwd=HERE)

    meshopt_doc = read_glb_json(meshopt)
    missing = CRITICAL_NODES - node_names(meshopt_doc)
    if missing:
        raise RuntimeError(f'Meshopt output lost critical nodes: {sorted(missing)}')
    required = set(meshopt_doc.get('extensionsRequired', []))
    if 'EXT_meshopt_compression' not in required:
        raise RuntimeError(f'Meshopt extension is not required: {sorted(required)}')
    if compat.stat().st_size <= meshopt.stat().st_size:
        raise RuntimeError('Meshopt output is not smaller than compatibility GLB')

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['web_variants'] = {
        'compat': {'file': compat.name, 'requires': []},
        'meshopt': {
            'file': meshopt.name,
            'requires': ['MeshoptDecoder'],
            'extensions_required': sorted(required),
        },
    }
    manifest['default_web_variant'] = 'compat'
    manifest['preferred_web_variant'] = 'meshopt'
    manifest['web_optimizer'] = {
        'tool': '@gltf-transform/cli',
        'version': GLTF_TRANSFORM_VERSION,
        'command': 'meshopt --level high',
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + '\n',
        encoding='utf-8',
        newline='\n',
    )

    print(json.dumps({
        'compat_bytes': compat.stat().st_size,
        'meshopt_bytes': meshopt.stat().st_size,
        'ratio': round(meshopt.stat().st_size / compat.stat().st_size, 4),
        'critical_nodes': sorted(CRITICAL_NODES),
        'extensions_required': sorted(required),
    }, indent=2))


if __name__ == '__main__':
    main()
