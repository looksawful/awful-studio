# Extension Foundation checkpoint — 2026-09-09

Engineering handoff for [issue #10](https://github.com/looksawful/awful-studio/issues/10) and [draft PR #11](https://github.com/looksawful/awful-studio/pull/11).
Notion remains authoritative for product and architecture decisions; issues own implementation status. This document records verification evidence and restart instructions, not a separate roadmap.

## Resume point

- Branch: `feature/extension-foundation`.
- Verified source commit: `fc04cc262d56ee248db300ebd2fbbe677cf26241`.
- Checkpoint: source foundation is committed; Blender runtime acceptance remains blocked.
- Do not merge, tag a production release, or call Alpha 0.0.16 ready from this evidence.
- Fetch the branch and inspect its current head before editing: other contributors may have advanced it.

## Source available in the branch

- `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`: immutable monolithic baseline.
- `extension/awful_studio/blender_manifest.toml`: version 0.0.16 Extension manifest.
- `extension/awful_studio/__init__.py`: registration, preferences, scene state, explicit Build/Rebuild/Remove/Reset/Migrate commands.
- `extension/awful_studio/core/legacy.py`: adapted implementation retaining the historical studio logic.
- `extension/awful_studio/ownership.py`: scene ownership and managed cleanup.
- `extension/awful_studio/migrations.py`: explicit historical metadata migration.
- `extension/awful_studio/asset_cache.py`: optional network/cache layer.
- `tests/fast/test_foundation.py`: five source/manifest/baseline checks.
- `tests/runtime/extension_contract.py`: real Blender contracts, no render tests.
- `tools/setup_blender.py`: exact 5.2.1 distribution download and checksum verification.
- `tools/verify_extension.py`: official validation/build and isolated final-ZIP runtime phases.
- `.github/workflows/extension-ci.yml`: fast checks and Linux/Windows runtime jobs.

Presence of these implementations is not evidence that Blender behavior passes.

## Fresh verification

On 2026-09-09 the files were restored from the exact GitHub source commit through the connector because shell cloning was unavailable.

```sh
python3 -m unittest discover -s tests/fast -v
```

Exit 0: 5 tests passed (0.078 seconds).
The baseline SHA-256 is exactly:
`5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.

A first local reconstruction introduced an extra final newline and failed the hash check. Restoring the exact repository bytes resolved it; no baseline source was changed or uploaded.

[CI run 34328053010](https://github.com/looksawful/awful-studio/actions/runs/34328053010), for the source commit above:
- Fast job 102389840348: passed, including `git diff --check`.
- Windows runtime job 102389868425: failed at installation.
- Linux runtime job 102389868426: failed at installation.
- Both logs confirm `HTTP Error 403: Forbidden` while opening the official `blender-5.2.1.sha256` URL.
- Final-ZIP validation/runtime and candidate upload were skipped.
- Evidence upload also failed because installation had not produced the requested evidence files.

No Blender executable was run in this checkpoint turn. The earlier conversation reported an independent official-packager validation/build, but its artifact and provenance were not recovered here; do not treat that report as a verified deliverable of this commit.

## Next bounded work

1. Resolve the official distribution/checksum access failure. Independently verify the exact official version and URLs before changing the pin; do not silently substitute another Blender version or bypass checksum checks.
2. Run the existing final-ZIP harness with a verified Blender 5.2 executable:

```sh
python tools/setup_blender.py --destination .blender
python tools/verify_extension.py --blender /absolute/path/to/blender
```

On Windows pass the full `blender.exe` path. The setup command prints the executable path.
The harness validates/builds the ZIP and runs historical, install, reopen and migrate phases. Preserve `dist/*.log`, `dist/*.json` and the distribution provenance. Investigate the first real failure before changing code.
3. Verify install/enable/disable/re-enable/restart, offline explicit build/rebuild, unmanaged data preservation, schema/migration and save/reopen against the packaged extension. Runtime coverage must be reviewed too; a green source test does not replace a missing runtime scenario.
4. Reconcile fixes mentioned in the previous session with the actual branch, especially role-only ownership access and animation-created datablock tagging. Only committed code and runtime evidence count.
5. Improve setup-failure evidence capture so CI preserves the download error without masking a failed required job.
6. After runtime passes, finish installation/update/uninstall/troubleshooting documentation and the gated candidate/release and native static update-repository infrastructure. These are not delivered by the current workflow.

## Delivery and integration limits

- PR #11 stays draft; issue #10 stays open.
- No verified release ZIP, production release, tag, or Pages update repository is published by this checkpoint.
- Existing README still describes initialization; it must be reconciled before release.
- No external integration was installed or promoted to supported in this checkpoint. Consult the existing integration audit and related issues; Blender 5.2 runtime evidence remains mandatory.
- No render tests are required by the current user brief.
- No user action is required to resume from GitHub: another agent can fetch the branch and continue with issue #10.
