"""Blender 5.2 runtime evidence for AWFUL product/support placement.

This contract intentionally does not render. It measures world-space bounds so
manual camera perspective cannot be mistaken for an actual support-plane gap.
"""
import argparse
import importlib
import json
from pathlib import Path
import platform
import sys
import traceback

import addon_utils
import bpy

MODULE = 'bl_ext.awful_test.awful_studio'
REPORT = {
    'status': 'failed',
    'checks': [],
    'blender': bpy.app.version_string,
    'platform': platform.platform(),
    'render_tests': False,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def xyz(value):
    return tuple(float(component) for component in value)


def transform_evidence(obj):
    return {
        'name': obj.name,
        'parent': obj.parent.name if obj.parent else None,
        'location': xyz(obj.location),
        'world_translation': xyz(obj.matrix_world.translation),
        'parent_inverse_translation': xyz(obj.matrix_parent_inverse.translation),
        'scale': xyz(obj.scale),
    }


def placement_chain(legacy, root):
    chain = []
    for role in (
        'PRODUCT_STAGE', 'PRODUCT_MOTION', 'PRODUCT_ROT_Z', 'PRODUCT_ROT_X',
        'PRODUCT_ROT_Y', 'PRODUCT_GEOMETRY_ROOT', 'PRODUCT_CONTENT',
    ):
        obj = legacy.REG.object(role)
        if obj is not None:
            chain.append(transform_evidence(obj))
    chain.append(transform_evidence(root))
    return chain


def geometry_bbox(legacy, root):
    objects = [root] + legacy.descendants(root)
    meshes = [obj for obj in objects if obj.type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}]
    return legacy.world_bbox(meshes)


def support_gap(legacy, root):
    bbox = geometry_bbox(legacy, root)
    if bbox is None:
        raise AssertionError('product has no measurable geometry')
    pedestal = legacy.REG.require_object('PEDESTAL')
    pedestal_bbox = legacy.world_bbox([pedestal])
    if pedestal_bbox is None:
        raise AssertionError('pedestal has no measurable geometry')
    product_bottom = float(bbox[0].z)
    pedestal_top = float(pedestal_bbox[1].z)
    return product_bottom - pedestal_top, product_bottom, pedestal_top


def assert_grounded(legacy, root, label, tolerance=1e-4):
    gap, product_bottom, pedestal_top = support_gap(legacy, root)
    check(
        f'{label} product bottom contacts pedestal top',
        abs(gap) <= tolerance,
        {
            'gap': gap,
            'product_bottom': product_bottom,
            'pedestal_top': pedestal_top,
            'pedestal': transform_evidence(legacy.REG.require_object('PEDESTAL')),
            'chain': placement_chain(legacy, root),
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)

    try:
        check('Blender 5.2 runtime', bpy.app.version[:2] == (5, 2), bpy.app.version_string)
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        bpy.ops.wm.open_mainfile(filepath=str(args.work / 'studio.blend'), use_scripts=False)

        ext = importlib.import_module(MODULE)
        product_quality = importlib.import_module(MODULE + '.product_quality')
        legacy = ext.legacy
        ownership = ext.ownership
        scene = bpy.context.scene
        scene.frame_set(1)

        # Reproduce the exact default diagnostic path from Build Studio first.
        content = legacy.REG.require_object('PRODUCT_CONTENT')
        diagnostic_roots = list(content.children)
        check('default diagnostic product exists', bool(diagnostic_roots), [o.name for o in diagnostic_roots])
        diagnostic_bbox_roots = [root for root in diagnostic_roots
                                 if geometry_bbox(legacy, root) is not None]
        check('default diagnostic product is measurable', len(diagnostic_bbox_roots) == 1,
              [o.name for o in diagnostic_bbox_roots])
        assert_grounded(legacy, diagnostic_bbox_roots[0], 'diagnostic')

        # Generated mockups must also begin on the support plane when no artistic
        # vertical-offset policy has been applied yet.
        scene.awful_studio.auto_fit = False
        for key in product_quality.mockup_keys():
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
            scene.frame_set(1)
            assert_grounded(legacy, root, f'{key} non-Auto-Fit')

        scene.awful_studio.auto_fit = True
        for key in product_quality.mockup_keys():
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
            scene.frame_set(1)
            assert_grounded(legacy, root, f'{key} Auto-Fit')

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'product_placement.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL product placement runtime contract failed')


if __name__ == '__main__':
    main()
