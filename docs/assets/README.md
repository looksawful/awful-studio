
# AWFUL STUDIO Asset Production Library

Canonical preparation package for all currently approved device, studio-equipment, furniture, prop and camera/lens assets.

- Registry: [`registry.json`](registry.json)
- Production order: [`PRODUCTION_ORDER.md`](PRODUCTION_ORDER.md)
- Source register: [`sources.md`](sources.md)
- Shared contracts: [`contracts/`](contracts/)
- System diagrams: [`diagrams/`](diagrams/)
- Individual dossiers: [`dossiers/`](dossiers/)

`production_ready=true` means documentation is sufficient to enter the next modeling gate. It never means the 3D asset is finished.

## Asset registry
| Asset | Category | Identity | Stage | Tier |
| --- | --- | --- | --- | --- |
| [Canon EOS 5D Mark IV](dossiers/canon_eos_5d_mark_iv.md) | `CAMERA` | `REFERENCE_STANDARD` | `SPEC_READY` | `HERO` |
| [iPad Pro 11 M5](dossiers/ipad_pro_11_m5.md) | `DEVICE_MOCKUP` | `PROJECT_VERIFIED` | `LOW_DRAFT` | `HERO` |
| [iPad Pro 13 M5](dossiers/ipad_pro_13_m5.md) | `DEVICE_MOCKUP` | `PROJECT_VERIFIED` | `LOW_DRAFT` | `HERO` |
| [iPhone 17](dossiers/iphone_17.md) | `DEVICE_MOCKUP` | `PROJECT_VERIFIED` | `LOW_DRAFT` | `HERO` |
| [MacBook Pro 14 M5](dossiers/macbook_pro_14_m5.md) | `DEVICE_MOCKUP` | `PROJECT_VERIFIED` | `RELEASE_CANDIDATE` | `HERO` |
| [Bar Stool, High](dossiers/bar_stool_high.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Bar Stool, Low](dossiers/bar_stool_low.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Chair, Wood + Metal](dossiers/chair_wood_metal.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Dining Chair, Wood](dossiers/dining_chair_wood.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Leather Sofa, 3-seat](dossiers/leather_sofa_3seat.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `HERO` |
| [Lounge Armchair, Fabric](dossiers/lounge_armchair_fabric.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `HERO` |
| [Lounge Armchair, Leather](dossiers/lounge_armchair_leather.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `HERO` |
| [Side Table, Round](dossiers/side_table_round.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Studio Table, Rectangular](dossiers/studio_table_rect.md) | `FURNITURE` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Canon EF 24-70mm f/2.8L II USM](dossiers/canon_ef_24_70_f28l_ii.md) | `LENS` | `REFERENCE_STANDARD` | `SPEC_READY` | `HERO` |
| [Avenger D200 Grip Head Reference](dossiers/avenger_d200_grip_head.md) | `LIGHT_ACCESSORY` | `REFERENCE_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Avenger D500 Extension Grip Arm Reference](dossiers/avenger_d500_grip_arm.md) | `LIGHT_ACCESSORY` | `REFERENCE_STANDARD` | `SPEC_READY` | `STANDARD` |
| [16 mm Baby Pin](dossiers/baby_pin_16mm.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Black Flag 60x90 cm](dossiers/black_flag_60x90.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Boom Counterweight 4 kg](dossiers/counterweight_4kg.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Diffusion Frame 120x120 cm](dossiers/diffusion_frame_120.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Gobo Frame 60x60 cm](dossiers/gobo_frame_60.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Studio Power Cable 5 m](dossiers/power_cable_5m.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Profoto RFi Speedring Reference](dossiers/profoto_rfi_speedring.md) | `LIGHT_ACCESSORY` | `REFERENCE_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Studio Sandbag 10 kg](dossiers/sandbag_10kg.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Flash Sync Cable 5 m](dossiers/sync_cable_5m.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Umbrella Holder](dossiers/umbrella_holder.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [White Reflector Card 100x150 cm](dossiers/white_reflector_100x150.md) | `LIGHT_ACCESSORY` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [ARRI 300 Plus](dossiers/arri_300_plus.md) | `LIGHT_FIXTURE` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Dedolight DLHM4-300](dossiers/dedolight_dlhm4_300.md) | `LIGHT_FIXTURE` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto Acute2 Generator](dossiers/profoto_acute2_generator.md) | `LIGHT_FIXTURE` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Profoto Acute/D4 Head](dossiers/profoto_acute_d4_head.md) | `LIGHT_FIXTURE` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto D1 500 Air](dossiers/profoto_d1_500_air.md) | `LIGHT_FIXTURE` | `HISTORICAL_CONFIRMED` | `MID` | `HERO` |
| [Fotokvant Evenly Stripbox 30x160 cm](dossiers/fotokvant_evenly_30x160.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Fotokvant U-101S Silver Umbrella](dossiers/fotokvant_u101s_silver.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Fotokvant U-104W Para White Umbrella](dossiers/fotokvant_u104w_para.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Grifon SB-FW95 Octabox](dossiers/grifon_sb_fw95.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Lumifor LUSL-18016 ULTRA Shoot-through Umbrella](dossiers/lumifor_lusl_18016.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `STANDARD` |
| [Profoto Magnum Reflector 100624](dossiers/profoto_magnum_100624.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `MID` | `HERO` |
| [Profoto RFi Softbox 3x4 ft / 90x120 cm 254704](dossiers/profoto_rfi_3x4_254704.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto RFi Softbox 5 ft Octa 254712](dossiers/profoto_rfi_octa_150_254712.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto Softlight Reflector Silver 100607](dossiers/profoto_softlight_silver_100607.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto Softlight Reflector White 100608](dossiers/profoto_softlight_white_100608.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Profoto Zoom Reflector 100785](dossiers/profoto_zoom_100785.md) | `LIGHT_MODIFIER` | `HISTORICAL_CONFIRMED` | `SPEC_READY` | `HERO` |
| [Air-cushioned Light Stand](dossiers/air_cushioned_light_stand.md) | `LIGHT_SUPPORT` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Avenger A2025F C-Stand Reference](dossiers/avenger_a2025f_cstand.md) | `LIGHT_SUPPORT` | `REFERENCE_STANDARD` | `MID` | `HERO` |
| [Studio Boom Stand](dossiers/boom_stand.md) | `LIGHT_SUPPORT` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Low Light Stand](dossiers/low_light_stand.md) | `LIGHT_SUPPORT` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Roller Studio Stand](dossiers/roller_stand.md) | `LIGHT_SUPPORT` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cone](dossiers/plaster_cone.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cube 300 mm](dossiers/plaster_cube_300.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cube 400 mm](dossiers/plaster_cube_400.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cube 500 mm](dossiers/plaster_cube_500.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cylinder, Low](dossiers/plaster_cylinder_low.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Cylinder, Tall](dossiers/plaster_cylinder_tall.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Rectangular Plinth, Low](dossiers/plaster_plinth_low.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Rectangular Plinth, Tall](dossiers/plaster_plinth_tall.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Round Pedestal, Low](dossiers/plaster_round_pedestal_low.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Round Pedestal, Tall](dossiers/plaster_round_pedestal_tall.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Sphere Ø300 mm](dossiers/plaster_sphere_300.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Sphere Ø400 mm](dossiers/plaster_sphere_400.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Plaster Sphere Ø500 mm](dossiers/plaster_sphere_500.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Wood Cube 300 mm](dossiers/wood_cube_300.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Wood Cube 400 mm](dossiers/wood_cube_400.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Wood Cube 500 mm](dossiers/wood_cube_500.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
| [Wood Cube 600 mm](dossiers/wood_cube_600.md) | `PROP` | `DESIGN_STANDARD` | `SPEC_READY` | `STANDARD` |
