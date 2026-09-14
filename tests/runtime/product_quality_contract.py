"""Blender 5.2 runtime contract for AWFUL Product Quality mockups."""
import argparse
import importlib
import json
import math
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
    'render_tests': False,
    'network_attempts': 0,
}


def check(name, condition, value=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'value': value})
    if not condition:
        raise AssertionError(name)


def dimensions(bbox):
    minimum, maximum = bbox
    return tuple(float(maximum[index] - minimum[index]) for index in range(3))


def managed_mockup_counts(legacy, ownership, scene):
    objects = [
        obj for obj in scene.objects
        if ownership.owned(obj, scene)
        and (obj.get(legacy.ROLE_KEY, '') == 'MOCKUP_ROOT'
             or str(obj.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_'))
    ]
    meshes = [
        mesh for mesh in bpy.data.meshes
        if ownership.owned(mesh, scene)
        and str(mesh.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_')
    ]
    materials = [
        material for material in bpy.data.materials
        if ownership.owned(material, scene)
        and str(material.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_MAT_')
    ]
    return {'objects': len(objects), 'meshes': len(meshes), 'materials': len(materials)}


def datablock_counts():
    return {name: len(getattr(bpy.data, name)) for name in
            ('objects', 'collections', 'meshes', 'materials', 'actions', 'cameras', 'lights')}


def metric_tuple(scene):
    return tuple(float(scene[f'awful_product_{name}']) for name in ('width', 'depth', 'height', 'scale'))


def block_network():
    def blocked(*args, **kwargs):
        REPORT['network_attempts'] += 1
        raise OSError('Network forbidden in product-quality runtime contract')
    socket.create_connection = blocked
    socket.socket.connect = blocked


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
        block_network()

        ext = importlib.import_module(MODULE)
        legacy = ext.legacy
        ownership = ext.ownership
        product_quality = importlib.import_module(MODULE + '.product_quality')
        scene = bpy.context.scene
        scene.awful_studio.auto_fit = False

        check('product-quality Blender adapter exists',
              callable(getattr(product_quality, 'replace_mockup', None)))
        check('device screen path property registered',
              hasattr(scene.awful_studio, 'device_screen_path'))
        check('device hinge preset property registered',
              hasattr(scene.awful_studio, 'device_hinge_preset'))

        for key in product_quality.mockup_keys():
            spec = product_quality.mockup_spec(key)
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
            check(f'{key} root is scene-owned', ownership.owned(root, scene))
            check(f'{key} root role', root.get(legacy.ROLE_KEY) == 'MOCKUP_ROOT',
                  root.get(legacy.ROLE_KEY))
            check(f'{key} metadata key', product_quality.mockup_key(root) == key)
            stored = tuple(float(value) for value in root['awful_mockup_source_dimensions_m'])
            check(f'{key} source dimensions metadata', stored == tuple(spec['dimensions_m']), stored)

            hierarchy = [root] + legacy.descendants(root)
            meshes = [obj for obj in hierarchy if obj.type == 'MESH']
            check(f'{key} has bounded mesh parts',
                  1 <= len(meshes) <= int(spec['max_mesh_parts']), len(meshes))
            bbox = legacy.world_bbox(meshes)
            check(f'{key} has measurable geometry', bbox is not None)
            measured = dimensions(bbox)
            expected = tuple(float(value) for value in spec['dimensions_m'])
            relative_error = [abs(a - b) / max(b, 1e-9) for a, b in zip(measured, expected)]
            check(f'{key} geometry keeps source scale', max(relative_error) < 0.08,
                  {'measured': measured, 'expected': expected, 'relative_error': relative_error})

            primary = next((obj for obj in meshes if obj.get('awful_mockup_primary')), None)
            check(f'{key} has primary mesh', primary is not None)
            material_roles = [material.get(legacy.ROLE_KEY, '') for material in primary.data.materials]
            expected_roles = [f"MOCKUP_MAT_{spec['slot_materials'][slot]}"
                              for slot in spec['material_slots']]
            check(f'{key} material slots are deterministic', material_roles == expected_roles,
                  {'actual': material_roles, 'expected': expected_roles})

            bevels = [modifier for obj in meshes for modifier in obj.modifiers
                      if modifier.type == 'BEVEL']
            check(f'{key} bevel complexity bounded',
                  all(int(modifier.segments) <= int(spec['bevel_segments']) for modifier in bevels),
                  [int(modifier.segments) for modifier in bevels])

        device_asset_loader = importlib.import_module(MODULE + '.device_asset_loader')
        screen_path = args.work / 'device_screen_test.png'
        generated_screen = bpy.data.images.new('AWFUL_RUNTIME_SCREEN_ART', width=2, height=2)
        generated_screen.generated_color = (0.9, 0.1, 0.2, 1.0)
        generated_screen.filepath_raw = str(screen_path)
        generated_screen.file_format = 'PNG'
        generated_screen.save()
        bpy.data.images.remove(generated_screen)
        scene.awful_studio.auto_fit = True
        for key in device_asset_loader.device_asset_keys():
            spec = device_asset_loader.device_asset_spec(key)
            scene.awful_studio.product_mockup = key
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
            check(f'{key} root is scene-owned', ownership.owned(root, scene))
            check(f'{key} root role', root.get(legacy.ROLE_KEY) == 'MOCKUP_ROOT')
            check(f'{key} metadata key', product_quality.mockup_key(root) == key)
            check(f'{key} asset id', root.get('awful_asset_id') == spec['asset_id'])
            check(f'{key} stage is honest', root.get('awful_asset_stage') == spec['stage'])
            check(f'{key} variant', root.get('awful_asset_variant') == spec['variant'])
            hierarchy = [root] + legacy.descendants(root)
            meshes = [obj for obj in hierarchy if obj.type == 'MESH']
            check(f'{key} has measurable meshes', bool(meshes) and legacy.world_bbox(meshes) is not None)
            check(f'{key} hierarchy is owned', all(ownership.owned(obj, scene) for obj in hierarchy))
            check(f'{key} excludes preview cameras', all(obj.type != 'CAMERA' for obj in hierarchy))
            check(f'{key} excludes preview lights', all(obj.type != 'LIGHT' for obj in hierarchy))
            check(f'{key} has screen content', any(obj.name.startswith('SCREEN_CONTENT') for obj in hierarchy))
            screen = device_asset_loader.apply_screen_image(legacy, scene, screen_path)
            check(f'{key} screen object selected', screen.name.startswith('SCREEN_CONTENT'), screen.name)
            screen_material = next((m for m in screen.data.materials if m is not None), None)
            check(f'{key} screen material exists', screen_material is not None)
            image_node = screen_material.node_tree.nodes.get('AWFUL_SCREEN_IMAGE')
            check(f'{key} screen image node exists', image_node is not None)
            check(f'{key} screen image is packed',
                  image_node is not None and image_node.image is not None and image_node.image.packed_file is not None)
            check(f'{key} screen artwork metadata',
                  root.get('awful_screen_artwork_name') == screen_path.name,
                  root.get('awful_screen_artwork_name'))
            scene.awful_studio.device_screen_path = str(screen_path)
            screen_op = bpy.ops.awful.apply_device_screen()
            check(f'{key} Apply Screen operator finishes', screen_op == {'FINISHED'}, list(screen_op))
            managed_screen_images = [img for img in bpy.data.images
                                     if ownership.owned(img, scene)
                                     and str(img.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_DEVICE_SCREEN_IMAGE_')]
            check(f'{key} repeated screen apply keeps one managed image',
                  len(managed_screen_images) == 1,
                  [img.name for img in managed_screen_images])
            metrics = legacy.get_product_metrics(scene)
            check(f'{key} Auto Fit metrics are positive',
                  min(metrics.width, metrics.depth, metrics.height, metrics.scale) > 0.0)
            if key == 'DEVICE_MACBOOK_PRO_14':
                check('MacBook bundled hinge control exists',
                      any(obj.name.startswith('CTRL_HINGE') for obj in hierarchy))
                for preset in device_asset_loader.hinge_preset_keys(key):
                    hinge = device_asset_loader.apply_hinge_preset(legacy, scene, preset)
                    angle = device_asset_loader.hinge_angle_degrees(key, preset)
                    expected_rotation = math.radians(90.0 - angle)
                    check(f'MacBook hinge preset {preset} rotation',
                          abs(float(hinge.rotation_euler.x) - expected_rotation) < 1e-6,
                          float(hinge.rotation_euler.x))
                    check(f'MacBook hinge preset {preset} metadata angle',
                          abs(float(hinge.get('open_angle_deg', -999.0)) - angle) < 1e-6,
                          hinge.get('open_angle_deg'))
                    check(f'MacBook hinge preset {preset} metadata name',
                          str(hinge.get('preset', '')) == preset,
                          hinge.get('preset'))
                scene.awful_studio.device_hinge_preset = '60'
                hinge_op = bpy.ops.awful.apply_device_hinge()
                check('MacBook Set Hinge operator finishes', hinge_op == {'FINISHED'}, list(hinge_op))
                hinge_after_op = next(obj for obj in hierarchy if obj.name.startswith('CTRL_HINGE'))
                check('MacBook Set Hinge operator applies selected preset',
                      abs(float(hinge_after_op.get('open_angle_deg', -999.0)) - 60.0) < 1e-6)
        scene.awful_studio.product_mockup = 'DEVICE_MACBOOK_PRO_14'
        rebuild = bpy.ops.awful.rebuild_studio()
        check('device rebuild finishes', rebuild == {'FINISHED'}, list(rebuild))
        restored = product_quality.mockup_roots(legacy, scene)
        check('device rebuild restores selected asset',
              len(restored) == 1 and product_quality.mockup_key(restored[0]) == 'DEVICE_MACBOOK_PRO_14')
        restored_hierarchy = [restored[0]] + legacy.descendants(restored[0])
        check('device rebuild restores hinge control',
              any(obj.name.startswith('CTRL_HINGE') for obj in restored_hierarchy))
        rebuilt_screen = next(obj for obj in restored_hierarchy if obj.name.startswith('SCREEN_CONTENT'))
        rebuilt_screen_material = next((m for m in rebuilt_screen.data.materials if m is not None), None)
        rebuilt_image_node = (rebuilt_screen_material.node_tree.nodes.get('AWFUL_SCREEN_IMAGE')
                              if rebuilt_screen_material is not None else None)
        check('device rebuild preserves selected screen artwork',
              restored[0].get('awful_screen_artwork_name') == screen_path.name
              and rebuilt_image_node is not None
              and rebuilt_image_node.image is not None
              and rebuilt_image_node.image.packed_file is not None)
        rebuilt_hinge = next(obj for obj in restored_hierarchy if obj.name.startswith('CTRL_HINGE'))
        check('device rebuild preserves selected hinge preset',
              str(rebuilt_hinge.get('preset', '')) == '60'
              and abs(float(rebuilt_hinge.get('open_angle_deg', -999.0)) - 60.0) < 1e-6)
        scene.awful_studio.auto_fit = False
        scene.awful_studio.product_mockup = 'BOTTLE'
        with ownership.for_scene(scene):
            product_quality.replace_mockup(legacy, scene, 'BOTTLE')
        stale = [c.name for c in bpy.data.collections if c.name.startswith('AWFUL_DEVICE_')]
        check('device replacement purges orphan bundled collections', not stale, stale)
        stale_screen_images = [img.name for img in bpy.data.images
                               if ownership.owned(img, scene)
                               and str(img.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_DEVICE_SCREEN_IMAGE_')]
        check('device replacement purges orphan screen images',
              not stale_screen_images, stale_screen_images)

        # Explicit UI generation must never displace a measurable unmanaged product.
        check('mockup selector scene state exists', hasattr(scene.awful_studio, 'product_mockup'))
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.5))
        user_root = bpy.context.object
        user_root.name = 'USER_PRODUCT_SAFETY_FIXTURE'
        with ownership.for_scene(scene):
            legacy.mount_product([user_root], False)
        scene.awful_studio.product_mockup = 'BOTTLE'
        try:
            operator_result = bpy.ops.awful.generate_mockup()
        except RuntimeError:
            operator_result = {'CANCELLED'}
        except AttributeError:
            operator_result = {'MISSING'}
        check('unmanaged mounted product refuses mockup operator',
              operator_result == {'CANCELLED'}, list(operator_result))
        check('unmanaged mounted product survives refusal',
              user_root.name in bpy.data.objects and not ownership.owned(user_root, scene))
        check('unmanaged mounted product stays mounted after refusal',
              user_root.parent is not None
              and user_root.parent.get(legacy.ROLE_KEY, '') == 'PRODUCT_CONTENT')

        # Remove only the local test fixture, then exercise owned replacement bounds.
        user_root.parent = None
        bpy.data.objects.remove(user_root, do_unlink=True)
        before = managed_mockup_counts(legacy, ownership, scene)
        for key in ('BOTTLE', 'JAR', 'PHONE', 'BOTTLE'):
            with ownership.for_scene(scene):
                root = product_quality.replace_mockup(legacy, scene, key)
        after = managed_mockup_counts(legacy, ownership, scene)
        final_limit = int(product_quality.mockup_spec('BOTTLE')['max_mesh_parts'])
        check('repeated owned replacement keeps one mockup root',
              len(product_quality.mockup_roots(legacy, scene)) == 1)
        check('repeated owned replacement keeps mockup meshes bounded',
              after['meshes'] <= final_limit,
              {'before': before, 'after': after, 'limit': final_limit})
        check('repeated owned replacement keeps starter materials bounded',
              after['materials'] <= len(product_quality.MATERIAL_STARTERS), after)

        # A user object parented into an owned mockup makes replacement ambiguous.
        guarded_root = product_quality.mockup_roots(legacy, scene)[0]
        foreign = bpy.data.objects.new('USER_CHILD_UNDER_MOCKUP', None)
        scene.collection.objects.link(foreign)
        foreign.parent = guarded_root
        refused = False
        try:
            with ownership.for_scene(scene):
                product_quality.replace_mockup(legacy, scene, 'JAR')
        except RuntimeError:
            refused = True
        check('unmanaged child under mockup refuses replacement', refused)
        check('unmanaged child guard is mutation-free',
              foreign.name in bpy.data.objects and foreign.parent == guarded_root)
        foreign.parent = None
        bpy.data.objects.remove(foreign, do_unlink=True)

        # Explicit rebuild restores the selected AWFUL mockup, not the diagnostic fixture.
        scene.awful_studio.product_mockup = 'PHONE'
        with ownership.for_scene(scene):
            product_quality.replace_mockup(legacy, scene, 'PHONE')
        check('selected mockup exists before rebuild',
              len(product_quality.mockup_roots(legacy, scene)) == 1)
        rebuild = bpy.ops.awful.rebuild_studio()
        check('mockup rebuild finishes', rebuild == {'FINISHED'}, list(rebuild))
        restored = product_quality.mockup_roots(legacy, scene)
        check('mockup selection survives rebuild', scene.awful_studio.product_mockup == 'PHONE')
        check('selected mockup geometry restored on rebuild',
              len(restored) == 1 and product_quality.mockup_key(restored[0]) == 'PHONE',
              [product_quality.mockup_key(item) for item in restored] if restored else [])

        # Auto Fit and camera framing must work for every procedural product.
        scene.awful_studio.auto_fit = True
        envelope = legacy.STUDIO_SPEC['product_envelope']
        for key in product_quality.mockup_keys():
            scene.awful_studio.product_mockup = key
            with ownership.for_scene(scene):
                product_quality.replace_mockup(legacy, scene, key)
            metrics = legacy.get_product_metrics(scene)
            check(f'{key} Auto Fit metrics are positive',
                  min(metrics.width, metrics.depth, metrics.height, metrics.scale) > 0.0,
                  {'width': metrics.width, 'depth': metrics.depth,
                   'height': metrics.height, 'scale': metrics.scale})
            check(f'{key} Auto Fit stays inside product envelope',
                  metrics.width <= float(envelope['max_xy'])
                  and metrics.depth <= float(envelope['max_xy'])
                  and metrics.height <= float(envelope['max_height']),
                  {'width': metrics.width, 'depth': metrics.depth, 'height': metrics.height})
            legacy.apply_camera_base_pose(scene, lens=70.0, margin=1.25)
            distance = float(scene['awful_camera_base_distance'])
            check(f'{key} camera framing distance is finite and positive',
                  math.isfinite(distance) and distance > 0.0, distance)

        # Rebuild must preserve the selected mockup's Auto Fit semantics and stay bounded.
        scene.awful_studio.product_mockup = 'BOTTLE'
        with ownership.for_scene(scene):
            product_quality.replace_mockup(legacy, scene, 'BOTTLE')
        pre_rebuild_metrics = metric_tuple(scene)
        first_rebuild = bpy.ops.awful.rebuild_studio()
        check('Auto Fit mockup first rebuild finishes', first_rebuild == {'FINISHED'})
        check('Auto Fit metrics survive explicit rebuild',
              all(abs(a - b) < 1e-6 for a, b in zip(metric_tuple(scene), pre_rebuild_metrics)),
              {'before': pre_rebuild_metrics, 'after': metric_tuple(scene)})

        baseline_counts = datablock_counts()
        for index in range(3):
            result = bpy.ops.awful.rebuild_studio()
            check(f'product-quality rebuild {index} finishes', result == {'FINISHED'})
            check(f'product-quality rebuild {index} datablocks bounded',
                  datablock_counts() == baseline_counts,
                  {'baseline': baseline_counts, 'actual': datablock_counts()})

        # Selected mockup metadata and measurable geometry survive a real file restart.
        reopen_path = args.work / 'product_quality_reopen.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(reopen_path))
        bpy.ops.wm.open_mainfile(filepath=str(reopen_path), use_scripts=False)
        scene = bpy.context.scene
        check('mockup selection survives save/reopen', scene.awful_studio.product_mockup == 'BOTTLE')
        reopened = product_quality.mockup_roots(legacy, scene)
        check('one mockup root survives save/reopen', len(reopened) == 1)
        reopened_meshes = [obj for obj in [reopened[0]] + legacy.descendants(reopened[0])
                           if obj.type == 'MESH']
        check('mockup geometry measurable after save/reopen',
              legacy.world_bbox(reopened_meshes) is not None)
        scene.awful_studio.product_mockup = 'DEVICE_MACBOOK_PRO_14'
        scene.awful_studio.auto_fit = True
        with ownership.for_scene(scene):
            product_quality.replace_mockup(legacy, scene, 'DEVICE_MACBOOK_PRO_14')
        device_reopen_path = args.work / 'device_asset_reopen.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(device_reopen_path))
        bpy.ops.wm.open_mainfile(filepath=str(device_reopen_path), use_scripts=False)
        scene = bpy.context.scene
        reopened_device = product_quality.mockup_roots(legacy, scene)
        check('device selection survives save/reopen',
              scene.awful_studio.product_mockup == 'DEVICE_MACBOOK_PRO_14')
        check('one device root survives save/reopen', len(reopened_device) == 1)
        check('device metadata survives save/reopen',
              reopened_device[0].get('awful_asset_stage') == 'RELEASE_CANDIDATE')
        reopened_device_hierarchy = [reopened_device[0]] + legacy.descendants(reopened_device[0])
        check('MacBook hinge survives save/reopen',
              any(obj.name.startswith('CTRL_HINGE') for obj in reopened_device_hierarchy))

        check('product-quality operations make zero network attempts',
              REPORT['network_attempts'] == 0, REPORT['network_attempts'])

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'product_quality.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL product-quality runtime contract failed')


if __name__ == '__main__':
    main()
