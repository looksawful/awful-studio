---
name: git-change-review
description: Review AWFUL STUDIO implementation changes for evidence, scope, accidental business-text changes and generated/private asset leakage before merge.
---

# Git change review

For a non-trivial implementation change, verify:

- the issue or requested behavior is explicit;
- acceptance evidence is described and matches the changed surface;
- there is no unrelated formatting/refactor churn;
- user/business text was not changed accidentally;
- generated renders, benchmark traces and large/private assets are absent unless intentionally versioned;
- external integrations are described as candidate/pilot/installed/supported accurately;
- relevant Blender 5.2 runtime, visual and performance evidence is present when required.

Review the diff as a product/runtime change, not merely as Python text. A small diff can still be dangerous if it changes scene lifecycle, render defaults or managed data.
