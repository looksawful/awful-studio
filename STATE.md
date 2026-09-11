# AWFUL STUDIO Current State

Last reviewed: 2026-09-11

This is the short engineering handoff. Product requirements live in Notion; implementation status/evidence lives in GitHub Issues and PRs.

## Release state

- Historical baseline: Alpha 0.0.15, immutable source at `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`.
- Historical SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Current target: Alpha 0.0.16 Extension Foundation on `feature/extension-foundation`.
- Blender target: 5.2 LTS; exact verified runtime is Blender 5.2.1 build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins are recorded in `runtime/blender.lock`.
- Alpha 0.0.16 is not yet public-release-ready only because final provenance/repository/update/release reconciliation is still being completed. Core lifecycle and the accepted P0 visual/product slices have real packaged runtime evidence.

## Canonical runtime architecture

There is one canonical path. Do not build another pytest/bootstrap/runtime stack.

- Fast/pure gate: `python -m unittest discover -s tests/fast -v`.
- Agent entrypoint: `python tools/awful.py status|doctor|fast|bootstrap|test-runtime`.
- Exact Blender bootstrap: `tools/setup_blender.py`.
- Exact Extension ZIP verifier: `tools/verify_extension.py`.
- Blender lifecycle contract: `tests/runtime/extension_contract.py`.
- Batched P0 structural contracts: `tests/runtime/p0_suite.py`.
- CI: `.github/workflows/extension-ci.yml` on GitHub-hosted Windows and Ubuntu runners.

`pytest-blender` is not required. The thinner custom harness is intentionally adopted because it validates Blender's official Extension build output and runs the exact generated ZIP inside isolated Blender profiles.

## Runtime and performance policy

- Ordinary local development must not launch full Blender runtime or probe GPU hardware automatically.
- `tools/verify_extension.py` refuses local full runtime unless `--allow-local-blender` is explicitly supplied; CI is allowed automatically.
- Structural runtime contains no render invocation.
- Build/Rebuild preserves Blender's native Cycles device selection and does not enumerate OPTIX/CUDA/HIP/ONEAPI/METAL.
- P0 structural contracts share one Blender process.
- Superseded CI runs for the same PR/ref are cancelled.
- Existing operation timings are collected from normal CI rather than adding render/GPU benchmark passes.

Verified cloud performance after #5:
- Windows Blender 5.2.1: Build about 0.231 s; Rebuild median about 0.240 s.
- Ubuntu Blender 5.2.1: Build about 0.107 s; Rebuild median about 0.111 s.

## Verified integrated P0 work

Integrated into `feature/extension-foundation` with exact packaged Blender 5.2.1 Windows/Ubuntu evidence:

- photographic lighting / complete Flash family (#6/#22);
- full product-bounds camera framing (#19);
- metric cyclorama and visible studio architecture (#7/#21);
- Natural Light v2 / Pure HDRI / Physical Sky / managed Sun (#9);
- runtime performance and zero-local-GPU development policy (#5);
- independent Product/Camera Once / Loop / Ping-Pong playback (#8).

## Active release work

- #23: third-party asset provenance and Blender Extensions packaging audit.
- #3/#10/#12: reconcile the already-working custom runtime harness, agent handoff, static Extension repository/native install/update path, and release documentation.
- #4 visual regression is explicitly opt-in/non-blocking. Do not run render/GPU visual tests without an explicit user instruction.
- #28 Product Quality starts after the 0.0.16 release gates: procedural Bottle/Jar/Box/Can/Phone/Tablet and starter materials.

## Safety invariants already enforced

- Import/register/enable/restart do not build a scene.
- Build/Rebuild/Remove are explicit and ownership-scoped.
- Names/roles alone never authorize destructive cleanup.
- Unmanaged nested/shared/multi-scene data has runtime safety coverage.
- Base Build/preset switching is offline; optional remote assets require explicit user/network permission.
- Historical migration is explicit and the baseline stays byte-identical.
- Exact generated ZIP is validated/installed in isolated Blender profiles in CI on Windows and Ubuntu.

## Immediate sequence

1. Finish and merge #23 provenance audit.
2. Finish #3/#10/#12 reconciliation and native static Extension repository/install gate in cloud CI.
3. Update release/install/update/troubleshooting docs from verified behavior.
4. Run one final exact-ZIP Windows + Ubuntu cloud gate.
5. Keep visual renders deferred unless explicitly approved.
6. Begin #28 Product Quality.

Use `AGENTS.md`, this file, the owning GitHub issue and only the relevant `.skills/` before editing. Evidence before claims.
