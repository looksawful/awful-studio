import { renderGroup } from '../src/story-factory.mjs';

export default { title: 'Models/Devices', parameters: { layout: 'fullscreen' } };
const story = (assetId, options = {}) => ({ render: () => renderGroup('Devices', assetId, options) });

export const IPhone17 = story('iphone-17-v30'); IPhone17.storyName = 'iPhone 17';
export const IPhone17Black = story('iphone-17-v30', { colorway: 'black' }); IPhone17Black.storyName = 'iPhone 17 — Black';
export const IPhone17White = story('iphone-17-v30', { colorway: 'white' }); IPhone17White.storyName = 'iPhone 17 — White';
export const IPhone17MistBlue = story('iphone-17-v30', { colorway: 'mist_blue' }); IPhone17MistBlue.storyName = 'iPhone 17 — Mist Blue';
export const IPhone17Sage = story('iphone-17-v30', { colorway: 'sage' }); IPhone17Sage.storyName = 'iPhone 17 — Sage';
export const IPhone17Lavender = story('iphone-17-v30', { colorway: 'lavender' }); IPhone17Lavender.storyName = 'iPhone 17 — Lavender';

export const IPadPro11 = story('ipad-pro-11-m5-v6'); IPadPro11.storyName = 'iPad Pro 11 M5';
export const IPadPro13 = story('ipad-pro-13-m5-v6'); IPadPro13.storyName = 'iPad Pro 13 M5';
export const MacBookPro14 = story('macbook-pro-14-m5-v1'); MacBookPro14.storyName = 'MacBook Pro 14 M5';
