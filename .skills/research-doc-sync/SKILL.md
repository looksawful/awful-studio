---
name: research-doc-sync
description: Keep AWFUL STUDIO research, verified project state, Notion requirements, GitHub implementation status and agent docs from drifting into competing sources of truth.
status: installed
---

# Research and Documentation Sync

Use when external research or an engineering decision changes project documentation.

## Classify information

Every important statement belongs to one category:

- verified current repository/runtime fact;
- Notion product/business/architecture requirement;
- external reference/documentation;
- recommendation/proposal;
- candidate/pilot integration status;
- verified installed/supported integration.

Do not present recommendations as current state.

## Where information lives

- Notion: product, business and accepted architecture requirements.
- GitHub Issues/PRs: implementation work, defects, acceptance and evidence.
- `AGENTS.md`: stable agent working rules.
- `STATE.md`: short current engineering handoff only.
- `.skills/`: repeatable methods only.
- `docs/references/`: external reference map and project interpretation.

Avoid copying full issue backlogs into docs or full Notion requirements into skills.

## Update rule

When runtime evidence disproves a document, update the stale statement in the same workstream or record the discrepancy in the owning issue. Cite exact versions/commits for external integrations. `installed`/`supported` requires actual environment/runtime evidence, not a README link.

Keep documentation concise enough that a new agent can start from `AGENTS.md` + `STATE.md` + relevant issue without rereading project history.