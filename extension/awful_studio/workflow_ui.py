# SPDX-License-Identifier: GPL-3.0-or-later
"""Task-oriented AWFUL STUDIO N-panel workflow.

This module has no direct bpy import. Blender adapters are installed explicitly
against the retained legacy runtime before Extension class registration.
"""
from __future__ import annotations

from typing import Mapping

PANEL_ORDER = (
    'STUDIO',
    'PRODUCT',
    'LIGHTING',
    'CAMERA',
    'ENVIRONMENT',
    'OUTPUT',
    'DIAGNOSTICS',
)


def workflow_snapshot(legacy, scene) -> dict[str, object]:
    settings = scene.awful_studio
    state = scene.awful_state
    return {
        'built': legacy.REG.object('CYC') is not None,
        'product': getattr(settings, 'product_mockup', 'NONE'),
        'lighting': getattr(settings, 'studio_light_preset', 'UNKNOWN'),
        'camera': getattr(settings, 'camera_motion', 'UNKNOWN'),
        'environment': getattr(settings, 'world_preset', 'UNKNOWN'),
        'preview': getattr(settings, 'preview_mode', 'FAST'),
        'last_error': getattr(state, 'last_error', ''),
    }


def status_lines(snapshot: Mapping[str, object]) -> tuple[str, ...]:
    if snapshot.get('last_error'):
        state = 'Needs attention'
    elif snapshot.get('built'):
        state = 'Ready'
    else:
        state = 'Not built'
    return (
        f"Studio: {state}",
        f"Product: {snapshot.get('product', 'NONE')}",
        f"Lighting: {snapshot.get('lighting', 'UNKNOWN')}",
        f"Camera: {snapshot.get('camera', 'UNKNOWN')}",
        f"Environment: {snapshot.get('environment', 'UNKNOWN')}",
    )


def _draw_main(legacy, panel, context):
    layout = panel.layout
    scene = context.scene
    snapshot = workflow_snapshot(legacy, scene)
    status = layout.box()
    for index, line in enumerate(status_lines(snapshot)):
        status.label(text=line, icon='CHECKMARK' if index == 0 and snapshot['built'] else 'NONE')

    if not snapshot['built']:
        layout.operator('awful.build_studio', icon='ADD')
        layout.operator('awful.migrate_scene', text='Upgrade Historical AWFUL Scene')
        return

    row = layout.row(align=True)
    row.operator('awful.use_selected_product_v4', text='Use Selected', icon='OBJECT_DATA')
    row.operator('awful.validate_v4', text='Validate', icon='CHECKMARK')
    layout.prop(scene.awful_studio, 'auto_fit', toggle=True)


def _install_output_panel(legacy):
    class AWFUL_PT_Output(legacy.bpy.types.Panel):
        bl_label = 'Output'
        bl_idname = 'AWFUL_PT_OUTPUT'
        bl_parent_id = 'AWFUL_PT_MAIN_V4'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_options = {'DEFAULT_CLOSED'}
        bl_order = 60

        def draw(self, context):
            scene = context.scene
            settings = scene.awful_studio
            layout = self.layout
            if hasattr(settings, 'preview_mode'):
                layout.prop(settings, 'preview_mode', text='Viewport')
            layout.prop(scene.render, 'film_transparent', text='Transparent Background')
            layout.operator('awful.build_post_pipeline_v4', icon='NODETREE')

    legacy.AWFUL_PT_Output = AWFUL_PT_Output
    legacy.CLASSES = tuple(legacy.CLASSES) + (AWFUL_PT_Output,)


def _install_diagnostics_panel(legacy):
    class AWFUL_PT_Diagnostics(legacy.bpy.types.Panel):
        bl_label = 'Diagnostics'
        bl_idname = 'AWFUL_PT_DIAGNOSTICS'
        bl_parent_id = 'AWFUL_PT_MAIN_V4'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_options = {'DEFAULT_CLOSED'}
        bl_order = 70

        def draw(self, context):
            scene = context.scene
            layout = self.layout
            error = getattr(scene.awful_state, 'last_error', '')
            if error:
                layout.label(text='Last operation needs attention', icon='ERROR')
                layout.label(text=str(error)[:120])
            else:
                layout.label(text='No recorded AWFUL error', icon='CHECKMARK')
            layout.operator('awful.validate_v4', icon='CHECKMARK')
            layout.operator('awful.rebuild_studio', icon='RECOVER_LAST')
            layout.operator('awful.reset_system')

    legacy.AWFUL_PT_Diagnostics = AWFUL_PT_Diagnostics
    legacy.CLASSES = tuple(legacy.CLASSES) + (AWFUL_PT_Diagnostics,)


def _order_existing_panels(legacy):
    order = {
        'AWFUL_PT_STUDIO_GEOMETRY': 10,
        'AWFUL_PT_PRODUCT_V4': 20,
        'AWFUL_PT_LIGHTING_V4': 30,
        'AWFUL_PT_CAMERA_V4': 40,
        'AWFUL_PT_ENVIRONMENT_V4': 50,
        'AWFUL_PT_SETUP_V4': 90,
    }
    for name, value in order.items():
        panel = getattr(legacy, name, None)
        if panel is not None:
            panel.bl_order = value


def install(legacy):
    if getattr(legacy, '_awful_workflow_ui_installed', False):
        return
    legacy.AWFUL_PT_Main.draw = lambda self, context: _draw_main(
        legacy, self, context)
    _order_existing_panels(legacy)
    _install_output_panel(legacy)
    _install_diagnostics_panel(legacy)
    legacy._awful_workflow_ui_installed = True
