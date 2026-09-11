# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime-performance policy for AWFUL STUDIO.

Studio Build/Rebuild configures render settings but must not enumerate or change
Cycles hardware. Device selection stays under Blender/user control. Explicit GPU
configuration remains available through the retained legacy helper if ever
needed by a separate opt-in workflow.
"""


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
            return original_setup_render(scene)
        finally:
            legacy.configure_cycles_gpu = original_probe

    legacy.setup_render = setup_render
    legacy._awful_runtime_performance_installed = True
