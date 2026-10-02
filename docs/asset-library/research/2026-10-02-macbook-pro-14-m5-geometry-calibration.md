# MacBook Pro 14-inch M5 — geometry calibration research

Date: 2026-10-02
Scope: research/planning only. No product geometry changes are authorized by this document.

## Research question

How should the MacBook Pro 14-inch M5 asset be rebuilt so that component placement and proportions come from a traceable metric system rather than hand-tuned coordinates, while preserving the existing master -> runtime pipeline?

## Primary-source hierarchy

### Tier A — Apple exact numeric facts

Apple's 14-inch M5 tech specs are the strongest public metric source for the global envelope and high-level product facts:

- closed height: 15.5 mm
- width: 312.6 mm
- depth: 221.2 mm
- display: 14.2-inch diagonal, 3024 x 1964, 254 ppi
- keyboard: 78 ANSI / 79 ISO keys, including 12 full-height function keys
- Touch ID
- Force Touch trackpad
- 12 MP Center Stage camera
- six-speaker sound system

Source:
https://support.apple.com/en-gb/125405

These values may be encoded as exact project datums with tight numerical tolerances.

### Tier B — Apple official model-specific imagery

Apple Design Resources publishes a MacBook Pro M5 Product Bezel package in Photoshop/PNG form.

Source:
https://developer.apple.com/design/resources/

The downloaded 14-inch Space Black PNG is 3860 x 2540 px. Treat it as a high-trust planar visual reference for the display/lid front view, not as a factory dimensional drawing.

The Apple MacBook Pro specs page also exposes model-specific image assets for:
- 14-inch keyboard
- two 14-inch dimension views
- 14-inch display
- multiple 14-inch port views

Page:
https://www.apple.com/macbook-pro/specs/

Method:
1. calibrate a planar image against a Tier-A dimension visible in the same plane;
2. measure repeated structures statistically rather than from one pixel span;
3. verify bilateral symmetry and residual error;
4. reject views with perspective or projection distortion above tolerance.

Tier-B measurements are calibrated, not manufacturer-declared dimensions.

### Tier C — Apple repair / service geometry and topology

Apple's M5 repair manual supplies authoritative part decomposition and assembly relationships.

Source:
https://support.apple.com/en-us/123173

Useful procedures include:
- Keys
- Speakers
- Trackpad and Trackpad Flex Cable
- Display Hinge Covers
- Display
- Touch ID Board
- Top Case with Battery and Keyboard

The repair documentation confirms that keyboard keys are not one undifferentiated family. Apple classifies Mac laptop key service geometry as:
- 1x1 keys
- 1x0.5 keys
- link bar keys

Sources:
https://support.apple.com/en-us/101269
https://support.apple.com/en-us/101270
https://support.apple.com/en-us/101271

For MacBook Pro 14-inch/16-inch 2021 and later, Apple publishes keyboard maps for those classes.

Trackpad reassembly uses four gap offsets around the trackpad and shims to establish flush height with the top case. This is strong evidence that gap/flush relationships are intentional assembly constraints, but the public repair article does not state the actual metric gap value.

Source:
https://support.apple.com/en-us/123161

Therefore repair documentation is authoritative for topology, part identity and relational constraints, but is not automatically a millimetre source.

### Tier D — visual cross-check only

Use the May Jestei model, user photographs and non-orthographic product renders only to:
- identify missing construction cues;
- compare shading;
- compare mechanical read;
- detect likely measurement mistakes.

Do not promote Tier-D measurements into the geometry contract.

## Key conclusion

The current generator contains valid engineering work, but its internal deck/display coordinates cannot be treated as authoritative merely because they are parametric.

Authoritative now means one of:

1. APPLE_EXACT — explicitly stated by Apple in numbers.
2. APPLE_CALIBRATED — measured from an official Apple planar reference after calibration.
3. APPLE_RELATIONAL — topology/relationship confirmed by Apple service documentation.
4. DERIVED — mathematically derived from stronger measurements.
5. PROVISIONAL — current model value not yet revalidated.

Only classes 1-4 may become frozen geometry-contract values.

## Coordinate system

Use the enclosure as the global datum.

- origin: chassis plan center
- X: left/right, positive right
- Y: front/back, positive toward display hinge
- Z: vertical, positive upward
- deck plane: explicit Z datum
- chassis front/back/left/right planes: exact Tier-A envelope datums

Do not use a key, trackpad or camera as the world origin. They are children of the chassis datum system.

## Measurement record

Every frozen geometric fact should carry:

- id
- value_mm or vector_mm
- source_class
- source_url / source_asset
- calibration_method
- tolerance_mm
- axis / coordinate frame
- confidence
- notes

Example:

    keyboard.pitch_x:
      value_mm: ...
      source_class: APPLE_CALIBRATED
      method: robust fit over repeated 1x1 key centers
      tolerance_mm: ...
      source_asset: Apple 14-inch keyboard image

## Calibration methodology

### Keyboard

Do not manually place 78 keys.

Fit a shared lattice from many repeated keys:

- Ux = standard 1x1 key width
- Uy = standard full-height key height
- Gx = horizontal gap
- Gy = vertical gap
- Px = Ux + Gx
- Py = Uy + Gy

Estimate Px/Py and the keyboard origin by least-squares fitting to repeated key centers visible in the official Apple keyboard image.

Use Apple's service classes as semantic families:
- 1x1
- 1x0.5
- link-bar

Do not assume all link-bar widths from desktop-keyboard conventions. Fit or derive them from row closure and Apple imagery.

Tests should verify:
- shared pitch invariants;
- repeated-key equality;
- row closure;
- symmetry where applicable;
- function-row alignment;
- arrow-cluster geometry;
- Touch ID placement relative to the function row.

### Speakers

Do not preserve the current 88 x 9 / pitch / field width merely because it exists.

From an official top/deck view:
- detect/fix left and right grille field bounds;
- fit grille centerline;
- fit row/column lattice if the raster resolves individual perforations;
- derive hole radius/pitch from repeated points;
- require bilateral symmetry unless Apple imagery disproves it.

One speaker-pattern contract must drive both:
- master physical geometry;
- runtime normal/alpha proxy.

### Trackpad

Calibrate:
- width
- height
- corner radius
- centerline
- front offset
- keyboard-to-trackpad gap
- trackpad-to-top-case gap

The repair manual confirms controlled perimeter gap and flush-height adjustment, so gap and Z seating must be explicit tested constraints.

### Touch ID / power button

Treat Touch ID as a distinct key/control family, not a glowing white function key.

Calibrate:
- bounds
- center
- row alignment
- corner radius
- surface height

Material/appearance should then be validated against official Apple imagery.

### Finger-opening recess

Treat the front-center opening recess as part of the chassis edge profile, not a decorative overlay.

Calibrate:
- center X = chassis center unless evidence says otherwise
- width
- depth
- plan radius/profile
- relation to trackpad centerline

### Display / lid / camera

Use the official MacBook Pro M5 Product Bezel and Apple display imagery to fit:
- outer lid/glass bounds
- outer corner radius
- visible display bounds
- bezel widths
- notch width/height/radius
- camera center
- lower display rail
- symmetry

Known chassis/display values provide the calibration scale and cross-check.

### Edge profile / chamfers

Use exact envelope plus official side/port imagery to constrain:
- top edge rolloff
- side transition
- bottom edge
- corner plan radius
- front lip profile

Because lighting can move the apparent highlight edge, derive hard silhouette constraints from imagery and keep shading-profile values at lower confidence until corroborated.

## Test philosophy

The primary tests are mathematical, not screenshot-diff tests.

Required test categories:

1. Exact datum tests
   - chassis envelope
   - global origin/axes

2. Lattice/invariant tests
   - keyboard pitch
   - row/column relationships
   - speaker lattice
   - symmetry

3. Derived geometry tests
   - trackpad center/gaps
   - Touch ID alignment
   - finger recess center/profile
   - display/notch/camera relationships

4. Cross-source calibration tests
   - calibrated overlay residual below declared tolerance

5. Existing mechanism/runtime tests
   - hinge sweep
   - ports
   - anchors
   - GLB/runtime contracts

Visual renders remain a human acceptance layer, not the source of geometry truth.

## Impact on current spec

The wording in #127 that the current parametric skeleton is authoritative for all dimensions/ports/anchors is now too broad.

Keep authoritative:
- Apple-verified external envelope;
- hinge behavior already proven by 103-angle clearance tests;
- runtime identity/anchors that do not encode disputed physical placement.

Revalidate before freezing:
- keyboard geometry and placement;
- speaker field dimensions/perforation;
- trackpad dimensions/gaps;
- Touch ID;
- finger recess;
- display/bezel/notch/camera;
- side-port centerlines if Apple calibrated imagery disagrees;
- edge/chamfer profiles.

## Research stop condition

Do not resume aesthetic surface polishing until:
- official reference assets are locally registered;
- calibration transforms are reproducible;
- the geometry-contract schema exists;
- the first calibrated constants pass numerical tests;
- a human overlay review confirms the chosen datum/reference method.
