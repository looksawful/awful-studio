# Blender tool integration policy

AWFUL Studio keeps third-party Blender tooling **declarative and non-invasive**. Importing or enabling AWFUL Studio never installs, enables, updates or removes another add-on, Extension, preset or template.

The machine-readable tool catalog is `extension/awful_studio/integrations/blender_tools.json`. It records tooling useful for asset and mockup work and classifies the only safe automation level:

- `builtin`: Blender-owned functionality; AWFUL may detect it, but does not mutate user preferences automatically.
- `extension-repository`: available through Blender's Extension ecosystem; installation remains an explicit user action.
- `manual`: third-party account/service or external distribution is involved; AWFUL only documents/detects it.

Tool tiers are intentionally small:

- `core`: useful in the normal asset/mockup workflow.
- `useful`: worth keeping available, but not required for every workstation.
- `optional`: specialist tooling that should never become an implicit dependency.

## Titan profile snapshot, 2026-09-16

The Blender user profile currently exposes extension directories for Blender 4.3, 5.0 and 5.1. The 5.1 profile contains `blenderkit` plus Blender Extensions including `bool_tool`, `looptools`, `measureit`, `extra_curve_objectes`, `extra_mesh_objects`, `add_camera_rigs`, `lighting_dynamic_sky`, `lighting_tri_lights`, `object_color_rules`, `object_fracture_cell`, `object_print3d_utils`, `object_collection_manager`, `curve_tools`, `io_scene_max`, `io_scene_x3d`, `io_import_images_as_planes`, `io_anim_camera`, `material_utils`, `mesh_snap_utilities_line`, `mesh_tissue`, `node_presets`, `node_arrange`, `copy_global_transform` and `amaranth`.

This snapshot is evidence, not a desired-state installer. AWFUL must not delete or overwrite those user-managed tools. Blender 5.2 is the project target, so migration or installation into 5.2 remains explicit until Blender 5.2 is present on Titan and each extension is confirmed compatible there.

## Curated asset/mockup set

The catalog now distinguishes the useful subset from the much larger installed profile instead of treating every historical extension as a dependency.

Core: Node Wrangler, LoopTools, Bool Tool, MeasureIt, Images as Planes, Material Utilities and BlenderKit. These cover node work, non-destructive modeling helpers, dimensional checks, reference/decal ingestion, material handling and free-tier asset discovery.

Useful: Collection Manager, Add Camera Rigs, Tri-Lighting, Extra Mesh Objects, Extra Curve Objects, Copy Global Transform, Node Arrange and Node Presets. These improve scene organization, mockup cameras/lights, common primitives and repeatable node/layout work without becoming mandatory runtime dependencies.

Optional: Amaranth and MakeHuman. MakeHuman remains manual because its content/distribution workflow belongs to the separate asset provenance pipeline rather than an add-on installer.

## Presets and templates

The machine-readable policy is `extension/awful_studio/integrations/blender_content_policy.json`.

AWFUL-owned presets stay inside the Extension namespace. Writing them into Blender user-space is `explicit-only`, collisions must never overwrite existing user presets, and preset payloads remain text/declarative rather than opaque binaries.

Templates are declarative scene specifications, not committed `.blend` startup files. AWFUL must not mutate `startup.blend` or a user's application-template directories. If a future command exports a user-space template, it must be explicit, namespaced, collision-safe and reversible.

This keeps repository-owned configuration versionable while avoiding the classic automation achievement of silently replacing someone's carefully tuned Blender profile.

## What AWFUL may automate

Safe now:

- load and validate the catalog and content policy;
- show whether a known tool is core/useful/optional;
- present explicit install/enable actions for Blender-owned Extension sources;
- manage AWFUL-owned declarative presets/templates inside its own namespace;
- verify manifests without starting Blender or rendering.

Not safe to automate implicitly:

- third-party authentication or acceptance of service terms;
- copying credentials into the repository;
- enabling/disabling arbitrary user extensions;
- overwriting user presets, templates or `startup.blend`;
- migrating the Titan profile into Blender 5.2 before compatibility is checked on that installed runtime.

## Verification

`tests/fast/test_blender_tools_contract.py` checks manifest uniqueness, allowed automation modes and tiers, the absence of credential-like fields, the preset/template no-overwrite contract, and that the loader has no Blender/network/subprocess side effects. This verification is deliberately lightweight and performs no rendering.
