import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

export function displayMetrics() {
  return { raster: [1206, 2622], viewport: [402, 874], widthMm: 1206 / 460 * 25.4, heightMm: 2622 / 460 * 25.4 };
}

export const iphoneScreenStates = {
  screen_on: { label: 'Home screen', emission_strength: 1 },
  screen_off: { label: 'Off', emission_strength: 0, glow_intensity: 0 },
  screen_lock: { label: 'Lock screen', texture: 'screens/iphone-lock.png', emission_strength: 1 },
  screen_website: { label: 'looksawful.ru', texture: 'screens/iphone-website.png', emission_strength: 1 },
  screen_resume: { label: 'Resume', texture: 'screens/iphone-resume.png', emission_strength: 1 },
};

// Presentation corrections are explicit web overrides; source delivery stays intact.
export function prepareIphonePresentation(model) {
  const ownedMaterials = [];
  const pill = model.getObjectByName('DYNAMIC_ISLAND');
  if (pill) {
    const camera = model.getObjectByName('FRONT_CAMERA_GLASS');
    const delta = camera ? pill.position.y - camera.position.y : 0;
    model.traverse(object => {
      if (/^FRONT_CAMERA_|^FRONT_SENSOR_PILL$/.test(object.name)) object.position.y += delta;
    });
  }
  const screen = model.getObjectByName('SCREEN_CONTENT');
  let glow = null;
  if (screen?.isMesh && !Array.isArray(screen.material)) {
    const front = screen.material;
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
    const edge = new THREE.MeshStandardMaterial({ color: 0x020203, roughness: .36, metalness: 0, emissiveIntensity: 0 });
    ownedMaterials.push(edge);
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
      if (material.name === 'MAT_DYNAMIC_ISLAND' || material.name === 'MAT_FRONT_SENSOR_PILL') {
        material.roughness = .6;material.envMapIntensity = .1;
        if ('clearcoat' in material) material.clearcoat = 0;
      }
      if (/^BOTTOM_.*APERTURE|^USB_C_CAVITY$/.test(object.name)) {
        const interior = material.clone();ownedMaterials.push(interior);
        interior.roughness = .82;interior.metalness = 0;interior.envMapIntensity = .15;
        object.material = interior;
      }
      if (material.name === 'MAT_FASTENER') { material.roughness = .5;material.envMapIntensity = .35; }
    }
  });
  return { glow, dispose() { glow?.removeFromParent();ownedMaterials.forEach(material => material.dispose()); } };
}
