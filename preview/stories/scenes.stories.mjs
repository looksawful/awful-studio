import { groupOptions, renderGroup } from '../src/story-factory.mjs';

const options = groupOptions('Scenes');

export default {
  title: 'Models/Scenes',
  args: { assetId: options[0] },
  argTypes: { assetId: { control: 'select', options } },
  parameters: { layout: 'fullscreen' },
};

export const Viewer = {
  render: ({ assetId }) => renderGroup('Scenes', assetId),
};
