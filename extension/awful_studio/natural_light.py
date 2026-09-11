# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure natural-light policy for AWFUL STUDIO.

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
    sun.data.energy = float(settings['energy'])
    sun.data.angle = math.radians(float(settings['angle_deg']))
    elevation = math.radians(float(settings['elevation_deg']))
    azimuth = math.radians(float(settings['rotation_deg']))
    direction = legacy.Vector((
        math.cos(elevation) * math.cos(azimuth),
        math.cos(elevation) * math.sin(azimuth),
        -math.sin(elevation),
    ))
    sun.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def _relink_world_source(legacy, scene, preset_id):
    world = scene.world
    if not world or not world.use_nodes:
        return
    nodes, links = world.node_tree.nodes, world.node_tree.links
    mix = nodes.get('AWFUL_CAMERA_BACKGROUND_MIX')
    black = nodes.get('AWFUL_BG_BLACK')
    path = nodes.get('AWFUL_LIGHT_PATH')
    output = nodes.get('AWFUL_WORLD_OUTPUT')
    if not all((mix, black, path, output)):
        return
    policy = mode_policy(preset_id)
    active = black
    if scene.awful_studio.natural_light_enabled:
        if policy['source'] == 'HDRI':
            active = nodes.get(f'AWFUL_BG_{preset_id}') or black
        else:
            active = nodes.get(f'AWFUL_BG_{preset_id}') or black
    legacy.relink_input(links, mix.inputs[1], active.outputs['Background'])
    camera_bg = active if (
        scene.awful_studio.natural_light_enabled
        and scene.awful_studio.show_environment_background
    ) else black
    legacy.relink_input(links, mix.inputs[2], camera_bg.outputs['Background'])
    legacy.relink_input(links, mix.inputs[0], path.outputs['Is Camera Ray'])
    legacy.relink_input(links, output.inputs['Surface'], mix.outputs['Shader'])


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


def install(legacy):
    """Install Blender adapters without touching scene data during import."""
    if getattr(legacy, '_awful_natural_light_policy_installed', False):
        return

    original_create_portal = legacy.create_window_portal
    original_set_portal = legacy.set_window_portal_enabled
    original_apply_environment = legacy.apply_environment_preset

    def create_window_portal(light_collection):
        portal = original_create_portal(light_collection)
        _create_managed_sun(legacy, light_collection)
        return portal

    def set_window_portal_enabled(scene, enabled):
        _apply_portal_policy(legacy, original_set_portal, scene, enabled)

    def apply_environment_preset(scene, preset_id, reset_defaults=True):
        mode_policy(preset_id)
        original_apply_environment(scene, preset_id, reset_defaults)
        _relink_world_source(legacy, scene, preset_id)
        _configure_sun(legacy, scene, preset_id)
        _apply_portal_policy(
            legacy, original_set_portal, scene,
            bool(scene.awful_studio.reflective_room_enabled),
        )
        legacy.bpy.context.view_layer.update()

    legacy.create_window_portal = create_window_portal
    legacy.set_window_portal_enabled = set_window_portal_enabled
    legacy.apply_environment_preset = apply_environment_preset
    legacy._awful_natural_light_policy_installed = True
