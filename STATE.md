# AWFUL STUDIO Current State

Last reviewed: 2026-09-13

This is the short engineering handoff. Product requirements live in accepted specs; implementation status/evidence lives in released source, GitHub Issues, PRs and CI.

## Release state

- Current release: 1.0.0.
- Historical baseline: Alpha 0.0.15, immutable source at `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`.
- Historical SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Blender target: 5.2 LTS; exact qualification runtime is Blender 5.2.1 build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins are recorded in `runtime/blender.lock`.
- 1.0.0 is based on the corrective 0.0.17 feature set from PR #46, with stable-version metadata and release hardening.
- The invalid pre-release PaintedPlaster PNG bundle is excluded from 1.0.0; procedural/offline material fallback remains the supported path until a verified source bundle is restored in a patch.
- Remaining visual libraries, device-model production passes and research integrations are post-1.0 work, not stable-core blockers.

## Stable core in 1.0.0

Packaged Blender 5.2 structural evidence covers:

- explicit install/enable/disable/re-enable/restart lifecycle;
- ownership-safe Build/Rebuild/Remove and unmanaged-data preservation;
- explicit historical migration;
- product/support grounding from world-space bounds and Auto Fit;
- Bottle / Jar / Box / Can / Phone / Tablet procedural starters;
- Product and Camera Once / Loop / Ping-Pong with synchronized Preview Range;
- metric cyclorama and independent room/architecture visibility controls;
- photographic lighting, Flash, Natural Light, Physical Sky and Hybrid Studio + World behavior;
- independent environment illumination and camera-visible background brightness;
- reviewed HDRI workflow, explicit network permissions, status/error handling and provenance-safe cache behavior;
- optional Post Pipeline with live capability detection, Light Groups, passes, compositor, idempotent rebuild and save/reopen safety;
- Fast/Quality viewport profiles and non-render device diagnostics;
- native Blender Extension package/repository generation and install verification.

## Canonical runtime architecture

There is one canonical path. Do not create a parallel runtime/bootstrap/test stack.

- Fast gate: `python -m unittest discover -s tests/fast -v`.
- Entry point: `python tools/awful.py status|doctor|fast|bootstrap|test-runtime`.
- Exact Blender bootstrap: `tools/setup_blender.py`.
- Exact Extension ZIP verifier: `tools/verify_extension.py`.
- Blender lifecycle contract: `tests/runtime/extension_contract.py`.
- Batched structural contracts: `tests/runtime/p0_suite.py` plus focused packaged-runtime phases.
- CI: `.github/workflows/extension-ci.yml` on GitHub-hosted Ubuntu and Windows runners.

The harness builds one canonical Extension ZIP, validates it with Blender's official CLI and reuses that exact artifact byte-for-byte on Windows rather than rebuilding per OS.

## Runtime and performance policy

- Ordinary local development must not launch full Blender runtime or probe GPU hardware automatically.
- `tools/verify_extension.py` refuses local full runtime unless `--allow-local-blender` is explicitly supplied; CI is allowed automatically.
- Structural runtime contains no render invocation.
- Build/Rebuild preserves Blender's native Cycles device/backend selection and never silently rewrites CUDA/OPTIX/HIP/ONEAPI/METAL preferences.
- AWFUL exposes explicit Fast Preview and Quality Preview modes that change viewport-only settings, not final render settings.
- AWFUL diagnostics make CPU-backed Cycles sessions visible rather than silently presenting them as an AWFUL slowdown.

## Safety invariants

- Import/register/enable/restart do not build a scene.
- Build/Rebuild/Remove are explicit and ownership-scoped.
- Names/roles alone never authorize destructive cleanup.
- Unmanaged nested/shared/multi-scene data has runtime safety coverage.
- Base Build/preset switching is offline; optional remote assets require explicit user/network permission.
- Historical migration is explicit and the baseline stays byte-identical.
- Exact generated ZIP is validated/installed in isolated Blender profiles on Windows and Ubuntu.
- Product mockup replacement may remove only AWFUL-owned mockup data; unmanaged user products survive.
- Post Pipeline creates managed data only inside the existing scene owner scope, including after save/reopen.
- Render/image regression remains a separate evidence layer and is not claimed by 1.0.0.
- Third-party binary media must be byte-safe and explicitly reviewed before bundling.

## Post-1.0 backlog

Existing issues remain the source of truth rather than being hidden behind an artificial "done" label:

- #4 deterministic rendered visual regression;
- #48 Scene Lab v3 visual/scene-quality work;
- #49–#54 production device mockups, materials, bakes and Extension delivery contract;
- #55 physical studio-equipment research plus subsequent modeling work;
- #1 Flue evaluation;
- #2 Blender Agent Studio evaluation;
- expanded motion/HDRI/fixture/volumetric libraries.

Patch releases should fix contained correctness, packaging and compatibility problems. Minor 1.x releases should add qualified workflows/assets without breaking the stable Extension contract. 2.0.0 is reserved for an intentional incompatible contract change.

Use `AGENTS.md`, this file, the owning issue/PR and only the relevant `.skills/` before editing. Evidence before claims.
