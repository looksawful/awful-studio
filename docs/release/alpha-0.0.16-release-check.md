# Alpha 0.0.16 release candidate and native update path

Status: infrastructure prepared; **not release-ready** until all gates below have fresh evidence.

## Scope

This document covers packaging, exact-candidate evidence, static Blender Extension repository generation, GitHub Pages-ready output, and native update verification. It does not replace runtime, ownership, migration, asset, or performance acceptance work tracked elsewhere.

## Canonical candidate

The release candidate is exactly one ZIP built with Blender Extension tooling from one reviewed source commit. The same ZIP must be exercised on Linux x64 and Windows x64.

Expected Alpha package:

```text
awful_studio-0.0.16.zip
```

Manifest authority:

```text
extension/awful_studio/blender_manifest.toml
id = awful_studio
version = 0.0.16
blender_version_min = 5.2.0
blender_version_max = 5.3.0
```

Do not hand-edit a built ZIP. Any source change requires a new candidate ZIP, new SHA-256, and new runtime evidence.

## Official Blender commands

The release workflow uses the official Extension CLI surface:

```sh
blender --command extension validate --source-dir extension/awful_studio
blender --command extension build --source-dir extension/awful_studio --output-dir dist
blender --command extension validate dist/awful_studio-0.0.16.zip
```

The static repository is generated only after the evidence gate opens:

```sh
blender --command extension server-generate --repo-dir=/path/to/repository --html
```

Official Blender 5.2 references:

- https://docs.blender.org/manual/en/5.2/advanced/extensions/getting_started.html
- https://docs.blender.org/manual/en/5.2/advanced/extensions/creating_repository/static_repository.html
- https://docs.blender.org/manual/en/5.2/advanced/command_line/extension_arguments.html

`server-generate` creates `index.json`; `--html` also creates a static `index.html`. Those files plus the exact ZIP are sufficient for static hosting. AWFUL STUDIO additionally ships `release-metadata.json` beside them for human/agent auditability.

## Release evidence contract

`tools/release_pipeline.py` records:

- source commit SHA;
- extension version;
- exact candidate filename;
- candidate size;
- candidate SHA-256;
- Linux runtime evidence;
- Windows runtime evidence;
- Blender version used by each runtime;
- explicit license approval state;
- release-gate reasons.

The metadata file is deterministic for identical inputs.

The publication gate remains closed unless all of these are true:

1. Linux x64 evidence exists and reports `status = passed`.
2. Windows x64 evidence exists and reports `status = passed`.
3. Both runtime records report Blender 5.2.x.
4. Both runtime records name `awful_studio-0.0.16.zip`.
5. Both runtime records contain the SHA-256 of the exact candidate ZIP used by the repository job.
6. Public-release licensing has been explicitly approved for this candidate run.

A failed or missing runtime job cannot be converted into a publishable candidate by artifact upload, `continue-on-error`, missing reports, or a similarly inventive CI loophole.

## Licensing gate

The current manifest declares:

```text
SPDX:GPL-3.0-or-later
```

The repository also currently contains GPL licensing material. This is technically consistent with Blender Extension distribution requirements, but **the project does not treat that fact as owner authorization to publish Alpha 0.0.16**.

The release workflow therefore defaults `license_approved` to `false`. The owner must explicitly set it to true for a specific candidate run before a static repository can be generated. If this decision changes, root/package LICENSE files, manifest metadata, SPDX headers, and release documentation must remain mutually consistent.

## GitHub Actions separation

Normal PR/runtime validation remains in:

```text
.github/workflows/extension-ci.yml
```

Release-candidate orchestration lives separately in:

```text
.github/workflows/release-candidate.yml
```

The release workflow is manual-only. It has read-only repository permissions, does not deploy GitHub Pages, does not create tags, and does not create GitHub Releases. When the gate is open it uploads:

- `candidate-zip`;
- `runtime-linux-x64`;
- `runtime-windows-x64`;
- `release-candidate-evidence`;
- `extension-repository-pages`;
- a GitHub Pages-ready artifact generated from the same static repository directory.

Actual public deployment is intentionally a separate owner-controlled action after final release review.

## Running the workflow

From GitHub Actions, select **Alpha Release Candidate** and run it on the exact reviewed branch or commit.

For a non-public evidence pass, leave `license_approved = false`. The workflow will still exercise fast checks, build the candidate and runtime jobs, write closed-gate metadata, then fail the repository stage deliberately. This is expected.

For a release-candidate repository build, set `license_approved = true` only after the licensing decision is confirmed. Repository generation still requires both runtime jobs to pass on the same candidate SHA.

## Local metadata/gate check

Given one exact candidate and normalized Linux/Windows evidence:

```sh
python tools/release_pipeline.py metadata \
  --package dist/awful_studio-0.0.16.zip \
  --source-sha <commit-sha> \
  --evidence evidence/linux/release-runtime.json \
  --evidence evidence/windows/release-runtime.json \
  --output dist/release-metadata.json \
  --license-approved
```

Generate the static repository only from open-gate metadata:

```sh
python tools/release_pipeline.py repository \
  --blender /path/to/blender \
  --package dist/awful_studio-0.0.16.zip \
  --metadata dist/release-metadata.json \
  --output-dir pages
```

The repository command refuses closed metadata and refuses a candidate whose name/SHA/version no longer match the recorded evidence.

## Native update verification

Install-from-file proves packaging, not remote update behavior. Before Alpha 0.0.16 is declared complete, verify the Blender-native remote path separately.

1. Produce an open-gate static repository with `index.json`, `index.html`, the exact ZIP, and `release-metadata.json`.
2. Host the directory on a temporary/static URL or use a local `file:///.../index.json` repository for plumbing verification.
3. In a clean Blender 5.2 profile, add the repository under **Get Extensions → Repositories**.
4. Sync the repository and install the known lower test version or a purpose-built pre-release fixture.
5. Publish a repository index containing a higher compatible test version built through the same gate.
6. Sync in Blender and confirm the higher version is discovered through the native Extension UI/CLI.
7. Execute native update.
8. Restart Blender and reopen ordinary plus AWFUL Studio files.
9. Re-run the relevant runtime/ownership/migration contracts against the updated installation.
10. Record repository URL, old/new versions, candidate SHAs, Blender version/platform, and runtime report artifacts.

Do not manufacture a fake `0.0.17` production version merely to test updates. Use a disposable prerelease fixture or the next real version once its manifest/version policy is agreed.

## Current blockers

At the time this infrastructure was added, Alpha 0.0.16 remains blocked by independent runtime and product-safety work, including issue #3 and issue #10 review findings. In particular, release publication must remain closed while canonical Blender 5.2 runtime evidence is missing or failing.

The current runtime bootstrap has also previously encountered an HTTP 403 while fetching Blender checksum metadata. That belongs to the canonical runtime/bootstrap workstream; this release branch intentionally does not modify `tools/setup_blender.py` or `tools/verify_extension.py` to avoid conflicting implementations.

## Final release checklist

- [ ] `python3 -m unittest discover -s tests/fast -v` passes.
- [ ] `git diff --check` passes.
- [ ] Official manifest validation passes.
- [ ] Candidate built by official Blender Extension tooling.
- [ ] Built ZIP validates with official Blender tooling.
- [ ] Candidate filename/version matches manifest 0.0.16.
- [ ] Linux x64 runtime evidence passes on the exact candidate SHA.
- [ ] Windows x64 runtime evidence passes on the exact candidate SHA.
- [ ] Ownership/remove/rebuild blockers are closed with runtime evidence.
- [ ] Migration blockers are closed with runtime evidence.
- [ ] Offline/cache blockers are closed with runtime evidence.
- [ ] Performance acceptance for required Alpha scope is recorded.
- [ ] License/publication decision is explicitly approved and consistent in files.
- [ ] `release-metadata.json` reports `publishable: true`.
- [ ] Static repository is generated by Blender `server-generate`.
- [ ] Generated `index.json` references exactly the verified candidate ZIP.
- [ ] GitHub Pages/static-hosting output is reviewed before deployment.
- [ ] Native repository install/update path is verified in clean Blender 5.2.
- [ ] Restart/reopen after native update passes.
- [ ] Final docs describe only behavior supported by fresh evidence.
- [ ] Only then create the public tag/release/deployment.
