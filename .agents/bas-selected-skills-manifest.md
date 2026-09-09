# Blender Agent Studio selected-skills manifest

Purpose: record exactly which upstream material is being evaluated for GitHub issue #2.

Pinned upstream repository: `ifBars/blender-agent-studio`
Pinned commit: `1f9e050b17ecbb9174c93a001bece7fdbe73f436`
Observed plugin version: `0.6.2`
License declared by upstream plugin: MIT
Target runtime for AWFUL validation: Blender 5.2 on Windows

## First-pass selected inputs

| Upstream skill | Pilot status | AWFUL use |
|---|---|---|
| `blender-asset-validation` | selected | deterministic scene/asset inspection and multiview evidence |
| `blender-iterative-refinement` | selected | freeze → critic ledger → smallest repair → identical recheck |
| `blender-rendering-workflow` | selected | reproducible render contract and evidence opening |
| `blender-procedural-workflow` | selected | editable generator contract and parameter-surface tests |
| `blender-animation-workflow` | conditional | camera/product motion evidence only |
| bounded MCP server | separate experimental variable | inspection/render tooling only after explicit runtime verification |

## Explicit non-selection for core pilot

- character workflow;
- simulation workflow;
- art-direction intake as a source of product requirements;
- generic game-ready/GLB delivery requirements;
- BAS umbrella routing as authoritative orchestration;
- benchmark gauntlets for ordinary AWFUL feature work.

## Local adapter

The project-local `.skills/blender-evidence-loop/SKILL.md` is an AWFUL-specific pilot adapter. It is not a copy or installation of the BAS plugin and does not make BAS a project dependency.

## Verification state

- Upstream repository inspected: yes.
- Upstream commit pinned: yes.
- Selected upstream skill contents inspected: yes for asset validation, iterative refinement, rendering, procedural workflow.
- Full BAS plugin installed into AWFUL environment: no.
- BAS MCP executed against Blender 5.2: no.
- Representative AWFUL runtime comparison completed: no.
- Supported dependency status: no.
