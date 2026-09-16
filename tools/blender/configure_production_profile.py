"""Apply the AWFUL STUDIO Blender 5.2.1 hard-surface production profile."""

from pathlib import Path
import json
import shutil

import addon_utils
import bpy

EXPECTED_VERSION = (5, 2, 1)
ASSET_LIBRARIES = {
    "AWFUL 3D Assets": r"A:\assets\3D ASSET",
    "AWFUL Textures": r"A:\Textures",
    "AWFUL Substance": r"A:\assets\SUBSTANCE",
}
REQUIRED_ADDONS = (
    "cycles", "io_curve_svg", "io_scene_fbx", "io_scene_gltf2", "blender_mcp",
    "bl_ext.blender_org.CAD_Sketcher", "bl_ext.blender_org.measureit",
    "bl_ext.blender_org.nd", "bl_ext.blender_org.bool_tool",
    "bl_ext.blender_org.looptools", "bl_ext.blender_org.magic_uv",
    "bl_ext.blender_org.asset_library_tools",
    "bl_ext.blender_org.ambientcg_material_importer",
    "bl_ext.blender_org.k_tools_texture_map_loader",
    "bl_ext.blender_org.material_utilities",
    "bl_ext.blender_org.gather_resources", "bl_ext.blender_org.node_preview",
)


def ensure_addon(module: str) -> None:
    prefs = bpy.context.preferences.addons
    if prefs.get(module) is None:
        bpy.ops.preferences.addon_enable(module=module)
    if prefs.get(module) is None:
        raise RuntimeError(f"Required add-on is not enabled: {module}")


def ensure_library(name: str, directory: str) -> None:
    path = Path(directory)
    if not path.is_dir():
        raise FileNotFoundError(path)
    libraries = bpy.context.preferences.filepaths.asset_libraries
    entry = next((item for item in libraries if item.name == name), None)
    if entry is None:
        try:
            entry = libraries.new(name=name, directory=directory)
        except TypeError:
            entry = libraries.new(name=name)
    entry.path = directory


def set_addon_pref(module: str, prop: str, value) -> None:
    addon = bpy.context.preferences.addons.get(module)
    if addon is None:
        raise RuntimeError(f"Missing add-on preferences: {module}")
    if hasattr(addon.preferences, prop):
        setattr(addon.preferences, prop, value)


def install_keymap_override() -> Path:
    source = Path(__file__).with_name("awful_studio_keymap_overrides.py")
    target_dir = Path(bpy.utils.user_resource("SCRIPTS", path="addons", create=True))
    target = target_dir / source.name
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    addon_utils.modules_refresh()
    addon_utils.enable("awful_studio_keymap_overrides", default_set=True, persistent=True)
    return target


def main() -> None:
    if tuple(bpy.app.version[:3]) != EXPECTED_VERSION:
        raise RuntimeError(f"Expected Blender 5.2.1, got {bpy.app.version_string}")
    prefs = bpy.context.preferences
    for module in REQUIRED_ADDONS:
        ensure_addon(module)
    for name, directory in ASSET_LIBRARIES.items():
        ensure_library(name, directory)
    prefs.filepaths.use_auto_save_temporary_files = True
    prefs.filepaths.auto_save_time = 2
    prefs.filepaths.save_version = max(2, prefs.filepaths.save_version)
    prefs.edit.undo_steps = max(64, prefs.edit.undo_steps)
    prefs.edit.undo_memory_limit = 0

    set_addon_pref("bl_ext.blender_org.bool_tool", "solver", "EXACT")
    set_addon_pref("bl_ext.blender_org.bool_tool", "apply_order", "BOOLEANS")
    set_addon_pref("bl_ext.blender_org.nd", "use_fast_booleans", False)
    set_addon_pref("bl_ext.blender_org.nd", "hide_asset_library_install_prompt", True)
    set_addon_pref("bl_ext.blender_org.k_tools_texture_map_loader", "sanitize_name", True)
    set_addon_pref("bl_ext.blender_org.k_tools_texture_map_loader", "use_folder_name", True)
    set_addon_pref("bl_ext.blender_org.k_tools_texture_map_loader", "default_disp_method", "BUMP")
    set_addon_pref("bl_ext.blender_org.k_tools_texture_map_loader", "pack_to_blend", False)
    set_addon_pref("bl_ext.blender_org.ambientcg_material_importer", "cache_dir", r"A:\Textures\ambientCG")
    set_addon_pref("bl_ext.blender_org.CAD_Sketcher", "decimal_precision", 4)
    set_addon_pref("bl_ext.blender_org.CAD_Sketcher", "angle_precision", 1)
    set_addon_pref("bl_ext.blender_org.CAD_Sketcher", "show_whats_new", False)
    Path(r"A:\Textures\ambientCG").mkdir(parents=True, exist_ok=True)

    cycles = prefs.addons["cycles"].preferences
    cycles.compute_device_type = "OPTIX"
    cycles.get_devices()
    for device in cycles.devices:
        device.use = device.type == "OPTIX" and "RTX 4070 Ti" in device.name
    override = install_keymap_override()
    bpy.ops.wm.save_userpref()
    print("AWFUL_BLENDER_SETUP", json.dumps({"version": bpy.app.version_string, "libraries": ASSET_LIBRARIES, "cycles": cycles.compute_device_type, "override": str(override)}))


if __name__ == "__main__":
    main()
