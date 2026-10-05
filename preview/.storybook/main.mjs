export default {
  stories: ['../stories/**/*.stories.mjs'],
  staticDirs: [
    { from: '../generated/iphone-review/frozen-current-2026-10-05', to: '/assets/iphone-review/frozen-current-2026-10-05' },
    { from: '../generated/device-review/current-2026-10-05', to: '/assets/device-review/current-2026-10-05' },
    { from: '../public/screens', to: '/screens' },
    { from: '../../assets/studio_equipment/studio_rig_v01/runtime/glb', to: '/assets/studio_equipment/studio_rig_v01/runtime/glb' },
    { from: '../../assets/studio_equipment/studio_rig_v01/runtime/lod', to: '/assets/studio_equipment/studio_rig_v01/runtime/lod' },
    { from: '../../assets/studio_equipment/studio_rig_v01/runtime/collision', to: '/assets/studio_equipment/studio_rig_v01/runtime/collision' },
    { from: '../generated/scenes', to: '/preview-scenes' },
  ],
  framework: {
    name: '@storybook/html-vite',
    options: {},
  },
};
