# Blender Agent Studio

Status: pilot.

Pinned upstream:
- Repository: https://github.com/ifBars/blender-agent-studio
- Commit: `1f9e050b17ecbb9174c93a001bece7fdbe73f436`
- Plugin version: `0.6.2`

This directory is intentionally not a vendored copy of the upstream repository.

Current AWFUL policy:
- Reuse selected validation/evidence/refinement methods through project-local adapters.
- Evaluate the full plugin separately on representative AWFUL tasks.
- Do not let BAS umbrella routing replace AWFUL orchestration or project state.
- Do not mark the full plugin or MCP as supported until Blender 5.2 runtime evidence exists.

See `.agents/blender-agent-studio-pilot.md` and `.agents/bas-selected-skills-manifest.md`.
