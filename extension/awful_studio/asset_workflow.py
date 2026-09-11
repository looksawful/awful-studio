# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure HDRI workflow policy for AWFUL STUDIO.

No Blender import, filesystem mutation, or network access occurs here. The
Blender adapter is installed separately after the policy is covered by fast tests.
"""
from __future__ import annotations

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
