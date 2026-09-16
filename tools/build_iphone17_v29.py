"""Rebuild the canonical iPhone 17 v29 source, web delivery and plugin bundle."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import struct

ROOT = Path(__file__).resolve().parents[1]
DEVICE = ROOT / 'assets/device_mockups/iphone_17'
RUNTIME = DEVICE / 'runtime/v29'
SOURCE_FILES = [
    'assets/device_mockups/common/foundation_common.py',
    'assets/device_mockups/iphone_17/generate_low_v29.py',
    'assets/device_mockups/iphone_17/reference/apple_logo_glb_mask.png',
    'assets/device_mockups/iphone_17/reference/ios26_home_screen_1206x2622.png',
]
sys.path.insert(0, str(ROOT / 'tools'))
from device_delivery_contract import source_fingerprint, sha256_file

def run(*args):
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', type=Path, required=True)
    args = parser.parse_args()
    blender = args.blender.resolve()
    revision, source_hashes = source_fingerprint(ROOT, SOURCE_FILES)
    source_commit = subprocess.check_output(
        ['git', 'log', '-1', '--format=%H', '--', SOURCE_FILES[1]],
        cwd=ROOT, text=True).strip()
    generated = DEVICE / 'generated/iphone_17_low_v29.blend'
    evidence = DEVICE / 'evidence/low_v29_validation.json'
    previews = DEVICE / 'previews/low_v29'
    run(blender, '--background', '--python', DEVICE / 'generate_low_v29.py', '--',
        '--out', generated, '--evidence', evidence, '--previews', previews)
    run(blender, generated, '--background', '--python', DEVICE / 'export_runtime_v29.py', '--',
        '--source-revision', revision, '--source-commit', source_commit)
    run(sys.executable, DEVICE / 'optimize_runtime_v29.py')
    bundle = ROOT / 'extension/awful_studio/assets/devices/iphone_17_low_v29.blend'
    run(blender, generated, '--background', '--python', ROOT / 'tools/package_device_asset.py', '--',
        '--output', bundle, '--entry', 'AWFUL_DEVICE_IPHONE_17', '--root', 'CTRL_IPHONE_17',
        '--key', 'IPHONE_17', '--stage', 'LOW_DRAFT', '--variant', 'low_v29', '--revision', revision)
    manifest_path = RUNTIME / 'iphone_17_v29.asset.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['source_files'] = source_hashes
    glb_path = RUNTIME / 'iphone_17_v29_web.glb'
    raw = glb_path.read_bytes()
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError('invalid GLB JSON chunk')
    doc = json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\0'))
    names = {node.get('name') for node in doc.get('nodes', [])}
    required = {'CTRL_IPHONE_17','DYNAMIC_ISLAND','FRONT_SENSOR_PILL','FRONT_CAMERA_GLASS','APPLE_LOGO_DECAL','SCREEN_CONTENT'}
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f'GLB lost required nodes: {missing}')
    triangles = 0
    for mesh in doc.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            if primitive.get('mode', 4) != 4:
                continue
            accessor = primitive.get('indices')
            count = doc['accessors'][accessor]['count'] if accessor is not None else doc['accessors'][primitive['attributes']['POSITION']]['count']
            triangles += count // 3
    manifest['glb_qa'] = {'triangle_count': triangles, 'required_nodes': sorted(required),
        'node_count': len(doc.get('nodes', [])), 'material_count': len(doc.get('materials', [])),
        'runtime_bounds_mm': manifest['runtime_bounds_mm']}
    artifact_paths = {
        'generated_blend': generated, 'validation': evidence,
        'delivery_blend': RUNTIME / 'iphone_17_v29_delivery.blend',
        'compat_glb': RUNTIME / 'iphone_17_v29_web.glb',
        'meshopt_glb': RUNTIME / 'iphone_17_v29_web_meshopt.glb',
        'plugin_bundle': bundle,
    }
    manifest['artifacts'] = {name: {'path': str(path.relative_to(ROOT)).replace('\\','/'),
        'sha256': sha256_file(path)} for name, path in artifact_paths.items()}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source_revision': revision, 'source_commit': source_commit,
                      'manifest': str(manifest_path), 'bundle': str(bundle)}, indent=2))

if __name__ == '__main__':
    main()
