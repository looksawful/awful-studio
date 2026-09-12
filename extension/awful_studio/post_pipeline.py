# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional Post Pipeline workflow adapter for AWFUL STUDIO.

The retained legacy compositor/pass builders stay authoritative. This module
adds explicit capability checks, idempotent user-facing setup semantics and UI
state without creating Post Pipeline data during normal Build/Rebuild.
"""
from __future__ import annotations


def capability_state(caps) -> dict[str, object]:
    """Return a concrete preflight result before any Post Pipeline mutation."""
    caps = dict(caps or {})
    missing = []
    if not caps.get('viewlayer_lightgroups'):
        missing.append('Cycles View Layer Light Groups')
    if not caps.get('compositor_group_api'):
        missing.append('Blender 5 Compositing Node Group API')
    if missing:
        return {
            'supported': False,
            'message': 'Post Pipeline unavailable: missing ' + ', '.join(missing),
        }
    return {
        'supported': True,
        'message': 'Post Pipeline capabilities available.',
    }


def install(legacy):
    """Install Post Pipeline workflow behavior before Extension registration."""
    if getattr(legacy, '_awful_post_pipeline_workflow_installed', False):
        return

    operator = legacy.AWFUL_OT_BuildPostPipeline
    original_execute = operator.execute
    original_setup_draw = legacy.AWFUL_PT_Setup.draw
    original_detect_capabilities = legacy.detect_blender_capabilities

    def detect_blender_capabilities():
        """Refine generic probes through Blender 5.2's live context APIs.

        Blender 5.2 exposes Light Group and compositor properties dynamically on
        live ViewLayer/Scene instances. Type-level RNA probes can therefore report
        false negatives even though the built-in operators and scene API work.
        """
        caps = original_detect_capabilities()
        try:
            scene_ops = legacy.bpy.ops.scene
            caps['viewlayer_lightgroups'] = all(
                hasattr(scene_ops, name)
                for name in (
                    'view_layer_add_lightgroup',
                    'view_layer_remove_lightgroup',
                    'view_layer_add_used_lightgroups',
                )
            )
        except Exception:
            caps['viewlayer_lightgroups'] = False

        try:
            scene = getattr(legacy.bpy.context, 'scene', None)
            caps['compositor_group_api'] = (
                scene is not None and hasattr(scene, 'compositing_node_group')
            )
        except Exception:
            caps['compositor_group_api'] = False
        return caps

    operator.bl_label = 'Setup Post Pipeline'
    operator.bl_description = (
        'Prepare Cycles Light Groups, render passes and a managed compositor '
        'for professional post-production review')

    def invoke(self, context, event):
        scene = context.scene
        if bool(scene.get(legacy.POST_PIPELINE_KEY, False)):
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        # CAPS is runtime state, not .blend data. Re-detect here so Setup Post
        # Pipeline works after save/reopen and after loading an existing studio.
        live_caps = detect_blender_capabilities()
        legacy.CAPS = dict(live_caps)
        state = capability_state(live_caps)
        if not state['supported']:
            self.report({'ERROR'}, str(state['message']))
            return {'CANCELLED'}

        result = original_execute(self, context)
        if result != {'FINISHED'}:
            return result

        # Workspace changes are UI-only. Background/cloud qualification validates
        # scene state without needing a screen or workspace.
        if not legacy.bpy.app.background and getattr(context, 'window', None):
            workspace = legacy.bpy.data.workspaces.get('Compositing')
            if workspace is not None:
                try:
                    context.window.workspace = workspace
                except Exception:
                    pass
        return result

    def draw_setup(self, context):
        original_setup_draw(self, context)
        ready = bool(context.scene.get(legacy.POST_PIPELINE_KEY, False))
        box = self.layout.box()
        box.label(
            text='Post Pipeline: Ready' if ready else 'Post Pipeline: Not Setup',
            icon='CHECKMARK' if ready else 'INFO',
        )
        if ready:
            box.label(text='Run Setup Post Pipeline again to rebuild it')

    legacy.detect_blender_capabilities = detect_blender_capabilities
    operator.invoke = invoke
    operator.execute = execute
    legacy.AWFUL_PT_Setup.draw = draw_setup
    legacy._awful_post_pipeline_workflow_installed = True
