"""Regression contract for managed diagnostic material registry visibility."""
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
    'render_tests': False,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)

    try:
        check('Blender 5.2 runtime', bpy.app.version[:2] == (5, 2), bpy.app.version_string)
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        bpy.ops.wm.open_mainfile(filepath=str(args.work / 'studio.blend'), use_scripts=False)

        ext = importlib.import_module(MODULE)
        product_quality = importlib.import_module(MODULE + '.product_quality')
        legacy = ext.legacy
        ownership = ext.ownership
        scene = bpy.context.scene

        before = legacy.REG.material('MAT_DIAGNOSTIC')
        check('diagnostic material is registered before replacement', before is not None)

        with ownership.for_scene(scene):
            product_quality.replace_mockup(legacy, scene, 'BOTTLE')

        named = bpy.data.materials.get('MAT_AWFUL_Diagnostic')
        check('diagnostic material datablock still exists after replacement', named is not None)
        check('diagnostic material role is preserved',
              named is not None and named.get(legacy.ROLE_KEY) == 'MAT_DIAGNOSTIC',
              named.get(legacy.ROLE_KEY) if named else None)
        check('diagnostic material remains registry-visible after replacement',
              legacy.REG.material('MAT_DIAGNOSTIC') is not None,
              {
                  'named_users': int(named.users) if named else None,
                  'role': named.get(legacy.ROLE_KEY) if named else None,
              })

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'product_material_registry.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL product material registry runtime contract failed')


if __name__ == '__main__':
    main()
