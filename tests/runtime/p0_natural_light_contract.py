"""Blender 5.2 runtime contract for Natural Light / Hybrid World semantics."""
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
        policy = ext.natural_light
        scene = bpy.context.scene
        settings = scene.awful_studio
        world = scene.world
        check('managed world exists', world is not None and world.use_nodes)
        nodes = world.node_tree.nodes
        mix = nodes.get('AWFUL_CAMERA_BACKGROUND_MIX')
        path = nodes.get('AWFUL_LIGHT_PATH')
        check('environment mix exists', mix is not None)
        check('Is Camera Ray node exists', path is not None)
        check('Is Camera Ray drives world branch selection',
              bool(mix.inputs[0].links)
              and mix.inputs[0].links[0].from_node == path
              and mix.inputs[0].links[0].from_socket == path.outputs['Is Camera Ray'])

        check('independent World/background strength RNA exists',
              hasattr(settings, 'world_light_strength')
              and hasattr(settings, 'background_brightness'))

        # Every source has distinct illumination and camera-visible Background shaders.
        for preset_id in tuple(policy.HDRI_PRESETS) + tuple(policy.PHYSICAL_SKY_PRESETS):
            light_bg = nodes.get(f'AWFUL_BG_{preset_id}')
            camera_bg = nodes.get(f'AWFUL_CAMERA_BG_{preset_id}')
            check(f'{preset_id} has illumination Background', light_bg is not None)
            check(f'{preset_id} has camera Background', camera_bg is not None)
            check(f'{preset_id} uses distinct Background nodes',
                  light_bg is not None and camera_bg is not None and light_bg != camera_bg)

        # Commercial presets default to Hybrid, without an exposure hack.
        original_exposure = float(scene.view_settings.exposure)
        legacy.apply_lighting_preset(scene, 'COMMERCIAL_3LIGHT', False, True)
        check('Commercial preset defaults World ON for Hybrid',
              settings.natural_light_enabled, settings.natural_light_enabled)
        check('Commercial preset keeps Studio lights ON',
              settings.studio_lights_enabled, settings.studio_lights_enabled)
        check('Commercial Hybrid does not rewrite scene exposure',
              abs(float(scene.view_settings.exposure) - original_exposure) < 1e-9,
              {'before': original_exposure, 'after': float(scene.view_settings.exposure)})

        # Use Physical Sky for deterministic offline strength/link tests.
        settings.world_light_strength = 1.0
        settings.background_brightness = 1.0
        settings.natural_light_enabled = True
        settings.studio_lights_enabled = True
        settings.show_environment_background = True
        settings.world_preset = 'NISHITA_DAY'
        legacy.apply_environment_preset(scene, 'NISHITA_DAY', reset_defaults=True)
        bpy.context.view_layer.update()

        light_bg = nodes.get('AWFUL_BG_NISHITA_DAY')
        camera_bg = nodes.get('AWFUL_CAMERA_BG_NISHITA_DAY')
        check('Nishita illumination branch selected', linked_node(mix.inputs[1]) == light_bg,
              linked_node(mix.inputs[1]).name if linked_node(mix.inputs[1]) else None)
        check('Nishita camera branch selected independently', linked_node(mix.inputs[2]) == camera_bg,
              linked_node(mix.inputs[2]).name if linked_node(mix.inputs[2]) else None)
        base_strength = 0.75
        expected_world = policy.effective_world_strength(
            base_strength=base_strength,
            user_strength=1.0,
            family='COMMERCIAL',
            world_enabled=True,
            studio_enabled=True,
        )
        expected_camera = policy.camera_background_strength(
            base_strength=base_strength,
            brightness=1.0,
        )
        check('Hybrid World contribution is intentionally reduced',
              abs(float(light_bg.inputs['Strength'].default_value) - expected_world) < 1e-6,
              {'actual': float(light_bg.inputs['Strength'].default_value),
               'expected': expected_world})
        check('camera background keeps independent full brightness',
              abs(float(camera_bg.inputs['Strength'].default_value) - expected_camera) < 1e-6,
              {'actual': float(camera_bg.inputs['Strength'].default_value),
               'expected': expected_camera})

        # Camera-background changes must not feed back into illumination energy.
        illumination_before = float(light_bg.inputs['Strength'].default_value)
        settings.background_brightness = 0.25
        bpy.context.view_layer.update()
        check('background brightness leaves illumination strength unchanged',
              abs(float(light_bg.inputs['Strength'].default_value) - illumination_before) < 1e-9,
              {'before': illumination_before,
               'after': float(light_bg.inputs['Strength'].default_value)})
        check('background brightness changes camera branch only',
              abs(float(camera_bg.inputs['Strength'].default_value)
                  - policy.camera_background_strength(
                      base_strength=base_strength, brightness=0.25)) < 1e-6,
              float(camera_bg.inputs['Strength'].default_value))

        camera_strength_before_toggle = float(camera_bg.inputs['Strength'].default_value)
        settings.show_environment_background = False
        bpy.context.view_layer.update()
        check('BG OFF keeps illumination branch selected', linked_node(mix.inputs[1]) == light_bg)
        check('BG OFF switches camera ray only to black',
              linked_node(mix.inputs[2]) == nodes.get('AWFUL_BG_BLACK'))
        check('BG OFF does not mutate illumination strength',
              abs(float(light_bg.inputs['Strength'].default_value) - illumination_before) < 1e-9)
        settings.show_environment_background = True
        bpy.context.view_layer.update()
        check('BG ON restores independent camera branch', linked_node(mix.inputs[2]) == camera_bg)
        check('BG toggle preserves camera brightness value',
              abs(float(camera_bg.inputs['Strength'].default_value) - camera_strength_before_toggle) < 1e-9)

        camera_before_world_change = float(camera_bg.inputs['Strength'].default_value)
        settings.world_light_strength = 2.0
        bpy.context.view_layer.update()
        check('World Light Strength changes illumination branch',
              float(light_bg.inputs['Strength'].default_value) > illumination_before,
              {'before': illumination_before,
               'after': float(light_bg.inputs['Strength'].default_value)})
        check('World Light Strength leaves camera brightness unchanged',
              abs(float(camera_bg.inputs['Strength'].default_value) - camera_before_world_change) < 1e-9)

        # Flash/Cinema remain Studio-only by default; Natural keeps World on.
        legacy.apply_lighting_preset(scene, 'DIRECT_FLASH', False, True)
        check('Flash defaults World OFF', not settings.natural_light_enabled)
        legacy.apply_lighting_preset(scene, 'DUAL_COLOR_STRIP', False, True)
        check('Cinema defaults World OFF', not settings.natural_light_enabled)
        legacy.apply_lighting_preset(scene, 'WINDOW_BALANCED', False, True)
        check('Natural defaults World ON', settings.natural_light_enabled)

        # Preserve ready-HDRI semantics separately from the #43 missing-asset fallback.
        settings.natural_light_enabled = True
        settings.reflective_room_enabled = True
        settings.studio_lights_enabled = False
        original_read_valid = ext.asset_cache.read_valid
        ext.asset_cache.read_valid = lambda _path: True
        try:
            legacy.apply_environment_preset(scene, 'FISH_HOEK', reset_defaults=True)
        finally:
            ext.asset_cache.read_valid = original_read_valid
        bpy.context.view_layer.update()

        active = linked_node(mix.inputs[1])
        check('ready pure HDRI keeps HDRI source selected',
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
