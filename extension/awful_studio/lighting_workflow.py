# SPDX-License-Identifier: GPL-3.0-or-later
"""Production-oriented shortcuts over AWFUL's canonical lighting presets."""
from __future__ import annotations

PRODUCTION_LOOKS = {
    'PRODUCT': 'COMMERCIAL_3LIGHT',
    'SOFT_BEAUTY': 'TOP_SOFT_PACKSHOT',
    'HARD_FLASH': 'DIRECT_FLASH',
    'EDGE': 'DUAL_STRIP_HERO',
    'ACCENT': 'DUAL_COLOR_STRIP',
    'GOBO': 'HARD_GOBO',
    'WINDOW': 'WINDOW_BALANCED',
    'GLASS': 'BACKLIT_GLASS',
}

PRODUCTION_LOOK_LABELS = {
    'PRODUCT': 'Product',
    'SOFT_BEAUTY': 'Soft',
    'HARD_FLASH': 'Flash',
    'EDGE': 'Edge',
    'ACCENT': 'Accent',
    'GOBO': 'Gobo',
    'WINDOW': 'Window',
    'GLASS': 'Glass',
}


def apply_look(legacy, scene, look: str) -> str:
    try:
        preset_id = PRODUCTION_LOOKS[look]
    except KeyError as exc:
        raise ValueError(f'Unknown production lighting look: {look}') from exc
    if preset_id not in legacy.LIGHTING_PRESETS:
        raise RuntimeError(
            f'Production look {look} targets missing preset {preset_id}')
    legacy.apply_lighting_preset(
        scene,
        preset_id,
        False,
        True,
    )
    return preset_id


def install(legacy):
    if getattr(legacy, '_awful_lighting_workflow_installed', False):
        return

    missing = [
        preset_id for preset_id in PRODUCTION_LOOKS.values()
        if preset_id not in legacy.LIGHTING_PRESETS
    ]
    if missing:
        raise RuntimeError(
            'Production lighting workflow references missing presets: '
            + ', '.join(missing)
        )

    class AWFUL_OT_ApplyProductionLook(legacy.bpy.types.Operator):
        bl_idname = 'awful.apply_production_look'
        bl_label = 'Apply Production Lighting Look'
        bl_options = {'REGISTER', 'UNDO'}

        @classmethod
        def poll(cls, context):
            return (
                context.scene is not None
                and legacy.REG.object('CYC') is not None
            )

        def execute(self, context):
            try:
                preset_id = apply_look(
                    legacy,
                    context.scene,
                    self.look,
                )
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            self.report(
                {'INFO'},
                f'{PRODUCTION_LOOK_LABELS[self.look]}: {preset_id}',
            )
            return {'FINISHED'}

    AWFUL_OT_ApplyProductionLook.__annotations__['look'] = legacy.EnumProperty(
        name='Look',
        items=[
            (key, PRODUCTION_LOOK_LABELS[key], '')
            for key in PRODUCTION_LOOKS
        ],
        default='PRODUCT',
    )

    original_draw = legacy.AWFUL_PT_Lighting.draw

    def draw_lighting(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Production Looks')
        keys = tuple(PRODUCTION_LOOKS)
        for start in range(0, len(keys), 4):
            row = box.row(align=True)
            for key in keys[start:start + 4]:
                op = row.operator(
                    'awful.apply_production_look',
                    text=PRODUCTION_LOOK_LABELS[key],
                )
                op.look = key
        box.label(
            text='Advanced preset remains authoritative below.',
            icon='INFO',
        )
        original_draw(self, context)

    legacy.AWFUL_OT_ApplyProductionLook = AWFUL_OT_ApplyProductionLook
    legacy.AWFUL_PT_Lighting.draw = draw_lighting
    legacy.CLASSES = tuple(legacy.CLASSES) + (
        AWFUL_OT_ApplyProductionLook,
    )
    legacy.apply_production_lighting_look = lambda scene, look: apply_look(
        legacy,
        scene,
        look,
    )
    legacy._awful_lighting_workflow_installed = True
