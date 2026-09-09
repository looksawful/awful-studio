# AWFUL STUDIO

AWFUL STUDIO is a Blender-native virtual product and advertising studio for building editable product-shooting scenes, lighting rigs, camera setups, environments and motion presets without replacing Blender's native controls.

## Status

- Historical baseline: **Alpha 0.0.15** (`historical/0.0.15/awful_studio_v4_2_gpu_perf.py`).
- Target: **Alpha 0.0.16 Extension Foundation**.
- Blender target: **5.2 LTS**, current verification target **5.2.1**.
- Active Extension work: draft PR #11 on `feature/extension-foundation`.
- **0.0.16 is not release-ready yet.** Fast tests exist, while final-ZIP Blender runtime, ownership/multi-scene safety, native update and release gates are still being completed.

The immutable historical source is checked by SHA-256:

```text
5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b
```

## Repository map

```text
extension/awful_studio/   Blender Extension package source
historical/0.0.15/        immutable historical baseline
tests/fast/               pure/static foundation tests
tests/runtime/            real Blender runtime contracts
tools/                    runtime/package verification tooling
integrations/             external integration status/pins
.skills/                  thin AWFUL-specific workflow adapters
.agents/                  research/checkpoint/evidence notes
docs/                     engineering plans and references
AGENTS.md                  default instructions for agents/contributors
STATE.md                   short current engineering handoff
```

## Development rules

Start with `AGENTS.md`, then `STATE.md`, the relevant GitHub issue/PR and only the `.skills/` needed for the task.

Key invariants:

- Blender behavior requires real Blender 5.2 runtime evidence; static tests are not proof of `bpy` behavior.
- Import/register/enable/restart must not build or mutate a scene.
- Build/Rebuild are explicit user actions.
- Base studio operation is offline; optional asset downloads require explicit opt-in.
- Rebuild/Remove/migration must preserve unmanaged and shared user data.
- Heavy post/compositor/volume paths remain opt-in.
- No mandatory render tests are required for the current 0.0.16 foundation.
- Notion remains authoritative for product/business/accepted architecture requirements. GitHub Issues own implementation work and status.

## Tests

Fast checks:

```sh
python -m unittest discover -s tests/fast -v
```

The canonical Blender runtime path is currently being reconciled in issues #3 and #12. Do not create a second bootstrap/test implementation. For current exact commands and blockers, read `STATE.md` and the active issue before running Blender QA.

The release contract ultimately validates/builds with Blender's own Extension CLI and executes the **exact generated ZIP** in isolated Blender profiles/processes.

## Extension installation

The source tree already contains an Alpha 0.0.16 Extension candidate, but no public package should be treated as a verified release until the release gates in `docs/superpowers/specs/2026-09-10-awful-studio-production-readiness-design.md` pass.

The intended final user flow is a Blender remote Extension repository so Blender can install and update AWFUL STUDIO through its native Extensions UI. `Install from Disk` is used for candidate testing, not as proof of native update behavior.

## Agent skills and integrations

`.skills/README.md` lists the installed project-local workflow adapters for TDD, debugging, verification, Git isolation/review, Blender runtime/lifecycle/data safety, network/cache safety, performance, release and handoff.

External tools such as Blender Agent Studio, Flue or pytest-blender keep explicit `candidate`/`pilot`/`reference` status until exact-version Blender 5.2 evidence justifies calling them supported.

## Production-readiness plan

- Design: `docs/superpowers/specs/2026-09-10-awful-studio-production-readiness-design.md`
- Implementation plan: `docs/superpowers/plans/2026-09-10-awful-studio-production-readiness.md`
- Official Blender Extension references: `docs/references/blender-extension-development.md`

Do not infer release readiness from this README. The current source of implementation truth is the active GitHub issue/PR evidence.