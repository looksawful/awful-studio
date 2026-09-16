# Character, rig and mocap libraries

AWFUL Studio keeps third-party character assets outside the Git repository. The extension ships only a reviewed catalog and pure discovery/import-planning helpers. Raw third-party character, clothing and mocap payloads are not bundled with the extension.

Default layout under the configured AWFUL Asset Cache Directory:

`characters/cmu_mocap`, `characters/makehuman`, `characters/makehuman_community`, `characters/quaternius/...`, and `characters/actorcore`.

## Sources and policy

- **CMU Motion Capture Database**: free for use, including commercially sold products, but the dataset may not be resold directly even after conversion. Store ASF/AMC files under `characters/cmu_mocap`. Source: https://mocap.cs.cmu.edu/
- **MakeHuman / MPFB core assets**: core graphical assets are CC0. MPFB program code is GPL; do not confuse tool licensing with generated/core graphical assets. Source: https://static.makehumancommunity.org/about/license.html
- **MakeHuman community packs**: licenses can be per-asset. Prefer packs explicitly marked CC0 and retain their metadata. The official curated asset-pack index currently includes CC0 clothing collections such as Dress 01, Pants 01, Shirts 01, Shoes 01, Skirts 01 and Suits packs. Never assume an arbitrary user-contributed asset inherits MakeHuman core licensing. Sources: https://static.makehumancommunity.org/assets/assetpacks.html and https://static.makehumancommunity.org/assets/assetpacks/dress01.html
- **Quaternius Ultimate Modular Men/Women**: CC0, with FBX/OBJ/Blend/glTF variants and included animations. Sources: https://quaternius.com/packs/ultimatemodularcharacters.html and https://quaternius.com/packs/ultimatemodularwomen.html
- **Quaternius Universal Base Characters and compatible Modular Character Outfits - Fantasy**: the free downloadable portion is CC0 and the outfit kit is explicitly compatible with Universal Base Characters. Keep free downloads separate from Source/member extras. Sources: https://quaternius.com/packs/universalbasecharacters.html and https://quaternius.com/packs/modularcharacteroutfitsfantasy.html
- **ActorCore free actors/motions**: useful for Blender and offers free content, but it is Reallusion-licensed content rather than CC0. Keep account-acquired files in the user-owned `characters/actorcore` cache and never commit raw ActorCore assets to AWFUL Studio. Source: https://actorcore.reallusion.com/

The source/licensing statements above were rechecked against the official provider pages on 2026-09-16. Provider terms remain authoritative and should be re-reviewed before changing redistribution behavior.

## Format contract

Each catalog record separates two concepts:

- `formats`: formats that may legitimately exist in that upstream library;
- `import_formats`: formats AWFUL Studio may hand off to a Blender 5.2 import strategy.

This distinction is intentional. CMU ASF/AMC files are discoverable source data but are not advertised as direct Blender imports. MakeHuman community `.mhclo` / `.mhmat` assets stay inside the MakeHuman/MPFB ecosystem and are likewise not emitted as generic Blender import candidates. ActorCore FBX/BVH and the declared Quaternius interchange files can be handed to their Blender strategies. `.blend` is treated as a Blender library operation and `.mhx2` as an external-addon workflow rather than pretending they are ordinary import operators.

`import_candidates()` rejects symlinked files and candidates whose resolved path escapes the selected library root. It performs no network access and no scene mutation. `import_plan()` is also pure and only reports the Blender 5.2 handoff strategy/operator.

## Workflow

1. Set **Asset Cache Directory** in AWFUL Studio preferences.
2. Download/install the chosen upstream library using its official source. Account-gated ActorCore stays a manual/account-owned acquisition step.
3. Put files below the matching `characters/<provider>` directory. `character_library.discover()` reports local availability without network access.
4. Use `import_candidates()` only for files declared in `import_formats`; use `import_plan()` to determine the Blender 5.2 handoff.
5. For MakeHuman, install MPFB as its own Blender extension/add-on and keep MakeHuman assets in its external library. AWFUL Studio does not copy GPL MPFB code into its extension.
6. Convert/retarget CMU ASF/AMC before Blender import. ActorCore FBX/BVH and Quaternius humanoid rigs are the preferred direct interchange path among the reviewed libraries.

The catalog is deliberately metadata-only. Automated downloading is out of this pass: it may be added only for sources with stable direct URLs and redistribution/download terms that permit unattended fetching. Verification for this integration is deliberately render-free.
