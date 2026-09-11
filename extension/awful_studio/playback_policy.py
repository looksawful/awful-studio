# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent Product/Camera playback policy for existing AWFUL motions.

Pure helpers stay Blender-independent for fast tests. `install()` adapts the
retained motion functions before PropertyGroup/Panel registration.
"""

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


def _apply_action_policy(action, mode):
    policy = mode_policy(mode)
    cycle_mode = policy['cycles_modifier']
    for fcurve in action.fcurves:
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

    product_draw = legacy.AWFUL_PT_Product.draw
    camera_draw = legacy.AWFUL_PT_Camera.draw

    def draw_product(self, context):
        product_draw(self, context)
        self.layout.prop(context.scene.awful_studio, 'product_playback', text='Playback')

    def draw_camera(self, context):
        camera_draw(self, context)
        self.layout.prop(context.scene.awful_studio, 'camera_playback', text='Playback')

    legacy.AWFUL_PT_Product.draw = draw_product
    legacy.AWFUL_PT_Camera.draw = draw_camera
    legacy._awful_playback_policy_installed = True
