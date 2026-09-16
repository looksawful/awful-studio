# Current bundled device previews

This directory is the runtime device bundle used by the AWFUL STUDIO Product workflow. The source-of-truth review gallery lives in `docs/screenshots/devices/current` on `main`.

## Current runtime assets

| Device | Stage | Runtime variant | Review gallery |
| --- | --- | --- | --- |
| iPhone 17 | `LOW_DRAFT` | `low_v29` | [`docs/screenshots/devices/current/iphone-17`](../../../../docs/screenshots/devices/current/iphone-17) |
| iPad Pro 11 M5 | `LOW_DRAFT` | `low_v6` | [`docs/screenshots/devices/current/ipad-pro-11`](../../../../docs/screenshots/devices/current/ipad-pro-11) |
| iPad Pro 13 M5 | `LOW_DRAFT` | `low_v6` | [`docs/screenshots/devices/current/ipad-pro-13`](../../../../docs/screenshots/devices/current/ipad-pro-13) |
| MacBook Pro 14 M5 | `RELEASE_CANDIDATE` | `low_v1_release` | [`docs/screenshots/devices/current/macbook-pro-14`](../../../../docs/screenshots/devices/current/macbook-pro-14) |

The stage and LOD are deliberately separate. A runtime `LOW` LOD does not promote a `LOW_DRAFT` or `RELEASE_CANDIDATE` asset to approved production LOW.

## Packaged Blender libraries

- `iphone_17_low_v29.blend`
- `ipad_pro_11_m5_low_v6.blend`
- `ipad_pro_13_m5_low_v6.blend`
- `macbook_pro_14_m5_low_v1_release.blend`

Each package contains one `AWFUL_DEVICE_*` entry collection, the device root hierarchy, packed image dependencies, and no diagnostic cameras or studio lights.
