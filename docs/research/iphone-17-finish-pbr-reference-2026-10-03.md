# iPhone 17 finish and PBR reference

Date: 2026-10-03

## Authority

Apple iPhone 17 Technical Specifications:
https://www.apple.com/iphone-17/specs/

Apple iPhone 17 product page:
https://www.apple.com/iphone-17/

Apple officially lists five finishes for the standard iPhone 17:

- Black
- White
- Mist Blue
- Sage
- Lavender

Apple describes the design as aluminum with a color-infused glass back for Black, Mist Blue, Sage and Lavender. Apple does not publish canonical material RGB/hex values.

## Color calibration

Display tints are calibrated from Apple's official 1728×912 product-viewer renders. They are render-reference approximations, not claims about measured spectral/material color.

Official product-viewer sources:

- Black: `colors_black__fzuhc3kqvmq2_large.jpg`
- White: `colors_white__979ypubjzdum_large.jpg`
- Mist Blue: `colors_mist_blue__700uff6zu2qa_large.jpg`
- Sage: `colors_sage__cr1jt90v1yoi_large.jpg`
- Lavender: `colors_lavender__bcaie9a8npj6_large.jpg`

Runtime palette:

| Finish | anodized aluminum | darker edge/rings | camera housing | back glass |
| --- | --- | --- | --- | --- |
| Black | #292a2c | #232426 | #6c6c6c | #6c6c6c |
| White | #b8b8b6 | #a2a3a1 | #f7f7f5 | #f7f7f5 |
| Mist Blue | #687c95 | #566a82 | #bdcde4 | #bdcde4 |
| Sage | #737e5e | #5f6b4d | #c8d2af | #c8d2af |
| Lavender | #998fa8 | #81758f | #efe4f4 | #efe4f4 |

The darker rail values are sampled from the shaded anodized side rail in the same official renders. Back/camera colors are sampled from broad non-specular back-surface regions.

## Variant architecture

The five finishes are one canonical v30 geometry/runtime asset.

No per-color GLB copies are created.

The preview applies finish variants by changing only base material color for:
- `MAT_ANODIZED_ALUMINUM`
- `MAT_ALUMINUM_EDGE`
- `MAT_CAMERA_HOUSING`
- `MAT_BACK_GLASS`

Normal maps, roughness maps, metallic response, geometry and screen state remain identical across variants.

Storybook exposes:
- generic iPhone 17
- Black
- White
- Mist Blue
- Sage
- Lavender

The viewer also exposes a `finish` selector.

## PBR surface policy

Silhouette-critical details remain geometry.

Micro-surface detail is texture-driven:

### Anodized aluminum
- embedded tangent-space normal map on body/buttons and darker edge/rings
- embedded roughness map
- camera housing keeps the same anodized roughness family but does not claim a tangent normal map when the exporter cannot produce stable tangents for that plateau mesh
- subtle amplitude only; no decorative grunge

### Back glass / Camera Control
- back glass: embedded micro-normal + micro-roughness
- Camera Control: embedded micro-normal + dedicated roughness map
- clearcoat/specular model retained

### Bottom fasteners
- physical screw head remains Ø1.50 geometry from the Apple dimensional drawing
- five-lobe pentalobe socket uses an embedded tangent-space normal map
- a dedicated roughness map separates the recessed socket response from the metal head
- a subtle base-color recess map improves readability at product-preview scale
- no heavy groove geometry is added

### Acoustic openings
- hole/recess silhouette remains geometry
- existing grille normal map remains the micro-detail layer

## Export contract

The compat GLB must contain:
- `TEXCOORD_0` on all PBR-mapped visible finish meshes
- embedded normal textures
- embedded metallic/roughness textures
- tangents where the exporter can calculate them

Three.js must preserve all PBR maps when switching finish variants.
