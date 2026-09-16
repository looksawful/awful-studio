# Blender tool integration policy

AWFUL Studio keeps third-party Blender tooling **declarative and non-invasive**. Importing or enabling AWFUL Studio never installs, enables, updates or removes another add-on, Extension, preset or template.

The machine-readable catalog is `extension/awful_studio/integrations/blender_tools.json`. It records tooling useful for asset and mockup work and classifies the only safe automation level:

- `builtin`: Blender-owned functionality; AWFUL may detect it, but does not mutate user preferences automatically.
- `extension-repository`: installable from Blender's Extension ecosystem; installation remains an explicit user action.
- `manual`: third-party account/service or external distribution is involved; AWFUL only documents/detects it.

## Titan profile snapshot, 2026-09-16

The Blender user profile currently exposes extension directories for Blender 4.3, 5.0 and 5.1. The 5.1 profile contains `blenderkit` plus Blender Extensions including `bool_tool`, `looptools`, `measureit`, `extra_curve_objectes`, `extra_mesh_objects`, `add_camera_rigs`, `lighting_dynamic_sky`, `lighting_tri_lights`, `object_color_rules`, `object_fracture_cell`, `object_print3d_utils`, `object_collection_manager`, `curve_tools`, `io_scene_max`, `io_scene_x3d`, `io_import_images_as_planes`, `io_anim_camera`, `material_utils`, `mesh_snap_utilities_line`, `mesh_tissue`, `node_presets`, `node_arrange`, `copy_global_transform` and `amaranth`.

This snapshot is documentation, not a desired-state installer. AWFUL must not delete or overwrite those user-managed tools. Blender 5.2 is the project target, so profile migration/installation into 5.2 must stay explicit until Blender 5.2 is present and each extension is confirmed compatible.

## Presets and templates

AWFUL-owned scene/camera/light/material presets belong in AWFUL Studio's own data/code and may be managed by the Extension. User Blender presets and startup templates are never overwritten. Future export of AWFUL presets into Blender user-space must use an explicit command, collision-safe names and reversible writes.

## Recommended core set

For mockup production the catalog currently recognizes Node Wrangler, LoopTools, Bool Tool and MeasureIt as small focused helpers. BlenderKit and MakeHuman are intentionally `manual`: both involve third-party distribution/content semantics and should not be silently provisioned. Character/content libraries are handled by the separate asset provenance workflow rather than pretending an add-on installer is an asset license manager.

## Verification

`tests/fast/test_blender_tools_contract.py` checks manifest uniqueness, allowed automation modes, absence of credential fields, and that the loader has no Blender/network/subprocess side effects. This is deliberately lightweight and performs no rendering.
