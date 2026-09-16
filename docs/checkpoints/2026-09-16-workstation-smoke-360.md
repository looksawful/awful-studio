# AWFUL STUDIO workstation smoke checkpoint — run 360

Date: 2026-09-16

Release source head: `aa7d1da38f7a6d5d2733d8c434c3d2c9757f2e70` (`agent/39-smoke-blockers`).

Qualified GitHub Actions run: `35145891298` / Extension QA #360.

Exact candidate: `awful_studio-0.0.17.zip`

Exact candidate SHA-256: `660a4c68948a17c21ab375b0fb9790d491b00be521569eef571e6dbd97e3483d`

GitHub Actions candidate artifact id: `10467701090` (`extension-candidate`).

Cloud qualification is GREEN for fast tests, canonical Ubuntu Blender 5.2.1 runtime, native Extension Repository install on Ubuntu, the exact same Ubuntu-built ZIP on Windows, and native Extension Repository install on Windows.

This candidate supersedes `334c3b31b014d547ff0e8e13d1275a68416a1f3127cd66b992a74cd686930d35`. Workstation smoke on that older candidate found a real runtime defect: after procedural mockup replacement, orphan AWFUL-owned mesh datablocks kept `MAT_AWFUL_Diagnostic` at nonzero users while no owned scene object used it, so `REG.material('MAT_DIAGNOSTIC')` became invisible and Post Pipeline validation failed.

The defect was fixed with TDD in PR #83. Cloud run #327 proved the regression RED; run #328 proved the focused production fix GREEN; PR #83 then merged to the release branch as `aa7d1da38f7a6d5d2733d8c434c3d2c9757f2e70`.

Titan recovery state:

- Blender 5.2.1 LTS is installed at `D:\Blender Foundation\Blender 5.2\blender.exe`;
- user GPU backend previously verified as OPTIX with NVIDIA GeForce RTX 4070 Ti enabled;
- exact run-360 candidate downloaded to `A:\assets\AWFUL_STUDIO\candidates\run-360\awful_studio-0.0.17.zip`;
- local candidate SHA-256 verified as `660a4c68948a17c21ab375b0fb9790d491b00be521569eef571e6dbd97e3483d`;
- an interactive Blender process was observed running, so the normal installed extension was not replaced while that session was active;
- attempts to launch a second isolated-profile Blender through Desktop Commander stalled before the probe script produced output; these stalls are not candidate failures.

Remaining release gate:

1. run non-render workstation smoke on the exact `660a4c68...` candidate with the real workstation GPU configuration;
2. verify Build Studio, all six procedural mockups, Fast/Quality Preview, Post Pipeline twice, save/reopen, Rebuild, Remove, and unmanaged-object survival;
3. run the human UI / Rendered Viewport smoke and camera navigation on the unchanged exact candidate;
4. only after those pass, merge PR #46, run the integrated post-merge gate, and tag/release the unchanged approved package.

Do not tag or publish 0.0.17 while the manual UI/Rendered Viewport gate is still open.
