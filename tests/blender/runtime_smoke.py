from __future__ import annotations

import bpy

EXPECTED_SERIES = (5, 2)
actual = tuple(bpy.app.version)

if actual[:2] != EXPECTED_SERIES:
    raise RuntimeError(
        f"AWFUL runtime requires Blender {EXPECTED_SERIES[0]}.{EXPECTED_SERIES[1]}.x; "
        f"got {bpy.app.version_string}"
    )

scene = bpy.context.scene
if scene is None:
    raise RuntimeError("Factory-startup Blender did not provide an active scene")

print(f"AWFUL_RUNTIME_SMOKE_OK blender={bpy.app.version_string} objects={len(scene.objects)}")
