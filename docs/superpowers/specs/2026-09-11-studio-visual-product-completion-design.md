# AWFUL STUDIO Visual / Product Completion Design

Date: 2026-09-11
Status: accepted execution design from the owner instruction to finish the planned studio/product work
Target runtime: Blender 5.2.1 LTS
Current integration base: `feature/extension-foundation`

## Goal

Turn the Alpha 0.0.16 Extension Foundation from a safe/installable technical foundation into the complete accepted P0 studio workflow, then continue into the first 0.0.17 Product Quality slice without weakening lifecycle, ownership, offline or runtime guarantees.

The immediate visible problem is not one isolated preset. The retained v4 implementation still mixes hidden bounce geometry, visible architecture, cyclorama geometry and coarse visibility state. This makes it difficult to control the stage physically and produces visually weak or misleading studio states even though the Extension lifecycle itself is now safe.

## Scope and milestone boundary

### Alpha 0.0.16 P0 completion

1. `#7` Cyclorama: metric placement, safe bounds, long floor run, White / Black / Chroma Green looks, Matte / Medium / Glossy finishes and independent visibility.
2. `#21` Studio architecture: visible floor independent from the hidden bounce shell, a real door opening, door geometry and independent camera/viewport visibility for walls, floor, ceiling, door, window frame, window glass and cyclorama.
3. `#9` Natural Light v2: helper-free Pure HDRI, Physical Sky modes, a real managed Sun role where required, zero-energy portal, independent artificial-light disable and network-clean Build/preset switching.
4. `#8` Playback policy: independent Once / Loop / Ping-Pong policy for existing product and camera motions, without action/modifier accumulation.
5. `#23` Asset provenance / Extensions compatibility: machine-readable source/license/distribution metadata for all active remote assets and strict cache/packaging rules.
6. Release/runtime reconciliation issues `#3`, `#5`, `#10`, `#12` and native repository/update verification.
7. `#4` deterministic visual evidence for visual-changing slices. Visual comparisons are evidence for intended look changes, not a universal exact-pixel release gate.

### First Alpha 0.0.17 Product Quality slice

After all 0.0.16 P0 gates are green, replace the diagnostic-product feel with production-usable procedural hero mockups and material starters:

- Bottle;
- Jar;
- Box;
- Can;
- Phone;
- Tablet;
- material starters appropriate to product work: coated/plastic, glass, metal, paper/cardboard and emissive/screen where applicable.

Expanded motion variants, fixtures/physical modifiers, volumetrics and the larger HDRI library remain later 0.0.17+ work unless explicitly promoted.

## Global invariants

- Blender target is 5.2 LTS; runtime evidence uses Blender 5.2.1.
- `historical/0.0.15/awful_studio_v4_2_gpu_perf.py` remains byte-identical evidence and is never edited.
- Import/register/enable/update/restart never creates or mutates a studio scene.
- Studio Build/Rebuild/Remove remain explicit operations.
- Base Build is offline and makes zero network requests.
- Names and `awful_role` are lookup metadata, not ownership authorization.
- Destructive mutations remain owner- and scene-scoped.
- Unmanaged user objects, materials, transforms, worlds, cameras and collections survive Build/Rebuild/Remove/migration.
- Blender-native controls remain authoritative; AWFUL exposes workflow intent, not copies of all Blender properties.
- Heavy or optional systems remain opt-in.
- No issue closes from static source inspection alone when behavior depends on `bpy`.
- Every production slice uses RED → GREEN → REFACTOR and the exact built ZIP for final runtime evidence.

## Studio geometry architecture

### Separate visible architecture from bounce geometry

The current `ROOM_*` shell remains the physical/bounce enclosure. It is not the visible studio floor or the sole source of camera-visible architecture.

New visible architecture is explicitly managed and role-addressable. At minimum:

- `ARCH_FLOOR_VISIBLE`;
- `DOOR_FRAME` objects;
- `DOOR_LEAF`;
- existing window frame and glass roles remain separately addressable;
- cyclorama remains `CYC`.

The visible floor must not be coplanar with the cyclorama floor. The default implementation uses non-overlapping floor regions around the cyclorama floor run rather than stacking two coincident planes.

### Door opening

The room wall that contains the door is constructed around a genuine empty opening. A decorative rectangle placed on an intact wall does not satisfy the requirement.

The door system includes:

- wall segments that stop around the opening;
- a frame;
- a managed door leaf positioned at the opening;
- a stable default transform suitable for a studio view;
- independent visibility without rebuilding the whole room.

### Cyclorama distance semantics

`cyclorama_distance_m` means the metric distance on studio Y from the product/stage origin to the floor-to-cove tangent (`curve_start_y`). Positive values move the cove away from the stage toward the background wall.

The allowed range is derived from room/cyclorama dimensions and safety clearance, not from an arbitrary UI clamp. It must keep:

- the product safe envelope clear of the cove;
- the cyclorama radius/vertical section clear of the background shell;
- the product/camera target relationship valid;
- the visible floor/cyclorama surfaces non-overlapping.

Changing distance mutates only the owned cyclorama placement/geometry and dependent stage targets. It does not rebuild unrelated user data.

### Cyclorama floor run

The cyclorama floor extends from the camera-side front edge to the tangent point. The default retains a long foreground run so the product is visually separated from the cove and is not perched directly on the curve.

### Cyclorama looks and finish

One owned cyclorama material is reused rather than creating a material per click.

Look policy:

- `WHITE`: neutral off-white suitable for commercial product work without clipping the base color to pure 1.0;
- `BLACK`: near-black, not mathematically zero, so roughness/specular response remains readable;
- `CHROMA_GREEN`: controlled chroma green suitable for keying.

Finish policy:

- `MATTE`: high roughness;
- `MEDIUM`: middle roughness;
- `GLOSSY`: low roughness with bounded physically plausible values.

Look and finish are orthogonal. Reapplying either state is idempotent and does not add nodes/materials/datablocks.

### Architecture visibility semantics

There are independent workflow toggles for:

- walls;
- visible floor;
- ceiling;
- door;
- window frame;
- window glass;
- cyclorama.

Where Blender supports ray visibility, a camera-visibility toggle does not silently remove a surface from diffuse/glossy/shadow participation. Viewport hiding and camera-ray visibility may change while render participation remains physically useful.

The existing reflective-room master remains a physical/bounce-shell control and is not reused as the sole visible architecture toggle.

## UI architecture

The N-panel gains one focused `Studio` / `Architecture` section rather than scattering new controls across unrelated panels.

Cyclorama controls:

- distance in meters;
- look;
- finish;
- visible.

Architecture controls:

- Walls;
- Floor;
- Ceiling;
- Door;
- Window Frame;
- Window Glass.

Native transforms/material nodes remain editable directly in Blender. The panel does not duplicate standard Blender transform/material controls.

## Natural Light v2 architecture

Natural-light work follows studio geometry because the window, cyclorama, walls and floor define what daylight actually illuminates.

Required modes:

- helper-free Pure HDRI;
- Physical Sky modes;
- managed Sun only where the selected mode requires directional sun;
- portal is sampling-only and has zero emitted energy;
- artificial studio lights can be disabled independently;
- Build and ordinary preset switching never download assets.

Only the selected HDRI is loaded lazily after explicit availability/user intent rules are satisfied.

## Playback architecture

Playback policy is independent from artistic motion choice.

Scene settings expose separate product and camera playback policy:

- `ONCE`;
- `LOOP`;
- `PING_PONG`.

Changing playback updates the existing action/keyframe/cycle behavior without accumulating actions, modifiers or transforms. Reapplying the same motion + playback pair is idempotent.

## Asset provenance architecture

Every active external asset constant is represented in a machine-readable provenance inventory containing at minimum:

- stable asset id;
- upstream source URL;
- human-readable asset name;
- license and attribution requirement;
- bundled / remote-only / cached state;
- expected file type;
- checksum or other validation information when available;
- distribution permission status.

Fast tests fail when a new active URL is introduced without matching provenance metadata.

## Product Quality architecture

Product Quality begins only after 0.0.16 P0 is integrated. The diagnostic object remains a test fixture, not the visual benchmark.

Each procedural mockup has:

- real-world-ish dimensions and proportions;
- non-destructive bevel/subdivision policy appropriate to the form;
- clean shading/normals;
- predictable origin and bottom plane;
- a measurable geometry hierarchy compatible with Auto Fit and camera framing;
- material slots with starter materials appropriate to the mockup;
- no network dependency;
- bounded polygon/modifier cost suitable for interactive studio work.

Mockup generation must be deterministic and idempotent. Choosing another mockup replaces only AWFUL-owned mockup data and never user-mounted products.

## Test architecture

### Fast/pure contracts

Use pure tests for:

- cyclorama distance bounds;
- profile placement math;
- look/finish mapping;
- visibility role groups;
- playback policy mapping;
- provenance completeness;
- mockup dimension/policy metadata where Blender is not required.

### Packaged Blender runtime

The exact final ZIP is installed into an isolated Blender 5.2.1 profile. Runtime phases extend the current verifier with focused contracts:

- `studio_geometry` for #7/#21;
- `natural_light` for #9;
- `playback` for #8;
- `assets` for #23 when runtime behavior is involved;
- `product_quality` when the 0.0.17 slice begins.

For visual-changing work, the runtime also records deterministic reference renders/metrics under #4 after structural GREEN exists. Structural/runtime correctness remains distinct from visual approval.

## Integration order

1. #7 + #21 Studio geometry/architecture in one branch because both own the same physical stage/room surfaces.
2. #9 Natural Light v2 after geometry roles and visibility semantics stabilize.
3. #8 Playback because it is largely independent from geometry and lighting.
4. #23 provenance before release packaging is declared complete.
5. #3/#5/#10/#12 runtime/performance/release reconciliation.
6. #4 visual evidence/baselines for the completed visual slices.
7. Final 0.0.16 exact-ZIP native repository/update verification.
8. 0.0.17 Product Quality mockups/material starters.

## Completion definition

A slice is complete only when:

1. acceptance criteria are mapped to tests;
2. the new test is observed failing for the intended missing behavior;
3. implementation makes the targeted test pass;
4. broader fast suite passes;
5. exact built ZIP passes the relevant Blender 5.2.1 runtime on Windows and Ubuntu;
6. no ownership/offline/lifecycle regression is introduced;
7. issue contains evidence and commit SHA;
8. Notion status reflects the verified implementation;
9. the branch is reviewable and merged into `feature/extension-foundation` only after its gates are green.
