"""Blender 5.2 runtime contract for P0 Natural Light v2 semantics."""
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
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def linked_node(input_socket):
    return input_socket.links[0].from_node if input_socket.links else None


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
        scene = bpy.context.scene
        settings = scene.awful_studio
        world = scene.world
        check('managed world exists', world is not None and world.use_nodes)
        nodes = world.node_tree.nodes
        mix = nodes.get('AWFUL_CAMERA_BACKGROUND_MIX')
        check('environment mix exists', mix is not None)

        settings.natural_light_enabled = True
        settings.reflective_room_enabled = True
        settings.studio_lights_enabled = False
        legacy.apply_environment_preset(scene, 'FISH_HOEK', reset_defaults=True)
        bpy.context.view_layer.update()

        active = linked_node(mix.inputs[1])
        check('pure HDRI keeps HDRI source selected',
              active is not None and active.name == 'AWFUL_BG_FISH_HOEK',
              active.name if active else None)
        portal = legacy.REG.object('WINDOW_PORTAL')
        check('portal exists', portal is not None)
        check('pure HDRI disables portal', portal.hide_render and portal.hide_viewport,
              {'hide_render': portal.hide_render, 'hide_viewport': portal.hide_viewport})
        sun = legacy.REG.object('NATURAL_SUN')
        check('managed natural Sun exists', sun is not None)
        check('pure HDRI disables managed Sun', sun.hide_render and sun.hide_viewport)

        for role in legacy.LIGHT_BANK_ROLES:
            light = legacy.REG.object(role)
            if light and light.get('awful_preset_active', False):
                check(f'artificial light disabled independently: {role}', light.hide_render)
        legacy.apply_environment_preset(scene, 'NISHITA_DAY', reset_defaults=True)
        bpy.context.view_layer.update()
        active = linked_node(mix.inputs[1])
        check('physical sky selects Nishita background',
              active is not None and active.name == 'AWFUL_BG_NISHITA_DAY',
              active.name if active else None)
        check('physical sky enables managed Sun',
              not sun.hide_render and not sun.hide_viewport,
              {'hide_render': sun.hide_render, 'hide_viewport': sun.hide_viewport})
        check('managed Sun is Blender SUN', sun.data.type == 'SUN', sun.data.type)
        check('managed Sun emits positive energy', sun.data.energy > 0.0, sun.data.energy)
        check('physical sky enables sampling portal',
              not portal.hide_render and not portal.hide_viewport,
              {'hide_render': portal.hide_render, 'hide_viewport': portal.hide_viewport})
        check('portal has zero emitted energy', abs(float(portal.data.energy)) < 1e-9,
              float(portal.data.energy))
        eager_volumes = [obj.name for obj in scene.objects
                         if ext.ownership.owned(obj, scene) and obj.type == 'VOLUME']
        check('no eager managed volumes', not eager_volumes, eager_volumes)
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'natural_light.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL natural light runtime contract failed')


if __name__ == '__main__':
    main()
