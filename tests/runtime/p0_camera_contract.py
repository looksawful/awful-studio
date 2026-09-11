"""Blender 5.2 runtime contract for P0 product-safe camera framing."""
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


def set_metrics(scene, width, depth, height):
    values = {
        'width': width, 'depth': depth, 'height': height,
        'half_x': width * 0.5, 'half_y': depth * 0.5, 'half_z': height * 0.5,
        'scale': 1.0, 'bottom_world': -height * 0.5,
    }
    for key, value in values.items():
        scene[f'awful_product_{key}'] = float(value)


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
        policy = ext.camera_policy
        scene = bpy.context.scene
        camera = legacy.REG.require_object('CAMERA')
        dolly = legacy.REG.require_object('CAMERA_DOLLY')
        aim = legacy.REG.require_object('AIM_PRODUCT')

        lighting_targets = [legacy.REG.object(role) for role in
                            ('TARGET_LABEL', 'TARGET_TOP', 'TARGET_BACKGROUND')]
        check('camera target distinct from lighting targets',
              all(target is not None and target != aim for target in lighting_targets))

        scenarios = {
            'wide': (4.0, 0.6, 1.0),
            'tall': (1.0, 0.8, 4.0),
            'deep': (1.2, 5.0, 1.5),
        }
        for name, (width, depth, height) in scenarios.items():
            set_metrics(scene, width, depth, height)
            legacy.apply_camera_base_pose(scene, lens=70.0, margin=1.25)
            distance = float(scene['awful_camera_base_distance'])
            zoff = float(scene['awful_camera_base_height_offset'])
            tan_x, tan_y = policy.frame_tangents(camera.data.view_frame(scene=scene))
            check(f'{name} bounds fit actual Blender camera',
                  policy.bounds_fit(width, depth, height, distance, zoff,
                                    tan_x, tan_y, 1.25),
                  {'distance': distance, 'zoff': zoff,
                   'tan_x': tan_x, 'tan_y': tan_y})
            check(f'{name} dolly uses computed distance',
                  abs(float(dolly.location.y) + distance) < 1e-6,
                  tuple(float(v) for v in dolly.location))

        # Large unscaled products may require distances beyond the old arbitrary 10 m cap.
        set_metrics(scene, 10.0, 10.0, 10.0)
        legacy.apply_camera_base_pose(scene, lens=85.0, margin=1.4)
        check('large product can exceed legacy 10m cap',
              float(scene['awful_camera_base_distance']) > 10.0,
              float(scene['awful_camera_base_distance']))

        # Render aspect participates through Camera.view_frame(scene=...).
        set_metrics(scene, 4.0, 0.6, 1.0)
        scene.render.resolution_x = 2000
        scene.render.resolution_y = 1000
        legacy.apply_camera_base_pose(scene, lens=70.0, margin=1.25)
        landscape_distance = float(scene['awful_camera_base_distance'])
        scene.render.resolution_x = 1000
        scene.render.resolution_y = 2000
        legacy.apply_camera_base_pose(scene, lens=70.0, margin=1.25)
        portrait_distance = float(scene['awful_camera_base_distance'])
        check('portrait aspect pushes wide product camera farther',
              portrait_distance > landscape_distance,
              {'landscape': landscape_distance, 'portrait': portrait_distance})

        # Native lens remains authoritative until an explicit AWFUL camera default/reset.
        camera.data.lens = 57.0
        legacy.apply_camera_motion(scene, 'STATIC')
        check('camera motion preserves manually edited lens',
              abs(float(camera.data.lens) - 57.0) < 1e-6, float(camera.data.lens))
        legacy.apply_lighting_preset(scene, 'COMMERCIAL_3LIGHT', False, False)
        check('lighting preset without camera reset preserves native lens',
              abs(float(camera.data.lens) - 57.0) < 1e-6, float(camera.data.lens))

        # Same explicit framing request is deterministic and does not grow datablocks.
        before_counts = {name: len(getattr(bpy.data, name)) for name in
                         ('objects', 'collections', 'cameras', 'lights', 'materials', 'actions')}
        legacy.apply_camera_base_pose(scene, lens=57.0, margin=1.25)
        first = (float(scene['awful_camera_base_distance']), tuple(float(v) for v in dolly.location))
        legacy.apply_camera_base_pose(scene, lens=57.0, margin=1.25)
        second = (float(scene['awful_camera_base_distance']), tuple(float(v) for v in dolly.location))
        after_counts = {name: len(getattr(bpy.data, name)) for name in before_counts}
        check('camera framing repeat is drift-free', first == second, {'first': first, 'second': second})
        check('camera framing repeat is datablock-bounded', before_counts == after_counts,
              {'before': before_counts, 'after': after_counts})

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'camera.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL camera runtime contract failed')


if __name__ == '__main__':
    main()
