# SPDX-License-Identifier: GPL-3.0-or-later
"""HDRI workflow policy and Blender adapter for AWFUL STUDIO.

The pure section performs no Blender, filesystem, or network work. ``install``
receives those adapters explicitly and wires the reviewed bulk workflow before
Extension class registration.
"""
from __future__ import annotations

from pathlib import Path

try:
    from . import asset_provenance
except ImportError:  # fast-test import from the extension source directory
    import asset_provenance

HDRI_MEDIA_TYPE = 'image/vnd.radiance'
HDRI_PRESETS = frozenset({
    'FISH_HOEK', 'BLOUBERG', 'KLOPPENHEIM', 'BELFAST', 'ROGLAND',
})
PHYSICAL_SKY_PRESETS = frozenset({'NISHITA_DAY', 'NISHITA_SUNSET'})
FALLBACK_PRESET = 'NISHITA_DAY'


def reviewed_hdri_records() -> list[dict[str, object]]:
    """Return only active, remote-only, provenance-reviewed Radiance HDRIs."""
    records = []
    for record in asset_provenance.active_assets().values():
        if (record.get('distribution') == 'remote-only'
                and record.get('media_type') == HDRI_MEDIA_TYPE):
            records.append(dict(record))
    return records


def permission_state(*, blender_online: bool, awful_consent: bool) -> dict[str, object]:
    """Keep Blender's platform permission distinct from AWFUL's persistent consent."""
    if not blender_online:
        return {
            'code': 'BLENDER_ONLINE_ACCESS_OFF',
            'ready': False,
            'message': (
                'Blender Online Access is disabled. Enable Allow Online Access '
                'in Blender Preferences before downloading AWFUL HDRIs.'
            ),
        }
    if not awful_consent:
        return {
            'code': 'AWFUL_CONSENT_REQUIRED',
            'ready': False,
            'message': (
                'AWFUL network asset access is not confirmed. Enable '
                'Allow Network Assets in AWFUL STUDIO preferences first.'
            ),
        }
    return {
        'code': 'READY',
        'ready': True,
        'message': 'Network asset download is permitted.',
    }


def environment_resolution(*, selected_preset: str, asset_ready: bool) -> dict[str, object]:
    """Resolve an effective source while preserving the user's selected HDRI intent."""
    if selected_preset in PHYSICAL_SKY_PRESETS:
        return {
            'selected_intent': selected_preset,
            'effective_preset': selected_preset,
            'fallback': False,
        }
    if selected_preset in HDRI_PRESETS:
        return {
            'selected_intent': selected_preset,
            'effective_preset': selected_preset if asset_ready else FALLBACK_PRESET,
            'fallback': not asset_ready,
        }
    raise ValueError(f'Unknown environment intent: {selected_preset}')


def _asset_ready(legacy, cache, preset_id: str) -> bool:
    if preset_id in PHYSICAL_SKY_PRESETS:
        return True
    if preset_id not in HDRI_PRESETS:
        raise ValueError(f'Unknown environment intent: {preset_id}')
    asset_key = legacy.HDRI_PRESETS[preset_id]['asset']
    return bool(cache.read_valid(Path(legacy.hdri_asset_path(asset_key))))


def runtime_status(legacy, cache, scene) -> dict[str, object]:
    """Return compact Environment-panel status without causing network activity."""
    selected = str(scene.awful_studio.world_preset)
    if selected in PHYSICAL_SKY_PRESETS:
        return {'code': 'PHYSICAL_SKY', 'label': 'Physical Sky', 'icon': 'WORLD_DATA'}
    if _asset_ready(legacy, cache, selected):
        return {'code': 'READY', 'label': 'HDRI: Ready', 'icon': 'CHECKMARK'}
    prefs = cache.preferences()
    permission = permission_state(
        blender_online=bool(legacy.bpy.app.online_access),
        awful_consent=bool(prefs and prefs.allow_network_assets),
    )
    if not permission['ready']:
        label = ('HDRI: Blender Online Access Off'
                 if permission['code'] == 'BLENDER_ONLINE_ACCESS_OFF'
                 else 'HDRI: Network Consent Required')
        return {'code': permission['code'], 'label': label, 'icon': 'ERROR'}
    return {
        'code': 'MISSING_FALLBACK',
        'label': 'HDRI: Missing, Physical Sky fallback',
        'icon': 'INFO',
    }


def install(legacy, cache):
    """Install reviewed bulk-download/fallback UX without fetching at startup."""
    if getattr(legacy, '_awful_asset_workflow_installed', False):
        return

    original_environment_draw = legacy.AWFUL_PT_Environment.draw

    def resolve_environment_preset(scene, selected_preset):
        resolution = environment_resolution(
            selected_preset=str(selected_preset),
            asset_ready=_asset_ready(legacy, cache, str(selected_preset)),
        )
        return str(resolution['effective_preset'])

    def ensure_assets(force=False):
        results = {}
        for record in reviewed_hdri_records():
            destination = (
                cache.root()
                / str(record.get('cache_subdir', ''))
                / str(record['filename'])
            )
            results[str(record['asset_id'])] = cache.fetch(
                str(record['download_url']), destination, force=bool(force))
        return results

    def fetch_execute(self, context):
        prefs = cache.preferences()
        permission = permission_state(
            blender_online=bool(legacy.bpy.app.online_access),
            awful_consent=bool(prefs and prefs.allow_network_assets),
        )
        if not permission['ready']:
            self.report({'ERROR'}, str(permission['message']))
            return {'CANCELLED'}
        selected = str(context.scene.awful_studio.world_preset)
        try:
            result = ensure_assets(False)
            if not all(result.values()):
                self.report({'ERROR'}, cache.last_error())
                return {'CANCELLED'}
            legacy.refresh_world_images()
            legacy.apply_environment_preset(context.scene, selected, False)
        except (OSError, ValueError, RuntimeError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f'{len(result)} reviewed HDRIs Ready')
        return {'FINISHED'}

    class AWFUL_OT_OpenOnlinePreferences(legacy.bpy.types.Operator):
        bl_idname = 'awful.open_online_preferences'
        bl_label = 'Open Blender Online Access Preferences'
        bl_description = 'Open Blender Preferences where Allow Online Access can be enabled'

        def execute(self, context):
            try:
                context.preferences.active_section = 'SYSTEM'
            except Exception:
                pass
            if legacy.bpy.app.background:
                self.report({'INFO'}, 'Open Blender Preferences > System and enable Allow Online Access')
                return {'FINISHED'}
            try:
                legacy.bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            except Exception as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            return {'FINISHED'}

    def draw_environment(self, context):
        original_environment_draw(self, context)
        scene = context.scene
        selected = str(scene.awful_studio.world_preset)
        status = runtime_status(legacy, cache, scene)
        box = self.layout.box()
        box.label(text=str(status['label']), icon=str(status['icon']))
        if selected in HDRI_PRESETS:
            prefs = cache.preferences()
            if prefs is not None:
                box.prop(prefs, 'allow_network_assets', text='Allow Network Assets')
            box.operator('awful.fetch_assets_v4', text='Download All HDRIs', icon='IMPORT')
            if status['code'] == 'BLENDER_ONLINE_ACCESS_OFF':
                box.operator('awful.open_online_preferences', icon='PREFERENCES')

    legacy.resolve_environment_preset = resolve_environment_preset
    legacy.ensure_assets = ensure_assets
    legacy.AWFUL_OT_FetchAssets.bl_label = 'Download All HDRIs'
    legacy.AWFUL_OT_FetchAssets.bl_description = (
        'Download all five provenance-reviewed AWFUL HDRIs into the managed cache')
    legacy.AWFUL_OT_FetchAssets.execute = fetch_execute
    legacy.CLASSES = (*legacy.CLASSES, AWFUL_OT_OpenOnlinePreferences)
    legacy.AWFUL_PT_Environment.draw = draw_environment
    legacy._awful_asset_workflow_installed = True
