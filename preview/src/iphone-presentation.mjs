import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

export function displayMetrics() {
  return { raster: [1206, 2622], viewport: [402, 874], widthMm: 1206 / 460 * 25.4, heightMm: 2622 / 460 * 25.4 };
}

export const iphoneScreenStates = {
  screen_on: { label: 'Home screen', emission_strength: 1, dynamic_island_state: 'idle' },
  screen_off: { label: 'Off', emission_strength: 0, glow_intensity: 0, dynamic_island_state: 'off' },
  screen_lock: { label: 'Lock screen', texture: 'screens/iphone-lock.png', emission_strength: 1, dynamic_island_state: 'idle' },
  screen_website: { label: 'looksawful.ru', texture: 'screens/iphone-website.png', emission_strength: 1, dynamic_island_state: 'idle' },
  screen_resume: { label: 'Resume', texture: 'screens/iphone-resume.png', emission_strength: 1, dynamic_island_state: 'idle' },
};

// Derived from the accepted clean/dynamic 1206x2622 reference pair. Apple does not publish idle-mask pixels.
const idleDynamicIslandRaster = Object.freeze({ x: 405, y: 37, width: 394, height: 121, radius: 60.5 });

export function composeIphoneScreenTexture(source, stateSpec, {
  createCanvas = () => document.createElement('canvas'),
} = {}) {
  if (!source?.image || stateSpec?.dynamic_island_state !== 'idle') return source;
  const [width, height] = displayMetrics().raster;
  const canvas = createCanvas();
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('iPhone screen compositor requires a 2D canvas context');
  context.drawImage(source.image, 0, 0, width, height);
  context.fillStyle = '#000000';
  context.beginPath();
  context.roundRect(
    idleDynamicIslandRaster.x,
    idleDynamicIslandRaster.y,
    idleDynamicIslandRaster.width,
    idleDynamicIslandRaster.height,
    idleDynamicIslandRaster.radius,
  );
  context.fill();
  const texture = new THREE.CanvasTexture(canvas);
  texture.name = 'AWFUL_IPHONE_SCREEN_COMPOSITE';
  texture.flipY = source.flipY;
  texture.colorSpace = source.colorSpace || THREE.SRGBColorSpace;
  texture.anisotropy = source.anisotropy;
  texture.wrapS = source.wrapS;
  texture.wrapT = source.wrapT;
  texture.magFilter = source.magFilter;
  texture.minFilter = source.minFilter;
  texture.generateMipmaps = source.generateMipmaps;
  return texture;
}

// Presentation corrections are explicit web overrides; source delivery stays intact.
export function prepareIphonePresentation(model) {
  const ownedMaterials = [];
  const screenNode = model.getObjectByName('SCREEN_CONTENT');
  const screen = screenNode?.isMesh ? screenNode : screenNode?.children.find(child => child.isMesh && (Array.isArray(child.material) ? child.material : [child.material]).some(material => material.name === 'MAT_SCREEN_CONTENT'));
  let glow = null;
  if (screen?.isMesh) {
    const front = Array.isArray(screen.material) ? screen.material.find(material => material.name === 'MAT_SCREEN_CONTENT') : screen.material;
    if (!front) throw new Error('iPhone display has no content material');
    front.map ??= front.emissiveMap;
    front.toneMapped = false;
    front.color.set(0x000000);
    front.roughness = 1;
    front.envMapIntensity = 0;
    if ('clearcoat' in front) front.clearcoat = 0;
    if ('specularIntensity' in front) front.specularIntensity = 0;
    front.emissive.set(0xffffff);
    front.emissiveMap = front.map;
    front.emissiveIntensity = 1;
    // OLED edge/back are opaque, unlit black; planar screen UVs only belong on the front.
    const sourceEdge = Array.isArray(screen.material) ? screen.material.find(material => material.name === 'MAT_SCREEN_EDGE') : null;
    const edge = sourceEdge ?? new THREE.MeshStandardMaterial({ color: 0x020203, roughness: .36, metalness: 0, emissiveIntensity: 0 });
    if (!sourceEdge) ownedMaterials.push(edge);
    const geometry = screen.geometry;
    const normal = geometry.getAttribute('normal');
    const index = geometry.index;
    const count = index?.count ?? normal.count;
    geometry.clearGroups();
    let start = 0, previous = -1;
    for (let i = 0; i < count; i += 3) {
      const ids = [0,1,2].map(j => index ? index.getX(i+j) : i+j);
      const side = ids.every(id => normal.getZ(id) > .995) ? 0 : 1;
      if (side !== previous) {
        if (i > start) geometry.addGroup(start,i-start,previous);
        start = i;previous = side;
      }
    }
    if (count > start) geometry.addGroup(start,count-start,previous);
    screen.material = [front,edge];
    geometry.computeBoundingBox();
    const size = geometry.boundingBox.getSize(new THREE.Vector3());
    RectAreaLightUniformsLib.init();
    glow = new THREE.RectAreaLight(0xd9eaff, 8, size.x, size.y);
    glow.name = 'AWFUL_SCREEN_GLOW';
    glow.position.z = geometry.boundingBox.max.z + .00002;
    // RectAreaLight emits toward local -Z; turn its face toward the display's +Z.
    glow.rotation.y = Math.PI;
    screen.add(glow);
  }
  model.traverse(object => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (/^BOTTOM_.*APERTURE|^USB_C_CAVITY$/.test(object.name)) {
        const interior = material.clone();ownedMaterials.push(interior);
        interior.roughness = .82;interior.metalness = 0;interior.envMapIntensity = .15;
        object.material = interior;
      }
      if (material.name === 'MAT_FASTENER') { material.roughness = .5;material.envMapIntensity = .35; }
      if (material.name === 'MAT_FRONT_OPTIC') {
        material.envMapIntensity = .1;
        if ('specularIntensity' in material) material.specularIntensity = .15;
      }
    }
  });
  return { glow, dispose() { glow?.removeFromParent();ownedMaterials.forEach(material => material.dispose()); } };
}
