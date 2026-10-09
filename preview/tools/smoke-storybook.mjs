import http from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
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
      if (assetId === 'ipad-pro-11-m5-v6' || assetId === 'ipad-pro-13-m5-v6') {
        // Guard against iPhone lookdev leaking through a shared material name.
        const logos = await viewer.evaluate((element) => {
          const values = [];
          element._model.traverse((object) => {
            if (!object.isMesh) return;
            for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
              if (material.name === 'MAT_APPLE_LOGO_DECAL') {
                values.push({ roughness: material.roughness, envMapIntensity: material.envMapIntensity });
              }
            }
          });
          return values;
        });
        if (!logos.length || logos.some((logo) => Math.abs(logo.roughness - 0.2) > 0.001 || Math.abs(logo.envMapIntensity - 1) > 0.001)) {
          throw new Error(`Shared iPhone material policy regressed ${assetId} logo: ${JSON.stringify(logos)}`);
        }
      }
      if (assetId === 'iphone-17-v30') {
        const backdrop = await viewer.evaluate((element) => `#${element._scene.background.getHexString()}`);
        if (backdrop !== '#92969f') throw new Error(`iPhone rear defaults to unreadable dark stage: ${backdrop}`);
        await page.locator('awful-model-viewer button[data-camera="rear"]').click();
        const rearPolicy = await viewer.evaluate((element) => {
          const materials = {};
          element._model.traverse((object) => {
            if (!object.isMesh) return;
            const entries = Array.isArray(object.material) ? object.material : [object.material];
            for (const material of entries) {
              if (['MAT_BACK_GLASS', 'MAT_APPLE_LOGO_DECAL'].includes(material.name)) {
                materials[material.name] = material.specularIntensity;
              }
            }
          });
          return materials;
        });
        if (rearPolicy.MAT_BACK_GLASS !== 0 || rearPolicy.MAT_APPLE_LOGO_DECAL !== 0) {
          throw new Error(`iPhone rear material hotspot suppression missing: ${JSON.stringify(rearPolicy)}`);
        }
        await page.locator('awful-model-viewer button[data-camera="front"]').click();
        const islandCenterRgb = await viewer.evaluate((element) => {
          let screenMaterial = null;
          element._model.traverse((object) => {
            if (!object.isMesh) return;
            const materials = Array.isArray(object.material) ? object.material : [object.material];
            for (const material of materials) {
              if (material.name === 'MAT_SCREEN_CONTENT') screenMaterial = material;
            }
          });
          const image = (screenMaterial?.emissiveMap ?? screenMaterial?.map)?.image;
          if (!image) return null;
          const canvas = document.createElement('canvas');
          canvas.width = image.width;
          canvas.height = image.height;
          const context = canvas.getContext('2d');
          context.drawImage(image, 0, 0);
          const rgba = context.getImageData(Math.floor(image.width / 2), Math.floor(image.height * 70 / 2622), 1, 1).data;
          return Array.from(rgba).slice(0, 3);
        });
        if (!islandCenterRgb || Math.max(...islandCenterRgb) > 5) {
          throw new Error(`iPhone system-owned Dynamic Island missing from screen_on compositor: ${JSON.stringify(islandCenterRgb)}`);
        }
      }
      const glow = await viewer.evaluate((element) => ({
        actual: [element._screenGlow?.width, element._screenGlow?.height],
        expected: [element.asset?.screenGlow?.width_mm / 1000, element.asset?.screenGlow?.height_mm / 1000],
      }));
      if (!glow.actual.every((value, index) => Number.isFinite(value) && Math.abs(value - glow.expected[index]) < 1e-6)) {
        throw new Error(`${assetId}: screen glow dimensions do not match manifest ${JSON.stringify(glow)}`);
      }
    }
    if (expectedClips.length) {
      const clips = page.locator('awful-model-viewer select[data-control="animation-clip"]');
      const options = await clips.locator('option').evaluateAll((items) => items.map((item) => item.value));
      for (const clip of expectedClips) if (!options.includes(clip)) throw new Error(`${assetId}: missing animation ${clip}`);
      await clips.selectOption(expectedClips[0]);
      await page.locator('awful-model-viewer input[data-control="animation"]').check();
      await page.waitForTimeout(150);
    }
  }
  const relevant404 = failedResponses.filter((entry) => !entry.includes('/favicon'));
  if (errors.length || relevant404.length) {
    throw new Error(`${assetId}: browser errors: ${[...errors, ...relevant404].join(' | ')}`);
  }
  await page.close();
}

try {
  await checkStory('models-devices--i-phone-17', 'iphone-17-v30');
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
  console.log('Storybook model smoke passed: all 11 canonical assets');
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
