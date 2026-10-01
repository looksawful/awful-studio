# iPad optics and port refinement — 2026-10-01

The rear pupil previously protruded in front of an opaque cover. It now sits behind transmitting optical glass, inside an open annular ring and a physical housing well. The USB-C opening now contains a recessed floor and tongue instead of a shallow exterior plate. The new optics/port validator failed against the previous delivery and passes on both regenerated sizes.

Closed X/Z prisms with inward normals are corrected before export; the old screen glass failed a signed-volume assertion. The OLED image now feeds emission only, with a dark nonreflective content base. Separate glass owns reflections; border materials have reduced specular response.

Browser comparison exposed an additional issue after normals were corrected: the black bezel could occlude the screen despite sitting behind it. Isolating the screen showed the image was present. Increasing the camera near plane restored the complete assembly without moving geometry. The durable viewer now bounds near/far to product distance, and a 24-bit depth regression verifies separation of the 40-micron layer gap. This fix is shared with the MacBook branch.

Blender 5.2.1 LTS checks: both independently sized envelopes within 0.01 mm; chassis non-manifold edges zero; controls and optics/port/normal assertions pass before packaging. Rebuilt both source/package/delivery blends and GLB variants, catalog, and all 14 tracked views. Fresh verification: 170 fast tests, 13 preview tests, Storybook build, and all 11 asset browser smoke. Browser captures verify on/off states on both sizes. Remote Desktop Commander was not used.

Remaining: reference-led camera dimensions/silhouette review, calibrated native screen UI and site/resume variants, final visual LOW acceptance, then detailed maps/LODs. Rear assembly values remain estimated LOW geometry. No controls redesign or production deployment in this pass.
