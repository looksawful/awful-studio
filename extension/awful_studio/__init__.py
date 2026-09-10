# SPDX-License-Identifier: GPL-3.0-or-later
"""AWFUL STUDIO Extension lifecycle. Import/register never read or mutate a scene."""
import time
import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty, PointerProperty, EnumProperty
from . import ownership, migrations, asset_cache
from .core import legacy

VERSION = (0, 0, 16)
_registered = []


class AWFUL_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    asset_cache_path: StringProperty(name='Asset Cache Directory', subtype='DIR_PATH')
    allow_network_assets: BoolProperty(name='Allow Network Assets', default=False)
    diagnostics: BoolProperty(name='Diagnostics', default=False)

    def draw(self, context):
        self.layout.label(text='AWFUL STUDIO 0.0.16 — Blender 5.2 LTS')
        self.layout.prop(self, 'asset_cache_path')
        self.layout.prop(self, 'allow_network_assets')
        self.layout.prop(self, 'diagnostics')
        self.layout.operator('awful.clear_asset_cache')
        op = self.layout.operator('wm.url_open', text='Documentation')
        op.url = 'https://github.com/looksawful/awful-studio'


class AWFUL_SceneState(bpy.types.PropertyGroup):
    schema_version: IntProperty(default=0, min=0)
    owner_id: StringProperty()
    built: BoolProperty(default=False)
    previous_world: PointerProperty(type=bpy.types.World)
    previous_camera: PointerProperty(type=bpy.types.Object)
    last_operation: StringProperty()
    last_error: StringProperty()


def _detach_non_product_children():
    """Keep unrelated user objects safe without treating them as mounted products."""
    content = legacy.REG.object('PRODUCT_CONTENT')
    if content is None:
        return
    for child in list(content.children):
        if legacy.is_managed(child):
            continue
        hierarchy = [child] + legacy.descendants(child)
        if legacy.world_bbox(hierarchy) is None:
            legacy.parent_keep_world(child, None)


def run_build(context):
    scene = context.scene
    migrations.migration_path(scene.awful_state.schema_version)
    ownership.initialize(scene)
    started = time.perf_counter()
    try:
        with ownership.for_scene(scene):
            _detach_non_product_children()
            legacy.build_studio(True)
            ownership.mark_generated_actions(scene)
        scene.awful_state.schema_version = migrations.CURRENT_SCHEMA
        scene.awful_state.built = True
        scene.awful_state.last_error = ''
    except Exception as exc:
        scene.awful_state.last_error = str(exc)
        raise
    finally:
        scene.awful_state.last_operation = f'build: {time.perf_counter()-started:.6f}s'


class AWFUL_OT_Build(bpy.types.Operator):
    bl_idname = 'awful.build_studio'
    bl_label = 'Build Studio'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and legacy.REG.object('CYC') is None

    def execute(self, context):
        try:
            run_build(context)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class AWFUL_OT_Rebuild(bpy.types.Operator):
    bl_idname = 'awful.rebuild_studio'
    bl_label = 'Rebuild Managed Studio'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and legacy.REG.object('CYC') is not None

    def execute(self, context):
        try:
            run_build(context)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class AWFUL_OT_Remove(bpy.types.Operator):
    bl_idname = 'awful.remove_studio'
    bl_label = 'Remove AWFUL Studio'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and bool(context.scene.awful_state.owner_id)

    def execute(self, context):
        try:
            ownership.remove(context.scene)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class AWFUL_OT_ResetSystem(bpy.types.Operator):
    bl_idname = 'awful.reset_system'
    bl_label = 'Reset Selected System Preset'
    bl_options = {'REGISTER', 'UNDO'}
    system: EnumProperty(items=[('LIGHTING', 'Lighting', ''), ('CAMERA', 'Camera', ''),
                                ('PRODUCT', 'Product', ''), ('ENVIRONMENT', 'Environment', '')])

    @classmethod
    def poll(cls, context):
        return context.scene is not None and legacy.REG.object('CYC') is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        s = scene.awful_studio
        with ownership.for_scene(scene):
            if self.system == 'LIGHTING':
                legacy.apply_lighting_preset(scene, s.studio_light_preset, False, False)
            elif self.system == 'CAMERA':
                legacy.apply_camera_motion(scene, s.camera_motion)
            elif self.system == 'PRODUCT':
                legacy.apply_product_motion(scene, s.product_motion)
            else:
                legacy.apply_environment_preset(scene, s.world_preset, True)
            ownership.mark_generated_actions(scene)
        return {'FINISHED'}


class AWFUL_OT_Migrate(bpy.types.Operator):
    bl_idname = 'awful.migrate_scene'
    bl_label = 'Upgrade Historical AWFUL Scene'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            with ownership.for_scene(context.scene):
                migrations.migrate(context.scene)
        except (ValueError, RuntimeError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class AWFUL_OT_ClearCache(bpy.types.Operator):
    bl_idname = 'awful.clear_asset_cache'
    bl_label = 'Clear Downloaded Asset Cache'

    def execute(self, context):
        self.report({'INFO'}, f'Removed {asset_cache.clear()} cached assets')
        return {'FINISHED'}


CLASSES = (AWFUL_AddonPreferences, AWFUL_SceneState, *legacy.CLASSES,
           AWFUL_OT_Build, AWFUL_OT_Rebuild, AWFUL_OT_Remove, AWFUL_OT_ResetSystem,
           AWFUL_OT_Migrate, AWFUL_OT_ClearCache)


def register():
    if _registered:
        return
    if hasattr(bpy.types.Scene, 'awful_studio') or hasattr(bpy.types.Scene, 'awful_state'):
        raise RuntimeError('Disable the historical AWFUL script/add-on before enabling this Extension')
    try:
        for cls in CLASSES:
            bpy.utils.register_class(cls)
            _registered.append(cls)
        bpy.types.Scene.awful_studio = PointerProperty(type=legacy.AWFUL_StudioSettings)
        bpy.types.Scene.awful_state = PointerProperty(type=AWFUL_SceneState)
    except Exception:
        unregister()
        raise


def unregister():
    if not _registered:
        return
    for attr in ('awful_state', 'awful_studio'):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
    for cls in reversed(_registered):
        bpy.utils.unregister_class(cls)
    _registered.clear()
