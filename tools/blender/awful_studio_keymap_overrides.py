bl_info = {'name': 'AWFUL Studio Keymap Overrides', 'author': 'AWFUL STUDIO', 'version': (1, 0, 1), 'blender': (5, 2, 0), 'category': 'System'}

"""Resolve AWFUL STUDIO hard-surface keymap collisions without disabling tools."""

import bpy
from bpy.app.handlers import persistent

_BOOL_TOOL_NUMPAD = {
    "object.boolean_brush_difference",
    "object.boolean_brush_union",
    "object.boolean_brush_intersect",
    "object.boolean_brush_slice",
}


def apply_overrides() -> int:
    wm = bpy.context.window_manager
    keyconfig = wm.keyconfigs.addon if wm else None
    if not keyconfig:
        return 0
    changed = 0
    for keymap in keyconfig.keymaps:
        for item in keymap.keymap_items:
            duplicate_numpad = item.idname in _BOOL_TOOL_NUMPAD and item.type.startswith("NUMPAD_") and item.ctrl
            duplicate_popup = item.idname == "wm.call_menu" and item.type == "B" and item.ctrl and item.shift and getattr(item.properties, "name", "") == "VIEW3D_MT_boolean_popup"
            if item.active and (duplicate_numpad or duplicate_popup):
                item.active = False
                changed += 1
    return changed


@persistent
def _load_post(_unused):
    apply_overrides()


def _timer():
    apply_overrides()
    return None


def register():
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)
    apply_overrides()
    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer, first_interval=0.5)


def unregister():
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)
