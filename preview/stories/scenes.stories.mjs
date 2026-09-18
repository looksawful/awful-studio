import { renderGroup } from '../src/story-factory.mjs';
export default { title: 'Models/Scenes', parameters: { layout: 'fullscreen' } };
const story = (assetId) => ({ render: () => renderGroup('Scenes', assetId) });
export const WhiteStudio = story('white-studio-v2'); WhiteStudio.storyName = 'White Studio';
export const DarkNeon = story('dark-neon-v2'); DarkNeon.storyName = 'Dark Neon';
export const LoftDaylight = story('loft-daylight-v2'); LoftDaylight.storyName = 'Loft Daylight';
