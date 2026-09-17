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
    root.innerHTML = groups.map((group) => {
      const items = catalog.assets.filter((asset) => asset.group === group);
      return `<section style="margin-bottom:28px"><h2>${group}</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px">${items.map((asset) => `<article style="border:1px solid #303034;padding:12px;background:#121214"><strong>${asset.label}</strong><div>${asset.version}</div><small style="color:#999">${asset.id}</small></article>`).join('')}</div></section>`;
    }).join('');
    return root;
  },
};
