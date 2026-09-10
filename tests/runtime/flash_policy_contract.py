"""Alpha 0.0.16 flash regime: real packaged Blender runtime assertions, no render."""
import argparse
import importlib
from pathlib import Path
import sys

import addon_utils
import bpy

MODULE = 'bl_ext.awful_test.awful_studio'
EPS = 1e-5


def close(a, b):
    return abs(float(a) - float(b)) <= EPS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not addon_utils.check(MODULE)[1]:
        addon_utils.enable(MODULE, default_set=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.input), use_scripts=False)
    ext = importlib.import_module(MODULE)
    scene = bpy.context.scene
    settings = scene.awful_studio

    ext.legacy.apply_lighting_preset(scene, 'COMMERCIAL_3LIGHT', False, False)
    base_exposure = float(scene.view_settings.exposure)
    camera = ext.legacy.REG.require_object('CAMERA')
    base_fstop = float(camera.data.dof.aperture_fstop)
    key = ext.legacy.REG.require_object('LIGHT_Key')
    if not getattr(key.data, 'use_temperature', False) or not close(key.data.temperature, 4300.0):
        raise RuntimeError('Continuous neutral light default is not 4300 K')

    ext.legacy.apply_lighting_preset(scene, 'DIRECT_FLASH', False, False)
    camera = ext.legacy.REG.require_object('CAMERA')
    flash = ext.legacy.REG.require_object('LIGHT_CameraFlash')
    if not close(scene.view_settings.exposure, -3.0):
        raise RuntimeError(f'Flash scene exposure is {scene.view_settings.exposure}, expected -3 EV')
    if not close(camera.data.dof.aperture_fstop, 11.0):
        raise RuntimeError(f'Flash aperture intent is f/{camera.data.dof.aperture_fstop}, expected f/11')
    if not close(scene.get('awful_aperture_intent_fstop', 0.0), 11.0):
        raise RuntimeError('Flash aperture intent is not persisted as scene metadata')
    if not getattr(flash.data, 'use_temperature', False) or not close(flash.data.temperature, 6500.0):
        raise RuntimeError('Camera flash default is not 6500 K')
    if not (flash.location.x < -EPS and close(flash.location.y, 0.0)):
        raise RuntimeError(f'Portrait flash is not camera-left / vertically centered: {tuple(flash.location)}')

    # Reapplying flash must not overwrite the saved continuous baseline with flash values.
    ext.legacy.apply_lighting_preset(scene, 'DIRECT_FLASH_WIDE', False, False)
    if not close(scene.view_settings.exposure, -3.0):
        raise RuntimeError('Repeated Flash application drifted scene exposure')
    ext.legacy.apply_lighting_preset(scene, 'COMMERCIAL_3LIGHT', False, False)
    if not close(scene.view_settings.exposure, base_exposure):
        raise RuntimeError('Leaving Flash did not restore continuous scene exposure')
    if not close(camera.data.dof.aperture_fstop, base_fstop):
        raise RuntimeError('Leaving Flash did not restore continuous aperture state')
    if scene.get('awful_flash_regime_active', False):
        raise RuntimeError('Flash regime stayed active after returning to continuous lighting')


if __name__ == '__main__':
    main()
