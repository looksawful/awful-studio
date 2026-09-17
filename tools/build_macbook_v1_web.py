"""Build canonical web-runtime delivery for MacBook Pro 14 M5 v1."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEVICE = ROOT / 'assets/device_mockups/macbook_pro_14'
RUNTIME = DEVICE / 'runtime/v1'
LOADER_PATH = ROOT / 'extension/awful_studio/device_asset_loader.py'
SOURCE_FILES = [
    'extension/awful_studio/assets/devices/macbook_pro_14_m5_low_v1_release.blend',
    'assets/device_mockups/macbook_pro_14/generate_low.py',
    'assets/device_mockups/macbook_pro_14/export_runtime_v1.py',
    'assets/device_mockups/macbook_pro_14/optimize_runtime_v1.py',
    'assets/device_mockups/macbook_pro_14/reference/apple_logo_alpha.png',
    'assets/device_mockups/macbook_pro_14/reference/macos26_official_screen.png',
]
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', type=Path, required=True)
    args = parser.parse_args()
    loader = load_loader()
    plugin_revision = loader.device_asset_spec('DEVICE_MACBOOK_PRO_14')['lods']['LOW']['source_revision']
    revision, source_hashes = source_fingerprint(ROOT, SOURCE_FILES)
    source_commit = subprocess.check_output(
        ['git', 'log', '-1', '--format=%H', '--', SOURCE_FILES[1]],
        cwd=ROOT, text=True,
    ).strip()
    source_blend = ROOT / SOURCE_FILES[0]
    run(
        args.blender.resolve(), source_blend, '--background',
        '--python', DEVICE / 'export_runtime_v1.py', '--',
        '--source-revision', revision,
        '--source-commit', source_commit,
        '--plugin-source-revision', plugin_revision,
    )
    run(sys.executable, DEVICE / 'optimize_runtime_v1.py')

    manifest_path = RUNTIME / 'macbook_pro_14_m5_v1.asset.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['source_files'] = source_hashes
    compat = RUNTIME / 'macbook_pro_14_m5_v1_web.glb'
    meshopt = RUNTIME / 'macbook_pro_14_m5_v1_web_meshopt.glb'
    delivery = RUNTIME / 'macbook_pro_14_m5_v1_delivery.blend'
    doc = read_glb_json(compat)
    names = {node.get('name') for node in doc.get('nodes', []) if node.get('name')}
    required = {
        'CTRL_MACBOOK_PRO_14', 'CTRL_HINGE', 'BASE_UNIBODY', 'LID_UNIBODY',
        'SCREEN_CONTENT', 'SCREEN_GLASS', 'FACETIME_CAMERA', 'TRACKPAD',
        'TOUCH_ID', 'MAGSAFE', 'HDMI', 'SDXC', 'APPLE_LOGO_RELEASE',
        'ANCHOR_CENTER', 'ANCHOR_BOTTOM_CENTER', 'ANCHOR_SCREEN_CENTER',
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f'MacBook GLB lost required nodes: {missing}')

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
    print(json.dumps({
        'source_revision': revision,
        'source_commit': source_commit,
        'plugin_source_revision': plugin_revision,
        'manifest': str(manifest_path),
        'compat_bytes': compat.stat().st_size,
        'meshopt_bytes': meshopt.stat().st_size,
    }, indent=2))


if __name__ == '__main__':
    main()
