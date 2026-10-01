// Explicit online capture; ordinary Blender builds use the committed offline PNG.
import { chromium } from '../preview/node_modules/playwright/index.mjs';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const output = fileURLToPath(new URL('../assets/device_mockups/macbook_pro_14/reference/looksawful_home_3024x1964.png', import.meta.url));
const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
try {
  const page = await browser.newPage({ viewport: { width: 1512, height: 982 }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  await page.goto('https://www.looksawful.ru/', { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  const cookieChoice = page.getByRole('button', { name: 'Отклонить', exact: true });
  if (await cookieChoice.isVisible()) await cookieChoice.click();
  await page.screenshot({ path: output, fullPage: false, animations: 'disabled' });
  const metadata = { url: page.url(), captured_at: new Date().toISOString(), viewport_css: [1512, 982], device_scale_factor: 2, image_px: [3024, 1964], sha256: createHash('sha256').update(readFileSync(output)).digest('hex'), mode: 'website viewport, no invented browser or OS chrome' };
  writeFileSync(output.replace('.png', '.json'), JSON.stringify(metadata, null, 2) + '\n');
  console.log(JSON.stringify(metadata));
} finally { await browser.close(); }
