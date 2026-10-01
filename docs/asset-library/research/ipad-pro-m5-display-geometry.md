# iPad Pro M5 display geometry and screen-glow validation

**Research date:** 2026-10-01
**Evidence class:** `VERIFIED` for Apple body/display specifications; `DERIVED` for physical display-envelope dimensions; runtime observations are repository evidence.

## Primary-source facts

Apple lists the following enclosure dimensions for both Wi‑Fi and Wi‑Fi + Cellular models:

| Variant | Enclosure (width × height × depth) | Display resolution / density | Portrait display rectangle |
| --- | ---: | ---: | ---: |
| iPad Pro 11-inch (M5) | `177.5 × 249.7 × 5.3 mm` | `1668 × 2420 px @ 264 ppi` | `1668 × 2420 px @ 2×` (`834 × 1210 pt`) |
| iPad Pro 13-inch (M5) | `215.5 × 281.6 × 5.1 mm` | `2064 × 2752 px @ 264 ppi` | `2064 × 2752 px @ 2×` (`1032 × 1376 pt`) |

The enclosure and display specifications come from Apple’s [11-inch M5 technical specifications](https://support.apple.com/en-us/125406) and [13-inch M5 technical specifications](https://support.apple.com/en-us/125407). Apple’s [HIG layout table](https://developer.apple.com/design/human-interface-guidelines/layout) supplies the portrait point/pixel orientation. Apple also states that the displays have rounded corners: the rectangular diagonal is 11.1 inches for the 11-inch model and 13 inches for the 13-inch model, while the actual viewable area is smaller. The [Apple Developer dimensional-drawing index](https://developer.apple.com/accessories/dimensional-drawings/) links the [11-inch M5 drawing](https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-11-inch-m5.pdf) and [13-inch M5 drawing](https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-13-inch-m5.pdf) for accessory clearances and cover-glass geometry.

## Derived display envelopes and repo comparison

Using `mm = pixels / 264 × 25.4` gives a nominal rectangular display envelope. This is a derivation from Apple’s rounded ppi value, not a claim that every corner pixel is viewable.

| Variant | Derived nominal envelope (width × height) | Repo `screen_mm` | Repo vs derived | Aspect-ratio check |
| --- | ---: | ---: | ---: | ---: |
| 11-inch | `160.482 × 232.833 mm` | `160.13 × 232.32 mm` | `−0.352 × −0.513 mm` (`<0.23%` each) | Repo `1.450821`; Apple pixels `1.450839` |
| 13-inch | `198.582 × 264.776 mm` | `199.14 × 265.19 mm` | `+0.558 × +0.414 mm` (`<0.29%` each) | Repo `1.331676`; Apple pixels `1.333333` (`−0.124%`) |

The repo’s body values in `assets/device_mockups/ipad_pro/generate_low_v6.py` match Apple’s published enclosure values. Its screen values are close to the derived nominal rectangle and should remain tagged as project/derived geometry until an exact Apple panel drawing exposes active-pixel edges. Preserve the portrait mapping as `[width, height]`; landscape is the same rectangle with the axes exchanged.

## Runtime screen-glow implications

- `assets/device_mockups/ipad_pro/runtime/v6/ipad_pro_{11,13}_m5_v6.asset.json` carries `screenGlow.width_mm/height_mm` as `[160.13, 232.32]` and `[199.14, 265.19]`. Validation should compare those fields against `SCREEN_CONTENT` in the same `[width, height]` order and accept the small physical-dimension difference above.
- The current source path is manifest-first: `preview/src/viewer-core.mjs:22` returns the manifest width/height, and `preview/src/model-viewer.mjs:275-281` constructs the `RectAreaLight` from that ordered pair, attaches it to `SCREEN_CONTENT`, and points it toward the screen. Check both variants and both `screen_on`/`screen_off` states; off must keep the glow intensity at zero.
- Fresh browser evidence in `evidence/ipad-continuation-20261001/browser.json` reports the corrected ordered values: 11-inch `width=0.16013, height=0.23232` and 13-inch `width=0.19914, height=0.26519`; both `screen_off` checks report zero glow intensity and no page errors.

## Sources

- [Apple Support — iPad Pro 11-inch (M5) Tech Specs](https://support.apple.com/en-us/125406)
- [Apple Support — iPad Pro 13-inch (M5) Tech Specs](https://support.apple.com/en-us/125407)
- [Apple Developer — Layout, iPadOS device screen dimensions](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Apple Developer — Download Device Dimensional Drawings](https://developer.apple.com/accessories/dimensional-drawings/)
- [Apple Developer — iPad Pro 11-inch (M5) dimensional drawing](https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-11-inch-m5.pdf)
- [Apple Developer — iPad Pro 13-inch (M5) dimensional drawing](https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-13-inch-m5.pdf)
