# Zero-cost QA tooling

This layer is optional and does not replace the canonical Blender 5.2 Extension QA path in `tools/awful.py` and `.github/workflows/extension-ci.yml`.

## Asset receipts

Generate a deterministic local receipt without Blender or network access:

```sh
python tools/awful.py asset-metrics path/to/model.glb --output dist/model.metrics.json
```

The receipt contains only bounded file metadata: name, extension, byte size and SHA-256. It deliberately omits absolute filesystem paths.

## Tooling doctor

```sh
python tools/awful.py tooling-doctor
```

Docker, SonarQube Community and CircleCI CLI are optional. Their absence does not fail canonical AWFUL STUDIO QA.

## SonarQube Community

`sonar-project.properties` contains the local project definition. `compose.sonar.yml` provides an operator-started Community Build. Nothing starts automatically and Blender never contacts it.

CircleCI is not part of this slice because the existing GitHub Extension QA already owns fast and runtime release verification. Adding a second authoritative copy would violate the repository's single canonical QA-path rule.
