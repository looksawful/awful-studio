from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "assets"
DOSSIERS = DOCS / "dossiers"
CONTRACTS = DOCS / "contracts"
DIAGRAMS = DOCS / "diagrams"
SCHEMA_VERSION = 1

SOURCES = {
    "awful_design_standard": ("INTERNAL_DESIGN_STANDARD", "docs/assets/contracts/GENERAL_ASSET_CONTRACT.md", "Canonical AWFUL production standard for representative and parametric assets."),
    "sensetique_current": ("HISTORICAL_INVENTORY", "https://www.looksawful.ru/work/sensetique/", "Confirms Sensetique equipment families; manufacturer data controls technical geometry."),
    "profoto_d1_manual": ("MANUFACTURER_MANUAL", "https://www.profoto.com/globalassets/support/user-guides/discontinued-products/d1/profoto-d1-user-guide_en.pdf", "D1 dimensions, controls and construction."),
    "profoto_acute_d4_manual": ("MANUFACTURER_MANUAL", "https://www.profoto.com/globalassets/support/user-guides/discontinued-products/acuted4-head/profoto-acute-d4-head-user-guide_en.pdf", "Acute/D4 head dimensions and construction."),
    "profoto_acute2_manual": ("MANUFACTURER_MANUAL", "https://www.profoto.com/globalassets/support/user-guides/discontinued-products/acute2/profoto-acute2-user-guide.pdf", "Acute2 generator dimensions and controls."),
    "profoto_magnum_sheet": ("MANUFACTURER_PRODUCT_SHEET", "https://cvp.com/pdf/Profoto-189_LST%20Magnum%20Reflector%20Product%20Sheet.pdf", "Magnum 100624 dimensions and zoom positions."),
    "profoto_zoom_sheet": ("MANUFACTURER_PRODUCT_SHEET", "https://cvp.com/pdf/Profoto-197_LST%20Zoom%20Reflector%20Product%20Sheet.pdf", "Zoom 100785 dimensions and profile."),
    "profoto_softlight_silver": ("MANUFACTURER_PRODUCT_PAGE", "https://www.profoto.com/de/de/shop/products/light-shaping-tools/beauty-dishes/softlight-reflector-silver/", "Softlight Silver 100607 product data."),
    "profoto_softlight_white": ("MANUFACTURER_PRODUCT_PAGE", "https://www.profoto.com/int/en/shop/products/light-shaping-tools/beauty-dishes/softlight-reflector-white2/", "Softlight White 100608 product data."),
}
SOURCES.update({
    "profoto_rfi_5_octa": ("MANUFACTURER_PRODUCT_PAGE", "https://www.profoto.com/int/en/shop/products/light-shaping-tools/softboxes/rfi-softbox-5-octa-variant/", "RFi 5 ft Octa 254712 family data."),
    "profoto_rfi_3x4": ("MANUFACTURER_PRODUCT_PAGE", "https://profoto.com/int/en/shop/products/light-shaping-tools/softboxes/rfi-softbox-3x4-90x120cm/", "RFi 3x4 ft / 90x120 cm product data."),
    "profoto_rfi_system": ("MANUFACTURER_SYSTEM_PAGE", "https://www.profoto.com/nl/en/still-photography/experience/softboxes", "RFi speedring and modifier-system compatibility."),
    "grifon_sb_fw95": ("MANUFACTURER_CATALOG", "https://foto-grifon.ru/magazin/folder/05-3-softboksy-i-oktaboksy-dlya-studiynykh-vspyshek", "SB-FW95 95 cm octabox construction."),
    "fotokvant_evenly": ("SPECIALIST_PRODUCT_GUIDE", "https://fotogora.ru/rukovodstvo-po-softboksam-fotokvant-anatomiya-instrumentov-formirovaniya-sveta/", "Evenly 30x160 cm stripbox family."),
    "fotokvant_u104w": ("SPECIALIST_PRODUCT_PAGE", "https://photogora.ru/light_mod/umbrella/fotokvant-u-104w-para-parabolicheskiy-glubokiy-zont-104-sm-belyy-na-otrazhenie/", "U-104W 104 cm white reflective umbrella."),
    "fotokvant_u101s": ("SPECIALIST_PRODUCT_PAGE", "https://photogora.ru/light_mod/umbrella/", "U-101S 101 cm silver umbrella family."),
    "lumifor_18016": ("HISTORICAL_PLUS_PRODUCT_ID", "https://www.looksawful.ru/work/sensetique/", "LUSL-18016 ULTRA 180 cm translucent umbrella, 16 ribs."),
    "avenger_a2025f": ("MANUFACTURER_PRODUCT_PAGE", "https://www.manfrotto.com/global-en/c-stand-25-a2025f/", "A2025F fixed-base dimensions and tube standards."),
    "avenger_d200": ("MANUFACTURER_PRODUCT_PAGE", "https://www.manfrotto.com/global-en/grip-head-2-1-2-d200/", "D200 grip-head geometry and 16 mm interface."),
    "avenger_d500": ("MANUFACTURER_PRODUCT_PAGE", "https://www.manfrotto.com/global-uk/20-extension-grip-arm-d500/", "D500 51 cm extension arm geometry."),
})
SOURCES.update({
    "dedolight_dlhm4": ("MANUFACTURER_SPECIFICATION", "https://www.markertek.com/Attachments/Specifications/DEDOLIGHT/DEDO-DLH4-Specifications.pdf", "DLHM4 optical/electrical specification."),
    "arri_300_plus": ("MANUFACTURER_PRODUCT_PAGE", "https://www.arri.com/en/lighting/daylight-tungsten/tungsten/arri-junior/arri-300-plus", "ARRI 300 Plus dimensions and Fresnel data."),
    "canon_5d4": ("MANUFACTURER_SPECIFICATION", "https://www.usa.canon.com/support/p/eos-5d-mark-iv", "EOS 5D Mark IV body specification; representative production reference, not historical proof."),
    "canon_2470_ii": ("MANUFACTURER_SPECIFICATION", "https://www.canon.de/store/canon-ef-24-70mm-f-2-8l-ii-usm-objektiv/5175B005/", "EF 24-70mm f/2.8L II USM dimensions and controls."),
    "iphone17_current": ("PROJECT_VERIFIED_SOURCE", "assets/device_mockups/iphone_17/README.md", "Current iPhone 17 geometry and runtime contract."),
    "ipad_current": ("PROJECT_VERIFIED_SOURCE", "assets/device_mockups/ipad_pro/generate_blockout.py", "Current iPad Pro 11/13 M5 dimensional contract."),
    "macbook_current": ("PROJECT_VERIFIED_SOURCE", "assets/device_mockups/macbook_pro_14/README.md", "Current MacBook Pro 14 M5 release-candidate geometry."),
})

ASSETS: list[dict] = []

def d(value, confidence="DESIGN_STANDARD"):
    return {"value": value, "confidence": confidence}

def add(asset_id, name, category, identity, tier, stage, dimensions, sources, components, materials,
        variants=None, articulation=None, mounts=None, notes=None, runtime=None):
    ASSETS.append({
        "id": asset_id, "name": name, "category": category, "identity_class": identity,
        "tier": tier, "stage": stage, "dimensions": dimensions, "source_refs": sources,
        "components": components, "materials": materials, "variants": variants or ["canonical"],
        "articulation": articulation or ["static"], "mounts": mounts or ["FLOOR_CONTACT"],
        "notes": notes or [], "runtime": runtime or {"lod": ["LOD0", "LOD1", "LOD2"], "collision": "simple_proxy", "shipping": "GLB"},
        "production_ready": True,
    })# Devices
add("iphone_17", "iPhone 17", "DEVICE_MOCKUP", "PROJECT_VERIFIED", "HERO", "LOW_V15",
    {"body_mm": d([71.5,149.6,7.95],"VERIFIED")}, ["iphone17_current"],
    ["unibody","display_stack","dynamic_island","front_camera","rear_camera_system","buttons","ports","logo"],
    ["anodized_aluminum","display_glass","optical_glass","matte_black","decal"], ["Space Black","Silver"], mounts=["SCREEN_PLANE","FLOOR_CONTACT"])
add("ipad_pro_11_m5", "iPad Pro 11 M5", "DEVICE_MOCKUP", "PROJECT_VERIFIED", "HERO", "RELEASE_CANDIDATE",
    {"body_mm": d([177.5,249.7,5.3],"VERIFIED"),"screen_mm": d([160.13,232.32],"PROJECT_VERIFIED")}, ["ipad_current"],
    ["unibody","display_stack","camera_housing","rear_camera","flash","lidar","front_camera","side_controls","smart_connector"],
    ["anodized_aluminum","display_glass","optical_glass","matte_black","decal"], ["Space Black","Silver"], mounts=["SCREEN_PLANE","FLOOR_CONTACT"])
add("ipad_pro_13_m5", "iPad Pro 13 M5", "DEVICE_MOCKUP", "PROJECT_VERIFIED", "HERO", "RELEASE_CANDIDATE",
    {"body_mm": d([215.5,281.6,5.1],"VERIFIED"),"screen_mm": d([199.14,265.19],"PROJECT_VERIFIED")}, ["ipad_current"],
    ["unibody","display_stack","camera_housing","rear_camera","flash","lidar","front_camera","side_controls","smart_connector"],
    ["anodized_aluminum","display_glass","optical_glass","matte_black","decal"], ["Space Black","Silver"], mounts=["SCREEN_PLANE","FLOOR_CONTACT"])
add("macbook_pro_14_m5", "MacBook Pro 14 M5", "DEVICE_MOCKUP", "PROJECT_VERIFIED", "HERO", "RELEASE_CANDIDATE",
    {"closed_mm": d([312.6,221.2,15.5],"VERIFIED"),"lid_mm": d([312,212,4.7],"PROJECT_VERIFIED")}, ["macbook_current"],
    ["base_unibody","lid_unibody","hinge","display_stack","keyboard","trackpad","speaker_fields","touch_id","ports","feet","logo"],
    ["anodized_aluminum","display_glass","keycap_polymer","trackpad_glass","optical_glass","rubber","decal"], ["Space Black","Silver"],
    ["lid_hinge: reviewed preset 102deg"], ["CTRL_HINGE","SCREEN_PLANE","FLOOR_CONTACT"])
# Historically confirmed fixtures and generators
add("profoto_d1_500_air","Profoto D1 500 Air","LIGHT_FIXTURE","HISTORICAL_CONFIRMED","HERO","MID",
    {"body_mm":d([300,130],"VERIFIED"),"height_with_adapter_mm":d(170,"VERIFIED"),"mass_kg":d(2.43,"VERIFIED")}, ["sensetique_current","profoto_d1_manual"],
    ["cylindrical_body","front_rings","frosted_glass","flash_tube","modeling_lamp","rear_control_panel","vents","handle_yoke","stand_adapter","umbrella_tube","sync_ac_fuse"],
    ["black_polymer","powder_coated_metal","frosted_glass","clear_glass","rubber","printed_decals"], articulation=["fixture_tilt"], mounts=["MOUNT_SUPPORT","MOUNT_MODIFIER","MOUNT_UMBRELLA","EMITTER_ORIGIN","LIGHT_TARGET"])
add("profoto_acute_d4_head","Profoto Acute/D4 Head","LIGHT_FIXTURE","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"envelope_mm":d([100,100,220],"VERIFIED"),"mass_kg":d(1.55,"VERIFIED"),"cable_m":d(3,"VERIFIED")}, ["sensetique_current","profoto_acute_d4_manual"],
    ["head_body","reflector_collar","glass_cover","flash_tube","modeling_lamp","power_cable","stand_adapter","umbrella_holder"],
    ["black_polymer","painted_metal","frosted_uv_glass","clear_glass","rubber","cable_jacket"], articulation=["fixture_tilt"], mounts=["MOUNT_SUPPORT","MOUNT_MODIFIER","MOUNT_UMBRELLA","EMITTER_ORIGIN"])
add("profoto_acute2_generator","Profoto Acute2 Generator","LIGHT_FIXTURE","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"1200_mm":d([220,190,130],"VERIFIED"),"2400_mm":d([300,190,130],"VERIFIED"),"mass_kg":d({"1200":4.1,"2400":5.9},"VERIFIED")}, ["sensetique_current","profoto_acute2_manual"],
    ["generator_shell","carry_handle","front_controls","flash_sockets","mains_socket","sync_input","slave_sensor","feet","labels"],
    ["painted_sheet_metal","black_polymer","rubber","screen_print_decals"], ["1200Ws","2400Ws"], mounts=["FLOOR_CONTACT","CABLE_PORT_A","CABLE_PORT_B"])
add("dedolight_dlhm4_300","Dedolight DLHM4-300","LIGHT_FIXTURE","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"envelope_mm":d([171,132,174],"SECONDARY_VERIFIED"),"mass_kg":d(1.02,"VERIFIED"),"power_w":d(150,"VERIFIED")}, ["sensetique_current","dedolight_dlhm4"],
    ["focus_head","aspheric_optics","barn_door_receiver","focus_mechanism","yoke","power_electronics","cable","16mm_mount"],
    ["black_cast_metal","anodized_metal","optical_glass","heat_resistant_polymer","rubber_cable"], articulation=["focus: 4.5-48deg","fixture_tilt"], mounts=["MOUNT_SUPPORT","LIGHT_TARGET","EMITTER_ORIGIN"])
add("arri_300_plus","ARRI 300 Plus","LIGHT_FIXTURE","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"with_pin_mm":d([187,160,254],"VERIFIED"),"body_mm":d([187,160,209],"VERIFIED"),"lens_diameter_mm":d(80,"VERIFIED"),"mass_kg":d(2,"VERIFIED")}, ["sensetique_current","arri_300_plus"],
    ["aluminum_housing","fresnel","lamp_holder","focus_slide","ventilation","yoke","16mm_pin","barndoor_receiver","cable"],
    ["painted_aluminum","optical_glass","stainless_fasteners","heat_resistant_polymer","rubber_cable"], ["blue/silver","black"], ["focus: 14-53deg","fixture_tilt"], ["MOUNT_SUPPORT","LIGHT_TARGET","EMITTER_ORIGIN"])

# Reflectors and soft modifiers
add("profoto_magnum_100624","Profoto Magnum Reflector 100624","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","MID",
    {"diameter_mm":d(345,"VERIFIED"),"depth_mm":d(265,"VERIFIED"),"mass_kg":d(0.8,"VERIFIED")}, ["sensetique_current","profoto_magnum_sheet"],
    ["curved_bowl","black_outer_shell","silver_inner_reflector","ribbed_collar","front_rim","label_zone"], ["matte_black_coating","high_reflectance_silver","aluminum_rim","printed_label"], articulation=["zoom_position: 4-10"], mounts=["MOUNT_MODIFIER"])
add("profoto_zoom_100785","Profoto Zoom Reflector 100785","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"diameter_mm":d(193,"VERIFIED"),"depth_mm":d(180,"VERIFIED"),"mass_kg":d(0.3,"VERIFIED")}, ["sensetique_current","profoto_zoom_sheet"],
    ["faceted_reflector_bowl","zoom_collar","front_rim","scale_marks","locking_interface"], ["textured_silver_reflector","black_polymer","anodized_aluminum","printed_scale"], articulation=["zoom_position: 4-10"], mounts=["MOUNT_MODIFIER"])
add("profoto_softlight_silver_100607","Profoto Softlight Reflector Silver 100607","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"front_diameter_mm":d(525,"VERIFIED"),"depth_mm":d(190,"SHARED_GEOMETRY_VERIFIED"),"mass_kg":d(1.25,"VERIFIED")}, ["sensetique_current","profoto_softlight_silver"],
    ["shallow_dish","central_deflector_mount","rubber_collar","front_rim"], ["painted_outer_metal","silver_reflective_inner","rubber_collar","aluminum_fasteners"], ["silver"], mounts=["MOUNT_MODIFIER"])
add("profoto_softlight_white_100608","Profoto Softlight Reflector White 100608","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"front_diameter_mm":d(525,"VERIFIED"),"depth_mm":d(190,"VERIFIED"),"mass_kg":d(1.25,"VERIFIED")}, ["sensetique_current","profoto_softlight_white"],
    ["shallow_dish","central_deflector_mount","rubber_collar","front_rim"], ["painted_outer_metal","matte_white_inner","rubber_collar","aluminum_fasteners"], ["white"], mounts=["MOUNT_MODIFIER"])
add("grifon_sb_fw95","Grifon SB-FW95 Octabox","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"front_diameter_mm":d(950,"VERIFIED"),"rod_count":d(8,"VERIFIED")}, ["sensetique_current","grifon_sb_fw95"],
    ["8_rod_shell","outer_black_fabric","silver_lining","inner_diffuser","front_diffuser","speedring_interface"], ["black_nylon","silver_reflective_textile","diffusion_textile","spring_steel_rods"], ["open","collapsed"], mounts=["MOUNT_MODIFIER"])
add("profoto_rfi_octa_150_254712","Profoto RFi Softbox 5 ft Octa 254712","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"front_diameter_mm":d(1500,"VERIFIED"),"depth_mm":d(470,"VERIFIED"),"rod_count":d(8,"VERIFIED")}, ["sensetique_current","profoto_rfi_5_octa","profoto_rfi_system"],
    ["octagonal_shell","8_rods","speedring_receiver","inner_diffuser","front_diffuser","silver_lining"], ["black_textile","silver_textile","diffusion_textile","spring_steel"], ["open","collapsed"], mounts=["MOUNT_MODIFIER"])
add("profoto_rfi_3x4_254704","Profoto RFi Softbox 3x4 ft / 90x120 cm 254704","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","HERO","SPEC_READY",
    {"front_mm":d([900,1200],"VERIFIED")}, ["sensetique_current","profoto_rfi_3x4","profoto_rfi_system"],
    ["rectangular_shell","4_rods","speedring_receiver","inner_diffuser","front_diffuser","silver_lining"], ["black_textile","silver_textile","diffusion_textile","spring_steel"], ["open","collapsed"], mounts=["MOUNT_MODIFIER"])
add("fotokvant_evenly_30x160","Fotokvant Evenly Stripbox 30x160 cm","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"front_mm":d([300,1600],"VERIFIED")}, ["sensetique_current","fotokvant_evenly"],
    ["strip_shell","rods","speedring_receiver","inner_diffuser","front_diffuser","silver_lining"], ["black_textile","silver_textile","diffusion_textile","spring_steel"], ["open","collapsed"], mounts=["MOUNT_MODIFIER"])
add("fotokvant_u104w_para","Fotokvant U-104W Para White Umbrella","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"diameter_mm":d(1040,"VERIFIED"),"mass_kg":d(0.4,"VERIFIED")}, ["sensetique_current","fotokvant_u104w"],
    ["central_shaft","fiberglass_ribs","white_reflective_canopy","runner","tips"], ["metal_shaft","fiberglass","white_textile","black_trim"], ["open","collapsed"], mounts=["MOUNT_UMBRELLA"])
add("fotokvant_u101s_silver","Fotokvant U-101S Silver Umbrella","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"diameter_mm":d(1010,"VERIFIED")}, ["sensetique_current","fotokvant_u101s"],
    ["central_shaft","ribs","silver_canopy","black_outer_canopy","runner","tips"], ["metal_shaft","fiberglass","silver_textile","black_textile"], ["open","collapsed"], mounts=["MOUNT_UMBRELLA"])
add("lumifor_lusl_18016","Lumifor LUSL-18016 ULTRA Shoot-through Umbrella","LIGHT_MODIFIER","HISTORICAL_CONFIRMED","STANDARD","SPEC_READY",
    {"diameter_mm":d(1800,"VERIFIED"),"rib_count":d(16,"VERIFIED")}, ["sensetique_current","lumifor_18016"],
    ["central_shaft","16_ribs","translucent_canopy","runner","tips"], ["metal_shaft","fiberglass","translucent_textile"], ["open","collapsed"], mounts=["MOUNT_UMBRELLA"])
# Support, grip and studio accessories
add("avenger_a2025f_cstand","Avenger A2025F C-Stand Reference","LIGHT_SUPPORT","REFERENCE_STANDARD","HERO","MID",
    {"footprint_mm":d([941,911],"PROJECT_VERIFIED"),"riser_diameters_mm":d([35,30,25],"VERIFIED"),"leg_diameter_mm":d(25,"VERIFIED")}, ["avenger_a2025f"],
    ["turtle_base","three_legs","three_risers","collars","baby_pin","hinges"], ["chrome_steel","cast_aluminum","black_polymer","rubber"], articulation=["stand_height","leg_spread"], mounts=["FLOOR_CONTACT","MOUNT_SUPPORT"])
add("avenger_d200_grip_head","Avenger D200 Grip Head Reference","LIGHT_ACCESSORY","REFERENCE_STANDARD","STANDARD","SPEC_READY",
    {"disc_diameter_mm":d(63.5,"VERIFIED"),"receiver_mm":d(16,"VERIFIED")}, ["avenger_d200"],
    ["two_grip_discs","receiver","locking_handle","washers"], ["cast_aluminum","steel","black_polymer"], articulation=["grip_rotation"], mounts=["MOUNT_SUPPORT","MOUNT_GRIP"])
add("avenger_d500_grip_arm","Avenger D500 Extension Grip Arm Reference","LIGHT_ACCESSORY","REFERENCE_STANDARD","STANDARD","SPEC_READY",
    {"arm_length_mm":d(510,"VERIFIED")}, ["avenger_d500"], ["steel_arm","fixed_grip_head","locking_handle"], ["chrome_steel","cast_aluminum","black_polymer"], articulation=["grip_rotation"], mounts=["MOUNT_GRIP","MOUNT_ACCESSORY"])

SUPPORT_DESIGNS = [
    ("air_cushioned_light_stand","Air-cushioned Light Stand",{"height_range_mm":d([1000,3000]),"footprint_mm":d(1000)},["tripod_base","telescopic_risers","collars","spigot"], ["aluminum","steel","polymer","rubber"]),
    ("low_light_stand","Low Light Stand",{"height_range_mm":d([200,900]),"footprint_mm":d(700)},["tripod_base","short_risers","collars","spigot"], ["aluminum","steel","polymer","rubber"]),
    ("boom_stand","Studio Boom Stand",{"height_range_mm":d([1200,3500]),"boom_length_mm":d(2000)},["base","risers","pivot","boom_arm","counterweight_mount"], ["steel","aluminum","polymer","rubber"]),
    ("roller_stand","Roller Studio Stand",{"height_range_mm":d([1100,3200]),"footprint_mm":d(1000)},["rolling_base","casters","risers","collars","spigot"], ["steel","aluminum","polymer","rubber"]),
]
for asset_id,name,dims,components,materials in SUPPORT_DESIGNS:
    add(asset_id,name,"LIGHT_SUPPORT","DESIGN_STANDARD","STANDARD","SPEC_READY",dims,["awful_design_standard"],components,materials, articulation=["height_adjustment"], mounts=["FLOOR_CONTACT","MOUNT_SUPPORT"])
ACCESSORY_DESIGNS = [
    ("baby_pin_16mm","16 mm Baby Pin",{"diameter_mm":d(16),"length_mm":d(100)},["pin","shoulder","threaded_base"],["zinc_plated_steel"]),
    ("umbrella_holder","Umbrella Holder",{"receiver_mm":d(16),"umbrella_shaft_mm":d(8)},["receiver","tilt_joint","umbrella_clamp","locking_knobs"],["aluminum","steel","black_polymer"]),
    ("counterweight_4kg","Boom Counterweight 4 kg",{"mass_kg":d(4),"envelope_mm":d([180,100,100])},["weight_body","clamp","locking_knob"],["painted_steel","rubber","polymer"]),
    ("sandbag_10kg","Studio Sandbag 10 kg",{"envelope_mm":d([360,250,70],"PROJECT_VERIFIED"),"nominal_mass_kg":d(10)},["two_soft_pouches","webbing_handle","seams","label_patch"],["ballistic_nylon","webbing","thread","granular_fill"]),
    ("power_cable_5m","Studio Power Cable 5 m",{"length_m":d(5),"cable_diameter_mm":d(8)},["cable","plug_a","plug_b","strain_relief"],["rubber_jacket","copper","polymer"]),
    ("sync_cable_5m","Flash Sync Cable 5 m",{"length_m":d(5),"cable_diameter_mm":d(4)},["cable","connector_a","connector_b","strain_relief"],["rubber_jacket","copper","polymer"]),
    ("black_flag_60x90","Black Flag 60x90 cm",{"frame_mm":d([600,900])},["frame","black_fabric","mount_ear"],["steel_rod","black_textile"]),
    ("white_reflector_100x150","White Reflector Card 100x150 cm",{"panel_mm":d([1000,1500,20])},["panel","edge_tape","mount_points"],["foam_board","matte_white_surface","fabric_tape"]),
    ("diffusion_frame_120","Diffusion Frame 120x120 cm",{"frame_mm":d([1200,1200])},["frame","diffusion_textile","tension_points","mount_ear"],["aluminum_tube","diffusion_textile"]),
    ("gobo_frame_60","Gobo Frame 60x60 cm",{"frame_mm":d([600,600])},["frame","insert_slot","mount_ear"],["painted_steel","black_polymer"]),
]
for asset_id,name,dims,components,materials in ACCESSORY_DESIGNS:
    add(asset_id,name,"LIGHT_ACCESSORY","DESIGN_STANDARD","STANDARD","SPEC_READY",dims,["awful_design_standard"],components,materials, mounts=["MOUNT_ACCESSORY"])
add("profoto_rfi_speedring","Profoto RFi Speedring Reference","LIGHT_ACCESSORY","REFERENCE_STANDARD","STANDARD","SPEC_READY",
    {"interface_diameter_mm":d(100,"VERIFIED")}, ["profoto_rfi_system"], ["speedring_body","rod_sockets","locking_collar","head_interface"], ["cast_aluminum","anodized_aluminum","black_polymer"], articulation=["locking_rotation"], mounts=["MOUNT_MODIFIER","MOUNT_FIXTURE"])

# Furniture: representative studio assets with frozen design envelopes.
FURNITURE = [
    ("leather_sofa_3seat","Leather Sofa, 3-seat",[2200,950,780],["frame","seat_cushions","back_cushions","arms","piping","feet"],["leather","foam","wood_frame","metal_fasteners"]),
    ("lounge_armchair_leather","Lounge Armchair, Leather",[900,900,800],["frame","seat_cushion","back_cushion","arms","piping","feet"],["leather","foam","wood_frame","metal_fasteners"]),
    ("lounge_armchair_fabric","Lounge Armchair, Fabric",[900,900,800],["frame","seat_cushion","back_cushion","arms","piping","feet"],["woven_fabric","foam","wood_frame","metal_fasteners"]),
    ("dining_chair_wood","Dining Chair, Wood",[480,520,820],["seat","back","front_legs","rear_legs","joinery"],["hardwood","clear_finish"]),
    ("chair_wood_metal","Chair, Wood + Metal",[500,540,820],["wood_seat","wood_back","metal_frame","feet"],["hardwood","powder_coated_steel","rubber"]),
    ("bar_stool_low","Bar Stool, Low",[420,420,650],["seat","legs","foot_ring","feet"],["wood","powder_coated_steel","rubber"]),
    ("bar_stool_high","Bar Stool, High",[430,430,780],["seat","legs","foot_ring","feet"],["wood","powder_coated_steel","rubber"]),
    ("studio_table_rect","Studio Table, Rectangular",[1600,800,750],["top","apron","legs","feet"],["wood_veneer","plywood","powder_coated_steel"]),
    ("side_table_round","Side Table, Round",[500,500,520],["round_top","column_or_legs","feet"],["wood","powder_coated_steel"]),
]
for asset_id,name,size,components,materials in FURNITURE:
    add(asset_id,name,"FURNITURE","DESIGN_STANDARD","HERO" if "sofa" in asset_id or "armchair" in asset_id else "STANDARD","SPEC_READY",
        {"design_envelope_mm":d(size)},["awful_design_standard"],components,materials, mounts=["FLOOR_CONTACT"], notes=["Representative studio design; silhouette and construction may be refined without changing the frozen envelope contract."])
# Hard studio props: parameterized families.
for size in (300,400,500,600):
    add(f"wood_cube_{size}",f"Wood Cube {size} mm","PROP","DESIGN_STANDARD","STANDARD","SPEC_READY",
        {"cube_mm":d([size,size,size])},["awful_design_standard"],["cube_body","edge_breaks"],["wood","clear_or_matte_finish"], mounts=["FLOOR_CONTACT"])
for size in (300,400,500):
    add(f"plaster_cube_{size}",f"Plaster Cube {size} mm","PROP","DESIGN_STANDARD","STANDARD","SPEC_READY",
        {"cube_mm":d([size,size,size])},["awful_design_standard"],["cube_body","edge_chips_microdetail"],["plaster","sealed_plaster_optional"], mounts=["FLOOR_CONTACT"])
for diameter in (300,400,500):
    add(f"plaster_sphere_{diameter}",f"Plaster Sphere Ø{diameter} mm","PROP","DESIGN_STANDARD","STANDARD","SPEC_READY",
        {"diameter_mm":d(diameter)},["awful_design_standard"],["sphere_body","contact_flat_microzone"],["plaster"], mounts=["FLOOR_CONTACT"])
for asset_id,name,diameter,height in (
    ("plaster_cylinder_low","Plaster Cylinder, Low",400,300),("plaster_cylinder_tall","Plaster Cylinder, Tall",350,700),
    ("plaster_round_pedestal_low","Round Pedestal, Low",500,450),("plaster_round_pedestal_tall","Round Pedestal, Tall",450,900)):
    add(asset_id,name,"PROP","DESIGN_STANDARD","STANDARD","SPEC_READY",{"diameter_mm":d(diameter),"height_mm":d(height)},["awful_design_standard"],["body","edge_breaks"],["plaster"], mounts=["FLOOR_CONTACT"])
for asset_id,name,size in (
    ("plaster_plinth_low","Plaster Rectangular Plinth, Low",[500,500,450]),
    ("plaster_plinth_tall","Plaster Rectangular Plinth, Tall",[400,400,900]),
    ("plaster_cone","Plaster Cone",[450,450,700])):
    add(asset_id,name,"PROP","DESIGN_STANDARD","STANDARD","SPEC_READY",{"design_envelope_mm":d(size)},["awful_design_standard"],["body","edge_breaks"],["plaster"], mounts=["FLOOR_CONTACT"])
# Canon production-reference pair. Representative, not claimed as historical Sensetique SKU.
add("canon_eos_5d_mark_iv","Canon EOS 5D Mark IV","CAMERA","REFERENCE_STANDARD","HERO","SPEC_READY",
    {"body_mm":d([150.7,116.4,75.9],"VERIFIED"),"mass_g":d(890,"VERIFIED")}, ["canon_5d4"],
    ["magnesium_polycarbonate_body","ef_mount","grip","viewfinder","hotshoe","top_lcd","rear_lcd","buttons","dials","doors","ports","strap_lugs"],
    ["matte_black_polymer","painted_magnesium","rubber_grip","optical_glass","clear_lcd_cover","printed_decals"], ["body_only"],
    ["rear_screen: fixed","dials_rotate"], ["EF_MOUNT_PLANE","SENSOR_PLANE","HOTSHOE_MOUNT","TRIPOD_MOUNT","OPTICAL_AXIS"],
    ["Representative production body selected for pipeline preparation; historical Sensetique identity remains intentionally unclaimed."])
add("canon_ef_24_70_f28l_ii","Canon EF 24-70mm f/2.8L II USM","LENS","REFERENCE_STANDARD","HERO","SPEC_READY",
    {"diameter_mm":d(88.5,"VERIFIED"),"retracted_length_mm":d(113,"VERIFIED"),"mass_g":d(805,"VERIFIED"),"filter_thread_mm":d(82,"VERIFIED")}, ["canon_2470_ii"],
    ["ef_mount","rear_barrel","zoom_ring","focus_ring","distance_window","front_barrel","filter_thread","front_element","switches","red_ring","engravings"],
    ["matte_black_polymer","rubber","painted_metal","optical_glass","printed_decals"], ["24mm","35mm","50mm","70mm"],
    ["zoom_rotation_and_extension","focus_ring_rotation"], ["EF_MOUNT_PLANE","OPTICAL_AXIS","FILTER_THREAD_82"])

CATEGORY_GEOMETRY = {
    "DEVICE_MOCKUP": "Build primary enclosure from verified envelope; keep glass, optics, controls and seams separate; use real bevel widths and non-destructive modifiers until runtime bake.",
    "LIGHT_FIXTURE": "Block primary envelope first; separate shell, optical/emitter parts, controls, vents, yoke/adapter and cable interfaces; articulation pivots must match physical axes.",
    "LIGHT_MODIFIER": "Build mount interface first, then profile/rod skeleton and fabric or reflector surface; preserve source/modifier separation and open/collapsed states when applicable.",
    "LIGHT_SUPPORT": "Build floor contact and load path first; telescoping tubes, collars, hinges and pins are separate mechanical parts with physical pivots.",
    "LIGHT_ACCESSORY": "Model only geometry that affects mounting, silhouette, collision or close-up readability; repeat hardware by instances.",
    "FURNITURE": "Establish ergonomic envelope and frame, then cushions/panels; upholstered assets require contact deformation, seam routes and believable compression rather than generic subdivision.",
    "PROP": "Use dimensionally exact primitive family as base; bevels, casting/wood/plaster irregularity and contact wear are secondary, non-destructive layers.",
    "CAMERA": "Respect mount plane, sensor plane and optical axis; body shell, grip, doors, controls, screens, ports and optical parts remain independently editable.",
    "LENS": "Build around optical axis and mount plane; zoom/focus rings and extending groups require clean pivots and preserved engraved/decal zones.",
}
def md_value(value):
    if isinstance(value, (dict, list)):
        return f"`{json.dumps(value, ensure_ascii=False, sort_keys=True)}`"
    return f"`{value}`"

def render_dossier(a):
    dims = "\n".join(
        f"- **{k}**: {md_value(v['value'])}; confidence `{v['confidence']}`."
        for k, v in a["dimensions"].items()
    )
    refs = []
    for ref in a["source_refs"]:
        authority, url, note = SOURCES[ref]
        refs.append(f"- `{ref}` [{authority}]: {url} — {note}")
    ref_text = "\n".join(refs)
    comps = "\n".join(f"- `{x}`" for x in a["components"])
    mats = "\n".join(
        f"- `{x}`: physically plausible master material; runtime version preserves the same surface role."
        for x in a["materials"]
    )
    variants = ", ".join(f"`{x}`" for x in a["variants"])
    articulation = "\n".join(f"- {x}" for x in a["articulation"])
    mounts = "\n".join(f"- `{x}`" for x in a["mounts"])
    tex = "4K authoring / 2K runtime hero set" if a["tier"] == "HERO" else "2K authoring / 1K runtime standard set"
    return dedent(f"""
    # {a['name']} — asset dossier

    ## Identity and production role
    - Asset ID: `{a['id']}`
    - Category: `{a['category']}`
    - Identity class: `{a['identity_class']}`
    - Current stage: `{a['stage']}`
    - Quality tier: `{a['tier']}`
    - Variants: {variants}
    - `production_ready=true` means this dossier is complete enough to enter the next modeling gate; it does not mean the 3D asset is released.

    ## Dimensional contract
    {dims}
    - Blender scale is metric: `1 Blender unit = 1 metre`.
    - `DESIGN_STANDARD` dimensions are frozen representative production targets, not historical manufacturer claims.

    ## Reference and provenance
    {ref_text}
    - Identity claims must not be upgraded beyond the evidence class without a new primary source.

    ## Component decomposition
    {comps}
    - Hidden construction may be simplified only when it does not affect articulation, silhouette, shadows, mount compatibility or bake results.
""")
def render_full_dossier(a):
    base = render_dossier(a)
    geometry = CATEGORY_GEOMETRY[a["category"]]
    tex_res = "4K authoring / 2K runtime" if a["tier"] == "HERO" else "2K authoring / 1K runtime"
    runtime = a["runtime"]
    notes = "\n".join(f"- {n}" for n in a["notes"]) or "- No asset-specific exception beyond the contracts below."
    articulation = "\n".join(f"- {x}" for x in a["articulation"])
    mounts = "\n".join(f"- `{x}`" for x in a["mounts"])
    text = base + dedent(f"""
    ## Geometry plan
    {geometry}
    - Blockout must match every frozen dimensional field before secondary detail begins.
    - MID preserves silhouette, control placement, seams, pivots and mount interfaces; HIGH is source-only detail for baking where useful.

    ## Materials and surface response
    {chr(10).join(f'- `{m}`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.' for m in a['materials'])}
    - Master shaders remain editable in Blender; runtime shaders must be glTF-friendly and bounded in cost.

    ## UV and texture plan
    - Target: `{tex_res}`; hidden surfaces may receive lower density, but visible hero surfaces keep consistent texel density.
    - UV0 carries PBR surfaces; UV1 or decals may carry labels, legends, logos and non-repeating identification marks.
    - Unique wear belongs only where reference evidence or product use justifies it.
""")
    text += dedent(f"""
    ## Bake plan
    - Bake `Normal`, `AO`, `Curvature`, `Thickness`, `Position` and material/object ID from HIGH to MID/LOW only where geometry warrants it.
    - Runtime outputs use BaseColor, Roughness, Metallic, Normal, AO, Opacity/Transmission and Emission as applicable.
    - Master masks stay separate; packed ORM is allowed only for delivery/runtime optimization.

    ## LOD, collision and runtime
    - Shipping format: `{runtime['shipping']}`.
    - LOD contract: {', '.join(runtime['lod'])}.
    - Collision contract: `{runtime['collision']}`; collision geometry must stay separate from hero/render geometry.
    - LOD1 target is at most 75% of LOD0 triangles; LOD2 target is at most 35% while preserving silhouette and mounts.
    - Export excludes preview cameras, lights, reference envelopes and authoring-only helpers.

    ## Rigging, variants and mounts
    **Articulation**
    {articulation}
    **Semantic mounts / origins**
    {mounts}
    - Origins must be deterministic and useful for placement, animation and Auto Fit.
""")
    text += dedent(f"""
    ## QA and acceptance gates
    - Dimensional validation passes for every frozen measurement and origin/mount coordinate.
    - Zero unintended non-manifold geometry, duplicate surfaces, z-fighting, broken normals or absolute texture paths.
    - Diagnostic renders include front, rear, left/right side, top/bottom when useful, three-quarter and required macro views.
    - Visual approval compares silhouette, proportion, material response and labeled controls against the cited references.
    - Blender 5.2.1 save/reopen, spawn/delete/respawn, LOD export and GLB validation pass before release approval.

    ## Production handoff
    - Next gate: `{a['stage']}` → blockout/review unless the current stage is already further advanced.
    - Modeling starts from this dossier and the shared contracts; new facts update `registry.json` and regenerate this file.
    - Evidence class remains `{a['identity_class']}` until a stronger source explicitly justifies an upgrade.
    **Asset-specific constraints**
    {notes}
    - A model is `FINAL` only after geometry, material, runtime and visual gates all pass; a complete dossier is preparation, not release approval.
""")


    return text

def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def validate_catalog():
    ids = [a["id"] for a in ASSETS]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate asset ids")
    for a in ASSETS:
        if not a["dimensions"]:
            raise ValueError(f"missing dimensions: {a['id']}")
        for ref in a["source_refs"]:
            if ref not in SOURCES:
                raise ValueError(f"unknown source {ref}: {a['id']}")
        if a["category"] not in CATEGORY_GEOMETRY:
            raise ValueError(f"missing category geometry rule: {a['category']}")


def registry_payload():
    assets = []
    for a in ASSETS:
        row = dict(a)
        row["dossier_path"] = f"docs/assets/dossiers/{a['id']}.md"
        assets.append(row)
    return {"schema_version": SCHEMA_VERSION, "asset_count": len(assets), "assets": assets}

def render_index():
    rows = ["| Asset | Category | Identity | Stage | Tier |", "| --- | --- | --- | --- | --- |"]
    for a in sorted(ASSETS, key=lambda x: (x["category"], x["id"])):
        rows.append(f"| [{a['name']}](dossiers/{a['id']}.md) | `{a['category']}` | `{a['identity_class']}` | `{a['stage']}` | `{a['tier']}` |")
    return dedent(f"""
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
    """) + "\n".join(rows) + "\n"


def render_sources():
    lines = ["# Source register", "", "Sources are evidence for identity, dimensions and construction. Historical identity and technical geometry are separate claims.", ""]
    for key, (authority, url, note) in sorted(SOURCES.items()):
        lines += [f"## `{key}`", f"- Authority: `{authority}`", f"- Location: {url}", f"- Use: {note}", ""]
    return "\n".join(lines)

def render_production_order():
    waves = [
        ("Wave 1 — current device assets", ["iphone_17","ipad_pro_11_m5","ipad_pro_13_m5","macbook_pro_14_m5"]),
        ("Wave 2 — studio rig core", ["profoto_d1_500_air","profoto_magnum_100624","avenger_a2025f_cstand","sandbag_10kg"]),
        ("Wave 3 — Profoto / continuous fixtures", ["profoto_acute_d4_head","profoto_acute2_generator","dedolight_dlhm4_300","arri_300_plus","profoto_zoom_100785","profoto_softlight_silver_100607","profoto_softlight_white_100608"]),
        ("Wave 4 — soft modifiers", ["grifon_sb_fw95","profoto_rfi_octa_150_254712","profoto_rfi_3x4_254704","fotokvant_evenly_30x160","fotokvant_u104w_para","fotokvant_u101s_silver","lumifor_lusl_18016"]),
        ("Wave 5 — support and grip", [a["id"] for a in ASSETS if a["category"] in {"LIGHT_SUPPORT","LIGHT_ACCESSORY"}]),
        ("Wave 6 — hard props", [a["id"] for a in ASSETS if a["category"] == "PROP"]),
        ("Wave 7 — furniture", [a["id"] for a in ASSETS if a["category"] == "FURNITURE"]),
        ("Wave 8 — Canon system", ["canon_eos_5d_mark_iv","canon_ef_24_70_f28l_ii"]),
    ]
    lines = ["# Production order", "", "Every asset follows the same gates: spec → blockout → low → mid → high/bake where justified → materials → LOD/runtime → visual approval.", ""]
    for title, ids in waves:
        lines += [f"## {title}"] + [f"- [{next(a['name'] for a in ASSETS if a['id']==i)}](dossiers/{i}.md)" for i in dict.fromkeys(ids)] + [""]
    return "\n".join(lines)

CONTRACT_DOCS = {
"GENERAL_ASSET_CONTRACT.md": """# General Asset Contract

- Blender target: 5.2.1 LTS; metric scale, 1 BU = 1 m.
- Every asset has stable ID, deterministic origin, explicit forward/up axes and semantic mounts.
- Manufacturer/historical identity is never inferred from visual similarity. `HISTORICAL_CONFIRMED`, `REFERENCE_STANDARD`, `DESIGN_STANDARD` and `PROJECT_VERIFIED` are distinct evidence classes.
- Primary dimensions are frozen before detail modeling; new evidence updates registry and dossier together.
- Source assets remain editable; runtime exports are derived artifacts.
- Native Blender properties remain canonical for light power/color/temperature and other Blender-owned controls.
- No absolute texture paths, eager downloads or scene mutation on import/enable.
- Rebuild may only replace AWFUL-owned data and must preserve user-owned scene content.
""",
"STUDIO_RIG_CONTRACT.md": """# Studio Rig Contract

`SUPPORT → FIXTURE → MODIFIER` are separate replaceable layers. One fixture may accept multiple compatible modifiers without duplicating the support or pose.

Required semantic points: `MOUNT_SUPPORT`, `MOUNT_FIXTURE`, `MOUNT_MODIFIER`, `MOUNT_UMBRELLA`, `EMITTER_ORIGIN`, `LIGHT_TARGET`, `FLOOR_CONTACT` as applicable.

Configurator changes preserve unrelated state: replacing a Magnum with an Octa does not move the stand or alter native light power. Physical support, grip and modifiers remain ordinary editable Blender objects.
""",
"MATERIAL_TEXTURE_CONTRACT.md": """# Material and Texture Contract

- Separate physically distinct surfaces: metal, polymer, rubber, glass, textile, plaster, wood, paper/label and emissive surfaces.
- Master materials are procedural/editable where useful; runtime materials are simplified glTF-friendly derivatives.
- Hero assets default to 4K authoring and 2K runtime; standard assets default to 2K authoring and 1K runtime unless close-up evidence requires more.
- UV0 is PBR; UV1 or decals carry labels/legends when useful.
- Bake Normal/AO/Curvature/Thickness/Position/IDs only when HIGH detail materially improves MID/LOW.
- Wear is restrained, reference-driven and never a substitute for correct geometry or roughness response.
""",
}
CONTRACT_DOCS.update({
"LOD_RUNTIME_CONTRACT.md": """# LOD and Runtime Contract

- Shipping format is GLB/glTF 2.0; source of truth remains Blender.
- Runtime hierarchy uses stable asset roots and semantic mounts. Preview cameras, lights, reference boxes and authoring-only helpers never ship.
- LOD0 preserves reviewed MID silhouette and product-defining details. LOD1 targets ≤75% of LOD0 triangles. LOD2 targets ≤35% while retaining silhouette, pivots and mounts.
- Collision is separate simplified geometry. Never use hero meshes as physics meshes by default.
- Meshopt is the preferred geometry-compression path after structural validation. KTX2 is the preferred runtime texture path when texture compression is required.
- Repeated props/supports should support instancing. Exported transforms are normalized and pivots remain meaningful for Three.js/game runtimes.
""",
"QA_VISUAL_APPROVAL_CONTRACT.md": """# QA and Visual Approval Contract

Release requires four independent gates: geometry, materials, runtime and visual approval.

Geometry: dimensions, origins, mounts, normals, manifold status, duplicate/z-fighting checks and articulation ranges.
Materials: missing files = 0, absolute paths = 0, correct color spaces, physically distinct surface roles and bounded runtime shaders.
Runtime: spawn/delete/respawn, save/reopen, LOD export, collision export, GLB validation and Blender 5.2.1 packaged runtime checks.
Visual: deterministic front/rear/side/three-quarter views plus top/bottom and macro views when useful. Review silhouette, proportion, labels, surface response and mechanical plausibility against cited references.

A green unit test is not visual approval. An attractive render is not dimensional approval. `FINAL` requires both.
""",
})
DIAGRAM_DOCS = {
"studio_rig.md": """# Studio Rig hierarchy

```mermaid
graph TD
  R[AWFUL_STUDIO_RIG] --> S[SUPPORT]
  R --> F[FIXTURE]
  R --> M[MODIFIER]
  R --> A[ACCESSORIES]
  R --> L[Native Blender Light]
  S --> MS[MOUNT_SUPPORT]
  F --> MF[MOUNT_FIXTURE / MOUNT_MODIFIER]
  M --> MM[MOUNT_MODIFIER]
  F --> E[EMITTER_ORIGIN]
  R --> T[LIGHT_TARGET]
```
""",
"asset_pipeline.md": """# Asset production pipeline

```mermaid
flowchart LR
  A[Spec + sources] --> B[Technical blockout]
  B --> C[LOW]
  C --> D[MID]
  D --> E[HIGH where justified]
  E --> F[UV + Bake]
  F --> G[Master materials]
  G --> H[Runtime materials]
  H --> I[LOD0/1/2]
  I --> J[GLB + collision]
  J --> K[Blender/runtime QA]
  K --> L[Visual approval]
```
""",
"soft_modifier_system.md": """# Soft modifier construction

```mermaid
graph TD
  SR[Speedring / umbrella shaft] --> SK[Rod or rib skeleton]
  SK --> OS[Outer shell / canopy]
  OS --> IL[Reflective inner lining]
  IL --> ID[Inner diffusion]
  ID --> FD[Front diffusion]
  SK --> ST[Open / collapsed state]
```
""",
"camera_lens_system.md": """# Camera and lens hierarchy

```mermaid
graph LR
  B[Camera body] --> MP[EF_MOUNT_PLANE]
  B --> SP[SENSOR_PLANE]
  B --> HS[HOTSHOE_MOUNT]
  L[Lens] --> MP
  L --> OA[OPTICAL_AXIS]
  L --> FR[Focus ring]
  L --> ZR[Zoom ring / extending group]
```
""",
"furniture_layers.md": """# Furniture construction layers

```mermaid
graph TD
  E[Verified/frozen envelope] --> F[Structural frame]
  F --> C[Cushion / panel volumes]
  C --> S[Seams + piping]
  C --> D[Contact deformation]
  S --> M[Material response]
  D --> H[Hero folds / bake detail]
  M --> R[Runtime material]
```
""",
"device_material_stack.md": """# Device material stack

```mermaid
graph TD
  U[Unibody metal] --> E[Edge/trim metal]
  U --> G[Display glass]
  G --> C[Replaceable screen content]
  U --> O[Optical/camera glass]
  U --> P[Polymer / rubber details]
  U --> D[Logo + decal layer]
```
""",
}

def build():
    validate_catalog()
    DOCS.mkdir(parents=True, exist_ok=True)
    DOSSIERS.mkdir(parents=True, exist_ok=True)
    CONTRACTS.mkdir(parents=True, exist_ok=True)
    DIAGRAMS.mkdir(parents=True, exist_ok=True)

    payload = registry_payload()
    write_text(DOCS / "registry.json", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    write_text(DOCS / "README.md", render_index())
    write_text(DOCS / "sources.md", render_sources())
    write_text(DOCS / "PRODUCTION_ORDER.md", render_production_order())

    for name, content in CONTRACT_DOCS.items():
        write_text(CONTRACTS / name, content)
    for name, content in DIAGRAM_DOCS.items():
        write_text(DIAGRAMS / name, content)
    write_text(DIAGRAMS / "README.md", "# System diagrams\n\n" + "\n".join(f"- [{name}]({name})" for name in sorted(DIAGRAM_DOCS)))

    expected = set()
    for a in ASSETS:
        path = DOSSIERS / f"{a['id']}.md"
        expected.add(path.name)
        write_text(path, render_full_dossier(a))
    for stale in DOSSIERS.glob("*.md"):
        if stale.name not in expected:
            stale.unlink()

    print(f"Generated {len(ASSETS)} asset dossiers in {DOCS}")


if __name__ == "__main__":
    build()
