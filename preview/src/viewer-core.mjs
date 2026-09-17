function normalizeBase(basePath = '/') {
  const trimmed = `/${String(basePath).replace(/^\/+|\/+$/g, '')}/`;
  return trimmed === '//' ? '/' : trimmed;
}

export function resolveAssetUrl(repoPath, basePath = '/') {
  const base = normalizeBase(basePath);
  if (repoPath.startsWith('assets/')) return `${base}${repoPath}`;
  const scenePrefix = 'preview/generated/scenes/';
  if (repoPath.startsWith(scenePrefix)) {
    return `${base}preview-scenes/${repoPath.slice(scenePrefix.length)}`;
  }
  throw new Error(`Unsupported preview asset path: ${repoPath}`);
}

export function availableLods(asset) {
  if (Array.isArray(asset.lods) && asset.lods.length > 0) return asset.lods;
  return [{ name: 'Default', path: asset.previewGlb }];
}

export function cameraDirection(preset) {
  const directions = {
    front: [0, -1, 0],
    side: [1, 0, 0],
    top: [0, 0, 1],
  };
  const direction = directions[preset];
  if (!direction) throw new Error(`Unknown camera preset: ${preset}`);
  return direction;
}
