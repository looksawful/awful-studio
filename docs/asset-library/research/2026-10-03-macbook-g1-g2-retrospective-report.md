# MacBook Pro 14 M5 вЂ” full engineering retrospective, G1в†’G2 error route, DoD and handoff

Date: 2026-10-03
Repository: `looksawful/awful-studio`
Primary tracker: #52 в†’ #127 / #128 / #129
Draft delivery PR: #121
Current branch: `agent/129-geometry-calibration`
Review fixed point: `518bb25`
Current state: G1 rejected by human visual gate; G2 corrective work in progress; no merge/deploy.

## 1. Executive summary

The MacBook work began as a production-quality LOW model task: keep the real Apple envelope, build a working hinge, make the model reproducible, then improve the keyboard, trackpad, speakers, ports, underside, display and materials until the asset was visually credible and browser-ready.

The first half of the work succeeded structurally. The project established a deterministic Blender 5.2.1 build, a 103-angle hinge collision gate, closed-envelope validation, GLB/Meshopt delivery, runtime ownership rules, Storybook/Three.js inspection, screen-state behavior and increasingly detailed ports/deck construction.

The central failure was subtler: **the project gradually confused вЂњparametric and test-coveredвЂќ with вЂњdimensionally authoritative.вЂќ** Several internal positions and dimensions were estimated from images or inherited from old geometry, then encoded as constants and protected by tests. The tests proved internal consistency, but not physical correctness against the actual MacBook.

The userвЂ™s phone review exposed this. The closed model still read wrong: lid/rear assembly, hinge semantics, keyboard scale, trackpad, speaker fields, finger recess, feet/screws and other relationships did not agree with Apple references.

That rejection led to the correct architectural change: calibration first. Apple exact dimensions became global datums; official orthographic/product imagery became calibrated metric sources; repair documentation became topology/relationship evidence; the older May/Jestei model was demoted to visual-only reference. G1 attempted this transition but contained a bad deck homography and still promoted provisional measurements too early. G2 then corrected the raster-to-mm math and performed a full-surface audit.

The corrected deck math has now been independently reproduced by Wolfram and unit tests. However the current G2 worktree still has important review blockers: mixed-quality external facts are frozen under one provenance label, some tests are tautological, provisional display dimensions remain in production geometry, the canonical v1 manifest is stale, and the overlay generator does not yet project the actual Blender model onto Apple references.

The correct path is therefore not more visual tweaking. It is:
`per-fact provenance в†’ world-space Blender tests в†’ remove provisional display magic в†’ actual model orthographic overlays в†’ master rebuild в†’ canonical runtime rebuild в†’ Storybook/browser gate в†’ human phone/desktop approval`.

## 2. Evidence used for this report

This report separates four evidence classes.

### Repository / tracker evidence
- GitHub #52: original MacBook production foundation and LOW rescue.
- GitHub #127: hybrid visual master в†’ derived runtime specification.
- GitHub #128: hybrid deck master/runtime proof slice.
- GitHub #129: display/lid work, later amended to calibration-first.
- PR #121: current draft MacBook delivery.
- Git history and current worktree.
- Existing research: `docs/asset-library/research/2026-10-02-macbook-pro-14-m5-geometry-calibration.md`.
- Existing plan: `docs/superpowers/plans/2026-10-02-macbook-pro-14-m5-geometry-rebuild.md`.
- G2 audit: `assets/device_mockups/macbook_pro_14/evidence/g2_full_surface_audit/`.

### Apple primary sources
- MacBook Pro tech specs: https://www.apple.com/macbook-pro/specs/
- M5 model tech specs: https://support.apple.com/en-gb/125405
- M5 repair manual: https://support.apple.com/en-us/123173
- Apple Design Resources / Product Bezels: https://developer.apple.com/design/resources/
- Apple dimensional-drawings catalog: https://developer.apple.com/accessories/dimensional-drawings/

Important limitation: Apple publishes exact overall dimensions and extensive model/repair imagery, but the public dimensional-drawings catalog does **not** expose a full MacBook Pro M5 factory drawing/CAD. Hidden radii, wall thicknesses and several hinge/display section dimensions therefore cannot honestly be called manufacturer-exact.

### Runtime / test evidence
- Blender 5.2.1 LTS.
- Fast tests.
- Blender geometry validators.
- 103-angle hinge sweep.
- compatibility GLB + Meshopt GLB.
- Storybook/Three.js.
- current G2 candidate manifest.

### Mathematical independent check
Wolfram was used as an independent arithmetic/transform check, not as a geometry source. It reproduced the corrected raster scales, G1 inflation, active-display size and key deck measurements from the supplied Apple/source coordinates.

## 3. Original task and original Definition of Done

Issue #52 asked for a high-quality MacBook Pro 14-inch M5 mockup with:
- real external dimensions;
- functional opening/closing mechanics;
- convincing base/lid silhouettes;
- physical hinge geometry;
- keyboard, trackpad, speakers and ports that read as production LOW;
- non-manifold-free base/lid;
- collision-safe hinge presets;
- evidence renders and runtime delivery.

The original locked chassis envelope was already strong:
- width: 312.6 mm;
- depth: 221.2 mm;
- closed height: 15.5 mm.

One early вЂњlockedвЂќ value later proved wrong: issue #52 recorded active display as approximately 301.66 Г— 195.92 mm. The Apple native resolution and density are 3024 Г— 1964 at 254 ppi, which derives exactly to **302.4 Г— 196.4 mm**. This became one of the examples of why source/provenance needed to be explicit.

The original DoD was therefore mostly structural:
1. envelope within 0.01 mm;
2. `CTRL_HINGE` drives full lid assembly;
3. hinge collision-safe through presets;
4. zero non-manifold main shell edges;
5. Apple-like silhouette rather than slabs;
6. LOW-readable deck/trackpad/speakers/ports;
7. validation JSON + visual evidence.

That DoD was necessary but not sufficient: it did not require every visible component placement to be source-calibrated.
## 4. Chronological route: successful work, mistakes, corrections

### 4.1 Reproducible foundation вЂ” September 15вЂ“24

Key commits:
- `574e3e7` вЂ” reproducible MacBook release candidate.
- `83d43fa` вЂ” geometry/screen-state/hinge animation refinement.
- `9f5d74b`, `a2caa26`, `b7d6d84` and related acceptance commits вЂ” hinge clearance and deterministic evidence.

Successful decisions:
- generation became deterministic instead of relying on a manually polished blend;
- main chassis dimensions and manifold checks became executable contracts;
- hinge collision was reproduced as a real defect rather than waved away visually;
- a dedicated RED-capable Blender validator was added;
- hinge repairs were tested mechanically before being accepted visually.

This was the right pattern: reproduce в†’ test RED в†’ minimal fix в†’ rerun actual Blender.

### 4.2 Web display duplication вЂ” September 25

Human review found the screen image appearing on more than one display surface.

Root cause:
the web export contained both `SCREEN_CONTENT` and `SCREEN_GLASS` as visually active screen-like surfaces.

Good correction:
reuse the already-proven iPhone invariant: one active screen-content surface in runtime. The exporter, not the geometry, was the narrowest correct seam.

Commit:
- `492bc0c` вЂ” keep MacBook web screen single-surface.

Lesson:
cross-device invariants should be generalized into explicit runtime contracts when they are truly universal.

### 4.3 Stale packaged geometry вЂ” October 1

A more serious delivery failure was found: the web builder could package a cached generated blend without regenerating the current geometry or revalidating hinge state.

Root cause:
a source fingerprint proved source identity, but did not prove that the packaged geometry had just been rebuilt from that source.

Correction:
- regenerate source;
- validate hinge;
- stop packaging on Blender-script failure;
- only then export/package.

Commit:
- `a7237f2` вЂ” regenerate and validate MacBook web deliveries.

This was a strong architectural improvement. It changed the evidence from вЂњsource hashes look currentвЂќ to вЂњthe exact delivered asset was freshly rebuilt and mechanically validated.вЂќ

### 4.4 Screen glare / material responsibility split

Controlled renders showed that the screen content itself reflected studio lights. The image surface and cover glass were both doing optical work.

Correction:
- content became dark-base + emissive image + zero content specular;
- separate cover glass retained reflections.

Commit:
- `b3a22f0`.

This decision survived later architecture work and became part of the master/runtime display strategy: content and glass have distinct responsibilities.

### 4.5 Deck / ports / normals / full hinge sweep

Commit:
- `55505e9`.

Improvements:
- 78-key estimated ANSI layout;
- Touch ID;
- recessed ports;
- connector interiors;
- speaker apertures;
- outward normals;
- bounded viewer depth;
- hinge validation expanded to every integer angle 0вЂ“102.

Good decision:
move from five named hinge samples to all **103 integer positions**. That removed a major blind spot and later remained a protected invariant.

Limitation:
key sizes, grille pattern, local radii and several placements were still LOW estimates. The system was becoming highly validated internally, but reference calibration had not caught up.

### 4.6 Construction pass and own-site display

Commits:
- `bfa73e3`;
- `cfd6817`.

Added:
- actual looksawful.ru capture;
- revised shells;
- dished keys and function icons;
- recessed trackpad;
- physical speaker apertures;
- camera layers;
- front recess;
- underside panel/fasteners;
- vents.

Important regressions caught by dedicated checks:
- vent proxies expanded external width to roughly 313.07 mm;
- complete closed assembly was about 16.205 mm high while component-only checks still passed.

Correction:
test the **complete assembled world-space bounds**, including feet/logo/secondary geometry, not just individual shell dimensions.

That lesson remains central to the final DoD.

### 4.7 Hinge concealment: locally successful, globally misleading

Commit:
- `83cb90a`.

A RED check showed reflective pivot ends exposed. 60 mm matte shrouds were introduced to hide them, plus a separate lower display rail. The existing 103-angle gate remained green.

At the time this was a successful visual/mechanical fix.

Later G2 research showed the deeper problem: AppleвЂ™s вЂњDisplay Hinge CoversвЂќ are small corner plates. Our `HINGE_COVER_L/R` objects had become long cylindrical shrouds and conflated:
- pivot/barrel;
- hinge cover plate;
- external clutch/rear display geometry.

So this checkpoint is a useful example of a **locally correct fix on a semantically wrong part model**. It solved вЂњbright rods visibleвЂќ but not вЂњhinge construction matches the product.вЂќ

### 4.8 Port quality

Commit:
- `1bd3453`.

Good decisions:
- centralize the port roster in `port_layout.py`;
- use Apple side imagery as reference without pretending the cropped image width equals chassis depth;
- use USB-C nominal dimensions only as a local interface datum;
- explicitly label the result as visual LOW, not compliance/factory CAD;
- add rows of contacts and curved socket walls;
- retain 2.6 mm recess-depth tests.

This work remains largely reusable because it was already careful about evidence strength.

## 5. Architectural pivot: #127 / #128

The May Jestei MacBook looked substantially better in shading, normals, keycap shape, speaker treatment, material hierarchy and mechanical read, but it was older and unsuitable as dimensional truth.

The chosen architecture was therefore:

**one authoritative visual master в†’ one automatically derived runtime asset.**

Rules that survived review:
- current M5 dimensional/mechanical skeleton is retained only where actually verified;
- richer authored surfaces are allowed in the master;
- runtime is derived, never hand-maintained in parallel;
- speaker/legend/microdetail can move to baked normal/alpha/AO/roughness when that preserves perceptual read;
- semantic anchors are separate from render-mesh count;
- existing Blender в†’ GLB в†’ Meshopt в†’ manifest в†’ Storybook pipeline is extended rather than replaced;
- the May model is visual/construction reference only, never donor mesh or dimensional authority.

Issue #128 proved this seam on the deck and committed the hybrid pipeline:
- `0776792` вЂ” prove hybrid MacBook deck pipeline;
- `23bd684` вЂ” scope runtime visibility to owned objects;
- `cdc35a1` вЂ” exact build provenance;
- `1d521ea` вЂ” refreshed hybrid delivery evidence.

This is one of the strongest successful decisions in the whole effort. It avoids maintaining two models and keeps browser optimization downstream of the authoritative asset.

## 6. Why calibration became mandatory

Human review challenged a hidden assumption in #127: вЂњcurrent parametric skeletonвЂќ was being treated as authoritative for too many internal dimensions.

The 2026-10-02 research changed the authority model to:

1. **APPLE_EXACT** вЂ” Apple publishes the number.
2. **APPLE_CALIBRATED** вЂ” measured from official Apple planar imagery after calibration.
3. **APPLE_RELATIONAL** вЂ” Apple repair docs prove identity/topology/relation, not necessarily millimetres.
4. **DERIVED** вЂ” formula over stronger facts.
5. **PROVISIONAL** вЂ” current value not yet revalidated.

Only 1вЂ“4 may be frozen, and even relational evidence must not be silently upgraded into invented metric precision.

The global datum became the chassis:
- origin = chassis plan center;
- +X right;
- +Y rear/hinge;
- +Z up.

Keys, trackpad, camera and ports are children of that datum, never local independent origins.
## 7. G1 calibration: what worked

Commits:
- `c5fdd55` вЂ” source-backed G1 calibration;
- `0bb259a` вЂ” mobile G1 review story;
- `bc5b639` вЂ” build MacBook geometry from G1 calibration;
- `34a4b49` вЂ” refine live runtime;
- `2768041` вЂ” refresh G1 live artifacts.

Strong G1 ideas:
- register primary Apple assets with hashes;
- separate exact/calibrated/relational sources;
- derive metric values from image measurements;
- preserve tolerances and coordinate frames;
- produce review overlays;
- expose the result in Storybook on the phone;
- keep PR #121 draft pending human review.

The phone review itself was crucial. It prevented automated GREEN from being mistaken for product fidelity.

## 8. G1 failure route

### 8.1 Wrong deck transform

The official Apple 2Г— deck raster has straight chassis edges at approximately:
- X: 108 вЂ¦ 1027 px;
- Y: 23 вЂ¦ 673 px.

Using the exact Apple 312.6 Г— 221.2 mm envelope gives:
- X scale = **0.3401523395 mm/px**;
- Y scale = **0.3403076923 mm/px**;
- axis-scale residual в‰€ **0.0457%**.

The G1 homography instead used four inset points near rounded corners as if they represented the physical rectangle.

When the real external raster edges are passed through that transform, the implied chassis becomes approximately:
- **318.3023 mm wide**;
- **226.5938 mm deep**.

Inflation:
- +5.7023 mm width = about **+1.824%**;
- +5.3938 mm depth = about **+2.438%**.

This single transform error contaminated downstream deck measurements.

### 8.2 Process failure: provisional became production

The G1 report itself marked measurements as:
- `PROVISIONAL`;
- `frozen=false`;
- awaiting human overlay approval.

But the generator consumed those values into a live/release-candidate geometry before approval.

That is the more important process defect: the policy existed but was not enforced at the production boundary.

### 8.3 Why automated tests did not save us

Many tests asserted values derived from the same flawed transform. They proved:
- formulas were repeatable;
- generator and contract agreed;
- counts and internal relationships stayed stable.

They did **not** prove:
- the chosen image points represented the actual chassis;
- the transform was physically correct;
- the generated Blender model overlapped the Apple product in orthographic projection.

Hence the user could see errors immediately while the suite remained mostly green.

## 9. G2 full-surface audit

Commit:
- `518bb25` вЂ” Record MacBook G2 full-surface audit.

Confirmed exact/strong anchors:
- chassis 312.6 Г— 221.2 Г— 15.5 mm;
- display 3024 Г— 1964 at 254 ppi в†’ **302.4 Г— 196.4 mm**;
- 78-key ANSI count.

Corrected calibrated deck values include:
- keyboard aggregate в‰€ 274.124 Г— 111.007 mm;
- keyboard well в‰€ 280.540 Г— 116.157 mm;
- trackpad в‰€ 129.598 Г— 80.993 mm;
- trackpad center Y в‰€ -64.659 mm;
- trackpad front gap в‰€ 5.445 mm;
- Touch ID center в‰€ (128.288, 82.692) mm;
- speaker lattice = **15 Г— 114 per side**;
- speaker pitch в‰€ 0.921 Г— 0.926 mm.

The earlier G1/live geometry had:
- keyboard too wide;
- trackpad too large and too far forward;
- front trackpad gap too small;
- Touch ID shifted;
- speaker lattice count/pitch/position wrong;
- front finger recess far too narrow;
- bottom feet too small and misplaced;
- outer screws too far inward;
- Apple logo too small;
- closed display/rear assembly not flush;
- hinge-cover semantics wrong.

## 10. Wolfram validation

Wolfram independently reproduced:
- deck scales 0.3401523395 / 0.3403076923 mm/px;
- G1 implied chassis 318.3023 Г— 226.5938 mm;
- active display 302.4 Г— 196.4 mm;
- trackpad 129.598 Г— 80.993 mm and 5.445 mm front gap;
- speaker pitch about 0.921 Г— 0.926 mm;
- keyboard / well / Touch ID reprojection results.

Wolfram is being used as a **calculation verifier**, not as a product-dimension authority. Product facts still come from Apple.

## 11. Current G2 implementation state

Current worktree after `518bb25` contains uncommitted G2 implementation work.

Fresh review evidence:

### GREEN
- targeted G2 tests: 11/11;
- Blender deck/ports validation: PASS;
- Blender construction validation: PASS;
- complete closed assembly: approximately 312.600 Г— 221.200 Г— 15.504 mm;
- hybrid deck validation: PASS;
- screen material validation: PASS;
- hinge sweep: all 103 integer positions 0вЂ“102 PASS;
- G2 candidate source revision matches its candidate manifest;
- preview tests: 13/13;
- Storybook production build: PASS;
- live G2 Storybook route returns HTTP 200;
- browser accessibility tree exposes controls, LODs, projection, screen and lid animation.

### RED / BLOCKING
1. canonical MacBook fast slice is **47/48**, failing the v1 manifest/source-revision drift contract;
2. `G2_EXTERNAL_FACTS` freezes mixed-strength estimates as one `APPLE_RELATIONAL / MEDIUM_HIGH` block;
3. some external tests compare contract constants to expected constants rather than proving generated Blender world-space geometry;
4. production generator still consumes provisional display/bezel/glass/gasket/lower-rail values;
5. current overlay tool mostly draws contract values over Apple references instead of projecting the actual Blender model;
6. G2 human visual acceptance has not happened;
7. browser screenshot capture was not completed because the Opera Browser Connector lost its AI connection, even though the page itself loaded.

Therefore current status is **REQUEST CHANGES**, not DONE and not merge-ready.
## 12. Final Definition of Done

The corrected DoD is deliberately stricter than the original #52 checklist.

### Geometry truth
- exact Apple envelope preserved;
- exact active display preserved;
- every frozen visible macro fact has source, method, tolerance, frame and confidence;
- PROVISIONAL/UNVERIFIED values cannot feed authoritative production geometry;
- relational evidence stays relational unless a calibrated metric measurement exists.

### Generated-model proof
- tests inspect actual Blender world-space geometry;
- keyboard/trackpad/Touch ID/speaker/finger recess/feet/screws/hinge relations are asserted from generated objects;
- complete closed assembly bounds pass;
- 103-angle hinge sweep passes;
- no regression to ports, ownership, anchors or screen states.

### Cross-source proof
- actual model geometry is projected into official top/front/left/right/bottom/deck/display references;
- residuals are reported in source-aware tolerances;
- views that cannot support metric truth are explicitly labelled qualitative/UNVERIFIED.

### Master/runtime proof
- one authoritative master;
- compatibility GLB and Meshopt generated from that source state;
- canonical v1 manifest drift check GREEN;
- no manual second model;
- no manual manifest-hash patching.

### Visual/runtime proof
- fixed comparison: May visual reference | previous AWFUL baseline | corrected candidate;
- Storybook/Three.js loads exact final assets;
- screen on/off and lid animation work;
- payload, triangles, render meshes and materials recorded;
- phone and desktop human review explicitly accept geometry and surface quality.

### Release control
- PR #121 stays draft until final human gate;
- no deployment/merge before acceptance.

## 13. Progress snapshot

Progress percentages are evidence-based completion of each named phase, not schedule estimates.

- [100%] Primary-source research and source hierarchy
- [65%] Correct G2 geometry/provenance contract
- [45%] Authoritative Blender master rebuild
- [75%] Derived runtime packaging
- [20%] True modelв†’reference orthographic overlays
- [70%] Browser/Storybook verification
- [0%] Final human visual acceptance

Weighted planning indicator: **57.25%**.

This number is intentionally lower than вЂњhow much code exists,вЂќ because final correctness is gated by provenance, model-projection evidence and human acceptance.

## 14. Tools, plugins and skills: what each actually did

### Research / source-driven development
Used to establish the evidence hierarchy and prevent вЂњlooks plausibleвЂќ from becoming geometry truth.

Primary sources:
- Apple tech specs;
- Apple model-specific imagery;
- Product Bezel;
- Apple repair manual;
- Apple key-service documentation;
- Apple dimensional-drawings catalog.

Outcome:
the project moved from hand-tuned coordinates to explicit source classes and tolerances.

### EngineeringSuite / AskMatt family
Used as the engineering router across:
- research;
- domain/spec work;
- planning;
- TDD/implementation;
- review;
- source-driven verification;
- handoff.

Most important contribution:
keeping implementation and review as separate gates rather than letting the authorвЂ™s confidence stand in for evidence.

### Ponytail
Cross-cutting anti-overengineering constraint.

Useful consequences:
- keep the existing v1 Blenderв†’GLBв†’Meshoptв†’Storybook pipeline;
- do not create a second exporter;
- do not maintain a second runtime model manually;
- use bake/alpha/normal proxies for repetitive detail where perceptually equivalent;
- preserve semantic anchors separately from render meshes.

Important boundary:
Ponytail may remove complexity, but it must not lower visible fidelity or erase mechanical/product constraints.

### Review
The fixed-point Standards + Spec review was decisive.

It caught:
- provenance overstatement;
- tautological tests;
- provisional display values still feeding production;
- wrong вЂњlid part equals complete closed planвЂќ contract;
- stale canonical v1 manifest;
- contract overlays being mistaken for model overlays.

Review prevented the next round of geometry work from being built on another incorrect authority layer.

### Plan
The plan changed from aesthetic refinement to:
`sources в†’ calibration в†’ geometry contract в†’ RED math/model tests в†’ master rebuild в†’ runtime в†’ orthographic evidence в†’ browser в†’ human gate`.

Current corrective plan:
`docs/superpowers/plans/2026-10-03-macbook-g2-corrective-plan.md`.

### Codex Engineering Guardrails
Applied as:
- evidence before completion claims;
- read-only review when reviewing;
- repository standards + explicit issue/spec as authority;
- fresh tests for current state;
- no вЂњDONEвЂќ based on stale runs;
- production changes and verification treated as different operations.

### Wolfram
Used for independent numerical validation:
- pixel/mm scale;
- old-transform inflation;
- display-size derivation;
- deck geometry arithmetic;
- progress weighting.

It did not replace Apple sources.

### Remote Desktop Commander
Primary execution transport to Titan for:
- reading/editing repo files;
- Git status/log/diff;
- Python/OpenCV scripts;
- Blender 5.2.1 runs;
- tests;
- Storybook build;
- local HTTP checks.

### GitHub connector
Used to inspect:
- #52, #127, #128, #129;
- PR #121;
- issue comments and historical checkpoints;
- acceptance requirements and status.

### Web research
Used only for current first-party Apple verification. No secondary article was needed for geometry authority.

### Python + OpenCV
Used for:
- raster measurement;
- connected components / edge analysis;
- Hough/circle/line investigations;
- homography inversion and reprojection;
- calibration and residual experiments.

### Blender 5.2.1
Canonical geometry/runtime evidence environment:
- world-space bounds;
- manifold checks;
- hinge sweep;
- deck/port validators;
- screen material;
- master/runtime asset generation.

### glTF / Meshopt
Existing runtime packaging path. Current candidate manifest reports:
- compatibility GLB;
- Meshopt variant using `@gltf-transform/cli 4.5.0`;
- preserved hinge control and required nodes;
- one authoritative master в†’ derived runtime.

### Storybook / Three.js
Human/browser inspection surface:
- phone-friendly viewer;
- Meshopt/Compat selection;
- texture/wireframe/clay/normals;
- perspective/orthographic;
- fixed views;
- lid animation;
- screen state.

This is the perceptual gate after mathematical geometry, not a substitute for calibration.

### Game Development Studio
Its asset-production discipline вЂ” inspect source bytes, normalize only when needed, validate outputs, package with provenance вЂ” matches the project philosophy.

However the `game-dev` CLI was **not** used for this MacBook work. Introducing it as a parallel asset pipeline would contradict #127 and the Ponytail constraint. The existing Blender/GLB pipeline remains canonical.

### AgentMarkup
Reviewed for applicability. It is for machine-readable website metadata such as llms.txt, JSON-LD, crawler policy and Agent Cards. It has no role in MacBook geometry or GLB validation, so it was intentionally not introduced. This is recorded as a scope decision, not a missing step.

### DevRecap
A valid DevRecap run exists for 2026-10-02 through 20:03 local session coverage:
- port/USB-C refinement;
- hybrid deck pipeline;
- runtime visibility scoping.

It does **not** cover the later G1 build, phone rejection, G2 audit or current review. No fresh bundled DevRecap runner was exposed on Titan during this report pass, so the older run is used only inside its evidence window rather than being stretched into a false вЂњcomplete dayвЂќ recap.

### Handoff
Used to produce a compact continuation document that points to this report, the corrective plan, issue #129 and exact next actions instead of duplicating the full history.

### Session Exporter
Used separately for a faithful current-conversation export. Earlier skipped/compacted ranges are explicitly marked unavailable rather than reconstructed as verbatim transcript.

### Progress Percent Plans
Used to show step completion based on artifacts/checks, not elapsed time or wishful вЂњalmost doneвЂќ estimates.

## 15. Approaches we are keeping

1. **Apple exact envelope as global datum.**
2. **Official orthographic imagery as calibrated evidence.**
3. **Repair docs for topology and relationships.**
4. **May/Jestei as visual benchmark only.**
5. **One authoritative master в†’ derived runtime.**
6. **Existing v1 delivery path, no parallel exporter.**
7. **Math/world-space tests before visual approval.**
8. **Actual browser/phone inspection after math.**
9. **Full 103-angle hinge gate.**
10. **Provenance and tolerance per frozen fact.**
11. **Bake/proxy repetitive detail when visually equivalent.**
12. **Human review can reject a green automated candidate.**

## 16. Approaches explicitly rejected

- treating parametric coordinates as truth because they are in code;
- using rounded-corner inset points as chassis calibration corners;
- freezing a whole family of dimensions under one weak provenance label;
- testing constants only against constants;
- contract-generated overlays masquerading as model-validation overlays;
- estimating hidden manufacturing dimensions and presenting them as official;
- copying May model dimensions/mesh;
- creating a second runtime/model pipeline;
- weakening drift guards to make delivery green;
- polishing materials before disputed geometry is settled;
- merging PR #121 before the LOW/G2 human gate.

## 17. Exact next actions

1. Split `G2_EXTERNAL_FACTS` into per-fact provenance records.
2. Demote unsupported hinge/display dimensions to PROVISIONAL.
3. Write Blender world-space RED tests for actual generated objects.
4. Replace lid-part equality with closed-assembly silhouette relation.
5. Build actual Blender-projection orthographic overlays.
6. Rebuild deck/external geometry from accepted facts only.
7. Resolve display Product-Bezel calibration without invented precision.
8. Rebuild G2 candidate and rerun 103-angle/structural gates.
9. Rebuild canonical v1 delivery; restore source-revision/hash GREEN.
10. Run preview + Storybook + live browser checks.
11. Present fixed Apple/model and May/old/new comparisons.
12. Human phone/desktop geometry approval.
13. Only then continue final materials/normals/runtime optimization.
14. PR #121 stays draft until all above gates pass.

## 18. Bottom line

The project did not fail because вЂњthe model was bad.вЂќ It failed because a strong engineering pipeline was wrapped around some weak geometric premises.

The useful part is that the failure became diagnosable:
- mechanics are strong;
- build provenance is strong;
- runtime delivery architecture is strong;
- master/runtime strategy is strong;
- Apple source hierarchy is now explicit;
- corrected deck mathematics is independently verified.

The remaining job is to make the **geometry authority layer as rigorous as the pipeline around it**. Once that is done, the visual polish work becomes much safer and much cheaper because we stop polishing the wrong shape.
