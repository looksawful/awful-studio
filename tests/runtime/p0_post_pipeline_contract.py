"""Blender 5.2 runtime contract for the optional Post Pipeline workflow."""
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
    'python': sys.version,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def managed_compositors(legacy):
    return [
        group for group in bpy.data.node_groups
        if legacy.is_managed(group) and group.get(legacy.ROLE_KEY) == 'COMPOSITOR'
    ]


def lightgroup_names(scene):
    try:
        return {group.name for group in scene.view_layers[0].lightgroups}
    except Exception:
        return set()


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
        scene = bpy.context.scene
        key = legacy.POST_PIPELINE_KEY

        check('Post Pipeline action is named Setup Post Pipeline',
              legacy.AWFUL_OT_BuildPostPipeline.bl_label == 'Setup Post Pipeline',
              legacy.AWFUL_OT_BuildPostPipeline.bl_label)
        check('Post Pipeline action explains created systems',
              all(token in legacy.AWFUL_OT_BuildPostPipeline.bl_description
                  for token in ('Light Groups', 'render passes', 'compositor')),
              legacy.AWFUL_OT_BuildPostPipeline.bl_description)
        check('repeated setup has explicit confirmation invoke',
              legacy.AWFUL_OT_BuildPostPipeline.__dict__.get('invoke') is not None)

        check('normal Build keeps Post Pipeline opt-in', not bool(scene.get(key, False)))
        check('normal Build creates no managed compositor', not managed_compositors(legacy),
              [group.name for group in managed_compositors(legacy)])

        original_caps = dict(legacy.CAPS or {})
        check('exact Blender exposes Light Group capability',
              bool(original_caps.get('viewlayer_lightgroups')), original_caps)
        check('exact Blender exposes compositor group API',
              bool(original_caps.get('compositor_group_api')), original_caps)

        result = bpy.ops.awful.build_post_pipeline_v4()
        check('Setup Post Pipeline finishes', result == {'FINISHED'}, list(result))
        check('Post Pipeline state becomes Ready only after setup', bool(scene.get(key, False)))

        groups_first = lightgroup_names(scene)
        check('all AWFUL Light Groups exist', set(legacy.LIGHT_GROUPS).issubset(groups_first),
              sorted(groups_first))
        view_layer = scene.view_layers[0]
        required_passes = (
            'use_pass_z', 'use_pass_normal', 'use_pass_diffuse_direct',
            'use_pass_glossy_direct', 'use_pass_transmission_direct',
            'use_pass_cryptomatte_object', 'use_pass_cryptomatte_material',
        )
        check('required render passes enabled',
              all(bool(getattr(view_layer, attr, False)) for attr in required_passes),
              {attr: bool(getattr(view_layer, attr, False)) for attr in required_passes})

        tree = scene.compositing_node_group
        check('managed compositor group assigned',
              tree is not None and legacy.is_managed(tree)
              and tree.get(legacy.ROLE_KEY) == 'COMPOSITOR',
              tree.name if tree else None)
        required_nodes = {
            'AWFUL_RenderLayers', 'AWFUL_Denoise', 'AWFUL_Exposure',
            'AWFUL_ColorBalance', 'AWFUL_Glare_Optional', 'AWFUL_GroupOutput',
        }
        node_names = {node.name for node in tree.nodes}
        check('managed compositor contains bounded professional stack',
              required_nodes.issubset(node_names), sorted(node_names))
        compositor_count_first = len(managed_compositors(legacy))
        lightgroup_count_first = len(groups_first)

        # Direct execute is used in background qualification. Interactive invoke
        # must ask for confirmation before this same bounded rebuild path.
        result = bpy.ops.awful.build_post_pipeline_v4()
        check('repeated direct setup remains successful', result == {'FINISHED'}, list(result))
        groups_second = lightgroup_names(scene)
        check('repeated setup does not accumulate Light Groups',
              len(groups_second) == lightgroup_count_first,
              {'before': lightgroup_count_first, 'after': len(groups_second)})
        check('repeated setup keeps one managed compositor',
              len(managed_compositors(legacy)) == compositor_count_first == 1,
              {'before': compositor_count_first,
               'after': len(managed_compositors(legacy))})

        # Unsupported capability must be an explicit no-op CANCELLED state.
        bpy.ops.wm.open_mainfile(filepath=str(args.work / 'studio.blend'), use_scripts=False)
        scene = bpy.context.scene
        legacy.CAPS = dict(original_caps)
        legacy.CAPS['viewlayer_lightgroups'] = False
        before_groups = lightgroup_names(scene)
        before_compositors = len(managed_compositors(legacy))
        result = bpy.ops.awful.build_post_pipeline_v4()
        check('unsupported capability returns CANCELLED', result == {'CANCELLED'}, list(result))
        check('unsupported setup does not mark Ready', not bool(scene.get(key, False)))
        check('unsupported setup does not mutate Light Groups',
              lightgroup_names(scene) == before_groups,
              {'before': sorted(before_groups), 'after': sorted(lightgroup_names(scene))})
        check('unsupported setup creates no compositor',
              len(managed_compositors(legacy)) == before_compositors == 0,
              {'before': before_compositors,
               'after': len(managed_compositors(legacy))})
        legacy.CAPS = original_caps

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        try:
            if 'legacy' in locals() and 'original_caps' in locals():
                legacy.CAPS = original_caps
        except Exception:
            pass
        (args.work / 'post_pipeline.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL Post Pipeline runtime contract failed')


if __name__ == '__main__':
    main()
