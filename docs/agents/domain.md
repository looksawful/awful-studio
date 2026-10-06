# Domain docs

Layout: single-context.

- Read root `CONTEXT.md` for the project domain vocabulary and durable context before changing domain behavior.
- Record hard-to-reverse architectural decisions as ADRs under `docs/adr/`.
- Do not create `CONTEXT-MAP.md` or per-package contexts unless the repository actually becomes a multi-context monorepo.
- Keep transient task state in GitHub Issues and handoffs, not in `CONTEXT.md`.
- When issue wording conflicts with established domain terminology, use `CONTEXT.md` as the vocabulary source and resolve the requirement conflict explicitly.
