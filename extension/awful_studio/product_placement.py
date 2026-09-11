# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure product/support placement policy for AWFUL STUDIO.

This module deliberately does not import Blender. It owns only coordinate math
that can be proved before the bpy adapter mutates scene transforms.
"""


def support_surface_offset(bottom_z: float, support_z: float) -> float:
    """Return the Z translation required to place ``bottom_z`` on ``support_z``."""
    return float(support_z) - float(bottom_z)


def mount_delta(*, center_x: float, center_y: float, bottom_z: float,
                target_x: float, target_y: float, support_z: float) -> tuple[float, float, float]:
    """Return world-space translation that centers XY and lands on support Z."""
    return (
        float(target_x) - float(center_x),
        float(target_y) - float(center_y),
        support_surface_offset(bottom_z, support_z),
    )
