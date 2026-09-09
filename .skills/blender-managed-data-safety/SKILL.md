---
name: blender-managed-data-safety
description: Scene-scoped ownership, cleanup, rebuild and migration safety for AWFUL STUDIO generated Blender datablocks.
status: installed
---

# Blender Managed Data Safety

Use before changing ownership, registry lookup, Build/Rebuild/Remove, product mounting or migration.

## Authorization model

A name or `awful_role` identifies semantics, not ownership. Destructive authority requires explicit AWFUL-managed metadata plus the active scene/studio owner ID.

Never use `as_pointer()`/allocator addresses as durable owner identity across deletion/recreation. Never adopt all globally new `bpy.data` blocks after an operation unless each block's provenance is otherwise proven.

## Scene scope

Every destructive loop must answer:

- does this block belong to the active owner?
- is the relationship being changed part of the active scene/studio?
- is the block shared by another scene/user datablock?
- what unmanaged data depends on it?

Do not detach, unlink, reset or delete an unmanaged object in another scene merely because its parent is managed somewhere else.

## Preservation cases

Runtime tests must cover:

- unmanaged object nested in managed collection;
- unmanaged child parented under managed object with world transform preservation;
- unmanaged nested collection;
- user object reusing generated material/image;
- shared object/data/material across two scenes;
- duplicate role/name without owner tag;
- previous user world/camera restoration;
- repeated rebuild with bounded datablocks.

## Migration

Historical metadata migration may establish owner/schema tags only when provenance is unambiguous. It must not reconstruct/reset scene appearance or transforms. Ambiguity is a safe error, not permission to guess.

## Failure safety

Run schema/ownership preflight before destructive mutation. If an operation fails after mutation begins, do not post-hoc mark unrelated data as managed. Prefer explicit tagging at creation sites and small reversible operations.