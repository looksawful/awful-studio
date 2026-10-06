import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { test } from 'node:test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const previewRoot = fileURLToPath(new URL('..', import.meta.url));
const viewerPath = path.join(previewRoot, 'src', 'model-viewer.mjs');
const storiesDir = path.join(previewRoot, 'stories');

test('viewer uses Three GLTF runtime and orbit controls', () => {
  assert.equal(existsSync(viewerPath), true);
  const source = readFileSync(viewerPath, 'utf8');
  assert.match(source, /GLTFLoader/); assert.match(source, /OrbitControls/); assert.match(source, /RoomEnvironment/);
  assert.match(source, /MeshoptDecoder/); assert.match(source, /requestFullscreen/); assert.match(source, /availableLods/);
  assert.match(source, /NeutralToneMapping/);
  // Exposure and light values are verified on the real renderer by browser smoke.
  assert.doesNotMatch(source, /HemisphereLight/);
  assert.match(source, /data-control="screen-state"/); assert.match(source, /data-control="colorway"/); assert.match(source, /data-control="animation-clip"/);
  assert.match(source, /applyIphoneColorway/); assert.match(source, /#applyScreenState/); assert.match(source, /new THREE\.RectAreaLight/);
});

test('wireframe review uses hidden-line depth occlusion instead of x-ray triangles', () => {
  const source = readFileSync(viewerPath, 'utf8');
  assert.match(source, /previewWireframeOverlay/);
  assert.match(source, /colorWrite:\s*false/);
  assert.match(source, /depthWrite:\s*false/);
  assert.match(source, /side:\s*THREE\.FrontSide/);
  assert.doesNotMatch(source, /wireframe:\s*true,\s*side:\s*source\.side/);
});

test('storybook exposes every canonical model as a first-class story', () => {
  const expected = {
    'devices.stories.mjs': ['IPhone17', 'IPadPro11', 'IPadPro13', 'MacBookPro14'],
    'studio-equipment.stories.mjs': ['CStand', 'ProfotoD1', 'ProfotoMagnum', 'StudioSandbag'],
    'scenes.stories.mjs': ['WhiteStudio', 'DarkNeon', 'LoftDaylight'],
  };
  for (const [name, exports] of Object.entries(expected)) {
    const source = readFileSync(path.join(storiesDir, name), 'utf8');
    for (const story of exports) assert.match(source, new RegExp(`export const ${story}\\b`), `${name}: ${story}`);
  }
});
