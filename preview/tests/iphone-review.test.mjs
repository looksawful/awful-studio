import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { verifySnapshotBytes } from '../src/viewer-core.mjs';

const asset = JSON.parse(readFileSync(new URL('../generated/iphone-review/frozen-current-2026-10-05/asset.json', import.meta.url), 'utf8'));
const bytes = readFileSync(new URL('../generated/iphone-review/frozen-current-2026-10-05/model.glb', import.meta.url));

test('frozen appearance accepts exact GLB bytes and rejects a changed snapshot', async () => {
  await verifySnapshotBytes(bytes, asset.sha256);
  const altered = new Uint8Array(bytes);
  altered[altered.length - 1] ^= 1;
  await assert.rejects(verifySnapshotBytes(altered, asset.sha256), /snapshot checksum mismatch/i);
});
