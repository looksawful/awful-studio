# External integrations

This directory is the controlled landing zone for third-party tools used while developing or testing AWFUL STUDIO.

Rules:
- Do not treat a tool as installed or supported just because a directory exists here.
- Pin every adopted dependency to an exact release or commit before use.
- Record upstream URL, license, purpose, Blender compatibility and verification status.
- Prefer adapters, manifests and setup scripts over vendoring entire third-party repositories.
- Do not duplicate product requirements or project state here. Notion remains the product/architecture source of truth; GitHub Issues remain implementation work items.
- Third-party code may only be vendored after its license and update strategy are reviewed.

Current integration slots:
- `blender-agent-studio/` — selective BAS methods / optional full-plugin pilot.
- `pytest-blender/` — candidate Blender runtime pytest harness.
- `flue/` — optional live Blender bridge candidate.
- `blender-addon-tester/` — reference-only multi-version add-on test harness.

See `manifest.toml` for the current status of each integration.
