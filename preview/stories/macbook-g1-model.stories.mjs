import { createModelViewer } from '../src/model-viewer.mjs';

const asset = {
  id: 'macbook-pro-14-m5-g2-live',
  label: 'MacBook Pro 14 M5 - G2 candidate',
  group: 'Review',
  version: 'g2-candidate',
  sourceBlend: 'assets/device_mockups/macbook_pro_14/runtime/g2_candidate/macbook_pro_14_m5_g2_delivery.blend',
  previewGlb: 'assets/device_mockups/macbook_pro_14/runtime/g2_candidate/macbook_pro_14_m5_g2_web_meshopt.glb',
  lods: [
    {
      name: 'Meshopt',
      path: 'assets/device_mockups/macbook_pro_14/runtime/g2_candidate/macbook_pro_14_m5_g2_web_meshopt.glb',
    },
    {
      name: 'Compat',
      path: 'assets/device_mockups/macbook_pro_14/runtime/g2_candidate/macbook_pro_14_m5_g2_web.glb',
    },
  ],
  sourceRevision: 'ada4bc70f13fcbb6b7704fa31acb006e59be6dfaf7cfc5df74c584f1c1b41da2',
  sourceCommit: '518bb25ee580de5e65f330737583adc9bbe0cd8d',
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
  title: 'Review/MacBook G2 Model',
  parameters: { layout: 'fullscreen', controls: { disable: true } },
};

export const LiveModel = {
  name: 'Live model',
  render: () => createModelViewer(asset),
};
