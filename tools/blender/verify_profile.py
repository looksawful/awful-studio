"""Assert the persisted AWFUL STUDIO Blender 5.2.1 workstation profile."""

import bpy

P = bpy.context.preferences
EXPECTED_LIBRARIES = {
    "AWFUL 3D Assets": r"A:\assets\3D ASSET",
    "AWFUL Textures": r"A:\Textures",
    "AWFUL Substance": r"A:\assets\SUBSTANCE",
}
REQUIRED = {
    "cycles", "io_curve_svg", "io_scene_fbx", "io_scene_gltf2", "blender_mcp",
    "bl_ext.blender_org.CAD_Sketcher", "bl_ext.blender_org.measureit",
    "bl_ext.blender_org.nd", "bl_ext.blender_org.bool_tool",
    "bl_ext.blender_org.looptools", "bl_ext.blender_org.magic_uv",
    "bl_ext.blender_org.asset_library_tools", "bl_ext.blender_org.ambientcg_material_importer",
    "bl_ext.blender_org.k_tools_texture_map_loader", "bl_ext.blender_org.material_utilities",
    "bl_ext.blender_org.gather_resources", "bl_ext.blender_org.node_preview",
    "awful_studio_keymap_overrides",
}

assert tuple(bpy.app.version[:3]) == (5, 2, 1), bpy.app.version_string
libs = {item.name: item.path for item in P.filepaths.asset_libraries}
assert all(libs.get(name) == path for name, path in EXPECTED_LIBRARIES.items()), libs
mods = {item.module for item in P.addons}
assert REQUIRED <= mods, sorted(REQUIRED - mods)
assert P.filepaths.use_auto_save_temporary_files and P.filepaths.auto_save_time == 2
assert P.filepaths.save_version >= 2 and P.edit.undo_steps >= 64 and P.edit.undo_memory_limit == 0
bt = P.addons["bl_ext.blender_org.bool_tool"].preferences
assert (bt.solver, bt.apply_order) == ("EXACT", "BOOLEANS")
assert P.addons["bl_ext.blender_org.nd"].preferences.use_fast_booleans is False
kt = P.addons["bl_ext.blender_org.k_tools_texture_map_loader"].preferences
assert kt.sanitize_name and kt.use_folder_name and kt.default_disp_method == "BUMP" and not kt.pack_to_blend
assert P.addons["bl_ext.blender_org.ambientcg_material_importer"].preferences.cache_dir == r"A:\Textures\ambientCG"
cad = P.addons["bl_ext.blender_org.CAD_Sketcher"].preferences
assert cad.decimal_precision == 4 and cad.angle_precision == 1 and cad.show_whats_new is False
cycles = P.addons["cycles"].preferences
assert cycles.compute_device_type == "OPTIX", cycles.compute_device_type
assert any(d.type == "OPTIX" and d.use and "4070 Ti" in d.name for d in cycles.devices)
assert all(not d.use for d in cycles.devices if d.type == "CPU")
assert hasattr(bpy.ops.import_scene, "gltf") and hasattr(bpy.ops.import_scene, "fbx")
assert hasattr(bpy.ops.import_curve, "svg")
print("VERIFY_PROFILE_PASS", bpy.app.version_string, cycles.compute_device_type, EXPECTED_LIBRARIES)
