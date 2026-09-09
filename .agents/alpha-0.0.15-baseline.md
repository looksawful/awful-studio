# Alpha 0.0.15 pilot baseline

Canonical historical source according to Notion Version History:

- Alpha: `0.0.15`
- source: `awful_studio_v4_2_gpu_perf.py`
- internal version: `4.2-gpu-perf`
- Library source SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`
- materialized size: 125340 bytes
- Python parse/compile check: PASS
- Blender runtime: PASS on Blender 5.2.1 LTS Linux x64
- Blender build hash used for verification: `9e2066aef7ef`

## Runtime evidence

The exact Alpha 0.0.15 source was executed headlessly with Blender 5.2.1 and completed with `[AWFUL v4] validation OK`.

Observed compatibility/runtime details:

- Cycles used CPU fallback because the cloud environment had no supported GPU backend.
- Blender 5.2 reports deprecation warnings for `Material.use_nodes` and `World.use_nodes`; these are Blender 6.0 compatibility debt, not current 5.2 failures.
- Base execution attempted one ambientCG texture download and five Poly Haven HDRI downloads. DNS failure was tolerated and studio construction still completed. Automatic network attempts are now a known Extension-foundation defect because normal base Build must become offline/opt-in.

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

## Evidence rule

No future condition may be called better or worse from static source inspection alone. Blender 5.2 runtime evidence remains mandatory for Blender-dependent changes.
