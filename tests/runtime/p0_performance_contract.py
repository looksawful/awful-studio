"""Blender 5.2 runtime contract for AWFUL viewport preview performance policy."""
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


def final_state(scene):
    return {
        'device': str(scene.cycles.device),
        'samples': int(scene.cycles.samples),
        'light_tree': bool(scene.cycles.use_light_tree),
        'resolution_x': int(scene.render.resolution_x),
        'resolution_y': int(scene.render.resolution_y),
        'resolution_percentage': int(scene.render.resolution_percentage),
    }


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
        policy = importlib.import_module(MODULE + '.runtime_performance')
        legacy = ext.legacy
        scene = bpy.context.scene

        before = final_state(scene)
        check('preview mode property exists',
              getattr(scene.awful_studio, 'preview_mode', None) in {'FAST', 'QUALITY'},
              getattr(scene.awful_studio, 'preview_mode', None))

        fast = policy.apply_preview_profile(scene, 'FAST')
        check('Fast Preview samples applied',
              scene.cycles.preview_samples == fast['samples'], scene.cycles.preview_samples)
        check('Fast Preview pixel size applied',
              str(scene.render.preview_pixel_size) == fast['pixel_size'],
              str(scene.render.preview_pixel_size))
        check('Fast Preview adaptive threshold applied',
              abs(scene.cycles.preview_adaptive_threshold - fast['adaptive_threshold']) < 1e-6,
              scene.cycles.preview_adaptive_threshold)
        check('Fast Preview keeps denoise enabled',
              bool(scene.cycles.use_preview_denoising) is True)

        diagnostics = policy.collect_diagnostics(legacy, scene)
        required = {
            'engine', 'scene_device', 'compute_device_type', 'preview_samples',
            'preview_pixel_size', 'preview_denoise', 'light_tree', 'object_count',
            'light_count', 'image_count', 'approx_image_bytes', 'cpu_warning',
        }
        check('diagnostics expose required bounded fields',
              required.issubset(diagnostics), sorted(diagnostics))
        check('diagnostics see managed studio objects', diagnostics['object_count'] > 0,
              diagnostics)
        check('diagnostics see managed lights', diagnostics['light_count'] > 0,
              diagnostics)

        quality = policy.apply_preview_profile(scene, 'QUALITY')
        check('Quality Preview samples applied',
              scene.cycles.preview_samples == quality['samples'], scene.cycles.preview_samples)
        check('Quality Preview pixel size applied',
              str(scene.render.preview_pixel_size) == quality['pixel_size'],
              str(scene.render.preview_pixel_size))

        after = final_state(scene)
        check('preview modes preserve final render and device settings', after == before,
              {'before': before, 'after': after})

        REPORT['diagnostics'] = diagnostics
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'performance.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL viewport performance runtime contract failed')


if __name__ == '__main__':
    main()
