"""Blender 5.2 runtime contract for read-only AWFUL diagnostics."""
import argparse
import importlib
import json
from pathlib import Path
import platform
import socket
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
    'network_attempts': 0,
    'render_tests': False,
}


def check(name, condition, value=None):
    REPORT['checks'].append({
        'name': name,
        'passed': bool(condition),
        'value': value,
    })
    if not condition:
        raise AssertionError(name)


def datablock_counts():
    return {
        'objects': len(bpy.data.objects),
        'collections': len(bpy.data.collections),
        'materials': len(bpy.data.materials),
        'images': len(bpy.data.images),
        'actions': len(bpy.data.actions),
        'node_groups': len(bpy.data.node_groups),
    }


def guard_network():
    original_create = socket.create_connection
    original_connect = socket.socket.connect

    def blocked(*args, **kwargs):
        REPORT['network_attempts'] += 1
        raise RuntimeError('Network access blocked by diagnostics contract')

    socket.create_connection = blocked
    socket.socket.connect = blocked
    return original_create, original_connect


def restore_network(originals):
    socket.create_connection, socket.socket.connect = originals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)

    originals = None
    try:
        check(
            'Blender 5.2 runtime',
            bpy.app.version[:2] == (5, 2),
            bpy.app.version_string,
        )
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        check('extension enabled', addon_utils.check(MODULE)[1])

        bpy.ops.wm.open_mainfile(
            filepath=str(args.work / 'studio.blend'),
            use_scripts=False,
        )
        ext = importlib.import_module(MODULE)
        workflow = importlib.import_module(MODULE + '.workflow_ui')
        diagnostics = importlib.import_module(MODULE + '.studio_diagnostics')
        scene = bpy.context.scene

        before = datablock_counts()
        originals = guard_network()
        items = workflow.run_diagnostics(ext.legacy, scene)
        after = datablock_counts()

        summary = diagnostics.summarize(items)
        check(
            'fresh studio diagnostics have no ERROR',
            summary['ERROR'] == 0,
            summary,
        )
        check(
            'diagnostics preserve datablock counts',
            after == before,
            {'before': before, 'after': after},
        )
        check(
            'diagnostics make zero network attempts',
            REPORT['network_attempts'] == 0,
            REPORT['network_attempts'],
        )
        check(
            'diagnostics record validation operation',
            str(scene.awful_state.last_operation).startswith('validate:'),
            scene.awful_state.last_operation,
        )

        REPORT['summary'] = summary
        REPORT['diagnostics'] = [item._asdict() for item in items]
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        if originals is not None:
            restore_network(originals)
        (args.work / 'diagnostics.json').write_text(
            json.dumps(REPORT, indent=2),
            encoding='utf-8',
        )

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL diagnostics runtime contract failed')


if __name__ == '__main__':
    main()
