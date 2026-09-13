# Apple Device Mockups Production Plan

> Target repository: `looksawful/awful-studio`
> Integration branch: `feature/device-mockups`
> Asset branches: `asset/macbook-pro`, `asset/iphone-17`, `asset/ipad-pro`
> Blender target: 5.2 LTS

## Goal

Build a production-grade Apple device mockup library for AWFUL STUDIO using a full game-asset style pipeline: verified references -> concept/draft -> metric blockout -> production low-poly -> high/detail pass -> topology/LOD cleanup -> UVs -> procedural master materials -> baking -> validation -> plugin packaging.

The assets must work both as high-quality hero-render mockups and as manageable reusable plugin assets. The master files stay non-destructive and editable; delivery variants are optimized and baked.

## Target devices

### iPhone 17
- Base model, 6.3-inch display.
- Verified body dimensions: 149.6 x 71.5 x 7.95 mm.
- Key exterior features: contoured anodized-aluminum frame, Ceramic Shield 2 front, textured/color-infused glass rear, vertical dual-camera system, Dynamic Island, Action button, Side button, Camera Control, USB-C, speaker/mic perforations.

### MacBook Pro
- Primary master: MacBook Pro 14-inch, M5 Pro / M5 Max generation (2026).
- Verified closed outer dimensions: 312.6 x 221.2 x 15.5 mm.
- Prepare architecture so a 16-inch variant can reuse shared parts and materials later; verified 16-inch envelope is 355.7 x 248.1 x 16.8 mm.
- Hero details: display shell, lower unibody, hinge, keyboard, key legends, Touch ID key, speaker perforations, Force Touch trackpad, MagSafe 3, USB-C / Thunderbolt, HDMI, SDXC, headphone jack, feet, screen glass, camera notch, Apple logo.

### iPad Pro
- Master family: iPad Pro M5.
- 11-inch: 249.7 x 177.5 x 5.3 mm.
- 13-inch: 281.6 x 215.5 x 5.1 mm.
- Shared construction where possible; size-specific screen, body and connector placement remain driven by reference measurements.
- Hero details: enclosure, display glass, camera module, LiDAR/flash where applicable, microphones, four-speaker openings, top button, volume buttons, Smart Connector, magnetic Apple Pencil area, Thunderbolt / USB 4 port.

## Branch strategy

`main`
- Stable AWFUL STUDIO baseline.
- Receives only reviewed and validated mockup integration.

`feature/device-mockups`
- Integration branch for the whole device library.
- Owns shared documentation, naming rules, shared materials, validation scripts, packaging rules, catalog metadata and final integration.
- Device branches merge here first, never directly to `main`.

`asset/iphone-17`
- iPhone-specific references, Blender source, meshes, materials, bake outputs, previews and QA.

`asset/macbook-pro`
- MacBook-specific references, Blender source, hinge/pose system, keyboard system, meshes, materials, bake outputs, previews and QA.

`asset/ipad-pro`
- iPad-specific references, 11/13-inch variants, meshes, materials, bake outputs, previews and QA.

Recommended merge order: device branch -> `feature/device-mockups` -> integration QA -> `main`.

## Repository layout

Create the following structure on `feature/device-mockups` and mirror the relevant device subtree in each asset branch:

```text
assets/
  device_mockups/
    shared/
      materials/
      node_groups/
      hdri_presets/
      studio_rigs/
      screen_system/
      validation/
    iphone_17/
      refs/
      concept/
      blend/
        iphone_17_master.blend
        iphone_17_delivery.blend
      meshes/
      textures/
        source/
        baked/
      previews/
      metadata/
        asset.json
    macbook_pro/
      refs/
      concept/
      blend/
        macbook_pro_14_master.blend
        macbook_pro_14_delivery.blend
      meshes/
      textures/
        source/
        baked/
      previews/
      metadata/
        asset.json
    ipad_pro/
      refs/
      concept/
      blend/
        ipad_pro_master.blend
        ipad_pro_11_delivery.blend
        ipad_pro_13_delivery.blend
      meshes/
      textures/
        source/
        baked/
      previews/
      metadata/
        asset.json

docs/
  mockups/
    pipeline.md
    naming.md
    material-standard.md
    baking-standard.md
    qa-checklist.md
```

Large binary `.blend` and texture policy must be decided before assets become heavy. If regular Git becomes unreasonable, use Git LFS for `.blend`, EXR/TIFF and high-resolution baked maps. Do not silently commit multi-hundred-megabyte binaries into ordinary Git history.

## Global modeling standard

- Blender 5.2 LTS.
- Scene unit: Metric, Unit Scale 1.0. Model in real-world meters while all source dimensions are recorded in millimeters in metadata.
- +Z up, consistent front orientation across all three assets.
- Origin conventions must be identical between source and delivery assets.
- Apply object scale before bevel-sensitive finalization.
- Keep transforms and modifier ordering deterministic.
- No destructive boolean cleanup until the master version is approved.
- Keep repeated details instanced whenever practical.
- Keep render-facing screen surface as a dedicated material slot/object so mockup artwork can be replaced without editing geometry.
- Master assets remain non-destructive; delivery assets may contain applied/optimized geometry.

## Naming standard

Objects use stable semantic names, not Blender defaults.

Examples:

```text
IPH17_BODY_FRAME
IPH17_BACK_GLASS
IPH17_SCREEN_GLASS
IPH17_CAM_MAIN_LENS
IPH17_CAM_UW_LENS
IPH17_BUTTON_ACTION
IPH17_PORT_USBC

MBP14_BODY_LOWER
MBP14_DISPLAY_SHELL
MBP14_DISPLAY_GLASS
MBP14_HINGE_L
MBP14_HINGE_R
MBP14_TRACKPAD
MBP14_KEY_ESC
MBP14_PORT_HDMI

IPAD11_BODY
IPAD11_SCREEN_GLASS
IPAD11_CAM_BODY
IPAD11_PORT_USBC
IPAD13_BODY
```

Collections:

```text
00_REFERENCE
10_BLOCKOUT
20_LOW
30_HIGH
40_BAKE
50_DELIVERY
90_HELPERS
```

## Phase 0 - Reference and specification lock

Before modeling any final geometry:

1. Gather official Apple front/back/side imagery and technical specifications.
2. Gather Apple accessory dimensional drawings where available.
3. Build orthographic reference sheets for front, rear, left, right, top, bottom and 3/4 views.
4. Record every verified dimension in `metadata/asset.json` with source URL and date.
5. Classify dimensions as `verified`, `derived`, or `visual-estimate`.
6. Never mix visually estimated dimensions with verified values without marking them.
7. Build a feature inventory for each device so tiny details are not rediscovered at the end.

Acceptance gate:
- overall envelope matches official dimensions;
- all exterior controls and openings are identified;
- ambiguous details are explicitly marked instead of guessed into the master mesh.

## Phase 1 - Draft / concept

Purpose: decide what the mockup needs to support before spending topology on details nobody will see.

For each device create:
- silhouette draft;
- material breakup draft;
- hero-camera draft;
- close-up detail camera list;
- screen-replacement concept;
- exploded component diagram for modeling responsibilities;
- planned LOD breakdown.

Required render/use cases:
- clean front/product view;
- rear view;
- 3/4 hero view;
- side/profile view;
- close-up on ports/buttons/cameras;
- screen-content mockup shot;
- isolated transparent-background render;
- studio floor/background render.

MacBook additionally:
- closed;
- partially open;
- standard presentation angle;
- near-flat/open angle within physically plausible hinge limits.

Acceptance gate:
- silhouette proportions read correctly at thumbnail size;
- every planned close-up has enough planned geometry/material detail;
- asset remains usable as a mockup, not just as one locked beauty render.

## Phase 2 - Metric blockout

Build only the major masses using exact outer dimensions.

### iPhone
- body envelope;
- front glass;
- rear glass;
- camera island/lens envelope;
- major buttons;
- USB-C opening;
- display active-area placeholder.

### MacBook
- lower unibody envelope;
- display lid envelope;
- hinge axis;
- keyboard deck;
- trackpad;
- display active area;
- port placeholders;
- feet.

### iPad
- body envelope for 11 and 13 inch;
- front glass;
- screen active area;
- rear camera envelope;
- buttons;
- USB-C/Thunderbolt opening;
- Smart Connector placeholder.

Blockout validation:
- orthographic overlays;
- bounding-box measurement script;
- extreme close-up silhouette inspection;
- no modifiers used to hide incorrect source dimensions.

## Phase 3 - Production low-poly / base topology

The `LOW` mesh is the clean production cage, not a decimated high-poly corpse.

Rules:
- intentional quad topology around primary bevels and curved silhouettes;
- support loops only where deformation or silhouette requires them;
- hard-surface planar regions stay simple;
- repeated holes/perforations use arrays/instances or baked solutions depending shot distance;
- separate pieces for physically separate materials and moving parts;
- weighted normals only after topology and bevel logic are stable.

Initial LOD0 triangle guidance, to be validated by actual render quality:
- iPhone: roughly 30k-60k triangles excluding optional micro-geometry;
- iPad: roughly 25k-60k triangles per size;
- MacBook Pro: roughly 80k-160k triangles with hero keyboard geometry.

These are ceilings for discipline, not targets to inflate toward.

## Phase 4 - High/detail pass

Duplicate/derive the approved low/base cage into `HIGH` and add physically visible manufacturing detail.

Core modifier philosophy:
1. Mirror where symmetry is real.
2. Boolean for ports, camera apertures, speaker fields and mechanical cutouts.
3. Bevel with real-world scale-aware widths.
4. Subdivision only where curved continuity benefits from it.
5. Weighted Normal / custom normals after bevels when appropriate.
6. Array/Geometry Nodes for repeated speaker/microphone/perforation patterns.
7. Shrinkwrap only for controlled decal/label surfaces, never to repair bad primary forms.

### iPhone detail checklist
- contoured aluminum edge transition;
- front/rear glass seating;
- lens rings, lens glass, inner optical stack impression;
- flash and microphone openings;
- Dynamic Island/display cutout handling;
- Action/volume/side buttons;
- Camera Control geometry;
- antenna breaks;
- USB-C shell and internal darkness;
- speaker/mic perforations;
- subtle frame/glass seams.

### MacBook detail checklist
- lower chassis edge radii;
- lid shell radii;
- hinge barrels/slots and believable gap clearances;
- display glass and bezel/notch;
- keyboard well;
- individual keycaps as instanced geometry for hero LOD;
- key legends via decal/texture, not engraved geometry unless a macro shot proves it necessary;
- Touch ID key;
- trackpad seam and glass response;
- left/right speaker perforation fields;
- MagSafe 3;
- Thunderbolt ports;
- HDMI;
- SDXC;
- headphone jack;
- underside feet, screws and ventilation details visible in hero shots;
- Apple logo as controlled material/decal/inlay solution.

### iPad detail checklist
- thin unibody edge profile;
- display glass seating and bezel;
- rear camera assembly;
- flash/LiDAR/sensors appropriate to the target model;
- microphone openings;
- speaker arrays;
- top and volume buttons;
- magnetic Pencil attachment region cues;
- Smart Connector contacts;
- USB-C/Thunderbolt port;
- antenna/seam details where visible.

## Phase 5 - Topology cleanup and LODs

Produce three practical delivery levels where they materially help plugin performance:

- `LOD0_HERO`: full close-up geometry.
- `LOD1_STANDARD`: normal product-shot geometry, reduced micro-detail.
- `LOD2_PROXY`: layout/viewport asset with aggressive simplification and baked detail.

The master `.blend` retains HIGH + LOW + helper collections. Delivery `.blend` contains only the intended user-facing collections plus optional LODs.

Validation:
- no non-manifold geometry unless intentional/open by design;
- no accidental duplicate faces;
- no zero-area faces;
- consistent sharp-edge strategy;
- sensible object count;
- no hidden helper objects accidentally packed into delivery collections.

## Phase 6 - UV and texel strategy

Because these are premium mockup assets, use a hybrid material approach:

- procedural shaders for metal, glass and generic micro-surface;
- UVs for logos, legends, subtle manufacturing marks, fingerprints/smudges when enabled, and baked curvature/AO/normal data;
- screen content gets a dedicated UV/material system with predictable 0-1 mapping.

Texture targets:
- master/bake: 4K minimum for iPhone/iPad, 4K-8K for MacBook hero set depending atlas split;
- delivery: 2K/4K selectable where plugin packaging benefits;
- linear/non-color treatment enforced for normal, roughness, metallic, AO and masks.

Prefer multiple logical material sets over one absurd atlas that wastes resolution.

## Phase 7 - Procedural master materials

Build reusable shared node groups under `assets/device_mockups/shared/materials`.

Required masters:
- anodized aluminum;
- space-black aluminum variant;
- silver aluminum variant;
- ceramic/display glass;
- textured matte rear glass for iPhone;
- optical camera glass;
- black polymer/rubber;
- keycap material;
- screen emission/display shader;
- fingerprints/smudges overlay with strength toggle;
- micro-scratch overlay with strength toggle;
- edge/wear system disabled by default for pristine commercial mockups.

Material controls exposed to plugin/user:
- finish/color preset;
- roughness bias;
- fingerprint amount;
- micro-scratch amount;
- screen brightness;
- screen reflection strength;
- screen image input;
- optional logo visibility where licensing/presentation requires it.

## Phase 8 - Baking

Bake from HIGH to LOW/LOD delivery assets only after topology and UV approval.

Standard bake set:
- tangent-space normal;
- AO;
- curvature;
- thickness where useful;
- material ID masks;
- object/part masks where useful;
- roughness/metallic maps only when the delivery shader benefits from baking instead of live procedural evaluation.

Rules:
- use named bake cages or controlled ray distances;
- keep bake source and target collections explicit;
- test skewing on ports, lens rings, speaker holes and narrow bevels;
- no final bake until normal-map orientation is verified in Blender 5.2;
- save bake settings in metadata so output is reproducible.

## Phase 9 - Mockup functionality

The assets need to behave like tools, not museum pieces.

### Screen system
- dedicated `SCREEN_CONTENT` object/material;
- exact aspect ratio per device;
- single image input exposed to plugin;
- Fit / Fill / Stretch policy decided explicitly;
- optional screen corner mask;
- optional emissive and non-emissive modes;
- controlled glass reflections independent from content texture.

### MacBook posing
- hinge controller/empty;
- physically constrained rotation range;
- lid, glass and display content parented consistently;
- presets for Closed, 30°, 60°, 90°, 110°/presentation and near-flat if mechanically plausible.

### Orientation presets
For iPhone/iPad:
- portrait front;
- portrait back;
- landscape front;
- 3/4 left;
- 3/4 right;
- floating hero pose.

## Phase 10 - Lighting and preview scenes

Create shared preview rigs so every asset is judged under the same conditions.

Required rigs:
- neutral softbox studio;
- dark glossy studio;
- white seamless;
- edge/rim diagnostic rig;
- flat material/normal diagnostic lighting.

Every asset gets:
- beauty render;
- wireframe render;
- clay render;
- normal-map diagnostic;
- material-ball closeups for key materials;
- dimensional orthographic sheet.

## Phase 11 - QA

Automate what can be automated, because human eyeballs eventually decide that 7.95 mm is 'close enough' after midnight.

Automated checks:
- Blender version compatibility;
- missing external files;
- unapplied scale where forbidden;
- invalid object/collection names;
- non-manifold geometry report;
- negative scale report;
- missing UVs on delivery meshes;
- missing required material slots;
- missing screen material;
- texture path portability;
- oversized texture/package report;
- bounding-box dimensions within tolerance;
- modifier sanity and missing-node-group checks.

Visual checks:
- silhouette overlay against official refs;
- corner-radius feel;
- bevel width consistency;
- glass/metal transition quality;
- camera optics readability;
- port cutout quality;
- screen replacement correctness;
- no shading gradients on planar metal;
- no bake seams or cage projection errors.

Dimension tolerance targets:
- major body envelope: <= 0.1 mm deviation from verified dimensions where the source dimension is known;
- secondary visible features: <= 0.25 mm when measured data is available;
- visually derived micro-details: judged by multi-angle overlay and documented as derived/estimated.

## Phase 12 - Plugin packaging

Each delivery asset must expose a predictable manifest.

Example `asset.json` fields:

```json
{
  "id": "iphone_17",
  "label": "iPhone 17",
  "category": "device_mockup",
  "blender_min": "5.2.0",
  "source_file": "blend/iphone_17_delivery.blend",
  "collection": "IPHONE_17_DELIVERY",
  "screen_material": "MAT_SCREEN_CONTENT",
  "lods": ["LOD0_HERO", "LOD1_STANDARD", "LOD2_PROXY"],
  "variants": ["black", "white", "mist_blue", "sage", "lavender"],
  "units": "m",
  "source_dimensions_mm": [71.5, 149.6, 7.95]
}
```

Plugin integration requirements:
- append/link asset through a stable collection name;
- expose screen image replacement;
- expose finish preset;
- expose LOD/quality level;
- expose fingerprint/micro-scratch controls;
- expose MacBook hinge preset when relevant;
- generate/use preview thumbnail;
- package with relative paths only;
- keep source/master files separate from lightweight user delivery files.

## Device execution order

### First: iPhone 17
Reason: smallest scope, enough hard-surface complexity to validate naming, bevel, camera optics, glass, bake, screen and plugin metadata systems without the keyboard/hinge complexity of MacBook.

Milestones:
1. refs/spec lock;
2. draft/concept;
3. metric blockout;
4. base low topology;
5. high/detail;
6. LOD pass;
7. UV;
8. procedural material pass;
9. bake;
10. screen system;
11. QA;
12. delivery/package.

### Second: iPad Pro
Reason: reuses phone material/screen/bake lessons but introduces very thin large-surface shading and two size variants.

Milestones mirror iPhone plus variant generation and 11/13-inch consistency checks.

### Third: MacBook Pro
Reason: most complex asset. It introduces articulated posing, keyboard instancing, many port types, large flat surfaces, speaker perforations and more aggressive LOD concerns.

Milestones mirror previous assets plus hinge controller, key system, port suite and closed/open validation.

## Review gates

No phase advances merely because geometry exists.

Gate A - Reference Lock
- official dimensions recorded;
- feature inventory complete;
- orthographic references ready.

Gate B - Blockout Approval
- silhouette and measured envelope correct;
- major feature placement correct.

Gate C - Low/Base Approval
- topology clean;
- bevel strategy viable;
- parts separated logically.

Gate D - High Detail Approval
- hero closeups hold up;
- no modifier-induced shading failures;
- all visible physical details represented by geometry or intentional texture solution.

Gate E - UV/Bake Approval
- no overlaps except deliberate stacks;
- no visible bake errors;
- screen UV exact and reusable.

Gate F - Material Approval
- metal/glass/optics read correctly in neutral and dark lighting;
- material controls are reusable across assets.

Gate G - Delivery Approval
- plugin asset loads with no missing dependencies;
- screen replacement works;
- presets work;
- dimensions validated;
- package size acceptable;
- previews generated.

## Commit discipline

Commit per meaningful, reviewable milestone instead of after every mouse twitch.

Suggested messages:

```text
chore(mockups): add verified iphone 17 references
feat(iphone17): add metric blockout
feat(iphone17): build production base topology
feat(iphone17): add camera and port detail pass
feat(iphone17): add UV and bake setup
feat(iphone17): add procedural material set
feat(iphone17): package delivery asset

feat(ipad): add metric 11 and 13 inch masters
feat(macbook): add 14 inch metric blockout
feat(macbook): add hinge and keyboard systems
feat(mockups): integrate shared screen material system
qa(mockups): add geometry and package validation
```

## First execution batch

Work begins on `asset/iphone-17`.

1. Create the device folder skeleton.
2. Save official technical specs/reference URLs.
3. Build a dimension manifest.
4. Build orthographic reference boards.
5. Create `iphone_17_master.blend` with standardized collections/units/origin.
6. Create the exact 149.6 x 71.5 x 7.95 mm blockout envelope.
7. Add display, back glass, camera and button placeholder volumes.
8. Create validation output for bounding dimensions.
9. Produce front/back/side/3-4 clay previews.
10. Review blockout before production topology begins.

The same pipeline is then reused rather than reinvented for iPad and MacBook.