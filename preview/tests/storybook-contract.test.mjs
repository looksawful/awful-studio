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
});

test('storybook exposes catalog and three model groups', () => {
  for (const name of ['catalog', 'devices', 'studio-equipment', 'scenes']) {
    assert.equal(existsSync(path.join(storiesDir, `${name}.stories.mjs`)), true, name);
  }
});
