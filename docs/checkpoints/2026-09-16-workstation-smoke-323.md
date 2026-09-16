# AWFUL STUDIO workstation smoke checkpoint

Date: 2026-09-16

Release candidate source commit: `15cc82c4f07c62c2331b8db470034f3fad95894d`

Qualified GitHub Actions run: `35112620822` / Extension QA #323.

Exact candidate: `awful_studio-0.0.17.zip`

Exact candidate SHA-256: `334c3b31b014d547ff0e8e13d1275a68416a1f3127cd66b992a74cd686930d35`

GitHub Actions candidate artifact id: `10453475568` (`extension-candidate`).

Cloud qualification state at this checkpoint:

- fast tests: passed;
- Ubuntu Blender 5.2.1 candidate build/runtime: passed;
- native Blender Extension Repository install on Ubuntu: passed;
- Windows Blender 5.2.1 runtime: passed;
- four PaintedPlaster PNG assets restored as real binary PNG files;
- `.gitattributes` now prevents line-ending normalization for bundled binary assets.

Titan state observed before this checkpoint:

- Blender 5.2.1 LTS build `9e2066aef7ef` is installed;
- the exact `334c3b31...` candidate was successfully installed into the normal `user_default` Blender extension repository;
- Blender reported `STATUS Installed "awful_studio"` with process exit code 0;
- the exact candidate was also downloaded to `A:\assets\AWFUL_STUDIO\candidates\run-323\awful_studio-0.0.17.zip`;
- local SHA-256 matched `334c3b31b014d547ff0e8e13d1275a68416a1f3127cd66b992a74cd686930d35`.

The remaining release gate is workstation/manual smoke. The release branch and exact candidate must not be changed merely to persist smoke tooling, therefore this checkpoint lives on `checkpoint/workstation-smoke-323`, forked from the qualified source commit.

`tools/workstation_smoke.py` persists the non-render workstation smoke harness in GitHub. It checks the installed extension using the normal Blender profile: configured GPU backend, Build Studio, six procedural mockups, Fast/Quality Preview, Post Pipeline setup/rebuild, save/reopen, Rebuild, Remove, and survival of unmanaged user data.

The last local invocation did not execute the smoke because PowerShell attempted to tee output into a non-existent `workstation` directory before Blender started. This is a harness-launch failure, not evidence about AWFUL runtime behavior.

Next safe sequence:

1. ensure the workstation output directory exists;
2. run Blender 5.2.1 `--background --python tools/workstation_smoke.py` using the normal user profile;
3. preserve `normal_profile_smoke.json` and relevant log output outside the workstation immediately;
4. if the smoke finds an AWFUL defect, create one focused fix commit on the release work branch, push immediately, then rebuild/requalify a new exact candidate;
5. if the automated workstation smoke passes, run the remaining human UI/Rendered Viewport smoke against the unchanged `334c3b31...` candidate;
6. do not merge/tag/publish 0.0.17 until that human gate passes.
