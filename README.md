# AWFUL STUDIO

AWFUL STUDIO is a Blender-native virtual product and advertising studio for building editable product-shooting scenes, lighting rigs, camera setups, environments and motion presets without replacing Blender's native controls.

## Status

- Historical baseline: **Alpha 0.0.15** (`historical/0.0.15/awful_studio_v4_2_gpu_perf.py`).
- Current target: **Alpha 0.0.16 Extension Foundation** on `feature/extension-foundation`.
- Blender target: **5.2 LTS**; exact verified runtime: **Blender 5.2.1**, build `9e2066aef7ef`.
- Exact official Windows/Linux distribution pins: `runtime/blender.lock`.
- 0.0.16 is not public-release-ready until the remaining provenance and native Extension repository/update gates are reconciled, but the core lifecycle and accepted P0 systems already have exact-package Blender 5.2.1 Windows/Ubuntu CI evidence.

Historical source SHA-256:

```text
5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b
```

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
docs/                     engineering plans and references
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
- Render/image regression tests are not mandatory for 0.0.16 and must not run locally without explicit user approval.
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

`pytest-blender` was evaluated as a candidate but is not required. AWFUL uses its thinner custom harness because the release contract must test the final Blender Extension ZIP, lifecycle, isolated profile, save/reopen and migration behavior rather than merely import source into Blender Python.

## Extension installation

Candidate packages are built with Blender's official Extension CLI. Direct `Install from Disk` is useful for isolated candidate testing, but the final user path is a Blender-native Extension repository so install/update can use Blender's Extensions UI.

Do not treat a package as a release merely because it imports. Release evidence must cover the exact ZIP, isolated install/enable/disable/re-enable/restart/save/reopen/migrate behavior, offline guarantees and the native repository/install/update path required by the current release issue.

## Optional third-party assets

Base Build contains no mandatory media downloads. Optional HDRIs are explicit opt-in cache assets. Provenance and third-party licenses are documented separately in `docs/THIRD_PARTY_ASSETS.md` once the provenance slice is integrated.

## Agent skills and integrations

`.skills/README.md` lists project-local workflow adapters for TDD, debugging, verification, Git isolation/review, Blender runtime/lifecycle/data safety, network/cache safety, performance, release and handoff.

External tools such as Blender Agent Studio and Flue remain explicit pilot/candidate integrations until exact-version Blender 5.2 evidence justifies a supported status. Do not introduce a second runtime harness merely because another tool can launch Blender too. Apparently one reproducible test system is less fashionable than three conflicting ones, but it is considerably easier to maintain.

## Production readiness

- Current handoff: `STATE.md`
- P0 roadmap: GitHub issue #27
- Cloud-only completion batch: GitHub issue #33
- Design: `docs/superpowers/specs/2026-09-10-awful-studio-production-readiness-design.md`
- Implementation plan: `docs/superpowers/plans/2026-09-10-awful-studio-production-readiness.md`
- Official Blender Extension references: `docs/references/blender-extension-development.md`

Current implementation truth is the latest GitHub issue/PR/CI evidence, not an old prose claim in a README.
