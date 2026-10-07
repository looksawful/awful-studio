import { renderGroup } from '../src/story-factory.mjs';

export default { title: 'Models/Devices', parameters: { layout: 'fullscreen' } };
const story = (assetId, options = {}) => ({ render: () => renderGroup('Devices', assetId, options) });

export const IPhone17 = story('iphone-17-v30', { colorway: 'white', screenState: 'screen_off' });
IPhone17.storyName = 'iPhone 17 - HUMAN GATE #146';

export const IPadPro11 = story('ipad-pro-11-m5-v6'); IPadPro11.storyName = 'iPad Pro 11 M5 — WIP REVIEW 05.10.2026';
export const IPadPro13 = story('ipad-pro-13-m5-v6'); IPadPro13.storyName = 'iPad Pro 13 M5 — WIP REVIEW 05.10.2026';
export const MacBookPro14 = story('macbook-pro-14-m5-v1'); MacBookPro14.storyName = 'MacBook Pro 14 M5 — WIP REVIEW 05.10.2026';
