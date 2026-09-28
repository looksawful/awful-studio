import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  availableLods,
  cameraDirection,
  resolveAssetUrl,
  previewMaterialPolicy,
  validateModelProvenance,
} from '../src/viewer-core.mjs';

test('preview URLs expose repository assets without copying binaries', () => {
  assert.equal(
    resolveAssetUrl('assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb'),
    '/assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb',
  );
  assert.equal(
    resolveAssetUrl('preview/generated/scenes/white-studio-v2.glb'),
    '/preview-scenes/white-studio-v2.glb',
  );
});

test('preview URLs support GitHub Pages subpaths', () => {
  assert.equal(
    resolveAssetUrl('assets/model.glb', '/awful-studio/'),
    '/awful-studio/assets/model.glb',
  );
  assert.equal(
    resolveAssetUrl('preview/generated/scenes/white-studio-v2.glb', '/awful-studio/'),
    '/awful-studio/preview-scenes/white-studio-v2.glb',
  );
});

test('LOD options preserve manifest order and fall back to preview model', () => {
  const asset = { previewGlb: 'assets/model.glb', lods: [
    { name: 'LOD0', path: 'assets/lod0.glb' },
    { name: 'LOD1', path: 'assets/lod1.glb' },
  ] };
  assert.deepEqual(availableLods(asset), asset.lods);
  assert.deepEqual(availableLods({ previewGlb: 'assets/model.glb', lods: [] }), [
    { name: 'Default', path: 'assets/model.glb' },
  ]);
});
test('device model provenance rejects stale stage or source revision', () => {
  const asset = { version: 'v30', stage: 'LOW_DRAFT', sourceRevision: 'abc', sourceCommit: 'def' };
  const root = { userData: {
    delivery_version: 'v30',
    delivery_stage: 'LOW_DRAFT',
    delivery_source_revision: 'abc',
    delivery_source_commit: 'def',
  } };
  assert.deepEqual(validateModelProvenance(asset, root), []);
  assert.deepEqual(
    validateModelProvenance({ ...asset, stage: 'RELEASE_CANDIDATE' }, root),
    ['GLB provenance mismatch: delivery_stage'],
  );
  assert.deepEqual(
    validateModelProvenance({ ...asset, sourceRevision: 'stale' }, root),
    ['GLB provenance mismatch: delivery_source_revision'],
  );
});

test('camera presets are explicit and normalized', () => {
  assert.deepEqual(cameraDirection('front'), [0, 0, 1]);
  assert.deepEqual(cameraDirection('side'), [1, 0, 0]);
  assert.deepEqual(cameraDirection('top'), [0, 1, 0]);
  assert.throws(() => cameraDirection('diagonal'), /Unknown camera preset/);
});

test('binary Apple decal uses crisp preview alpha policy', () => {
  assert.deepEqual(previewMaterialPolicy('MAT_APPLE_LOGO_DECAL'), {
    alphaTest: 0.5, transparent: false, depthWrite: true, frontSide: true,
  });
  assert.deepEqual(previewMaterialPolicy('MAT_SCREEN_CONTENT', { hasTexture: true }), { emissiveIntensity: 2, envMapIntensity: 0, minRoughness: 0.12, maxClearcoat: 0 });
  assert.deepEqual(previewMaterialPolicy('MAT_SCREEN_CONTENT'), { emissiveIntensity: 0, envMapIntensity: 0, minRoughness: 0.45, maxClearcoat: 0 });
  assert.deepEqual(previewMaterialPolicy('MAT_DISPLAY_GLASS'), { transmission: 0, transparent: true, opacity: 0.07, depthWrite: false, envMapIntensity: 0.04, minRoughness: 0.3, maxClearcoat: 0.03 });
  assert.deepEqual(previewMaterialPolicy('MAT_ANODIZED_ALUMINUM'), { frontSide: true, envMapIntensity: 0.55, minRoughness: 0.28 });
  assert.deepEqual(previewMaterialPolicy('MAT_IPAD_ALUMINUM'), { frontSide: true, envMapIntensity: 0.55, minRoughness: 0.3 });
  assert.deepEqual(previewMaterialPolicy('MAT_SPACE_BLACK_ALUMINUM'), { frontSide: true, envMapIntensity: 0.5, minRoughness: 0.28 });
  assert.deepEqual(previewMaterialPolicy('MAT_BACK_GLASS'), { frontSide: true, envMapIntensity: 0.32, minRoughness: 0.38 });
  assert.deepEqual(previewMaterialPolicy('MAT_OPTICS_BLACK'), { frontSide: true });
});
