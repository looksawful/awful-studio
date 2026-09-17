import argparse
from pathlib import Path
import sys

import bpy


def parse_args():
    argv = sys.argv
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    return parser.parse_args(argv)


def export_preview(output: Path):
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    selected = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or obj.hide_render:
            continue
        obj.hide_set(False)
        obj.select_set(True)
        selected.append(obj)
    if not selected:
        raise RuntimeError('Scene contains no renderable mesh objects')
    bpy.context.view_layer.objects.active = selected[0]
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    if not output.is_file() or output.stat().st_size <= 1024:
        raise RuntimeError(f'Invalid preview GLB: {output}')
    print(f'preview_glb={output}')


if __name__ == '__main__':
    export_preview(parse_args().output)
