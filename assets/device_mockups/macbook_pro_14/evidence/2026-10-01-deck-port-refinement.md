# MacBook deck and port refinement — 2026-10-01

## Changes and evidence

- Replaced reversed proxy rows with an ANSI deck: 78 physical keys including Touch ID, 76 mesh legends, a blank Space key, full-height function row, and four arrows in an inverted T. Apple specifies 78 ANSI keys and 12 full-height function keys: https://support.apple.com/en-my/126318. Pitch, key sizes, and printed legends are estimated LOW construction values, not measured CAD data.
- Seven real chassis openings replace exterior black plates. Runtime rays measured 2.6 mm recess depth at each opening. Thunderbolt profiles are rounded, the headphone opening circular, HDMI tapered; connector tongues and five MagSafe contacts are separate geometry. Detailed internal contact counts and connector dimensions remain estimated.
- Speaker fields moved outside the keyboard well. A combined cutter makes 150 actual deck apertures; dark floors are recessed below the deck. A regression ray against the previous delivery hit the flat deck and failed; current geometry passes. This sparse LOW grille is not an exact production perforation pattern.
- Closed shells with negative signed volume now have outward normals. The prior lid failed the signed-volume assertion; the regenerated lid/base/glass pass.
- Space Black aluminum, trackpad, keycap, and bezel finishes now retain a dark appearance under the unchanged acceptance lights. Colors are artistic LOW values, not measured reflectance.
- Expanded hinge validation from five presets to 103 samples, 0–102 degrees in 1-degree steps, adding lid/base intersection. At 81 degrees the former Boolean checker incorrectly reported the entire annular cover as overlapping. Measured cover radius was >=3.42 mm versus barrel radius <=3.30 mm; triangulating the evaluated annular caps before Boolean intersection removed the false result. All 103 samples now pass. This is dense sampled evidence, not a mathematical proof between samples.
- Perspective near/far planes now preserve depth separation between 40-micron display layers. A 24-bit depth regression failed with the old range and passes with the bounded range; the same fix is present in both model branches.

## Validation and delivery

Blender 5.2.1 LTS: dimensions within 0.01 mm, base/lid non-manifold edges zero, deck/port/normal/material assertions pass before packaging. Rebuilt the canonical source/package/delivery blends, compatibility and meshopt GLBs, catalog, and nine tracked acceptance views (including deck and both port sides).

Fresh checks: 171 fast tests, 12 preview tests, Storybook build, and browser loading/animation/screen-state smoke for all 11 assets. Browser evidence confirms 77 key meshes plus Touch ID and all four connector tongues. Remote Desktop Commander was not used.

Remaining: final reference-led silhouette comparison, calibrated native screen UI and site/resume variants, detailed material/bake/LOD work after LOW approval, and final visual acceptance. Controls redesign remains deferred; this branch is not a production deployment.
