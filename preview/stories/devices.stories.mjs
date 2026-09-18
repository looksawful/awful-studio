import { renderGroup } from '../src/story-factory.mjs';
export default { title: 'Models/Devices', parameters: { layout: 'fullscreen' } };
const story = (assetId) => ({ render: () => renderGroup('Devices', assetId) });
export const IPhone17 = story('iphone-17-v30'); IPhone17.storyName = 'iPhone 17';
export const IPadPro11 = story('ipad-pro-11-m5-v6'); IPadPro11.storyName = 'iPad Pro 11 M5';
export const IPadPro13 = story('ipad-pro-13-m5-v6'); IPadPro13.storyName = 'iPad Pro 13 M5';
export const MacBookPro14 = story('macbook-pro-14-m5-v1'); MacBookPro14.storyName = 'MacBook Pro 14 M5';
