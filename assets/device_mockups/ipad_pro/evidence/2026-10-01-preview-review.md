# iPad preview review — 2026-10-01

Review of commit dda41de found that the committed LOW v6 previews still showed the previous nested-device artwork, although the shipped blends and GLBs already used the clean lock-screen image. The web builder intentionally skips expensive acceptance renders, so delivery regeneration alone does not refresh visual evidence.

Regenerated all seven existing camera views for each size using the current canonical generator and its render profiles on Blender 5.2.1 LTS. Updated the existing tracked preview paths under `previews/11/low_v6` and `previews/13/low_v6`; these now depict the delivered texture and current controls. Both generator validation reports passed. Fresh fast suite: 170 tests passed.

When geometry or a screen texture changes, refresh these acceptance previews separately from the web build. Visual LOW approval remains pending; refreshed evidence is not approval.
