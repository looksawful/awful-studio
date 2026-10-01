import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { prepareIphonePresentation, displayMetrics } from '../src/iphone-presentation.mjs';

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
test('visible front camera follows the island while other device objects keep their datum', () => {
  const model = new THREE.Group(),pill=new THREE.Object3D(),camera=new THREE.Object3D(),body=new THREE.Object3D();
  pill.name='DYNAMIC_ISLAND';pill.position.y=.068665;
  camera.name='FRONT_CAMERA_GLASS';camera.position.y=.067015;
  body.name='BODY_ALUMINUM';model.add(pill,camera,body);
  prepareIphonePresentation(model);
  assert.equal(camera.position.y,pill.position.y);
  assert.equal(body.position.y,0);
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
