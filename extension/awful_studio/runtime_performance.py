# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime-performance policy for AWFUL STUDIO.

Build/Rebuild never enumerates or changes Cycles hardware. Device selection stays
under Blender/user control. This module owns explicit viewport-only preview modes
and lightweight diagnostics so slow CPU-backed Rendered Viewport sessions are
visible instead of being mistaken for runaway AWFUL scene complexity.
"""

_PREVIEW_PROFILES = {
    'FAST': {
        'samples': 8,
        'pixel_size': '2',
        'adaptive_threshold': 0.08,
        'denoise': True,
    },
    'QUALITY': {
        'samples': 16,
        'pixel_size': '1',
        'adaptive_threshold': 0.05,
        'denoise': True,
    },
}


def preview_profile(mode):
    try:
        return dict(_PREVIEW_PROFILES[mode])
    except KeyError as exc:
        raise ValueError(f'Unknown preview mode: {mode}') from exc


def _assign(target, name, value):
    if target is None or not hasattr(target, name):
        return False
    setattr(target, name, value)
    return True


def apply_preview_profile(scene, mode):
    """Apply viewport-only Cycles controls and leave final-render/device state alone."""
    profile = preview_profile(mode)
    _assign(scene.cycles, 'preview_samples', int(profile['samples']))
    _assign(scene.render, 'preview_pixel_size', str(profile['pixel_size']))
    _assign(scene.cycles, 'preview_adaptive_threshold', float(profile['adaptive_threshold']))
    _assign(scene.cycles, 'use_preview_denoising', bool(profile['denoise']))
    return profile


def _image_bytes(image):
    try:
        width, height = map(int, image.size)
        channels = int(getattr(image, 'channels', 4) or 4)
        if width <= 0 or height <= 0:
            return 0
        return width * height * max(1, channels) * 4
    except Exception:
        return 0


def collect_diagnostics(legacy, scene):
    """Collect cheap non-render viewport diagnostics without probing/changing devices."""
    compute_type = 'UNKNOWN'
    try:
        addon = legacy.bpy.context.preferences.addons.get('cycles')
        prefs = addon.preferences if addon else None
        compute_type = str(getattr(prefs, 'compute_device_type', 'NONE') or 'NONE')
    except Exception:
        compute_type = 'UNKNOWN'

    scene_device = str(getattr(scene.cycles, 'device', 'UNKNOWN'))
    objects = list(getattr(scene, 'objects', ()))
    images = list(getattr(legacy.bpy.data, 'images', ()))
    return {
        'engine': str(getattr(scene.render, 'engine', 'UNKNOWN')),
        'scene_device': scene_device,
        'compute_device_type': compute_type,
        'preview_samples': int(getattr(scene.cycles, 'preview_samples', 0) or 0),
        'preview_pixel_size': str(getattr(scene.render, 'preview_pixel_size', '?')),
        'preview_denoise': bool(getattr(scene.cycles, 'use_preview_denoising', False)),
        'light_tree': bool(getattr(scene.cycles, 'use_light_tree', False)),
        'object_count': len(objects),
        'light_count': sum(1 for obj in objects if getattr(obj, 'type', None) == 'LIGHT'),
        'image_count': len(images),
        'approx_image_bytes': sum(_image_bytes(image) for image in images),
        'cpu_warning': scene_device == 'CPU' or compute_type in {'NONE', ''},
    }


def _preserve_native_device(_scene):
    return 'NATIVE', 'Blender device selection unchanged'


def install(legacy):
    if getattr(legacy, '_awful_runtime_performance_installed', False):
        return

    original_setup_render = legacy.setup_render

    def setup_render(scene):
        original_probe = legacy.configure_cycles_gpu
        legacy.configure_cycles_gpu = _preserve_native_device
        try:
            result = original_setup_render(scene)
        finally:
            legacy.configure_cycles_gpu = original_probe
        if hasattr(scene, 'cycles') and hasattr(scene, 'render'):
            settings = getattr(scene, 'awful_studio', None)
            mode = getattr(settings, 'preview_mode', 'FAST')
            apply_preview_profile(scene, mode)
        return result

    legacy.setup_render = setup_render

    # Unit-policy tests intentionally use a minimal FakeLegacy. Keep the pure
    # setup-render adapter usable without requiring Blender UI registration.
    if not all(hasattr(legacy, attr) for attr in (
            'AWFUL_StudioSettings', 'EnumProperty', 'AWFUL_PT_Setup', 'CLASSES', 'bpy')):
        legacy._awful_runtime_performance_installed = True
        return

    def on_preview_mode(self, context):
        scene = getattr(context, 'scene', None)
        if scene is not None and getattr(scene.render, 'engine', '') == 'CYCLES':
            apply_preview_profile(scene, self.preview_mode)

    annotations = legacy.AWFUL_StudioSettings.__annotations__
    annotations['preview_mode'] = legacy.EnumProperty(
        name='Viewport Preview',
        items=[
            ('FAST', 'Fast Preview', 'Responsive Cycles viewport for look development'),
            ('QUALITY', 'Quality Preview', 'Higher-quality Cycles viewport without changing final render'),
        ],
        default='FAST',
        update=on_preview_mode,
    )

    original_setup_draw = legacy.AWFUL_PT_Setup.draw

    def draw_setup(self, context):
        original_setup_draw(self, context)
        scene = context.scene
        settings = scene.awful_studio
        box = self.layout.box()
        box.label(text='Viewport Preview')
        box.prop(settings, 'preview_mode', text='Mode')
        diagnostics = collect_diagnostics(legacy, scene)
        box.label(
            text=(f"Cycles device: {diagnostics['scene_device']} / "
                  f"{diagnostics['compute_device_type']}")
        )
        if diagnostics['cpu_warning']:
            box.label(
                text='CPU active. Configure Cycles GPU in Blender Preferences > System.',
                icon='ERROR',
            )
        box.label(
            text=(f"Samples {diagnostics['preview_samples']} | "
                  f"Lights {diagnostics['light_count']} | "
                  f"Images {diagnostics['image_count']}")
        )

    legacy.AWFUL_PT_Setup.draw = draw_setup
    legacy._awful_runtime_performance_installed = True
