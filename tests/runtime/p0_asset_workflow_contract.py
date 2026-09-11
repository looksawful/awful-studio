"""Blender 5.2 structural runtime contract for HDRI workflow and fallback."""
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
    'render_tests': False,
    'network_attempts': 0,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def linked_node(input_socket):
    return input_socket.links[0].from_node if input_socket.links else None


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
        cache = ext.asset_cache
        workflow = importlib.import_module(MODULE + '.asset_workflow')
        scene = bpy.context.scene
        settings = scene.awful_studio
        world = scene.world
        nodes = world.node_tree.nodes
        mix = nodes.get('AWFUL_CAMERA_BACKGROUND_MIX')

        check('primary fetch operator is Download All HDRIs',
              legacy.AWFUL_OT_FetchAssets.bl_label == 'Download All HDRIs',
              legacy.AWFUL_OT_FetchAssets.bl_label)
        check('online-preferences helper operator is registered',
              hasattr(bpy.ops.awful, 'open_online_preferences'))

        # Missing reviewed HDRI keeps selected intent but resolves to Physical Sky.
        selected = 'FISH_HOEK'
        asset_key = legacy.HDRI_PRESETS[selected]['asset']
        path = Path(legacy.hdri_asset_path(asset_key))
        check('isolated runtime starts without selected HDRI cache',
              not cache.read_valid(path), str(path))
        env = nodes.get(f'AWFUL_ENV_{selected}')
        env.image = None
        settings.natural_light_enabled = True
        settings.studio_lights_enabled = False
        settings.show_environment_background = True
        settings.world_preset = selected
        legacy.apply_environment_preset(scene, selected, reset_defaults=True)
        bpy.context.view_layer.update()

        check('missing HDRI preserves selected intent', settings.world_preset == selected,
              settings.world_preset)
        check('missing HDRI is never assigned as a supposedly valid image', env.image is None)
        check('missing HDRI uses Physical Sky illumination fallback',
              linked_node(mix.inputs[1]) == nodes.get('AWFUL_BG_NISHITA_DAY'),
              linked_node(mix.inputs[1]).name if linked_node(mix.inputs[1]) else None)
        check('missing HDRI uses Physical Sky camera fallback',
              linked_node(mix.inputs[2]) == nodes.get('AWFUL_CAMERA_BG_NISHITA_DAY'),
              linked_node(mix.inputs[2]).name if linked_node(mix.inputs[2]) else None)

        # Bulk workflow is proven without performing real network I/O.
        reviewed = workflow.reviewed_hdri_records()
        expected_urls = {record['download_url'] for record in reviewed}
        calls = []
        original_fetch = cache.fetch

        def fake_fetch(url, destination, force=False):
            REPORT['network_attempts'] += 1
            calls.append({
                'url': str(url),
                'path': str(destination),
                'force': bool(force),
            })
            return True

        cache.fetch = fake_fetch
        selected_before_download = settings.world_preset
        try:
            result = legacy.ensure_assets(True)
        finally:
            cache.fetch = original_fetch

        check('Download All requests every reviewed HDRI exactly once',
              len(calls) == len(reviewed) == 5,
              {'calls': calls, 'reviewed': len(reviewed)})
        check('Download All requests exactly provenance-reviewed URLs',
              {call['url'] for call in calls} == expected_urls,
              {'actual': sorted(call['url'] for call in calls),
               'expected': sorted(expected_urls)})
        check('bulk result reports every reviewed HDRI',
              len(result) == 5 and all(result.values()), result)
        check('bulk download never switches selected environment',
              settings.world_preset == selected_before_download,
              {'before': selected_before_download, 'after': settings.world_preset})

        # Strict provenance redirect behavior stays in place until real evidence says otherwise.
        cache_source = Path(cache.__file__).read_text(encoding='utf-8')
        check('unreviewed redirects remain rejected',
              'Unexpected asset redirect; review the curated source' in cache_source)

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'asset_workflow.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL asset workflow runtime contract failed')


if __name__ == '__main__':
    main()
