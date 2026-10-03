# iPhone 17 v30 body normal bake — primary-source findings

Date: 2026-10-04
Scope: BODY_ALUMINUM_HIGH → BODY_ALUMINUM in Blender 5.2.1, with glTF export.

## Primary-source findings

1. **Selected-to-Active is the correct high→low bake mode.** Blender casts rays from the active low-poly object toward the selected source object(s). Blender documents two different controls for the ray start/search envelope: **Cage Extrusion** when using a cage, and **Max Ray Distance** when not using a cage.
   - https://docs.blender.org/manual/en/latest/render/cycles/baking.html
   - https://docs.blender.org/api/master/bpy.ops.object.html

2. **Do not treat Cage Extrusion and Max Ray Distance as additive controls.** Blender's manual explicitly describes Max Ray Distance as the non-cage control and Cage Extrusion as the cage control. If a manually authored cage is required, it must match the low mesh topology/face order.
   - https://docs.blender.org/manual/en/latest/render/cycles/baking.html

3. **Every material that should receive an image bake needs an active/selected Image Texture node targeting the destination image.** Blender states that if a material does not contain an active and selected Image Texture node, nothing is baked for that material.
   - https://docs.blender.org/manual/en/latest/render/cycles/baking.html

4. **Tangent-space normals require the same UV basis at bake and use time.** Blender's Normal Map documentation says tangent normal maps must use matching UV coordinates and Non-Color image data. Blender 5.2's exact UV tangent implementation is MikkTSpace, matching the tangent basis used by Blender shading/export.
   - https://docs.blender.org/manual/id/5.2/render/shader_nodes/displacement/normal_map.html
   - https://docs.blender.org/manual/pt/latest/modeling/geometry_nodes/mesh/uv/uv_tangent.html

5. **Hard/smooth normal boundaries matter.** Blender warns that hard splits can cause non-smooth normal results around edges during selected-to-active baking. For machine surfaces, smooth/flat/sharp boundaries must be intentional and consistent before the bake.
   - https://docs.blender.org/manual/en/latest/render/cycles/baking.html
   - https://docs.blender.org/manual/en/latest/modeling/meshes/editing/face/shading.html

6. **glTF only supports tangent-space normal maps.** Blender's glTF exporter expects an Image Texture in Non-Color → Normal Map (Tangent Space) → Principled BSDF Normal. The exporter can export mesh normals and tangents; the normal map should keep Blender's default tangent-space convention (+Y/OpenGL).
   - https://docs.blender.org/manual/th/5.2/addons/scene_gltf2.html
   - https://docs.blender.org/manual/sl/5.2/addons/scene_gltf2.html

7. **glTF tangent basis is an explicit runtime contract.** glTF defines NORMAL and TANGENT attributes; when tangents are absent, runtimes should derive them with MikkTSpace using the positions, normals and UV set associated with the normal texture. Degenerate geometry should be avoided.
   - https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

## Implication for this repo

The current low body is one mesh with two material slots:
- slot 0: anodized metal, intended to receive the macro body normal;
- slot 1: dark recessed tray/wall geometry, which should remain physically dark and **does not need the metal macro normal**.

The simplest reliable pipeline is therefore:

1. Keep the production low mesh unchanged.
2. Create a temporary bake-target duplicate of BODY_ALUMINUM.
3. On the temporary target, delete every face whose material index is not the metal slot.
4. Keep the exact UV layer and vertex positions of the metal faces.
5. Bake selected-to-active from BODY_ALUMINUM_HIGH to that metal-only target.
6. Start without a cage and use a deliberately small Max Ray Distance. Increase only until the outer high surface is captured; do not let rays cross the depth of button/aperture recesses.
7. Use a 32 px margin and 1024² normal map unless visual evidence proves that smaller is enough.
8. Keep the high source's procedural micro-normal disconnected during the macro geometry bake. Re-add the existing anodized micro-normal/roughness separately in the runtime material if still visually useful.
9. Connect the baked result as Non-Color → Normal Map (Tangent) → Principled Normal only on the metal material.
10. Export normals + tangents and verify the actual GLB with Khronos validator and runtime renders.

## What not to assume

- Do not assume a larger ray distance is safer. It expands the set of nearby/internal surfaces a ray can hit.
- Do not assume the dark tray material needs the body normal map just because it shares the same mesh.
- Do not assume a normal map can repair silhouette or missing contact geometry.
- Do not assume a successful bake is useful. Compare geometry-only vs baked output under identical lighting and keep the bake only if it materially improves the rail.
- Do not add a generic bake framework. One iPhone-local bake helper/script is enough unless a second device proves reuse.
