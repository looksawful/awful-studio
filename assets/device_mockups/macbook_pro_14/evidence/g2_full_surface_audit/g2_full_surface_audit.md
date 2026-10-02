# MacBook Pro 14 M5 — G2 full-surface geometry audit

Status: **RED**. Live phone review rejects G1 as a geometry acceptance gate.

## Source hierarchy

- **A0** — exact Apple-published numeric datum.
- **A1** — official Apple orthographic image calibrated against A0.
- **A2** — official Apple repair relation or calibrated repair image.
- **B1** — interface/industry standard used only as a local datum.
- **U** — unverified; public evidence is insufficient to freeze the value.

Apple's current Dimensional Drawings catalog does not publish a MacBook Pro M5 manufacturing drawing/CAD. The audit therefore combines exact Apple specs, official orthographic product imagery and Apple repair imagery. Hidden manufacturing dimensions remain UNVERIFIED rather than guessed.

## Exact anchors that are already correct

| Datum | Apple | Current | Verdict |
|---|---:|---:|---|
| Chassis width | 312.6 mm | 312.6 mm | GREEN |
| Chassis depth | 221.2 mm | 221.2 mm | GREEN |
| Closed height | 15.5 mm | 15.504 mm validation | GREEN |
| Active display | 302.4 × 196.4 mm | 302.4 × 196.4 mm | GREEN |
| ANSI key count | 78 | 78 | GREEN |

## Root cause: G1 deck transform is invalid

On the official Apple 2× keyboard image the straight chassis edges resolve at approximately x=108..1027 and y=23..673. Apple's exact 312.6 × 221.2 mm envelope therefore gives:

- x scale: **0.340152 mm/px**
- y scale: **0.340308 mm/px**
- axis-scale residual: only **~0.046%**

The old G1 homography maps those same external edges to approximately **318.30 × 226.59 mm**. It inflated the chassis plane by **+5.70 mm width** and **+5.39 mm depth** because inset points around rounded corners were treated as the physical chassis rectangle.

That transform cannot remain a geometry authority.

## Confirmed geometry errors

| Part / relation | Corrected Apple target | Current model | Delta / problem | Confidence |
|---|---:|---:|---|---|
| Keyboard aggregate | 274.12 × 111.01 mm | 278.75 × 111.39 mm | +4.63 mm width | HIGH |
| Keyboard well | 280.54 × 116.16 mm | 284.80 × 117.55 mm | +4.26 / +1.39 mm | HIGH |
| Trackpad | 129.60 × 80.99 mm | 131.94 × 82.81 mm | +2.34 / +1.82 mm | HIGH |
| Trackpad center Y | -64.66 mm | -66.47 mm | 1.81 mm too far forward | HIGH |
| Trackpad front gap | 5.45 mm | 2.72 mm | ~2.72 mm too small | HIGH |
| Pad vs recess X | both 0 | pad 0; recess +0.581 mm | datum mismatch | HIGH |
| Touch ID center | (128.29, 82.69) mm | (130.33, 84.25) mm | +2.04 / +1.56 mm | HIGH |
| Speaker lattice | 15 × 114 | 12 × 109 | wrong count | HIGH |
| Speaker pitch | ~0.921 × 0.926 mm | 1.0 × 1.0 mm | too coarse | HIGH |
| Speaker center X | ±148.05 mm | ±149.55 mm | ~1.50 mm too far outward | HIGH |
| Closed display/top-case | flush relation | lid panel stops 8.5 mm before rear; current cover still ~4.85 mm short | exposed rear ledge | HIGH |
| Hinge covers | ~20 mm corner plates at x≈±130 mm | 60 mm sleeves at x=±108.3 mm | wrong size/place/part representation | MEDIUM-HIGH |
| Front finger recess | ~54.2 mm | 36 mm | ~18.2 mm too narrow | HIGH |
| Bottom feet | ~16.5–18.1 mm diameter; ~20–22 mm side inset | 10.4 mm; 18 mm side inset | too small and misplaced | MEDIUM-HIGH |
| Outer bottom screws | ~3–9 mm side inset | 15 mm side inset | much too far inward | MEDIUM-HIGH |
| Lid Apple logo | ~37 × 45 mm visual bbox | 27.68 × 34 mm | materially undersized | MEDIUM |

## Important semantic error in the hinge

Apple's repair material calls the blue corner parts **Display Hinge Covers**. They are small plates at the rear corners. Our objects named `HINGE_COVER_L/R` are 60 mm cylindrical shrouds centered much farther inboard. This is not just a dimensional miss: the current model conflates different mechanical parts.

The next master must separate:

1. actual pivot / hinge bracket,
2. small hinge-cover plates,
3. external rear display/clutch geometry,
4. top-case rear edge / vent-antenna relation.

## Do not freeze these yet

Current public evidence is not strong enough to make the following exact constants:

- 8.3 mm base shell / 4.7 mm lid split;
- current 1.845 mm residual `GAP`;
- outer corner radii;
- 307.2×204.2 bezel, 307.6×204.6 glass, 309.3×207 gasket;
- 3.4 mm lower rail;
- exterior vent-slot dimensions;
- exact port centers/opening dimensions beyond current local-ruler evidence.

The current generator consuming G1 values while its own evidence says `PROVISIONAL / frozen=false` is itself a contract failure.

## Required RED contracts

- external deck silhouette reproduces 312.6 × 221.2 mm before measuring subparts;
- trackpad and recess share the same X datum;
- trackpad size/position/front gap follow corrected A1 calibration;
- keyboard/well bounds follow corrected A1 calibration;
- speaker grille is 15 × 114 with calibrated pitch and nonzero side margin;
- closed external display assembly is flush with the top-case silhouette;
- front finger recess follows the front orthographic calibration;
- feet and bottom screw centers fall inside repair-image calibrated ranges;
- PROVISIONAL / UNVERIFIED measurements cannot produce RELEASE_CANDIDATE geometry.

## Official view / assembly coverage

| Surface / assembly | Official Apple evidence used | What it can constrain |
|---|---|---|
| closed top | Tech Specs 14-inch dimensions image | full plan silhouette, logo scale/position, corner silhouette |
| closed front | Tech Specs front dimensions image | total height, front lip/recess, seam silhouette |
| left side | Tech Specs ports image | MagSafe / 2× USB-C / headphone ordering and local spacing |
| right side | Tech Specs ports image | SDXC / USB-C / HDMI ordering and local spacing |
| open deck | Tech Specs keyboard 2× image | chassis plane, keyboard, speakers, Touch ID, trackpad |
| display face | Product Bezel + exact 3024×1964 @ 254 ppi | active matrix, notch/camera relations; outer bezel still provisional |
| bottom | Bottom Case repair imagery | feet, eight screw centers, bottom-case seam |
| hinge corners | Display Hinge Covers + Display repair imagery | cover size/placement, hinge-to-top-case relation, closed flush requirement |
| rear internal edge | Vent/Antenna repair imagery | module span and rear assembly relationship; exterior vents remain unverified |
| trackpad mechanics | Trackpad repair imagery | cutout/seam/screw/shim relations |
| speakers | Speakers repair imagery + deck orthographic | speaker assembly context and grille lattice |
| internal top case | Top Case / Display repair imagery | mechanical relationship of top case, hinge, display and rear structure |

This is the maximum defensible public-source set found. Apple exposes enough to constrain all external planes and several mechanical relationships, but not a full manufacturing CAD with every hidden radius, wall thickness and hinge section.

## Next gate

`G2 targets → RED tests → master rebuild from datums → derived runtime → top/front/left/right/bottom/deck/display overlays → structural/runtime/browser verification → phone Storybook visual gate`.
