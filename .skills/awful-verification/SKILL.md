---
name: awful-verification
description: Mandatory evidence gate before saying an AWFUL STUDIO change is fixed, passing, ready, mergeable or releasable.
status: installed
---

# AWFUL Verification

Evidence before claims. A previous run or another agent's summary is not fresh verification.

## Match evidence to the change

- Pure Python/tooling: targeted tests + relevant fast suite.
- `bpy` behavior: real Blender 5.2 runtime test.
- Extension lifecycle/package: exact built ZIP installed and executed in isolated profile/process.
- Ownership/destructive logic: fixtures proving unmanaged/shared/multi-scene data preservation.
- Migration: physical-state comparison, idempotence and save/reopen.
- Network/cache: offline/no-attempt and cache-boundary tests.
- Performance-sensitive path: repeatable timing/count comparison.
- Visual output change: visual evidence only when the task actually requires it; renders are not a blanket 0.0.16 gate.

## Before commit/PR handoff

Run fresh:

```sh
python -m unittest discover -s tests/fast -v
git diff --check
```

and the appropriate Blender/runtime command for the changed subsystem.

Read exit codes and full failure counts. Do not describe a partial suite as the full suite.

## Before release-ready claim

Verify against the exact candidate package:

- source validate;
- package build;
- ZIP validate;
- install;
- enable/disable/re-enable;
- restart/reopen;
- offline Build/Rebuild/Remove;
- ownership and migration contract;
- Linux and Windows target evidence;
- native update path;
- approved license consistency;
- package SHA-256 and evidence artifacts.

If any required item was not executed, say `unverified` or `blocked`, not `should pass`.