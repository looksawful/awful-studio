# AWFUL STUDIO

AWFUL STUDIO is a Blender-native virtual product and advertising studio for building editable product-shooting scenes, lighting rigs, camera setups, environments, procedural product mockups and motion presets without replacing Blender's native controls.

## Status

- Historical baseline: **Alpha 0.0.15** (`historical/0.0.15/awful_studio_v4_2_gpu_perf.py`).
- Current target: **Alpha 0.0.17 pre-release candidate**.
- Blender target: **5.2 LTS**; exact verified runtime: **Blender 5.2.1**, build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins: `runtime/blender.lock`.
- Structural/runtime qualification is cloud-first and uses the exact built Extension ZIP on Windows and Ubuntu.
- The final manual UI smoke remains the last human gate before 0.0.17 is tagged or published.

Historical source SHA-256:

```text
5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b
```

## Branch contract

The accepted repository topology is:

- `dev` = working/integration branch;
- `prod` = production/release/deploy branch.

Feature/agent branches integrate into `dev`. Release/tag/deploy work advances from `dev` to `prod` only after the owning release gates pass. Do not redefine branch topology from stale branch names in historical PRs or documentation.

## Repository map

```text
extension/awful_studio/   Blender Extension package source
historical/0.0.15/        immutable historical baseline
runtime/blender.lock      exact verified Blender runtime pins
tests/fast/               pure/static policy and tooling tests
tests/runtime/            real Blender packaged-runtime contracts
tools/awful.py            agent/human status, doctor, fast, bootstrap, runtime entrypoint
tools/setup_blender.py    official Blender download/checksum bootstrap
tools/verify_extension.py official build + exact-ZIP runtime verifier
integrations/             external integration status/pins
.skills/                  thin AWFUL-specific workflow adapters
.agents/                  research/checkpoint/evidence notes
docs/                     install, release, engineering plans and references
AGENTS.md                  default instructions for agents/contributors
STATE.md                   current engineering handoff
```

## Development rules

Start with `AGENTS.md`, then `STATE.md`, the owning GitHub issue/PR and only the `.skills/` needed for the task.

Key invariants:

- Blender behavior requires real Blender 5.2 runtime evidence; static tests are not proof of `bpy` behavior.
- Import/register/enable/restart must not build or mutate a scene.
- Build/Rebuild are explicit user actions and preserve Blender's native device selection.
- Base studio operation is offline; optional asset downloads require explicit opt-in.
- Rebuild/Remove/migration preserve unmanaged and shared user data.
- Heavy post/compositor/volume paths remain opt-in.
- Ordinary structural QA contains no render invocation and must not probe local GPU hardware automatically.
- Notion owns product/business/accepted architecture requirements. GitHub Issues own implementation work/status/evidence.

## Tests and runtime

Fast checks, no Blender:

```sh
python -m unittest discover -s tests/fast -v
```

Agent-oriented pure status/health checks:

```sh
python tools/awful.py status
python tools/awful.py doctor
python tools/awful.py fast
```

`status` and `doctor` do not launch Blender and do not use the network.

The canonical runtime is cloud-first. GitHub Actions downloads the exact official Blender 5.2.1 distribution, verifies Blender's official SHA-256, validates/builds the Extension with Blender's own CLI, then executes the **exact generated ZIP** in isolated profiles on Windows and Ubuntu.

Explicit runtime bootstrap:

```sh
python tools/awful.py bootstrap --destination .blender
```

Explicit full runtime verification:

```sh
python tools/awful.py test-runtime --blender <path-to-blender>
```

Outside CI the underlying verifier refuses to launch full Blender runtime unless the caller deliberately adds `--allow-local-blender`. Ordinary development should use fast tests locally and packaged runtime in CI.

## 0.0.17 scope

The current candidate includes:

- ownership-safe Build/Rebuild/Remove and historical migration;
- photographic lighting and Flash family;
- metric cyclorama and independent studio architecture visibility;
- full product-bounds camera framing;
- Pure HDRI / Physical Sky / managed Sun natural-light semantics;
- independent Product/Camera Once / Loop / Ping-Pong playback;
- reviewed optional-asset provenance and offline cache safety;
- procedural Bottle / Jar / Box / Can / Phone / Tablet mockups;
- deterministic offline starter materials and Auto Fit integration;
- native static Blender Extension repository generation/sync/install verification.

The separate visual-regression/render harness is not a release blocker. The required remaining human acceptance step is the manual UI smoke documented in `docs/releases/0.0.17.md`.

## Extension installation and update

Use `docs/INSTALL_UPDATE.md` for the verified Install from Disk and Blender Extension Repository workflows, update rules and troubleshooting.

Candidate packages are built with Blender's official Extension CLI. A package is not considered published merely because it imports or passes CI: tagging/release/deploy happens only after the final manual UI smoke.

## Optional third-party assets

Base Build contains no mandatory media downloads. Optional HDRIs are explicit opt-in cache assets. Provenance and third-party licenses are documented in `docs/THIRD_PARTY_ASSETS.md`.

## Agent skills and integrations

`.skills/README.md` lists project-local workflow adapters for TDD, debugging, verification, Git isolation/review, Blender runtime/lifecycle/data safety, network/cache safety, performance, release and handoff.

External tools such as Blender Agent Studio and Flue remain optional research items. They are not required for AWFUL STUDIO 0.0.17 readiness and must not replace the canonical runtime path.

## Release references

- Current handoff: `STATE.md`
- Install/update: `docs/INSTALL_UPDATE.md`
- 0.0.17 release notes and final smoke gate: `docs/releases/0.0.17.md`
- Third-party assets: `docs/THIRD_PARTY_ASSETS.md`
- Official Blender Extension references: `docs/references/blender-extension-development.md`
- Completed product roadmap: GitHub issue #27
- Pre-smoke release prep: GitHub issue #37

Current implementation truth is the latest accepted GitHub issue/PR/CI evidence, not stale historical branch names or prose claims.
