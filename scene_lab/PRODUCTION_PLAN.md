# Hero scene production plan

## Layer 1 — structural scene

Build shell, floor, pedestal, hero reserve, production camera, primary lights and only the set dressing needed to establish depth. This layer must remain procedural, metre-scaled and independent from the AWFUL STUDIO Extension.

## Layer 2 — surface quality

Replace placeholder-looking surfaces with authored procedural/PBR materials. Priorities: micro-roughness, believable edge wear restraint, scale-correct concrete/plaster, glass and metal reflection control, and clean color management.

## Layer 3 — authored props

Use Blender procedural geometry for architecture and simple fixtures. Use Tripo/to3D or similar image-to-3D only for approved decorative props where bespoke silhouette matters. Never use generated meshes for walls, floors, ceilings, Boolean openings, collision or camera-critical supports.

## Layer 4 — light shaping

Tune source size, distance, feathering, negative fill and reflection cards around a temporary neutral hero. Lock the camera before final dressing. Lighting acceptance is visual, not merely numeric.

## Layer 5 — scene dressing

Add props only when they improve depth, scale, story or reflection structure. Keep the hero reserve visually quiet. Reject clutter, tangencies and props that compete with the hero through brightness or central placement.

## Layer 6 — review evidence

For each scene produce: hero camera, wide BTS camera, overhead plan, left/right oblique and material/light diagnostic frames. A `.blend` build passing is structural evidence only; it is not visual approval.

## Scene order

1. White Studio — establishes clean commercial material/light quality.
2. Loft Daylight — establishes architectural detail, sunlight and lifestyle depth.
3. Dark Neon — establishes controlled colored reflections and dark-value separation.

## Git isolation

Scene branches never modify `extension/awful_studio/**`. Approved ideas may later be reimplemented in a dedicated integration branch rather than merged wholesale from scene branches.
