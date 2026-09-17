import { groupOptions, renderGroup } from '../src/story-factory.mjs';

const options = groupOptions('Devices');

export default {
  title: 'Models/Devices',
  args: { assetId: options[0] },
  argTypes: { assetId: { control: 'select', options } },
  parameters: { layout: 'fullscreen' },
};

export const Viewer = {
  render: ({ assetId }) => renderGroup('Devices', assetId),
};
