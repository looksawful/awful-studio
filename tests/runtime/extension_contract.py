"""Real Blender-only assertions. No renders; no source checkout import of the Extension."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import platform
import socket
import sys
import time
import traceback

import bpy
import addon_utils

MODULE = 'bl_ext.awful_test.awful_studio'
REPORT = {'status': 'failed', 'checks': [], 'operations': [], 'blender': bpy.app.version_string,
          'platform': platform.platform(), 'python': sys.version}


def check(name, condition):
    REPORT['checks'].append({'name': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)


def freeze():
    return {'objects': [(o.name, o.type, tuple(round(v, 6) for row in o.matrix_world for v in row),
                         o.parent.name if o.parent else None) for o in bpy.data.objects],
            'counts': {g: len(getattr(bpy.data, g)) for g in
                       ('objects', 'collections', 'materials', 'meshes', 'cameras', 'lights', 'worlds', 'actions', 'node_groups', 'images')},
            'world': bpy.context.scene.world.name if bpy.context.scene.world else None,
            'camera': bpy.context.scene.camera.name if bpy.context.scene.camera else None,
            'engine': bpy.context.scene.render.engine,
            'frame': bpy.context.scene.frame_current}


def measured(name, function):
    started = time.perf_counter()
    result = function()
    REPORT['operations'].append({'operation': name, 'wall_seconds': time.perf_counter()-started,
                                 'counts': freeze()['counts']})
    return result


def cancelled_operator(function):
    """Normalize Blender's two Python forms of an operator reporting ERROR+CANCELLED."""
    try:
        return function()
    except RuntimeError:
        return {'CANCELLED'}


def block_network():
    def blocked(*args, **kwargs):
        REPORT['network_attempts'] = REPORT.get('network_attempts', 0) + 1
        raise OSError('Network forbidden in the offline runtime contract')
    socket.create_connection = blocked
    socket.socket.connect = blocked


def install(args):
    before = freeze()
    repos = bpy.context.preferences.extensions.repos
    repos.new(name='AWFUL Runtime Test', module='awful_test',
              custom_directory=str(args.work / 'installed'), remote_url='', source='USER')
    result = bpy.ops.extensions.package_install_files(filepath=str(args.zip), repo='awful_test', enable_on_install=False)
    check('install final ZIP', result == {'FINISHED'})
    check('install preserves scene', before == freeze())
    measured('register', lambda: addon_utils.enable(MODULE, default_set=True))
    check('enabled', addon_utils.check(MODULE)[1])
    check('enable preserves scene', before == freeze())
    ext = importlib.import_module(MODULE)
    check('running installed package', str(args.work / 'installed') in ext.__file__)
    handlers = {name: len(getattr(bpy.app.handlers, name)) for name in ('load_post', 'depsgraph_update_post', 'frame_change_post')}
    for i in range(2):
        addon_utils.disable(MODULE, default_set=True)
        check(f'disable {i} removes RNA', not hasattr(bpy.types.Scene, 'awful_studio'))
        check(f'disable {i} preserves scene', before == freeze())
        addon_utils.enable(MODULE, default_set=True)
        check(f're-enable {i}', addon_utils.check(MODULE)[1] and before == freeze())
    check('no handler accumulation', handlers == {n: len(getattr(bpy.app.handlers, n)) for n in handlers})
    bpy.ops.wm.save_userpref()
    bpy.ops.wm.save_as_mainfile(filepath=str(args.work / 'ordinary.blend'))
    scene = bpy.context.scene
    original_world = scene.world
    original_camera = scene.camera
    user = bpy.data.objects['Cube']
    user.location = (9.25, 2.5, 1.5)
    user['awful_role'] = 'CYC'  # A role alone is not ownership.
    mat = bpy.data.materials.new('MAT_Cyclorama')
    mat.use_nodes = True
    mat.node_tree.nodes.new('ShaderNodeValue').outputs[0].default_value = 0.123
    user.data.materials.append(mat)
    user_matrix = user.matrix_world.copy()
    check('Build Studio explicit', measured('initial_build', bpy.ops.awful.build_studio) == {'FINISHED'})
    check('managed studio exists', ext.legacy.REG.object('CYC') is not None)
    check('ownership tagged objects', all(o.get('awful_owner') for o in scene.objects if o.get('awful_managed')))
    check('schema persisted', scene.awful_state.schema_version == 1)
    check('native user material preserved', len(mat.node_tree.nodes) == 3 and not mat.get('awful_managed'))
    check('world preserved', original_world.name in bpy.data.worlds)
    ext.legacy.validate_built_scene(scene)
    counts = freeze()['counts']
    for i in range(3):
        check(f'rebuild {i}', measured('rebuild', bpy.ops.awful.rebuild_studio) == {'FINISHED'})
        check(f'rebuild {i} bounded datablocks', counts == freeze()['counts'])
        generated_actions = [getattr(getattr(o, 'animation_data', None), 'action', None)
                             for o in scene.objects if ext.ownership.owned(o, scene)]
        generated_actions = [a for a in generated_actions if a]
        check(f'rebuild {i} generated actions owned',
              all(ext.ownership.owned(a, scene) for a in generated_actions))

    # A foreign-scene-only child parented to an owned object must make destructive
    # cleanup refuse the operation rather than silently mutate the other scene.
    foreign_scene = bpy.data.scenes.new('ForeignScene')
    foreign_child = bpy.data.objects.new('ForeignSceneChild', None)
    foreign_scene.collection.objects.link(foreign_child)
    foreign_parent = ext.legacy.REG.object('CYC')
    foreign_child.parent = foreign_parent
    foreign_matrix = foreign_child.matrix_world.copy()
    check('cross-scene remove refused', cancelled_operator(bpy.ops.awful.remove_studio) == {'CANCELLED'})
    check('foreign scene child parent preserved', foreign_child.parent == foreign_parent)
    check('foreign scene child transform preserved',
          all(abs(a-b) < 1e-5 for ra, rb in zip(foreign_child.matrix_world, foreign_matrix) for a,b in zip(ra,rb)))
    foreign_child.parent = None
    bpy.data.objects.remove(foreign_child, do_unlink=True)
    bpy.data.scenes.remove(foreign_scene)

    # Unmanaged objects and nested collections inside owned containers must survive removal.
    child = bpy.data.objects.new('UserInsideAwful', None)
    ext.legacy.REG.collection('COL_PRODUCT').objects.link(child)
    child.parent = ext.legacy.REG.object('PRODUCT_CONTENT')
    nested = bpy.data.collections.new('UserNestedCollection')
    ext.legacy.REG.collection('ROOT').children.link(nested)
    nested_obj = bpy.data.objects.new('UserNestedObject', None)
    nested.objects.link(nested_obj)
    child.location = (0.15, 0.25, 0.35)
    bpy.context.view_layer.update()
    child_matrix = child.matrix_world.copy()
    check('rebuild nested user data', bpy.ops.awful.rebuild_studio() == {'FINISHED'})
    check('nested user objects survive', child.name in scene.objects and nested_obj.name in scene.objects)
    check('nested collection survives', nested.name in bpy.data.collections)
    check('nested child transform preserved', all(abs(a-b) < 1e-5 for ra, rb in zip(child.matrix_world, child_matrix) for a,b in zip(ra,rb)))
    check('original user object preserved', user.name in scene.objects)
    # Reusing a generated material on a user object must not authorize its deletion/reset.
    shared = ext.legacy.REG.material('MAT_CYC')
    user.data.materials.append(shared)
    shared.diffuse_color = (0.13, 0.24, 0.35, 1)
    check('rebuild shared material', bpy.ops.awful.rebuild_studio() == {'FINISHED'})
    check('shared generated material survives', shared.name in bpy.data.materials and abs(shared.diffuse_color[0] - 0.13) < 1e-6)
    check('retained shared material transferred to user ownership',
          not shared.get('awful_managed') and not shared.get('awful_owner'))
    check('world/cameras/lights', scene.world is not None and scene.camera is not None and len(bpy.data.lights) > 1)
    check('post off by default', not scene.get('awful_post_pipeline_enabled'))
    check('no eager volumes', not any(o.type == 'VOLUME' for o in scene.objects))
    # Presets + unavailable optional assets exercise fallback under a forbidden network.
    for pid in ('COMMERCIAL_3LIGHT',):
        measured('lighting_preset', lambda: ext.legacy.apply_lighting_preset(scene, pid, False, False))
    scene.awful_studio.natural_light_enabled = True
    for pid in ext.legacy.WORLD_PRESET_ORDER:
        measured('environment_preset', lambda: ext.legacy.apply_environment_preset(scene, pid, True))
    check('offline operation made no network attempt', REPORT.get('network_attempts', 0) == 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.work / 'studio.blend'))
    before = freeze()
    addon_utils.disable(MODULE, default_set=True)
    check('disable built scene preserves content', before == freeze())
    addon_utils.enable(MODULE, default_set=True)
    check('re-enable built scene preserves content', before == freeze())
    bpy.ops.wm.save_userpref()
    check('remove studio', bpy.ops.awful.remove_studio() == {'FINISHED'})
    check('remove preserves user nested content', child.name in scene.objects and nested_obj.name in scene.objects)
    check('remove restores original world and camera', scene.world == original_world and scene.camera == original_camera)
    check('retained shared material stays user-owned after remove',
          shared.name in bpy.data.materials and not shared.get('awful_managed') and not shared.get('awful_owner'))
    check('remove clears managed scene objects', not any(ext.ownership.owned(o, scene) for o in scene.objects))


def reopen(args):
    check('enabled after process restart', addon_utils.check(MODULE)[1])
    check('startup no auto-build', len(bpy.data.objects) == 3)
    bpy.ops.wm.open_mainfile(filepath=str(args.work / 'ordinary.blend'), use_scripts=False)
    check('ordinary file no auto-build', len(bpy.data.objects) == 3)
    bpy.ops.wm.open_mainfile(filepath=str(args.work / 'studio.blend'), use_scripts=False)
    ext = importlib.import_module(MODULE)
    check('reopened current schema', bpy.context.scene.awful_state.schema_version == 1)
    ext.legacy.validate_built_scene(bpy.context.scene)
    check('registry resolves reopened scene', ext.legacy.REG.object('CYC') is not None)
    check('reopened studio rebuild', bpy.ops.awful.rebuild_studio() == {'FINISHED'})
    # Unknown future schemas refuse changes.
    bpy.context.scene.awful_state.schema_version = 999
    before = freeze()
    result = cancelled_operator(bpy.ops.awful.rebuild_studio)
    check('future schema rejected without mutation', result == {'CANCELLED'} and freeze() == before)


def historical(args):
    import types
    source = args.source
    check('historical SHA256', hashlib.sha256(source.read_bytes()).hexdigest() ==
          '5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b')
    mod = types.ModuleType('awful_historical_fixture')
    mod.__file__ = str(source)
    sys.modules[mod.__name__] = mod
    exec(compile(source.read_text(), str(source), 'exec'), mod.__dict__)
    mod.register()
    # Historical downloads are intentionally denied, not patched into the source.
    mod.build_studio(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.work / 'historical.blend'))
    check('historical real scene built', any(o.get('awful_managed') for o in bpy.data.objects))


def migrate(args):
    check('enabled for migration', addon_utils.check(MODULE)[1])
    bpy.ops.wm.open_mainfile(filepath=str(args.work / 'historical.blend'), use_scripts=False)
    before = freeze()
    check('historical file not automatically rebuilt', bpy.context.scene.awful_state.schema_version == 0)
    check('explicit historical migration', bpy.ops.awful.migrate_scene() == {'FINISHED'})
    check('metadata migration preserves physical scene', freeze() == before)
    check('migrated schema', bpy.context.scene.awful_state.schema_version == 1)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.work / 'migrated.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(args.work / 'migrated.blend'), use_scripts=False)
    check('migrated file reopened', bpy.context.scene.awful_state.schema_version == 1)
    check('migrated scene can rebuild', bpy.ops.awful.rebuild_studio() == {'FINISHED'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('install', 'reopen', 'historical', 'migrate'), required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.work.mkdir(parents=True, exist_ok=True)
    try:
        check('Blender 5.2 runtime', bpy.app.version[:2] == (5, 2))
        block_network()
        globals()[args.phase](args)
        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / f'{args.phase}.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
    if REPORT['status'] != 'passed':
        raise RuntimeError(f'AWFUL {args.phase} runtime contract failed')


if __name__ == '__main__':
    main()
