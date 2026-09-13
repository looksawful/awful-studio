# Source Register — Wave 01B Support & Grip

Accessed: 2026-09-13

## Avenger / Manfrotto primary manufacturer sources

### A2025F C-Stand 25 Fixed Base

Manufacturer page:
https://www.manfrotto.com/de-de/c-stand-25-a2025f/

Extracted facts:
- max height 253 cm;
- min/closed height 110 cm;
- footprint 95 cm;
- weight 5 kg;
- payload 10 kg;
- 3 sections / 2 risers;
- tube diameters 35 / 30 / 25 mm;
- leg tube diameter 25 mm;
- chrome steel;
- 16 mm male top;
- compatibility with D200 and D500 series.

Trust: `PRIMARY / VERIFIED`.
Historical Sensetique identity: `UNPROVEN`.

### D200 Grip Head

Manufacturer page:
https://www.manfrotto.com/global-en/grip-head-2-1-2-d200/

Extracted facts:
- nominal 2.5 in / 63.5 mm head class;
- 0.55 kg;
- aluminum;
- 16 mm / 5/8 in socket;
- grip holes 6.4 / 9.5 / 12.7 / 16 mm;
- automotive-type brake discs;
- rubberized T-handle.

Trust: `PRIMARY / VERIFIED`.
Historical Sensetique identity: `UNPROVEN`.

### D520 Extension Grip Arm

Manufacturer page:
https://www.manfrotto.com/global-en/40-extension-grip-arm-d520/

Extracted facts:
- 102 cm arm length;
- 1.1 kg;
- chrome-plated steel arm;
- fixed aluminum grip head;
- hole diameters 6.4 / 9.5 / 12.7 / 16 mm.

Trust: `PRIMARY / VERIFIED`.
Historical Sensetique identity: `UNPROVEN`.

### A0040CS Baby Stand 40

Manufacturer page:
https://www.manfrotto.com/global-uk/baby-stand-40-steel-a0040cs/

Extracted facts:
- max 400 cm;
- min 142 cm;
- closed 124 cm;
- 8 kg class;
- payload 9 kg;
- 4 sections / 3 risers;
- tube diameters 35 / 30 / 25 / 20 mm;
- square legs 20 x 20 mm;
- one leveling leg;
- 16 mm top;
- chrome steel.

Trust: `PRIMARY / VERIFIED`.
Historical Sensetique identity: `UNPROVEN`.

### G200-1 Sand Bag 10 kg

Manufacturer page:
https://www.manfrotto.com/global-es/sand-bag-10kg-g200-1/

Extracted facts:
- 10 kg filled/load class;
- 0.28 kg empty product mass;
- black synthetic textile;
- sand not included.

Trust: `PRIMARY / VERIFIED BASIC`.
Exact filled envelope: `UNKNOWN`.
Historical Sensetique identity: `UNPROVEN`.

### D600 Mini Boom

Manufacturer page:
https://www.manfrotto.com/ca-en/mini-boom-arm-with-sliding-attachment-d600/

Manufacturer prose states approximately:
- 117 cm minimum extension;
- 212 cm maximum extension;
- 30 kg capacity at minimum extension;
- 7 kg at full extension;
- mass 3.7 kg.

However current structured fields on regional pages appear reversed/malformed for min/max extension. Before modeling, inspect the spare-parts drawing/brochure listed by the manufacturer.

Trust: `PRIMARY / CONFLICT WITHIN PAGE`.
Modeling gate: `FAIL / RESEARCH_MORE`.

---

## Dedolight envelope corroboration

Technical reseller page:
https://bceromania.ro/produse/dedolight-dlhm4-300-dlhm4-300-focusing-light-head-with-dimmable-power-supply

Extracted facts:
- dimensions given as `171 x 132 x 174 mm`;
- mass 1.02 kg;
- 150 W / 24 V;
- focus 4.5° to 48°;
- integrated transformer/dimmer;
- 5 m cable in this regional kit;
- 16 mm / 5/8 in stand compatibility.

Trust: `SECONDARY TECHNICAL / CORROBORATED PARTIAL`.

Important: page does not label the axis order of the three dimensions. Until a dimensioned drawing or a second source maps the axes explicitly, keep the value as an unordered envelope triple rather than writing it into Width/Height/Depth fields.

This removes the previous state `no external dimensions at all`, but does **not** yet justify a manufacturer-grade precision gate.

---

## ARRI CAD route

Manufacturer page:
https://www.arri.com/en/lighting/daylight-tungsten/tungsten/arri-junior/arri-300-plus

The manufacturer explicitly exposes:
- 2D DXF CAD drawing;
- 2D DWG CAD drawing;
- user manual;
- exact current bounding measurements;
- lens/accessory diameters.

Next production artifact should be a derived, license-safe dimensional trace from the manufacturer CAD. Do not commit the manufacturer's CAD archive unless redistribution permission is established.
