import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const previewRoot = fileURLToPath(new URL('..', import.meta.url));
const repoRoot = path.resolve(previewRoot, '..');
const generator = path.join(previewRoot, 'tools', 'generate-catalog.mjs');
const catalogPath = path.join(previewRoot, 'generated', 'asset-catalog.json');

const runGenerator = (...args) => spawnSync(process.execPath, [generator, ...args], {
  cwd: repoRoot,
  encoding: 'utf8',
});

test('catalog generator produces only canonical model inventory', () => {
  const result = runGenerator();
  assert.equal(result.status, 0, result.stderr || result.stdout || 'catalog generation failed');
  assert.equal(existsSync(catalogPath), true);

  const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
  const ids = catalog.assets.map((asset) => asset.id);
  assert.equal(new Set(ids).size, ids.length, 'asset ids must be unique');

  const devices = catalog.assets.filter((asset) => asset.group === 'Devices');
  assert.deepEqual(devices.map(({ id, version }) => [id, version]), [
    ['iphone-17-v30', 'v30'],
    ['ipad-pro-11-m5-v6', 'v6'],
    ['ipad-pro-13-m5-v6', 'v6'],
    ['macbook-pro-14-m5-v1', 'v1'],
  ]);
  assert.deepEqual(devices.map(({ stage }) => stage), [
    'LOW_DRAFT',
    'LOW_DRAFT',
    'LOW_DRAFT',
    'RELEASE_CANDIDATE',
  ]);

  const studio = catalog.assets.filter((asset) => asset.group === 'Studio Equipment');
  assert.equal(studio.length, 4);
  assert.equal(studio.every((asset) => asset.lods?.length === 3), true);
  assert.equal(studio.every((asset) => typeof asset.collision === 'string'), true);

  const scenes = catalog.assets.filter((asset) => asset.group === 'Scenes');
  assert.deepEqual(scenes.map(({ id, version }) => [id, version]), [
    ['white-studio-v2', 'v2'],
    ['dark-neon-v2', 'v2'],
    ['loft-daylight-v2', 'v2'],
  ]);

  for (const asset of catalog.assets.filter((entry) => entry.group !== 'Scenes')) {
    assert.equal(existsSync(path.join(repoRoot, asset.previewGlb)), true, asset.previewGlb);
  }
});

test('catalog check mode rejects no committed drift', () => {
  const generated = runGenerator();
  assert.equal(generated.status, 0, generated.stderr || generated.stdout);
  const checked = runGenerator('--check');
  assert.equal(checked.status, 0, checked.stderr || checked.stdout || 'catalog check failed');
});
