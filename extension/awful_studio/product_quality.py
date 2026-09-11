# SPDX-License-Identifier: GPL-3.0-or-later
"""Product Quality policy and Blender adapter hooks for AWFUL STUDIO.

The catalog and starter-material policy at the top of this module are pure
Python so ordinary tests can validate product intent without launching Blender.
Scene mutation is added through explicit adapter functions below that consume
the retained ``legacy`` module rather than importing Blender at module import.
"""
from __future__ import annotations

from copy import deepcopy


MOCKUP_SPECS = {
    'BOTTLE': {
        'label': 'Bottle',
        'dimensions_m': (0.075, 0.075, 0.220),
        'material_slots': ('BODY', 'CAP', 'LABEL'),
        'slot_materials': {
            'BODY': 'GLASS_CLEAR',
            'CAP': 'PLASTIC_GLOSSY',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'JAR': {
        'label': 'Jar',
        'dimensions_m': (0.090, 0.090, 0.110),
        'material_slots': ('BODY', 'LID', 'LABEL'),
        'slot_materials': {
            'BODY': 'GLASS_CLEAR',
            'LID': 'METAL_ANODIZED',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'BOX': {
        'label': 'Box',
        'dimensions_m': (0.120, 0.070, 0.180),
        'material_slots': ('BODY', 'LABEL'),
        'slot_materials': {
            'BODY': 'CARDBOARD',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 2,
        'bevel_segments': 4,
    },
    'CAN': {
        'label': 'Can',
        'dimensions_m': (0.066, 0.066, 0.122),
        'material_slots': ('BODY', 'TOP', 'LABEL'),
        'slot_materials': {
            'BODY': 'METAL_ANODIZED',
            'TOP': 'METAL_ANODIZED',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'PHONE': {
        'label': 'Phone',
        'dimensions_m': (0.071, 0.008, 0.147),
        'material_slots': ('FRAME', 'BACK', 'SCREEN'),
        'slot_materials': {
            'FRAME': 'METAL_ANODIZED',
            'BACK': 'GLASS_DARK',
            'SCREEN': 'SCREEN',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 5,
    },
    'TABLET': {
        'label': 'Tablet',
        'dimensions_m': (0.178, 0.0065, 0.248),
        'material_slots': ('FRAME', 'BACK', 'SCREEN'),
        'slot_materials': {
            'FRAME': 'METAL_ANODIZED',
            'BACK': 'GLASS_DARK',
            'SCREEN': 'SCREEN',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 5,
    },
}


MATERIAL_STARTERS = {
    'PLASTIC_MATTE': {
        'label': 'Matte Plastic',
        'base_color': (0.12, 0.13, 0.15, 1.0),
        'roughness': 0.62,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.46,
        'emission_strength': 0.0,
    },
    'PLASTIC_GLOSSY': {
        'label': 'Glossy Plastic',
        'base_color': (0.09, 0.10, 0.12, 1.0),
        'roughness': 0.22,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.46,
        'emission_strength': 0.0,
    },
    'METAL_ANODIZED': {
        'label': 'Anodized Metal',
        'base_color': (0.18, 0.19, 0.21, 1.0),
        'roughness': 0.28,
        'metallic': 1.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'GLASS_CLEAR': {
        'label': 'Clear Glass',
        'base_color': (0.94, 0.97, 1.0, 1.0),
        'roughness': 0.08,
        'metallic': 0.0,
        'transmission': 0.95,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'GLASS_DARK': {
        'label': 'Dark Glass',
        'base_color': (0.025, 0.03, 0.04, 1.0),
        'roughness': 0.12,
        'metallic': 0.0,
        'transmission': 0.92,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'CERAMIC': {
        'label': 'Ceramic',
        'base_color': (0.82, 0.80, 0.76, 1.0),
        'roughness': 0.34,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'CARDBOARD': {
        'label': 'Cardboard',
        'base_color': (0.42, 0.27, 0.13, 1.0),
        'roughness': 0.78,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'PAPER_LABEL': {
        'label': 'Paper Label',
        'base_color': (0.86, 0.84, 0.79, 1.0),
        'roughness': 0.56,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'SCREEN': {
        'label': 'Screen',
        'base_color': (0.015, 0.020, 0.028, 1.0),
        'roughness': 0.16,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_color': (0.035, 0.055, 0.085, 1.0),
        'emission_strength': 0.65,
    },
}


def mockup_keys() -> tuple[str, ...]:
    return tuple(MOCKUP_SPECS)


def mockup_spec(key: str) -> dict:
    try:
        return deepcopy(MOCKUP_SPECS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL mockup: {key}') from exc


def material_spec(key: str) -> dict:
    try:
        return deepcopy(MATERIAL_STARTERS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL starter material: {key}') from exc
