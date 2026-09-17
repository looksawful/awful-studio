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

## Publishing

`main` deploys the static Storybook through GitHub Pages. Working branches only validate the preview through `Extension QA`; they do not create permanent preview branches.
