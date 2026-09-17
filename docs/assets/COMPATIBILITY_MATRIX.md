# Studio equipment compatibility matrix

This matrix describes AWFUL runtime compatibility, not a claim that every combination existed historically in Sensetique.

| Support / fixture | D1 500 Air | Acute/D4 head | Dedolight | ARRI 300 Plus |
| --- | --- | --- | --- | --- |
| C-Stand / baby pin | via stand adapter | via stand adapter | 16 mm | 16 mm |
| Air-cushioned stand | supported | supported | supported | supported |
| Low stand | supported when load/height is valid | supported | supported | supported |
| Boom stand | supported with counterweight/load validation | supported with counterweight/load validation | supported | supported |
| Roller stand | supported | supported | supported | supported |

## Modifier compatibility

- Profoto D1 / Acute-D4: Magnum, Zoom, Softlight and RFi via the appropriate Profoto interface/speedring.
- Grifon and Fotokvant soft modifiers remain separate shells; mount adapter is an independent asset.
- Umbrellas use `MOUNT_UMBRELLA`, not `MOUNT_MODIFIER`.
- Dedolight and ARRI barndoor/gobo systems are modeled as their own accessory path and are not silently treated as Profoto modifiers.

## Runtime rule

Changing support, fixture or modifier replaces only that layer and preserves position, target and unrelated native Blender light properties.
