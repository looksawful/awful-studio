# AWFUL STUDIO model preview

Internal Storybook catalog for canonical 3D assets.

## Local use

```powershell
cd preview
npm ci
npm run storybook
```

Production verification:

```powershell
npm test
npm run storybook:build
npm run smoke
```

## Catalog

The generated catalog contains only current canonical assets:
- iPhone 17 v30
- iPad Pro 11 M5 v6
- iPad Pro 13 M5 v6
- MacBook Pro 14 M5 v1
- Studio Rig v01 objects and LODs
- White Studio v2
- Dark Neon v2
- Loft Daylight v2

Device and Studio Rig GLBs are served from their canonical repository runtime paths. Scene GLBs under `generated/scenes/` are preview-only exports from the canonical Blender scene candidates.

## iPhone web presentation

The iPhone viewer adds Home, Off, Lock, Website and Resume display states. Website and Resume are live mobile captures of the public portfolio; the browser frame and lock artwork are illustrative. `public/screens/provenance.json` retains capture dimensions and source URLs.

The display raster is 1206 × 2622, with a 402 × 874 logical viewport at 3×. At Apple's specified 460 ppi this corresponds to 66.59 × 144.78 mm, matching the canonical 66.57 × 144.79 mm active area within rounding. UI is mapped without cover cropping or screen-vertex rescaling; the inherited Home plate remains the official reference artwork.

`iphone-presentation.mjs` keeps the mapped/emitting material only on the front face, aligns visible front optics to the visible island, calibrates cavity/fastener reflections, and adds a correctly oriented display-sized area emitter. The canonical GLB now has a separate dark display-edge material and deep grille backings with an embedded weave normal map and exported UV tangents. The helper accepts both the original mesh and GLTFLoader's split-primitive group. Visual front-optic alignment remains a web override; the source hardware datum and LOW_DRAFT delivery stage are preserved.

## Publishing

`main` deploys the static Storybook through GitHub Pages. Working branches only validate the preview through `Extension QA`; they do not create permanent preview branches.
