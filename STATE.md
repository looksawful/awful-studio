# AWFUL STUDIO Current State

Last reviewed: 2026-09-12

This is the short engineering handoff. Product requirements live in the accepted specs; implementation status/evidence lives in GitHub Issues, PRs and CI.

## Release state

- Historical baseline: Alpha 0.0.15, immutable source at `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`.
- Historical SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Current target: Alpha 0.0.17 corrective pre-release candidate.
- Blender target: 5.2 LTS; exact verified runtime is Blender 5.2.1 build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins are recorded in `runtime/blender.lock`.
- The old pre-smoke ZIP with SHA-256 `cc3a404ecc00e82e82716c91aece6260affd3c30d92bff1330b540965e489540` is defect-reproduction evidence only and must not be released.
- Manual-smoke corrective work is tracked by #39 / draft PR #46.
- #40 product grounding, #41 Timeline synchronization, #42 Hybrid lighting/background, #43 HDRI workflow and #44 Post Pipeline are engineering-complete.
- #45 viewport performance is structurally implemented; its final acceptance is the manual Rendered Viewport check on the new exact candidate with a deliberately configured Blender GPU scene.
- PR #46 run #240 (`34692939833`) passed fast checks, exact Blender 5.2.1 packaged runtime and native Extension Repository install on Ubuntu and Windows using one canonical ZIP.
- The final manual UI smoke remains the last human acceptance gate before tag/publication/deploy. Structural CI does not replace it.

## Canonical runtime architecture

There is one canonical path. Do not build another pytest/bootstrap/runtime stack.

- Fast/pure gate: `python -m unittest discover -s tests/fast -v`.
- Agent entrypoint: `python tools/awful.py status|doctor|fast|bootstrap|test-runtime`.
- Exact Blender bootstrap: `tools/setup_blender.py`.
- Exact Extension ZIP verifier: `tools/verify_extension.py`.
- Blender lifecycle contract: `tests/runtime/extension_contract.py`.
- Batched structural contracts: `tests/runtime/p0_suite.py` plus focused packaged-runtime phases.
- CI: `.github/workflows/extension-ci.yml` on GitHub-hosted Windows and Ubuntu runners.

The harness validates Blender's official Extension build output and runs the exact generated ZIP inside isolated Blender profiles. One cloud-built candidate is reused byte-for-byte on Windows rather than rebuilt per OS.

## Runtime and performance policy

- Ordinary local development must not launch full Blender runtime or probe GPU hardware automatically.
- `tools/verify_extension.py` refuses local full runtime unless `--allow-local-blender` is explicitly supplied; CI is allowed automatically.
- Structural runtime contains no render invocation.
- Build/Rebuild preserves Blender's native Cycles device/backend selection and never silently rewrites CUDA/OPTIX/HIP/ONEAPI/METAL preferences.
- AWFUL exposes explicit `Fast Preview` and `Quality Preview` modes that change viewport-only Cycles settings, not final render settings.
- AWFUL diagnostics make CPU-backed Cycles sessions visible to the user instead of silently presenting them as an AWFUL slowdown.
- Local smoke evidence on the target RTX workstation showed the original isolated smoke profile used `compute_device_type = NONE` and `scene.cycles.device = CPU`; the user's normal Blender profile has OPTIX configured, but a new scene can still remain on CPU until Blender's scene Device is set to GPU Compute.
- Structural contracts share Blender processes where safe instead of relaunching Blender for every assertion.

Cloud Build/Rebuild remains sub-second; Rendered Viewport performance is a separate user-machine/device concern and is not measured by render CI.

## Verified 0.0.17 corrective behavior

Packaged Blender 5.2.1 structural evidence now covers:

- deterministic product/support grounding from real world-space bounds, including built-in Bottle / Jar / Box / Can / Phone / Tablet and Auto Fit/Rebuild paths;
- Product and Camera Once / Loop / Ping-Pong with synchronized Blender Preview Range, independent actions and bounded modifiers;
- Hybrid Studio + World lighting with independent environment illumination and camera-visible background brightness;
- reviewed HDRI bulk download workflow, explicit Blender/AWFUL network permissions, status/error handling and Physical Sky fallback without changing selected HDRI intent;
- optional `Setup Post Pipeline` with live Blender 5.2 capability detection, Light Groups, render passes, managed compositor, idempotent rebuild and save/reopen ownership safety;
- explicit Fast/Quality viewport profiles and non-render performance diagnostics;
- existing photographic lighting, camera framing, cyclorama/architecture, Natural Light, ownership safety, asset provenance, migration and native Extension Repository contracts.

## Safety invariants

- Import/register/enable/restart do not build a scene.
- Build/Rebuild/Remove are explicit and ownership-scoped.
- Names/roles alone never authorize destructive cleanup.
- Unmanaged nested/shared/multi-scene data has runtime safety coverage.
- Base Build/preset switching is offline; optional remote assets require explicit user/network permission.
- Historical migration is explicit and the baseline stays byte-identical.
- Exact generated ZIP is validated/installed in isolated Blender profiles in CI on Windows and Ubuntu.
- Product mockup replacement may remove only AWFUL-owned mockup data; unmanaged user products survive.
- Post Pipeline creates managed data only inside the existing scene owner scope, including after save/reopen.
- Render/image regression remains separate and non-blocking for this release candidate.

## Remaining gate to MVP/release

1. finish release-document reconciliation on PR #46;
2. run the fresh canonical `awful_studio-0.0.17.zip` gate after the documentation commit;
3. merge the accepted corrective PR into `feature/extension-foundation` and run the integrated exact-candidate gate;
4. identify/download the exact integrated candidate and its SHA-256;
5. run the final manual UI smoke on that exact ZIP, including Rendered Viewport with Blender scene Device deliberately set to GPU Compute for the performance check;
6. if smoke passes, tag and publish 0.0.17 using the repository's actual release process.

No tag or public release is created before the manual smoke passes.

Use `AGENTS.md`, this file, the owning GitHub issue/PR and only the relevant `.skills/` before editing. Evidence before claims.
