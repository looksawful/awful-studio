# Blender tool integration policy

AWFUL Studio keeps third-party Blender tooling **declarative and non-invasive**. Importing or enabling AWFUL Studio never installs, enables, updates or removes another add-on, Extension, preset or template.

The machine-readable tool catalog is `extension/awful_studio/integrations/blender_tools.json`. Safe automation classes are:

- `extension-repository`: Blender Extension source may be offered as an explicit user action; AWFUL does not silently install or enable it.
- `manual`: account-gated, externally distributed or user-managed software; AWFUL only documents/detects it.
- `builtin`: Blender-owned capability, detected without mutating user preferences.

Tiers are `core`, `useful` and `optional`; none of them makes a third-party tool a runtime dependency of AWFUL Studio.

## Titan live audit, Blender 5.2.1, 2026-09-16

The 5.2 profile was inspected directly on Titan under the Blender user Extension repositories. This is an observed inventory, not a desired-state installer. The production profile from PR #87 remains the owner of machine settings, keymaps, OptiX and required workstation modules.

The live audit confirmed the existing production subset and additional free/open-source tools relevant to asset and mockup work. Installed manifests reported:

- MPFB 2.0.17, GPL-3.0-or-later: Blender-side MakeHuman character/rig workflow.
- Retarget 5.2.0, GPL-3.0-or-later: rig/animation and mocap retargeting.
- RetopoFlow 3.4.10, GPL-2.0-or-later: useful retopology, but installed from the user-managed repository, so AWFUL classifies it `manual`.
- BagaPie 11.0.12, GPL-3.0-or-later: modeling/geometry-node environment work.
- Modern Primitive 0.0.57, GPL-3.0-or-later and F2 1.8.5, GPL-3.0-or-later: mesh/hard-surface helpers.
- BatchForge 2.8.0, Batch Texture Converter 1.1.3 and Geo Bake Batch 0.0.1, all GPL-3.0-or-later: repeatable asset export/texture/bake operations.
- HDR Rotation 1.0.7 and Node Group Presets 0.8.0, GPL-3.0-or-later: lighting and reusable node setup.
- Enhanced SVG 0.2.4, GPL-3.0-or-later: vector ingestion for graphics/mockups.
- Tissue 0.3.71, GPL-2.0-or-later: specialist procedural mesh work.

These records were read from the installed `blender_manifest.toml` files. Adobe Substance, Character Creator tooling and other vendor/account-specific integrations observed on Titan are intentionally not promoted into this free-tool catalog. Duplicate or niche tools are also not promoted merely because they happen to be installed.

## Curated asset/mockup set

Core covers the normal production path: Node Wrangler, LoopTools, Bool Tool, ND, MeasureIt, Images as Planes, Material Utilities, Asset Library Tools, K-Tools Texture Map Loader, MPFB and BlenderKit.

Useful covers focused workflow accelerators: Collection Manager, camera/light helpers, Extra Mesh/Curve Objects, transform/node helpers, Magic UV, AmbientCG Material Importer, Gather Resources, CAD Sketcher, BagaPie, Modern Primitive, F2, Retarget, BatchForge, Batch Texture Converter, Geo Bake Batch, HDR Rotation, Enhanced SVG, Node Group Presets and RetopoFlow.

Optional stays specialist: Node Preview, Tissue, Amaranth and the external MakeHuman application workflow. Node Preview can create temporary preview renders; catalog inclusion is not permission to invoke it during lightweight verification.

## Presets and templates

The machine-readable policy is `extension/awful_studio/integrations/blender_content_policy.json`.

AWFUL-owned presets stay inside the Extension namespace. User-space export is explicit-only, collision-safe and never overwrites an existing user preset. Preset payloads remain declarative text/config rather than opaque binaries.

Templates are declarative scene specifications, not committed `.blend` startup files. AWFUL must not mutate `startup.blend` or user application-template directories. Any future user-space export must be explicit, namespaced and reversible.

## What AWFUL may automate

Safe now:

- load and validate tool/content manifests;
- report known tools and their tier/automation class;
- present explicit install/enable actions for Blender Extension sources;
- detect/document user-managed tools without taking ownership of them;
- manage AWFUL-owned declarative presets/templates inside its own namespace;
- verify manifests without starting Blender or rendering.

Never implicit:

- third-party authentication or acceptance of service terms;
- copying credentials into the repository;
- enabling/disabling arbitrary user extensions merely because they are catalogued;
- network/file-writing operations owned by another add-on;
- overwriting user presets, templates or `startup.blend`;
- changing the Titan production profile owned by the workstation-profile workflow.

## Verification

`tests/fast/test_blender_tools_contract.py` checks manifest uniqueness, automation/tier validity, the Titan-audited free-tool subset, manual treatment of user-managed RetopoFlow/BlenderKit/MakeHuman, absence of credential-like fields, preset/template no-overwrite rules and the absence of Blender/network/subprocess side effects in the catalog loader. Verification performs no rendering.
