import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  availableLods,
  cameraDirection,
  resolveAssetUrl,
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
test('camera presets are explicit and normalized', () => {
  assert.deepEqual(cameraDirection('front'), [0, -1, 0]);
  assert.deepEqual(cameraDirection('side'), [1, 0, 0]);
  assert.deepEqual(cameraDirection('top'), [0, 0, 1]);
  assert.throws(() => cameraDirection('diagonal'), /Unknown camera preset/);
});
