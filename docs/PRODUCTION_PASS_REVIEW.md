# AWFUL STUDIO Production Pass Review

Date: 2026-09-18
Branch: `agent/production-pass`
Blender qualification runtime: 5.2.1 LTS, build `9e2066aef7ef`

## Result

The Production Pass is complete on its isolated branch and has not been merged
to dev or main.

Blender + AWFUL STUDIO remains the only source of truth. Unreal stays a
downstream local viewer/QA surface and is not required by the Extension.

## Delivered workflow

- task-oriented Studio / Product / Lighting / Camera / Environment / Output /
  Diagnostics workflow;
- read-only actionable diagnostics;
- capability-driven iPhone/iPad/MacBook controls;
- deterministic still-camera views: Hero, 3/4 Left/Right, Side, Wide 50,
  Detail 120 and Top 3/4;
- production lighting shortcuts over canonical presets: Product, Soft, Flash,
  Edge, Accent, Gobo, Window and Glass;
- explicit Physical Sky / HDRI / offline environment status;
- safe Preview / Final Output / Post UI that leaves the user's render backend
  and final settings alone;
- reproducible Full Studio review scene and bounded review-render tool.

## Verification evidence

Fast/static gate:

```text
Ran 194 tests
OK
```

Repository doctor: PASS.

Canonical exact-ZIP verifier: PASS.

```text
Package: awful_studio-1.0.0.zip
SHA-256: 56c3656026056684a0edd654eb33e9bde69966a0e159d6b309c45d9489a2c49b
Package source: official Blender Extension build
Blender processes: 8
GPU autoconfig during Build: false
```

Verified phases: historical, install, reopen, migrate, lighting, camera,
studio_geometry, natural_light, asset_workflow, performance, diagnostics,
post_pipeline, playback, product_quality and product_placement.

Measured runtime includes initial Build at about 0.391 s and median Rebuild at
about 0.285 s in this qualification run.

## Bugs found and fixed during final QA

- missing HDRIs now preserve the user's selected intent while rendering through
  Physical Sky fallback when the optional asset is unavailable;
- lazy HDRI nodes stay muted until a real image is loaded, eliminating Cycles
  missing-image warnings;
- lighting changes batch environment side effects so a single preset change
  applies the environment once rather than repeatedly;
- interactive environment loads run under explicit scene ownership;
- the required diagnostic material survives save/reopen without leaking an
  extra material on Rebuild;
- ownership cleanup now ignores Blender's synthetic fake user while still
  preserving datablocks that have real external users.

## Visual review artifact

`A:\awful\PURE_REF\awful-studio-review-2026-09-18\08_BlenderPlugin\FullStudio.blend`

The review scene is validated, uses HERO_85 / STATIC, and packs the active
`fish_hoek_beach_2k.hdr` inside the blend file.

Final review renders are 800x1000 at 16 samples:

- `product.png` — COMMERCIAL_3LIGHT;
- `accent.png` — DUAL_COLOR_STRIP;
- `gobo.png` — HARD_GOBO;
- `window.png` — WINDOW_BALANCED with KLOPPENHEIM intent.

The representative scene remains bounded at 86 objects, 12 collections,
13 materials, 15 lights and zero actions across the review looks. Lazy HDRI
loading changes the image count only between 2 and 3 as expected.

The working branch is intentionally left unmerged for owner review.
