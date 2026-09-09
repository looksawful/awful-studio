# AWFUL STUDIO current handoff

Updated: 2026-09-09

## Release state

- Current historical baseline: Alpha 0.0.15.
- Baseline source: `awful_studio_v4_2_gpu_perf.py`.
- Internal source version: `4.2-gpu-perf`.
- Baseline SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Next target: Alpha 0.0.16 — Extension Foundation.

## Runtime evidence

Blender 5.2.1 LTS Linux x64 has been executed successfully against the Alpha 0.0.15 source in a headless environment. The baseline completes studio construction and reports `[AWFUL v4] validation OK`.

Known runtime observations:

- Cycles falls back to CPU when no supported GPU backend is available.
- Blender 5.2 emits deprecation warnings for `Material.use_nodes` and `World.use_nodes`; these are compatibility debt for Blender 6.0, not current 5.2 failures.
- Baseline `Build Studio` currently attempts external ambientCG and Poly Haven downloads. Network failure is tolerated, but the automatic attempts violate the intended offline/opt-in development path and must be removed during Extension foundation work.

## Active engineering focus

GitHub issue #12: agent-ready Blender 5.2.1 development runtime and handoff.

Immediate next steps:

1. land `AGENTS.md`, this state file, pinned runtime metadata and single `tools/awful.py` entrypoint;
2. establish GitHub Actions Blender 5.2.1 runtime smoke evidence;
3. import the exact Alpha 0.0.15 source into Git history;
4. migrate it minimally into a Blender Extension before broad modularization.

## Integration status

- Blender Agent Studio 0.6.2 / commit `1f9e050b17ecbb9174c93a001bece7fdbe73f436`: `pilot`.
- pytest-blender: `candidate`.
- Flue: `candidate`.
- blender-addon-tester: `reference`.

Do not infer `installed` or `supported` from these statuses.

## Testing policy

- Real Blender runtime evidence is mandatory for Blender-dependent claims.
- Render regression tests are not required at this stage.
- Base studio build should become fully offline.
