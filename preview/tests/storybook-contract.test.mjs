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
  assert.match(source, /GLTFLoader/);
  assert.match(source, /OrbitControls/);
  assert.match(source, /RoomEnvironment/);
  assert.match(source, /MeshoptDecoder/);
  assert.match(source, /requestFullscreen/);
  assert.match(source, /availableLods/);
  assert.match(source, /NeutralToneMapping/);
  assert.match(source, /toneMappingExposure = 0\.7/);
  assert.doesNotMatch(source, /HemisphereLight/);
  assert.match(source, /new THREE\.DirectionalLight\(0xffffff, 0\.65\)/);
  assert.match(source, /_viewLight\.position\.copy\(this\._camera\.position\)/);
  assert.match(source, /getMaxAnisotropy/);
  assert.match(source, /previewMaterialPolicy/);
  assert.match(source, /hasTexture: Boolean\(material\.map \|\| material\.emissiveMap\)/);
  assert.match(source, /material\.transmission = policy\.transmission/);
  assert.match(source, /material\.roughness = Math\.max/);
  assert.match(source, /material\.clearcoat = Math\.min/);
  assert.match(source, /environmentIntensity = 1\.0/);
  assert.match(source, /autoRotate = false/);
  assert.match(source, /data-control="screen-state"/);
  assert.match(source, /data-control="animation-clip"/);
  assert.match(source, /#applyScreenState/);
  assert.match(source, /new THREE\.RectAreaLight/);
});

test('storybook exposes catalog and three model groups', () => {
  for (const name of ['catalog', 'devices', 'studio-equipment', 'scenes']) {
    assert.equal(existsSync(path.join(storiesDir, `${name}.stories.mjs`)), true, name);
  }
});
