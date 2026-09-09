# Pinned Blender runtime

AWFUL STUDIO development is pinned to Blender 5.2.1 LTS for the current foundation work.

`blender.lock` is the machine-readable source for the exact Linux runtime archive, checksum and extraction layout.

Distribution order used by `tools/awful.py bootstrap`:

1. AWFUL STUDIO GitHub Release asset `runtime-blender-5.2.1` when available;
2. official Blender Foundation download as a fallback;
3. SHA-256 verification before extraction.

The large Blender archive is intentionally not committed to ordinary Git history and does not require Git LFS. `.runtime/` and `.cache/` are local/generated directories and must remain untracked.

The Blender binary is a separate GPL-licensed upstream distribution. AWFUL does not modify Blender as part of this runtime bootstrap.
