# Blender 5.2 Extension Development References

Verified reference set for AWFUL STUDIO. These links are external references, not project requirements; Notion and GitHub remain authoritative for AWFUL decisions and status.

## Official Blender 5.2 documentation

- Extension creation and manifest: https://docs.blender.org/manual/en/5.2/advanced/extensions/getting_started.html
- Extension command line (`build`, `validate`, `install-file`, `repo-add`, `sync`, `update`, `server-generate`): https://docs.blender.org/manual/en/5.2/advanced/command_line/extension_arguments.html
- Extension preferences, remote repositories and update behavior: https://docs.blender.org/manual/en/5.2/editors/preferences/extensions.html
- Third-party/static extension repositories: https://docs.blender.org/manual/en/5.2/advanced/extensions/creating_repository/index.html
- Blender production/offline deployment and `--offline-mode`: https://docs.blender.org/manual/en/5.2/advanced/deploying_blender.html

## AWFUL interpretation

### Packaging

The 0.0.17 Extension source contains `blender_manifest.toml` and `__init__.py`. Release verification uses Blender's own command-line extension tooling rather than constructing a ZIP with a custom archiver.

Canonical package checks:

```sh
blender --command extension validate extension/awful_studio
blender --command extension build --source-dir extension/awful_studio --output-dir dist
blender --command extension validate dist/awful_studio-0.0.17.zip
```

The exact built ZIP, not the source checkout, is what runtime QA installs and executes.

### Install/update

`Install from Disk` is useful for exact candidate verification but is not the production update channel. Native update behavior uses a Blender Extension Repository. Blender generates the static repository listing with `extension server-generate`; AWFUL verifies that repository through Blender's native `repo-add` / `sync` / install path in isolated CI profiles.

The production repository URL is published only after the final manual UI smoke. Do not invent a placeholder URL in release-facing docs or code.

Required publication/update evidence:

1. the exact candidate ZIP passes packaged runtime on Windows and Ubuntu;
2. Blender generates the static repository from the exact package;
3. an isolated Blender profile adds and syncs the repository;
4. Blender installs AWFUL STUDIO through the native repository path;
5. after the final manual UI smoke, the approved state is promoted through the accepted `dev` → `prod` release topology;
6. the production repository is published and exposes 0.0.17;
7. future update qualification uses a higher test version and Blender's native update path before that later release is published.

### Network permissions and offline behavior

Manifest permissions document capability; they do not replace runtime discipline. Blender's `--offline-mode` is part of the runtime contract. AWFUL additionally ensures its own code makes no direct network attempt during import/register/startup/build/preset/procedural-mockup operations. Optional downloads require explicit user intent and Blender online access.

Blender 5.2 also requires online access to be explicitly enabled for repository synchronization, including file-backed repository tests. The canonical repository gate therefore enables online mode only for the explicit repository sync/install operation; this does not make normal AWFUL scene operations network-dependent.

### Repository generation

Canonical static repository generation uses Blender itself:

```sh
blender --command extension server-generate --repo-dir dist/repository
```

Do not hand-maintain a second package index format if Blender can generate it.

## Project-specific evidence rules

- Target Blender: 5.2.1 for 0.0.17 verification.
- Runtime tests are structural/lifecycle/data-safety tests; renders are not required for the ordinary candidate gate.
- Linux and Windows cloud runtime must both pass before the candidate reaches the manual UI smoke.
- Save/reopen and native repository install are compatibility requirements, not optional documentation exercises.
- The manual UI smoke is the final human acceptance layer before tag/publication; it does not require rendering.
- Release/tag/deploy follows the accepted branch contract: `dev` = integration, `prod` = production/release/deploy.
- Final candidate identification must retain commit/run/artifact evidence; the published release must expose the exact approved package and SHA-256.
