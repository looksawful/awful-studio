# Device Mockups Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the current device-mockup task with verified current assets, review renders, runtime packages, and clean GitHub state for iPhone 17, iPad Pro 11/13, and MacBook Pro 14.

**Architecture:** Keep each device isolated in its existing asset worktree. Promote only QA-verified versions to CURRENT/LATEST, keep presentation renders separate from source assets, and require regression QA before publishing replacements.

**Tech Stack:** Blender 5.2.1 LTS, Python generators/QA, Git worktrees, GLB/glTF + Meshopt, GitHub.

**Spec:** Current project requirements and Apple dimensional drawings stored under each asset reference directory.

## Global Constraints

- iPhone verified dimensions: 71.5 × 149.6 × 7.95 mm.
- iPad 11 verified dimensions: 177.5 × 249.7 × 5.3 mm.
- iPad 13 verified dimensions: 215.5 × 281.6 × 5.1 mm.
- MacBook closed dimensions: 312.6 × 221.2 × 15.5 mm; target open angle 102°.
- Production geometry keeps silhouette, mechanics, true openings, and major depth.
- Never promote a version to CURRENT unless geometry QA and visual review both pass.
- Do not start production UV/bake before LOW approval.

---