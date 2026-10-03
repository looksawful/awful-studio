# iPhone 17 post-ship dimensional audit

Date: 2026-10-02  
Audited model tree: `394951d61e21868cafe448d1543b82c10db14e39` (same tree as pre-squash `4af33de6399c7ffab68e48898347bccacd1fd46d`)  
Scope: standard iPhone 17 v30 external geometry, controls, camera stack, front hardware datum, bottom I/O, screen envelope.

## Sources

Primary authority:
- Apple Developer, **iPhone 17 Dimensional Drawings**, dated 2025-09-09: https://developer.apple.com/download/files/accessories/dimensional-drawings/iphone-17.pdf
- Apple Developer, **Dimensional Drawings index**: https://developer.apple.com/accessories/dimensional-drawings/
- Apple, **iPhone 17 Technical Specifications**: https://www.apple.com/iphone-17/specs/
- Apple Support, **iPhone 17 Repair Manual**: https://support.apple.com/en-us/123029
- Apple Support, **iPhone 17 Internal View, Orderable Parts, and Exploded View**: https://support.apple.com/en-us/123034

Secondary sources were searched only as a sanity check. No secondary dimensional claim overrides the Apple drawing.

## Method

- Read the Apple dimensional drawing directly, including rendered drawing sheets.
- Inspected the shipped Blender source and the actual generated `.blend` geometry.
- Dumped world-space bounding boxes and centers from Blender 5.2.1 with `--factory-startup`.
- Used Wolfram Language for numerical deltas, PPI verification, and Apple corner-profile error.
- Treated Apple keepout dimensions as keepouts, not automatically as visible artwork or physical aperture dimensions.

## What matches Apple very closely

| Feature | Apple drawing | Shipped model | Delta |
|---|---:|---:|---:|
| Product width | 71.45 mm | 71.45 mm | 0.00 |
| Product length | 149.61 mm | 149.61 mm | 0.00 |
| Product thickness | 7.95 mm | 7.95 mm | 0.00 |
| Cover glass | 69.45 × 147.61 mm | 69.45 × 147.61 mm | exact |
| Display active area | 66.57 × 144.79 mm | 66.57 × 144.79 mm | exact |
| Rear camera center X | 13.62 mm from left | 13.62 mm | exact |
| Rear camera 1 center Y | 13.62 mm from top | 13.62 mm | exact |
| Rear camera 2 center Y | 31.34 mm from top | 31.34 mm | exact |
| Rear camera outer diameter | 16.00 mm | 16.00 mm | exact |
| Rear optical diameter | 13.62 mm | 13.62 mm | exact |
| Flash center | 30.41 × 22.48 mm | 30.41 × 22.48 mm | exact |
| Flash diameter | 6.28 mm | 6.28 mm | exact |
| Camera housing outer bounds | X 1.18–26.06, Y 1.34–43.62 mm | same derived bounds | exact |
| Camera housing inner bounds | X 3.79–23.45, Y 3.97–40.99 mm | same derived bounds | exact |
| Front hardware keepout base | 20.75 × 5.12 mm | metadata/datums 20.75 × 5.12 mm | exact |
| Front hardware center from top | 7.79 mm | 7.79 mm | exact |
| Receiver keepout width | 14.02 mm | 14.02 mm | exact |
| Apple logo size | 15.75 × 19.34 mm | 15.75 × 19.34 mm | exact |
| Apple logo center from top | 73.18 mm | 73.18 mm | exact |

The physical active area plus 1206 × 2622 raster resolves to ~460.0005 ppi, matching Apple's 460 ppi specification.

### Corner profile

The body is not a naive rounded rectangle. The shipped generator has an Apple-specific Bézier corner profile and a regression test against Apple's Detail A points:

`(0,19.23), (0.02,14.53), (0.48,9.87), (2.26,5.56), (5.56,2.26), (9.87,0.48), (14.53,0.02), (19.23,0)`.

Wolfram comparison of the generator Bézier against those eight points:
- max error: **0.0363 mm**
- mean error: **0.0129 mm**

This part is excellent for a visual/product mockup model.

## Findings that do not match the Apple drawing

### P0 / Major: rear camera stack is much too shallow

Apple sheet 1 explicitly gives:
- **1.78 mm** back glass → camera plateau
- **3.45 mm** back glass → camera glass

Shipped model:
- camera plateau top: **0.72 mm** above back glass
- camera glass top: **1.61 mm** above back glass
- even the outermost modeled rear stack only reaches **1.8125 mm** above back glass

Deltas:
- plateau: **-1.06 mm** (about 59.6% too shallow)
- camera glass: **-1.84 mm** (about 53.3% too shallow)
- outermost modeled stack vs camera-glass datum: **-1.6375 mm**

Equivalent total depth:
- Apple body + camera glass: **11.40 mm**
- shipped model to `CAMERA_n_GLASS`: **9.56 mm**

This is the largest geometry discrepancy in the audit.

### P0 / Major: bottom acoustic layout has the wrong count and spacing

Apple bottom drawing labels **8× Ø1.35 ports** total. The elevation shows:
- 3 acoustic ports on the microphone side
- 5 speaker ports on the speaker side
- 2 separate Ø1.50 screws

The shipped generator creates:
- 3 microphone apertures
- **6** speaker apertures
- 2 screws

So there is **one extra speaker hole**.

Apple dimensioned bottom landmarks:
- mic cluster first/last port centers: **19.71 / 24.22 mm**
- left screw center: **28.80 mm**
- USB-C opening edges: **31.23 / 40.22 mm**
- right screw center: **42.65 mm**
- speaker cluster first/last port centers: **47.23 / 56.25 mm**

Shipped model:
- mic centers from left: **17.525 / 20.625 / 23.725 mm**
- screw centers: **28.575 / 42.875 mm**
- USB-C cutter edges: **31.20 / 40.25 mm**
- speaker centers begin at **47.725 mm** and continue to an extra sixth opening at about **62.84 mm**

Implications:
- USB-C opening itself is excellent: edge error ≈ **0.03 mm**.
- screws are displaced ≈ **0.225 mm** outward.
- acoustic clusters are substantially mis-spaced, and the extra speaker port visibly climbs toward the rounded corner.

### P1 / Major-visual: side-control sizes are wrong even though their centers are right

Centers from product top are essentially exact (all ≈ +0.005 mm due to half-height arithmetic):
- Action: Apple 34.08, model 34.085 mm
- Volume +: Apple 48.23, model 48.235 mm
- Volume -: Apple 62.43, model 62.435 mm
- Side button: Apple 55.32, model 55.325 mm
- Camera Control: Apple 98.20, model 98.205 mm

But control sizes differ:

| Control | Apple drawing | Shipped model | Delta |
|---|---:|---:|---:|
| Action length | 2×3.45 = **6.90 mm** | **11.60 mm** | +4.70 |
| Volume button length | 2×5.60 = **11.20 mm** each | **9.20 mm** | -2.00 |
| Action/volume face width | **2.66 mm** | **2.56 mm** | -0.10 |
| Side button length | 2×8.85 = **17.70 mm** | **17.70 mm** | exact |
| Side button face width | **2.66 mm** | **2.56 mm** | -0.10 |
| Camera Control length | 2×8.55 = **17.10 mm** | **17.50 mm** | +0.40 |
| Camera Control face width | **3.03 mm** | **3.00 mm** | -0.03 |

The Action and Volume lengths are the important errors. Their vertical datums were copied correctly, but the visible button dimensions were not.

### P1: rear microphone X position is wrong

Apple Detail D:
- rear mic diameter: **Ø1.00 mm**
- X center from product left: **20.54 mm**
- Y center from product top: **22.48 mm**

Shipped model:
- X ≈ **22.675 mm**
- Y ≈ **22.505 mm**
- diameter: **1.00 mm**

Delta:
- X: **+2.135 mm**
- Y: **+0.025 mm**

The diameter and row are correct; the mic is horizontally too far toward the flash/right side.

## Conditional / documentation finding: SIM tray

Apple's dimensional drawing includes a SIM tray:
- center datum from top: **105.66 mm**
- length: **2×9.82 = 19.64 mm**
- width: **2.56 mm**

The shipped model has no SIM-tray geometry.

This is not automatically a defect because iPhone 17 hardware varies by market and eSIM-only variants exist. The model currently does not declare a regional variant, so this is a **variant-definition gap**:
- if the asset is intended as eSIM-only/U.S.-style hardware, document that;
- if it is intended as generic/global iPhone 17, add the SIM tray or provide regional variants.

## Front hardware / Dynamic Island

No new problem found in the front datum split:
- Apple's **20.75 × 5.12 mm** drawing is a camera/sensor keepout base, not the visible Dynamic Island silhouette.
- the physical hardware datum at **7.79 mm** is preserved in the model.
- the visible baseline Dynamic Island is correctly handled separately in presentation/runtime compositing.

This remains the correct architecture.

## Repair-manual cross-check

Apple's repair manual/exploded view independently confirms the expected hardware topology:
- rear camera assembly
- front camera
- top speaker
- main microphone
- USB-C connector
- bottom speaker
- enclosure

No topology conflict was found with the model's intended external parts. The discrepancies above are dimensional/placement issues, not a misunderstanding of what components exist.

## Recommended disposition

**Do not merge PR #119 to `main` yet.**

The post-ship audit found at least four geometry corrections worth doing before final production landing:
1. rear camera plateau/glass depth
2. bottom port count and spacing
3. Action/Volume button lengths and control widths
4. rear microphone X datum

Then:
- regenerate the same v30 line; do not create v31/v32;
- add drawing-derived tests for these exact callouts;
- rerun Blender/Khronos/preview/Storybook/browser gates;
- perform a focused Human Gate from the same front/back/side/bottom evidence angles.

## Confidence

High confidence:
- body/screen/camera XY datums
- camera protrusion discrepancy
- bottom port count
- side-control size discrepancy
- rear mic X discrepancy

Conditional:
- SIM tray, because it depends on regional hardware variant.

## Resolution candidate

The four high-confidence geometry findings were corrected in the existing v30 line, without a v31/v32 fork:

- rear camera external depth now targets Apple 1.78 mm plateau / 3.45 mm camera-glass protrusion;
- bottom I/O now uses 3 microphone + 5 speaker Ø1.35 ports, Apple X datums, Ø1.50 screws, and the existing centered USB-C opening;
- Action / Volume / Side / Camera Control visible dimensions now match the Apple side elevations while preserving their already-correct center datums;
- rear microphone center now uses Apple Detail D 20.54 × 22.48 mm, Ø1.00.

Regression coverage is at the exported compat-GLB seam. All four contracts were observed RED against the prior shipped tree before the fixes and are GREEN on the resolution candidate.

Fresh technical verification:
- fast suite: 204/204;
- Blender 5.2.1 LTS geometry contract with --factory-startup: GREEN;
- Khronos validator compat + Meshopt: 0 errors / 0 warnings;
- preview tests: 19/19;
- Storybook production build: GREEN;
- browser smoke: 11/11 canonical assets;
- targeted screen_website browser repro: correct state, zero console errors, zero failed responses;
- git diff --check: clean.

PR #119 remains HOLD/draft until focused Human Gate passes on the corrected rear, bottom, side and front views.
