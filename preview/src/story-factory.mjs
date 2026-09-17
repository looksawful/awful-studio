import catalog from '../generated/asset-catalog.json';
import { createModelViewer } from './model-viewer.mjs';

export function assetsForGroup(group) {
  return catalog.assets.filter((asset) => asset.group === group);
}

export function groupOptions(group) {
  return assetsForGroup(group).map((asset) => asset.id);
}

export function renderGroup(group, assetId) {
  const assets = assetsForGroup(group);
  if (!assets.length) throw new Error(`No preview assets in group: ${group}`);
  const asset = assets.find((entry) => entry.id === assetId) ?? assets[0];
  return createModelViewer(asset);
}

export { catalog };
