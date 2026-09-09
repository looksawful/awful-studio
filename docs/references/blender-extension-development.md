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

The source directory for Alpha 0.0.16 must contain `blender_manifest.toml` and `__init__.py`. Release verification uses Blender's own command-line extension tooling rather than constructing a ZIP with a custom archiver.

Canonical package checks:

```sh
blender --command extension validate extension/awful_studio
blender --command extension build --source-dir extension/awful_studio --output-dir dist
blender --command extension validate dist/awful_studio-0.0.16.zip
```

The exact built ZIP, not the source checkout, is what runtime QA installs and executes.

### Install/update

`Install from Disk` is useful for local package verification but belongs to a local repository and does not provide the remote update flow AWFUL wants. Native update behavior requires a remote Extension repository. Blender can generate a static repository listing with `extension server-generate`; AWFUL can host the generated files on GitHub Pages or equivalent static hosting.

Required update evidence:

1. install a published test package from the remote repository;
2. publish a higher test version;
3. sync/check updates;
4. update using Blender's native extension mechanism;
5. restart/reopen the saved AWFUL scene;
6. rerun lifecycle/schema/runtime assertions.

### Network permissions and offline behavior

Manifest permissions document capability; they do not replace runtime discipline. Blender's `--offline-mode` is part of the runtime contract. AWFUL must additionally ensure its own code makes no direct network attempt during import/register/startup/build/preset operations. Optional downloads require explicit user intent and Blender online access.

### Repository generation

Canonical static repository generation should use Blender itself:

```sh
blender --command extension server-generate --repo-dir dist/repository
```

Do not hand-maintain a second package index format if Blender can generate it.

## Project-specific evidence rules

- Target Blender: 5.2.1 for Alpha 0.0.16 verification.
- Runtime tests are structural/lifecycle/data-safety tests; renders are not required for this foundation.
- Both Linux CI and Windows verification matter before calling the package production-ready.
- Save/reopen and native update are part of compatibility, not optional documentation exercises.
- All final commands, Blender version, package SHA-256 and test reports should be retained as release evidence.