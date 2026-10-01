# MacBook delivery validation — 2026-10-01

The web builder previously packaged a cached generated blend without running the current generator or checking hinge clearance. It now regenerates the source, validates hinge clearance, and only then packages and exports the delivery. Blender script failures return a nonzero exit code at every stage.

Validation on Blender 5.2.1 LTS:

- Canonical source, extension package, delivery blend, compatibility GLB, and meshopt GLB rebuilt successfully.
- Delivery hinge clearance passed at 0, 30, 60, 90, and 102 degrees: all six measured intersection volumes are zero at each sampled angle. This is sampled clearance evidence, not proof for every intermediate angle.
- Fresh six-view acceptance renders generated with the existing render harness.
- Fast suite: 170 tests passed, including generation ordering and stopping packaging after a hinge validation failure. Both new tests failed against the previous builder before the fix.
- Preview tests: 11 passed; Storybook build passed; browser smoke loaded all 11 canonical assets, including MacBook lid and screen states.

Remaining work: visual LOW acceptance, screen glare/material refinement, and detailed keyboard/port appearance. Existing rendered screen glare remains visible; this change does not claim visual acceptance or production publication. Keep the site's 3D controls hidden and defer their redesign as requested.
