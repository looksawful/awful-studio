export default {
  stories: ['../stories/**/*.stories.mjs'],
  staticDirs: [
    { from: '../../assets/device_mockups/iphone_17/runtime/v30', to: '/assets/device_mockups/iphone_17/runtime/v30' },
    { from: '../../assets/device_mockups/ipad_pro/runtime/v6', to: '/assets/device_mockups/ipad_pro/runtime/v6' },
    { from: '../../assets/device_mockups/macbook_pro_14/runtime/v1', to: '/assets/device_mockups/macbook_pro_14/runtime/v1' },
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
