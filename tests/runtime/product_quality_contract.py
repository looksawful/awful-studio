"""Blender 5.2 runtime contract for AWFUL Product Quality mockups."""
import argparse
import importlib
import json
from pathlib import Path
import platform
import sys
import traceback

import addon_utils
import bpy

MODULE = 'bl_ext.awful_test.awful_studio'
REPORT = {
    'status': 'failed',
    'checks': [],
    'blender': bpy.app.version_string,
    'platform': platform.platform(),
    'python': sys.version,
    'render_tests': False,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def dimensions(bbox):
    minimum, maximum = bbox
    return tuple(float(maximum[index] - minimum[index]) for index in range(3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)

    try:
        check('Blender 5.2 runtime', bpy.app.version[:2] == (5, 2), bpy.app.version_string)
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        check('extension enabled', addon_utils.check(MODULE)[1])
        bpy.ops.wm.open_mainfile(filepath=str(args.work / 'studio.blend'), use_scripts=False)

        ext = importlib.import_module(MODULE)
        legacy = ext.legacy
        ownership = ext.ownership
        product_quality = importlib.import_module(MODULE + '.product_quality')
        scene = bpy.context.scene
        scene.awful_studio.auto_fit = False

        check('product-quality Blender adapter exists',
              callable(getattr(product_quality, 'replace_mockup', None)))

        for key in product_quality.mockup_keys():
            spec = product_quality.mockup_spec(key)
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
            check(f'{key} root is scene-owned', ownership.owned(root, scene))
            check(f'{key} root role', root.get(legacy.ROLE_KEY) == 'MOCKUP_ROOT',
                  root.get(legacy.ROLE_KEY))
            check(f'{key} metadata key', product_quality.mockup_key(root) == key)
            stored = tuple(float(value) for value in root['awful_mockup_source_dimensions_m'])
            check(f'{key} source dimensions metadata', stored == tuple(spec['dimensions_m']), stored)

            hierarchy = [root] + legacy.descendants(root)
            meshes = [obj for obj in hierarchy if obj.type == 'MESH']
            check(f'{key} has bounded mesh parts',
                  1 <= len(meshes) <= int(spec['max_mesh_parts']), len(meshes))
            bbox = legacy.world_bbox(meshes)
            check(f'{key} has measurable geometry', bbox is not None)
            measured = dimensions(bbox)
            expected = tuple(float(value) for value in spec['dimensions_m'])
            relative_error = [abs(a - b) / max(b, 1e-9) for a, b in zip(measured, expected)]
            check(f'{key} geometry keeps source scale', max(relative_error) < 0.08,
                  {'measured': measured, 'expected': expected, 'relative_error': relative_error})

            primary = next((obj for obj in meshes if obj.get('awful_mockup_primary')), None)
            check(f'{key} has primary mesh', primary is not None)
            material_roles = [material.get(legacy.ROLE_KEY, '') for material in primary.data.materials]
            expected_roles = [f"MOCKUP_MAT_{spec['slot_materials'][slot]}"
                              for slot in spec['material_slots']]
            check(f'{key} material slots are deterministic', material_roles == expected_roles,
                  {'actual': material_roles, 'expected': expected_roles})

            bevels = [modifier for obj in meshes for modifier in obj.modifiers
                      if modifier.type == 'BEVEL']
            check(f'{key} bevel complexity bounded',
                  all(int(modifier.segments) <= int(spec['bevel_segments']) for modifier in bevels),
                  [int(modifier.segments) for modifier in bevels])

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'product_quality.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL product-quality runtime contract failed')


if __name__ == '__main__':
    main()
