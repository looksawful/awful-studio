"""Blender 5.2 runtime contract for P0 photographic lighting behavior."""
import argparse
import importlib
import json
from pathlib import Path
import platform
import sys
import traceback

import bpy
import addon_utils

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


def counts():
    return {name: len(getattr(bpy.data, name)) for name in
            ('objects', 'collections', 'materials', 'meshes', 'cameras', 'lights',
             'worlds', 'actions', 'node_groups', 'images')}


def lighting_state(legacy):
    result = {}
    for role in tuple(legacy.LIGHT_BANK_ROLES):
        light = legacy.REG.object(role)
        if light is None:
            result[role] = None
            continue
        data = light.data
        result[role] = {
            'active': bool(light.get('awful_preset_active', False)),
            'hide_render': bool(light.hide_render),
            'hide_viewport': bool(light.hide_viewport),
            'energy': round(float(getattr(data, 'energy', 0.0)), 6),
            'color': tuple(round(float(v), 6) for v in getattr(data, 'color', ())),
            'use_temperature': bool(getattr(data, 'use_temperature', False)),
            'temperature': round(float(getattr(data, 'temperature', 0.0)), 3),
        }
    for role in tuple(legacy.SHAPER_ROLES):
        shaper = legacy.REG.object(role)
        if shaper is not None:
            result[role] = {
                'active': bool(shaper.get('awful_preset_active', False)),
                'hide_render': bool(shaper.hide_render),
                'hide_viewport': bool(shaper.hide_viewport),
                'location': tuple(round(float(v), 6) for v in shaper.location),
                'dimensions': tuple(round(float(v), 6) for v in shaper.dimensions),
            }
    for index in range(1, 8):
        slat = legacy.REG.object(f'GOBO_SLAT_{index:02d}')
        if slat is not None:
            result[f'GOBO_SLAT_{index:02d}'] = {
                'hide_render': bool(slat.hide_render),
                'hide_viewport': bool(slat.hide_viewport),
                'location': tuple(round(float(v), 6) for v in slat.location),
            }
    return result


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
        photography = ext.photography
        scene = bpy.context.scene
        camera = legacy.REG.object('CAMERA')
        flash = legacy.REG.object('LIGHT_CameraFlash')

        check('camera exists', camera is not None)
        check('camera flash exists', flash is not None)
        check('camera flash parented to camera', flash.parent == camera)
        check('17 presets available', len(legacy.LIGHTING_PRESETS) == 17,
              len(legacy.LIGHTING_PRESETS))
        expected_flash = {
            'DIRECT_FLASH', 'DIRECT_FLASH_WIDE',
            'DIRECT_FLASH_AMBIENT', 'DIRECT_FLASH_COLOR',
        }
        check('complete flash family reachable',
              expected_flash.issubset(set(legacy.LIGHT_FAMILY_PRESETS['FLASH'])),
              list(legacy.LIGHT_FAMILY_PRESETS['FLASH']))

        # Preserve a deliberately non-default native baseline to prove exact restoration.
        scene.view_settings.exposure = 0.375
        aperture = camera.data.dof
        aperture.aperture_fstop = 4.0

        before = counts()
        legacy.apply_lighting_preset(scene, 'DIRECT_FLASH', False, False)
        check('flash exposure -3 EV',
              abs(scene.view_settings.exposure - photography.FLASH_SCENE_EXPOSURE) < 1e-6,
              scene.view_settings.exposure)
        check('flash aperture intent f11',
              abs(float(scene['awful_aperture_intent_fstop']) - 11.0) < 1e-6,
              float(scene['awful_aperture_intent_fstop']))
        check('camera aperture f11', abs(aperture.aperture_fstop - 11.0) < 1e-6,
              aperture.aperture_fstop)
        check('flash CCT 6500K',
              bool(getattr(flash.data, 'use_temperature', False)) and
              abs(float(flash.data.temperature) - 6500.0) < 1e-6,
              float(getattr(flash.data, 'temperature', 0.0)))
        check('flash camera-left off axis', flash.location.x < -0.05,
              tuple(round(v, 4) for v in flash.location))
        check('flash vertically centered', abs(flash.location.z) < 1e-6,
              tuple(round(v, 4) for v in flash.location))

        # Reapplying Flash must not overwrite the saved native continuous baseline.
        legacy.apply_lighting_preset(scene, 'DIRECT_FLASH_WIDE', False, False)
        legacy.apply_lighting_preset(scene, 'COMMERCIAL_3LIGHT', False, False)
        check('continuous exposure restored exactly',
              abs(scene.view_settings.exposure - 0.375) < 1e-6,
              scene.view_settings.exposure)
        check('continuous aperture restored exactly',
              abs(aperture.aperture_fstop - 4.0) < 1e-6,
              aperture.aperture_fstop)

        continuous = legacy.REG.object('LIGHT_Key')
        check('continuous CCT 4300K',
              continuous is not None and bool(getattr(continuous.data, 'use_temperature', False)) and
              abs(float(continuous.data.temperature) - 4300.0) < 1e-6,
              float(getattr(continuous.data, 'temperature', 0.0)) if continuous else None)

        # Apply every supported scheme, then representative repeats, with no datablock growth.
        inventory_counts = counts()
        for preset_id in tuple(legacy.LIGHTING_PRESETS):
            legacy.apply_lighting_preset(scene, preset_id, False, True)
            check(f'preset reachable: {preset_id}', scene.awful_studio.studio_light_preset == preset_id)
            check(f'preset bounded: {preset_id}', counts() == inventory_counts, counts())
        for preset_id in ('DIRECT_FLASH', 'DIRECT_FLASH_AMBIENT', 'COMMERCIAL_3LIGHT'):
            legacy.apply_lighting_preset(scene, preset_id, False, True)
            check(f'repeat bounded: {preset_id}', counts() == inventory_counts, counts())

        check('initial datablock inventory remained bounded', before == inventory_counts,
              {'before': before, 'inventory': inventory_counts})

        workflow = importlib.import_module(MODULE + '.lighting_workflow')
        workflow.apply_look(legacy, scene, 'ACCENT')
        accent_first = lighting_state(legacy)
        workflow.apply_look(legacy, scene, 'PRODUCT')
        product_state = lighting_state(legacy)
        workflow.apply_look(legacy, scene, 'ACCENT')
        accent_second = lighting_state(legacy)
        check(
            'Accent -> Product -> Accent returns identical lighting state',
            accent_first == accent_second,
            {'first': accent_first, 'second': accent_second},
        )
        check(
            'production look updates canonical preset',
            scene.awful_studio.studio_light_preset == 'DUAL_COLOR_STRIP',
            scene.awful_studio.studio_light_preset,
        )
        workflow.apply_look(legacy, scene, 'PRODUCT')
        for role in ('LIGHT_Accent_L', 'LIGHT_Accent_R', 'LIGHT_Strip_L', 'LIGHT_Strip_R'):
            state = lighting_state(legacy)[role]
            if role.startswith('LIGHT_Accent'):
                check(
                    f'Product resets {role}',
                    not state['active'] and state['hide_render'] and state['hide_viewport'],
                    state,
                )
        check(
            'production lighting shortcuts stay datablock-bounded',
            counts() == inventory_counts,
            {'expected': inventory_counts, 'actual': counts()},
        )
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'lighting.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL lighting runtime contract failed')


if __name__ == '__main__':
    main()
