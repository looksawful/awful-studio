import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const [glbPath, out] = process.argv.slice(2);
assert(glbPath && out, 'usage: node ticket146-whole-device-audit.mjs exact.glb output-dir');

const readJson = (url) => JSON.parse(readFileSync(fileURLToPath(url), 'utf8'));
const bytes = readFileSync(glbPath);
const sha = createHash('sha256').update(bytes).digest('hex');
const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString().trim());
const manifest = readJson(new URL('../../assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json', import.meta.url));
const catalog = readJson(new URL('../generated/asset-catalog.json', import.meta.url));
const asset = catalog.assets.find(entry => entry.id === 'iphone-17-v30');

assert(asset, 'iPhone review asset missing from catalog');
assert.equal(asset.sha256, sha);
assert.equal(asset.previewGlb, manifest.artifacts.compat_glb.path);
assert.equal(asset.sourceRevision, manifest.source_revision);
assert.equal(asset.sourceCommit, manifest.source_commit);

const reviewMeshes = asset.reviewParts.flatMap(group => group.meshes).sort();
const glbMeshes = gltf.nodes.filter(node => Number.isInteger(node.mesh)).map(node => node.name).sort();
const triangles = gltf.meshes.reduce(
  (total, mesh) => total + mesh.primitives.reduce((sum, primitive) => sum + gltf.accessors[primitive.indices].count / 3, 0),
  0,
);
assert.equal(glbMeshes.length, 51);
assert.deepEqual(glbMeshes, reviewMeshes);
assert.equal(triangles, asset.triangleCount);

const cameras = [
  ['front', [0, 0, 1], [0, 0], 0.29, 'all'],
  ['front-three-quarter', [0.45, 0.10, 1], [0, 0], 0.29, 'all'],
  ['left-side', [1, 0, 0], [0, 0], 0.20, 'all'],
  ['right-side', [-1, 0, 0], [0, 0], 0.20, 'all'],
  ['bottom', [0, -1, 0], [0, -0.42], 0.16, 'all'],
  ['back', [0, 0, -1], [0, 0], 0.29, 'all'],
  ['rear-three-quarter', [-0.4, 0.1, -1], [0, 0], 0.29, 'all'],
  ['camera-system', [0, 0, -1], [0.317, 0.35], 0.095, 'all'],
  ['rear-mic', [0, 0, -1], [0.218, 0.35], 0.019, 'all'],
  ['housing-wire', [0, 0, -1], [0.317, 0.35], 0.095, 'mesh:CAMERA_HOUSING'],
];

mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('http://127.0.0.1:6006/iframe.html?id=models-devices--i-phone-17&viewMode=story', { waitUntil: 'networkidle' });

  const viewer = page.locator('awful-model-viewer');
  await page.waitForFunction(expected => {
    const element = document.querySelector('awful-model-viewer');
    return element?.dataset.snapshotVerified === expected
      && element.dataset.modelLoaded === 'iphone-17-v30'
      && !element.dataset.modelError;
  }, sha, { timeout: 30000 });

  const provenance = await viewer.evaluate(element => {
    const root = element._model.getObjectByName('CTRL_IPHONE_17');
    return [root.userData.delivery_source_revision, root.userData.delivery_source_commit];
  });
  assert.deepEqual(provenance, [manifest.source_revision, manifest.source_commit]);

  const part = viewer.locator('select[data-control="part"]');
  const mode = viewer.locator('select[data-control="mode"]');
  await viewer.locator('select[data-control="screen-state"]').selectOption('screen_on');
  await viewer.locator('select[data-control="colorway"]').selectOption('white');

  for (const [name, direction, fraction, distance, selection] of cameras) {
    await part.selectOption(selection);
    await viewer.evaluate((element, camera) => {
      const body = element._model.getObjectByName('BODY_ALUMINUM');
      const Vector = element._camera.position.constructor;
      const lo = new Vector(Infinity, Infinity, Infinity);
      const hi = new Vector(-Infinity, -Infinity, -Infinity);
      body.updateMatrixWorld(true);
      body.traverse(object => {
        if (!object.isMesh) return;
        const positions = object.geometry.attributes.position;
        for (let index = 0; index < positions.count; index++) {
          const point = new Vector().fromBufferAttribute(positions, index).applyMatrix4(object.matrixWorld);
          lo.min(point);
          hi.max(point);
        }
      });
      const center = lo.clone().add(hi).multiplyScalar(0.5);
      const size = hi.clone().sub(lo);
      center.x += size.x * camera.fraction[0];
      center.y += size.y * camera.fraction[1];
      element._controls.target.copy(center);
      element._camera.position.copy(center).add(new Vector(...camera.direction).normalize().multiplyScalar(camera.distance));
      element._camera.lookAt(center);
      element._controls.update();
    }, { direction, fraction, distance });

    for (const reviewMode of ['texture', 'clay', 'wireframe']) {
      await mode.selectOption(reviewMode);
      await page.waitForTimeout(120);
      await viewer.locator('canvas').screenshot({ path: `${out}/${name}-${reviewMode}-white-screen_on.png` });
    }
  }

  assert.deepEqual(errors, []);
  const result = {
    sha,
    sourceRevision: manifest.source_revision,
    sourceCommit: manifest.source_commit,
    meshNodes: glbMeshes.length,
    nodeCount: gltf.nodes.length,
    triangles,
    views: cameras.map(([name]) => name),
    errors,
  };
  writeFileSync(`${out}/audit.json`, JSON.stringify(result, null, 2));
  console.log('TICKET146_WHOLE_DEVICE_GREEN', JSON.stringify(result));
} finally {
  await browser.close();
}
