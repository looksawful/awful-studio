# MacBook Pro 14-inch M5 - G2 model-to-Apple overlay calibration

Date: 2026-10-03
Scope: evidence calibration for the existing G2 model-to-Apple overlay pipeline. This note does not promote LOW or UNVERIFIED geometry to manufacturing truth.

## Primary sources

1. Apple MacBook Pro technical specifications
   https://www.apple.com/macbook-pro/specs/
   Exact 14-inch M5 envelope used here:
   - width: 312.6 mm
   - depth: 221.2 mm
   - closed height: 15.5 mm
   - display: 3024 x 1964 at 254 ppi

2. Apple Design Resources - MacBook Pro M5 Product Bezel
   https://developer.apple.com/design/resources/
   Used as an official planar display/notch/camera visual reference. It is not a manufacturing drawing.

3. Apple MacBook Pro (14-inch, M5) Repair Manual
   https://support.apple.com/en-us/123173
   Used for part identity/topology and repair-image relationships. Public repair imagery is not treated as a general millimetre source.

4. Repo construction ledger
   `assets/device_mockups/macbook_pro_14/evidence/2026-10-01-construction-ledger.md`
   Records the side-port LOW calibration from Apple's model-specific side images. The picked source centers are native pixels in the current ~409 px side images; a visible ~24 px USB-C opening is used as an approximate local 8.4 mm ruler.

## Review finding

The first G2 overlay implementation had two false-confidence behaviors in `tools/build_macbook_g2_surface_overlays.py`:

1. `side_x_mapper()` divided the recorded Apple `center_pixel` values by two even though the cached Apple side images are already the native ~409 px references used by `port_layout.py`.
2. Front and side Z projection normalized the generated model's own `zmin..zmax` to the full image height. A wrong model height would therefore still fit the reference by construction.

The old `<=0.5 px` side residual was not independent geometry evidence because both model placement and overlay targets came from the same side-image calibration.

## Corrected calibration

### Side X

Use the native Apple source pixel centers directly, without `/2`.

The residual is now explicitly named a **reprojection residual**. It checks projection/export consistency for geometry that already consumes the same LOW calibration. It must not be cited as an independent proof of port geometry.

### Front / side Z

Use the Apple exact closed height, 15.5 mm, as the fixed vertical scale.

Reference body-silhouette rows measured from the cached Apple imagery:
- front: y = 0..20 px
- left: y = 7..53 px
- right: y = 7..53 px

Method:
- exclude dimension brackets, isolated reflections and shadow tails;
- use the broad occupied chassis rows, not the complete JPEG bbox;
- align only the model Z translation by the evaluated closed-hull center;
- derive pixels/mm from the fixed Apple 15.5 mm height.

This deliberately does **not** normalize the model's height. A model that becomes too tall or too short projects outside the Apple silhouette and makes the gate red.

Current evaluated Blender closed Z envelope:
- z_min = -0.655 mm
- z_max = 14.848996 mm
- height = 15.503996 mm

## Bottom-view numerical cross-check

Bottom reference calibration:
- X: 312.6 / 798 = 0.3917293233 mm/px
- Y: 221.2 / 562 = 0.3935943060 mm/px
- scale anisotropy: ~0.475%

Current model-to-Apple foot residuals:
- 0.877 mm
- 1.567 mm
- 1.239 mm
- 0.555 mm

The four values were independently reproduced with Wolfram Language from the stored point correspondences.

## Current evidence semantics

- top/front/side/bottom/deck contours: evaluated Blender geometry projected into registered Apple references;
- display active matrix/notch/camera: Apple exact/Apple calibrated facts;
- hinge cover X span: calibrated/relational evidence;
- hinge cover depth/thickness: still `UNVERIFIED_VISUAL`;
- display outer surround: still `RELATIONAL_VISUAL`;
- side-port reprojection: consistency evidence, not an independent geometry measurement.

## Regression coverage

`tests/fast/test_macbook_g2_model_overlay_contract.py` now requires:
- native Apple side pixels are used directly;
- front/side Z use a fixed-height mapper;
- a deliberately too-tall model projects outside the reference bounds.

`tests/fast/test_macbook_g2_overlay_pairing.py` separately keeps the bottom-foot matching order-independent and red-capable for displaced geometry.
