# Ticket #146 exact whole-device candidate

Technical integration gate for the exact iPhone 17 v30 candidate. This is not Human PASS.

- writer HEAD before #146 evidence commit: `45cc11b`
- source revision: `9b1913cbd9fa9188dd61c119c7731e4d6ea9aa6ab520e0ca39ee347da65de1f5`
- compat SHA-256: `ba4ef30c68ef93470eff6d8d472d78454ad51f99a727469a8f6d12fa58eda05c`
- Meshopt SHA-256: `57f25b2a72741e7ea630fa5580e112e6f4a40c4a2830813bb901e8690edf7b07`
- delivery.blend SHA-256: `650aeb1f82fb73d612d7ac9731f589fe93daddc9ac9e41897c9513cb7464f67b`
- plugin bundle SHA-256: `82173e9bdfb0c22d521ea939ed4dd7343600bcfdd87e8d3b516ac6414f4b40a3`
- 51 mesh nodes / 57 total nodes / 12,634 triangles
- browser exact-candidate audit: 10 review views, five finishes, screen on/off, 0 page errors
- compat/Meshopt semantic identity: 51/51 mesh nodes, identical parent hierarchy/material bindings, max world-bound drift 0.0044 mm (limit 0.01 mm)
- fast: 213/213 GREEN
- preview: 25/25 GREEN
- Blender runtime: 17/17 GREEN
- Storybook build + smoke: GREEN
- Khronos compat + Meshopt: 0 errors / 0 warnings

Human Gate remains pending. PR #119 stays HOLD; no merge/deploy.
