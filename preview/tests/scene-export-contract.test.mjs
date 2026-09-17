import assert from 'node:assert/strict';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { test } from 'node:test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const previewRoot = fileURLToPath(new URL('..', import.meta.url));
const exporter = path.join(previewRoot, 'tools', 'export-scene-preview.py');

test('scene preview exporter is explicit and render-free', () => {
  assert.equal(existsSync(exporter), true);
  const source = readFileSync(exporter, 'utf8');
  assert.match(source, /bpy\.ops\.export_scene\.gltf/);
  assert.doesNotMatch(source, /bpy\.ops\.render/);
  assert.match(source, /export_cameras=False/);
  assert.match(source, /export_lights=False/);
});

test('all canonical scene previews are materialized', () => {
  for (const name of ['white-studio-v2', 'dark-neon-v2', 'loft-daylight-v2']) {
    const file = path.join(previewRoot, 'generated', 'scenes', `${name}.glb`);
    assert.equal(existsSync(file), true, name);
    assert.ok(statSync(file).size > 1024, `${name} preview is unexpectedly small`);
  }
});
