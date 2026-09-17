# General Asset Contract

- Blender target: 5.2.1 LTS; metric scale, 1 BU = 1 m.
- Every asset has stable ID, deterministic origin, explicit forward/up axes and semantic mounts.
- Manufacturer/historical identity is never inferred from visual similarity. `HISTORICAL_CONFIRMED`, `REFERENCE_STANDARD`, `DESIGN_STANDARD` and `PROJECT_VERIFIED` are distinct evidence classes.
- Primary dimensions are frozen before detail modeling; new evidence updates registry and dossier together.
- Source assets remain editable; runtime exports are derived artifacts.
- Native Blender properties remain canonical for light power/color/temperature and other Blender-owned controls.
- No absolute texture paths, eager downloads or scene mutation on import/enable.
- Rebuild may only replace AWFUL-owned data and must preserve user-owned scene content.
