# MacBook construction ledger — 2026-10-01

The owner rejected the slab-like MacBook candidate as primitive and requested construction diagrams, an iPhone-style deliberate refinement loop, and their own website on the display. Passing structural tests is not visual acceptance.

## Grounding and diagrams

- Diagram: `construction-map.svg`, with top layout, shell cross section, display layer order, screenshot scale, and operations.
- Official reference: https://www.apple.com/macbook-pro/specs/ — 312.6 × 221.2 × 15.5 mm envelope and 3024 × 1964 native pixels. The exact local shell radii, chassis split, key profiles, fastener locations, optics and perforation pitch remain LOW estimates; no MacBook Pro manufacturing drawing was obtained.
- Screen capture: `reference/looksawful_home_3024x1964.png`; source URL, timestamp, viewport and SHA-256 recorded in adjacent JSON. Explicit online capture uses 1512 × 982 CSS px at DPR 2. Ordinary builds are offline and use the committed PNG. Cookie consent is declined through the actual page control. No fabricated OS/browser chrome.
- Baseline: commit `55505e9`, fixed acceptance views in `previews/acceptance_v1`, unchanged Blender 5.2.1 LTS, Eevee, exposure -1.35 and lighting.

## Deliberate operations

| Assembly | Proven problem | Durable operation | Evidence gate |
| --- | --- | --- | --- |
| Base/lid | Constant flat extrusion | Nine outline rings form edge/shoulder profiles while preserving verified bounds | Runtime dimensions, manifold, signed volume; side/closed render |
| Keyboard | Floating flat proxy well and block keycaps | Boolean deck recess, seated support geometry, six-ring rounded/dished caps | Runtime profile count; deck/keycap macro |
| Keyboard labels | Generic F-number labels and tiny letters | Twelve vector icons, larger letter legends, matte black well | Runtime icon roster; deck macro |
| Trackpad | Raised plate almost touches keyboard | Physical pocket, flush seating, revised 132 × 80 mm plate, >=4 mm well separation | Runtime pocket ray/gap; deck macro |
| Speakers | Sparse oversized dot array | 1584 small physical recesses with shared dark backing | Runtime deck ray and count; speaker macro |
| Display | Unrelated macOS picture | Native-ratio own-site capture feeding emission | Image/provenance/hash test; packed Blender image; GLB/browser on/off |
| Camera | One cylinder | Separate camera base, pupil, coating, optical cover and status/ambient sensors | Runtime layer order; notch macro |
| Display perimeter | No seating detail | Separate gasket behind bezel/glass | Runtime node plus perimeter render |
| Opening/underside | Plain slab and missing assembly cues | Physical front finger recess, eight fasteners/socket meshes | Runtime roster; front/underside render |
| Logo | 89 mm vertically stretched quad | Image-aspect preserving quad centered on lid | Runtime height bound; lid-back render |
| Mechanics | Geometry changes could invalidate prior pass | Repeat exact sampled clearance contract | 103 integer angles, unchanged thresholds |

## Acceptance ledger

Do not mark the asset as finished from the table above. Inspect all changed assemblies in identical views. Final silhouette comparison, precise ports/vent layout, hinge concealment, optical response and additional screen variants remain subject to visual refinement. LOW estimates are disclosed rather than promoted to measured CAD. Production publication is separate from this construction pass.

## Runtime integrity and performance

The old clearance loop leaked meshes after deleting temporary objects. A known-volume fixture reproduced growing datablock counts `[7, 11, 15]`; after explicitly removing each owned temporary mesh the same test stays stable. Rigid local geometry/modifiers are baked and triangulated once, while the current world transform is applied at every sample. Closed meshes use Blender's MANIFOLD Boolean solver; open meshes retain EXACT fallback. Known 0.5 mm³ overlap, tangent/disjoint cubes and annular clearance agree with EXACT. The 103-angle acceptance range and 0.01 mm³ threshold are unchanged.

Dense grille construction uses MANIFOLD and is performed after port cutting, avoiding repeated expensive operations over perforated topology. All 1584 aperture centers are checked by runtime rays, rather than trusting the array metadata.

The keycap macro exposed striped glyphs: 10-micron legend seating was below the default orthographic depth increment with a 1000 m far plane. The acceptance camera now uses 0.01–2 m clipping, yielding <0.12-micron nominal depth increments. Camera location, lighting, exposure, engine and geometry are retained; all 16 views are refreshed. The added full-frame hero addresses the former cropped composition separately from the unchanged legacy views.

## Fresh delivery checks

Blender 5.2.1 LTS: both main shells have zero non-manifold edges and match the locked outer dimensions within 0.01 mm. All 103 hinge samples, seven port depths, all 1584 aperture rays, camera layers, own-site packed image, key profiles/icons and trackpad pocket/gap pass. The solver fixture agrees with EXACT and retains stable temporary mesh counts.

Fresh checks are recorded below after the complete assembly pass. The increased detail has a larger payload than the earlier proxy; no final LOD/frame-rate claim is made. No Remote Desktop Commander used. No production deployment.

## Complete assembly corrections

The underside diagnostic initially had insufficient light and could not support visual acceptance. It now adds a documented bottom softbox only for the underside view; other comparison lights are unchanged. Actual inspection then found that the panel lay behind a solid chassis cap. The generator cuts its seat and retains a 0.3 mm perimeter lip at the bottom profile, so the panel can be seen and removed conceptually as a separate component. Twenty-four vents are now real low-side cuts with recessed backing. Their centers are checked by rays. This removes the old exterior plates, which expanded web width from 312.6 to 313.07 mm; a dedicated fast regression reproduced that failure.

The complete closed assembly, including feet and the logo, measured 16.205 mm high despite the earlier component-only 15.5 mm check. The hinge gap now includes the modeled 0.655 mm foot allowance, and the logo sits 4 microns above the lid instead of 0.05 mm. Full assembly bounds now pass the unchanged 0.01 mm tolerance. The base/lid split and foot geometry remain construction estimates constrained by the official outer dimensions.

Final measured closed assembly: 312.599987 × 221.200004 × 15.503996 mm. Fresh verification: 173 fast tests, 12 preview tests, Storybook build, all 11 browser assets, on/off captures, 103 hinge positions, 1584 speaker rays and 24 vent rays. All 16 tracked views were rerendered after the final geometry changes. Compatibility GLB: 8,902,272 bytes; meshopt: 2,225,684 bytes. These are acceptance candidates with disclosed local estimates, not a claim of final photographic fidelity.

## Hinge concealment continuation

Baseline `cfd6817`: the fixed hero exposes two bright cylindrical hinge segments. [Apple's product-viewer front reference](https://www.apple.com/v/macbook-pro/ax/images/overview/product-viewer/pv_hero_endframe__gc89p7dw1syi_large.jpg) instead reads as a dark continuous lower-display assembly. This is a visual inference from the reference, not a manufacturing measurement.

Root cause: 58 mm metal pivots were enclosed by only 51 mm reflective sleeves, leaving both ends exposed. A runtime regression probes close to both pivot ends in the hinge coordinate frame; the old candidate fails `Exposed hinge barrel at L end -1`. The same gate independently checks the outer sleeve finish. It does not treat collision clearance as visual acceptance.

Repair: retain both mechanical pivots and their controller, replace the exterior sleeves with 60 mm matte shrouds, add a shallow front flat and a separate black lower-display rail. Estimated section: pivot radius 3.3 mm, sleeve bore 3.42 mm, outer radius 3.65 mm, visible face 3.46 mm from the axis; all stay within the existing 3.9 mm chassis relief. Full-angle mechanical clearance, complete-envelope tolerance and delivery fingerprints are unchanged. No object is hidden just to pass the presentation check.

Fresh verification: Blender 5.2.1 LTS build and all 103 hinge positions pass; end probes and authored matte finish pass, as do all prior construction/deck/port checks. Complete closed bounds remain 312.599987 × 221.200004 × 15.503996 mm. All 16 fixed views were rerendered; hero and 30-degree rear macro inspection show the former bright rods concealed by dark exterior sleeves under unchanged lights/cameras. Browser screen-on/off capture and all 11 assets pass; 173 fast and 12 preview tests pass. Compatibility GLB is 8,885,704 bytes; meshopt is 2,224,516 bytes. Decision: `retain_repair` for the exposed-rod defect. Exact hinge construction, calibrated local dimensions and overall photographic fidelity remain unaccepted LOW estimates. No deployment and no Remote Desktop Commander.
