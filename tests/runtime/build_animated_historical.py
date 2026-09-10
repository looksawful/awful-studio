"""Build a real animated 0.0.15 scene. No Extension is loaded in this process."""
import argparse
import hashlib
from pathlib import Path
import socket
import sys
import types

import bpy

EXPECTED_SHA = '5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b'


def block_network():
    def blocked(*args, **kwargs):
        raise OSError('Network forbidden in historical runtime fixture')
    socket.create_connection = blocked
    socket.socket.connect = blocked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if hashlib.sha256(args.source.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise RuntimeError('Historical source checksum mismatch')
    block_network()
    mod = types.ModuleType('awful_historical_animated_fixture')
    mod.__file__ = str(args.source)
    sys.modules[mod.__name__] = mod
    exec(compile(args.source.read_text(), str(args.source), 'exec'), mod.__dict__)
    mod.register()
    mod.build_studio(True)
    mod.apply_product_motion(bpy.context.scene, 'SPIN_Z')
    actions = [getattr(getattr(obj, 'animation_data', None), 'action', None)
               for obj in bpy.context.scene.objects if obj.get('awful_managed')]
    actions = [action for action in actions if action]
    if not actions:
        raise RuntimeError('Historical 0.0.15 fixture did not create a generated Action')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))


if __name__ == '__main__':
    main()
