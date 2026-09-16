# HANDOFF — Storybook production + AWFUL STUDIO device mockups

Date: 2026-09-16

You are taking over active work from a previous ChatGPT session. Do not restart discovery from zero. Work directly with GitHub + Remote Desktop Commander on Titan. The user expects execution, commits, merges and verified artifacts, not plans/status-only replies.

## User operating style
- Russian.
- Execute immediately; do not ask for confirmation for routine safe work.
- Prefer one-pass conflict-free work, then concise factual progress.
- Use Superpowers skills when applicable, especially systematic-debugging, TDD, verification-before-completion, using-git-worktrees, finishing-a-development-branch.
- Never claim completion without fresh verification.
- Do not change authored site copy/words unless explicitly requested.
- Clean temporary files after accepted work, but never delete the only source of an unfinished asset.

## 1. Production Storybook / looksawful.ru
Repository: looksawful/looksawful.ru

The live/private production Storybook is the `lab` line. Do NOT merge old long-lived Storybook histories wholesale into prod/dev.

Already completed during handoff:
- PR #986 `Lab: enforce project component Storybook parity` was marked ready and MERGED into `lab`.
- Merge commit: `77e0cb4294a327a92bc03ed7765fd046d904d16a`.
- #986 exact head before merge: `8e503fc49085d5725988f245586f9ba2f9228814`.
- Private Lab Verify run 35035145059 was green; PR body also records typecheck, parity contracts, isolated Lab build, Storybook/parity inventory and isolation checks as PASS.
- PR #924 old stacked `storybook/final-integration` was CLOSED as superseded. Do not revive it or `storybook/dev-integration` wholesale.

Open Storybook work that still matters:

### PR #928 — verified integration-state promotion
URL: https://github.com/looksawful/looksawful.ru/pull/928
Head: `storybook/integration-states-promote`
Head SHA: `6c764032633253eaa506b95af0ac1bf0ce2db06b`
Targets: `dev`
Scope: 14 bounded files for production-backed Project Navigation, Media Deck, Media Lightbox, Animated Canvas Gallery, Home visibility, inventory/contracts/browser smoke.
Old exact-head checks were all green: Fast CI, Private Lab Verify, CodeQL, Dependency Review, PR Preview.
BUT `dev` has moved materially since the branch was created. A handoff review comment was added. Do NOT merge old evidence blindly.
Next action: sync/replay ONLY this bounded 14-file slice onto current `dev` in an isolated worktree, inspect diff for hitchhikers, rerun exact-head checks, merge if clean/green. Never merge stale Storybook history wholesale.

### PR #949 — Foundations token visualization
URL: https://github.com/looksawful/looksawful.ru/pull/949
Head SHA: `44779ba1e5091344f2a91eba2ffc5055c2ad20f8`
Targets: `dev`
Scope: Storybook/Lab only, canonical site CSS remains source of truth.
Current checks: Private Lab Verify GREEN, CodeQL GREEN, Dependency Review GREEN; Fast CI RED, PR Preview RED.
A handoff review comment was added explicitly blocking promotion until those failures are understood.
Next action: inspect Fast CI and PR Preview job logs, find root cause (likely drift/current dev interaction, do not guess), fix/rebase/sync minimally, rerun exact-head checks, merge only when all required gates are green.

### Important Storybook boundary
- `lab` is private/read-only/noindex review surface.
- Production-backed stories must reuse canonical production renderers/data/CSS; do not create Storybook-only fake product APIs or duplicate authored markup/CSS.
- `project-teaser` remains a type-only contract without renderer and is intentionally blocked by issue #967. Do not invent a Lab-only renderer merely for parity.
- If adding AWFUL STUDIO/device mockup review into Storybook, first find an existing production-backed 3D/media component pattern. Add it only if it can reuse production assets/runtime cleanly; otherwise track it rather than fabricating a one-off Storybook implementation.

## 2. AWFUL STUDIO device mockups
Repository: looksawful/awful-studio
Local root: `A:\Projects\CODE\awful-studio`
Blender: `D:\Blender Foundation\Blender 5.2\blender.exe`
Remote device Titan ID: `775215fd-bbe3-4173-b277-fcc99cc5a15d`

Linked worktrees:
- iPhone: `A:\Projects\CODE\awful-studio\.worktrees\iphone-17` branch `asset/iphone-17`
- iPad: `A:\Projects\CODE\awful-studio\.worktrees\ipad-pro` branch `asset/ipad-pro`
- MacBook: `A:\Projects\CODE\awful-studio\.worktrees\macbook-pro` branch `asset/macbook-pro`

Review/handoff folder was cleaned and normalized:
`A:\Projects\CODE\awful-studio\assets\device_mockups\LATEST_MODELS`
Contains only:
- `iphone_17_CURRENT_RELEASE_v15.blend`
- `iphone_17_WORKING_v19.blend`
- `ipad_pro_11_CURRENT_WORKING_v6.blend`
- `ipad_pro_13_CURRENT_WORKING_v6.blend`
- `macbook_pro_14_CURRENT_RELEASE_CANDIDATE_v1.blend`
- `STATUS.txt`
Source of truth remains the worktrees, not LATEST_MODELS.

One-off patch/probe scripts were cleaned from iPhone/iPad; latest generators/QA/evidence/previews remain. Do not delete latest unfinished generator/evidence.

### iPhone 17
Branch `asset/iphone-17`.
Last committed/public safe runtime-backed version: v15.
Important commits:
- previews: `fab5424`
- runtime/finalize v15: `c4ad21a`
Issue #50 has a fresh handoff comment.

Verified dimensions: 71.5 × 149.6 × 7.95 mm.
Official local reference: `assets/device_mockups/iphone_17/reference/apple_iphone_17_dimensional_drawings_2025-09-09.pdf`.

Newer v18/v19 work fixed several real root causes:
- rear camera cluster had been mirrored to the wrong side in back view;
- flash was on wrong side of housing;
- Apple decal UV was mirrored;
- front camera cover used wrong material;
- old front camera/TrueDepth stack protruded outside verified front envelope;
- rear diagnostic cameras pointed to obsolete mirrored side.
Regression scripts `qa_camera_logo_v18.py` / `qa_camera_logo_v19.py` were used and v19 passed camera/logo geometry QA plus dimensional/non-manifold/boolean QA.

However v19 is NOT publishable. After correctly moving the TrueDepth/front optics inside the 7.95 mm envelope, the Dynamic Island/front camera became visually hidden behind the screen stack. This is the current blocker.
Do NOT publish v19 and do NOT replace v15 CURRENT with it.

Next iPhone task = v20:
1. Write/extend regression test first.
2. Rebuild the front display/cutout stack so Dynamic Island/front camera/sensors are visible through the correct front surface while every component remains inside verified envelope.
3. Do not solve by simply pushing optics outward again.
4. Preserve the corrected rear camera side/flash/logo orientation from v18/v19.
5. Render and inspect front, front_sensor_macro, back, camera_macro, 3/4, sides, bottom, screen edge.
6. Run full QA: dimensions, non-manifold, booleans, mandatory objects, camera/logo regression, front-envelope regression.
7. Only after visual acceptance create CURRENT/delivery, runtime GLB + Meshopt, manifest, validation; then commit/push and update #50/#53.

### iPad Pro M5 11/13
Branch `asset/ipad-pro`.
Commits:
- previews v6: `9381df5`
- generator/blends/evidence v6: `8087e77`
Issue #51 has fresh handoff comment.

v6 QA is green individually:
11-inch: 177.499995 × 249.699995 × 5.3 mm, non-manifold 0, 28 boolean cuts, mandatory_missing=[]
13-inch: 215.499997 × 281.599998 × 5.1 mm, non-manifold 0, 28 boolean cuts, mandatory_missing=[]
Stage is still LOW_DRAFT.

Remaining iPad work:
- visually review latest v6 hero/macros after final lighting pass;
- fix only concrete visual defects, do not restart geometry casually;
- create runtime canonical GLB + Meshopt web GLB + manifest + round-trip validation using same contract as iPhone v15;
- promote to LOW only after individual 11/13 visual gates;
- update LATEST_MODELS and issue #51/#53.

### MacBook Pro 14
Branch `asset/macbook-pro`.
Commits:
- preview set: `6647276`
- reproducible release candidate: `7eee470`
Issue #52 has fresh handoff comment.

Current QA release candidate:
- base expected/actual ~312.6 × 221.2 × 8.3 mm
- lid ~312.0 × 4.7 × 212.0 mm
- base/lid non-manifold 0
- hinge open angle 102°
- mandatory_missing=[]
- object_count 283, material_count 9

This is NOT portfolio-publishable yet. Major LOW polish remains:
- Space Black materials / stop white-gray overexposure;
- better base/lid silhouette, radii, seams and underside;
- hinge physical clearance + presets CLOSED/30/60/90/102, collision-safe range;
- screen/glass/notch/FaceTime stack;
- keyboard/trackpad/speaker perforations/ports;
- proper studio render set;
- runtime package after visual/mechanical approval.

## 3. GitHub issue state
Fresh handoff comments were added to awful-studio issues:
- #50 iPhone
- #51 iPad
- #52 MacBook
- #53 device integration
Materials policy remains tracked in #54.

## 4. Immediate next execution order
Do real work in this order unless fresh evidence says otherwise:
A. Storybook production hygiene first:
   1. Verify current `lab` contains merge `77e0cb4` from #986 and run/fetch post-merge verification if available.
   2. Repair #949 Fast CI/PR Preview failures and merge only after all gates green.
   3. Refresh #928 onto current dev, bounded 14-file diff, exact-head full checks, then merge if green.
   4. Close any newly proven-superseded Storybook integration PRs, but do not close active unrelated work.
B. Device assets:
   1. iPhone v20 front stack + full QA + runtime packaging.
   2. iPad v6 visual acceptance + GLB/Meshopt/runtime package.
   3. MacBook LOW polish + mechanics + render QA + runtime package.
C. Storybook/device handoff:
   - if a production-backed viewer exists, surface accepted device assets in the private Storybook/Lab without duplicating runtime logic; otherwise open/annotate an issue instead of inventing a fake viewer.
D. Cleanup:
   - keep only accepted CURRENT/delivery assets plus necessary latest working source;
   - delete throwaway patch/probe scripts after their changes exist in a retained generator/commit;
   - never delete the only source of an unfinished model;
   - finish with clean/status-explained worktrees and update issues.

## 5. Verification discipline
Before saying anything is done:
- GitHub work: exact-head CI/checks green on CURRENT base, not stale prior-base evidence.
- Blender: regenerate from source, verify dimensions, non-manifold, mandatory objects, boolean count, visual macro/hero review.
- Runtime: import GLB back into clean Blender, verify expected root/anchors/names/envelope; web Meshopt may have bounded quantization but canonical GLB must stay dimensionally exact.
- Git: inspect diff/status; no unrelated or temporary files in commits.

No user manual action is currently required. Continue autonomously with available connectors/tools and leave blockers in issues if they cannot be safely solved.
