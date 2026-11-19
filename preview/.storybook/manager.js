import { addons } from 'storybook/manager-api';

addons.setConfig({
  layoutCustomisations: {
    showPanel(state, defaultValue) {
      return state.viewMode === 'story' ? false : defaultValue;
    },
  },
});
