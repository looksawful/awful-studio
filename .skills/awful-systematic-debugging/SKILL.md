---
name: awful-systematic-debugging
description: Debug AWFUL STUDIO by separating pure-Python, Blender API, scene-state, GPU/render and visual-quality failures before patching.
---

# AWFUL STUDIO systematic debugging

Apply the Superpowers systematic-debugging method, then collect Blender-specific evidence before changing code.

1. Reproduce under factory startup when practical.
2. Record Blender version, render engine/device, active scene, selected preset and relevant managed-object metadata.
3. Classify the failure as pure Python, Blender API, scene state, GPU/render, asset/provenance or visual-quality.
4. Reduce to the smallest reproducible scene or function.
5. Change only the proven cause.
6. Rerun the original reproduction and the relevant regression/runtime checks.

Do not "fix" a scene-state bug with global cleanup, hide a GPU failure with a quality downgrade, or weaken product requirements to get a green test. Live-session bridges are diagnostic aids, not canonical evidence.
