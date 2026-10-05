# iPhone 17: existing component inventory and recursive topology work design

Research snapshot: 2026-10-05. Scope is planning and source/runtime inspection; no geometry modification. Existing issue #118 and its handoff remain the execution owner. The grouping below is an inspection/work map, not new backlog, new nodes, or a replacement hierarchy.

## [100%] Verified runtime inventory

Read the actual GLB JSON chunk and indexed accessor counts, not a manifest count. Candidate: [iphone_17_v30_web.glb](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb), SHA-256 `68bcd22831e427a077ddfd48662e41bbe8ef46ebda0359c7153b9e3579afeae0`. Exact inventory: **51 meshes, 57 nodes, 11,538 triangles**, 53 material primitives. All 51 mesh nodes are direct children of `CTRL_IPHONE_17`, node 56. Its other five children are `ANCHOR_BOTTOM_CENTER`, `ANCHOR_CENTER`, `ANCHOR_REAR_CAMERA`, `ANCHOR_SCREEN_CENTER`, `SCREEN_GLOW_ANCHOR`. Scene root is node 56. No recursive geometric assemblies currently exist in the exported hierarchy.

Each leaf below appears exactly once. Counts sum to 11,538. UV yes means every primitive has TEXCOORD_0; it does not certify bake-quality UVs. All UV-bearing primitives also have TANGENT; POSITION and NORMAL are present throughout.

| Existing mesh | Inspection group | Export triangles | UV | Runtime material(s) |
|---|---|---:|---|---|
| `BACK_GLASS` | panels_and_display | 268 | yes | MAT_BACK_GLASS |
| `SCREEN_CONTENT` | panels_and_display | 268 | yes | MAT_SCREEN_CONTENT, MAT_SCREEN_EDGE |
| `DISPLAY_BEZEL` | panels_and_display | 780 | no | MAT_DISPLAY_BEZEL |
| `DISPLAY_GLASS_SEAT` | panels_and_display | 780 | no | MAT_ASSEMBLY_GAP |
| `APPLE_LOGO_DECAL` | panels_and_display | 2 | yes | MAT_APPLE_LOGO_DECAL |
| `BODY_ALUMINUM` | body | 5644 | yes | MAT_ANODIZED_ALUMINUM, MAT_UNDER_GLASS_BLACK |
| `ACTION_BUTTON` | side_controls | 84 | yes | MAT_ANODIZED_ALUMINUM_ACTION_BUTTON |
| `ANTENNA_SIDE_L_55` | side_controls | 12 | yes | MAT_OPTICS_BLACK |
| `ANTENNA_SIDE_L_-55` | side_controls | 12 | yes | MAT_OPTICS_BLACK |
| `ANTENNA_SIDE_R_55` | side_controls | 12 | yes | MAT_OPTICS_BLACK |
| `ANTENNA_SIDE_R_-55` | side_controls | 12 | yes | MAT_OPTICS_BLACK |
| `CAMERA_CONTROL` | side_controls | 84 | yes | MAT_CAMERA_CONTROL_GLASS |
| `SIDE_BUTTON` | side_controls | 84 | yes | MAT_ANODIZED_ALUMINUM_SIDE_BUTTON |
| `VOL_DOWN` | side_controls | 84 | yes | MAT_ANODIZED_ALUMINUM_VOL_DOWN |
| `VOL_UP` | side_controls | 84 | yes | MAT_ANODIZED_ALUMINUM_VOL_UP |
| `BOTTOM_MIC_APERTURE_01` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_MIC_APERTURE_02` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_MIC_APERTURE_03` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_SCREW_L` | bottom | 80 | yes | MAT_FASTENER |
| `BOTTOM_SCREW_R` | bottom | 80 | yes | MAT_FASTENER |
| `BOTTOM_SPEAKER_APERTURE_01` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_SPEAKER_APERTURE_02` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_SPEAKER_APERTURE_03` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_SPEAKER_APERTURE_04` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `BOTTOM_SPEAKER_APERTURE_05` | bottom | 64 | yes | MAT_APERTURE_GRILLE |
| `USB_C_CAVITY` | bottom | 12 | yes | MAT_APERTURE_GRILLE |
| `USB_C_TONGUE` | bottom | 12 | yes | MAT_ALUMINUM_EDGE |
| `FRONT_CAMERA_GLASS` | front_hardware | 88 | yes | MAT_FRONT_OPTIC |
| `FRONT_CAMERA_INNER` | front_hardware | 64 | yes | MAT_OPTICS_BLACK |
| `FRONT_CAMERA_IRIS` | front_hardware | 48 | yes | MAT_FRONT_OPTIC |
| `FRONT_CAMERA_MASK` | front_hardware | 96 | yes | MAT_UNDER_GLASS_BLACK |
| `FRONT_CAMERA_PUPIL` | front_hardware | 32 | yes | MAT_OPTICS_BLACK |
| `FRONT_RECEIVER_MIC` | front_hardware | 12 | yes | MAT_OPTICS_BLACK |
| `FRONT_SENSOR_MASK` | front_hardware | 108 | no | MAT_UNDER_GLASS_BLACK |
| `CAMERA_HOUSING` | rear_camera_housing | 164 | yes | MAT_CAMERA_HOUSING |
| `CAMERA_HOUSING_SEAT` | rear_camera_housing | 164 | yes | MAT_CAMERA_HOUSING_SEAT |
| `CAMERA_1_BEVEL` | rear_camera_1 | 160 | yes | MAT_CAMERA_BEVEL |
| `CAMERA_1_GLASS` | rear_camera_1 | 160 | yes | MAT_LENS_GLASS |
| `CAMERA_1_INNER` | rear_camera_1 | 128 | yes | MAT_OPTICS_BLACK |
| `CAMERA_1_IRIS` | rear_camera_1 | 96 | yes | MAT_LENS_GLASS |
| `CAMERA_1_PUPIL` | rear_camera_1 | 64 | yes | MAT_OPTICS_BLACK |
| `CAMERA_1_RING` | rear_camera_1 | 160 | yes | MAT_CAMERA_RING |
| `CAMERA_2_BEVEL` | rear_camera_2 | 160 | yes | MAT_CAMERA_BEVEL |
| `CAMERA_2_GLASS` | rear_camera_2 | 160 | yes | MAT_LENS_GLASS |
| `CAMERA_2_INNER` | rear_camera_2 | 128 | yes | MAT_OPTICS_BLACK |
| `CAMERA_2_IRIS` | rear_camera_2 | 96 | yes | MAT_LENS_GLASS |
| `CAMERA_2_PUPIL` | rear_camera_2 | 64 | yes | MAT_OPTICS_BLACK |
| `CAMERA_2_RING` | rear_camera_2 | 160 | yes | MAT_CAMERA_RING |
| `FLASH` | rear_flash_and_mic | 128 | yes | MAT_FLASH |
| `FLASH_RING` | rear_flash_and_mic | 128 | yes | MAT_ALUMINUM_EDGE |
| `REAR_MIC` | rear_flash_and_mic | 64 | yes | MAT_OPTICS_BLACK |

## JSON-friendly exact group map

Use only to filter/isolate actual loaded GLB meshes in the existing viewer. Hiding groups is a review tool; full-device wireframe must remain available. Per-mesh selection remains possible within each group.

```json
{
  "panels_and_display": [
    "BACK_GLASS",
    "SCREEN_CONTENT",
    "DISPLAY_BEZEL",
    "DISPLAY_GLASS_SEAT",
    "APPLE_LOGO_DECAL"
  ],
  "body": [
    "BODY_ALUMINUM"
  ],
  "side_controls": [
    "ACTION_BUTTON",
    "ANTENNA_SIDE_L_55",
    "ANTENNA_SIDE_L_-55",
    "ANTENNA_SIDE_R_55",
    "ANTENNA_SIDE_R_-55",
    "CAMERA_CONTROL",
    "SIDE_BUTTON",
    "VOL_DOWN",
    "VOL_UP"
  ],
  "bottom": [
    "BOTTOM_MIC_APERTURE_01",
    "BOTTOM_MIC_APERTURE_02",
    "BOTTOM_MIC_APERTURE_03",
    "BOTTOM_SCREW_L",
    "BOTTOM_SCREW_R",
    "BOTTOM_SPEAKER_APERTURE_01",
    "BOTTOM_SPEAKER_APERTURE_02",
    "BOTTOM_SPEAKER_APERTURE_03",
    "BOTTOM_SPEAKER_APERTURE_04",
    "BOTTOM_SPEAKER_APERTURE_05",
    "USB_C_CAVITY",
    "USB_C_TONGUE"
  ],
  "front_hardware": [
    "FRONT_CAMERA_GLASS",
    "FRONT_CAMERA_INNER",
    "FRONT_CAMERA_IRIS",
    "FRONT_CAMERA_MASK",
    "FRONT_CAMERA_PUPIL",
    "FRONT_RECEIVER_MIC",
    "FRONT_SENSOR_MASK"
  ],
  "rear_camera_housing": [
    "CAMERA_HOUSING",
    "CAMERA_HOUSING_SEAT"
  ],
  "rear_camera_1": [
    "CAMERA_1_BEVEL",
    "CAMERA_1_GLASS",
    "CAMERA_1_INNER",
    "CAMERA_1_IRIS",
    "CAMERA_1_PUPIL",
    "CAMERA_1_RING"
  ],
  "rear_camera_2": [
    "CAMERA_2_BEVEL",
    "CAMERA_2_GLASS",
    "CAMERA_2_INNER",
    "CAMERA_2_IRIS",
    "CAMERA_2_PUPIL",
    "CAMERA_2_RING"
  ],
  "rear_flash_and_mic": [
    "FLASH",
    "FLASH_RING",
    "REAR_MIC"
  ]
}
```

## [100%] Source correspondence and constraints

The generator creates named Blender objects and parents body/detail/screen collections to one root: [generate_low_v30.py:1072](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:1072). The export selects root plus recursive children, retains extras and tangents, and uses the same names as mesh data: [export_runtime_v30.py:51](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/export_runtime_v30.py:51), [export_runtime_v30.py:124](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/export_runtime_v30.py:124).

Authored source correspondence by family:

- BACK_GLASS and SCREEN_CONTENT use the existing strip-prism helper, segments16; bezel/seat use old outline_segments48: [generate_low_v30.py:544](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:544), [generate_low_v30.py:557](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:557), [generate_low_v30.py:580](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:580). Screen uses two explicit material slots and dedicated planar UVs; preserve that contract [generate_low_v30.py:599](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:599).
- BODY_ALUMINUM is authored directly by build_body_mesh, with local cells and segments28: [generate_low_v30.py:1056](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:1056). Builder explicitly describes disconnected manifold shells, not one welded shell: [body_topology_v30.py:133](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/body_topology_v30.py:133). Body regions therefore need seam/overlap inspection; being one named mesh is not proof that its cells form a welded continuous surface.
- Five controls use capsule_prism_x and per-part bake normals; four antennas are named boxes: [generate_low_v30.py:935](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:935), [generate_low_v30.py:957](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:957).
- USB cavity/tongue are separate named objects. Acoustic ports and screws use radial_prism_z, respectively16/20 radial segments: [generate_low_v30.py:966](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:966), [generate_low_v30.py:1018](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:1018). Their presence is verified; a dark USB render is not evidence of missing tongue.
- Front masks and circular optics use strip/radial meshes under the screen plane; official7.79mm datum and privacy artwork remain: [generate_low_v30.py:576](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:576), [generate_low_v30.py:693](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:693).
- Rear housing/seat and camera rings/bevel/glass use accepted40-class helper; inner/iris/pupil have separate radial budgets: [camera_topology_v30.py:13](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/camera_topology_v30.py:13), [generate_low_v30.py:736](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:736). Rear optics audit must preserve previously accepted camera appearance; topology rejection of whole device does not invalidate camera silhouette evidence automatically.
- APPLE_LOGO_DECAL is a2-triangle material/alpha-backed surface and has special runtime image handling: [export_runtime_v30.py:34](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/export_runtime_v30.py:34). Preserve alpha/UV/placement.

Authored-only components must also be audited, but never quietly introduced into browser rendering: SCREEN_GLASS is explicitly excluded by the web exporter [export_runtime_v30.py:126](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/export_runtime_v30.py:126). Its Blender modifiers and native appearance remain a separate gate. BACK_GLASS_SEAT and BODY_ALUMINUM_HIGH are hidden references, not missing exported runtime leaves: [generate_low_v30.py:543](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:543), [generate_low_v30.py:1050](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/generate_low_v30.py:1050); exporter removes hidden meshes [export_runtime_v30.py:32](F:/Temp/iphone17-v30-topology-rebuild/assets/device_mockups/iphone_17/export_runtime_v30.py:32).

## [20%] Recursive execution design: leaves, neighbors, assembly

1. **Freeze appearance evidence first.** Copy exact candidate bytes plus manifest identity; pin viewer/PBR policy and representative camera/finish/screen settings. Archive historical comparisons by identity without deleting them. Frozen reference is not a claim that current topology passed.
2. **Panels/display frame pilot.** Audit DISPLAY_BEZEL and DISPLAY_GLASS_SEAT individually, then their nesting against SCREEN_CONTENT/BACK_GLASS. Decide corner samples from silhouette error at agreed close zoom. Sparse planar interiors can retain intentional diagonals. RED must demonstrate a concrete surplus/poor segment flow or render defect on one existing leaf. Pilot teaches the repeatable workflow before applying it everywhere.
3. **Body regions and mating geometry.** Audit existing body disconnected components: rounded corners, front/back seating rails, side cells, bottom cells. Keep the single existing object identity. Shared boundary curves must agree with panels. Repair/weld only where one physical continuous skin requires it and evidence proves seams/overlaps; no global remesh. Inspect silhouette and grazing highlights before advancing.
4. **Controls + antennas.** Isolate each control, then its corresponding body recess/rail; audit antennas against side skin. Per-part normal maps must remain tied to matching UV/tangent layout. Changing one reused construction helper requires tests of all five control leaves, not only its exemplar.
5. **Bottom module.** USB_C_CAVITY and USB_C_TONGUE, each mic/speaker aperture, then screws. Couple every visible insert to its body cell, with world-space aperture/recess alignment, no sliver gaps/occlusion regressions. Flat cavity versus reference render is an observation to diagnose, not an established root cause.
6. **Front hardware.** Masks, front optics layers and receiver, then SCREEN_CONTENT interactions at7.79mm datum. Keep software Dynamic Island/privacy on screen; no coplanar island geometry or depth workaround. Masks remain under-glass.
7. **Rear camera audit last.** Housing/seat, camera1 leaves, camera2 leaves, flash/ring/mic, then camera module against back panel. Preserve accepted camera geometry/bakes unless a specific failed mesh quality criterion requires a targeted correction. Do not copy poor historical camera back into current assembly.
8. **Whole assembly and native delivery.** Run complete flat-hierarchy scene, all finishes/screen states, exterior normals, GLB/world-space contracts, browser wireframe/render, and native saved/reopened Blender validation. Re-check all changed mating boundaries and provenance. Obtain human mesh+render PASS before release actions.

Recursion means inspect leaf -> repair/test leaf -> inspect neighboring mating surfaces -> inspect group -> inspect whole device. It does not require creating new Blender meshes or reparenting exported nodes. Assembly is ordering of verification dependencies; existing identity, transforms, anchors and material/state contracts stay stable.

## [0%] Per-leaf RED/GREEN contract

For each selected existing mesh record: source object and region, frozen runtime identity, intended function, observed defect, boundary neighbors, expected silhouette/highlight behavior and texture/UV constraints. RED uses actual exported positions/indices/normals/UVs and/or saved Blender geometry; no constant-vs-constant tests. Keep the failure local to the observed candidate and record a matched image/macro if visual.

GREEN checks: no newly degenerate/duplicate/flipped geometry; appropriate manifold/open-surface policy for that part; stable world-space datums and mating gaps; UV/tangent/material correctness; deterministic export triangulation; useful corner/fillet segments at close zoom; no needless hidden/flat-area tessellation. Do not impose universal all-quads, uniform density, fixed global aspect ratio, or an arbitrary triangle ceiling. Long planar triangles can be valid; thin curved triangles, poles and cap fans require region-specific evaluation. Merged vertices can be intentionally split at UV/sharp-normal/material boundaries in export.

Every stage uses the same renderer and actual GLB triangles, group/leaf isolation plus full assembly wireframe and render. After a topology/UV change, re-bake affected maps, fingerprint every consumed input, and compare the resulting GLB and Blender render against frozen appearance. Human inspection is a separate gate from automated geometry correctness.

## Uncertainties and blockers

- Original research verified GLB and source correspondence. The primary agent subsequently opened all three saved files in pinned Blender 5.2.1/build9e2066aef7ef on Oct05. Source/plugin each contain56meshes/52 hide_render=False; delivery.blend contains52meshes/no HIGH. Native-only visible leaf SCREEN_GLASS is confirmed. Four hidden source/plugin references: BACK_GLASS_SEAT, BODY_ALUMINUM_HIGH, CAMERA_1_SEAT and CAMERA_2_SEAT. Plugin HIGH exclusion remains an open requirement. Source/native appearance has not been accepted from these counts.
- Saved-file audit confirms two authored n-gons each in DISPLAY_BEZEL/DISPLAY_GLASS_SEAT, three in SCREEN_GLASS. Visible BEVEL remains on four antennas, FRONT_RECEIVER_MIC, USB_C_CAVITY/USB_C_TONGUE and SCREEN_GLASS; SCREEN_GLASS also has WEIGHTED_NORMAL. Pilot/native materialization requirements remain open. Full saved-file inventory and hashes were preserved as `iphone17-native-inventory-2026-10-05.json` with the owner deliverables. Ten existing runtime contracts pass but do not certify these uncovered criteria.
- A mesh's triangle count/UV presence is not proof of clean topology, acceptable tangents or visual equivalence. None of the51 leaves is marked topology-approved by this report.
- Existing two780-triangle frame leaves have no runtime UVs; assign/test UVs only if their production material needs them, rather than inventing maps because others have maps.
- Current driver/Three.js warnings remain outside this mesh inventory, and final native/UV/provenance gates remain open. No final visual PASS or release authorization inferred.
