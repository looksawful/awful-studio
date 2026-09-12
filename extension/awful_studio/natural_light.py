# SPDX-License-Identifier: GPL-3.0-or-later
"""Natural-light, Hybrid World and camera-background policy for AWFUL STUDIO.

This module deliberately avoids importing bpy so environment semantics can be
proved by the fast test layer before Blender adapters are introduced.
"""
from __future__ import annotations

import math

HDRI_PRESETS = frozenset({
    'FISH_HOEK', 'BLOUBERG', 'KLOPPENHEIM', 'BELFAST', 'ROGLAND',
})
PHYSICAL_SKY_PRESETS = frozenset({'NISHITA_DAY', 'NISHITA_SUNSET'})

HYBRID_WORLD_FACTOR = 0.25
MAX_STRENGTH_MULTIPLIER = 4.0
_LIGHTING_REGIMES = {
    'COMMERCIAL': {
        'regime': 'HYBRID',
        'world_default': True,
        'world_factor': HYBRID_WORLD_FACTOR,
    },
    'NATURAL': {
        'regime': 'NATURAL',
        'world_default': True,
        'world_factor': 1.0,
    },
    'FLASH': {
        'regime': 'STUDIO',
        'world_default': False,
        'world_factor': 0.0,
    },
    'CINEMA': {
        'regime': 'STUDIO',
        'world_default': False,
        'world_factor': 0.0,
    },
}


def _bounded_multiplier(value: float) -> float:
    return max(0.0, min(MAX_STRENGTH_MULTIPLIER, float(value)))


def lighting_regime(family: str) -> dict[str, object]:
    """Return the preset-family default World participation policy."""
    try:
        return dict(_LIGHTING_REGIMES[family])
    except KeyError as exc:
        raise ValueError(f'Unknown lighting family: {family}') from exc


def effective_world_strength(*, base_strength: float, user_strength: float,
                             family: str, world_enabled: bool | None = None,
                             studio_enabled: bool = True) -> float:
    """Resolve illumination strength without coupling it to camera background.

    Commercial defaults to World as a 25% fill while Studio lights are active.
    Natural uses the World at full preset strength. Flash/Cinema default World
    off, but an explicit user enable remains meaningful instead of being locked
    to zero by the default regime.
    """
    policy = lighting_regime(family)
    enabled = bool(policy['world_default']) if world_enabled is None else bool(world_enabled)
    if not enabled:
        return 0.0

    if family == 'NATURAL' or not studio_enabled:
        factor = 1.0
    elif bool(policy['world_default']):
        factor = float(policy['world_factor'])
    else:
        # Explicit World opt-in for a Studio-only family becomes a normal hybrid.
        factor = HYBRID_WORLD_FACTOR

    return max(0.0, float(base_strength)) * _bounded_multiplier(user_strength) * factor


def camera_background_strength(*, base_strength: float, brightness: float) -> float:
    """Resolve camera-visible background brightness independently of lighting."""
    return max(0.0, float(base_strength)) * _bounded_multiplier(brightness)


def mode_policy(preset_id: str) -> dict[str, object]:
    if preset_id in HDRI_PRESETS:
        return {
            'source': 'HDRI',
            'requires_asset': True,
            'sun': False,
            'portal': False,
            'allow_fallback': False,
        }
    if preset_id in PHYSICAL_SKY_PRESETS:
        return {
            'source': 'PHYSICAL_SKY',
            'requires_asset': False,
            'sun': True,
            'portal': True,
            'allow_fallback': False,
        }
    raise ValueError(f'Unknown environment preset: {preset_id}')


SUN_SETTINGS = {
    'NISHITA_DAY': {
        'energy': 2.2,
        'angle_deg': 0.75,
        'elevation_deg': 34.0,
        'rotation_deg': 118.0,
    },
    'NISHITA_SUNSET': {
        'energy': 1.3,
        'angle_deg': 1.05,
        'elevation_deg': 6.0,
        'rotation_deg': 235.0,
    },
}


def sun_settings(preset_id: str) -> dict[str, float]:
    if preset_id not in PHYSICAL_SKY_PRESETS:
        raise ValueError(f'Preset has no managed Sun: {preset_id}')
    return dict(SUN_SETTINGS[preset_id])


def _family(scene) -> str:
    family = str(getattr(scene.awful_studio, 'studio_light_family', 'COMMERCIAL'))
    lighting_regime(family)
    return family


def _base_strength(node) -> float:
    if node is None:
        return 0.0
    if 'awful_base_strength' not in node:
        node['awful_base_strength'] = float(node.inputs['Strength'].default_value)
    return float(node['awful_base_strength'])


def _ensure_camera_background_nodes(legacy, world):
    if not world or not world.use_nodes:
        return
    nodes, links = world.node_tree.nodes, world.node_tree.links
    source_nodes = {
        **{preset_id: nodes.get(f'AWFUL_ENV_{preset_id}') for preset_id in HDRI_PRESETS},
        'NISHITA_DAY': nodes.get('AWFUL_SKY_DAY'),
        'NISHITA_SUNSET': nodes.get('AWFUL_SKY_SUNSET'),
    }
    for preset_id, source in source_nodes.items():
        illumination = nodes.get(f'AWFUL_BG_{preset_id}')
        if source is None or illumination is None:
            continue
        base = _base_strength(illumination)
        camera = nodes.get(f'AWFUL_CAMERA_BG_{preset_id}')
        if camera is None:
            camera = nodes.new('ShaderNodeBackground')
            camera.name = f'AWFUL_CAMERA_BG_{preset_id}'
            camera.label = 'Camera Background Only'
            camera.location = (70, illumination.location.y - 70)
        camera['awful_base_strength'] = base
        camera.inputs['Strength'].default_value = base
        legacy.relink_input(links, camera.inputs['Color'], source.outputs['Color'])


def _selected_nodes(legacy, scene, preset_id):
    world = scene.world
    if not world or not world.use_nodes:
        return None, None, None, None, None
    nodes = world.node_tree.nodes
    return (
        nodes.get('AWFUL_CAMERA_BACKGROUND_MIX'),
        nodes.get('AWFUL_BG_BLACK'),
        nodes.get('AWFUL_LIGHT_PATH'),
        nodes.get(f'AWFUL_BG_{preset_id}'),
        nodes.get(f'AWFUL_CAMERA_BG_{preset_id}'),
    )


def _update_selected_strengths(legacy, scene, preset_id):
    _mix, _black, _path, illumination, camera = _selected_nodes(legacy, scene, preset_id)
    if illumination is None or camera is None:
        return
    base = _base_strength(illumination)
    illumination.inputs['Strength'].default_value = effective_world_strength(
        base_strength=base,
        user_strength=float(scene.awful_studio.world_light_strength),
        family=_family(scene),
        world_enabled=bool(scene.awful_studio.natural_light_enabled),
        studio_enabled=bool(scene.awful_studio.studio_lights_enabled),
    )
    camera.inputs['Strength'].default_value = camera_background_strength(
        base_strength=base,
        brightness=float(scene.awful_studio.background_brightness),
    )


def _relink_world_source(legacy, scene, preset_id):
    world = scene.world
    if not world or not world.use_nodes:
        return
    nodes, links = world.node_tree.nodes, world.node_tree.links
    mix, black, path, illumination, camera = _selected_nodes(legacy, scene, preset_id)
    output = nodes.get('AWFUL_WORLD_OUTPUT')
    if not all((mix, black, path, output)):
        return

    _update_selected_strengths(legacy, scene, preset_id)
    light_source = illumination if (
        scene.awful_studio.natural_light_enabled and illumination is not None
    ) else black
    camera_source = camera if (
        scene.awful_studio.natural_light_enabled
        and scene.awful_studio.show_environment_background
        and camera is not None
    ) else black
    legacy.relink_input(links, mix.inputs[1], light_source.outputs['Background'])
    legacy.relink_input(links, mix.inputs[2], camera_source.outputs['Background'])
    legacy.relink_input(links, mix.inputs[0], path.outputs['Is Camera Ray'])
    legacy.relink_input(links, output.inputs['Surface'], mix.outputs['Shader'])


def _create_managed_sun(legacy, light_collection):
    sun = legacy.REG.object('NATURAL_SUN')
    if sun is not None:
        return sun
    data = legacy.bpy.data.lights.new('LIGHT_Natural_Sun', type='SUN')
    legacy.mark_managed(data, 'NATURAL_SUN_DATA')
    data.energy = 0.0
    obj = legacy.bpy.data.objects.new('LIGHT_Natural_Sun', data)
    legacy.mark_managed(obj, 'NATURAL_SUN')
    light_collection.objects.link(obj)
    obj.hide_render = True
    obj.hide_viewport = True
    return obj


def _configure_sun(legacy, scene, preset_id):
    sun = legacy.REG.object('NATURAL_SUN')
    if sun is None:
        return
    policy = mode_policy(preset_id)
    enabled = bool(scene.awful_studio.natural_light_enabled and policy['sun'])
    sun.hide_render = not enabled
    sun.hide_viewport = not enabled
    if not enabled:
        return
    settings = sun_settings(preset_id)
    sun.data.energy = effective_world_strength(
        base_strength=float(settings['energy']),
        user_strength=float(scene.awful_studio.world_light_strength),
        family=_family(scene),
        world_enabled=True,
        studio_enabled=bool(scene.awful_studio.studio_lights_enabled),
    )
    sun.data.angle = math.radians(float(settings['angle_deg']))
    elevation = math.radians(float(settings['elevation_deg']))
    azimuth = math.radians(float(settings['rotation_deg']))
    direction = legacy.Vector((
        math.cos(elevation) * math.cos(azimuth),
        math.cos(elevation) * math.sin(azimuth),
        -math.sin(elevation),
    ))
    sun.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def _apply_portal_policy(legacy, original, scene, requested):
    try:
        policy = mode_policy(scene.awful_studio.world_preset)
    except ValueError:
        policy = {'portal': False}
    enabled = bool(
        requested
        and scene.awful_studio.natural_light_enabled
        and policy['portal']
    )
    original(scene, enabled)
    portal = legacy.REG.object('WINDOW_PORTAL')
    if portal is not None:
        portal.data.energy = 0.0


def _refresh_current_world(legacy, scene):
    if legacy.REG.object('CYC') is None or scene.world is None:
        return
    preset_id = str(scene.awful_studio.world_preset)
    _relink_world_source(legacy, scene, preset_id)
    _configure_sun(legacy, scene, preset_id)
    legacy.bpy.context.view_layer.update()


def install(legacy):
    """Install Blender adapters without touching scene data during import."""
    if getattr(legacy, '_awful_natural_light_policy_installed', False):
        return

    original_setup_world = legacy.setup_world_nodes
    original_create_portal = legacy.create_window_portal
    original_set_portal = legacy.set_window_portal_enabled
    original_apply_environment = legacy.apply_environment_preset
    original_apply_lighting = legacy.apply_lighting_preset
    original_environment_draw = legacy.AWFUL_PT_Environment.draw

    def on_world_strength(self, context):
        _refresh_current_world(legacy, context.scene)

    def on_background_brightness(self, context):
        _refresh_current_world(legacy, context.scene)

    def on_studio_master(self, context):
        if legacy.REG.object('LIGHT_RIG'):
            legacy.apply_artificial_master(context.scene)
        _refresh_current_world(legacy, context.scene)

    annotations = legacy.AWFUL_StudioSettings.__annotations__
    annotations['world_light_strength'] = legacy.bpy.props.FloatProperty(
        name='World Light Strength',
        description='Environment illumination strength, independent of camera background',
        default=1.0,
        min=0.0,
        max=MAX_STRENGTH_MULTIPLIER,
        update=on_world_strength,
    )
    annotations['background_brightness'] = legacy.bpy.props.FloatProperty(
        name='Background Brightness',
        description='Camera-visible environment brightness without changing product illumination',
        default=1.0,
        min=0.0,
        max=MAX_STRENGTH_MULTIPLIER,
        update=on_background_brightness,
    )
    # Rebind Studio's update callback so toggling Studio also recalculates whether
    # World is a 25% hybrid fill or a full standalone source.
    annotations['studio_lights_enabled'] = legacy.BoolProperty(
        name='Studio', default=True, update=on_studio_master,
    )

    def setup_world_nodes():
        world = original_setup_world()
        _ensure_camera_background_nodes(legacy, world)
        return world

    def create_window_portal(light_collection):
        portal = original_create_portal(light_collection)
        _create_managed_sun(legacy, light_collection)
        return portal

    def set_window_portal_enabled(scene, enabled):
        _apply_portal_policy(legacy, original_set_portal, scene, enabled)

    def apply_environment_preset(scene, preset_id, reset_defaults=True):
        mode_policy(preset_id)
        original_apply_environment(scene, preset_id, reset_defaults)
        _ensure_camera_background_nodes(legacy, scene.world)
        _relink_world_source(legacy, scene, preset_id)
        _configure_sun(legacy, scene, preset_id)
        _apply_portal_policy(
            legacy, original_set_portal, scene,
            bool(scene.awful_studio.reflective_room_enabled),
        )
        legacy.bpy.context.view_layer.update()

    def apply_lighting_preset(scene, preset_id, apply_camera_defaults=False,
                              apply_environment_defaults=True):
        result = original_apply_lighting(
            scene, preset_id, apply_camera_defaults, apply_environment_defaults)
        if apply_environment_defaults:
            preset = legacy.LIGHTING_PRESETS[preset_id]
            regime = lighting_regime(preset.family)
            scene.awful_studio.natural_light_enabled = bool(regime['world_default'])
            apply_environment_preset(
                scene, scene.awful_studio.world_preset, reset_defaults=True)
        return result

    def draw_environment(self, context):
        original_environment_draw(self, context)
        settings = context.scene.awful_studio
        column = self.layout.column(align=True)
        column.enabled = bool(settings.natural_light_enabled)
        column.prop(settings, 'world_light_strength', text='World Light Strength')
        camera_row = column.row(align=True)
        camera_row.enabled = bool(settings.show_environment_background)
        camera_row.prop(settings, 'background_brightness', text='Background Brightness')

    legacy.setup_world_nodes = setup_world_nodes
    legacy.create_window_portal = create_window_portal
    legacy.set_window_portal_enabled = set_window_portal_enabled
    legacy.apply_environment_preset = apply_environment_preset
    legacy.apply_lighting_preset = apply_lighting_preset
    legacy.AWFUL_PT_Environment.draw = draw_environment
    legacy._awful_natural_light_policy_installed = True
