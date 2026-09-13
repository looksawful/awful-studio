# AWFUL STUDIO - Apple device mockup foundation

This package is the blockout / blueprint stage for the device mockup pipeline.

## Included

- Dimensioned SVG + PNG blueprints for iPhone 17, iPad Pro 11-inch M5, iPad Pro 13-inch M5 and MacBook Pro 14-inch M5 Pro/Max.
- A 4-page PDF blueprint booklet.
- GLB blockouts that import directly into Blender.
- Blender 5.2 Python generators that create native collections, materials, screen objects, controllers and save `.blend` foundations.
- `build_blend_files.ps1` for Windows batch generation.
- `device_specs.json` with dimensional source metadata.

## Coordinate convention

Phone / iPad: X = width, Y = thickness, Z = height. Front display faces -Y. Product origin is the geometric center.

MacBook: X = width, Y = front-to-back depth, Z = up. Base origin is centered on the footprint. Rear hinge is +Y.

## Accuracy status

`V` = verified from Apple specs/dimensional drawings. `D` = mathematically derived from verified values. `E` = estimated for blockout and must be refined during LOW/HIGH modeling.

The iPhone and iPad sheets use Apple's current public tech specs plus Apple Developer dimensional drawings as dimensional references. The MacBook chassis envelope and display data are verified, while keyboard, hinge and exact port positions remain blockout estimates because a comparable public MacBook dimensional drawing is not provided on Apple's accessory dimensional-drawing page.

## Generate native .blend files on Windows

Open PowerShell in `blender/` and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build_blend_files.ps1
```

The script searches common Blender 5.x install paths and creates `generated_blend/` next to this folder.

## Next production gate

Do not start hero detailing until silhouette, corner radii, camera cluster, screen active area, hinge axis and major port/button positions have passed reference review.
