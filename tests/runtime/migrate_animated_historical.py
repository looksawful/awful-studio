"""Migrate an animated 0.0.15 scene with the installed Extension and assert Action ownership."""
import argparse
import importlib
from pathlib import Path
import sys

import bpy
import addon_utils

MODULE = 'bl_ext.awful_test.awful_studio'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not addon_utils.check(MODULE)[1]:
        addon_utils.enable(MODULE, default_set=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.input), use_scripts=False)
    ext = importlib.import_module(MODULE)
    scene = bpy.context.scene
    if scene.awful_state.schema_version != 0:
        raise RuntimeError('Expected historical schema 0 before migration')
    result = bpy.ops.awful.migrate_scene()
    if result != {'FINISHED'}:
        raise RuntimeError(f'Historical migration failed: {result}')
    actions = [getattr(getattr(obj, 'animation_data', None), 'action', None)
               for obj in scene.objects if ext.ownership.owned(obj, scene)]
    actions = [action for action in actions if action]
    if not actions:
        raise RuntimeError('Migrated fixture lost its historical generated Action')
    if not all(ext.ownership.owned(action, scene) for action in actions):
        raise RuntimeError('Historical generated Action was not adopted by scene ownership')


if __name__ == '__main__':
    main()
