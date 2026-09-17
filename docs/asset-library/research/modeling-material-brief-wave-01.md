# Modeling & Material Brief — Studio Equipment Wave 01

This document converts the research pack into production decisions for Blender 5.2 / AWFUL STUDIO.

## 1. Modeling principle

The library is not a museum scan archive and not a bag of unrelated `.blend` files. Each model must preserve the characteristics that matter for:

- recognisable silhouette;
- real-world scale;
- correct support / mount compatibility;
- believable mechanical articulation;
- hero close-up shading;
- efficient runtime use inside AWFUL STUDIO.

Geometry must be spent where it changes silhouette, specular behavior, deformation or compatibility. Everything else should move toward material response, decals and baking.

---

## 2. Hard-surface construction stack

Preferred non-destructive source stack:

1. dimensioned blockout;
2. boolean / cutter stage;
3. bevel stage using real-world widths;
4. weighted normals / controlled custom normals only where still useful in Blender 5.2;
5. support/detail geometry;
6. source-only high-frequency details;
7. runtime cleanup / triangulation validation at export boundary, not during authoring.

Avoid:

- arbitrary subdivision on industrial equipment;
- destructive booleans before silhouette approval;
- bevel widths driven by screen pixels;
- fake panel lines painted into normal maps when they create visible parallax in hero shots;
- screws modeled as unique objects when an instanced family works.

## 3. Shared industrial detail library

Create reusable components:

- socket-head screw;
- Phillips / Pozidriv screw;
- slotted fastener;
- knurled knob;
- star knob;
- rubber foot;
- cable gland;
- strain relief;
- IEC/C13-style inlet family;
- 3.5 mm jack family;
- toggle switch;
- rocker switch;
- ventilation grille primitives;
- 16 mm / 5/8 in receiver and pin;
- Profoto rubber-collar / clasp primitives;
- softbox rod-end and color-coded receiver family.

Every component should have a real unit scale and instance-friendly origin.

---

## 4. Profoto D1 500 Air modeling plan

### Primary envelope

- L 300 mm
- W 130 mm
- H 170 mm

### Decomposition

- central cylindrical/barrel body;
- front flat-reflector/glass assembly;
- rear circular control housing;
- side ventilation zones;
- top carry handle / bridge structure;
- lower stand bracket / yoke block;
- tilt-lock knob;
- mount receiver;
- rear buttons / encoder / display;
- power and sync connectors;
- labels and logos as decals.

### Hero geometry

Must be geometry:

- front glass thickness and metal ring;
- carry handle silhouette;
- stand bracket;
- major vents;
- encoder/knob relief;
- rear button caps;
- casing transitions and bevels.

Can be texture/decal:

- Profoto logo;
- D1 label;
- numerical scale / control legends;
- tiny compliance labels;
- very shallow injection/paint imperfections.

### Shading goal

The D1 should read as dense professional equipment, not a smooth black plastic tube. Important signals:

- slightly different roughness between painted structural body and molded controls;
- faint edge polishing only on handled areas;
- fingerprints and dust optional hero overlay, off by default;
- front glass roughness/transmission independent from internal reflector.

---

## 5. Magnum / Zoom / Softlight reflector modeling

### Shared rule

Build actual revolved profiles from dimensioned envelopes and photographic profile matching. Do not scale one reflector to create another.

### Magnum

- Ø345 mm
- depth 265 mm

Need:

- outer shell;
- inner reflective shell;
- front rolled lip;
- rear neck;
- rubber collar;
- clasp/lock;
- subtle shell thickness.

Interior hammered texture:

- procedural source normal using multi-frequency cellular/noise blend;
- low-amplitude displacement allowed only in source/high material;
- runtime uses normal + roughness, not displaced geometry.

### Zoom

- Ø193 mm
- depth 180 mm

Need:

- distinct profile curve;
- integrated front grid-holder structure;
- rear rubber collar / clasp;
- smooth-but-not-perfect silver interior.

### Softlight

- Ø525 mm
- depth 190 mm

Need:

- shallow dish shell;
- central deflector plate;
- support rods/hardware for the deflector;
- front rim;
- rear collar.

Variants:

- Silver: metal-like reflective interior, 100607.
- White: coated white interior, 100608.

Same geometry can serve both if historical exterior hardware matches the selected reference generation.

---

## 6. RFi softbox modeling system

Create a procedural/source rig, then freeze clean runtime geometry per model.

### Parameters

- face width / height or diameter;
- depth;
- rod count;
- speedring radius;
- recessed-front depth;
- corner radius/tension;
- inner diffuser offset;
- outer diffuser inset;
- shell sag amount;
- rod bow amount.

### Cloth behavior

We do not need a heavy cloth simulation every time. Better source workflow:

1. analytical base cage;
2. Geometry Nodes or modifiers for panel generation;
3. controlled cloth/tension pass only for approved source shape;
4. apply/freeze to high/source mesh;
5. derive runtime mesh with preserved silhouette and seam zones.

Visible realism comes from tension asymmetry:

- corners tighter than panel centers;
- subtle concavity between rods;
- diffuser not perfectly planar;
- seams slightly raised;
- rod pockets create local deformation.

### 5' Octa

Eight radial panels must not be perfectly identical at hero level. Runtime can instance symmetry in geometry while roughness/normal variation breaks repetition.

### Rectangular RFi

The 2x3 and 3x4 should share a generator but not simple uniform scaling: depth differs and rod angle changes.

---

## 7. Umbrella source generator

Umbrellas deserve a parametric generator because diameter, depth and rib count vary.

Required parameters:

- canopy diameter;
- canopy depth;
- rib count;
- shaft diameter;
- rib arc;
- rib taper;
- stretcher position;
- runner height;
- fabric panel sag;
- open amount 0..1.

### Geometry

- shaft and hardware as hard surface;
- ribs as curves with bevel profile;
- fabric as radial panels;
- separate seam strip along each rib only for HERO mode;
- small ferrule / rib-tip components instanced.

### Runtime levels

- LOD0: ribs + stretchers + actual panel curvature.
- LOD1: ribs retained, stretchers simplified.
- LOD2: canopy shell + a reduced rib impression.
- proxy: silhouette only.

---

## 8. ARRI 300 Plus source plan

Use manufacturer 2D CAD as the preferred profile reference before final model approval.

Critical parts:

- die-cast/extruded body;
- ventilation ribs;
- 80 mm stepped Fresnel lens;
- front 130 mm accessory ring;
- yoke;
- 16 mm receiver;
- focus drive / knob;
- rear door / lamp access;
- cable;
- 4-leaf barn doors as independent accessory.

### Fresnel lens

At HERO tier model the concentric Fresnel steps physically, but keep segment density sane. The lens is a major specular feature and normal-map-only treatment will fail in close side angles.

At STANDARD tier use simplified physical rings + normal support.

---

## 9. Dedolight DLHM4-300 source plan

Do not precision-model until outer dimensions are found. The fixture is compact and dimension errors will be obvious because many parts are tightly packed.

Prepare decomposition now:

- front optics barrel;
- focus mechanism;
- accessory receiver;
- yoke;
- side/rear electronics shell;
- inline cable switch;
- strain relief;
- barn doors as accessory;
- projection/imager accessories later.

---

## 10. Master material recipes

### 10.1 Powder-coated black metal

Source shader:

- base color: near-black, never absolute zero;
- roughness macro variation: 0.03–0.08 amplitude;
- micro orange-peel normal: extremely fine;
- optional edge polish mask from curvature, manually restrained;
- dust layer disabled by default.

Bake/runtime:

- BaseColor
- Roughness
- Normal
- optional AO

### 10.2 Reflector silver

Source shader:

- metallic ~1;
- high reflectance;
- roughness varies by tool;
- hammered Magnum interior gets multi-scale normal;
- Softlight Silver should be smoother than exaggerated hammered foil.

Rule: do not use pure mirror response. Real reflector interiors preserve texture and broaden highlights.

### 10.3 Anodized / brushed aluminum

Use directional micro-normal aligned to manufacturing direction. Keep anisotropy subtle unless reference clearly shows brushing.

### 10.4 Technical black plastic

Separate families:

- matte structural ABS;
- satin molded knob plastic;
- slightly softer rubberized control surface.

Do not collapse these into one black material.

### 10.5 Rubber

- high micro-normal frequency;
- moderate roughness;
- subtle compression/contact variation;
- no broad procedural color noise.

### 10.6 Softbox black fabric

Source:

- woven normal;
- slight fuzzy/sheeny response if supported cleanly;
- macro folds from geometry, not texture;
- roughness changes along tension direction.

Runtime:

- normal + roughness + optional sheen-safe node group;
- avoid expensive procedural weave at distance.

### 10.7 Softbox silver lining

A fabric with reflective coating, not metal sheet.

Combine:

- silver base;
- high reflectance;
- broken weave normal;
- higher roughness than polished aluminum;
- subtle panel-direction variation.

### 10.8 Diffusion fabric

Need:

- off-white base;
- controlled transmission;
- fine woven normal;
- very subtle opacity variation;
- optional subsurface only if it improves Cycles result and stays performant.

The emitter itself remains a Blender Light. Fabric material must not become the sole lighting system.

### 10.9 Fresnel / optical glass

Separate:

- surface glass;
- internal optical structure;
- lens edge.

Use physically plausible IOR and roughness. Colored reflections should come from lighting/coating, not arbitrary blue tint unless reference supports it.

---

## 11. Texture resolution policy

Source masters:

- 8K only for hero authoring if needed for labels or large soft fabric surfaces.
- 4K default hero source.
- 2K standard source.

Runtime initial targets:

- D1 / ARRI / Dedolight hero: 4K max, preferably split decal atlas from surface maps.
- hard reflectors: 2K normally enough because large appearance is procedural/specular.
- softboxes: 2K surface tile + reusable procedural/trim approach; do not dedicate unique 4K maps to every black panel.
- umbrellas: shared tiled fabric + small unique mask if needed.
- small accessories: 1K or shared atlas.

VRAM is a budget, not a decorative suggestion.

---

## 12. Decal strategy

Create reusable decal atlas families:

- Profoto white logos;
- product names;
- numerical scales;
- safety labels;
- control legends;
- ARRI logos / model plate;
- Dedolight marks;
- generic compliance labels where legally/visually appropriate.

For historical replicas used internally/portfolio, preserve visual authenticity. For distributable public asset packs, review trademark/logo redistribution policy separately.

---

## 13. Bake plan

Source-to-runtime maps:

- tangent-space Normal;
- AO;
- Curvature;
- Material ID;
- Position;
- optional Thickness for fabric/transmission masks.

Validation scenes:

1. neutral softbox-lit gray studio;
2. hard raking key light;
3. HDRI/specular check;
4. close-up 85–120 mm lens;
5. distance 35–50 mm lens.

Reject bake if:

- gradients reveal cage mismatch;
- thin shells show projection leakage;
- UV seams pop under grazing specular;
- reflector interiors lose intended radial continuity;
- mirrored labels or asymmetric controls appear.

---

## 14. Naming contract

Examples:

- `AS_FIX_PROFOTO_D1_500`
- `AS_FIX_PROFOTO_ACUTE_D4_HEAD`
- `AS_GEN_PROFOTO_ACUTE2_1200`
- `AS_MOD_PROFOTO_MAGNUM_100624`
- `AS_MOD_PROFOTO_ZOOM_100785`
- `AS_MOD_PROFOTO_SOFTLIGHT_SILVER_100607`
- `AS_MOD_PROFOTO_RFI_OCTA_150`
- `AS_FIX_ARRI_300_PLUS`
- `AS_FIX_DEDOLIGHT_DLHM4_300`

Subobjects:

- `GEO_`
- `COL_`
- `RIG_`
- `MOUNT_`
- `DECAL_`
- `MAT_`
- `IMG_`

---

## 15. Immediate pre-model deliverables

Before opening precision modeling for the first vertical slice:

- create D1 orthographic reference board;
- trace D1 300 x 130 x 170 mm envelope;
- create Magnum Ø345 x 265 profile sheet;
- define Profoto collar axis and emitter origin;
- establish temporary 16 mm support proxy;
- create material ball tests for black coating, silver reflector, rubber and glass;
- test two camera distances to determine required bevel fidelity;
- verify all source URLs remain accessible and record access date in asset manifests.
