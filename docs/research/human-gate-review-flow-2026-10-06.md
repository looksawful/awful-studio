# Human Gate review flow — 2026-10-06

## Question

How the AWFUL STUDIO Human Gate is supposed to work for device mockups, and what the current iPhone #146 gate actually uses.

## Primary project sources

- `CONTEXT.md`: Human Gate = owner's explicit visual approval or rejection of an identified review candidate. Automated tests or agent visual review are not Human Gate.
- `docs/handoffs/iphone17-v30-topology-implementation.md`: the required review surface is the existing Storybook / Three.js viewer with orbit/zoom, materials, clay and actual exported GLB triangle wireframe. Static sheets do not replace it. No second viewer or parallel review pipeline.
- `preview/README.md`: one Storybook package, one Three.js viewer, one generated catalog. A candidate is identified by exact GLB checksum + source revision/commit, not by a version label alone.

## Network surface

Official Tailscale guidance confirms that Serve privately exposes a local service only to devices in the same tailnet, while Funnel exposes it publicly.

Primary docs:
- https://tailscale.com/docs/features/tailscale-serve
- https://tailscale.com/docs/reference/tailscale-cli/serve
- https://tailscale.com/docs/use-cases/application-testing/share-local-dev-server-with-team

Current Titan configuration:
- Titan is online in Tailscale as `titan.tail85619a.ts.net`.
- Tailscale Serve has `:8443 -> http://127.0.0.1:6006` configured for the Storybook review surface.
- Local Storybook/static preview on `127.0.0.1:6006` returns HTTP 200.
- The iPhone peer is currently offline in Tailscale, last seen 2026-10-03.
- A current HTTPS self-check to the `:8443` Tailscale endpoint from Titan failed, so mobile live review should not be claimed operational until connectivity is reverified end to end.

## Gate state machine

1. Engineering pins one exact candidate: source revision, GLB hashes, writer commit.
2. Automated gates run first: focused/full tests, Blender runtime, Khronos, Storybook/browser/consumer identity.
3. Independent Standards + Spec review must pass.
4. Issue moves to `ready-for-human`.
5. Owner inspects the exact candidate in the existing Storybook interactively:
   - rotate / zoom;
   - texture/material mode;
   - clay mode;
   - exported GLB triangle wireframe;
   - relevant finish variants;
   - relevant screen states;
   - whole-device plus diagnosed close-ups.
6. Owner returns one of:
   - PASS: exact candidate is visually accepted;
   - REJECT: name the exact visible defect and affected view/part.
7. PASS is recorded against the exact candidate identity. This does not automatically authorize merge/deploy unless the owning issue/PR says so.
8. REJECT reopens only the affected slice, then that slice's focused contract plus broad technical gates rerun before the next Human Gate.

## Ponytail / prototype conclusion

Do not build a separate Human Gate app. The existing Storybook is already the interactive prototype/review surface and the repo explicitly requires reusing it. Contact sheets are navigation/evidence only, never the actual Human Gate.

The minimal Human Gate UX is therefore:
`pinned candidate -> private Storybook link -> owner inspects -> PASS or precise REJECT -> record verdict`.
