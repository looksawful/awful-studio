"""Blender 5.2 runtime contract for P0 cyclorama and studio architecture."""
import argparse
import importlib
import json
from pathlib import Path
import platform
import sys
import traceback

import bpy
import addon_utils

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


def counts():
    return {name: len(getattr(bpy.data, name)) for name in
            ('objects', 'collections', 'materials', 'meshes', 'cameras',
             'lights', 'worlds', 'actions', 'node_groups', 'images')}


def role_objects(legacy, role):
    return [obj for obj in bpy.data.objects
            if legacy.is_managed(obj) and obj.get(legacy.ROLE_KEY, '') == role]


def principled(material):
    if material is None or not material.use_nodes:
        return None
    return next((node for node in material.node_tree.nodes
                 if node.type == 'BSDF_PRINCIPLED'), None)


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
        settings = scene.awful_studio

        required_props = (
            'cyclorama_distance_m', 'cyclorama_look', 'cyclorama_finish',
            'show_cyclorama', 'show_walls', 'show_floor', 'show_ceiling',
            'show_door', 'show_window_frame', 'show_window_glass',
        )
        for name in required_props:
            check(f'workflow property registered: {name}', hasattr(settings, name))

        required_roles = (
            'CYC', 'ARCH_FLOOR_VISIBLE', 'DOOR_FRAME', 'DOOR_LEAF',
            'ROOM_CEILING', 'WINDOW_FRAME', 'WINDOW_GLASS', 'ROOM_FLOOR',
        )
        for role in required_roles:
            check(f'managed role exists: {role}', bool(role_objects(legacy, role)), role)

        cyc = legacy.REG.require_object('CYC')
        mat = legacy.REG.material('MAT_CYC')
        check('cyclorama material exists', mat is not None)
        shader = principled(mat)
        check('cyclorama principled exists', shader is not None)

        inventory = counts()
        settings.cyclorama_distance_m = 3.5
        bpy.context.view_layer.update()
        check('metric distance stored', abs(float(settings.cyclorama_distance_m) - 3.5) < 1e-6,
              float(settings.cyclorama_distance_m))
        check('metric distance applied to scene',
              abs(float(scene['awful_cyclorama_distance_m']) - 3.5) < 1e-6,
              float(scene.get('awful_cyclorama_distance_m', -1.0)))
        check('distance update datablock bounded', counts() == inventory, counts())

        material_id = mat.as_pointer()
        for look in ('WHITE', 'BLACK', 'CHROMA_GREEN'):
            for finish in ('MATTE', 'MEDIUM', 'GLOSSY'):
                settings.cyclorama_look = look
                settings.cyclorama_finish = finish
                bpy.context.view_layer.update()
                current = legacy.REG.material('MAT_CYC')
                check(f'material reused: {look}/{finish}', current.as_pointer() == material_id)
                check(f'style bounded: {look}/{finish}', counts() == inventory, counts())

        visible_floor = role_objects(legacy, 'ARCH_FLOOR_VISIBLE')[0]
        bounce_floor = role_objects(legacy, 'ROOM_FLOOR')[0]
        check('visible floor separate from bounce floor', visible_floor != bounce_floor)
        check('visible floor camera-visible by default', bool(visible_floor.visible_camera))
        check('bounce floor camera-hidden', not bool(bounce_floor.visible_camera))

        walls = []
        for role in ext.studio_geometry.ARCHITECTURE_ROLE_GROUPS['WALLS']:
            walls.extend(role_objects(legacy, role))
        check('visible wall group exists', bool(walls))

        bpy.ops.mesh.primitive_cube_add(size=0.25, location=(4.5, -4.0, 0.5))
        foreign = bpy.context.object
        foreign.name = 'USER_RoleCollision'
        foreign[legacy.ROLE_KEY] = 'ROOM_CEILING'
        foreign_before = (foreign.hide_viewport, bool(foreign.visible_camera))

        settings.show_floor = True
        settings.show_walls = True
        settings.show_ceiling = True
        settings.show_door = True
        settings.show_window_frame = True
        settings.show_cyclorama = True
        bpy.context.view_layer.update()

        settings.show_walls = False
        bpy.context.view_layer.update()
        check('walls hidden independently', all(o.hide_viewport and not o.visible_camera for o in walls))
        check('floor unaffected by wall toggle', not visible_floor.hide_viewport and visible_floor.visible_camera)
        check('foreign colliding role untouched',
              (foreign.hide_viewport, bool(foreign.visible_camera)) == foreign_before)

        settings.show_walls = True
        settings.show_floor = False
        bpy.context.view_layer.update()
        check('visible floor hidden independently', visible_floor.hide_viewport and not visible_floor.visible_camera)
        check('bounce floor remains physical', not bounce_floor.hide_render)

        settings.show_floor = True
        settings.show_cyclorama = False
        bpy.context.view_layer.update()
        check('cyclorama hidden independently', cyc.hide_viewport and not cyc.visible_camera)
        check('visible floor survives cyclorama toggle', not visible_floor.hide_viewport and visible_floor.visible_camera)

        settings.show_cyclorama = True
        before_repeat = counts()
        for _ in range(3):
            settings.cyclorama_distance_m = 3.2
            settings.cyclorama_look = 'WHITE'
            settings.cyclorama_finish = 'MATTE'
            settings.show_door = not settings.show_door
            settings.show_door = not settings.show_door
        bpy.context.view_layer.update()
        check('repeated studio state bounded', counts() == before_repeat, counts())

        REPORT['status'] = 'passed'
    except Exception:
        REPORT['traceback'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        (args.work / 'studio_geometry.json').write_text(
            json.dumps(REPORT, indent=2), encoding='utf-8')

    if REPORT['status'] != 'passed':
        raise RuntimeError('AWFUL studio geometry runtime contract failed')


if __name__ == '__main__':
    main()
