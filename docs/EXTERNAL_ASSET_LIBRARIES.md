# External environment and prop libraries

1. Acquire the desired pack from its provider and keep the provider license/readme beside the files.
2. Extract it outside the AWFUL STUDIO repository, for example `D:\Assets\3D\Quaternius`.
3. In Blender: Preferences > Add-ons > AWFUL STUDIO, set **External Asset Library** to that root.
4. Press **Register External Asset Library**. Registration is explicit and changes only Blender's user Asset Library preference.
5. Existing `.blend` files that contain marked assets can be browsed in Asset Browser. OBJ/FBX/glTF/GLB remain source exchange files and are imported when needed rather than copied into the Extension.

AWFUL never scans or registers a directory during Extension import/enable/startup. It never republishes third-party packs. The machine-readable catalog stores provenance and categories so future UI can discover compatible local packs without inventing download URLs.

The currently reviewed Downtown City MegaKit, Medieval Village MegaKit, Modular Sci-Fi MegaKit, Stylized Nature MegaKit and Sushi Restaurant Kit are recorded as CC0 because their own official pack pages identify those releases as CC0. Quaternius also publishes QAL v1.0 for assets released under that license; do not rewrite older pack-specific licensing based only on the current site-wide license page. Re-review the provider page before changing redistribution behavior.

Recommended root layout:

```
3D/
  Quaternius/
    DowntownCityMegaKit/
    MedievalVillageMegaKit/
    ModularSciFiMegaKit/
    StylizedNatureMegaKit/
    SushiRestaurantKit/
```

Keep third-party binaries out of Git. The integration is deliberately path-based so a large local library can live on a dedicated asset drive and survive Extension updates.
