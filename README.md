# AWFUL STUDIO

Blender-native virtual product/ad studio project.

Project source of truth for business requirements and architecture currently lives in Notion. This repository is being initialized deliberately: agent tooling and QA infrastructure are added only after verification against the actual AWFUL STUDIO workflow.

## Agent infrastructure

- `.agents/skills-audit.md` — verified skill/workflow audit and adoption decisions.
- `.skills/README.md` — project-local skill policy and proposed adapters.

External skill packs are not considered installed or supported merely because they are documented here. Each integration requires a pinned version, a Blender 5.2 runtime check where applicable, and evidence recorded in its GitHub issue.
