"""Build canonical web-runtime deliveries for iPad Pro 11/13 M5 v6."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEVICE = ROOT / 'assets/device_mockups/ipad_pro'
RUNTIME = DEVICE / 'runtime/v6'
LOADER_PATH = ROOT / 'extension/awful_studio/device_asset_loader.py'
CASES = {
    '11': ('ipad_pro_11_m5', 'DEVICE_IPAD_PRO_11', 'CTRL_IPAD_PRO_11'),
    '13': ('ipad_pro_13_m5', 'DEVICE_IPAD_PRO_13', 'CTRL_IPAD_PRO_13'),
}
sys.path.insert(0, str(ROOT / 'tools'))
from device_delivery_contract import source_fingerprint, sha256_file


def run(*args):
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)


def load_loader():
    spec = importlib.util.spec_from_file_location('awful_device_asset_loader', LOADER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_glb_json(path: Path):
    raw = path.read_bytes()
    if raw[:4] != b'glTF':
        raise RuntimeError(f'not a GLB: {path}')
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError(f'invalid GLB JSON chunk: {path}')
    return json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\0'))


def source_files_for(size: str, asset_id: str) -> list[str]:
    return [
        f'extension/awful_studio/assets/devices/{asset_id}_low_v6.blend',
        'assets/device_mockups/ipad_pro/generate_low_v6.py',
        'assets/device_mockups/ipad_pro/export_runtime_v6.py',
        'assets/device_mockups/ipad_pro/optimize_runtime_v6.py',
        f'assets/device_mockups/ipad_pro/reference/ipados26_official_screen_{size}.png',
        'assets/device_mockups/ipad_pro/reference/apple_logo_alpha.png',
    ]


def build_one(blender: Path, size: str, loader):
    asset_id, loader_key, root_name = CASES[size]
    source_files = source_files_for(size, asset_id)
    revision, source_hashes = source_fingerprint(ROOT, source_files)
    source_commit = subprocess.check_output(
        ['git', 'log', '-1', '--format=%H', '--', 'assets/device_mockups/ipad_pro/export_runtime_v6.py'],
        cwd=ROOT, text=True,
    ).strip()
    plugin_revision = loader.device_asset_spec(loader_key)['lods']['LOW']['source_revision']
    source_blend = ROOT / f'extension/awful_studio/assets/devices/{asset_id}_low_v6.blend'
    run(
        blender, source_blend, '--background', '--python', DEVICE / 'export_runtime_v6.py', '--',
        '--size', size,
        '--source-revision', revision,
        '--source-commit', source_commit,
        '--plugin-source-revision', plugin_revision,
    )
    run(sys.executable, DEVICE / 'optimize_runtime_v6.py', '--size', size)

    prefix = f'{asset_id}_v6'
    manifest_path = RUNTIME / f'{prefix}.asset.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['source_files'] = source_hashes

    compat = RUNTIME / f'{prefix}_web.glb'
    meshopt = RUNTIME / f'{prefix}_web_meshopt.glb'
    delivery = RUNTIME / f'{prefix}_delivery.blend'
    doc = read_glb_json(compat)
    names = {node.get('name') for node in doc.get('nodes', []) if node.get('name')}
    required = {
        root_name, 'SCREEN_CONTENT', 'SCREEN_GLASS', 'FRONT_CAMERA_GLASS',
        'APPLE_LOGO_DECAL', 'CAMERA_HOUSING', 'REAR_CAMERA_GLASS', 'LIDAR',
        'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
        'ANCHOR_REAR_CAMERA', 'SCREEN_GLOW_ANCHOR',
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f'{asset_id} GLB lost required nodes: {missing}')
    triangles = 0
    for mesh in doc.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            if primitive.get('mode', 4) != 4:
                continue
            accessor = primitive.get('indices')
            if accessor is not None:
                count = doc['accessors'][accessor]['count']
            else:
                count = doc['accessors'][primitive['attributes']['POSITION']]['count']
            triangles += count // 3

    manifest['glb_qa'] = {
        'triangle_count': triangles,
        'required_nodes': sorted(required),
        'node_count': len(doc.get('nodes', [])),
        'material_count': len(doc.get('materials', [])),
        'runtime_bounds_mm': manifest['runtime_bounds_mm'],
    }
    artifacts = {
        'delivery_blend': delivery,
        'compat_glb': compat,
        'meshopt_glb': meshopt,
    }
    manifest['artifacts'] = {
        name: {
            'path': str(path.relative_to(ROOT)).replace('\\', '/'),
            'sha256': sha256_file(path),
        }
        for name, path in artifacts.items()
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n'
    )
    return {
        'asset_id': asset_id,
        'source_revision': revision,
        'plugin_source_revision': plugin_revision,
        'manifest': str(manifest_path),
        'compat_bytes': compat.stat().st_size,
        'meshopt_bytes': meshopt.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--size', choices=['11', '13', 'all'], default='all')
    args = parser.parse_args()
    loader = load_loader()
    sizes = ('11', '13') if args.size == 'all' else (args.size,)
    results = [build_one(args.blender.resolve(), size, loader) for size in sizes]
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
