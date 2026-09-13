# AWFUL STUDIO Manual Smoke / Post-MVP Design Amendment

Date: 2026-09-11
Status: owner-directed design amendment for issue #39
Target runtime: Blender 5.2.1 LTS
Base design: `docs/superpowers/specs/2026-09-11-studio-visual-product-completion-design.md`
Working branch: `agent/39-smoke-blockers`

## Goal

Resolve all release-blocking defects observed in the 0.0.17 manual smoke while preserving the accepted Extension lifecycle, ownership, offline, native-Blender and exact-ZIP release guarantees. This amendment also incorporates the owner's post-MVP workflow decisions so the fixes converge toward the intended product rather than merely suppressing symptoms.

The defective 0.0.17 candidate with SHA-256 `cc3a404ecc00e82e82716c91aece6260affd3c30d92bff1330b540965e489540` is now a reproducible baseline, not a publishable release candidate.

## Global constraints

- Blender 5.2 LTS; qualification uses exact Blender 5.2.1.
- TDD is mandatory for every production change: RED -> verify RED -> GREEN -> full regression -> refactor.
- Historical 0.0.15 evidence stays byte-identical.
- Build/Rebuild/Remove remain explicit and owner-scoped.
- Base Build remains offline and never downloads assets.
- Native Blender controls remain authoritative where Blender already owns the concept.
- AWFUL never silently rewrites user GPU backend/device preferences.
- No render/GPU CI test becomes mandatory without explicit opt-in.
- No tag/public release until a new exact candidate passes Windows + Ubuntu packaged runtime, native repository install, and a repeated manual smoke.

## 1. Product placement, support surfaces and Auto Fit

### Default support behavior

- Generated and mounted products default to the round pedestal.
- The product bottom plane must contact the pedestal top exactly within runtime tolerance. No cosmetic floating gap.
- The pedestal is enabled by default but remains user-disableable.
- Pedestal size may adapt to the product within bounded, visually reasonable limits; it does not scale without limits.

### Motion-specific support behavior

- `SPIN_Z` is allowed to float rather than being forced into physical contact for the whole motion.
- Motions that rotate through X/Y/Tumble may automatically lower/remove the pedestal rather than lifting the product excessively. This preserves readable motion without the pedestal intersecting the rotating product.
- Grounding logic and camera framing remain separate systems.

### Auto Fit

Auto Fit remains a high-level workflow action and may coordinate:

- product scale;
- product placement;
- support/pedestal fit;
- camera framing.

Each result must still be derivable and testable independently. The camera frames the full object with small safe margins by default. Bottle/Jar/Can default to a medium hero composition. Phone/Tablet orientation/framing may depend on the selected camera preset.

Auto Fit must never introduce a product/support gap when the current motion/support policy expects contact.

## 2. Motion playback and Timeline synchronization

### Playback policy

Existing artistic motion and playback policy remain independent. Product and Camera continue to expose `ONCE`, `LOOP`, and `PING_PONG`.

### Preview range semantics

AWFUL synchronizes Blender's Preview Range, not the global render frame range.

- `ONCE`: exactly one keyed action span.
- `LOOP`: two complete action spans so repetition is visible.
- `PING_PONG`: one complete forward + backward cycle.
- Product and Camera ranges are combined by union when both are active.
- Camera motion does not destructively retime Product motion and vice versa.
- If the current frame remains inside the new Preview Range, keep it unchanged.
- If the current frame falls outside the new range, clamp it into the valid range.
- FPS defaults to 24 but remains user-editable.
- Motion duration is preset-specific rather than forced to one universal frame count.

### UI controls

Provide both:

- `Fit Timeline to Motion`;
- `Reset Timeline`.

Automatic synchronization runs when generated Product/Camera motion or playback policy changes. The buttons remain useful for restoring intent after manual user edits.

## 3. Lighting architecture: Hybrid by default, World and camera BG decoupled

### Default regime

Hybrid Studio + World is the primary general product-lighting regime. Some preset families are allowed to override this intentionally:

- flash-oriented looks may default to Studio-only;
- cinematic setups may default to Studio-only or another explicit preset-owned regime;
- presets must declare the intended lighting regime rather than relying on accidental toggle combinations.

### Hybrid energy policy

When Studio + World are both active, World contribution is deliberately reduced to a fill/environment role. The starting target is approximately 20-30% of standalone World strength, then calibrated from structural/runtime evidence. Studio light levels are not globally reduced as a shortcut.

Lighting presets may adapt to material class. Glass should generally receive softer/controlled illumination to avoid destructive overexposure. More specialized reflection/rim behavior can remain a later targeted preset improvement; do not force it into the first blocker fix.

The current cyan/magenta character remains a stylized preset family, not the visual identity of all default lighting presets.

### Separate illumination and visible background

World illumination strength and camera-visible background brightness are separate controls.

The World shader must use an `Is Camera Ray` split so:

- non-camera rays use the lighting Background branch;
- camera rays use an independently controlled camera Background branch;
- `BG` only shows/hides/adjusts the camera-visible environment;
- toggling `BG` never changes the environment energy illuminating the product.

Expose both user controls in the AWFUL Environment UI:

- `World Light Strength`;
- `Background Brightness`.

This follows Blender's native ray-path model instead of faking exposure with scene color-management changes.

## 4. HDRI assets, downloads and diagnostic magenta

### Download policy

All reviewed active HDRIs are downloadable together through `Download All HDRIs`. Manual single-HDRI download may remain internally useful but is not the primary owner-selected workflow.

After successful download the asset status becomes Ready; it does not need to auto-switch the user's current environment.

If an HDRI is unavailable, use the Physical Sky fallback for usable operation. The selected HDRI intent remains visible so the user can retry after fixing connectivity/permissions.

### Blender magenta semantics

Do not suppress Blender's standard magenta missing-texture diagnostic. It remains a legitimate Blender diagnostic state.

The test contract is stricter: an AWFUL-controlled happy path that is expected to have a valid texture must never silently reach magenta. Runtime tests should inspect image availability/load state and world-node assignments directly rather than trying to assert pixels or replacing Blender's diagnostic behavior.

### Network permission UX

- Blender Online Access is authoritative.
- AWFUL keeps explicit network consent, but after first user confirmation may persist that consent in the Extension preferences.
- If Blender Online Access is disabled, AWFUL clearly explains the exact problem and provides a button to open the relevant Blender Preferences page.
- Errors are shown in full technical detail because this is a technical Blender tool; the operator also exposes compact status/icon state in the Environment panel.
- Environment status is shown primarily as an icon/state rather than a large permanent diagnostic block.

Redirects are not accepted broadly. A redirect is allowed only after observed/verified Poly Haven behavior is captured in a RED test and the final host/path remains within reviewed provenance policy.

## 5. Post Pipeline remains an optional professional feature

The feature stays. It is useful because Cycles Light Groups permit relighting individual light contributions in compositing without re-rendering the scene.

### User-facing behavior

Rename/reframe the action as `Setup Post Pipeline` with a tooltip/description explaining that it prepares:

- Cycles Light Groups;
- render passes;
- managed compositor nodes;
- the Compositing workspace for review.

On success:

- show `Post Pipeline: Ready`;
- the action becomes an explicit rebuild/setup action rather than appearing inert;
- switch to the Compositing workspace when running interactively.

Repeated execution asks for confirmation before rebuilding and remains idempotent. Advanced UI may expose `Remove Post Pipeline`.

Unsupported Blender capability is an explicit `CANCELLED` result with a concrete explanation, never a silent no-op.

Build/Rebuild Studio keeps Post Pipeline opt-in and must not create it automatically.

## 6. Rendered viewport performance

### Observed scope

The primary slowdown is Rendered Viewport and camera navigation while Rendered Viewport is active. Solid playback is not reported as slow.

### Native device policy

AWFUL does not automatically choose CUDA/OptiX or rewrite Cycles device preferences. Blender requires the user to configure available Cycles devices and the scene render device. AWFUL may diagnose the current state and provide navigation/help, but device choice remains Blender/user-owned.

### Diagnostics

Add an Advanced diagnostics view that reports at minimum:

- active render engine and Cycles scene device;
- selected/available device information when safely queryable without changing it;
- preview samples;
- denoise state;
- Light Tree state;
- managed light count;
- object/mesh count;
- loaded image count and approximate bytes where available;
- depsgraph/update timings collected by explicit diagnostic action.

### Preview modes

Provide explicit `Fast Preview` and `Quality Preview` modes. Do not automatically reduce quality merely because animation playback starts.

Do not decide the exact settings by guesswork. First capture the baseline on the smoke scene, then change one factor at a time. Expected likely tuning targets include sample budget, viewport pixel size and denoise cost. Light Tree, HDRI quality or managed lights are not disabled automatically unless profiling proves they are the actual bottleneck.

Final render settings remain untouched by preview-mode changes.

## 7. UI / workflow amendment

The overall current UI is considered acceptable; this is targeted workflow clarification, not a redesign.

- Keep `Studio / Room / World` wording.
- The top-level workflow should prioritize preset-driven operation.
- Auto Fit needs clearer semantics; expose or label `Fit Product` / `Frame Camera` separation where useful while keeping the high-level Auto Fit workflow.
- Do not automatically switch to Camera View after Build.
- Do not automatically select a newly generated mockup.
- Move procedural mockup creation into a focused `Create Mockup` subpanel.
- Use compact Blender-native large buttons/grid for Bottle/Jar/Box/Can/Phone/Tablet rather than elaborate custom cards.
- Generate Mockup runs Auto Fit by default.
- Keep the current selected-product action unless smoke evidence shows the wording itself causes mistakes; do not churn labels for style alone.

## 8. Release priorities and blockers

All six smoke findings are release blockers. None may be deferred from the next candidate:

1. product/support placement;
2. Timeline synchronization;
3. hybrid lighting/background behavior;
4. HDRI download/asset reliability;
5. Post Pipeline correctness/clarity;
6. rendered viewport performance.

Post Pipeline and automatic Timeline synchronization are required for release. HDRI may remain manual-download driven; automatic background downloading is not required.

After fixes, repeat the affected manual smoke scenarios at minimum. Because the release candidate itself changes, exact ZIP install/update/save/reopen and the full cloud packaged-runtime/native-repository gate are still mandatory before publication even if every visual panel is not manually re-walked.

Keep version `0.0.17` during this corrective cycle unless release/version policy independently requires a bump before publication. No public 0.0.17 has been tagged yet, so fixing the candidate under the same version is valid.

After successful manual smoke, run one final cloud exact-candidate gate before tag/release/publication.

## TDD decomposition

Implementation is split into independent reviewable slices under umbrella issue #39:

1. baseline diagnostics/performance evidence;
2. product support/Auto Fit grounding;
3. Timeline Preview Range synchronization;
4. World/camera-BG split + Hybrid policy;
5. HDRI bulk download + explicit permission/error state;
6. Post Pipeline runtime contract + UI state;
7. evidence-driven preview optimization;
8. exact-candidate qualification and repeated manual smoke.

Each slice must first prove the current defect or missing behavior with a failing pure/runtime test. No production fix is committed before its RED is observed.
