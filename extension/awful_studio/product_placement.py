# SPDX-License-Identifier: GPL-3.0-or-later
"""Product/support placement policy and Blender adapter for AWFUL STUDIO.

Pure coordinate helpers remain Blender-independent. ``install()`` receives the
retained legacy adapter explicitly, so importing this module never touches bpy or
a scene.
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


def float_motion_heights(*, lift: float, amplitude: float) -> tuple[float, float, float, float, float]:
    """Return a support-safe bob cycle whose minimum never falls below ``lift``."""
    lift = float(lift)
    amplitude = max(0.0, float(amplitude))
    return (lift, lift + amplitude, lift, lift + amplitude, lift)


def _align_mounted_geometry(legacy, metrics):
    content = legacy.REG.require_object('PRODUCT_CONTENT')
    motion = legacy.REG.require_object('PRODUCT_MOTION')
    pedestal = legacy.REG.require_object('PEDESTAL')

    product_bbox = legacy.world_bbox(legacy.current_product_objects())
    pedestal_bbox = legacy.world_bbox([pedestal])
    if product_bbox is None or pedestal_bbox is None:
        raise RuntimeError('Mounted product or pedestal has no measurable geometry')

    minimum, maximum = product_bbox
    center = (minimum + maximum) * 0.5
    target = motion.matrix_world.translation
    delta = mount_delta(
        center_x=center.x,
        center_y=center.y,
        bottom_z=minimum.z,
        target_x=target.x,
        target_y=target.y,
        support_z=pedestal_bbox[1].z,
    )

    world_delta = legacy.Vector(delta)
    if content.parent is not None:
        local_delta = content.parent.matrix_world.inverted().to_3x3() @ world_delta
    else:
        local_delta = world_delta
    content.location += local_delta
    legacy.bpy.context.view_layer.update()

    aligned_bbox = legacy.world_bbox(legacy.current_product_objects())
    if aligned_bbox is None:
        raise RuntimeError('Mounted product became unmeasurable after alignment')
    aligned_minimum, aligned_maximum = aligned_bbox
    aligned_center = (aligned_minimum + aligned_maximum) * 0.5
    metrics.center_world = aligned_center
    metrics.bottom_world = float(aligned_minimum.z)
    scene = legacy.bpy.context.scene
    scene['awful_product_bottom_world'] = metrics.bottom_world
    return metrics


def install(legacy):
    """Install one owner-safe mount normalization wrapper before UI registration."""
    if getattr(legacy, '_awful_product_placement_installed', False):
        return

    original_mount_product = legacy.mount_product

    def mount_product(root_objects, auto_fit=True):
        metrics = original_mount_product(root_objects, auto_fit)
        return _align_mounted_geometry(legacy, metrics)

    legacy.float_motion_heights = float_motion_heights
    legacy.mount_product = mount_product
    legacy._awful_product_placement_installed = True
