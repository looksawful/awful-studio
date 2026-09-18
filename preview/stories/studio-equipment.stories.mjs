import { renderGroup } from '../src/story-factory.mjs';
export default { title: 'Models/Studio Equipment', parameters: { layout: 'fullscreen' } };
const story = (assetId) => ({ render: () => renderGroup('Studio Equipment', assetId) });
export const CStand = story('studio-support-cstand-01'); CStand.storyName = 'C-Stand';
export const ProfotoD1 = story('profoto-d1-500-air'); ProfotoD1.storyName = 'Profoto D1 500 Air';
export const ProfotoMagnum = story('profoto-magnum-100624'); ProfotoMagnum.storyName = 'Profoto Magnum 100624';
export const StudioSandbag = story('studio-sandbag-01'); StudioSandbag.storyName = 'Studio Sandbag';
