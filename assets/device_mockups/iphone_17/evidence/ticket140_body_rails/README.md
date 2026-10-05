# Ticket140 body corners/rails evidence

Review fixed point a8ad3a2. Exact identities, contract results and artifact hashes
are recorded in summary.json. Standards and Spec independently PASS for this slice.
No whole-device acceptance or Human PASS is claimed.

comparison-{texture,clay,wireframe}.jpg: rows isolated four corners and top/left/right/bottom rails;
columns baseline/current/frozen. assembly-comparison files show the same four
corners with the assembled device, using the same cameras. Wireframe is the actual
loaded GLB triangle topology; browser audits verify buffers unchanged across modes.

The baseline contract log reproduces crossed annulus coverage RED. Current contract
log records independent coverage GREEN, actual saved triangle quality GREEN and
632-triangle GLB correspondence GREEN. build-failure-proof log/script demonstrates
that real Blender Python errors stop the existing build before export/package.

Full 135 PNG captures and all raw diagnostics remain at
F:\Temp\iphone17-ticket140-continuation. Prior captures and prototypes were preserved.

Portability follow-up: invoke build-failure-proof.py with required --blender.
Repository is derived from script location; fixtures use system temp. Fresh proof
and fast209/209 PASS after the retained evidence was added; independent Standards/Spec PASS.
