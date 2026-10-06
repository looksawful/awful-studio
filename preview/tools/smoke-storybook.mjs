import http from 'node:http';
import { existsSync, readFileSync, statSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const previewRoot = fileURLToPath(new URL('..', import.meta.url));
const staticRoot = path.join(previewRoot, 'storybook-static');
const port = Number(process.env.PREVIEW_SMOKE_PORT || 6010);

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.glb': 'model/gltf-binary',
};

function serveFile(request, response) {
  const pathname = decodeURIComponent(new URL(request.url, `http://127.0.0.1:${port}`).pathname);
  let file = path.join(staticRoot, pathname.replace(/^\/+/, ''));
  if (existsSync(file) && statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!existsSync(file)) {
    response.writeHead(404);
    response.end('not found');
    return;
  }
  response.writeHead(200, { 'content-type': mime[path.extname(file)] || 'application/octet-stream' });
  response.end(readFileSync(file));
}

const server = http.createServer(serveFile);
await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));

const systemChrome = process.platform === 'win32'
  ? 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  : null;
const launchOptions = { headless: true };
if (systemChrome && existsSync(systemChrome)) launchOptions.executablePath = systemChrome;
const browser = await chromium.launch(launchOptions);

async function checkStory(id, assetId, expectedClips = []) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  const failedResponses = [];
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().startsWith('Failed to load resource:')) errors.push(message.text());
  });
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('response', (response) => {
    if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`);
  });
  const url = `http://127.0.0.1:${port}/iframe.html?id=${id}&viewMode=story`;
  await page.goto(url, { waitUntil: 'networkidle' });
  const viewer = page.locator(`awful-model-viewer[data-model-loaded="${assetId}"]`);
  await viewer.waitFor({ state: 'attached', timeout: 20000 });
  const canvas = page.locator('awful-model-viewer canvas');
  await canvas.waitFor({ state: 'visible', timeout: 5000 });
  const size = await canvas.evaluate((element) => [element.width, element.height]);
  if (size[0] <= 0 || size[1] <= 0) {
    throw new Error(`${assetId}: canvas has invalid size ${size}`);
  }
  if (assetId.startsWith('iphone-') || assetId.startsWith('ipad-') || assetId.startsWith('macbook-')) {
    const screen = page.locator('awful-model-viewer select[data-control="screen-state"]');
    if (await screen.isEnabled()) {
      const options = await screen.locator('option').evaluateAll((items) => items.map((item) => item.value));
      if (!options.includes('screen_off') || !options.includes('screen_on')) {
        throw new Error(`${assetId}: screen state controls missing`);
      }
      await screen.selectOption('screen_off');
      await screen.selectOption('screen_on');
    }
    if (expectedClips.length) {
      const clips = page.locator('awful-model-viewer select[data-control="animation-clip"]');
      const options = await clips.locator('option').evaluateAll((items) => items.map((item) => item.value));
      for (const clip of expectedClips) if (!options.includes(clip)) throw new Error(`${assetId}: missing animation ${clip}`);
      await clips.selectOption(expectedClips[0]);
      await page.locator('awful-model-viewer input[data-control="animation"]').check();
      await page.waitForTimeout(150);
      await viewer.evaluate(element => {
        const action = element._animationAction;
        action.time = action.getClip().duration;
        element._mixer.update(0);
      });
      await page.locator('awful-model-viewer button[data-action="fit"]').click();
    }
    const snapshot = await viewer.evaluate(element => ({ asset: element.asset, verified: element.dataset.snapshotVerified }));
    if (!snapshot.asset.reviewOnly || snapshot.verified !== snapshot.asset.sha256) throw new Error(`${assetId}: device review snapshot was not verified`);
    const fingerprint = () => viewer.evaluate(element => {
      const meshes = [];
      element._model.traverse(object => { if (object.isMesh && !object.userData.previewWireframeOverlay) meshes.push([object.name, object.geometry.uuid, object.geometry.index?.count, object.geometry.attributes.position.count]); });
      return meshes;
    });
    const before = await fingerprint();
    await page.locator('awful-model-viewer input[data-control="animation"]').uncheck();
    const mode = page.locator('awful-model-viewer select[data-control="mode"]');
    await mode.selectOption('wireframe');
    const wire = await viewer.evaluate(element => {
      let baseValid = true, overlayValid = true, overlays = 0;
      element._model.traverse(object => {
        if (!object.isMesh) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        if (object.userData.previewWireframeOverlay) {
          overlays++;
          for (const material of materials) overlayValid &&= material.isMeshBasicMaterial && material.wireframe && material.depthTest && !material.depthWrite && material.color?.getHexString() === 'ececec';
        } else {
          for (const material of materials) baseValid &&= material.isMeshBasicMaterial && !material.wireframe && material.depthTest && material.depthWrite && material.colorWrite === false;
        }
      });
      return { baseValid, overlayValid, overlays };
    });
    if (!wire.baseValid || !wire.overlayValid || wire.overlays !== before.length || JSON.stringify(before) !== JSON.stringify(await fingerprint())) throw new Error(`${assetId}: hidden-line wireframe does not preserve unchanged GLB triangles`);
    if (process.env.PREVIEW_EVIDENCE_DIR) {
      mkdirSync(process.env.PREVIEW_EVIDENCE_DIR, { recursive: true });
      await page.screenshot({ path: path.join(process.env.PREVIEW_EVIDENCE_DIR, `${assetId}-wireframe.png`) });
    }
    await mode.selectOption('texture');
    const render = await viewer.evaluate(element => {
      let valid = true;
      element._model.traverse(object => { if (object.isMesh) for (const material of (Array.isArray(object.material) ? object.material : [object.material])) valid &&= !material.wireframe && material.isMeshStandardMaterial; });
      return valid;
    });
    if (!render || JSON.stringify(before) !== JSON.stringify(await fingerprint())) throw new Error(`${assetId}: render materials/geometry were not restored`);
    if (process.env.PREVIEW_EVIDENCE_DIR) await page.screenshot({ path: path.join(process.env.PREVIEW_EVIDENCE_DIR, `${assetId}-render.png`) });
  }
  if (assetId === 'iphone-17-v30') {
    if (id === 'models-devices--i-phone-17') {
      const identity = await viewer.evaluate(element => ({ asset: element.asset, verified: element.dataset.snapshotVerified }));
      if (!identity.asset.frozenReview || identity.verified !== 'ba4ef30c68ef93470eff6d8d472d78454ad51f99a727469a8f6d12fa58eda05c') throw new Error('Primary iPhone story is not the verified #146 Human Gate candidate');
      const profile = await viewer.evaluate(element => ({ exposure: element._renderer.toneMappingExposure, fov: element._perspective.fov, environment: element._scene.environmentIntensity, light: element._viewLight.intensity }));
      if (profile.exposure !== .7 || profile.fov !== 35 || profile.environment !== 1 || profile.light !== .65) throw new Error('Human Gate renderer profile changed');
      const part = page.locator('awful-model-viewer select[data-control="part"]');
      if (await part.count() !== 1) throw new Error('Human Gate iPhone lacks part isolation');
      const originalNodes = await viewer.evaluate(element => element.asset.reviewParts.flatMap(group => group.meshes).map(name => {
        const node = element._model.getObjectByName(name);
        return [name, node.parent.uuid, node.matrixWorld.toArray()];
      }));
      const options = await part.locator('option').evaluateAll(items => items.map(item => item.value));
      if (options.filter(value => value.startsWith('mesh:')).length !== 51) throw new Error('Review leaves do not cover the 51 exported nodes');
      for (const choice of options) {
        await part.selectOption(choice);
        const state = await viewer.evaluate(element => {
          const nodes = element.asset.reviewParts.flatMap(group => group.meshes).map(name => {
            const node = element._model.getObjectByName(name);
            return [name, node.parent.uuid, node.matrixWorld.toArray()];
          });
          const visible = element.asset.reviewParts.flatMap(group => group.meshes).filter(name => element._model.getObjectByName(name).visible);
          return { nodes, visible };
        });
        if (JSON.stringify(state.nodes) !== JSON.stringify(originalNodes)) throw new Error(`${choice}: isolation changed assembly transforms/parents`);
        const expected = choice === 'all' ? identity.asset.reviewParts.flatMap(group => group.meshes)
          : choice.startsWith('mesh:') ? [choice.slice(5)]
            : identity.asset.reviewParts.find(group => group.id === choice.slice(6)).meshes;
        if (JSON.stringify(state.visible.slice().sort()) !== JSON.stringify(expected.slice().sort())) throw new Error(`${choice}: wrong visible parts`);
      }
      await part.selectOption('all');
    }
    const readDelivery = () => viewer.evaluate(element => {
      const meshes = [], materials = {};
      element._model.traverse(object => {
        if (!object.isMesh || object.userData.previewWireframeOverlay) return;
        meshes.push([object.name, object.geometry.uuid, object.geometry.index?.count ?? object.geometry.attributes.position.count]);
        for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
          materials[material.name] = { color: material.color?.getHexString(), normal: material.normalMap?.uuid ?? null, roughness: material.roughnessMap?.uuid ?? null, wireframe: material.wireframe, envMapIntensity: material.envMapIntensity };
        }
      });
      return { meshes, materials };
    });
    const original = await readDelivery();
    for (const [finish, expected] of [['black', '292a2c'], ['white', 'b8b8b6'], ['mist_blue', '687c95'], ['sage', '737e5e'], ['lavender', '998fa8']]) {
      await page.locator('awful-model-viewer select[data-control="colorway"]').selectOption(finish);
      const current = await readDelivery();
      for (const [name, material] of Object.entries(current.materials)) {
        if (name === 'MAT_ANODIZED_ALUMINUM' || /^MAT_ANODIZED_ALUMINUM_(ACTION_BUTTON|SIDE_BUTTON|VOL_UP|VOL_DOWN)$/.test(name)) {
          if (material.color !== expected) throw new Error(`${id}/${finish}: ${name} remains ${material.color}`);
          if (material.envMapIntensity !== .55) throw new Error(`${id}: ${name} has inconsistent reflection policy`);
        }
        if (material.normal !== original.materials[name].normal || material.roughness !== original.materials[name].roughness) throw new Error(`${id}: finish replaced PBR maps on ${name}`);
      }
    }
    const mode = page.locator('awful-model-viewer select[data-control="mode"]');
    const wireState = () => viewer.evaluate(element => {
      let bases = 0, overlays = 0, valid = true;
      element._model.traverse(object => {
        if (!object.isMesh) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        if (object.userData.previewWireframeOverlay) {
          overlays++;
          for (const material of materials) valid &&= material.isMeshBasicMaterial && material.wireframe && material.color?.getHexString() === 'ececec' && material.depthTest && !material.depthWrite;
        } else {
          bases++;
          for (const material of materials) valid &&= material.isMeshBasicMaterial && !material.wireframe && material.colorWrite === false && material.depthTest && material.depthWrite;
        }
      });
      return { bases, overlays, valid };
    });
    await mode.selectOption('wireframe');
    let hiddenLine = await wireState();
    if (!hiddenLine.valid || hiddenLine.bases !== original.meshes.length || hiddenLine.overlays !== original.meshes.length) throw new Error(`${id}: incomplete hidden-line GLB wireframe`);
    const wireGeometry = await readDelivery();
    if (JSON.stringify(wireGeometry.meshes) !== JSON.stringify(original.meshes)) throw new Error(`${id}: wireframe replaced delivery geometry`);
    await page.locator('awful-model-viewer select[data-control="colorway"]').selectOption('black');
    await page.locator('awful-model-viewer select[data-control="screen-state"]').selectOption('screen_off');
    hiddenLine = await wireState();
    if (!hiddenLine.valid) throw new Error('Finish controls changed the diagnostic wire overlay');
    await mode.selectOption('texture');
    const restored = await readDelivery();
    if (Object.values(restored.materials).some(material => material.wireframe)) throw new Error(`${id}: wireframe leaked into render`);
    for (const [name, material] of Object.entries(restored.materials)) {
      if (material.normal !== original.materials[name].normal || material.roughness !== original.materials[name].roughness) throw new Error(`${id}: render did not restore original PBR maps on ${name}`);
      if ((name === 'MAT_ANODIZED_ALUMINUM' || /^MAT_ANODIZED_ALUMINUM_(ACTION_BUTTON|SIDE_BUTTON|VOL_UP|VOL_DOWN)$/.test(name)) && material.color !== '292a2c') throw new Error('Finish selected in wireframe was lost on render restoration');
    }
    const screenRestored = await viewer.evaluate(element => {
      let state;
      element._model.traverse(object => {
        for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
          if (material?.name === 'MAT_SCREEN_CONTENT') state = { map: Boolean(material.map), emission: material.emissiveIntensity };
        }
      });
      return state;
    });
    if (screenRestored?.map || screenRestored?.emission !== 0) throw new Error('Screen state selected in wireframe was lost on render restoration');
    await mode.selectOption('wireframe');
    await page.locator('awful-model-viewer select[data-control="colorway"]').selectOption('white');
    await page.locator('awful-model-viewer select[data-control="screen-state"]').selectOption('screen_on');
    await mode.selectOption('texture');
    const onRestored = await viewer.evaluate(element => {
      const state = {};
      element._model.traverse(object => {
        for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
          if (material?.name === 'MAT_ANODIZED_ALUMINUM') state.color = material.color.getHexString();
          if (material?.name === 'MAT_SCREEN_CONTENT') state.screen = { map: Boolean(material.map), emission: material.emissiveIntensity };
        }
      });
      return state;
    });
    if (onRestored.color !== 'b8b8b6' || !onRestored.screen?.map || onRestored.screen?.emission !== 1) throw new Error('White/Home screen selected in wireframe was not restored');
    await page.locator('awful-model-viewer select[data-control="colorway"]').selectOption('black');
    const beforeOrbit = await viewer.evaluate(element => element._camera.position.toArray());
    const box = await canvas.boundingBox();
    await page.mouse.move(box.x + box.width * .5, box.y + box.height * .5);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .65, box.y + box.height * .55, { steps: 8 });
    await page.mouse.up();
    await page.waitForTimeout(150);
    const afterOrbit = await viewer.evaluate(element => element._camera.position.toArray());
    if (JSON.stringify(beforeOrbit) === JSON.stringify(afterOrbit)) throw new Error(`${id}: orbit did not move camera`);
    const beforeZoom = await viewer.evaluate(element => element._camera.position.distanceTo(element._controls.target));
    await page.mouse.wheel(0, -180);
    await page.waitForTimeout(150);
    const afterZoom = await viewer.evaluate(element => element._camera.position.distanceTo(element._controls.target));
    if (beforeZoom === afterZoom) throw new Error(`${id}: zoom did not move camera`);
  }
  const relevant404 = failedResponses.filter((entry) => !entry.includes('/favicon'));
  if (errors.length || relevant404.length) {
    throw new Error(`${assetId}: browser errors: ${[...errors, ...relevant404].join(' | ')}`);
  }
  await page.close();
}

async function rejectChangedReviewStory() {
  const page = await browser.newPage();
  await page.route('**/assets/iphone-review/human-gate-2026-10-06/model.glb', async route => {
    const response = await route.fetch();
    const body = await response.body();
    body[body.length - 1] ^= 1;
    await route.fulfill({ response, body });
  });
  await page.goto(`http://127.0.0.1:${port}/iframe.html?id=models-devices--i-phone-17&viewMode=story`, { waitUntil: 'networkidle' });
  const viewer = page.locator('awful-model-viewer[data-model-error]');
  await viewer.waitFor({ timeout: 20000 });
  const state = await viewer.evaluate(element => ({ error: element.dataset.modelError, loaded: element.dataset.modelLoaded }));
  if (!/snapshot checksum mismatch/i.test(state.error) || state.loaded) throw new Error('Changed pinned review GLB was not rejected before display');
  await page.close();
}

async function checkCatalogNavigation() {
  const page = await browser.newPage();
  await page.goto(`http://127.0.0.1:${port}/iframe.html?id=models-catalog--catalog&viewMode=story`, { waitUntil: 'networkidle' });
  await page.locator('a[href*="i-pad-pro-11"]').click();
  await page.waitForURL(url => url.searchParams.get('path') === '/story/models-devices--i-pad-pro-11');
  if (new URL(page.url()).pathname !== '/') throw new Error('Catalog link navigated to the story iframe instead of the Storybook manager');
  await page.frameLocator('#storybook-preview-iframe').locator('awful-model-viewer[data-model-loaded="ipad-pro-11-m5-v6"]').waitFor({ timeout: 20000 });
  await page.close();
}

try {
  await checkCatalogNavigation();
  const index = await (await browser.newPage()).request.get(`http://127.0.0.1:${port}/index.json`);
  const iphoneStories = Object.keys((await index.json()).entries).filter(id => id.startsWith('models-devices--i-phone-17'));
  if (JSON.stringify(iphoneStories) !== JSON.stringify(['models-devices--i-phone-17'])) throw new Error('Ambiguous iPhone variants remain in Storybook');
  await checkStory('models-devices--i-phone-17', 'iphone-17-v30');
  await rejectChangedReviewStory();
  await checkStory('models-devices--i-pad-pro-11', 'ipad-pro-11-m5-v6');
  await checkStory('models-devices--i-pad-pro-13', 'ipad-pro-13-m5-v6');
  await checkStory('models-devices--mac-book-pro-14', 'macbook-pro-14-m5-v1', ['lid_open', 'lid_close']);
  await checkStory('models-studio-equipment--c-stand', 'studio-support-cstand-01');
  await checkStory('models-studio-equipment--profoto-d-1', 'profoto-d1-500-air');
  await checkStory('models-studio-equipment--profoto-magnum', 'profoto-magnum-100624');
  await checkStory('models-studio-equipment--studio-sandbag', 'studio-sandbag-01');
  await checkStory('models-scenes--white-studio', 'white-studio-v2');
  await checkStory('models-scenes--dark-neon', 'dark-neon-v2');
  await checkStory('models-scenes--loft-daylight', 'loft-daylight-v2');
  console.log('Storybook model smoke passed: exact iPhone Human Gate candidate + other canonical assets; hidden-line GLB triangle wireframe/render, orbit and zoom verified');
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
