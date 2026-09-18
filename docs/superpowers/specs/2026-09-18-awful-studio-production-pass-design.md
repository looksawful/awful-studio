# AWFUL STUDIO Production Pass Design

Date: 2026-09-18
Status: owner-approved design pending written-spec review
Target runtime: Blender 5.2.1 LTS
Base: committed HEAD of the current device-quality line, isolated in `agent/production-pass`

## Purpose

Finish AWFUL STUDIO as a polished Blender-native product/advertising studio without creating a second product in Unreal or replacing Blender-native controls with a parallel abstraction layer.

This Production Pass sits on top of the accepted 1.0.0 stable core, the Visual/Product Completion design, and the 1.1.0 release design. It does not replace their ownership, lifecycle, packaging, or release rules.

The primary outcome is simple: a Blender 5.2 user should be able to build a studio, choose or mount a product, create a strong product-lighting setup, frame it, preview it, validate it, save/reopen it, and understand failures without knowing AWFUL internals.

## Product boundary

Blender + AWFUL STUDIO is the only source of truth for scene construction, assets, lighting, camera, environment, motion, post, validation and export intent.

Unreal remains a local downstream viewer/QA surface only. It may ingest exported scene data and display it, but it must not become a second preset system, second camera rig authority, or second studio editor. Unreal project files are not part of this production-pass Git scope.

## Scope

The pass covers seven product surfaces:

1. **Studio shell** — build/rebuild/remove, architecture, cyclorama, room controls and stable scene status.
2. **Product workflow** — bundled mockups/devices, selected-user products, auto fit, placement, LOD, screen replacement, orientation and MacBook hinge.
3. **Lighting** — production-ready photographic preset families using native Blender lights and existing studio geometry.
4. **Camera** — product-bounds framing, practical lens/view presets, focus/DOF and motion without transform drift.
5. **Environment** — HDRI, physical sky, window/background and hybrid studio/world workflows with explicit network boundaries.
6. **Output** — preview profiles, render-ready state, optional post pipeline and clear output preparation.
7. **Diagnostics** — visible health/status, actionable validation and release-grade verification evidence.

The pass also repairs current delivery-contract drift for changed device generators, but does not silently promote LOW_DRAFT or RELEASE_CANDIDATE assets to DELIVERY quality.

## Non-goals

- No monolithic rewrite of `core/legacy.py` merely for cleanliness.
- No custom renderer or duplicate transform/material UI.
- No automatic GPU/backend changes.
- No hidden network downloads.
- No invented HIGH device geometry or fake production claims.
- No Unreal-side product feature development.
- No release publication/tagging as part of this implementation slice; the accepted 1.1.0 release design owns publication.

## UX architecture

The N-panel becomes a task-oriented control surface while native Blender editors remain authoritative.

### Main status

The top panel shows a compact studio summary rather than only action buttons:

- studio state: not built / ready / validation issue;
- active product source: diagnostic / bundled mockup / bundled device / user selection;
- active lighting preset;
- active camera preset/motion;
- active environment;
- output/preview mode;
- last validation result when available.

Primary actions are context-sensitive: Build Studio before construction; Use Selected / Generate Product after build; Validate always when meaningful.

### Panel order

The stable workflow order is:

1. Studio
2. Product
3. Lighting
4. Camera
5. Environment
6. Output
7. Diagnostics / Setup

Advanced or destructive actions stay collapsed. Routine work must not require opening Diagnostics.

## Product workflow design

A user product or bundled asset follows one predictable path: choose source → mount/generate → fit → review → shoot.

- **User object:** select one or more unmanaged roots and choose Use Selected. AWFUL mounts only those hierarchies and never acquires ownership of user data.
- **Procedural mockup:** choose the mockup and Generate / Replace Product. Replacement deletes only AWFUL-owned mockup data.
- **Bundled device:** choose device and LOD explicitly, generate it, then expose only controls that the selected device supports.

Device controls remain capability-driven:

- iPhone/iPad: orientation and screen artwork where supported;
- MacBook: hinge preset plus screen artwork;
- LOD/stage are shown separately so quality status cannot be confused with polygon level.

Auto Fit uses product bounds and is deterministic. Reapplying the same asset and preset must not accumulate scale, transforms, materials, actions or hidden objects.

The current two failing fast tests are treated as delivery-manifest drift from active generator changes. Their repair must update fingerprints/revisions through the existing reproducible delivery path, not by weakening verification.

## Lighting design

Lighting remains native Blender lighting. AWFUL exposes photographic intent and repeatable presets, not replacements for Blender light controls.

The production set must cover at least: neutral product/three-light, soft beauty, hard/flash, rim or silhouette, accent/color, gobo/graphic, window/daylight, natural/HDRI and hybrid studio + world.

Each preset defines only AWFUL-managed light state and remains inspectable/editable with native Blender controls. Switching presets is idempotent and must not leave stale color, energy, visibility, animation or light-group state from the previous look.

Preset quality is judged both structurally and visually. Structural tests prove the intended rig/state; reviewed reference previews prove that presets are meaningfully distinct and useful for product photography.

## Camera design

Camera framing is product-bounds driven and independent of the camera's previous transform.

The production camera surface provides practical still views such as hero/front, three-quarter left/right, side, detail/tele, wide and top three-quarter. Lens choices use photographic focal lengths such as 50 mm, 85 mm and 120 mm while respecting the existing 36x24-style policy where applicable.

Applying a camera preset twice, or returning to it after another preset, must produce the same transform and lens state. Camera motion remains a separate concern from still framing and keeps the existing Once / Loop / Ping-Pong policy.

Focus/DOF controls should use native Blender camera properties and targets. AWFUL may set a useful default target/distance, but must not hide the resulting camera state from Blender.

## Environment design

Environment controls present illumination and camera-visible background as distinct concepts.

HDRI use remains explicit and provenance-safe. Base studio operation is offline. Missing optional HDRIs report availability and a clear download/retry action rather than triggering network access during Build or preset switching.

Physical Sky, HDRI and hybrid modes must leave artificial studio lighting independently controllable. Window glass/background visibility remain explicit, not implied by unrelated master toggles.

## Output and preview design

AWFUL exposes a small set of explicit output intents:

- Fast Preview for interaction;
- Quality Preview for look development;
- Final-ready state for the user's chosen Blender render path;
- optional transparent-background and post-pipeline preparation where supported.

These modes may adjust viewport/render workflow settings owned by AWFUL, but must not silently change the user's Cycles device/backend or overwrite unrelated render configuration.

The existing Post Pipeline remains opt-in. Building it must remain ownership-safe, idempotent and save/reopen safe.

## Diagnostics design

Validation becomes a user-facing diagnostic report rather than a binary status-bar message.

Checks are grouped by Studio, Product, Lighting, Camera, Environment, Output and Assets. Results use clear OK / warning / error semantics with short actionable explanations. Diagnostics must distinguish an optional unavailable asset from a broken required studio component.

The report should expose current scene schema, ownership identity/status, active product source, device stage/LOD when applicable, missing optional assets, camera framing state, light-rig state and post-pipeline state.

Diagnostics do not auto-fix destructive problems. Repair actions remain explicit operators such as Rebuild, Fetch Assets or system reset.

## Code boundaries

New workflow/UI logic should live in focused modules rather than extending the 125k legacy module further. Existing legacy functions remain the stable implementation surface unless a scoped change is required for correctness.

A thin UI/orchestration layer may call existing modules such as `product_quality`, `device_asset_loader`, `camera_policy`, `natural_light`, `post_pipeline` and `runtime_performance`. New modules must have one clear responsibility and avoid a second scene-state model.

## Data flow

The canonical interactive flow is:

1. user explicitly builds or opens an existing AWFUL scene;
2. AWFUL reads scene-owned state and exposes current status;
3. user chooses/mounts product and AWFUL computes bounds/placement;
4. lighting, camera and environment presets mutate only their owned systems;
5. preview/output settings prepare Blender-native rendering;
6. Validate inspects the resulting state without destructive mutation;
7. save/reopen preserves all intended state and unmanaged user data.

Export/viewer flow is one-way: Blender scene → explicit export/sync artifact → local viewer. The viewer may report import problems but never feeds authoritative preset state back into Blender.

## Error handling

Expected user errors return operator cancellation plus a concise explanation, not Python tracebacks in normal use. Examples include selecting only managed controls as a product, requesting a device-only operation on a procedural mockup, missing screen artwork, unavailable optional HDRI, stale delivery manifest or unsafe ownership ambiguity.

Unexpected internal exceptions are recorded in diagnostics/last-error state and remain visible for debugging. Safety wins over guessing: if ownership cannot be proven, AWFUL refuses destructive mutation.

## Test strategy

Every production-code change follows repository TDD: targeted failing contract first, observed RED, minimum GREEN, then broader verification.

Fast tests cover pure policy, UI contracts, capability mapping, idempotence metadata, delivery fingerprints and diagnostics formatting where Blender is not required.

Real Blender 5.2.1 runtime covers build/rebuild/remove, product mounting/replacement, lighting/camera/environment application, output profiles, save/reopen, lifecycle and ownership behavior. Runtime-dependent claims are never made from static source inspection alone.

Visual-changing work also receives reviewed deterministic preview evidence. These images are evidence of look quality, not a brittle universal exact-pixel gate.

The final candidate must pass the existing exact-ZIP lifecycle path: build Extension ZIP, validate it, install it in an isolated Blender 5.2.1 profile, enable, disable, re-enable, restart/reopen, exercise required runtime contracts and audit the same artifact that would ship.

## Integration and concurrency

The Production Pass lives in its own short-lived branch/worktree so current iPhone/iPad generator edits are not mixed with UI/runtime work. Device-delivery changes are integrated only after their owning work is committed and verified.

Do not duplicate the existing bootstrap, verifier, delivery-manifest or release machinery. Use the canonical paths documented in `STATE.md` and `AGENTS.md`.

The implementation order is:

1. restore a green baseline by reconciling current device manifest drift once the owning generator revisions are stable;
2. add status/diagnostic contracts and task-oriented panel structure;
3. polish Product workflow and capability-driven device controls;
4. qualify lighting looks with structural + visual evidence;
5. harden camera framing/focus and idempotence;
6. polish Environment and Output workflows;
7. create canonical Full Studio review scene/previews;
8. run full fast + packaged Blender runtime + exact-ZIP lifecycle verification.

## Completion criteria

Production Pass is complete only when all of the following are true:

- fast suite is fully green on the integrated source;
- relevant Blender 5.2.1 runtime suites are green in the current work session;
- Build/Rebuild/Remove and save/reopen preserve unmanaged data;
- bundled products/devices expose only valid capabilities and their delivery manifests verify;
- lighting presets are structurally valid, visually distinct and reviewed;
- camera presets are deterministic and bounds-driven;
- environment/network behavior remains explicit and offline-safe;
- preview/output modes do not silently alter the user's render device/backend;
- diagnostics surface actionable state without destructive auto-fixes;
- the canonical Full Studio scene is usable without developer tooling;
- the exact built Extension ZIP passes lifecycle verification;
- Unreal remains a local downstream viewer and contains no required source-of-truth behavior.

Success means a user can install the Extension, build a studio, choose a product, create a convincing product setup, understand what is active, validate it, save/reopen it and continue working using normal Blender controls without reading the codebase.
