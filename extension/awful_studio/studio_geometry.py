# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure studio-geometry policy plus Blender adapter hooks for AWFUL STUDIO.

The policy functions in this module intentionally avoid importing ``bpy`` so
metric placement/material/role rules can be proven by the fast test layer.
Blender-specific scene mutation is installed explicitly later by ``install``.
"""
from __future__ import annotations

import math
from typing import Mapping


CYC_LOOKS = {
    'WHITE': (0.78, 0.78, 0.78, 1.0),
    'BLACK': (0.015, 0.015, 0.015, 1.0),
    'CHROMA_GREEN': (0.02, 0.55, 0.04, 1.0),
}

CYC_FINISH = {
    'MATTE': 0.82,
    'MEDIUM': 0.48,
    'GLOSSY': 0.18,
}

ARCHITECTURE_ROLE_GROUPS = {
    'WALLS': (
        'ROOM_RIGHT_CAMERA',
        'ROOM_RIGHT_DOOR_REAR',
        'ROOM_RIGHT_DOOR_FRONT',
        'ROOM_RIGHT_DOOR_TOP',
        'ROOM_CAMERA',
        'ROOM_BACKGROUND',
        'ROOM_LEFT_CAMERA',
        'ROOM_LEFT_BACKGROUND',
        'ROOM_LEFT_WINDOW_BOTTOM',
        'ROOM_LEFT_WINDOW_TOP',
    ),
    'FLOOR': ('ARCH_FLOOR_VISIBLE',),
    'CEILING': ('ROOM_CEILING',),
    'DOOR': ('DOOR_FRAME', 'DOOR_LEAF'),
    'WINDOW_FRAME': ('WINDOW_FRAME',),
    'WINDOW_GLASS': ('WINDOW_GLASS',),
    'CYC': ('CYC',),
}


def cyclorama_distance_bounds(studio_spec: Mapping, clearance: float = 0.25) -> tuple[float, float]:
    """Return physically safe stage-origin -> cove-tangent distance bounds.

    Minimum clearance keeps the maximum supported product envelope away from
    the cove. Maximum clearance keeps the cove radius/vertical section inside
    the room background shell. The rule derives from dimensions instead of a
    magic UI range so future room sizes remain self-consistent.
    """
    clearance = float(clearance)
    if clearance < 0.0:
        raise ValueError('Cyclorama clearance must be non-negative')

    cyc = studio_spec['cyc']
    envelope = studio_spec['product_envelope']
    minimum = max(0.5, float(envelope['max_xy']) * 0.5 + clearance)
    maximum = float(studio_spec['background_y']) - float(cyc['radius']) - clearance
    if maximum <= minimum:
        raise ValueError('Studio dimensions leave no safe cyclorama placement range')
    return minimum, maximum


def clamp_cyclorama_distance(value: float, studio_spec: Mapping, clearance: float = 0.25) -> float:
    low, high = cyclorama_distance_bounds(studio_spec, clearance)
    return min(max(float(value), low), high)


def cyclorama_profile(
    studio_spec: Mapping,
    distance: float,
    segments: int = 64,
    clearance: float = 0.25,
) -> list[tuple[float, float]]:
    """Return the Y/Z profile for the floor run, quarter cove and back rise."""
    if int(segments) < 2:
        raise ValueError('Cyclorama curve needs at least two segments')

    cyc = studio_spec['cyc']
    radius = float(cyc['radius'])
    height = float(cyc['height'])
    if radius <= 0.0 or height < radius:
        raise ValueError('Cyclorama radius/height are physically invalid')

    tangent_y = clamp_cyclorama_distance(distance, studio_spec, clearance)
    front_y = float(cyc['front_y'])
    if front_y >= tangent_y:
        raise ValueError('Cyclorama front edge must stay camera-side of the cove tangent')

    profile: list[tuple[float, float]] = [(front_y, 0.0), (tangent_y, 0.0)]
    for index in range(1, int(segments) + 1):
        t = index / float(segments)
        angle = math.radians(-90.0 + 90.0 * t)
        y = tangent_y + radius * math.cos(angle)
        z = radius + radius * math.sin(angle)
        profile.append((y, z))
    profile.append((tangent_y + radius, height))
    return profile


def cyclorama_style(look: str, finish: str) -> dict[str, object]:
    """Resolve orthogonal cyclorama look and finish into bounded material intent."""
    try:
        base_color = CYC_LOOKS[look]
    except KeyError as exc:
        raise ValueError(f'Unknown cyclorama look: {look}') from exc
    try:
        roughness = CYC_FINISH[finish]
    except KeyError as exc:
        raise ValueError(f'Unknown cyclorama finish: {finish}') from exc
    return {
        'look': look,
        'finish': finish,
        'base_color': base_color,
        'roughness': float(roughness),
    }


def install(legacy):
    """Install Blender adapters later; pure policy import remains scene-clean.

    The runtime implementation is deliberately added only after its packaged
    Blender RED contract exists. Keeping the marker here makes the import path
    explicit without mutating Blender state during module import.
    """
    if getattr(legacy, '_awful_studio_geometry_policy_installed', False):
        return
    legacy._awful_studio_geometry_policy_installed = True
