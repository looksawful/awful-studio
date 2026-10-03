import { createModelViewer } from '../src/model-viewer.mjs';

const asset = {
  id: 'macbook-pro-14-m5-v1-live',
  label: 'MacBook Pro 14 M5 - canonical v1',
  group: 'Review',
  version: 'v1',
  sourceBlend: 'extension/awful_studio/assets/devices/macbook_pro_14_m5_low_v1_release.blend',
  previewGlb: 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1_web_meshopt.glb',
  lods: [
    {
      name: 'Meshopt',
      path: 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1_web_meshopt.glb',
    },
    {
      name: 'Compat',
      path: 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1_web.glb',
    },
  ],
  sourceRevision: 'e0a105f4c83fa6695437e7bfb2c8f917b61d102da4bda4a9084a63a683693840',
  sourceCommit: '0d25c1ffba30dbc53c75b4879dffb8e348638613',
  animations: ['lid_open', 'lid_close'],
  screenStates: {
    screen_off: { emission_strength: 0, glow_energy: 0 },
    screen_on: { emission_strength: 0.65, glow_energy: 8 },
  },
  screenGlow: {
    anchor: 'SCREEN_GLOW_ANCHOR',
    type: 'rect_area',
    width_mm: 302.4,
    height_mm: 196.4,
    source_energy_w: 8,
  },
};

export default {
  title: 'Review/MacBook G2 Canonical',
  parameters: { layout: 'fullscreen', controls: { disable: true } },
};

export const LiveModel = {
  name: 'Live model',
  render: () => createModelViewer(asset),
};
