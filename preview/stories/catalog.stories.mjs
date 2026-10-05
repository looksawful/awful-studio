import { catalog } from '../src/story-factory.mjs';

export default {
  title: 'Models/Catalog',
  parameters: { layout: 'fullscreen' },
};

export const Catalog = {
  render: () => {
    const root = document.createElement('main');
    root.style.cssText = 'padding:24px;background:#0b0b0c;color:#eee;min-height:100vh;font:14px/1.45 ui-monospace,monospace';
    const groups = ['Devices', 'Studio Equipment', 'Scenes'];
    const deviceStories = { 'iphone-17-v30': 'i-phone-17', 'ipad-pro-11-m5-v6': 'i-pad-pro-11', 'ipad-pro-13-m5-v6': 'i-pad-pro-13', 'macbook-pro-14-m5-v1': 'mac-book-pro-14' };
    root.innerHTML = '<p>Device review snapshots · 05.10.2026 · HUMAN NEEDED. This build identifies its own files; the published main build may be older.</p>' + groups.map((group) => {
      const items = catalog.assets.filter((asset) => asset.group === group);
      return `<section style="margin-bottom:28px"><h2>${group}</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px">${items.map((asset) => `<article style="border:1px solid #303034;padding:12px;background:#121214"><strong>${asset.label}</strong><div>${asset.version}</div><small style="color:#999">${asset.id}</small>${deviceStories[asset.id] ? `<p><a style="color:#9acaff" target="_top" href="./?path=/story/models-devices--${deviceStories[asset.id]}">Open render / wireframe</a></p><div>SHA-256: ${asset.sha256.slice(0, 12)}…</div>` : ''}</article>`).join('')}</div></section>`;
    }).join('');
    return root;
  },
};
