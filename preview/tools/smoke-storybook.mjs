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
