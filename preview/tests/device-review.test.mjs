import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { test } from 'node:test';
import { validateModelProvenance } from '../src/viewer-core.mjs';

const catalog = JSON.parse(readFileSync(new URL('../generated/asset-catalog.json', import.meta.url)));

test('the shared catalog identifies and verifies exactly the device snapshots shown by primary stories', () => {
  const devices = catalog.assets.filter(asset => asset.group === 'Devices');
  assert.equal(devices.length, 4);
  for (const asset of devices) {
    assert.match(asset.sha256 ?? '', /^[a-f0-9]{64}$/, `${asset.id}: review identity missing`);
    const relative = asset.previewGlb.replace(/^assets\/(iphone-review|device-review)\//, 'preview/generated/$1/');
    const bytes = readFileSync(new URL(`../../${relative}`, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, asset.id);
    const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
    let triangles = 0;
    for (const mesh of gltf.meshes) for (const primitive of mesh.primitives) {
      assert.equal(primitive.mode ?? 4, 4, `${asset.id}: unexpected primitive mode`);
      triangles += gltf.accessors[primitive.indices ?? primitive.attributes.POSITION].count / 3;
    }
    assert.equal(triangles, asset.triangleCount, `${asset.id}: stale triangle count`);
    assert.equal(gltf.materials.length, asset.materialCount, `${asset.id}: stale material count`);
    const root = gltf.nodes.find(node => node.name === asset.root);
    assert.deepEqual(validateModelProvenance(asset, { userData: root?.extras }), [], asset.id);
    assert.equal(asset.reviewOnly, true);
    assert.equal(asset.topologyAccepted, false);
  }
});
