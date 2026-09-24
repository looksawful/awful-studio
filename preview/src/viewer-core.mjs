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

export function validateModelProvenance(asset, root) {
  if (!root?.userData) return ['GLB provenance root missing'];
  const expected = {
    delivery_version: asset.version,
    delivery_stage: asset.stage,
    delivery_source_revision: asset.sourceRevision,
    delivery_source_commit: asset.sourceCommit,
  };
  return Object.entries(expected)
    .filter(([, value]) => value != null)
    .filter(([key, value]) => root.userData[key] !== value)
    .map(([key]) => `GLB provenance mismatch: ${key}`);
}

export function cameraDirection(preset) {
  const directions = {
    front: [0, 0, 1],
    side: [1, 0, 0],
    top: [0, 1, 0],
  };
  const direction = directions[preset];
  if (!direction) throw new Error(`Unknown camera preset: ${preset}`);
  return direction;
}

export function previewMaterialPolicy(name, { hasTexture = false } = {}) {
  const surfacePolicies = {
    MAT_ANODIZED_ALUMINUM: { frontSide: true, envMapIntensity: 0.55, minRoughness: 0.28 },
    MAT_IPAD_ALUMINUM: { frontSide: true, envMapIntensity: 0.55, minRoughness: 0.3 },
    MAT_IPAD_EDGE: { frontSide: true, envMapIntensity: 0.5, minRoughness: 0.28 },
    MAT_SPACE_BLACK_ALUMINUM: { frontSide: true, envMapIntensity: 0.5, minRoughness: 0.28 },
    MAT_EDGE_ALUMINUM: { frontSide: true, envMapIntensity: 0.5, minRoughness: 0.28 },
    MAT_BACK_GLASS: { frontSide: true, envMapIntensity: 0.32, minRoughness: 0.38 },
    MAT_CAMERA_HOUSING: { frontSide: true, envMapIntensity: 0.45, minRoughness: 0.3 },
    MAT_TRACKPAD: { frontSide: true, envMapIntensity: 0.35, minRoughness: 0.3 },
  };
  if (surfacePolicies[name]) return surfacePolicies[name];
  if (name === 'MAT_APPLE_LOGO_DECAL') {
    return { alphaTest: 0.5, transparent: false, depthWrite: true, frontSide: true };
  }
  if (name === 'MAT_SCREEN_CONTENT') {
    return hasTexture
      ? { emissiveIntensity: 2, envMapIntensity: 0, minRoughness: 0.12, maxClearcoat: 0 }
      : { emissiveIntensity: 0, envMapIntensity: 0, minRoughness: 0.45, maxClearcoat: 0 };
  }
  if (name === 'MAT_DISPLAY_GLASS') {
    return { transmission: 0, transparent: true, opacity: 0.07, depthWrite: false, envMapIntensity: 0.04, minRoughness: 0.3, maxClearcoat: 0.03 };
  }
  return { frontSide: true };
}
