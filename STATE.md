# AWFUL STUDIO Current State

Last reviewed: 2026-09-11

This is the short engineering handoff. Product requirements live in Notion; implementation status/evidence lives in GitHub Issues and PRs.

## Release state

- Historical baseline: Alpha 0.0.15, immutable source at `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`.
- Historical SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Current target: Alpha 0.0.17 pre-release candidate.
- Blender target: 5.2 LTS; exact verified runtime is Blender 5.2.1 build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins are recorded in `runtime/blender.lock`.
- The integrated Product Quality candidate at `87ec06d49a65520020ac7c3331bdad27c39f2851` passed fast tests, exact-ZIP Blender 5.2.1 runtime and native Extension repository install on Windows and Ubuntu in CI #168.
- Issue #37 owns pre-smoke release preparation. A fresh candidate gate is required after those documentation/hygiene changes.
- The final manual UI smoke remains the last human acceptance gate before tag/publication/deploy. It is not replaced by structural CI.

## Branch contract

Accepted topology:

- `dev` = working/integration;
- `prod` = production/release/deploy.

Agent/feature work targets `dev`; release/tag/deploy advances to `prod` only after release gates pass. Historical PR bases and branch names do not redefine this contract. Do not mutate or close parallel work merely to normalize old topology.

## Canonical runtime architecture

There is one canonical path. Do not build another pytest/bootstrap/runtime stack.

- Fast/pure gate: `python -m unittest discover -s tests/fast -v`.
- Agent entrypoint: `python tools/awful.py status|doctor|fast|bootstrap|test-runtime`.
- Exact Blender bootstrap: `tools/setup_blender.py`.
- Exact Extension ZIP verifier: `tools/verify_extension.py`.
- Blender lifecycle contract: `tests/runtime/extension_contract.py`.
- Batched structural contracts: `tests/runtime/p0_suite.py` plus focused packaged-runtime phases.
- CI: `.github/workflows/extension-ci.yml` on GitHub-hosted Windows and Ubuntu runners.

The custom harness is intentionally retained because it validates Blender's official Extension build output and runs the exact generated ZIP inside isolated Blender profiles.

## Runtime and performance policy

- Ordinary local development must not launch full Blender runtime or probe GPU hardware automatically.
- `tools/verify_extension.py` refuses local full runtime unless `--allow-local-blender` is explicitly supplied; CI is allowed automatically.
- Structural runtime contains no render invocation.
- Build/Rebuild preserves Blender's native Cycles device selection and does not enumerate OPTIX/CUDA/HIP/ONEAPI/METAL.
- Structural contracts share Blender processes where safe instead of relaunching Blender for every assertion.
- Superseded CI runs for the same PR/ref are cancelled.
- Existing operation timings are collected from normal CI rather than adding render/GPU benchmark passes.

Verified cloud performance after #5:
- Windows Blender 5.2.1: Build about 0.231 s; Rebuild median about 0.240 s.
- Ubuntu Blender 5.2.1: Build about 0.107 s; Rebuild median about 0.111 s.

## Verified integrated work

Integrated with packaged Blender 5.2.1 Windows/Ubuntu evidence:

- photographic lighting / complete Flash family (#6/#22);
- full product-bounds camera framing (#19);
- metric cyclorama and visible studio architecture (#7/#21);
- Natural Light v2 / Pure HDRI / Physical Sky / managed Sun (#9);
- runtime performance and zero-local-GPU development policy (#5);
- independent Product/Camera Once / Loop / Ping-Pong playback (#8);
- machine-readable third-party asset provenance / cache authorization (#23);
- canonical runtime/release reconciliation and native static Extension repository gate (#3/#10/#12);
- procedural Bottle / Jar / Box / Can / Phone / Tablet, starter materials, Auto Fit and bounded rebuild behavior (#28).

## Safety invariants

- Import/register/enable/restart do not build a scene.
- Build/Rebuild/Remove are explicit and ownership-scoped.
- Names/roles alone never authorize destructive cleanup.
- Unmanaged nested/shared/multi-scene data has runtime safety coverage.
- Base Build/preset switching is offline; optional remote assets require explicit user/network permission.
- Historical migration is explicit and the baseline stays byte-identical.
- Exact generated ZIP is validated/installed in isolated Blender profiles in CI on Windows and Ubuntu.
- Product mockup replacement may remove only AWFUL-owned mockup data; unmanaged user products survive.
- Render/image regression remains separate and non-blocking for this release candidate.

## Release gate before manual smoke

Issue #37 must leave the repository in a state where the only remaining release action is the human smoke plus publication:

1. reconcile README/STATE to 0.0.17;
2. document Install from Disk and Extension Repository install/update paths;
3. document release notes, troubleshooting and the final smoke checklist;
4. pass pure/static release-hygiene checks;
5. run fresh exact `awful_studio-0.0.17.zip` Windows + Ubuntu cloud runtime;
6. pass native static Extension repository generation/sync/install on both platforms;
7. identify the exact candidate artifact/evidence for the manual smoke;
8. after the manual smoke passes, promote through the accepted `dev` → `prod` release path, tag and publish.

No tag or public release is created before the manual smoke passes.

Use `AGENTS.md`, this file, the owning GitHub issue/PR and only the relevant `.skills/` before editing. Evidence before claims.
