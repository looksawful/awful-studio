# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure natural-light policy for AWFUL STUDIO.

This module deliberately avoids importing bpy so environment semantics can be
proved by the fast test layer before Blender adapters are introduced.
"""
from __future__ import annotations

HDRI_PRESETS = frozenset({
    'FISH_HOEK', 'BLOUBERG', 'KLOPPENHEIM', 'BELFAST', 'ROGLAND',
})
PHYSICAL_SKY_PRESETS = frozenset({'NISHITA_DAY', 'NISHITA_SUNSET'})


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
