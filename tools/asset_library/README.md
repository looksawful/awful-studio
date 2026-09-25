# AWFUL asset-library tooling

Canonical scripts for the external asset library at `F:\AWFUL_ASSETS`.

- `rebuild_geometry_nodes.py`: staged build → cards → embed → validation → publish.
- `check_geometry_nodes_fail_closed.py`: proves failures after build/cards/embed/validate do not mutate the canonical bundle or last-known-good checkpoint.
- `build_asset_index.py`: inode-aware duplicate index.
- `check_asset_index_determinism.py`: proves two consecutive index runs are identical and generated reports are not self-indexed.
- `scan_blender_assets.py` → `scan_asset_metadata_open.py` → `audit_catalog_resolution.py`: Blender Asset Browser inventory and catalog validation.

Generated CSV/JSON/previews stay under `F:\AWFUL_ASSETS\_catalog`; they are evidence, not canonical source.
