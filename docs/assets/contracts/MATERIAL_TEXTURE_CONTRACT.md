# Material and Texture Contract

- Separate physically distinct surfaces: metal, polymer, rubber, glass, textile, plaster, wood, paper/label and emissive surfaces.
- Master materials are procedural/editable where useful; runtime materials are simplified glTF-friendly derivatives.
- Hero assets default to 4K authoring and 2K runtime; standard assets default to 2K authoring and 1K runtime unless close-up evidence requires more.
- UV0 is PBR; UV1 or decals carry labels/legends when useful.
- Bake Normal/AO/Curvature/Thickness/Position/IDs only when HIGH detail materially improves MID/LOW.
- Wear is restrained, reference-driven and never a substitute for correct geometry or roughness response.
