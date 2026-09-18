#!/usr/bin/env python3
"""Build an explicit local AWFUL STUDIO Production Pass review artifact.

Run inside Blender 5.2.1, for example:

    blender --background --factory-startup \
      --python tools/production_pass_review.py -- \
      --output A:/Temp/awful-production-review --render

This tool is intentionally outside Extension runtime. It never downloads assets
and only renders when --render is provided.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / 'extension'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--product', default='BOTTLE')
    parser.add_argument('--camera', default='HERO_85')
    parser.add_argument('--environment', default='AUTO')
    parser.add_argument(
        '--looks',
        nargs='+',
        default=['PRODUCT', 'ACCENT', 'GOBO', 'WINDOW'],
    )
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=800)
    parser.add_argument('--samples', type=int, default=16)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return parser.parse_args(argv)


def _bounded_render_args(args: argparse.Namespace) -> None:
    if not 128 <= args.width <= 1920:
        raise ValueError('--width must be between 128 and 1920')
    if not 128 <= args.height <= 1920:
        raise ValueError('--height must be between 128 and 1920')
    if not 1 <= args.samples <= 64:
        raise ValueError('--samples must be between 1 and 64')


def _prepare_clean_review_scene() -> None:
    if not bpy.app.background:
        raise RuntimeError(
            'Production Pass review must run in Blender background mode')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0 and not datablock.use_fake_user:
                datablocks.remove(datablock)

    collection = bpy.data.collections.get('Collection')
    if collection is not None and len(collection.objects) == 0:
        try:
            bpy.data.collections.remove(collection)
        except RuntimeError:
            pass


def _pack_managed_images(awful_studio) -> tuple[str, ...]:
    legacy = awful_studio.legacy
    packed = []
    for image in bpy.data.images:
        if (
            legacy.is_managed(image)
            and image.source == 'FILE'
            and image.users > 0
            and image.packed_file is None
        ):
            image.pack()
            packed.append(image.name)
    return tuple(packed)


def _scene_counts() -> dict[str, int]:
    return {
        'objects': len(bpy.data.objects),
        'collections': len(bpy.data.collections),
        'materials': len(bpy.data.materials),
        'lights': len(bpy.data.lights),
        'images': len(bpy.data.images),
        'actions': len(bpy.data.actions),
    }


def _active_state(awful_studio, scene) -> dict[str, object]:
    legacy = awful_studio.legacy
    camera = legacy.REG.object('CAMERA')
    return {
        'product': str(getattr(scene.awful_studio, 'product_mockup', 'NONE')),
        'lighting': str(getattr(scene.awful_studio, 'studio_light_preset', '')),
        'camera_view': str(getattr(scene.awful_studio, 'camera_view', '')),
        'camera_motion': str(getattr(scene.awful_studio, 'camera_motion', '')),
        'camera_lens': float(camera.data.lens) if camera is not None else None,
        'environment': str(getattr(scene.awful_studio, 'world_preset', '')),
        'studio_lights': bool(getattr(scene.awful_studio, 'studio_lights_enabled', False)),
        'world_enabled': bool(getattr(scene.awful_studio, 'natural_light_enabled', False)),
        'background_visible': bool(
            getattr(scene.awful_studio, 'show_environment_background', False)
        ),
        'window_glass': bool(getattr(scene.awful_studio, 'window_glass_enabled', False)),
        'counts': _scene_counts(),
    }


def _apply_product(awful_studio, scene, key: str) -> None:
    from awful_studio import product_quality

    if key == 'NONE':
        return
    scene.awful_studio.product_mockup = key
    product_quality.replace_mockup(awful_studio.legacy, scene, key)
    awful_studio.legacy.apply_product_motion(scene, 'STATIC')


def _apply_review_state(
    awful_studio,
    scene,
    *,
    look: str,
    camera_view: str,
    environment: str,
) -> None:
    from awful_studio import lighting_workflow

    lighting_workflow.apply_look(awful_studio.legacy, scene, look)
    awful_studio.legacy.apply_camera_view(scene, camera_view)
    if environment != 'AUTO':
        scene.awful_studio.world_preset = environment
        awful_studio.legacy.apply_environment_preset(
            scene,
            environment,
            True,
        )
    bpy.context.view_layer.update()


def _render_look(
    awful_studio,
    scene,
    output: Path,
    *,
    look: str,
    camera_view: str,
    environment: str,
) -> Path:
    _apply_review_state(
        awful_studio,
        scene,
        look=look,
        camera_view=camera_view,
        environment=environment,
    )
    path = output / f'{look.lower()}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path


def main() -> int:
    args = parse_args()
    _bounded_render_args(args)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    _prepare_clean_review_scene()
    sys.path.insert(0, str(EXTENSION))
    import awful_studio

    awful_studio.register()
    awful_studio.run_build(bpy.context)
    scene = bpy.context.scene

    _apply_product(awful_studio, scene, args.product)
    _apply_review_state(
        awful_studio,
        scene,
        look=args.looks[0],
        camera_view=args.camera,
        environment=args.environment,
    )
    awful_studio.legacy.validate_static_configuration(scene)
    awful_studio.legacy.validate_built_scene(scene)
    packed_images = _pack_managed_images(awful_studio)

    blend_path = output / 'FullStudio.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest: dict[str, object] = {
        'status': 'passed',
        'blender': bpy.app.version_string,
        'extension_version': '.'.join(map(str, awful_studio.VERSION)),
        'source_root': str(ROOT),
        'scene': str(blend_path),
        'product': args.product,
        'camera': args.camera,
        'environment': args.environment,
        'looks': list(args.looks),
        'render_requested': bool(args.render),
        'review_render': {
            'width': args.width,
            'height': args.height,
            'samples': args.samples,
        },
        'base_state': _active_state(awful_studio, scene),
        'packed_images': list(packed_images),
        'renders': [],
    }

    if args.render:
        original = {
            'resolution_x': scene.render.resolution_x,
            'resolution_y': scene.render.resolution_y,
            'resolution_percentage': scene.render.resolution_percentage,
            'samples': scene.cycles.samples,
            'filepath': scene.render.filepath,
        }
        try:
            scene.render.resolution_x = args.width
            scene.render.resolution_y = args.height
            scene.render.resolution_percentage = 100
            scene.cycles.samples = args.samples
            if hasattr(scene.cycles, 'use_denoising'):
                scene.cycles.use_denoising = True

            for look in args.looks:
                render_path = _render_look(
                    awful_studio,
                    scene,
                    output,
                    look=look,
                    camera_view=args.camera,
                    environment=args.environment,
                )
                manifest['renders'].append({
                    'look': look,
                    'path': str(render_path),
                    'state': _active_state(awful_studio, scene),
                })
        finally:
            scene.render.resolution_x = original['resolution_x']
            scene.render.resolution_y = original['resolution_y']
            scene.render.resolution_percentage = original['resolution_percentage']
            scene.cycles.samples = original['samples']
            scene.render.filepath = original['filepath']

    manifest_path = output / 'manifest.json'
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding='utf-8',
    )
    print('AWFUL_REVIEW_OK', manifest_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
