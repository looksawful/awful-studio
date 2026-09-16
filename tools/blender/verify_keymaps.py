"""Assert AWFUL STUDIO hard-surface operator and keymap availability."""

import bpy

ids = {
    "object.boolean_brush_difference",
    "object.boolean_brush_union",
    "object.boolean_brush_intersect",
    "object.boolean_brush_slice",
}
seen = []
for keymap in bpy.context.window_manager.keyconfigs.addon.keymaps:
    for item in keymap.keymap_items:
        if item.idname in ids and item.type.startswith("NUMPAD_") and item.ctrl:
            seen.append((keymap.name, item.idname, item.type, item.active))
            assert not item.active, (keymap.name, item.idname, item.type)
assert len(seen) == 4, seen

operators = (
    "object.boolean_auto_difference",
    "mesh.looptools_circle",
    "measureit.runopengl",
    "material.assign_material",
    "uv.muv_uv_bounding_box",
    "view3d.slvs_add_sketch",
    "alt.open_library_folder",
    "file.gather_resources",
    "node.npv_refresh",
)
for operator in operators:
    category, name = operator.split(".", 1)
    assert hasattr(getattr(bpy.ops, category), name), operator

print("VERIFY_KEYMAPS_PASS", seen, len(operators))
