"""Blender 5.2 runtime contract for independent bounded playback policy."""
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
    'status': 'failed', 'checks': [], 'blender': bpy.app.version_string,
    'platform': platform.platform(), 'python': sys.version,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def target_sources(legacy, target):
    roles = (
        ('PRODUCT_STAGE', 'PRODUCT_MOTION', 'PRODUCT_ROT_Z', 'PRODUCT_ROT_X',
         'PRODUCT_ROT_Y', 'PRODUCT_GEOMETRY_ROOT')
        if target == 'PRODUCT' else
        ('CAMERA_YAW', 'CAMERA_PITCH', 'CAMERA_DOLLY', 'CAMERA_PATH_FOLLOW')
    )
    sources = [legacy.REG.object(role) for role in roles]
    if target == 'CAMERA':
        camera = legacy.REG.object('CAMERA')
        if camera:
            sources.append(camera.data)
    return [source for source in sources if source is not None]


def target_actions(legacy, target):
    actions = []
    seen = set()
    for source in target_sources(legacy, target):
        animation = getattr(source, 'animation_data', None)
        action = getattr(animation, 'action', None) if animation else None
        if action and action.as_pointer() not in seen:
            seen.add(action.as_pointer())
            actions.append(action)
    return actions


def keyed_span(policy, actions):
    frames = []
    for action in actions:
        for fcurve in policy.iter_fcurves(action):
            frames.extend(float(point.co.x) for point in fcurve.keyframe_points)
    if not frames:
        return None
    return min(frames), max(frames)


def cycles_state(policy, actions):
    result = []
    for action in actions:
        for fcurve in policy.iter_fcurves(action):
            cycles = [modifier for modifier in fcurve.modifiers if modifier.type == 'CYCLES']
            result.append({
                'action': action.name,
                'path': fcurve.data_path,
                'count': len(cycles),
                'before': cycles[0].mode_before if cycles else None,
                'after': cycles[0].mode_after if cycles else None,
            })
    return result


def assert_mode(legacy, policy, target, mode, expected):
    actions = target_actions(legacy, target)
    check(f'{target} {mode} has keyed action', bool(actions), [action.name for action in actions])
    state = cycles_state(policy, actions)
    check(f'{target} {mode} exposes fcurves', bool(state), state)
    if expected is None:
        check(f'{target} {mode} has no cycles modifier',
              all(item['count'] == 0 for item in state), state)
    else:
        check(f'{target} {mode} has exactly one cycles modifier per curve',
              all(item['count'] == 1 for item in state), state)
        check(f'{target} {mode} cycles mode is {expected}',
              all(item['before'] == expected and item['after'] == expected for item in state), state)


def expected_preview(legacy, policy, settings):
    product = policy.preview_span(
        keyed_span(policy, target_actions(legacy, 'PRODUCT')),
        settings.product_playback,
    )
    camera = policy.preview_span(
        keyed_span(policy, target_actions(legacy, 'CAMERA')),
        settings.camera_playback,
    )
    return policy.union_preview_spans(product, camera)


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
        policy = ext.playback_policy
        scene = bpy.context.scene
        settings = scene.awful_studio

        check('independent playback RNA exists',
              hasattr(settings, 'product_playback') and hasattr(settings, 'camera_playback'))
        check('default FPS is 24', scene.render.fps == 24, scene.render.fps)

        legacy.apply_product_motion(scene, 'SPIN_Z')
        legacy.apply_camera_motion(scene, 'ARC_LR')
        check('representative artistic presets selected',
              settings.product_motion == 'SPIN_Z' and settings.camera_motion == 'ARC_LR')

        modes = (
            ('ONCE', None),
            ('LOOP', 'REPEAT'),
            ('PING_PONG', 'MIRROR'),
        )
        for mode, expected in modes:
            product_motion = settings.product_motion
            camera_motion = settings.camera_motion
            settings.product_playback = mode
            assert_mode(legacy, policy, 'PRODUCT', mode, expected)
            check(f'product {mode} does not change artistic preset',
                  settings.product_motion == product_motion)
            check(f'product {mode} leaves camera policy independent',
                  settings.camera_motion == camera_motion)

            settings.camera_playback = mode
            assert_mode(legacy, policy, 'CAMERA', mode, expected)
            check(f'camera {mode} does not change artistic preset',
                  settings.camera_motion == camera_motion)

        settings.product_playback = 'LOOP'
        settings.camera_playback = 'PING_PONG'
        assert_mode(legacy, policy, 'PRODUCT', 'independent LOOP', 'REPEAT')
        assert_mode(legacy, policy, 'CAMERA', 'independent PING_PONG', 'MIRROR')
        check('playback properties remain independent',
              settings.product_playback == 'LOOP' and settings.camera_playback == 'PING_PONG')

        # Preview Range is a view/playback aid. It must never rewrite the render range.
        render_range = (scene.frame_start, scene.frame_end)
        scene.frame_set(100)
        settings.product_playback = 'LOOP'
        settings.camera_playback = 'ONCE'
        preview = expected_preview(legacy, policy, settings)
        check('generated playback enables Preview Range', scene.use_preview_range, scene.use_preview_range)
        check('Preview Range is union of Product and Camera playback',
              (scene.frame_preview_start, scene.frame_preview_end) == preview,
              {'actual': (scene.frame_preview_start, scene.frame_preview_end), 'expected': preview})
        check('Preview Range synchronization preserves render range',
              (scene.frame_start, scene.frame_end) == render_range,
              {'actual': (scene.frame_start, scene.frame_end), 'expected': render_range})
        check('current frame stays unchanged when already inside Preview Range',
              scene.frame_current == 100, scene.frame_current)

        # Changing one independent playback policy expands the union and clamps only
        # when the current frame is outside the newly computed range.
        scene.frame_set(preview[1] + 100)
        settings.camera_playback = 'PING_PONG'
        expanded = expected_preview(legacy, policy, settings)
        check('playback update recomputes Preview Range automatically',
              (scene.frame_preview_start, scene.frame_preview_end) == expanded,
              {'actual': (scene.frame_preview_start, scene.frame_preview_end), 'expected': expanded})
        check('current frame clamps into recomputed Preview Range',
              scene.frame_current == expanded[1],
              {'actual': scene.frame_current, 'expected': expanded[1]})
        check('automatic playback synchronization still preserves render range',
              (scene.frame_start, scene.frame_end) == render_range)

        # Manual recovery controls are required even though synchronization is automatic.
        scene.use_preview_range = False
        fit_result = bpy.ops.awful.fit_timeline_to_motion()
        check('Fit Timeline to Motion operator finishes', fit_result == {'FINISHED'}, list(fit_result))
        check('Fit Timeline restores expected Preview Range',
              scene.use_preview_range
              and (scene.frame_preview_start, scene.frame_preview_end) == expanded)
        reset_result = bpy.ops.awful.reset_timeline()
        check('Reset Timeline operator finishes', reset_result == {'FINISHED'}, list(reset_result))
        check('Reset Timeline disables Preview Range', not scene.use_preview_range)
        check('Reset Timeline does not change render range',
              (scene.frame_start, scene.frame_end) == render_range)

        # FPS stays a native editable Blender setting rather than an AWFUL lock.
        scene.render.fps = 30
        legacy.apply_product_motion(scene, 'SPIN_Z')
        check('user-edited FPS survives motion reapply', scene.render.fps == 30, scene.render.fps)

        baseline_actions = len(bpy.data.actions)
        for _ in range(5):
            legacy.apply_product_motion(scene, 'SPIN_Z')
            legacy.apply_camera_motion(scene, 'ARC_LR')
        check('reapplying motions does not accumulate actions',
              len(bpy.data.actions) == baseline_actions,
              {'before': baseline_actions, 'after': len(bpy.data.actions)})
        assert_mode(legacy, policy, 'PRODUCT', 'reapplied LOOP', 'REPEAT')
        assert_mode(legacy, policy, 'CAMERA', 'reapplied PING_PONG', 'MIRROR')

        check('generated playback actions remain owned',
              all(ext.ownership.owned(action, scene)
                  for target in ('PRODUCT', 'CAMERA')
                  for action in target_actions(legacy, target)))

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'playback.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL playback runtime contract failed')


if __name__ == '__main__':
    main()
