import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const previewRoot = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const repoRoot = path.resolve(previewRoot, '..');
const output = path.join(previewRoot, 'generated', 'asset-catalog.json');

const reviewDevices = [
  'preview/generated/iphone-review/frozen-current-2026-10-05/asset.json',
  'preview/generated/device-review/current-2026-10-05/ipad_pro_11_m5_v6/asset.json',
  'preview/generated/device-review/current-2026-10-05/ipad_pro_13_m5_v6/asset.json',
  'preview/generated/device-review/current-2026-10-05/macbook_pro_14_m5_v1/asset.json',
];

const sceneConfigs = [
  ['white-studio-v2', 'White Studio', 'scene_lab/white_studio/scene.json', 'scene_lab/white_studio/generated/white_studio_v2.blend'],
  ['dark-neon-v2', 'Dark Neon', 'scene_lab/dark_neon/scene.json', 'scene_lab/dark_neon/generated/dark_neon_v2.blend'],
  ['loft-daylight-v2', 'Loft Daylight', 'scene_lab/loft_daylight/scene.json', 'scene_lab/loft_daylight/generated/loft_daylight_v2.blend'],
];

const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(repoRoot, relative), 'utf8'));
const studioLabels = {
  studio_support_cstand_01: 'C-Stand',
  profoto_d1_500_air: 'Profoto D1 500 Air',
  profoto_magnum_100624: 'Profoto Magnum 100624',
  studio_sandbag_01: 'Studio Sandbag',
};

function studioEntries() {
  const manifestPath = 'assets/studio_equipment/studio_rig_v01/runtime/asset_manifest.json';
  const data = readJson(manifestPath);
  const runtimeDir = path.posix.dirname(manifestPath);
  return Object.entries(data.assets).map(([id, asset]) => ({
    id: id.replaceAll('_', '-'),
    label: studioLabels[id] ?? id,
    group: 'Studio Equipment',
    version: 'v01',
    sourceBlend: 'assets/studio_equipment/studio_rig_v01/generated/studio_rig_v01.blend',
    previewGlb: path.posix.join(runtimeDir, asset.glb),
    lods: Object.entries(asset.lod_glb ?? {}).map(([name, relative]) => ({ name, path: path.posix.join(runtimeDir, relative) })),
    collision: asset.collision_glb ? path.posix.join(runtimeDir, asset.collision_glb) : null,
    sourceRevision: null,
    sourceCommit: null,
    interaction: asset.interaction ?? null,
  }));
}

function sceneEntry([id, label, metadataPath, sourceBlend]) {
  const metadata = readJson(metadataPath);
  return {
    id,
    label,
    group: 'Scenes',
    version: 'v2',
    sourceBlend,
    previewGlb: `preview/generated/scenes/${id}.glb`,
    lods: [],
    collision: null,
    sourceRevision: null,
    sourceCommit: null,
    sceneMetadata: metadata,
  };
}
const assets = [
  ...reviewDevices.map(readJson),
  ...studioEntries(),
  ...sceneConfigs.map(sceneEntry),
];

const ids = new Set();
for (const asset of assets) {
  if (ids.has(asset.id)) throw new Error(`Duplicate asset id: ${asset.id}`);
  ids.add(asset.id);
  if (!asset.previewGlb || !asset.sourceBlend) throw new Error(`Incomplete asset entry: ${asset.id}`);
}

const catalog = {
  schemaVersion: 1,
  generatedFrom: 'pinned device review snapshots; canonical studio and scene manifests',
  assets,
};
const serialized = `${JSON.stringify(catalog, null, 2)}\n`;

if (process.argv.includes('--check')) {
  if (!fs.existsSync(output)) throw new Error(`Catalog missing: ${output}`);
  const current = fs.readFileSync(output, 'utf8').replaceAll('\r\n', '\n');
  if (current !== serialized) {
    console.error('preview/generated/asset-catalog.json is stale; run npm run catalog from preview/.');
    process.exit(1);
  }
} else {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, serialized, 'utf8');
  console.log(`Wrote ${path.relative(repoRoot, output)} with ${assets.length} assets`);
}
