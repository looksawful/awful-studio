import { groupOptions, renderGroup } from '../src/story-factory.mjs';

const options = groupOptions('Studio Equipment');

export default {
  title: 'Models/Studio Equipment',
  args: { assetId: options[0] },
  argTypes: { assetId: { control: 'select', options } },
  parameters: { layout: 'fullscreen' },
};

export const Viewer = {
  render: ({ assetId }) => renderGroup('Studio Equipment', assetId),
};
