import { createModelViewer } from '../src/model-viewer.mjs';

const asset = {
  id: 'macbook-pro-14-m5-g1-live',
  label: 'MacBook Pro 14 M5 - G1 live build',
  group: 'Review',
  version: 'g1-live',
  sourceBlend: 'assets/device_mockups/macbook_pro_14/runtime/v1/macbook_pro_14_m5_v1_delivery.blend',
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
  sourceRevision: '776f8a1e5ab8ca55cb6ee2a81a2187d152076c0c1c22f64d13c9b1a366204f20',
  sourceCommit: '34a4b4973704b7c8cf938ffd393002276399baa5',
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
  title: 'Review/MacBook G1 Model',
  parameters: { layout: 'fullscreen', controls: { disable: true } },
};

export const LiveModel = {
  name: 'Live model',
  render: () => createModelViewer(asset),
};
