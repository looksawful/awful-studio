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

172 fast tests, 12 preview tests, Storybook build, and browser smoke for all 11 canonical assets pass. Browser captures verify MacBook on/off states using the actual site image. Compatibility GLB is 8,551,872 bytes; meshopt GLB is 2,159,660 bytes. The increased detail has a larger payload than the earlier proxy; no final LOD/frame-rate claim is made. No Remote Desktop Commander used. No production deployment.
