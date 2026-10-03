# MacBook G2 side-overlay calibration — 2026-10-03

## Question

Why did the G2 left/right actual-model overlays report <=0.5 px port-center residuals while the green closed-chassis silhouette visibly failed to align with the Apple side rasters?

## Primary sources

- Apple MacBook Pro specifications page: https://www.apple.com/macbook-pro/specs/
  - Apple publishes model-specific closed left/right side images for the 14-inch M5 port layouts.
- Existing local Apple-source calibration in `assets/device_mockups/macbook_pro_14/port_layout.py`.
  - The side views crop the front of the device.
  - Port Y positions are therefore calibrated with the visible USB-C opening as a local ruler instead of scaling the full raster width to chassis depth.
  - Stored `center_pixel` and `rear_pixel` values are already coordinates in the cached side-image raster.

## Finding

`tools/build_macbook_g2_surface_overlays.py::side_x_mapper` divided the stored Apple source pixels by two:

```python
px = np.array([p.center_pixel / 2 for p in specs], dtype=float)
```

and the reported target residual repeated the same half-scale target:

```python
actual_centers.append((spec.name, q[0], spec.center_pixel / 2))
```

This made the port-center metric self-consistent while projecting the closed chassis at half the intended horizontal image scale.

The visible symptom matches the math:
- left rear datum: Apple source 3 px -> old overlay 1.5 px
- right rear datum: Apple source 406 px -> old overlay 203 px

Because the side images intentionally crop the chassis front, the correct full-depth continuation may extend outside the raster. That is expected and must not be “fixed” by scaling the whole image to 221.2 mm.

## Independent numerical check

Using the existing local ruler `8.4 / 24 = 0.35 mm/px` and depth `221.2 mm`, the source-pixel fits are:

- left: `x_px = 319 - 2.857142857 * y_mm`
- right: `x_px = 90 + 2.857142857 * y_mm`

At the rear chassis datum `y = +110.6 mm`, they return:
- left: 3 px
- right: 406 px

At the front datum `y = -110.6 mm`, they return:
- left: 635 px
- right: -226 px

The out-of-frame front values are consistent with the documented cropped-front calibration method.

## Required contract

The side-overlay mapper must round-trip every calibrated `Port.y_mm` back to its original Apple `center_pixel`, and `D/2` back to the side's Apple `rear_pixel`.

The regression test lives in:
`tests/fast/test_macbook_g2_overlay_pairing.py::test_side_mapper_roundtrips_apple_reference_pixels`

## Scope

This finding is an overlay/calibration-mapping bug, not evidence of incorrect Blender port geometry. Do not move ports or rescale the chassis to make the old overlay look correct.

After the mapping fix, regenerate the side overlays from the same evaluated Blender projection JSON and visually verify them before treating the model-to-Apple gate as accepted.
