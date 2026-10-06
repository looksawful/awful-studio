# iPhone Human Gate mobile UX critique — 2026-10-07

⚠️ DEGRADED: single-context (no isolated sub-agent/Task runner or Impeccable detector executable is exposed in this session).

Target: the existing Storybook iPhone review surface, especially mobile Human Gate use.

## Deterministic browser evidence

Live Webcmd/Playwright inspection of the exact #146 story at a 390×844 viewport:

- exact candidate label is correct: `iPhone 17 - HUMAN GATE #146 (ba4ef30c)`;
- viewer client width: ~375 px;
- viewer scroll width: 450 px;
- canvas width: ~449 px;
- horizontal overflow: ~75 px in the Webcmd browser environment;
- all seven select controls are ~28 px high;
- all five buttons are ~28 px high;
- no JavaScript/page errors were observed.

The independent four-width Playwright audit found:
- 320 px viewport: ~130 px horizontal overflow;
- 390 px viewport: ~60 px overflow;
- 430 px viewport: ~20 px overflow;
- 768 px viewport: no horizontal overflow.

This matches the owner's iPhone screenshots: the control panel clips content and consumes too much of the review surface.

## Design health

| # | Nielsen heuristic | Score / 4 | Finding |
| --- | --- | ---: | --- |
| 1 | Visibility of system status | 3 | Candidate/hash and current selections are visible, but review progress and gate state are not. |
| 2 | Match system / real world | 3 | Expert 3D terms are appropriate; the layout does not match touch-device usage. |
| 3 | User control and freedom | 3 | Orbit/zoom/view presets exist; mobile overflow makes some controls awkward. |
| 4 | Consistency and standards | 2 | Selects, buttons, checkboxes and range controls form a dense toolbar with weak mobile hierarchy. |
| 5 | Error prevention | 2 | No explicit review-coverage guard before a Human Gate verdict. |
| 6 | Recognition rather than recall | 2 | Too many controls are exposed simultaneously; labels are terse and clipped on narrow screens. |
| 7 | Flexibility and efficiency | 2 | Powerful desktop controls, but poor expert-mobile efficiency. |
| 8 | Aesthetic and minimalist design | 1 | Toolbar dominates the artifact and reduces inspection space. |
| 9 | Error recovery | 2 | Model errors can be reported, but the Human Gate path has no explicit recovery/status treatment. |
| 10 | Help and documentation | 1 | The surface does not explain what must be reviewed before PASS/REJECT. |
| **Total** |  | **21/40** | **Functional desktop tool, weak mobile review instrument.** |

## Priority findings

### P0 — mobile horizontal overflow

The viewer hard-codes a 560 px minimum stage height and the rendered canvas remains about 449 px wide on a 320–430 px host. Controls also extend past the viewport.

The review surface must be width-safe at 320 px and above. Horizontal page scrolling is unacceptable for Human Gate.

### P1 — artifact is not visually primary

The toolbar takes roughly 216 px before the model begins. On the owner's phone the first interaction is with controls, not the device.

Human Gate should be canvas-first. The artifact should occupy the viewport; secondary controls should be disclosed only when needed.

### P1 — touch targets are desktop-sized

Controls are approximately 28 px high. For the mobile Human Gate, primary touch controls should be at least 44 px high.

### P1 — review state is underspecified

Candidate identity is visible, but the surface does not expose:
- current Human Gate state;
- which required views/modes have been inspected;
- PASS/REJECT affordance associated with the exact candidate.

Do not turn this into bureaucracy. A compact review-progress cue is enough.

### P2 — technical typography is over-applied

The entire viewer uses monospace. Candidate hash, measurements and diagnostic values benefit from monospace; ordinary control labels do not.

Use the incumbent dark technical visual language but let controls use the system UI face for faster scanning.

## Shape brief

**Job and audience:** one expert owner reviews one exact 3D candidate on desktop or iPhone and must be able to judge geometry quickly.

**Outcome:** the model is the primary surface; candidate identity is impossible to confuse; render/clay/wireframe and critical view presets are one tap away; secondary settings never steal canvas space.

**Direction:** preserve the dark technical review world. Move from a permanent dense toolbar to a canvas-first HUD plus one collapsible inspector/bottom sheet.

**Boundaries:** do not create a second viewer or review pipeline; do not alter model bytes; reuse the current Storybook/Three.js viewer and exact-candidate verification.

**States:** loading, model/provenance error, exact candidate ready, fullscreen, narrow portrait, landscape, long candidate label, offline/Tailscale failure.

## Throwaway UI prototype

Three 390×844 variants were built against a real exact-candidate wireframe capture.

- **A — structured canvas:** compact status bar, top render-mode strip, inspector button, fixed verdict bar.
- **B — floating HUD:** status and verdict float over a fully immersive canvas.
- **C — minimal review:** candidate identity only at top; render/clay/wire and inspector sit near the bottom; verdict bar is the only persistent bottom chrome.

Recommendation: **C** as the mobile base, with A's explicit hash/status treatment retained in a compact disclosure. It gives the model the most space while preserving fast expert controls.

The prototype is intentionally throwaway and is not committed into the product.

## Hardening requirements

Before productionizing the selected direction:

- no horizontal overflow at 320, 390, 430, 768, 1024 and 1440 px;
- touch targets >=44 px on mobile;
- safe-area insets respected;
- portrait and landscape verified;
- 200% zoom does not hide the gate controls;
- long candidate names/hashes truncate without hiding identity;
- loading/provenance/model errors have explicit recovery;
- orbit/pinch gestures are not intercepted by overlays;
- keyboard focus remains visible on desktop;
- reduced-motion/no-animation path remains functional;
- no new viewer, no new model-loading path, no new candidate identity source.

## Polish decision

Do **not** polish the existing permanent toolbar. Its mobile structure is the problem. Shape the canvas-first review composition first, then run one bounded polish pass after implementation.

## Build gate

Production UI implementation should begin only after the owner confirms the selected mobile direction.

Production topology TDD should begin only after the owner confirms the visible-surface quality seam. Current recommendation remains:
- major visible caps/panels: minimum triangle angle >= 5°;
- aspect ratio <= 10;
- thin physical bevel/thickness strips exempt when their existing surface-error contract passes.

Those values are a project quality bar, not a Blender/glTF standard.
