# AWFUL STUDIO agent guide

Read this file first, then `STATE.md`, then the GitHub issue for the task you are executing. Read Notion only when the issue does not contain enough product/business context.

## Project

AWFUL STUDIO is a Blender-native virtual product and advertising studio. Target runtime: Blender 5.2 LTS. Historical baseline: Alpha 0.0.15 (`awful_studio_v4_2_gpu_perf.py`, internal `4.2-gpu-perf`). The next foundation release is Alpha 0.0.16 as a Blender Extension.

## Sources of truth

- Notion AWFUL STUDIO: product/business requirements and architecture decisions.
- GitHub Issues: implementation tasks and acceptance criteria.
- Repository: code, tests, runtime metadata and engineering evidence.
- `.skills/`: repeatable workflow adapters only, never project state.

Do not create another project-management system or duplicate the full Notion backlog into repository docs.

## Non-negotiable engineering rules

- Preserve Blender-native editing. Do not duplicate ordinary Blender transforms and native controls without a real AWFUL-specific reason.
- Blender behavior requires real Blender 5.2 runtime evidence. Static Python checks are not sufficient.
- Render tests are not required for the current foundation work.
- Performance regressions are bugs, but do not build a heavyweight benchmark framework without evidence that it is needed.
- Enabling/disabling the Extension must not build, rebuild or destructively modify the current scene.
- Studio build/rebuild may delete only AWFUL-managed data. Unmanaged user data must survive.
- Base studio build must work offline. Network assets are opt-in/explicit.
- Do not relax product requirements to satisfy tests or tools.
- Do not call an external integration `supported` unless the exact pinned version has passed relevant Blender 5.2 runtime verification.

## Start every executable task

Run:

```bash
python tools/awful.py status
python tools/awful.py doctor
```

If Blender is needed locally and `doctor` reports it missing:

```bash
python tools/awful.py bootstrap
```

For runtime evidence:

```bash
python tools/awful.py test-runtime
```

The same runtime test path must be usable locally and in GitHub Actions.

## GPT Chat vs GPT Work

Use GPT Chat primarily for focused analysis, code review, small patches, debugging, test design and architecture decisions. Do not bootstrap Blender for tasks that do not depend on Blender behavior.

Use GPT Work for repository-wide changes, downloads/uploads, browser work, dependency audits, CI/release infrastructure, packaging and long multi-step execution. Work should execute safe actions rather than merely describe them.

Both modes should prefer GitHub Actions for canonical remote Blender runtime evidence. Local Blender execution is an acceleration path, not a prerequisite for reasoning about unrelated code.

## Git workflow

Do not implement substantial changes directly on `main`. Use short-lived branches named `agent/<issue>-<short-name>`. Keep commits focused. Delete stale agent branches after merge.

Before claiming completion:

1. run relevant static checks;
2. run Blender runtime checks for Blender-dependent behavior;
3. inspect the final diff;
4. record exact evidence in the GitHub issue;
5. update `STATE.md` only when verified project state changed.

## External integrations

Statuses mean exactly:

- `reference`: useful example only;
- `candidate`: under consideration, not installed/supported;
- `pilot`: deliberately being evaluated;
- `supported`: pinned and verified in the required runtime;
- `rejected`: evaluated and intentionally not adopted.

See `integrations/manifest.toml` for current status.
