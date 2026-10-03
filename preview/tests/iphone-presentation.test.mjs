import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { applyIphoneColorway, composeIphoneScreenTexture, prepareIphonePresentation, displayMetrics, iphoneColorways, iphoneScreenStates } from '../src/iphone-presentation.mjs';

test('official iPhone 17 colorways are exposed as material variants', () => {
  assert.deepEqual(
    Object.values(iphoneColorways).map(item => item.label),
    ['Black', 'White', 'Mist Blue', 'Sage', 'Lavender'],
  );
});

test('colorway changes tint without replacing PBR maps', () => {
  const model = new THREE.Group();
  const materials = {};
  for (const name of ['MAT_ANODIZED_ALUMINUM', 'MAT_ALUMINUM_EDGE', 'MAT_CAMERA_HOUSING', 'MAT_BACK_GLASS']) {
    const material = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: .3, metalness: name === 'MAT_BACK_GLASS' ? 0 : 1 });
    material.name = name;
    material.normalMap = new THREE.Texture();
    material.roughnessMap = new THREE.Texture();
    materials[name] = material;
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), material);
    model.add(mesh);
  }
  const maps = Object.fromEntries(Object.entries(materials).map(([name, material]) => [name, [material.normalMap, material.roughnessMap]]));

  applyIphoneColorway(model, 'mist_blue');

  assert.equal(materials.MAT_ANODIZED_ALUMINUM.color.getHexString(), iphoneColorways.mist_blue.aluminum.slice(1).toLowerCase());
  assert.equal(materials.MAT_BACK_GLASS.color.getHexString(), iphoneColorways.mist_blue.backGlass.slice(1).toLowerCase());
  for (const [name, material] of Object.entries(materials)) {
    assert.equal(material.normalMap, maps[name][0], name);
    assert.equal(material.roughnessMap, maps[name][1], name);
  }
});

test('active screen states keep the baseline Dynamic Island independent of raster artwork', () => {
  for (const state of ['screen_on', 'screen_lock', 'screen_website', 'screen_resume']) {
    assert.equal(iphoneScreenStates[state].dynamic_island_state, 'idle', state);
  }
  assert.equal(iphoneScreenStates.screen_off.dynamic_island_state, 'off');
});

test('website raster gets the baseline idle Dynamic Island in the compositor', () => {
  const calls = [];
  const context = {
    drawImage: (...args) => calls.push(['drawImage', ...args]),
    beginPath: () => calls.push(['beginPath']),
    roundRect: (...args) => calls.push(['roundRect', ...args]),
    fill: () => calls.push(['fill']),
    set fillStyle(value) { calls.push(['fillStyle', value]); },
  };
  const canvas = { width: 0, height: 0, getContext: () => context };
  const source = new THREE.Texture({ width: 1206, height: 2622 });
  source.flipY = false;
  source.colorSpace = THREE.SRGBColorSpace;
  source.anisotropy = 8;

  const composed = composeIphoneScreenTexture(source, iphoneScreenStates.screen_website, {
    createCanvas: () => canvas,
  });

  assert.notEqual(composed, source);
  assert.equal(canvas.width, 1206);
  assert.equal(canvas.height, 2622);
  assert.deepEqual(calls.find(call => call[0] === 'roundRect'), ['roundRect', 405, 37, 394, 121, 60.5]);
  assert.deepEqual(calls.find(call => call[0] === 'fillStyle'), ['fillStyle', '#000000']);
  assert.equal(composed.flipY, false);
  assert.equal(composed.colorSpace, THREE.SRGBColorSpace);
  assert.equal(composed.anisotropy, 8);
  composed.dispose();
});

test('display raster and mobile viewport preserve physical aspect and pixel pitch', () => {
  const metrics = displayMetrics();
  assert.deepEqual(metrics.viewport, [402, 874]);
  assert.ok(Math.abs(metrics.widthMm - 66.59) < 0.01);
  assert.ok(Math.abs(metrics.heightMm - 144.78) < 0.01);
});
test('only front display triangles emit; sides stay dark without modifying vertices', () => {
  const model = new THREE.Group();
  const screen = new THREE.Mesh(new THREE.BoxGeometry(.06657,.14479,.000325), new THREE.MeshStandardMaterial({map:new THREE.Texture()}));
  screen.name = 'SCREEN_CONTENT';model.add(screen);
  const original = Array.from(screen.geometry.attributes.position.array);
  const presentation = prepareIphonePresentation(model);
  assert.ok(Array.isArray(screen.material));
  assert.deepEqual(Array.from(screen.geometry.attributes.position.array),original);
  assert.ok(screen.geometry.groups.some(g=>g.materialIndex===1));
  assert.equal(screen.material[1].emissiveIntensity,0);
  assert.ok(Math.abs(presentation.glow.width-.06657)<1e-8);
  assert.ok(Math.abs(presentation.glow.height-.14479)<1e-8);
  assert.equal(presentation.glow.rotation.y,Math.PI);
  presentation.dispose();
});
test('front camera keeps its authored hardware datum', () => {
  const model = new THREE.Group(), camera = new THREE.Object3D(), body = new THREE.Object3D();
  camera.name = 'FRONT_CAMERA_GLASS'; camera.position.y = .067015;
  body.name = 'BODY_ALUMINUM'; model.add(camera, body);
  prepareIphonePresentation(model);
  assert.equal(camera.position.y, .067015);
  assert.equal(body.position.y, 0);
});

test('canonical multi-material display keeps emission, state controls and source edge ownership', () => {
  const model = new THREE.Group();
  const front = new THREE.MeshStandardMaterial({ emissiveMap: new THREE.Texture() });
  front.name = 'MAT_SCREEN_CONTENT';
  const edge = new THREE.MeshStandardMaterial({ color: 0x020203 });
  edge.name = 'MAT_SCREEN_EDGE';
  const screen = new THREE.Mesh(new THREE.BoxGeometry(.06657,.14479,.000325), [front,edge]);
  screen.name = 'SCREEN_CONTENT'; model.add(screen);
  let edgeDisposed = false;
  edge.addEventListener('dispose', () => { edgeDisposed = true; });
  const presentation = prepareIphonePresentation(model);
  assert.ok(presentation.glow);
  assert.equal(screen.material[0], front);
  assert.equal(screen.material[1], edge);
  assert.equal(front.emissiveIntensity, 1);
  presentation.dispose();
  assert.equal(edgeDisposed, false, 'source materials belong to model teardown');
});

test('GLTFLoader split primitives retain a working display and glow', () => {
  const model = new THREE.Group(), node = new THREE.Group();
  node.name = 'SCREEN_CONTENT'; model.add(node);
  const front = new THREE.MeshStandardMaterial({ emissiveMap: new THREE.Texture() });
  front.name = 'MAT_SCREEN_CONTENT';
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(.06657,.14479), front);
  node.add(mesh);
  const presentation = prepareIphonePresentation(model);
  assert.ok(presentation.glow, 'GLTFLoader emits a Group for multiple material primitives');
  assert.equal(mesh.material[0].map, front.emissiveMap);
  presentation.dispose();
});
