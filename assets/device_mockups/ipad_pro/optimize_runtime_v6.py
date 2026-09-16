import argparse
import json
import os
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / 'runtime' / 'v6'
GLTF_TRANSFORM_VERSION = '4.5.0'
SPECS = {
    '11': ('ipad_pro_11_m5', 'CTRL_IPAD_PRO_11'),
    '13': ('ipad_pro_13_m5', 'CTRL_IPAD_PRO_13'),
}
COMMON_CRITICAL = {
    'SCREEN_CONTENT', 'SCREEN_GLASS', 'FRONT_CAMERA_GLASS',
    'APPLE_LOGO_DECAL', 'CAMERA_HOUSING', 'REAR_CAMERA_GLASS', 'LIDAR',
    'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
    'ANCHOR_REAR_CAMERA',
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
    parser.add_argument('--size', choices=sorted(SPECS), required=True)
    args = parser.parse_args()
    asset_id, root_name = SPECS[args.size]
    prefix = f'{asset_id}_v6'
    compat = RUNTIME / f'{prefix}_web.glb'
    meshopt = RUNTIME / f'{prefix}_web_meshopt.glb'
    manifest_path = RUNTIME / f'{prefix}.asset.json'
    for path in (compat, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    npx = 'npx.cmd' if os.name == 'nt' else 'npx'
    subprocess.run([
        npx, '--yes', f'@gltf-transform/cli@{GLTF_TRANSFORM_VERSION}',
        'meshopt', str(compat), str(meshopt), '--level', 'high',
    ], check=True, cwd=HERE)

    meshopt_doc = read_glb_json(meshopt)
    critical = COMMON_CRITICAL | {root_name}
    missing = critical - node_names(meshopt_doc)
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
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')

    print(json.dumps({
        'asset_id': asset_id,
        'compat_bytes': compat.stat().st_size,
        'meshopt_bytes': meshopt.stat().st_size,
        'ratio': round(meshopt.stat().st_size / compat.stat().st_size, 4),
        'critical_nodes': sorted(critical),
        'extensions_required': sorted(required),
    }, indent=2))


if __name__ == '__main__':
    main()
