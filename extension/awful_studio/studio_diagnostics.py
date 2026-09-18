# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only studio diagnostics for AWFUL STUDIO."""
from __future__ import annotations

from collections import namedtuple

Diagnostic = namedtuple('Diagnostic', 'code section level message')
LEVELS = ('OK', 'WARNING', 'ERROR')


def make_diagnostic(code, section, level, message):
    level = str(level).upper()
    if level not in LEVELS:
        raise ValueError(f'Unknown diagnostic level: {level}')
    return Diagnostic(str(code), str(section), level, str(message))


def summarize(items):
    counts = {level: 0 for level in LEVELS}
    for item in items:
        if item.level not in counts:
            raise ValueError(f'Unknown diagnostic level: {item.level}')
        counts[item.level] += 1
    return counts


def _item(code, section, condition, ok_message, error_message, level='ERROR'):
    return make_diagnostic(
        code,
        section,
        'OK' if condition else level,
        ok_message if condition else error_message,
    )


def collect(legacy, scene, runtime_performance):
    """Collect cheap diagnostics without mutating scene or downloading assets."""
    settings = scene.awful_studio
    items = []

    built = legacy.REG.object('CYC') is not None
    items.append(_item(
        'studio.built', 'Studio', built,
        'Studio is built.', 'Build Studio has not been run.'))

    product_objects = list(legacy.current_product_objects()) if built else []
    items.append(_item(
        'product.present', 'Product', bool(product_objects),
        'Product hierarchy is present.',
        'No measurable product is mounted in the studio.'))

    preset_id = str(getattr(settings, 'studio_light_preset', ''))
    items.append(_item(
        'lighting.preset', 'Lighting', preset_id in legacy.LIGHTING_PRESETS,
        f'Lighting preset {preset_id} is valid.',
        f'Lighting preset {preset_id or "<none>"} is invalid.'))

    camera = legacy.REG.object('CAMERA') if built else None
    camera_ok = camera is not None and float(getattr(camera.data, 'lens', 0.0)) > 0.0
    items.append(_item(
        'camera.ready', 'Camera', camera_ok,
        'Product camera is available.', 'Product camera is missing or invalid.'))


    world_id = str(getattr(settings, 'world_preset', ''))
    items.append(_item(
        'environment.preset', 'Environment',
        world_id in tuple(getattr(legacy, 'WORLD_PRESET_ORDER', ())),
        f'Environment preset {world_id} is valid.',
        f'Environment preset {world_id or "<none>"} is invalid.'))

    perf = runtime_performance.collect_diagnostics(legacy, scene)
    items.append(make_diagnostic(
        'output.preview', 'Output', 'OK',
        f"Preview {getattr(settings, 'preview_mode', 'FAST')} | "
        f"{perf['engine']} | {perf['scene_device']}."))

    if perf.get('cpu_warning'):
        items.append(make_diagnostic(
            'output.cpu', 'Output', 'WARNING',
            'Cycles is CPU-backed or no compute backend is selected.'))

    post_key = getattr(legacy, 'POST_PIPELINE_KEY', 'awful_post_pipeline_enabled')
    post_enabled = bool(scene.get(post_key, False))
    items.append(make_diagnostic(
        'output.post', 'Output', 'OK',
        'Post Pipeline enabled.' if post_enabled else 'Post Pipeline is optional and not built.'))

    return tuple(items)
