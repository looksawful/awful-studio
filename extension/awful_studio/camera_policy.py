# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe product-bounds camera framing for Alpha 0.0.16.

The math in this module is deliberately Blender-independent so it can be tested
without importing bpy. `install()` adapts the retained v4 camera function at
runtime and uses Blender's actual camera view frame, which already accounts for
lens, sensor fit, render aspect and camera shift.
"""
import math

MIN_CAMERA_DISTANCE = 2.2
_MAX_SEARCH_DISTANCE = 1_000_000.0

CAMERA_VIEW_PRESETS = {
    'HERO_85': {'label': 'Hero - 85 mm', 'lens': 85.0, 'margin': 1.24, 'yaw_deg': 0.0, 'pitch_deg': 4.0},
    'THREE_QUARTER_LEFT_85': {'label': '3/4 Left - 85 mm', 'lens': 85.0, 'margin': 1.28, 'yaw_deg': -28.0, 'pitch_deg': 5.0},
    'THREE_QUARTER_RIGHT_85': {'label': '3/4 Right - 85 mm', 'lens': 85.0, 'margin': 1.28, 'yaw_deg': 28.0, 'pitch_deg': 5.0},
    'SIDE_85': {'label': 'Side - 85 mm', 'lens': 85.0, 'margin': 1.30, 'yaw_deg': 90.0, 'pitch_deg': 2.0},
    'WIDE_50': {'label': 'Wide - 50 mm', 'lens': 50.0, 'margin': 1.38, 'yaw_deg': 0.0, 'pitch_deg': 3.0},
    'DETAIL_120': {'label': 'Detail - 120 mm', 'lens': 120.0, 'margin': 1.10, 'yaw_deg': -18.0, 'pitch_deg': 4.0},
    'TOP_THREE_QUARTER_85': {'label': 'Top 3/4 - 85 mm', 'lens': 85.0, 'margin': 1.32, 'yaw_deg': -28.0, 'pitch_deg': 24.0},
}


def camera_view_spec(key: str) -> dict:
    try:
        return dict(CAMERA_VIEW_PRESETS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL camera view: {key}') from exc


def frame_tangents(frame):
    """Return conservative horizontal/vertical half-frustum tangents.

    Blender's Camera.view_frame(scene=...) returns camera-local frame corners.
    Using the smaller left/right and top/bottom allowance keeps shifted cameras
    safe instead of assuming a symmetric sensor gate.
    """
    horizontal_negative = []
    horizontal_positive = []
    vertical_negative = []
    vertical_positive = []
    for corner in frame:
        depth = -float(corner.z)
        if depth <= 1e-9:
            continue
        x = float(corner.x) / depth
        y = float(corner.y) / depth
        if x < 0:
            horizontal_negative.append(-x)
        elif x > 0:
            horizontal_positive.append(x)
        if y < 0:
            vertical_negative.append(-y)
        elif y > 0:
            vertical_positive.append(y)
    if not all((horizontal_negative, horizontal_positive,
                vertical_negative, vertical_positive)):
        raise RuntimeError('Camera view frame has no usable symmetric framing area')
    tan_x = min(max(horizontal_negative), max(horizontal_positive))
    tan_y = min(max(vertical_negative), max(vertical_positive))
    if tan_x <= 1e-9 or tan_y <= 1e-9:
        raise RuntimeError('Camera field of view is too narrow for safe framing')
    return tan_x, tan_y


def _corners(width, depth, height):
    half_w = max(float(width), 1e-9) * 0.5
    half_d = max(float(depth), 1e-9) * 0.5
    half_h = max(float(height), 1e-9) * 0.5
    for x in (-half_w, half_w):
        for y in (-half_d, half_d):
            for z in (-half_h, half_h):
                yield x, y, z


def bounds_fit(width, depth, height, distance, height_offset,
               tan_half_x, tan_half_y, margin=1.0):
    """Return whether every axis-aligned product bound corner fits the frustum.

    The camera is placed at (0, -distance, height_offset) and tracks the product
    center. The test therefore includes the vertical tilt and product depth
    rather than treating the product as a flat width/height card.
    """
    distance = float(distance)
    height_offset = float(height_offset)
    margin = max(float(margin), 1.0)
    tan_x = float(tan_half_x) / margin
    tan_y = float(tan_half_y) / margin
    if distance <= 0 or tan_x <= 1e-9 or tan_y <= 1e-9:
        return False

    length = math.hypot(distance, height_offset)
    if length <= 1e-9:
        return False
    forward_y = distance / length
    forward_z = -height_offset / length
    up_y = height_offset / length
    up_z = distance / length

    for x, y, z in _corners(width, depth, height):
        rel_y = y + distance
        rel_z = z - height_offset
        camera_depth = forward_y * rel_y + forward_z * rel_z
        if camera_depth <= 1e-6:
            return False
        camera_vertical = up_y * rel_y + up_z * rel_z
        if abs(x) / camera_depth > tan_x + 1e-12:
            return False
        if abs(camera_vertical) / camera_depth > tan_y + 1e-12:
            return False
    return True


def required_distance_for_bounds(width, depth, height, tan_half_x, tan_half_y,
                                 margin=1.32, height_offset=0.0):
    """Find the minimum safe target-to-camera distance by monotonic bisection."""
    dims = tuple(max(float(value), 1e-6) for value in (width, depth, height))
    margin = max(float(margin), 1.0)
    tan_x = float(tan_half_x)
    tan_y = float(tan_half_y)
    if tan_x <= 1e-9 or tan_y <= 1e-9:
        raise ValueError('Camera frustum tangents must be positive')

    lower = max(1e-3, dims[1] * 0.5 + 1e-3)
    upper = max(MIN_CAMERA_DISTANCE, max(dims), lower * 1.25)
    while not bounds_fit(*dims, upper, height_offset, tan_x, tan_y, margin):
        upper *= 2.0
        if upper > _MAX_SEARCH_DISTANCE:
            raise RuntimeError('Unable to find a safe camera distance for product bounds')

    for _ in range(64):
        middle = (lower + upper) * 0.5
        if bounds_fit(*dims, middle, height_offset, tan_x, tan_y, margin):
            upper = middle
        else:
            lower = middle
    return max(MIN_CAMERA_DISTANCE, upper)


def install(legacy):
    """Install bounds framing and deterministic still-view workflow once."""
    if getattr(legacy, '_awful_camera_policy_installed', False):
        return

    updating_view = False

    def compute_camera_base_pose(scene, camera, metrics, lens=85.0, margin=1.32):
        camera.data.lens = float(lens)
        legacy.bpy.context.view_layer.update()
        tan_x, tan_y = frame_tangents(camera.data.view_frame(scene=scene))
        height_offset = float(metrics.height) * 0.08
        distance = required_distance_for_bounds(
            metrics.width, metrics.depth, metrics.height,
            tan_x, tan_y, margin, height_offset,
        )
        scene['awful_camera_base_distance'] = float(distance)
        scene['awful_camera_base_height_offset'] = float(height_offset)
        scene['awful_camera_base_lens'] = float(lens)
        scene['awful_camera_margin'] = float(margin)
        return distance, height_offset

    def apply_camera_view(scene, key):
        nonlocal updating_view
        spec = camera_view_spec(key)
        yaw = legacy.REG.require_object('CAMERA_YAW')
        pitch = legacy.REG.require_object('CAMERA_PITCH')
        dolly = legacy.REG.require_object('CAMERA_DOLLY')
        follower = legacy.REG.require_object('CAMERA_PATH_FOLLOW')
        camera = legacy.REG.require_object('CAMERA')
        for obj in (yaw, pitch, dolly, follower):
            legacy.clear_animation(obj)
        legacy.clear_animation(camera.data)
        legacy.set_camera_source(False)
        scene.awful_studio.camera_motion = 'STATIC'
        legacy.apply_camera_base_pose(
            scene,
            float(spec['lens']),
            float(spec['margin']),
        )
        yaw.rotation_euler[2] = math.radians(float(spec['yaw_deg']))
        pitch.rotation_euler[0] = math.radians(float(spec['pitch_deg']))
        legacy.bpy.context.view_layer.update()
        if getattr(scene.awful_studio, 'camera_view', None) != key:
            updating_view = True
            try:
                scene.awful_studio.camera_view = key
            finally:
                updating_view = False

    def on_camera_view(self, context):
        if updating_view:
            return
        scene = getattr(context, 'scene', None)
        if scene is None or legacy.REG.object('CYC') is None:
            return
        apply_camera_view(scene, self.camera_view)

    annotations = legacy.AWFUL_StudioSettings.__annotations__
    annotations['camera_view'] = legacy.EnumProperty(
        name='Still View',
        items=[
            (key, spec['label'], '')
            for key, spec in CAMERA_VIEW_PRESETS.items()
        ],
        default='HERO_85',
        update=on_camera_view,
    )

    original_draw = legacy.AWFUL_PT_Camera.draw

    def draw_camera(self, context):
        box = self.layout.box()
        box.label(text='Still View')
        box.prop(context.scene.awful_studio, 'camera_view', text='')
        original_draw(self, context)

    legacy.AWFUL_PT_Camera.draw = draw_camera
    legacy.compute_camera_base_pose = compute_camera_base_pose
    legacy.apply_camera_view = apply_camera_view
    legacy._awful_camera_policy_installed = True
