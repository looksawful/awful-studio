---
name: release-readiness
description: Release-candidate and native Blender Extension repository gate for AWFUL STUDIO Alpha releases.
status: installed
---

# AWFUL Release Readiness

Use for candidate packaging, release workflows, GitHub Pages/static Extension repository work, tags and publication.

## Candidate rule

The candidate is the exact ZIP built by Blender Extension tooling from the reviewed commit. Source checkout tests do not substitute for package tests.

Record:

- source commit SHA;
- manifest version;
- Blender version/platform;
- package filename and SHA-256;
- required runtime reports/logs.

## Required package path

```sh
blender --command extension validate extension/awful_studio
blender --command extension build --source-dir extension/awful_studio --output-dir dist
blender --command extension validate dist/awful_studio-0.0.16.zip
```

Then install and execute that ZIP in isolated Blender user data.

## Publication gate

Do not publish/tag/deploy production packages when required Linux/Windows runtime evidence is failing or missing. Artifact-upload convenience must never turn a required job failure into success.

Licensing must be explicitly owner-approved and consistent across root/package LICENSE, manifest and SPDX headers before public release.

## Native update

Generate the static repository using Blender `extension server-generate`, publish only verified packages, then test install → higher-version discovery → native update → restart/reopen → runtime compatibility.

Install-from-disk is a package test, not proof of remote update behavior.

## Final release evidence

Before closing the release issue, independently verify every release gate from the production-readiness spec against fresh candidate evidence. Unexecuted gates are `unverified`, not assumed.