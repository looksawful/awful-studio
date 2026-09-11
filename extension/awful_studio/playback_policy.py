# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent Product/Camera playback and Preview Range policy.

Pure helpers stay Blender-independent for fast tests. `install()` adapts the
retained motion functions before PropertyGroup/Panel registration.
"""

import math

PLAYBACK_MODES = ('ONCE', 'LOOP', 'PING_PONG')
_MODE_POLICIES = {
    'ONCE': {'cycles_modifier': None, 'repeats': False},
    'LOOP': {'cycles_modifier': 'REPEAT', 'repeats': True},
    'PING_PONG': {'cycles_modifier': 'MIRROR', 'repeats': True},
}
_SETTING_FIELDS = {
    'PRODUCT': 'product_playback',
    'CAMERA': 'camera_playback',
}
_PRODUCT_ROLES = (
    'PRODUCT_STAGE', 'PRODUCT_MOTION', 'PRODUCT_ROT_Z', 'PRODUCT_ROT_X',
    'PRODUCT_ROT_Y', 'PRODUCT_GEOMETRY_ROOT',
)
_CAMERA_ROLES = (
    'CAMERA_YAW', 'CAMERA_PITCH', 'CAMERA_DOLLY', 'CAMERA_PATH_FOLLOW',
)


def mode_policy(mode):
    try:
        return dict(_MODE_POLICIES[mode])
    except KeyError as exc:
        raise ValueError(f'Unknown playback mode: {mode}') from exc


def setting_fields():
    return dict(_SETTING_FIELDS)


def modifier_plan(mode):
    policy = mode_policy(mode)
    return {
        'remove_existing_cycles': True,
        'cycles_modifiers_to_add': 0 if policy['cycles_modifier'] is None else 1,
        'mode': policy['cycles_modifier'],
    }


def _integer_keyed_span(span):
    if span is None:
        return None
    start, end = map(float, span)
    if not math.isfinite(start) or not math.isfinite(end):
        raise ValueError('Playback span must be finite')
    if end < start:
        start, end = end, start
    return int(math.floor(start)), int(math.ceil(end))


def preview_span(keyed_span, mode):
    """Map one keyed action span to the Preview Range needed to see playback.

    ONCE shows one keyed span. LOOP shows two consecutive spans. PING_PONG uses
    the same two-span duration, representing one forward + backward cycle.
    """
    mode_policy(mode)
    span = _integer_keyed_span(keyed_span)
    if span is None:
        return None
    start, end = span
    if mode == 'ONCE':
        return start, end
    duration = max(0, end - start)
    return start, end + duration


def union_preview_spans(*spans):
    """Return the union of available Product/Camera preview spans."""
    normalized = [_integer_keyed_span(span) for span in spans if span is not None]
    if not normalized:
        return None
    return min(span[0] for span in normalized), max(span[1] for span in normalized)


def clamp_frame_to_span(frame, span):
    """Preserve current frame inside a span and clamp only when outside it."""
    start, end = _integer_keyed_span(span)
    value = int(frame)
    return max(start, min(end, value))


def iter_fcurves(action):
    """Yield an Action's F-Curves on both legacy and Blender 5.2 APIs.

    Blender 5.2 stores keyframed channels under Action layers -> strips ->
    channelbags. Older/legacy actions expose `action.fcurves` directly.
    """
    seen = set()
    direct = getattr(action, 'fcurves', None)
    if direct is not None:
        for fcurve in direct:
            pointer = fcurve.as_pointer()
            if pointer not in seen:
                seen.add(pointer)
                yield fcurve
    for layer in getattr(action, 'layers', ()):
        for strip in getattr(layer, 'strips', ()):
            for channelbag in getattr(strip, 'channelbags', ()):
                for fcurve in getattr(channelbag, 'fcurves', ()):
                    pointer = fcurve.as_pointer()
                    if pointer not in seen:
                        seen.add(pointer)
                        yield fcurve


def _sources(legacy, target):
    roles = _PRODUCT_ROLES if target == 'PRODUCT' else _CAMERA_ROLES
    sources = [legacy.REG.object(role) for role in roles]
    if target == 'CAMERA':
        camera = legacy.REG.object('CAMERA')
        if camera is not None:
            sources.append(getattr(camera, 'data', None))
    return [source for source in sources if source is not None]


def _action(source):
    animation = getattr(source, 'animation_data', None)
    return getattr(animation, 'action', None) if animation else None


def _actions(legacy, target):
    result = []
    seen = set()
    for source in _sources(legacy, target):
        action = _action(source)
        if action is not None and action.as_pointer() not in seen:
            seen.add(action.as_pointer())
            result.append(action)
    return result


def _keyed_span(actions):
    frames = []
    for action in actions:
        for fcurve in iter_fcurves(action):
            frames.extend(float(point.co.x) for point in fcurve.keyframe_points)
    if not frames:
        return None
    return min(frames), max(frames)


def target_preview_span(legacy, scene, target):
    field = _SETTING_FIELDS[target]
    return preview_span(_keyed_span(_actions(legacy, target)), getattr(scene.awful_studio, field))


def scene_preview_span(legacy, scene):
    return union_preview_spans(
        target_preview_span(legacy, scene, 'PRODUCT'),
        target_preview_span(legacy, scene, 'CAMERA'),
    )


def sync_preview_range(legacy, scene):
    """Fit Blender Preview Range to generated motion without touching render range/FPS."""
    span = scene_preview_span(legacy, scene)
    if span is None:
        scene.use_preview_range = False
        return None
    start, end = span
    scene.frame_preview_start = start
    scene.frame_preview_end = end
    scene.use_preview_range = True
    clamped = clamp_frame_to_span(scene.frame_current, span)
    if clamped != scene.frame_current:
        scene.frame_set(clamped)
    return span


def reset_preview_range(scene):
    """Disable AWFUL's playback Preview Range without changing the render range."""
    scene.use_preview_range = False
    scene.frame_preview_start = int(scene.frame_start)
    scene.frame_preview_end = int(scene.frame_end)


def _apply_action_policy(action, mode):
    policy = mode_policy(mode)
    cycle_mode = policy['cycles_modifier']
    for fcurve in iter_fcurves(action):
        for modifier in list(fcurve.modifiers):
            if modifier.type == 'CYCLES':
                fcurve.modifiers.remove(modifier)
        if cycle_mode is not None:
            modifier = fcurve.modifiers.new('CYCLES')
            modifier.mode_before = cycle_mode
            modifier.mode_after = cycle_mode


def _mark_current_actions(legacy, scene, target):
    for action in _actions(legacy, target):
        if not legacy.ownership.owned(action, scene):
            legacy.ownership.mark(action, 'ACTION', scene)


def _remove_replaced_owned_actions(legacy, scene, previous):
    current_ptrs = {action.as_pointer() for target in ('PRODUCT', 'CAMERA')
                    for action in _actions(legacy, target)}
    for action in previous:
        try:
            if (action.as_pointer() not in current_ptrs and action.users == 0 and
                    legacy.ownership.owned(action, scene)):
                legacy.bpy.data.actions.remove(action)
        except ReferenceError:
            pass


def apply_target_policy(legacy, scene, target, mode=None):
    field = _SETTING_FIELDS[target]
    mode = mode or getattr(scene.awful_studio, field)
    mode_policy(mode)  # validate before mutating anything
    for action in _actions(legacy, target):
        _apply_action_policy(action, mode)
    sync_preview_range(legacy, scene)
    return mode


def install(legacy):
    if getattr(legacy, '_awful_playback_policy_installed', False):
        return

    items = [
        ('ONCE', 'Once', 'Play the keyed motion once without cyclic extrapolation'),
        ('LOOP', 'Loop', 'Repeat the keyed motion continuously'),
        ('PING_PONG', 'Ping-Pong', 'Repeat the keyed motion forward and backward'),
    ]

    def on_product_playback(self, context):
        if legacy.REG.object('CYC') is not None:
            apply_target_policy(legacy, context.scene, 'PRODUCT', self.product_playback)

    def on_camera_playback(self, context):
        if legacy.REG.object('CYC') is not None:
            apply_target_policy(legacy, context.scene, 'CAMERA', self.camera_playback)

    annotations = legacy.AWFUL_StudioSettings.__annotations__
    annotations['product_playback'] = legacy.EnumProperty(
        name='Product Playback', items=items, default='ONCE', update=on_product_playback,
    )
    annotations['camera_playback'] = legacy.EnumProperty(
        name='Camera Playback', items=items, default='ONCE', update=on_camera_playback,
    )

    original_product = legacy.apply_product_motion
    original_camera = legacy.apply_camera_motion

    def apply_product_motion(scene, preset=None):
        previous = _actions(legacy, 'PRODUCT')
        result = original_product(scene, preset)
        _mark_current_actions(legacy, scene, 'PRODUCT')
        _remove_replaced_owned_actions(legacy, scene, previous)
        apply_target_policy(legacy, scene, 'PRODUCT')
        return result

    def apply_camera_motion(scene, preset=None):
        previous = _actions(legacy, 'CAMERA')
        result = original_camera(scene, preset)
        _mark_current_actions(legacy, scene, 'CAMERA')
        _remove_replaced_owned_actions(legacy, scene, previous)
        apply_target_policy(legacy, scene, 'CAMERA')
        return result

    legacy.apply_product_motion = apply_product_motion
    legacy.apply_camera_motion = apply_camera_motion

    class AWFUL_OT_FitTimelineToMotion(legacy.bpy.types.Operator):
        bl_idname = 'awful.fit_timeline_to_motion'
        bl_label = 'Fit Timeline to Motion'
        bl_description = 'Fit Blender Preview Range to generated Product and Camera motion'
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            span = sync_preview_range(legacy, context.scene)
            if span is None:
                self.report({'INFO'}, 'No generated Product or Camera motion to fit')
            return {'FINISHED'}

    class AWFUL_OT_ResetTimeline(legacy.bpy.types.Operator):
        bl_idname = 'awful.reset_timeline'
        bl_label = 'Reset Timeline'
        bl_description = 'Disable the AWFUL Preview Range and leave Blender render range unchanged'
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            reset_preview_range(context.scene)
            return {'FINISHED'}

    legacy.CLASSES = (*legacy.CLASSES, AWFUL_OT_FitTimelineToMotion, AWFUL_OT_ResetTimeline)

    product_draw = legacy.AWFUL_PT_Product.draw
    camera_draw = legacy.AWFUL_PT_Camera.draw

    def draw_timeline_controls(layout):
        row = layout.row(align=True)
        row.operator('awful.fit_timeline_to_motion', text='Fit Timeline')
        row.operator('awful.reset_timeline', text='Reset Timeline')

    def draw_product(self, context):
        product_draw(self, context)
        self.layout.prop(context.scene.awful_studio, 'product_playback', text='Playback')
        draw_timeline_controls(self.layout)

    def draw_camera(self, context):
        camera_draw(self, context)
        self.layout.prop(context.scene.awful_studio, 'camera_playback', text='Playback')
        draw_timeline_controls(self.layout)

    legacy.AWFUL_PT_Product.draw = draw_product
    legacy.AWFUL_PT_Camera.draw = draw_camera
    legacy._awful_playback_policy_installed = True
