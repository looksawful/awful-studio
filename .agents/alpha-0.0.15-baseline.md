# Alpha 0.0.15 pilot baseline

Canonical historical source according to Notion Version History:

- Alpha: `0.0.15`
- source: `awful_studio_v4_2_gpu_perf.py`
- internal version: `4.2-gpu-perf`
- Library source SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`
- materialized size: 125340 bytes
- Python parse/compile check in current agent environment: PASS
- Blender runtime check in current agent environment: NOT RUN; Blender executable is unavailable here

## Why this baseline

Notion Version History explicitly maps Alpha 0.0.15 to `awful_studio_v4_2_gpu_perf.py` and describes it as the current baseline: GPU-first Cycles, lightweight bounce material and lower interactive path-tracing cost.

`awful_studio_v4_3.py` exists in the ChatGPT Library as a later candidate, but the project Version History explicitly says the v4.3 specification belongs to Alpha 0.0.16+ requirements. It must therefore not silently replace the 0.0.15 baseline for controlled comparisons.

## Static observations relevant to the BAS pilot

The 0.0.15 baseline contains:

- Blender-native `bpy` implementation;
- managed-data keys and project semantic roles;
- large physical studio specification;
- HDRI lazy-loading assets;
- GPU/performance settings;
- optional post-pipeline state;
- data-driven studio/light configuration;
- camera/product motion systems;
- runtime/UI registration code.

These make it suitable for the first BAS comparison, provided the same source revision is used for all comparison conditions.

## Evidence rule

No condition may be called better or worse from static source inspection alone. Blender 5.2 runtime scene evidence remains mandatory before closing GitHub issue #2.
