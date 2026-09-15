# iPhone 17 runtime asset v15

This directory contains the web/runtime delivery generated from the validated Blender LOW asset.

## Files

- `iphone_17_v15_delivery.blend` — packed Blender delivery scene.
- `iphone_17_v15_web.glb` — compatibility GLB exported directly by Blender.
- `iphone_17_v15_web_meshopt.glb` — preferred web GLB compressed with Meshopt.
- `iphone_17_v15.asset.json` — runtime contract and variant manifest.

The compatibility GLB is the canonical interchange output. The Meshopt file is derived from it with pinned `@gltf-transform/cli@4.5.0`.

## Coordinate contract

Blender source space uses meters, `+Z` up and `-Y` forward. glTF runtime space uses meters and `+Y` up. Do not apply an additional manual axis conversion after `GLTFLoader` loads the asset.

The manifest records both source and runtime axis conventions. Runtime camera framing must use loaded world-space bounds rather than hard-coded body dimensions because the camera bump and controls extend beyond the nominal body depth.

## Stable anchors

- `ANCHOR_CENTER`
- `ANCHOR_BOTTOM_CENTER`
- `ANCHOR_SCREEN_CENTER`
- `ANCHOR_REAR_CAMERA`

These anchors are part of the runtime contract and must survive optimization.

## Three.js loading

Use `GLTFLoader` for both variants. The compatibility variant has no decoder dependency. The Meshopt variant requires `MeshoptDecoder`:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);
const gltf = await loader.loadAsync('iphone_17_v15_web_meshopt.glb');
const model = gltf.scene;
```

After loading, compute a `Box3` from the model and fit the camera to those world-space bounds. Preserve the root transform and use the named anchors for screen mounting, grounding and camera-related interactions.

## Rebuild

1. Run `generate_low_v15.py` in Blender 5.2.1 LTS.
2. Run `export_runtime_v15.py` against the generated `.blend`.
3. Run `optimize_runtime_v15.py` with Python and Node/npm available.
4. Validate both GLBs with the Khronos glTF validator.
5. Perform browser visual QA in Three.js for front, rear and three-quarter views.

Do not use Blender's current built-in Meshopt export for this asset. During v15 QA it preserved a formally valid file but visually damaged the very thin front sensor geometry in Three.js. The pinned glTF Transform post-process preserves that geometry.
