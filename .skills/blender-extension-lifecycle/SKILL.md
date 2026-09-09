---
name: blender-extension-lifecycle
description: Blender Extension lifecycle discipline for AWFUL STUDIO registration, enable/disable, restart, package install and native update.
status: installed
---

# Blender Extension Lifecycle

Use when editing `__init__.py`, registration, properties, handlers, packaging or update behavior.

## Import/register boundary

Import/register may define/register classes, properties and handlers only. Do not resolve restricted scene context at module import. Do not Build, download, mutate scene datablocks or migrate automatically on enable/startup/update.

`register()` must be idempotent enough to fail/rollback cleanly. `unregister()` removes RNA/handlers/classes it registered without touching scene content.

## Required runtime sequence

Test the exact built ZIP:

1. install with enable disabled;
2. verify install preserves ordinary scene;
3. enable and verify no scene mutation;
4. disable and verify RNA/handlers removed, scene preserved;
5. re-enable twice and verify no accumulation;
6. save preferences and start a new Blender process;
7. verify Extension enabled but no auto-build;
8. open ordinary and AWFUL files;
9. disable/re-enable while a built studio exists and verify content unchanged.

## Failure handling

If registration fails midway, rollback only what this Extension registered in that attempt. Never fix a lifecycle error by performing scene construction earlier.

## Packaging/update

Lifecycle acceptance is against the ZIP produced by Blender's Extension build command. Native update gets its own restart/reopen test because update is not equivalent to source reload.