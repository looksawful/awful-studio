# SPDX-License-Identifier: GPL-3.0-or-later
"""Photographic lighting policy for Alpha 0.0.16.

This module adapts the retained v4 preset engine without touching a Blender scene
at import time. `install()` changes only in-memory preset metadata/callables before
Extension classes are registered. Scene exposure/aperture changes happen only when
a user explicitly applies/builds an AWFUL lighting preset.
"""
from dataclasses import replace

from bpy.props import EnumProperty

FLASH_SCENE_EXPOSURE = -3.0
FLASH_APERTURE_FSTOP = 11.0
FLASH_CCT = 6500.0
CONTINUOUS_CCT = 4300.0
FLASH_LOCAL_OFFSET = (-0.090, 0.075, 0.0)

_REGIME_KEY = 'awful_photographic_regime'
_SAVED_EXPOSURE_KEY = 'awful_preflash_exposure'
_SAVED_APERTURE_KEY = 'awful_preflash_aperture_fstop'
_APERTURE_INTENT_KEY = 'awful_aperture_intent_fstop'


def _retune_spec(spec):
    """Apply the established CCT/off-axis defaults without touching colored FX."""
    if spec.color is not None:
        return spec
    is_camera_flash = spec.role == 'LIGHT_CameraFlash' or spec.camera_local
    return replace(
        spec,
        temperature=FLASH_CCT if is_camera_flash else CONTINUOUS_CCT,
        local_offset=FLASH_LOCAL_OFFSET if is_camera_flash else spec.local_offset,
    )


def _retune_inventory(legacy):
    for preset_id, preset in tuple(legacy.LIGHTING_PRESETS.items()):
        legacy.LIGHTING_PRESETS[preset_id] = replace(
            preset,
            lights=tuple(_retune_spec(spec) for spec in preset.lights),
        )

    if 'DIRECT_FLASH_AMBIENT' not in legacy.LIGHTING_PRESETS:
        legacy.LIGHTING_PRESETS['DIRECT_FLASH_AMBIENT'] = legacy.LightingPreset(
            'DIRECT_FLASH_AMBIENT', 'FLASH', 'Neutral Ambient Flash',
            lights=(
                legacy.LightSpec(
                    'LIGHT_CameraFlash', camera_local=True,
                    absolute_size=(0.070, 0.045), base_power=180,
                    exposure_ev=3.1, spread=54, temperature=FLASH_CCT,
                    light_group='LG_FLASH', local_offset=FLASH_LOCAL_OFFSET,
                ),
                legacy.LightSpec(
                    'LIGHT_Fill', azimuth=32, elevation=16,
                    distance=legacy.R_FILL, size_x=legacy.SZ_FILL,
                    size_y=legacy.SZ_FILL, base_power=120,
                    exposure_ev=-1.7, spread=180,
                    temperature=CONTINUOUS_CCT, target='CENTER',
                    light_group='LG_FILL',
                ),
            ),
            camera_lens=50.0, camera_margin=1.22, flash_backdrop=True,
        )

    legacy.LIGHT_FAMILY_PRESETS = {
        family: [p.id for p in legacy.LIGHTING_PRESETS.values() if p.family == family]
        for family in legacy.LIGHT_FAMILY_ORDER
    }
    legacy.LIGHT_PRESET_LABELS = {
        key: value.label for key, value in legacy.LIGHTING_PRESETS.items()
    }

    # AWFUL_StudioSettings is defined while legacy.py imports, so refresh only its
    # deferred EnumProperty metadata before bpy.utils.register_class sees it.
    legacy.AWFUL_StudioSettings.__annotations__['studio_light_preset'] = EnumProperty(
        name='Lighting Preset',
        items=[(key, legacy.LIGHT_PRESET_LABELS[key], '') for key in legacy.LIGHTING_PRESETS],
        default='COMMERCIAL_3LIGHT',
    )


def _validate_inventory(legacy):
    if len(legacy.LIGHTING_PRESETS) != 17:
        raise RuntimeError(f'Expected 17 lighting presets, got {len(legacy.LIGHTING_PRESETS)}')
    required_flash = {
        'DIRECT_FLASH', 'DIRECT_FLASH_WIDE',
        'DIRECT_FLASH_AMBIENT', 'DIRECT_FLASH_COLOR',
    }
    if not required_flash.issubset(legacy.LIGHT_FAMILY_PRESETS.get('FLASH', ())):
        raise RuntimeError('Flash preset inventory is incomplete')


def _camera_aperture(scene, legacy):
    camera = legacy.REG.object('CAMERA')
    if camera is None:
        camera = getattr(scene, 'camera', None)
    dof = getattr(getattr(camera, 'data', None), 'dof', None) if camera else None
    return dof if dof is not None and hasattr(dof, 'aperture_fstop') else None


def apply_photographic_regime(scene, preset, legacy):
    """Apply/restore photographic intent at the explicit preset boundary only."""
    is_flash = preset.family == 'FLASH'
    previous = str(scene.get(_REGIME_KEY, 'CONTINUOUS'))
    aperture = _camera_aperture(scene, legacy)

    if is_flash:
        if previous != 'FLASH':
            scene[_SAVED_EXPOSURE_KEY] = float(scene.view_settings.exposure)
            if aperture is not None:
                scene[_SAVED_APERTURE_KEY] = float(aperture.aperture_fstop)
        scene.view_settings.exposure = FLASH_SCENE_EXPOSURE
        scene[_APERTURE_INTENT_KEY] = FLASH_APERTURE_FSTOP
        if aperture is not None:
            aperture.aperture_fstop = FLASH_APERTURE_FSTOP
        scene[_REGIME_KEY] = 'FLASH'
        return

    if previous == 'FLASH':
        scene.view_settings.exposure = float(scene.get(_SAVED_EXPOSURE_KEY, 0.0))
        if aperture is not None and _SAVED_APERTURE_KEY in scene:
            aperture.aperture_fstop = float(scene[_SAVED_APERTURE_KEY])
        for key in (_SAVED_EXPOSURE_KEY, _SAVED_APERTURE_KEY):
            if key in scene:
                del scene[key]
    if aperture is not None:
        scene[_APERTURE_INTENT_KEY] = float(aperture.aperture_fstop)
    scene[_REGIME_KEY] = 'CONTINUOUS'


def install(legacy):
    """Install the 0.0.16 policy exactly once, before class registration."""
    if getattr(legacy, '_awful_photography_policy_installed', False):
        return

    _retune_inventory(legacy)
    _validate_inventory(legacy)

    original_apply = legacy.apply_lighting_preset
    original_validate = legacy.validate_static_configuration

    def apply_lighting_preset(scene, preset_id, apply_camera_defaults=False,
                              apply_environment_defaults=True):
        result = original_apply(scene, preset_id, apply_camera_defaults,
                                apply_environment_defaults)
        apply_photographic_regime(scene, legacy.LIGHTING_PRESETS[preset_id], legacy)
        return result

    def validate_static_configuration(scene=None):
        # The retained legacy validator knows the historical 16-preset inventory.
        # Validate those rules against a temporary 16-item view, then validate the
        # additive 0.0.16 inventory contract separately. No scene state is touched.
        neutral = legacy.LIGHTING_PRESETS.pop('DIRECT_FLASH_AMBIENT')
        try:
            result = original_validate(scene)
        finally:
            legacy.LIGHTING_PRESETS['DIRECT_FLASH_AMBIENT'] = neutral
        _validate_inventory(legacy)
        return result

    legacy.apply_lighting_preset = apply_lighting_preset
    legacy.validate_static_configuration = validate_static_configuration
    legacy._awful_photography_policy_installed = True
