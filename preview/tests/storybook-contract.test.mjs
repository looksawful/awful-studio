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
  assert.match(source, /NeutralToneMapping/); assert.match(source, /toneMappingExposure = 0\.7/);
  assert.doesNotMatch(source, /HemisphereLight/); assert.match(source, /new THREE\.DirectionalLight\(0xffffff, 0\.65\)/);
  assert.match(source, /data-control="screen-state"/); assert.match(source, /data-control="animation-clip"/);
  assert.match(source, /#applyScreenState/); assert.match(source, /new THREE\.RectAreaLight/);
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
