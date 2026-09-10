"""Inject a mid-build failure and require Rebuild to preserve the pre-existing studio."""
import argparse
import importlib
from pathlib import Path
import sys

import addon_utils
import bpy

MODULE = 'bl_ext.awful_test.awful_studio'


def snapshot(scene, ext):
    owned = sorted(
        (obj.get('awful_role', ''), obj.name, obj.type,
         tuple(round(v, 6) for row in obj.matrix_world for v in row))
        for obj in scene.objects if ext.ownership.owned(obj, scene)
    )
    counts = {name: len(getattr(bpy.data, name)) for name in
              ('objects', 'collections', 'meshes', 'materials', 'cameras', 'lights', 'worlds', 'actions')}
    return {
        'owner': scene.awful_state.owner_id,
        'schema': scene.awful_state.schema_version,
        'built': scene.awful_state.built,
        'owned': owned,
        'counts': counts,
        'world': scene.world.name if scene.world else None,
        'camera': scene.camera.name if scene.camera else None,
    }


def cancelled(call):
    try:
        return call()
    except RuntimeError:
        return {'CANCELLED'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not addon_utils.check(MODULE)[1]:
        addon_utils.enable(MODULE, default_set=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.input), use_scripts=False)
    ext = importlib.import_module(MODULE)
    scene = bpy.context.scene
    ext.legacy.validate_built_scene(scene)
    before = snapshot(scene, ext)
    original = ext.legacy.build_cyclorama

    def injected_failure(*_args, **_kwargs):
        raise RuntimeError('injected rebuild failure after cleanup')

    ext.legacy.build_cyclorama = injected_failure
    try:
        result = cancelled(bpy.ops.awful.rebuild_studio)
    finally:
        ext.legacy.build_cyclorama = original
    if result != {'CANCELLED'}:
        raise RuntimeError(f'Expected cancelled rebuild, got {result}')
    after = snapshot(scene, ext)
    if after != before:
        raise RuntimeError('Failed rebuild changed or destroyed the previous studio')
    ext.legacy.validate_built_scene(scene)


if __name__ == '__main__':
    main()
