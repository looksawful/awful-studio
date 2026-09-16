---
name: asset-network-safety
description: Offline-first network, download, cache and provenance rules for AWFUL STUDIO optional assets.
status: installed
---

# Asset and Network Safety

Base AWFUL operation is offline. Network is an explicit optional capability.

## Network gate

A download requires all of:

- an explicit user-triggered operator/action;
- AWFUL network preference enabled;
- Blender online access enabled;
- an allowlisted curated URL/resource.

Import/register/startup/update/Build/Rebuild and ordinary preset switching make zero network attempts.

## Download contract

- enforce a maximum byte count while streaming;
- use a temporary `.part` file and atomically replace only after validation;
- reject cache path escape and symlink targets;
- validate expected content format, not just HTTP success;
- record source URL, digest, byte count, license/provenance and status in sidecar metadata;
- remove partial payload on failure;
- do not silently follow an unexpected redirect to a different source.

## Cache deletion

Clear only known AWFUL cache entries whose provenance matches the curated source. Never recursively delete a user-configured directory. Unknown files remain untouched.

## Tests

Cover disabled gates, `--offline-mode`, disallowed URL, traversal/symlink, redirect, oversized response, invalid payload, interrupted download, stale/forged sidecar, valid cached reuse and safe clear.

When assets are missing or invalid, use the documented procedural/physical-sky fallback rather than downloading automatically.