# Device Visual Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fast, non-destructive visual review pipeline for all device BLEND/GLB candidates.

**Architecture:** A pure-Python discovery layer inventories unique candidates across authoritative worktrees, a Blender 5.2 script produces cheap diagnostic views without modifying sources, and a static HTML contact sheet presents the results. Review output lives outside canonical asset folders and can be regenerated.

**Tech Stack:** Python stdlib, Blender 5.2.1 Workbench/EEVEE, HTML/CSS/JS.

**Spec:** User-approved chat design, 2026-09-16.

## Global Constraints

- Never modify source `.blend` or `.glb` candidates.
- Render front/back/left/right/top/bottom/front-3q/back-3q.
- Tier 1 is cheap: material/clay plus diagnostic wire/normals/silhouette sheets.
- GLB and BLEND are reviewed independently.
- Prefer 640 px diagnostics, no Cycles/DOF/volumetrics/high-sample rendering.
- Deduplicate byte-identical copies across worktrees while preserving provenance paths.
- Never delete rejected assets as part of review generation.

---### Task 1: Candidate inventory

**Files:**
- Create: `tools/device_review.py`
- Test: `tests/fast/test_device_review.py`

- [ ] Write failing tests for candidate classification, `.blend1` exclusion, hash deduplication and provenance retention.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement minimal inventory/manifest generation.
- [ ] Run targeted tests and broader fast suite.

### Task 2: Blender diagnostic renderer

**Files:**
- Create: `tools/device_review_blender.py`

- [ ] Add eight deterministic camera views and cheap render modes.
- [ ] Use Workbench for clay/wire/normals/silhouette and EEVEE for material preview.
- [ ] Import GLB into a fresh scene; open BLEND read-only through a separate Blender process.
- [ ] Smoke-render one candidate with Blender 5.2.1 and verify PNG output.

### Task 3: Review surface

**Files:**
- Modify: `tools/device_review.py`

- [ ] Generate static `index.html`, `manifest.json`, and local decision state.
- [ ] Group by device/version/format and expose KEEP/MAYBE/REJECT controls.
- [ ] Generate Tier-1 review output for discovered candidates.
- [ ] Verify `git diff --check`, tests, output manifest and source immutability.
- [ ] Commit and push isolated branch; update issue #53 with evidence.