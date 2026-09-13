import bpy
import math
import os
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, List
from mathutils import Vector
from bpy.props import EnumProperty, BoolProperty, PointerProperty, StringProperty, IntProperty
from .. import ownership, asset_cache

# ============================================================
# AWFUL STUDIO v4 — PROFESSIONAL PRODUCT / ADVERTISING STUDIO
# Blender 4.5+ / 5.x, designed and calibrated for Cycles.
#
# Philosophy:
# - presets create editable starting points; they do not fight later manual edits
# - all scene-scale decisions come from product metrics + physical min/max rules
# - the N-panel switches systems/presets only; numeric tuning stays in Blender
# - rebuild removes only AWFUL-managed data and preserves user objects
# ============================================================

VERSION = "0.0.16"
ROOT_COLLECTION_NAME = "AWFUL_STUDIO"
MANAGED_KEY = "awful_managed"
ROLE_KEY = "awful_role"
VERSION_KEY = "awful_version"
POST_PIPELINE_KEY = "awful_post_pipeline_enabled"

# ============================================================
# 01 — PHYSICAL CONFIGURATION
# ============================================================

STUDIO_SPEC = {
    "width": 14.0,
    "depth": 18.0,
    "height": 7.0,
    "camera_y": -11.0,
    "background_y": 7.0,
    "wall_thickness": 0.18,
    "floor_offset": 0.04,
    "cyc": {
        "width": 12.0,
        "front_y": -9.5,
        "curve_start_y": 3.0,
        "radius": 3.0,
        "height": 6.5,
        "thickness": 0.08,
    },
    "window": {
        "center_y": -1.3,
        "width": 8.5,
        "bottom_z": 0.55,
        "top_z": 6.15,
        "glass_thickness": 0.008,
        "frame_depth": 0.24,
        "frame_width": 0.12,
    },
    "pedestal": {
        "radius": 1.35,
        "height": 0.50,
    },
    "product_envelope": {
        # Auto Fit normalizes arbitrary imports to a useful studio working size.
        # It does NOT try to fill the entire maximum safe envelope.
        "target_xy": 1.40,
        "target_height": 1.60,
        "max_xy": 2.60,
        "max_height": 3.20,
    },
}

DEFAULT_FPS = 24
DEFAULT_FRAMES = 240
RENDER_X = 1600
RENDER_Y = 2000
RENDER_SAMPLES = 256
PREVIEW_SAMPLES = 16
PREVIEW_ADAPTIVE_THRESHOLD = 0.05

# ============================================================
# 02 — ASSETS
# ============================================================

PAINT_ZIP_FILENAME = "PaintedPlaster017_2K-PNG.zip"
PAINT_ZIP_URL = "https://acg-download.struffelproductions.com/file/ambientCG-Web/download/PaintedPlaster017_kZF8yCTI/PaintedPlaster017_2K-PNG.zip"
PAINT_TARGET_FILES = {
    "paint_color": "painted_plaster017_color.png",
    "paint_ao": "painted_plaster017_ao.png",
    "paint_roughness": "painted_plaster017_roughness.png",
    "paint_normal": "painted_plaster017_normalgl.png",
    "paint_displacement": "painted_plaster017_displacement.png",
}

ASSET_URLS = {
    "hdri_fish_hoek": (
        "fish_hoek_beach_2k.hdr",
        "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/fish_hoek_beach_2k.hdr",
    ),
    "hdri_blouberg": (
        "blouberg_sunrise_2_2k.hdr",
        "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/blouberg_sunrise_2_2k.hdr",
    ),
    "hdri_kloppenheim": (
        "kloppenheim_01_puresky_2k.hdr",
        "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/kloppenheim_01_puresky_2k.hdr",
    ),
    "hdri_belfast": (
        "belfast_sunset_puresky_2k.hdr",
        "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/belfast_sunset_puresky_2k.hdr",
    ),
    "hdri_rogland": (
        "rogland_overcast_2k.hdr",
        "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/rogland_overcast_2k.hdr",
    ),
}

HDRI_PRESETS = {
    "FISH_HOEK": {"asset": "hdri_fish_hoek", "strength": 0.90, "rotation": math.radians(30.0)},
    "BLOUBERG": {"asset": "hdri_blouberg", "strength": 0.82, "rotation": math.radians(120.0)},
    "KLOPPENHEIM": {"asset": "hdri_kloppenheim", "strength": 0.88, "rotation": math.radians(65.0)},
    "BELFAST": {"asset": "hdri_belfast", "strength": 0.78, "rotation": math.radians(205.0)},
    "ROGLAND": {"asset": "hdri_rogland", "strength": 1.00, "rotation": math.radians(20.0)},
}

WORLD_PRESET_ORDER = [
    "FISH_HOEK", "BLOUBERG", "KLOPPENHEIM", "BELFAST", "ROGLAND",
    "NISHITA_DAY", "NISHITA_SUNSET",
]
WORLD_PRESET_LABELS = {
    "FISH_HOEK": "Overcast Beach",
    "BLOUBERG": "Soft Beach Sunrise",
    "KLOPPENHEIM": "Grey Sky + Warm Break",
    "BELFAST": "Calm Sunset",
    "ROGLAND": "Neutral Overcast",
    "NISHITA_DAY": "Physical Sky Day",
    "NISHITA_SUNSET": "Physical Sky Sunset",
}

# ============================================================
# 03 — DATA MODELS / PURE RULES
# ============================================================

@dataclass
class ProductMetrics:
    width: float
    depth: float
    height: float
    half_x: float
    half_y: float
    half_z: float
    scale: float
    center_world: Vector
    bottom_world: float

    @property
    def S(self) -> float:
        return max(self.width, self.depth, self.height, 0.10)

    def basis(self, key: str) -> float:
        return {
            "S": self.S,
            "W": max(self.width, 0.10),
            "D": max(self.depth, 0.10),
            "H": max(self.height, 0.10),
        }.get(key, self.S)


@dataclass(frozen=True)
class DistanceRule:
    factor: float
    minimum: float
    maximum: float
    basis: str = "S"

    def resolve(self, metrics: ProductMetrics) -> float:
        raw = metrics.basis(self.basis) * self.factor
        return max(self.minimum, min(self.maximum, raw))


@dataclass(frozen=True)
class LightSpec:
    role: str
    kind: str = "AREA"
    azimuth: float = 0.0
    elevation: float = 0.0
    distance: DistanceRule = field(default_factory=lambda: DistanceRule(3.0, 2.0, 5.0))
    size_x: DistanceRule = field(default_factory=lambda: DistanceRule(1.4, 1.0, 3.0))
    size_y: DistanceRule = field(default_factory=lambda: DistanceRule(1.4, 1.0, 3.0))
    base_power: float = 120.0
    exposure_ev: float = 0.0
    spread: float = 180.0
    color: Optional[Tuple[float, float, float]] = None
    temperature: Optional[float] = 5600.0
    target: str = "CENTER"
    light_group: str = "LG_KEY"
    linking: Optional[str] = None
    spot_size: float = 50.0
    spot_blend: float = 0.25
    camera_local: bool = False
    absolute_size: Optional[Tuple[float, float]] = None
    local_offset: Tuple[float, float, float] = (0.0, 0.075, -0.040)


@dataclass(frozen=True)
class ShaperSpec:
    role: str
    azimuth: float
    elevation: float
    distance: DistanceRule
    width: DistanceRule
    height: DistanceRule
    depth: float = 0.035
    material: str = "BLACK"
    camera_visible: bool = False


@dataclass(frozen=True)
class LightingPreset:
    id: str
    family: str
    label: str
    lights: Tuple[LightSpec, ...] = ()
    shapers: Tuple[ShaperSpec, ...] = ()
    natural_light: bool = False
    environment: str = "FISH_HOEK"
    room: bool = True
    camera_lens: float = 85.0
    camera_margin: float = 1.32
    flash_backdrop: bool = False
    gobo: bool = False


# ============================================================
# 04 — PRESET DATABASE
# ============================================================

COLOR_WARM = (1.0, 0.44, 0.14)
COLOR_AMBER = (1.0, 0.24, 0.035)
COLOR_TEAL = (0.015, 0.38, 0.60)
COLOR_CYAN = (0.015, 0.66, 1.00)
COLOR_MAGENTA = (1.0, 0.025, 0.30)
COLOR_RED = (1.0, 0.008, 0.015)
COLOR_BLUE = (0.020, 0.12, 1.0)
COLOR_MOON = (0.055, 0.16, 1.0)

R_SOFT = DistanceRule(3.2, 2.4, 5.5)
R_FILL = DistanceRule(3.6, 2.8, 6.0)
R_STRIP = DistanceRule(2.8, 2.0, 4.6)
R_HARD = DistanceRule(4.0, 3.0, 7.0)
SZ_SOFT = DistanceRule(1.8, 1.4, 3.6)
SZ_FILL = DistanceRule(2.2, 1.8, 4.2)
SZ_STRIP_W = DistanceRule(0.28, 0.28, 0.60, "W")
SZ_STRIP_H = DistanceRule(2.1, 1.6, 4.6, "H")
SZ_SMALL = DistanceRule(0.65, 0.55, 1.25)

BLACK_LEFT = ShaperSpec("FLAG_Black_L", -92, 0, DistanceRule(1.6, 1.2, 2.8), DistanceRule(0.9, 0.8, 1.8), DistanceRule(1.8, 1.6, 3.8, "H"), material="BLACK")
BLACK_RIGHT = ShaperSpec("FLAG_Black_R", 92, 0, DistanceRule(1.6, 1.2, 2.8), DistanceRule(0.9, 0.8, 1.8), DistanceRule(1.8, 1.6, 3.8, "H"), material="BLACK")
WHITE_LEFT = ShaperSpec("CARD_White_L", -92, 0, DistanceRule(1.7, 1.3, 3.0), DistanceRule(1.0, 0.9, 2.0), DistanceRule(1.9, 1.7, 4.0, "H"), material="WHITE")
WHITE_RIGHT = ShaperSpec("CARD_White_R", 92, 0, DistanceRule(1.7, 1.3, 3.0), DistanceRule(1.0, 0.9, 2.0), DistanceRule(1.9, 1.7, 4.0, "H"), material="WHITE")

LIGHTING_PRESETS: Dict[str, LightingPreset] = {}

def add_preset(p: LightingPreset):
    LIGHTING_PRESETS[p.id] = p

# 01 Commercial Soft / 3-light
add_preset(LightingPreset(
    "COMMERCIAL_3LIGHT", "COMMERCIAL", "Classic 3-Light",
    lights=(
        LightSpec("LIGHT_Key", azimuth=-42, elevation=27, distance=R_SOFT, size_x=SZ_SOFT, size_y=SZ_SOFT, base_power=120, exposure_ev=2.0, spread=125, target="LABEL", light_group="LG_KEY"),
        LightSpec("LIGHT_Fill", azimuth=38, elevation=17, distance=R_FILL, size_x=SZ_FILL, size_y=SZ_FILL, base_power=120, exposure_ev=-0.2, spread=170, target="CENTER", light_group="LG_FILL"),
        LightSpec("LIGHT_Rim", azimuth=142, elevation=24, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.0, spread=78, target="CENTER", light_group="LG_RIM"),
    ), camera_lens=85.0,
))

# 02 Top soft packshot
add_preset(LightingPreset(
    "TOP_SOFT_PACKSHOT", "COMMERCIAL", "Top Soft Packshot",
    lights=(
        LightSpec("LIGHT_Top", azimuth=0, elevation=78, distance=DistanceRule(2.7, 2.6, 5.0), size_x=DistanceRule(2.4, 2.0, 4.5), size_y=DistanceRule(2.0, 1.8, 4.0), base_power=120, exposure_ev=1.8, spread=165, target="TOP", light_group="LG_KEY"),
        LightSpec("LIGHT_Fill", azimuth=0, elevation=5, distance=R_FILL, size_x=SZ_FILL, size_y=DistanceRule(1.3, 1.2, 2.8), base_power=120, exposure_ev=-1.4, spread=180, target="LABEL", light_group="LG_FILL"),
    ), shapers=(WHITE_LEFT, WHITE_RIGHT), camera_lens=70.0,
))

# 03 Dual rear strips
add_preset(LightingPreset(
    "DUAL_STRIP_HERO", "COMMERCIAL", "Dual Strip Hero",
    lights=(
        LightSpec("LIGHT_Strip_L", azimuth=-136, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.4, spread=72, target="CENTER", light_group="LG_STRIPS"),
        LightSpec("LIGHT_Strip_R", azimuth=136, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.4, spread=72, target="CENTER", light_group="LG_STRIPS"),
        LightSpec("LIGHT_Key", azimuth=0, elevation=8, distance=DistanceRule(3.0, 2.5, 5.2), size_x=SZ_SMALL, size_y=DistanceRule(0.8, 0.70, 1.5), base_power=120, exposure_ev=-0.8, spread=78, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
    ), shapers=(BLACK_LEFT, BLACK_RIGHT), camera_lens=100.0,
))

# 04 Glossy hero
add_preset(LightingPreset(
    "FOUR_LIGHT_GLOSSY", "COMMERCIAL", "Four-Light Glossy Hero",
    lights=(
        LightSpec("LIGHT_Key", azimuth=-18, elevation=18, distance=R_SOFT, size_x=DistanceRule(1.0, 0.9, 2.0), size_y=DistanceRule(1.2, 1.0, 2.5), base_power=120, exposure_ev=0.4, spread=82, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
        LightSpec("LIGHT_Strip_L", azimuth=-140, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.2, spread=65, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Strip_R", azimuth=140, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.2, spread=65, light_group="LG_STRIPS"),
        LightSpec("LIGHT_BG", kind="SPOT", azimuth=0, elevation=30, distance=DistanceRule(3.0, 2.5, 5.0), base_power=120, exposure_ev=0.8, target="BACKGROUND", light_group="LG_BACKGROUND", linking="BACKGROUND", spot_size=62, spot_blend=0.58),
    ), shapers=(BLACK_LEFT, BLACK_RIGHT), camera_lens=100.0,
))

# 05 Backlit glass / bottle
add_preset(LightingPreset(
    "BACKLIT_GLASS", "COMMERCIAL", "Backlit Glass / Bottle",
    lights=(
        LightSpec("LIGHT_Back", azimuth=180, elevation=6, distance=DistanceRule(3.0, 2.5, 5.0), size_x=DistanceRule(2.6, 2.2, 5.0), size_y=DistanceRule(2.4, 2.2, 5.0, "H"), base_power=120, exposure_ev=2.0, spread=170, light_group="LG_RIM"),
        LightSpec("LIGHT_Key", azimuth=0, elevation=7, distance=R_SOFT, size_x=SZ_SMALL, size_y=DistanceRule(0.9, 0.8, 1.6), base_power=120, exposure_ev=-1.2, spread=70, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
    ),
    shapers=(
        ShaperSpec("DIFFUSION_Back", 180, 4, DistanceRule(1.8, 1.5, 3.0), DistanceRule(2.7, 2.2, 5.2), DistanceRule(2.5, 2.2, 5.0, "H"), 0.004, "DIFFUSION"),
        BLACK_LEFT, BLACK_RIGHT,
    ), camera_lens=85.0,
))

# 06 Direct flash
add_preset(LightingPreset(
    "DIRECT_FLASH", "FLASH", "Direct Camera Flash",
    lights=(
        LightSpec("LIGHT_CameraFlash", camera_local=True, absolute_size=(0.070, 0.045), base_power=180, exposure_ev=3.6, spread=50, light_group="LG_FLASH"),
    ), camera_lens=50.0, camera_margin=1.22, flash_backdrop=True,
))

# 07 Wide flash
add_preset(LightingPreset(
    "DIRECT_FLASH_WIDE", "FLASH", "Direct Flash Wide",
    lights=(
        LightSpec("LIGHT_CameraFlash", camera_local=True, absolute_size=(0.070, 0.045), base_power=180, exposure_ev=3.4, spread=58, light_group="LG_FLASH"),
    ), camera_lens=35.0, camera_margin=1.15, flash_backdrop=True,
))

# 08 Flash + colored ambient
add_preset(LightingPreset(
    "DIRECT_FLASH_COLOR", "FLASH", "Direct Flash + Color Ambient",
    lights=(
        LightSpec("LIGHT_CameraFlash", camera_local=True, absolute_size=(0.070, 0.045), base_power=180, exposure_ev=3.2, spread=52, light_group="LG_FLASH"),
        LightSpec("LIGHT_Accent_L", azimuth=-112, elevation=12, distance=R_STRIP, size_x=DistanceRule(0.5, 0.45, 1.0), size_y=SZ_STRIP_H, base_power=120, exposure_ev=-0.2, spread=92, color=COLOR_CYAN, temperature=None, light_group="LG_FX"),
        LightSpec("LIGHT_Accent_R", azimuth=112, elevation=12, distance=R_STRIP, size_x=DistanceRule(0.5, 0.45, 1.0), size_y=SZ_STRIP_H, base_power=120, exposure_ev=-0.2, spread=92, color=COLOR_MAGENTA, temperature=None, light_group="LG_FX"),
    ), camera_lens=50.0, camera_margin=1.20, flash_backdrop=True,
))

# 09 Cyan/Magenta rear strips
add_preset(LightingPreset(
    "DUAL_COLOR_STRIP", "CINEMA", "Dual Color Strip",
    lights=(
        LightSpec("LIGHT_Strip_L", azimuth=-136, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.2, spread=70, color=COLOR_CYAN, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Strip_R", azimuth=136, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=1.2, spread=70, color=COLOR_MAGENTA, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Key", azimuth=0, elevation=8, distance=R_SOFT, size_x=SZ_SMALL, size_y=DistanceRule(0.9, 0.8, 1.8), base_power=120, exposure_ev=-0.8, spread=76, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
    ), camera_lens=85.0,
))

# 10 Teal / orange
add_preset(LightingPreset(
    "TEAL_ORANGE", "CINEMA", "Teal / Orange",
    lights=(
        LightSpec("LIGHT_Key", azimuth=-48, elevation=24, distance=R_SOFT, size_x=DistanceRule(1.1, 1.0, 2.2), size_y=DistanceRule(1.3, 1.1, 2.7), base_power=120, exposure_ev=1.1, spread=92, color=COLOR_WARM, temperature=None, target="LABEL", light_group="LG_KEY"),
        LightSpec("LIGHT_Accent_R", azimuth=142, elevation=15, distance=R_STRIP, size_x=DistanceRule(0.45, 0.38, 0.9), size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.9, spread=72, color=COLOR_TEAL, temperature=None, light_group="LG_FX"),
        LightSpec("LIGHT_BG", kind="SPOT", azimuth=165, elevation=28, distance=R_HARD, base_power=120, exposure_ev=-0.2, color=COLOR_TEAL, temperature=None, target="BACKGROUND", light_group="LG_BACKGROUND", linking="BACKGROUND", spot_size=70, spot_blend=0.65),
    ), shapers=(BLACK_RIGHT,), camera_lens=75.0,
))

# 11 Sodium / moonlight
add_preset(LightingPreset(
    "SODIUM_MOON", "CINEMA", "Sodium / Moonlight",
    lights=(
        LightSpec("LIGHT_Hard", azimuth=-58, elevation=32, distance=R_HARD, size_x=DistanceRule(0.20, 0.18, 0.35), size_y=DistanceRule(0.20, 0.18, 0.35), base_power=120, exposure_ev=1.7, spread=48, color=COLOR_AMBER, temperature=None, target="LABEL", light_group="LG_FX"),
        LightSpec("LIGHT_Accent_R", azimuth=145, elevation=22, distance=R_STRIP, size_x=DistanceRule(0.45, 0.40, 0.9), size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.7, spread=75, color=COLOR_MOON, temperature=None, light_group="LG_FX"),
        LightSpec("LIGHT_Fill", azimuth=25, elevation=8, distance=R_FILL, size_x=SZ_FILL, size_y=SZ_FILL, base_power=120, exposure_ev=-2.0, spread=175, color=COLOR_BLUE, temperature=None, light_group="LG_FILL"),
    ), camera_lens=75.0,
))

# 12 Red / black luxury
add_preset(LightingPreset(
    "RED_BLACK_LUXURY", "CINEMA", "Red / Black Luxury",
    lights=(
        LightSpec("LIGHT_Key", azimuth=0, elevation=10, distance=R_SOFT, size_x=DistanceRule(0.65, 0.55, 1.3), size_y=DistanceRule(0.95, 0.8, 1.8), base_power=120, exposure_ev=-0.2, spread=62, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
        LightSpec("LIGHT_Strip_L", azimuth=-138, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.9, spread=65, color=COLOR_RED, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Strip_R", azimuth=138, elevation=5, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.9, spread=65, color=COLOR_RED, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_BG", kind="SPOT", azimuth=180, elevation=22, distance=R_HARD, base_power=120, exposure_ev=0.6, color=COLOR_RED, temperature=None, target="BACKGROUND", light_group="LG_BACKGROUND", linking="BACKGROUND", spot_size=64, spot_blend=0.72),
    ), shapers=(BLACK_LEFT, BLACK_RIGHT), camera_lens=100.0,
))

# 13 Blue tech
add_preset(LightingPreset(
    "BLUE_TECH", "CINEMA", "Blue Tech",
    lights=(
        LightSpec("LIGHT_Strip_L", azimuth=-138, elevation=7, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.9, spread=70, color=COLOR_BLUE, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Strip_R", azimuth=138, elevation=7, distance=R_STRIP, size_x=SZ_STRIP_W, size_y=SZ_STRIP_H, base_power=120, exposure_ev=0.9, spread=70, color=COLOR_CYAN, temperature=None, light_group="LG_STRIPS"),
        LightSpec("LIGHT_Top", azimuth=0, elevation=76, distance=DistanceRule(2.8, 2.8, 5.2), size_x=DistanceRule(1.5, 1.4, 3.0), size_y=DistanceRule(1.5, 1.4, 3.0), base_power=120, exposure_ev=0.2, spread=128, target="TOP", light_group="LG_KEY"),
        LightSpec("LIGHT_Key", azimuth=0, elevation=7, distance=R_SOFT, size_x=SZ_SMALL, size_y=DistanceRule(0.8, 0.75, 1.6), base_power=120, exposure_ev=-1.1, spread=68, target="LABEL", light_group="LG_KEY", linking="PRODUCT"),
    ), camera_lens=85.0,
))

# 14 Hard gobo
add_preset(LightingPreset(
    "HARD_GOBO", "CINEMA", "Hard Sun / Gobo",
    lights=(
        LightSpec("LIGHT_Gobo", kind="SPOT", azimuth=-38, elevation=38, distance=R_HARD, base_power=120, exposure_ev=2.0, temperature=5200, target="BACKGROUND", light_group="LG_FX", linking="BACKGROUND", spot_size=44, spot_blend=0.06),
        LightSpec("LIGHT_Key", azimuth=-35, elevation=20, distance=R_SOFT, size_x=DistanceRule(0.55, 0.50, 1.1), size_y=DistanceRule(0.75, 0.70, 1.5), base_power=120, exposure_ev=-0.5, spread=64, target="LABEL", light_group="LG_KEY"),
        LightSpec("LIGHT_Fill", azimuth=48, elevation=10, distance=R_FILL, size_x=SZ_FILL, size_y=SZ_FILL, base_power=120, exposure_ev=-2.3, spread=180, light_group="LG_FILL"),
    ), camera_lens=75.0, gobo=True,
))

# 15 Natural window + negative fill
add_preset(LightingPreset(
    "WINDOW_NEG_FILL", "NATURAL", "Window + Negative Fill",
    lights=(), shapers=(BLACK_RIGHT,), natural_light=True, environment="FISH_HOEK", camera_lens=85.0,
))

# 16 Natural balanced
add_preset(LightingPreset(
    "WINDOW_BALANCED", "NATURAL", "Window Balanced",
    lights=(
        LightSpec("LIGHT_Fill", azimuth=42, elevation=12, distance=R_FILL, size_x=SZ_FILL, size_y=SZ_FILL, base_power=120, exposure_ev=-2.5, spread=180, target="CENTER", light_group="LG_FILL"),
    ), shapers=(WHITE_RIGHT,), natural_light=True, environment="KLOPPENHEIM", camera_lens=85.0,
))

LIGHT_FAMILY_ORDER = ["COMMERCIAL", "FLASH", "CINEMA", "NATURAL"]
LIGHT_FAMILY_LABELS = {"COMMERCIAL": "Commercial", "FLASH": "Flash", "CINEMA": "Cinema", "NATURAL": "Natural"}
LIGHT_FAMILY_PRESETS = {
    family: [p.id for p in LIGHTING_PRESETS.values() if p.family == family]
    for family in LIGHT_FAMILY_ORDER
}
LIGHT_PRESET_LABELS = {key: value.label for key, value in LIGHTING_PRESETS.items()}

PRODUCT_PRESET_ORDER = ["STATIC", "SPIN_Z", "SPIN_X", "SPIN_Y", "FLOAT_SPIN", "HERO_REVEAL", "TUMBLE", "PENDULUM", "ORBIT_BOB", "BREATH"]
PRODUCT_PRESET_LABELS = {
    "STATIC": "Static", "SPIN_Z": "Spin Z", "SPIN_X": "Spin X", "SPIN_Y": "Spin Y",
    "FLOAT_SPIN": "Float + Spin", "HERO_REVEAL": "Hero Reveal", "TUMBLE": "Tumble",
    "PENDULUM": "Pendulum", "ORBIT_BOB": "Orbit + Bob", "BREATH": "Breath",
}
CAMERA_PRESET_ORDER = ["STATIC", "CUSTOM_PATH", "ARC_LR", "ARC_RL", "VERTICAL_ARC", "PUSH_IN", "PULL_OUT", "DOLLY_ZOOM_IN", "DOLLY_ZOOM_OUT", "ORBIT_PUSH", "ORBIT_RISE", "HERO_ARC", "FIGURE_8"]
CAMERA_PRESET_LABELS = {
    "STATIC": "Static", "CUSTOM_PATH": "Custom Path", "ARC_LR": "Arc Left → Right", "ARC_RL": "Arc Right → Left",
    "VERTICAL_ARC": "Vertical Arc", "PUSH_IN": "Push In", "PULL_OUT": "Pull Out", "DOLLY_ZOOM_IN": "Dolly Zoom In",
    "DOLLY_ZOOM_OUT": "Dolly Zoom Out", "ORBIT_PUSH": "Orbit + Push", "ORBIT_RISE": "Orbit + Rise", "HERO_ARC": "Hero Arc", "FIGURE_8": "Figure 8",
}

LIGHT_BANK_ROLES = (
    "LIGHT_Key", "LIGHT_Fill", "LIGHT_Rim", "LIGHT_Top", "LIGHT_Back", "LIGHT_BG",
    "LIGHT_Strip_L", "LIGHT_Strip_R", "LIGHT_Accent_L", "LIGHT_Accent_R", "LIGHT_Hard", "LIGHT_Gobo", "LIGHT_CameraFlash",
)
SHAPER_ROLES = (
    "CARD_White_L", "CARD_White_R", "CARD_White_Top",
    "FLAG_Black_L", "FLAG_Black_R", "FLAG_Black_Top",
    "DIFFUSION_Back", "DIFFUSION_Top", "FLASH_Backdrop", "GOBO_ROOT",
)
LIGHT_GROUPS = ("LG_KEY", "LG_FILL", "LG_RIM", "LG_STRIPS", "LG_BACKGROUND", "LG_FLASH", "LG_FX", "LG_WORLD")

# ============================================================
# 05 — CAPABILITIES / COMPATIBILITY
# ============================================================

ALLOWED_EMPTY_DISPLAY_TYPES = {"PLAIN_AXES", "ARROWS", "SINGLE_ARROW", "CIRCLE", "CUBE", "SPHERE", "CONE", "IMAGE"}


def safe_set(target, attr, value):
    if target is None or not hasattr(target, attr):
        return False
    try:
        setattr(target, attr, value)
        return True
    except Exception:
        return False


def detect_blender_capabilities():
    caps = {
        "blender_version": tuple(bpy.app.version),
        "light_exposure": hasattr(bpy.types.Light, "exposure"),
        "object_lightgroup": hasattr(bpy.types.Object, "lightgroup"),
        "object_light_linking": hasattr(bpy.types.Object, "light_linking"),
        "world_lightgroup": hasattr(bpy.types.World, "lightgroup"),
        "viewlayer_lightgroups": hasattr(bpy.types.ViewLayer, "lightgroups"),
        "compositor_group_api": hasattr(bpy.types.Scene, "compositing_node_group"),
        "khronos_pbr_neutral": False,
        "portal": False,
    }
    # Portal lives on CyclesLightSettings; test on a temporary datablock without linking it.
    try:
        data = bpy.data.lights.new("__AWFUL_CAP_TEST", type="AREA")
        caps["portal"] = bool(getattr(data, "cycles", None) and hasattr(data.cycles, "is_portal"))
        bpy.data.lights.remove(data)
    except Exception:
        pass
    return caps

CAPS = None

# ============================================================
# 06 — MANAGED REGISTRY / COLLECTIONS
# ============================================================


def mark_managed(datablock, role=""):
    return ownership.mark(datablock, role)


def is_managed(datablock):
    try:
        return bool(datablock.get(MANAGED_KEY, False))
    except Exception:
        return False


def ensure_object_mode():
    try:
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass


def parent_keep_world(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


def detach_external_children_from_managed():
    for current in list(bpy.data.objects):
        if is_managed(current):
            continue
        if current.parent and is_managed(current.parent):
            mw = current.matrix_world.copy()
            current.parent = None
            current.matrix_world = mw


def remove_managed_studio():
    ownership.remove(bpy.context.scene)


class StudioRegistry:
    def __init__(self, scene=None):
        # Do not resolve the restricted Blender context during import/register.
        pass

    def object(self, role):
        scene = getattr(bpy.context, "scene", None)
        if scene is None:
            return None
        return next((o for o in scene.objects if ownership.owned(o, scene)
                     and o.get(ROLE_KEY) == role), None)

    def collection(self, role):
        scene = getattr(bpy.context, "scene", None)
        if scene is None:
            return None
        return next((c for c in scene.collection.children_recursive
                     if ownership.owned(c, scene) and c.get(ROLE_KEY) == role), None)

    def material(self, role):
        scene = getattr(bpy.context, "scene", None)
        if scene is None:
            return None
        used = {m for o in scene.objects if ownership.owned(o, scene)
                for m in getattr(o.data, "materials", ()) if m}
        return next((m for m in bpy.data.materials if ownership.owned(m, scene)
                     and m.get(ROLE_KEY) == role and (m.users == 0 or m in used)), None)

    def require_object(self, role):
        result = self.object(role)
        if result is None:
            raise RuntimeError(f"AWFUL Studio object missing: {role}")
        return result


REG = StudioRegistry()


def make_root_collection():
    root = bpy.data.collections.new(ROOT_COLLECTION_NAME)
    mark_managed(root, "ROOT")
    bpy.context.scene.collection.children.link(root)
    return root


def make_child_collection(parent, name, role):
    c = bpy.data.collections.new(name)
    mark_managed(c, role)
    parent.children.link(c)
    return c


def build_collection_tree():
    root = make_root_collection()
    cols = {
        "ROOT": root,
        "PRODUCT": make_child_collection(root, "01_PRODUCT", "COL_PRODUCT"),
        "STAGE": make_child_collection(root, "02_STAGE", "COL_STAGE"),
        "CAMERA": make_child_collection(root, "03_CAMERA", "COL_CAMERA"),
        "LIGHTS": make_child_collection(root, "04_LIGHTS", "COL_LIGHTS"),
        "SHAPERS": make_child_collection(root, "05_SHAPERS", "COL_SHAPERS"),
        "ROOM": make_child_collection(root, "06_ROOM", "COL_ROOM"),
        "WINDOW": make_child_collection(root, "07_WINDOW", "COL_WINDOW"),
        "CONTROLS": make_child_collection(root, "08_CONTROLS", "COL_CONTROLS"),
        "DIAGNOSTICS": make_child_collection(root, "09_DIAGNOSTICS", "COL_DIAGNOSTICS"),
    }
    return cols


def link_object_to_collection(obj, collection):
    for old in list(obj.users_collection):
        try:
            old.objects.unlink(obj)
        except Exception:
            pass
    collection.objects.link(obj)


def add_empty(name, role, location, collection, display="PLAIN_AXES", size=0.4):
    o = bpy.data.objects.new(name, None)
    mark_managed(o, role)
    o.location = location
    o.empty_display_type = display if display in ALLOWED_EMPTY_DISPLAY_TYPES else "PLAIN_AXES"
    o.empty_display_size = size
    collection.objects.link(o)
    return o


def add_damped_track(source, target):
    c = source.constraints.new(type="DAMPED_TRACK")
    c.name = "AWFUL_TRACK"
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    return c


def add_copy_location(source, target, name):
    c = source.constraints.new(type="COPY_LOCATION")
    c.name = name
    c.target = target
    return c


def obj_by_name(name):
    return bpy.data.objects.get(name)

# ============================================================
# 07 — ASSET MANAGER
# ============================================================


def asset_root():
    return str(asset_cache.root())


def hdri_asset_path(key):
    filename, _ = ASSET_URLS[key]
    return os.path.join(asset_root(), "hdri", filename)


def packaged_asset_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets"))


def paint_asset_path(key):
    bundled = os.path.join(packaged_asset_root(), "painted_plaster017", PAINT_TARGET_FILES[key])
    if file_is_valid(bundled):
        return bundled
    return os.path.join(asset_root(), "painted_plaster017", PAINT_TARGET_FILES[key])


def file_is_valid(path):
    try:
        return os.path.exists(path) and os.path.getsize(path) > 4096
    except Exception:
        return False


def download_file(url, path, force=False):
    # All network access is centralized and requires the explicit fetch operator.
    return asset_cache.fetch(url, path, force=force)


def extract_paint_bundle(zip_path, force=False):
    if not file_is_valid(zip_path):
        return False
    out_dir = os.path.join(asset_root(), "painted_plaster017")
    os.makedirs(out_dir, exist_ok=True)
    targets = {k: paint_asset_path(k) for k in PAINT_TARGET_FILES}
    if not force and all(file_is_valid(v) for v in targets.values()):
        return True
    patterns = {
        "paint_color": ("_color.", "_basecolor.", "_albedo.", "_diffuse."),
        "paint_ao": ("_ambientocclusion.", "_ao."),
        "paint_roughness": ("_roughness.",),
        "paint_normal": ("_normalgl.", "_normal-gl.", "_normal_gl."),
        "paint_displacement": ("_displacement.", "_height."),
    }
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            for key, pats in patterns.items():
                destination = targets[key]
                if file_is_valid(destination) and not force:
                    continue
                source = next((n for n in names if any(p in n.lower() for p in pats)), None)
                if source:
                    with zf.open(source) as src, open(destination, "wb") as dst:
                        shutil.copyfileobj(src, dst)
        return all(file_is_valid(targets[k]) for k in ("paint_color", "paint_roughness", "paint_normal", "paint_displacement"))
    except Exception as exc:
        print(f"[AWFUL] paint extraction failed: {exc}")
        return False


def ensure_assets(force=False):
    # Download only the chosen environment, never a whole library.
    pid = bpy.context.scene.awful_studio.world_preset
    if pid not in HDRI_PRESETS:
        return {}
    key = HDRI_PRESETS[pid]["asset"]
    filename, url = ASSET_URLS[key]
    return {key: download_file(url, hdri_asset_path(key), force)}


def load_image(path, non_color=False):
    if not file_is_valid(path):
        return None
    try:
        image = bpy.data.images.load(path, check_existing=False)
        mark_managed(image, "ASSET_IMAGE")
        try:
            image.reload()
        except Exception:
            pass
        if non_color:
            try:
                image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
        return image
    except Exception:
        return None

# ============================================================
# 08 — MATERIAL SYSTEM
# ============================================================


def get_or_create_managed_material(name, role):
    mat = REG.material(role)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mark_managed(mat, role)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    return mat


def make_simple_material(name, role, color, roughness=0.5, metallic=0.0):
    mat = get_or_create_managed_material(name, role)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["IOR"].default_value = 1.5
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def build_painted_material(name, role, wall=False, coord_obj=None):
    """Smooth expensive painted plaster. Texture data is deliberately subtle."""
    mat = get_or_create_managed_material(name, role)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links

    out = nodes.new("ShaderNodeOutputMaterial")
    out.name = "AWFUL_OUTPUT"
    out.location = (900, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "AWFUL_PAINT_SHADER"
    bsdf.location = (620, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["IOR"].default_value = 1.48
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.48

    base_white = (0.78, 0.78, 0.76, 1.0) if not wall else (0.75, 0.75, 0.73, 1.0)
    bsdf.inputs["Base Color"].default_value = base_white
    bsdf.inputs["Roughness"].default_value = 0.48 if not wall else 0.55

    coord = nodes.new("ShaderNodeTexCoord")
    coord.location = (-1100, 0)
    if coord_obj is not None:
        coord.object = coord_obj
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "AWFUL_PAINT_MAPPING"
    mapping.label = "Manual texture scale / rotation"
    mapping.location = (-900, 0)
    mapping.inputs["Scale"].default_value = (1.0 / 1.5, 1.0 / 1.5, 1.0 / 1.5)
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    color_img = load_image(paint_asset_path("paint_color"), False)
    rough_img = load_image(paint_asset_path("paint_roughness"), True)
    normal_img = load_image(paint_asset_path("paint_normal"), True)
    height_img = load_image(paint_asset_path("paint_displacement"), True)

    if color_img and rough_img and normal_img and height_img:
        def image_node(node_name, image, y):
            n = nodes.new("ShaderNodeTexImage")
            n.name = node_name
            n.image = image
            n.location = (-650, y)
            safe_set(n, "projection", "BOX")
            safe_set(n, "projection_blend", 0.20)
            safe_set(n, "extension", "REPEAT")
            links.new(mapping.outputs["Vector"], n.inputs["Vector"])
            return n

        tex_color = image_node("AWFUL_PAINT_COLOR", color_img, 330)
        tex_rough = image_node("AWFUL_PAINT_ROUGH", rough_img, 80)
        tex_normal = image_node("AWFUL_PAINT_NORMAL", normal_img, -170)
        tex_height = image_node("AWFUL_PAINT_HEIGHT", height_img, -420)

        mix = nodes.new("ShaderNodeMixRGB")
        mix.name = "AWFUL_PAINT_COLOR_MIX"
        mix.location = (-100, 300)
        mix.blend_type = "MIX"
        mix.inputs["Fac"].default_value = 0.08 if not wall else 0.12
        mix.inputs[1].default_value = base_white
        links.new(tex_color.outputs["Color"], mix.inputs[2])
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

        rough_range = nodes.new("ShaderNodeMapRange")
        rough_range.name = "AWFUL_PAINT_ROUGHNESS_RANGE"
        rough_range.location = (-90, 80)
        rough_range.inputs["From Min"].default_value = 0.0
        rough_range.inputs["From Max"].default_value = 1.0
        rough_range.inputs["To Min"].default_value = 0.42 if not wall else 0.48
        rough_range.inputs["To Max"].default_value = 0.56 if not wall else 0.64
        links.new(tex_rough.outputs["Color"], rough_range.inputs["Value"])
        links.new(rough_range.outputs["Result"], bsdf.inputs["Roughness"])

        normal = nodes.new("ShaderNodeNormalMap")
        normal.name = "AWFUL_PAINT_NORMAL_MAP"
        normal.location = (-120, -170)
        normal.inputs["Strength"].default_value = 0.07 if not wall else 0.11
        links.new(tex_normal.outputs["Color"], normal.inputs["Color"])

        bump = nodes.new("ShaderNodeBump")
        bump.name = "AWFUL_PAINT_MICRO_BUMP"
        bump.location = (180, -220)
        bump.inputs["Strength"].default_value = 0.07 if not wall else 0.10
        bump.inputs["Distance"].default_value = 0.00035 if not wall else 0.00050
        links.new(normal.outputs["Normal"], bump.inputs["Normal"])
        links.new(tex_height.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.location = (-500, -180)
        noise.inputs["Scale"].default_value = 220.0
        noise.inputs["Detail"].default_value = 2.0
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.location = (150, -180)
        bump.inputs["Strength"].default_value = 0.025
        bump.inputs["Distance"].default_value = 0.0003
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_window_glass_material():
    mat = get_or_create_managed_material("MAT_Window_Glass", "MAT_WINDOW_GLASS")
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.008
    bsdf.inputs["IOR"].default_value = 1.52
    for socket_name in ("Transmission Weight", "Transmission"):
        if socket_name in bsdf.inputs:
            bsdf.inputs[socket_name].default_value = 1.0
            break
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat




def make_diffusion_material():
    """Transmissive studio diffusion sheet for back/top light shapers."""
    mat = get_or_create_managed_material("MAT_Diffusion", "MAT_DIFFUSION")
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "AWFUL_DIFFUSION_SHADER"
    bsdf.inputs["Base Color"].default_value = (0.94, 0.94, 0.92, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.38
    bsdf.inputs["IOR"].default_value = 1.45
    for socket_name in ("Transmission Weight", "Transmission"):
        if socket_name in bsdf.inputs:
            bsdf.inputs[socket_name].default_value = 1.0
            break
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def make_diagnostic_material():
    mat = get_or_create_managed_material("MAT_AWFUL_Diagnostic", "MAT_DIAGNOSTIC")
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.18, 0.20, 0.22, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.31
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["IOR"].default_value = 1.5
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def build_all_materials(coord_obj=None):
    return {
        "cyc": build_painted_material("MAT_Studio_Cyclorama", "MAT_CYC", wall=False, coord_obj=coord_obj),
        "room_bounce": make_simple_material("MAT_Studio_Bounce_White", "MAT_ROOM_BOUNCE", (0.72, 0.72, 0.70), 0.58, 0.0),
        "floor": build_painted_material("MAT_Studio_Floor", "MAT_FLOOR", wall=False, coord_obj=coord_obj),
        "glass": make_window_glass_material(),
        "diagnostic": make_diagnostic_material(),
        "pedestal": make_simple_material("MAT_Pedestal", "MAT_PEDESTAL", (0.055, 0.060, 0.070), 0.34, 0.03),
        "frame": make_simple_material("MAT_Window_Frame", "MAT_WINDOW_FRAME", (0.78, 0.79, 0.80), 0.30, 0.12),
        "white_card": make_simple_material("MAT_Card_White", "MAT_CARD_WHITE", (0.82, 0.82, 0.80), 0.68, 0.0),
        "black_card": make_simple_material("MAT_Card_Black", "MAT_CARD_BLACK", (0.006, 0.006, 0.007), 0.78, 0.0),
        "diffusion": make_diffusion_material(),
    }



def refresh_material_assets():
    """Reload downloaded PBR images without erasing the user's material tuning.

    If the studio was originally built offline and therefore uses procedural
    fallback paint, upgrade the cyclorama paint once the maps exist.
    """
    coord_obj = REG.object("MATERIAL_COORDS")
    image_specs = {
        "AWFUL_PAINT_COLOR": ("paint_color", False),
        "AWFUL_PAINT_ROUGH": ("paint_roughness", True),
        "AWFUL_PAINT_NORMAL": ("paint_normal", True),
        "AWFUL_PAINT_HEIGHT": ("paint_displacement", True),
    }
    for role, wall in (("MAT_CYC", False), ("MAT_FLOOR", False)):
        mat = REG.material(role)
        if not mat or not mat.use_nodes:
            continue
        nodes = mat.node_tree.nodes
        has_texture_stack = nodes.get("AWFUL_PAINT_COLOR") is not None
        maps_ready = all(file_is_valid(paint_asset_path(key)) for key, _nc in image_specs.values())
        if maps_ready and not has_texture_stack:
            # Offline fallback -> PBR upgrade. This one-time rebuild is deliberate.
            build_painted_material(mat.name, role, wall=wall, coord_obj=coord_obj)
            continue
        for node_name, (key, non_color) in image_specs.items():
            node = nodes.get(node_name)
            if node is not None:
                image = load_image(paint_asset_path(key), non_color)
                if image is not None:
                    node.image = image

# ============================================================
# 09 — GEOMETRY SYSTEM
# ============================================================


def set_ray_visibility(o, camera=False, diffuse=True, glossy=True, transmission=True, shadow=True):
    safe_set(o, "visible_camera", camera)
    safe_set(o, "visible_diffuse", diffuse)
    safe_set(o, "visible_glossy", glossy)
    safe_set(o, "visible_transmission", transmission)
    safe_set(o, "visible_shadow", shadow)
    safe_set(o, "visible_volume_scatter", True)


def add_box(name, role, location, dimensions, collection, material=None, camera_visible=False):
    bpy.ops.mesh.primitive_cube_add(location=location)
    o = bpy.context.object
    o.name = name
    mark_managed(o, role)
    mark_managed(o.data, role + "_MESH")
    o.scale = (dimensions[0] * 0.5, dimensions[1] * 0.5, dimensions[2] * 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object_to_collection(o, collection)
    if material:
        o.data.materials.append(material)
    set_ray_visibility(o, camera_visible, True, True, True, True)
    return o


def add_room_shell(name, role, location, dimensions, collection, material):
    o = add_box(name, role, location, dimensions, collection, material, camera_visible=False)
    o.display_type = "WIRE"
    o.hide_select = True
    return o


def build_cyclorama(collection, material):
    cyc = STUDIO_SPEC["cyc"]
    half = cyc["width"] * 0.5
    profile = [(cyc["front_y"], 0.0), (cyc["curve_start_y"], 0.0)]
    for i in range(1, 65):
        t = i / 64.0
        angle = math.radians(-90.0 + 90.0 * t)
        y = cyc["curve_start_y"] + cyc["radius"] * math.cos(angle)
        z = cyc["radius"] + cyc["radius"] * math.sin(angle)
        profile.append((y, z))
    profile.append((cyc["curve_start_y"] + cyc["radius"], cyc["height"]))

    verts = []
    for x in (-half, half):
        for y, z in profile:
            verts.append((x, y, z))
    n = len(profile)
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    mesh = bpy.data.meshes.new("MESH_Cyclorama")
    mark_managed(mesh, "CYC_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new("CYC_Cyclorama", mesh)
    mark_managed(o, "CYC")
    collection.objects.link(o)
    for poly in mesh.polygons:
        poly.use_smooth = True
    o.data.materials.append(material)
    return o


def build_pedestal(collection, material):
    spec = STUDIO_SPEC["pedestal"]
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=spec["radius"], depth=spec["height"], location=(0, 0, spec["height"] * 0.5))
    o = bpy.context.object
    o.name = "GEO_Pedestal"
    mark_managed(o, "PEDESTAL")
    mark_managed(o.data, "PEDESTAL_MESH")
    link_object_to_collection(o, collection)
    bevel = o.modifiers.new("Bevel", "BEVEL")
    bevel.width = 0.045
    bevel.segments = 4
    o.data.materials.append(material)
    return o


def build_room(room_col, window_col, wall_mat, frame_mat, glass_mat):
    width, depth, height = STUDIO_SPEC["width"], STUDIO_SPEC["depth"], STUDIO_SPEC["height"]
    half_w = width * 0.5
    camera_y, bg_y = STUDIO_SPEC["camera_y"], STUDIO_SPEC["background_y"]
    center_y = (camera_y + bg_y) * 0.5
    thick = STUDIO_SPEC["wall_thickness"]
    floor_offset = STUDIO_SPEC["floor_offset"]

    add_room_shell("ROOM_Right", "ROOM_RIGHT", (half_w, center_y, height * 0.5), (thick, depth, height), room_col, wall_mat)
    add_room_shell("ROOM_CameraSide", "ROOM_CAMERA", (0, camera_y, height * 0.5), (width, thick, height), room_col, wall_mat)
    # Close the world-facing background side as well. The cyclorama is a visible
    # interior surface, not a substitute for the physical room shell; without this
    # wall HDRI light leaks into the studio from behind the cove and defeats the window.
    add_room_shell("ROOM_BackgroundWall", "ROOM_BACKGROUND", (0, bg_y, height * 0.5), (width, thick, height), room_col, wall_mat)
    add_room_shell("ROOM_Ceiling", "ROOM_CEILING", (0, center_y, height), (width, depth, thick), room_col, wall_mat)
    add_room_shell("ROOM_Floor", "ROOM_FLOOR", (0, center_y, -floor_offset - thick * 0.5), (width, depth, thick), room_col, wall_mat)

    win = STUDIO_SPEC["window"]
    ymin = win["center_y"] - win["width"] * 0.5
    ymax = win["center_y"] + win["width"] * 0.5
    rear_len = ymin - camera_y
    front_len = bg_y - ymax
    rear_center = (camera_y + ymin) * 0.5
    front_center = (ymax + bg_y) * 0.5
    mid_y = win["center_y"]
    bottom = win["bottom_z"]
    top = win["top_z"]
    mid_z = (bottom + top) * 0.5
    win_h = top - bottom

    add_room_shell("ROOM_Left_Camera", "ROOM_LEFT_CAMERA", (-half_w, rear_center, height * 0.5), (thick, rear_len, height), room_col, wall_mat)
    add_room_shell("ROOM_Left_Background", "ROOM_LEFT_BACKGROUND", (-half_w, front_center, height * 0.5), (thick, front_len, height), room_col, wall_mat)
    add_room_shell("ROOM_Left_WindowBottom", "ROOM_LEFT_WINDOW_BOTTOM", (-half_w, mid_y, bottom * 0.5), (thick, win["width"], bottom), room_col, wall_mat)
    add_room_shell("ROOM_Left_WindowTop", "ROOM_LEFT_WINDOW_TOP", (-half_w, mid_y, top + (height - top) * 0.5), (thick, win["width"], height - top), room_col, wall_mat)

    frame_d = win["frame_depth"]
    frame_w = win["frame_width"]
    x = -half_w + 0.02
    add_box("WINDOW_Frame_Rear", "WINDOW_FRAME", (x, ymin, mid_z), (frame_d, frame_w, win_h), window_col, frame_mat, camera_visible=True)
    add_box("WINDOW_Frame_Front", "WINDOW_FRAME", (x, ymax, mid_z), (frame_d, frame_w, win_h), window_col, frame_mat, camera_visible=True)
    add_box("WINDOW_Frame_Bottom", "WINDOW_FRAME", (x, mid_y, bottom), (frame_d, win["width"], frame_w), window_col, frame_mat, camera_visible=True)
    add_box("WINDOW_Frame_Top", "WINDOW_FRAME", (x, mid_y, top), (frame_d, win["width"], frame_w), window_col, frame_mat, camera_visible=True)

    for idx, yy in enumerate((mid_y - win["width"] / 6.0, mid_y + win["width"] / 6.0), 1):
        add_box(f"WINDOW_Mullion_V{idx}", "WINDOW_FRAME", (x, yy, mid_z), (frame_d, frame_w * 0.85, win_h), window_col, frame_mat, camera_visible=True)
    for idx, zz in enumerate((bottom + win_h / 3.0, bottom + 2.0 * win_h / 3.0), 1):
        add_box(f"WINDOW_Mullion_H{idx}", "WINDOW_FRAME", (x, mid_y, zz), (frame_d, win["width"], frame_w * 0.85), window_col, frame_mat, camera_visible=True)

    glass = add_box("WINDOW_Glass", "WINDOW_GLASS", (-half_w + 0.045, mid_y, mid_z), (win["glass_thickness"], win["width"] - frame_w, win_h - frame_w), window_col, glass_mat, camera_visible=True)
    glass.hide_render = True
    glass.hide_viewport = True
    return glass

# ============================================================
# 10 — PRODUCT SYSTEM / METRICS
# ============================================================


def descendants(root):
    out = []
    for child in root.children:
        out.append(child)
        out.extend(descendants(child))
    return out


def world_bbox(objects):
    points = []
    for o in objects:
        if o.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            continue
        try:
            points.extend(o.matrix_world @ Vector(corner) for corner in o.bound_box)
        except Exception:
            pass
    if not points:
        return None
    mn = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    mx = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mn, mx


def build_product_rig(controls_col, product_col):
    pedestal_top = STUDIO_SPEC["pedestal"]["height"]
    stage_zero = add_empty("STAGE_ZERO", "STAGE_ZERO", (0, 0, 0), controls_col, "PLAIN_AXES", 0.5)
    stage = add_empty("PRODUCT_STAGE", "PRODUCT_STAGE", (0, 0, pedestal_top), controls_col, "PLAIN_AXES", 0.6)
    stage.parent = stage_zero
    motion = add_empty("PRODUCT_MOTION", "PRODUCT_MOTION", (0, 0, 1.0), controls_col, "CIRCLE", 0.8)
    motion.parent = stage
    center = add_empty("PRODUCT_TARGET", "PRODUCT_TARGET", (0, 0, 0), controls_col, "SPHERE", 0.22)
    center.parent = motion
    label = add_empty("TARGET_LABEL", "TARGET_LABEL", (0, 0, 0), controls_col, "SPHERE", 0.18)
    label.parent = motion
    top = add_empty("TARGET_TOP", "TARGET_TOP", (0, 0, 0), controls_col, "SPHERE", 0.18)
    top.parent = motion
    bg = add_empty("TARGET_BACKGROUND", "TARGET_BACKGROUND", (0, STUDIO_SPEC["cyc"]["curve_start_y"] + STUDIO_SPEC["cyc"]["radius"] - 0.25, 2.8), controls_col, "SPHERE", 0.18)
    rz = add_empty("PRODUCT_ROT_Z", "PRODUCT_ROT_Z", (0, 0, 0), controls_col, "CIRCLE", 0.62); rz.parent = motion
    rx = add_empty("PRODUCT_ROT_X", "PRODUCT_ROT_X", (0, 0, 0), controls_col, "CIRCLE", 0.56); rx.parent = rz
    ry = add_empty("PRODUCT_ROT_Y", "PRODUCT_ROT_Y", (0, 0, 0), controls_col, "CIRCLE", 0.50); ry.parent = rx
    geo_root = add_empty("PRODUCT_GEOMETRY_ROOT", "PRODUCT_GEOMETRY_ROOT", (0, 0, 0), product_col, "PLAIN_AXES", 0.35); geo_root.parent = ry
    aim = add_empty("AIM_PRODUCT", "AIM_PRODUCT", (0, 0, pedestal_top + 1.0), controls_col, "SPHERE", 0.24)
    add_copy_location(aim, center, "Aim Copy Location")
    return geo_root


def create_diagnostic_product(diag_col, material):
    root = add_empty("PRODUCT_DIAGNOSTIC_ROOT", "DIAGNOSTIC_ROOT", (0, 0, 0), diag_col, "PLAIN_AXES", 0.30)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.48))
    body = bpy.context.object
    body.name = "PRODUCT_DIAGNOSTIC_BODY"
    mark_managed(body, "DIAGNOSTIC_BODY"); mark_managed(body.data, "DIAGNOSTIC_BODY_MESH")
    body.scale = (0.34, 0.24, 0.48)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object_to_collection(body, diag_col)
    body.parent = root
    bevel = body.modifiers.new("Bevel", "BEVEL"); bevel.width = 0.07; bevel.segments = 6
    body.data.materials.append(material)

    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.18, depth=0.20, location=(0, 0, 1.08))
    cap = bpy.context.object
    cap.name = "PRODUCT_DIAGNOSTIC_CAP"
    mark_managed(cap, "DIAGNOSTIC_CAP"); mark_managed(cap.data, "DIAGNOSTIC_CAP_MESH")
    link_object_to_collection(cap, diag_col)
    cap.parent = root
    bevel = cap.modifiers.new("Bevel", "BEVEL"); bevel.width = 0.035; bevel.segments = 4
    cap.data.materials.append(material)
    return root




def delete_object_hierarchy(root):
    for child in list(root.children):
        if ownership.owned(child, bpy.context.scene):
            delete_object_hierarchy(child)
        else:
            parent_keep_world(child, None)
    if ownership.owned(root, bpy.context.scene):
        bpy.data.objects.remove(root, do_unlink=True)

def current_product_objects():
    content = REG.object("PRODUCT_CONTENT")
    if not content:
        return []
    result = []
    for child in content.children:
        result.append(child)
        result.extend(descendants(child))
    return result


def clear_product_content(delete_managed_children=True):
    content = REG.object("PRODUCT_CONTENT")
    if not content:
        return
    for child in list(content.children):
        if is_managed(child) and delete_managed_children:
            delete_object_hierarchy(child)
        else:
            mw = child.matrix_world.copy()
            child.parent = None
            child.matrix_world = mw
    try:
        bpy.data.objects.remove(content, do_unlink=True)
    except Exception:
        pass


def measure_product(objects, scale=1.0) -> ProductMetrics:
    bbox = world_bbox(objects)
    if bbox is None:
        raise RuntimeError("Selected product contains no measurable geometry")
    mn, mx = bbox
    size = mx - mn
    center = (mn + mx) * 0.5
    return ProductMetrics(
        width=max(size.x * scale, 1e-6), depth=max(size.y * scale, 1e-6), height=max(size.z * scale, 1e-6),
        half_x=max(size.x * scale * 0.5, 1e-6), half_y=max(size.y * scale * 0.5, 1e-6), half_z=max(size.z * scale * 0.5, 1e-6),
        scale=scale, center_world=center, bottom_world=mn.z,
    )


def store_product_metrics(scene, metrics):
    for key in ("width", "depth", "height", "half_x", "half_y", "half_z", "scale", "bottom_world"):
        scene[f"awful_product_{key}"] = float(getattr(metrics, key))


def get_product_metrics(scene) -> ProductMetrics:
    return ProductMetrics(
        width=float(scene.get("awful_product_width", 1.0)), depth=float(scene.get("awful_product_depth", 1.0)), height=float(scene.get("awful_product_height", 1.0)),
        half_x=float(scene.get("awful_product_half_x", 0.5)), half_y=float(scene.get("awful_product_half_y", 0.5)), half_z=float(scene.get("awful_product_half_z", 0.5)),
        scale=float(scene.get("awful_product_scale", 1.0)), center_world=Vector((0, 0, 0)), bottom_world=float(scene.get("awful_product_bottom_world", 0.0)),
    )


def mount_product(root_objects, auto_fit=True):
    if not root_objects:
        raise RuntimeError("No product objects selected")
    if len(root_objects) == 1 and root_objects[0].type == "FONT":
        root_objects[0].rotation_euler.x = math.radians(90.0)
        safe_set(root_objects[0].data, "align_x", "CENTER")
        safe_set(root_objects[0].data, "align_y", "CENTER")
        bpy.context.view_layer.update()

    all_objects = []
    for root in root_objects:
        all_objects.extend([root] + descendants(root))
    raw = measure_product(all_objects, 1.0)

    clear_product_content(delete_managed_children=True)
    geo_root = REG.require_object("PRODUCT_GEOMETRY_ROOT")
    product_col = REG.collection("COL_PRODUCT")
    content = add_empty("PRODUCT_CONTENT", "PRODUCT_CONTENT", raw.center_world, product_col, "PLAIN_AXES", 0.25)
    for root in root_objects:
        parent_keep_world(root, content)
    parent_keep_world(content, geo_root)
    content.location = (0, 0, 0)
    content.rotation_euler = (0, 0, 0)

    scale_factor = 1.0
    if auto_fit:
        env = STUDIO_SPEC["product_envelope"]
        scale_factor = min(env["target_xy"] / max(raw.width, raw.depth, 1e-6), env["target_height"] / max(raw.height, 1e-6))
        content.scale = (scale_factor,) * 3
    metrics = ProductMetrics(
        raw.width * scale_factor, raw.depth * scale_factor, raw.height * scale_factor,
        raw.half_x * scale_factor, raw.half_y * scale_factor, raw.half_z * scale_factor,
        scale_factor, Vector((0, 0, 0)), raw.bottom_world,
    )
    store_product_metrics(bpy.context.scene, metrics)

    motion = REG.require_object("PRODUCT_MOTION")
    motion.location = (0, 0, metrics.half_z)
    label = REG.object("TARGET_LABEL"); top = REG.object("TARGET_TOP"); bg = REG.object("TARGET_BACKGROUND")
    if label: label.location = (0, -metrics.half_y * 0.25, 0)
    if top: top.location = (0, 0, metrics.half_z * 0.45)
    if bg: bg.location.z = max(2.4, STUDIO_SPEC["pedestal"]["height"] + metrics.height * 0.65)
    bpy.context.view_layer.update()
    return metrics

# ============================================================
# 11 — CAMERA SYSTEM
# ============================================================


def build_camera_rig(camera_col, controls_col):
    aim = REG.require_object("AIM_PRODUCT")
    yaw = add_empty("CAMERA_ORBIT_YAW", "CAMERA_YAW", (0, 0, 0), controls_col, "CIRCLE", 0.9)
    add_copy_location(yaw, aim, "Orbit Center")
    pitch = add_empty("CAMERA_ORBIT_PITCH", "CAMERA_PITCH", (0, 0, 0), controls_col, "CIRCLE", 0.78); pitch.parent = yaw
    dolly = add_empty("CAMERA_DOLLY", "CAMERA_DOLLY", (0, -6, 0), controls_col, "SINGLE_ARROW", 0.68); dolly.parent = pitch
    anchor = add_empty("CAMERA_ANCHOR", "CAMERA_ANCHOR", (0, 0, 0), controls_col, "SPHERE", 0.26)
    c = add_copy_location(anchor, dolly, "Anchor From Dolly"); c.influence = 1.0

    cam_data = bpy.data.cameras.new("CAM_Product")
    mark_managed(cam_data, "CAMERA_DATA")
    cam_data.lens = 85.0; cam_data.sensor_width = 36.0; cam_data.dof.use_dof = False
    camera = bpy.data.objects.new("CAM_Product", cam_data)
    mark_managed(camera, "CAMERA")
    camera_col.objects.link(camera)
    camera.parent = anchor
    camera.location = (0, 0, 0)
    add_damped_track(camera, aim)
    bpy.context.scene.camera = camera

    path_data = bpy.data.curves.new("PATH_Camera_Custom", type="CURVE")
    mark_managed(path_data, "CAMERA_PATH_DATA")
    path_data.dimensions = "3D"
    spline = path_data.splines.new("BEZIER"); spline.bezier_points.add(3)
    path = bpy.data.objects.new("PATH_Camera_Custom", path_data)
    mark_managed(path, "CAMERA_PATH")
    camera_col.objects.link(path); path.hide_render = True; path.show_in_front = True
    follower = add_empty("CAMERA_PATH_FOLLOW", "CAMERA_PATH_FOLLOW", (0, 0, 0), controls_col, "PLAIN_AXES", 0.3)
    fp = follower.constraints.new(type="FOLLOW_PATH"); fp.name = "Custom Camera Path"; fp.target = path
    safe_set(fp, "use_fixed_location", True); safe_set(fp, "use_curve_follow", False); safe_set(fp, "offset_factor", 0.0)
    cp = add_copy_location(anchor, follower, "Anchor From Path"); cp.influence = 0.0
    return camera


def compute_camera_base_pose(scene, camera, metrics, lens=85.0, margin=1.32):
    camera.data.lens = float(lens)
    bpy.context.view_layer.update()
    angle_x = max(float(camera.data.angle_x), math.radians(1.0))
    angle_y = max(float(camera.data.angle_y), math.radians(1.0))
    half_w = metrics.width * 0.5 * margin
    half_h = metrics.height * 0.5 * margin
    d_x = half_w / max(math.tan(angle_x * 0.5), 1e-6)
    d_y = half_h / max(math.tan(angle_y * 0.5), 1e-6)
    distance = max(d_x, d_y) + metrics.depth * 0.55
    distance = max(2.2, min(10.0, distance))
    height_offset = metrics.height * 0.08
    scene["awful_camera_base_distance"] = float(distance)
    scene["awful_camera_base_height_offset"] = float(height_offset)
    scene["awful_camera_base_lens"] = float(lens)
    scene["awful_camera_margin"] = float(margin)
    return distance, height_offset


def apply_camera_base_pose(scene, lens=None, margin=None):
    camera = REG.require_object("CAMERA")
    metrics = get_product_metrics(scene)
    if lens is None: lens = float(camera.data.lens)
    if margin is None: margin = float(scene.get("awful_camera_margin", 1.32))
    distance, zoff = compute_camera_base_pose(scene, camera, metrics, lens, margin)
    yaw = REG.require_object("CAMERA_YAW"); pitch = REG.require_object("CAMERA_PITCH"); dolly = REG.require_object("CAMERA_DOLLY")
    yaw.rotation_euler = (0, 0, 0); pitch.rotation_euler = (0, 0, 0); dolly.location = (0, -distance, zoff)
    update_custom_camera_path(scene)


def update_custom_camera_path(scene):
    path = REG.object("CAMERA_PATH")
    aim = REG.object("AIM_PRODUCT")
    if not path or not aim or not path.data.splines:
        return
    distance = float(scene.get("awful_camera_base_distance", 6.0))
    zoff = float(scene.get("awful_camera_base_height_offset", 0.2))
    center = aim.matrix_world.translation
    points = [
        (-distance * 0.34, -distance * 1.04, zoff),
        (-distance * 0.14, -distance * 0.92, zoff + distance * 0.10),
        (distance * 0.14, -distance * 0.92, zoff + distance * 0.10),
        (distance * 0.34, -distance * 1.04, zoff),
    ]
    spline = path.data.splines[0]
    for bp, p in zip(spline.bezier_points, points):
        bp.co = center + Vector(p)
        bp.handle_left_type = "AUTO"; bp.handle_right_type = "AUTO"

# ============================================================
# 12 — WORLD / ENVIRONMENT / PORTAL
# ============================================================


def configure_sky_node(sky, mode):
    for sky_type in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = sky_type
            break
        except Exception:
            pass
    safe_set(sky, "sun_disc", True)
    safe_set(sky, "altitude", 0.0)
    safe_set(sky, "air_density", 1.0)
    safe_set(sky, "dust_density", 1.0)
    safe_set(sky, "aerosol_density", 1.0)
    safe_set(sky, "ozone_density", 1.0)
    safe_set(sky, "ground_albedo", 0.25)
    if mode == "DAY":
        safe_set(sky, "sun_elevation", math.radians(34)); safe_set(sky, "sun_rotation", math.radians(118)); safe_set(sky, "sun_size", math.radians(0.75)); safe_set(sky, "sun_intensity", 0.75); safe_set(sky, "turbidity", 3.2)
    else:
        safe_set(sky, "sun_elevation", math.radians(6.0)); safe_set(sky, "sun_rotation", math.radians(235)); safe_set(sky, "sun_size", math.radians(1.05)); safe_set(sky, "sun_intensity", 0.48); safe_set(sky, "turbidity", 4.8)


def setup_world_nodes():
    scene = bpy.context.scene
    world = bpy.data.worlds.new("WORLD_Awful_Studio")
    mark_managed(world, "WORLD")
    scene.world = world; world.use_nodes = True
    safe_set(world.cycles, "sampling_method", "AUTOMATIC")
    safe_set(world.cycles, "sample_map_resolution", 1024)
    nodes, links = world.node_tree.nodes, world.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld"); out.name = "AWFUL_WORLD_OUTPUT"; out.location = (900, 0)
    path = nodes.new("ShaderNodeLightPath"); path.name = "AWFUL_LIGHT_PATH"; path.location = (300, 260)
    mix = nodes.new("ShaderNodeMixShader"); mix.name = "AWFUL_CAMERA_BACKGROUND_MIX"; mix.location = (650, 0)
    black = nodes.new("ShaderNodeBackground"); black.name = "AWFUL_BG_BLACK"; black.location = (300, -260); black.inputs["Color"].default_value = (0,0,0,1); black.inputs["Strength"].default_value = 0.0
    texcoord = nodes.new("ShaderNodeTexCoord"); texcoord.name = "AWFUL_WORLD_COORDS"; texcoord.location = (-1050, 250)
    mapping = nodes.new("ShaderNodeMapping"); mapping.name = "AWFUL_HDRI_MAPPING"; mapping.label = "Manual HDRI rotation"; mapping.location = (-830, 250)
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    y = 560
    for idx, (pid, data) in enumerate(HDRI_PRESETS.items()):
        env = nodes.new("ShaderNodeTexEnvironment"); env.name = f"AWFUL_ENV_{pid}"; env.location = (-560, y - idx*220)
        # Lazy-load HDRIs. Keeping all five 2K float environments decoded in memory
        # is wasteful for an interactive studio where only one preset is active.
        env.image = None
        links.new(mapping.outputs["Vector"], env.inputs["Vector"])
        bg = nodes.new("ShaderNodeBackground"); bg.name = f"AWFUL_BG_{pid}"; bg.location = (-180, y - idx*220); bg.inputs["Strength"].default_value = data["strength"]
        links.new(env.outputs["Color"], bg.inputs["Color"])
    sky_d = nodes.new("ShaderNodeTexSky"); sky_d.name = "AWFUL_SKY_DAY"; sky_d.location = (-560, -700); configure_sky_node(sky_d, "DAY")
    bg_d = nodes.new("ShaderNodeBackground"); bg_d.name = "AWFUL_BG_NISHITA_DAY"; bg_d.location = (-180, -700); bg_d.inputs["Strength"].default_value = 0.75; links.new(sky_d.outputs["Color"], bg_d.inputs["Color"])
    sky_s = nodes.new("ShaderNodeTexSky"); sky_s.name = "AWFUL_SKY_SUNSET"; sky_s.location = (-560, -920); configure_sky_node(sky_s, "SUNSET")
    bg_s = nodes.new("ShaderNodeBackground"); bg_s.name = "AWFUL_BG_NISHITA_SUNSET"; bg_s.location = (-180, -920); bg_s.inputs["Strength"].default_value = 0.70; links.new(sky_s.outputs["Color"], bg_s.inputs["Color"])
    links.new(path.outputs["Is Camera Ray"], mix.inputs[0]); links.new(black.outputs["Background"], mix.inputs[1]); links.new(black.outputs["Background"], mix.inputs[2]); links.new(mix.outputs["Shader"], out.inputs["Surface"])
    if CAPS and CAPS.get("world_lightgroup"):
        safe_set(world, "lightgroup", "LG_WORLD")
    return world


def relink_input(links, input_socket, output_socket):
    for link in list(input_socket.links):
        links.remove(link)
    links.new(output_socket, input_socket)


def release_inactive_hdri_images(active_preset=None):
    """Keep at most the active AWFUL HDRI attached to the managed World.

    Images are removed from bpy.data only when no other datablock uses them, so a
    professional user can safely reuse an HDRI elsewhere without AWFUL deleting it.
    """
    world = bpy.context.scene.world
    if not world or not world.use_nodes:
        return
    nodes = world.node_tree.nodes
    for pid, data in HDRI_PRESETS.items():
        if pid == active_preset:
            continue
        env = nodes.get(f"AWFUL_ENV_{pid}")
        if not env or env.image is None:
            continue
        image = env.image
        env.image = None
        try:
            if is_managed(image) and image.users == 0:
                expected = os.path.normcase(os.path.abspath(hdri_asset_path(data["asset"])))
                actual = os.path.normcase(os.path.abspath(bpy.path.abspath(image.filepath)))
                if actual == expected:
                    bpy.data.images.remove(image)
        except Exception:
            pass


def apply_environment_preset(scene, preset_id, reset_defaults=True):
    settings = scene.awful_studio
    settings.world_preset = preset_id
    world = scene.world
    if not world or not world.use_nodes:
        return
    nodes, links = world.node_tree.nodes, world.node_tree.links
    black = nodes.get("AWFUL_BG_BLACK"); mix = nodes.get("AWFUL_CAMERA_BACKGROUND_MIX"); out = nodes.get("AWFUL_WORLD_OUTPUT"); path = nodes.get("AWFUL_LIGHT_PATH")
    mapping = nodes.get("AWFUL_HDRI_MAPPING")
    if not all((black, mix, out, path)):
        return
    active = black
    if preset_id in HDRI_PRESETS:
        active = nodes.get(f"AWFUL_BG_{preset_id}") or black
        env = nodes.get(f"AWFUL_ENV_{preset_id}")
        # Decode the environment only when it can actually contribute to the scene.
        if settings.natural_light_enabled and env and env.image is None:
            env.image = load_image(hdri_asset_path(HDRI_PRESETS[preset_id]["asset"]), False)
        if settings.natural_light_enabled and env and env.image is None:
            active = nodes.get("AWFUL_BG_NISHITA_DAY") or black
        release_inactive_hdri_images(preset_id if settings.natural_light_enabled else None)
        if reset_defaults and mapping:
            mapping.inputs["Rotation"].default_value[2] = HDRI_PRESETS[preset_id]["rotation"]
        if reset_defaults and active:
            active.inputs["Strength"].default_value = HDRI_PRESETS[preset_id]["strength"]
    elif preset_id == "NISHITA_DAY":
        active = nodes.get("AWFUL_BG_NISHITA_DAY") or black
    elif preset_id == "NISHITA_SUNSET":
        active = nodes.get("AWFUL_BG_NISHITA_SUNSET") or black
    if not settings.natural_light_enabled:
        active = black
    relink_input(links, mix.inputs[1], active.outputs["Background"])
    camera_bg = active if settings.natural_light_enabled and settings.show_environment_background else black
    relink_input(links, mix.inputs[2], camera_bg.outputs["Background"])
    relink_input(links, mix.inputs[0], path.outputs["Is Camera Ray"])
    relink_input(links, out.inputs["Surface"], mix.outputs["Shader"])
    set_window_portal_enabled(scene, settings.natural_light_enabled and settings.reflective_room_enabled)


def refresh_world_images():
    """Reload only the currently active environment; other HDRIs stay lazy."""
    scene = bpy.context.scene
    world = scene.world
    if not world or not world.use_nodes:
        return
    preset = getattr(getattr(scene, "awful_studio", None), "world_preset", None)
    release_inactive_hdri_images(preset if getattr(scene.awful_studio, "natural_light_enabled", False) else None)
    if preset not in HDRI_PRESETS or not scene.awful_studio.natural_light_enabled:
        return
    env = world.node_tree.nodes.get(f"AWFUL_ENV_{preset}")
    if env:
        old = env.image
        env.image = None
        if old is not None:
            try:
                old.reload()
            except Exception:
                pass
        env.image = load_image(hdri_asset_path(HDRI_PRESETS[preset]["asset"]), False)


def create_window_portal(light_col):
    win = STUDIO_SPEC["window"]
    data = bpy.data.lights.new("LIGHT_Window_Portal", type="AREA")
    mark_managed(data, "WINDOW_PORTAL_DATA")
    data.shape = "RECTANGLE"; data.size = win["width"]; data.size_y = win["top_z"] - win["bottom_z"]; data.energy = 0.0
    if getattr(data, "cycles", None):
        safe_set(data.cycles, "is_portal", True)
    o = bpy.data.objects.new("LIGHT_Window_Portal", data)
    mark_managed(o, "WINDOW_PORTAL")
    light_col.objects.link(o)
    o.location = (-STUDIO_SPEC["width"]*0.5 + 0.08, win["center_y"], (win["bottom_z"] + win["top_z"]) * 0.5)
    direction = Vector((1.0, 0.0, 0.0))
    o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    o.hide_render = True; o.hide_viewport = True
    return o


def set_window_portal_enabled(scene, enabled):
    portal = REG.object("WINDOW_PORTAL")
    if portal:
        portal.hide_render = not enabled
        portal.hide_viewport = not enabled

# ============================================================
# 13 — LIGHT BANK / SHAPERS / RESOLVER
# ============================================================


def set_light_color(data, color=None, temperature=None):
    if color is not None:
        safe_set(data, "use_temperature", False)
        data.color = color
    else:
        data.color = (1.0, 1.0, 1.0)
        if temperature is not None:
            safe_set(data, "use_temperature", True)
            safe_set(data, "temperature", float(temperature))


def create_light(name, role, kind, collection, parent=None, target=None, light_group=""):
    data = bpy.data.lights.new(name, type=kind)
    mark_managed(data, role + "_DATA")
    data.energy = 0.0
    safe_set(data, "use_shadow", True)
    safe_set(data, "exposure", 0.0)
    if getattr(data, "cycles", None):
        safe_set(data.cycles, "use_multiple_importance_sampling", True)
    if kind == "AREA":
        data.shape = "RECTANGLE"; data.size = 1.0; data.size_y = 1.0; safe_set(data, "normalize", True); safe_set(data, "spread", math.radians(180))
    elif kind == "SPOT":
        data.spot_size = math.radians(50); data.spot_blend = 0.25
    o = bpy.data.objects.new(name, data)
    mark_managed(o, role)
    collection.objects.link(o)
    if parent: o.parent = parent
    if target: add_damped_track(o, target)
    if light_group: safe_set(o, "lightgroup", light_group)
    o.hide_render = True; o.hide_viewport = True
    return o


def create_shaper(name, role, collection, material, parent):
    o = add_box(name, role, (0,0,0), (1,0.035,1), collection, material)
    o.parent = parent
    o.hide_render = True; o.hide_viewport = True
    set_ray_visibility(o, False, True, True, True, True)
    return o


def build_light_bank(light_col, controls_col, shaper_col, materials):
    aim = REG.require_object("AIM_PRODUCT")
    camera = REG.require_object("CAMERA")
    rig = add_empty("LIGHT_RIG", "LIGHT_RIG", (0,0,0), controls_col, "CIRCLE", 0.86)
    add_copy_location(rig, aim, "Light Rig Center")
    role_group = {
        "LIGHT_Key":"LG_KEY", "LIGHT_Fill":"LG_FILL", "LIGHT_Rim":"LG_RIM", "LIGHT_Top":"LG_KEY", "LIGHT_Back":"LG_RIM",
        "LIGHT_BG":"LG_BACKGROUND", "LIGHT_Strip_L":"LG_STRIPS", "LIGHT_Strip_R":"LG_STRIPS", "LIGHT_Accent_L":"LG_FX", "LIGHT_Accent_R":"LG_FX",
        "LIGHT_Hard":"LG_FX", "LIGHT_Gobo":"LG_FX", "LIGHT_CameraFlash":"LG_FLASH",
    }
    for role in LIGHT_BANK_ROLES:
        if role == "LIGHT_CameraFlash":
            o = create_light(role, role, "AREA", light_col, camera, None, role_group[role])
            o.location = (0, 0.075, -0.040); o.rotation_euler = (0,0,0)
        else:
            kind = "SPOT" if role in {"LIGHT_BG", "LIGHT_Gobo"} else "AREA"
            target = REG.object("TARGET_BACKGROUND") if role in {"LIGHT_BG", "LIGHT_Gobo"} else aim
            create_light(role, role, kind, light_col, rig, target, role_group[role])

    for role in ("CARD_White_L", "CARD_White_R", "CARD_White_Top"):
        create_shaper(role, role, shaper_col, materials["white_card"], rig)
    for role in ("FLAG_Black_L", "FLAG_Black_R", "FLAG_Black_Top"):
        create_shaper(role, role, shaper_col, materials["black_card"], rig)
    for role in ("DIFFUSION_Back", "DIFFUSION_Top"):
        create_shaper(role, role, shaper_col, materials["diffusion"], rig)
    flash_bg = create_shaper("FLASH_Backdrop", "FLASH_Backdrop", shaper_col, materials["cyc"], rig)
    set_ray_visibility(flash_bg, True, True, True, True, True)

    gobo_root = add_empty("GOBO_ROOT", "GOBO_ROOT", (0,0,0), controls_col, "PLAIN_AXES", 0.35); gobo_root.parent = rig
    for idx in range(7):
        slat = create_shaper(f"GOBO_Slat_{idx+1:02d}", f"GOBO_SLAT_{idx+1:02d}", shaper_col, materials["black_card"], gobo_root)
        set_ray_visibility(slat, False, False, False, False, True)
    return rig


def polar_position(spec: LightSpec, metrics: ProductMetrics):
    distance = spec.distance.resolve(metrics)
    az = math.radians(spec.azimuth); el = math.radians(spec.elevation)
    horizontal = math.cos(el) * distance
    x = math.sin(az) * horizontal
    y = -math.cos(az) * horizontal
    z = math.sin(el) * distance
    return Vector((x, y, z))


def clamp_local_position_to_studio(local_pos, metrics, margin=0.45):
    """Keep generated rig elements inside the physical shell.

    The LIGHT_RIG origin follows the product center, so clamp in world-like
    coordinates and convert Z back to rig-local space.
    """
    center_z = STUDIO_SPEC["pedestal"]["height"] + metrics.half_z
    world = Vector((local_pos.x, local_pos.y, local_pos.z + center_z))
    half_w = STUDIO_SPEC["width"] * 0.5
    world.x = max(-half_w + margin, min(half_w - margin, world.x))
    world.y = max(STUDIO_SPEC["camera_y"] + margin, min(STUDIO_SPEC["background_y"] - margin, world.y))
    world.z = max(margin, min(STUDIO_SPEC["height"] - margin, world.z))
    return Vector((world.x, world.y, world.z - center_z))


def resolve_light_spec(spec: LightSpec, metrics: ProductMetrics):
    if spec.camera_local:
        return {
            "position": Vector(spec.local_offset), "size_x": spec.absolute_size[0], "size_y": spec.absolute_size[1],
            "energy": spec.base_power, "exposure": spec.exposure_ev,
        }
    return {
        "position": clamp_local_position_to_studio(polar_position(spec, metrics), metrics),
        "size_x": spec.size_x.resolve(metrics), "size_y": spec.size_y.resolve(metrics),
        "energy": spec.base_power, "exposure": spec.exposure_ev,
    }


def target_for_name(name):
    return {
        "CENTER": REG.object("AIM_PRODUCT"), "LABEL": REG.object("TARGET_LABEL"), "TOP": REG.object("TARGET_TOP"), "BACKGROUND": REG.object("TARGET_BACKGROUND"),
    }.get(name, REG.object("AIM_PRODUCT"))


def configure_light_from_spec(light, spec, metrics):
    r = resolve_light_spec(spec, metrics)
    if spec.camera_local:
        light.location = r["position"]; light.rotation_euler = (0,0,0)
    else:
        light.location = r["position"]
        track = next((c for c in light.constraints if c.type == "DAMPED_TRACK"), None)
        if track: track.target = target_for_name(spec.target)
    light.data.energy = r["energy"]
    if CAPS and CAPS.get("light_exposure"):
        safe_set(light.data, "exposure", r["exposure"])
    else:
        light.data.energy = r["energy"] * (2.0 ** r["exposure"])
    set_light_color(light.data, spec.color, spec.temperature)
    if spec.kind == "AREA" and light.data.type == "AREA":
        light.data.shape = "RECTANGLE"; light.data.size = max(r["size_x"], 0.001); light.data.size_y = max(r["size_y"], 0.001); safe_set(light.data, "normalize", True); safe_set(light.data, "spread", math.radians(spec.spread))
    elif spec.kind == "SPOT" and light.data.type == "SPOT":
        light.data.spot_size = math.radians(spec.spot_size); light.data.spot_blend = spec.spot_blend
    safe_set(light, "lightgroup", spec.light_group)


def place_shaper(shaper, spec: ShaperSpec, metrics: ProductMetrics):
    distance = spec.distance.resolve(metrics)
    az = math.radians(spec.azimuth); el = math.radians(spec.elevation)
    horizontal = math.cos(el) * distance
    pos = Vector((math.sin(az)*horizontal, -math.cos(az)*horizontal, math.sin(el)*distance))
    pos = clamp_local_position_to_studio(pos, metrics, margin=0.30)
    shaper.location = pos
    direction = -pos
    if direction.length > 1e-6:
        shaper.rotation_euler = direction.to_track_quat("Y", "Z").to_euler()
    width = spec.width.resolve(metrics); height = spec.height.resolve(metrics)
    # create_shaper() has real 1 m × 0.035 m × 1 m mesh dimensions already;
    # assign physical dimensions directly instead of treating it like an unapplied 2 m cube.
    shaper.dimensions = (width, spec.depth, height)
    shaper.hide_render = False; shaper.hide_viewport = False
    set_ray_visibility(shaper, spec.camera_visible, True, True, True, True)


def reset_light_bank():
    for role in LIGHT_BANK_ROLES:
        light = REG.object(role)
        if light:
            light.hide_render = True; light.hide_viewport = True; light["awful_preset_active"] = False
    for role in SHAPER_ROLES:
        shaper = REG.object(role)
        if shaper:
            shaper.hide_render = True; shaper.hide_viewport = True; shaper["awful_preset_active"] = False
    for idx in range(1, 8):
        slat = REG.object(f"GOBO_SLAT_{idx:02d}")
        if slat:
            slat.hide_render = True; slat.hide_viewport = True


def configure_flash_backdrop(metrics):
    o = REG.object("FLASH_Backdrop")
    if not o: return
    distance = max(0.85, min(1.8, metrics.S * 0.9))
    width = max(3.0, min(7.0, metrics.width * 3.8))
    height = max(3.2, min(6.4, metrics.height * 3.2))
    product_center_z = STUDIO_SPEC["pedestal"]["height"] + metrics.half_z
    o.location = (0, distance, height * 0.5 - product_center_z)
    o.rotation_euler = (0,0,0); o.dimensions = (width, 0.05, height)
    o.hide_render = False; o.hide_viewport = False; o["awful_preset_active"] = True


def configure_gobo(metrics, enabled):
    root = REG.object("GOBO_ROOT")
    if not root: return
    if not enabled:
        root.hide_render = True; root.hide_viewport = True
        for i in range(1,8):
            s = REG.object(f"GOBO_SLAT_{i:02d}")
            if s: s.hide_render = True; s.hide_viewport = True
        return
    root.location = (0.0, 3.7, 2.8)
    root.rotation_euler = (0, math.radians(18), math.radians(-12))
    root.hide_render = False; root.hide_viewport = False
    spacing = max(0.42, min(0.90, metrics.width*0.48))
    for idx in range(7):
        s = REG.object(f"GOBO_SLAT_{idx+1:02d}")
        if not s: continue
        s.location = ((idx-3)*spacing, 0, 0); s.rotation_euler = (0,0,0); s.dimensions = (0.20, 0.05, 4.40)
        s.hide_render = False; s.hide_viewport = False


def apply_artificial_master(scene):
    enabled = bool(scene.awful_studio.studio_lights_enabled)
    for role in LIGHT_BANK_ROLES:
        light = REG.object(role)
        if light:
            active = bool(light.get("awful_preset_active", False))
            light.hide_render = not (enabled and active)
            light.hide_viewport = not (enabled and active)


def apply_lighting_preset(scene, preset_id, apply_camera_defaults=False, apply_environment_defaults=True):
    if preset_id not in LIGHTING_PRESETS:
        raise RuntimeError(f"Unknown lighting preset: {preset_id}")
    preset = LIGHTING_PRESETS[preset_id]
    metrics = get_product_metrics(scene)
    settings = scene.awful_studio
    settings.studio_light_preset = preset_id
    settings.studio_light_family = preset.family

    reset_light_bank()
    for spec in preset.lights:
        light = REG.object(spec.role)
        if not light: continue
        configure_light_from_spec(light, spec, metrics)
        light["awful_preset_active"] = True

    for ss in preset.shapers:
        shaper = REG.object(ss.role)
        if shaper:
            place_shaper(shaper, ss, metrics); shaper["awful_preset_active"] = True
    if preset.flash_backdrop:
        configure_flash_backdrop(metrics)
    configure_gobo(metrics, preset.gobo)

    if apply_environment_defaults:
        settings.reflective_room_enabled = preset.room
        settings.natural_light_enabled = preset.natural_light
        settings.world_preset = preset.environment
        # Window glass intentionally remains user-controlled and defaults OFF.
        apply_room_visibility(scene)
        apply_environment_preset(scene, preset.environment, reset_defaults=True)

    if apply_camera_defaults:
        apply_camera_base_pose(scene, preset.camera_lens, preset.camera_margin)

    setup_light_linking_for_preset(preset)
    apply_artificial_master(scene)
    bpy.context.view_layer.update()

# ============================================================
# 14 — LIGHT LINKING / LIGHT GROUPS
# ============================================================


def ensure_link_collection(name, role):
    c = REG.collection(role)
    if c is None:
        c = bpy.data.collections.new(name); mark_managed(c, role)
    return c


def clear_collection_objects(c):
    for o in list(c.objects):
        try: c.objects.unlink(o)
        except Exception: pass


def populate_link_collections():
    product_c = ensure_link_collection("AWFUL_LINK_PRODUCT", "LINK_PRODUCT")
    bg_c = ensure_link_collection("AWFUL_LINK_BACKGROUND", "LINK_BACKGROUND")
    clear_collection_objects(product_c); clear_collection_objects(bg_c)
    for o in current_product_objects():
        if o.type in {"MESH","CURVE","FONT","SURFACE","META"} and o.name not in product_c.objects:
            try: product_c.objects.link(o)
            except Exception: pass
    cyc = REG.object("CYC")
    if cyc:
        try: bg_c.objects.link(cyc)
        except Exception: pass
    return product_c, bg_c


def setup_light_linking_for_preset(preset):
    if not (CAPS and CAPS.get("object_light_linking")):
        return
    product_c, bg_c = populate_link_collections()
    for spec in preset.lights:
        light = REG.object(spec.role)
        if not light or not hasattr(light, "light_linking"):
            continue
        try:
            light.light_linking.receiver_collection = None
            if spec.linking == "PRODUCT": light.light_linking.receiver_collection = product_c
            elif spec.linking == "BACKGROUND": light.light_linking.receiver_collection = bg_c
        except Exception:
            pass


def setup_light_groups(scene):
    if not (CAPS and CAPS.get("viewlayer_lightgroups")):
        return
    view_layer = scene.view_layers[0]
    try:
        existing = {lg.name for lg in view_layer.lightgroups}
    except Exception:
        existing = set()
    for name in LIGHT_GROUPS:
        if name not in existing:
            try: bpy.ops.scene.view_layer_add_lightgroup(name=name)
            except Exception: pass
    try:
        bpy.ops.scene.view_layer_add_used_lightgroups()
    except Exception:
        pass
    if scene.world and CAPS.get("world_lightgroup"):
        safe_set(scene.world, "lightgroup", "LG_WORLD")

# ============================================================
# 15 — ROOM VISIBILITY
# ============================================================


def apply_room_visibility(scene):
    enabled = bool(scene.awful_studio.reflective_room_enabled)
    for o in bpy.data.objects:
        role = o.get(ROLE_KEY, "")
        if role.startswith("ROOM_") or role == "WINDOW_FRAME":
            o.hide_render = not enabled; o.hide_viewport = not enabled
    glass = REG.object("WINDOW_GLASS")
    if glass:
        glass_enabled = enabled and bool(scene.awful_studio.window_glass_enabled)
        glass.hide_render = not glass_enabled; glass.hide_viewport = not glass_enabled
    set_window_portal_enabled(scene, enabled and bool(scene.awful_studio.natural_light_enabled))

# ============================================================
# 16 — MOTION PRESETS
# ============================================================


def clear_animation(idblock):
    try:
        if idblock and idblock.animation_data:
            idblock.animation_data_clear()
    except Exception:
        pass


def set_action_interpolation(idblock, interpolation="LINEAR"):
    try:
        action = idblock.animation_data.action
        for fc in action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = interpolation
    except Exception:
        pass


def key_rotation(node, axis, a, b, start, end, interpolation="LINEAR"):
    node.rotation_euler[axis] = a; node.keyframe_insert(data_path="rotation_euler", index=axis, frame=start)
    node.rotation_euler[axis] = b; node.keyframe_insert(data_path="rotation_euler", index=axis, frame=end)
    set_action_interpolation(node, interpolation)


def key_location(node, axis, keys, interpolation="BEZIER"):
    for frame, value in keys:
        node.location[axis] = value; node.keyframe_insert(data_path="location", index=axis, frame=frame)
    set_action_interpolation(node, interpolation)


def safe_product_center_height(scene, preset):
    m = get_product_metrics(scene)
    if preset == "SPIN_X": return math.sqrt(m.half_y*m.half_y + m.half_z*m.half_z)
    if preset == "SPIN_Y": return math.sqrt(m.half_x*m.half_x + m.half_z*m.half_z)
    if preset == "TUMBLE": return math.sqrt(m.half_x*m.half_x + m.half_y*m.half_y + m.half_z*m.half_z)
    return m.half_z


def apply_product_motion(scene, preset=None):
    preset = preset or scene.awful_studio.product_motion
    scene.awful_studio.product_motion = preset
    stage, motion = REG.object("PRODUCT_STAGE"), REG.object("PRODUCT_MOTION")
    rz, rx, ry = REG.object("PRODUCT_ROT_Z"), REG.object("PRODUCT_ROT_X"), REG.object("PRODUCT_ROT_Y")
    root = REG.object("PRODUCT_GEOMETRY_ROOT")
    if not all((stage,motion,rz,rx,ry,root)): return
    for o in (stage,motion,rz,rx,ry,root): clear_animation(o)
    stage.location=(0,0,STUDIO_SPEC["pedestal"]["height"]); stage.rotation_euler=(0,0,0)
    for o in (rz,rx,ry): o.rotation_euler=(0,0,0)
    root.scale=(1,1,1)
    lift=safe_product_center_height(scene,preset); motion.location=(0,0,lift)
    end=DEFAULT_FRAMES+1; sign=-1.0
    if preset=="STATIC": return
    if preset=="SPIN_Z": key_rotation(rz,2,0,sign*math.tau,1,end)
    elif preset=="SPIN_X": key_rotation(rx,0,0,sign*math.tau,1,end)
    elif preset=="SPIN_Y": key_rotation(ry,1,0,sign*math.tau,1,end)
    elif preset=="FLOAT_SPIN":
        key_rotation(rz,2,0,sign*math.tau,1,end)
        amp=max(0.08,min(0.28,get_product_metrics(scene).height*0.12))
        heights=float_motion_heights(lift=lift, amplitude=amp)
        key_location(motion,2,list(zip((1,60,120,180,end),heights)))
    elif preset=="HERO_REVEAL":
        key_rotation(rz,2,math.radians(45),math.radians(-6),1,DEFAULT_FRAMES,"BEZIER"); key_rotation(rx,0,math.radians(8),0,1,DEFAULT_FRAMES,"BEZIER")
    elif preset=="TUMBLE":
        key_rotation(rz,2,0,sign*math.tau,1,end); key_rotation(rx,0,0,sign*math.tau*0.8,1,end); key_rotation(ry,1,0,sign*math.tau*0.6,1,end)
    elif preset=="PENDULUM":
        for frame,deg in [(1,-12),(60,12),(120,-12),(180,12),(end,-12)]: rx.rotation_euler.x=math.radians(deg); rx.keyframe_insert(data_path="rotation_euler",index=0,frame=frame)
        set_action_interpolation(rx,"BEZIER")
    elif preset=="ORBIT_BOB":
        r=max(0.08,min(0.30,get_product_metrics(scene).width*0.12))
        for frame,x,y in [(1,0,-r),(60,r,0),(120,0,r),(180,-r,0),(end,0,-r)]: stage.location=(x,y,STUDIO_SPEC["pedestal"]["height"]); stage.keyframe_insert(data_path="location",frame=frame)
        set_action_interpolation(stage,"BEZIER"); key_rotation(rz,2,0,sign*math.tau,1,end)
    elif preset=="BREATH":
        for frame,v in [(1,1.0),(60,1.02),(120,1.0),(180,0.985),(end,1.0)]: root.scale=(v,v,v); root.keyframe_insert(data_path="scale",frame=frame)
        set_action_interpolation(root,"BEZIER")


def set_camera_source(path_mode):
    anchor=REG.object("CAMERA_ANCHOR")
    if not anchor: return
    for c in anchor.constraints:
        if c.name=="Anchor From Dolly": c.influence=0.0 if path_mode else 1.0
        elif c.name=="Anchor From Path": c.influence=1.0 if path_mode else 0.0


def apply_camera_motion(scene, preset=None):
    preset=preset or scene.awful_studio.camera_motion; scene.awful_studio.camera_motion=preset
    yaw,pitch,dolly=REG.object("CAMERA_YAW"),REG.object("CAMERA_PITCH"),REG.object("CAMERA_DOLLY")
    camera,follower=REG.object("CAMERA"),REG.object("CAMERA_PATH_FOLLOW")
    if not all((yaw,pitch,dolly,camera,follower)): return
    for o in (yaw,pitch,dolly,follower): clear_animation(o)
    clear_animation(camera.data)
    # Recompute base from the camera's current manually editable lens.
    apply_camera_base_pose(scene, camera.data.lens, float(scene.get("awful_camera_margin",1.32)))
    base=float(scene.get("awful_camera_base_distance",6.0)); z=float(scene.get("awful_camera_base_height_offset",0.2)); end=DEFAULT_FRAMES+1
    set_camera_source(False)
    if preset=="STATIC": return
    if preset=="CUSTOM_PATH":
        set_camera_source(True); c=next((c for c in follower.constraints if c.type=="FOLLOW_PATH"),None)
        if c: c.offset_factor=0.0; c.keyframe_insert(data_path="offset_factor",frame=1); c.offset_factor=1.0; c.keyframe_insert(data_path="offset_factor",frame=end); set_action_interpolation(follower,"LINEAR")
        return
    if preset=="ARC_LR": key_rotation(yaw,2,math.radians(-20),math.radians(20),1,end,"BEZIER")
    elif preset=="ARC_RL": key_rotation(yaw,2,math.radians(20),math.radians(-20),1,end,"BEZIER")
    elif preset=="VERTICAL_ARC": key_rotation(pitch,0,math.radians(-8),math.radians(10),1,end,"BEZIER")
    elif preset=="PUSH_IN": key_location(dolly,1,[(1,-base),(end,-base*0.78)],"BEZIER")
    elif preset=="PULL_OUT": key_location(dolly,1,[(1,-base),(end,-base*1.25)],"BEZIER")
    elif preset=="DOLLY_ZOOM_IN":
        end_d=base*0.78; key_location(dolly,1,[(1,-base),(end,-end_d)],"LINEAR"); start_lens=camera.data.lens; camera.data.keyframe_insert(data_path="lens",frame=1); camera.data.lens=start_lens*(end_d/base); camera.data.keyframe_insert(data_path="lens",frame=end); set_action_interpolation(camera.data,"LINEAR")
    elif preset=="DOLLY_ZOOM_OUT":
        end_d=base*1.25; key_location(dolly,1,[(1,-base),(end,-end_d)],"LINEAR"); start_lens=camera.data.lens; camera.data.keyframe_insert(data_path="lens",frame=1); camera.data.lens=start_lens*(end_d/base); camera.data.keyframe_insert(data_path="lens",frame=end); set_action_interpolation(camera.data,"LINEAR")
    elif preset=="ORBIT_PUSH": key_rotation(yaw,2,math.radians(-22),math.radians(22),1,end,"BEZIER"); key_location(dolly,1,[(1,-base*1.03),(end,-base*0.82)],"BEZIER")
    elif preset=="ORBIT_RISE": key_rotation(yaw,2,math.radians(-24),math.radians(24),1,end,"BEZIER"); key_location(dolly,2,[(1,z),(end,z+get_product_metrics(scene).height*0.65)],"BEZIER")
    elif preset=="HERO_ARC": key_rotation(yaw,2,math.radians(-18),math.radians(16),1,end,"BEZIER"); key_rotation(pitch,0,math.radians(6),math.radians(-2),1,end,"BEZIER"); key_location(dolly,1,[(1,-base*1.04),(end,-base*0.87)],"BEZIER")
    elif preset=="FIGURE_8":
        for node,axis,vals in ((yaw,2,[(1,-16),(60,16),(120,-16),(180,16),(end,-16)]),(pitch,0,[(1,-6),(60,6),(120,-6),(180,6),(end,-6)])):
            for frame,deg in vals: node.rotation_euler[axis]=math.radians(deg); node.keyframe_insert(data_path="rotation_euler",index=axis,frame=frame)
            set_action_interpolation(node,"BEZIER")

# ============================================================
# 17 — RENDER / PASSES / COMPOSITOR
# ============================================================


def configure_cycles_gpu(scene):
    """Prefer an available GPU backend for the current Blender session.

    AWFUL Studio is a Cycles lighting tool; leaving scene.cycles.device at CPU
    makes a fast NVIDIA/AMD/Intel GPU irrelevant. This does not save user
    preferences to disk; it only configures the current Blender session.
    """
    try:
        addon = bpy.context.preferences.addons.get("cycles")
        if addon is None:
            raise RuntimeError("Cycles addon preferences unavailable")
        prefs = addon.preferences
        for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
            try:
                prefs.compute_device_type = backend
                prefs.get_devices()
                devices = list(getattr(prefs, "devices", []))
                gpu_devices = [d for d in devices if getattr(d, "type", "") != "CPU"]
                if not gpu_devices:
                    continue
                for dev in devices:
                    dev.use = dev in gpu_devices
                scene.cycles.device = "GPU"
                names = ", ".join(getattr(d, "name", getattr(d, "type", "GPU")) for d in gpu_devices)
                print(f"[AWFUL v4] Cycles GPU: {backend} -> {names}")
                return backend, names
            except Exception:
                continue
    except Exception as exc:
        print(f"[AWFUL v4] GPU detection failed: {exc}")
    try:
        scene.cycles.device = "CPU"
    except Exception:
        pass
    print("[AWFUL v4] WARNING: no usable Cycles GPU backend detected; using CPU")
    return "CPU", "CPU"


def setup_render(scene):
    scene.render.engine = "CYCLES"
    configure_cycles_gpu(scene)
    scene.render.preview_pixel_size = "2"
    scene.render.resolution_x = RENDER_X
    scene.render.resolution_y = RENDER_Y
    scene.render.resolution_percentage = 100
    scene.render.fps = DEFAULT_FPS
    scene.frame_start = 1
    scene.frame_end = DEFAULT_FRAMES
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "16"
    scene.render.filepath = "//renders/product_####.png"

    # Final render stays high quality; rendered viewport gets an explicit small
    # sample budget. Blender's default viewport budget can be far higher and was
    # one of the main sources of needless GPU load in the previous v4 build.
    scene.cycles.samples = RENDER_SAMPLES
    safe_set(scene.cycles, "preview_samples", PREVIEW_SAMPLES)
    safe_set(scene.cycles, "use_adaptive_sampling", True)
    safe_set(scene.cycles, "use_light_tree", True)
    safe_set(scene.cycles, "adaptive_threshold", 0.01)
    safe_set(scene.cycles, "preview_adaptive_threshold", PREVIEW_ADAPTIVE_THRESHOLD)
    safe_set(scene.cycles, "use_denoising", True)
    safe_set(scene.cycles, "use_preview_denoising", True)
    safe_set(scene.cycles, "max_bounces", 6)
    safe_set(scene.cycles, "diffuse_bounces", 2)
    safe_set(scene.cycles, "glossy_bounces", 4)
    safe_set(scene.cycles, "transmission_bounces", 6)
    safe_set(scene.cycles, "transparent_max_bounces", 4)
    safe_set(scene.cycles, "caustics_reflective", False)
    safe_set(scene.cycles, "caustics_refractive", False)
    safe_set(scene.render, "use_motion_blur", False)

    # Persistent Data deliberately stays off for the default interactive tool.
    # It speeds repeated final renders by retaining render data, but Blender's own
    # manual explicitly notes the extra memory cost while doing other work.
    safe_set(scene.render, "use_persistent_data", False)

    for transform in ("Khronos PBR Neutral", "AgX"):
        try:
            scene.view_settings.view_transform = transform
            break
        except Exception:
            pass
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


def setup_passes(scene):
    vl=scene.view_layers[0]
    for attr in ("use_pass_z","use_pass_normal","use_pass_mist","use_pass_diffuse_direct","use_pass_diffuse_indirect","use_pass_glossy_direct","use_pass_glossy_indirect","use_pass_transmission_direct","use_pass_transmission_indirect","use_pass_emit","use_pass_ambient_occlusion","use_pass_shadow","use_pass_cryptomatte_object","use_pass_cryptomatte_material"):
        safe_set(vl,attr,True)
    safe_set(vl,"pass_cryptomatte_depth",6)
    try:
        safe_set(vl.cycles, "denoising_store_passes", True)
    except Exception:
        pass
    try:
        vl.update_render_passes()
    except Exception:
        pass


def build_compositor(scene):
    """Build a conservative, non-destructive AWFUL post foundation.

    Blender 5.x moved the scene compositor to Scene.compositing_node_group and
    uses Group Output as the render result. Blender 4.x keeps the legacy
    Scene.node_tree / Composite node path. Artistic nodes are neutral or muted
    by default so the generated scene never bakes a look into the render.
    """
    safe_set(scene.render, "use_compositing", True)

    def wire_common(tree, use_group_output):
        nodes, links = tree.nodes, tree.links
        rl = nodes.new("CompositorNodeRLayers")
        rl.name = "AWFUL_RenderLayers"
        rl.location = (-720, 0)

        previous_output = rl.outputs.get("Noisy Image") or rl.outputs.get("Image")

        try:
            den = nodes.new("CompositorNodeDenoise")
            den.name = "AWFUL_Denoise"
            den.location = (-440, 0)
            if previous_output and den.inputs.get("Image"):
                links.new(previous_output, den.inputs["Image"])
            if rl.outputs.get("Denoising Normal") and den.inputs.get("Normal"):
                links.new(rl.outputs["Denoising Normal"], den.inputs["Normal"])
            if rl.outputs.get("Denoising Albedo") and den.inputs.get("Albedo"):
                links.new(rl.outputs["Denoising Albedo"], den.inputs["Albedo"])
            if den.inputs.get("HDR"):
                den.inputs["HDR"].default_value = True
            previous_output = den.outputs.get("Image") or previous_output
        except Exception as exc:
            print(f"[AWFUL] compositor Denoise unavailable: {exc}")

        try:
            exp = nodes.new("CompositorNodeExposure")
            exp.name = "AWFUL_Exposure"
            exp.label = "Manual post exposure"
            exp.location = (-160, 0)
            if exp.inputs.get("Exposure"):
                exp.inputs["Exposure"].default_value = 0.0
            if previous_output and exp.inputs.get("Image"):
                links.new(previous_output, exp.inputs["Image"])
            previous_output = exp.outputs.get("Image") or previous_output
        except Exception as exc:
            print(f"[AWFUL] compositor Exposure unavailable: {exc}")

        try:
            cb = nodes.new("CompositorNodeColorBalance")
            cb.name = "AWFUL_ColorBalance"
            cb.label = "Manual grade"
            cb.location = (100, 0)
            if previous_output and cb.inputs.get("Image"):
                links.new(previous_output, cb.inputs["Image"])
            previous_output = cb.outputs.get("Image") or previous_output
        except Exception as exc:
            print(f"[AWFUL] compositor Color Balance unavailable: {exc}")

        # Present as a ready-made optional tool, but disabled by default.
        try:
            glare = nodes.new("CompositorNodeGlare")
            glare.name = "AWFUL_Glare_Optional"
            glare.label = "OPTIONAL — subtle specular glow"
            glare.location = (360, 0)
            safe_set(glare, "glare_type", "FOG_GLOW")
            safe_set(glare, "quality", "HIGH")
            safe_set(glare, "threshold", 2.0)
            safe_set(glare, "mix", -1.0)
            glare.mute = True
            if previous_output and glare.inputs.get("Image"):
                links.new(previous_output, glare.inputs["Image"])
            previous_output = glare.outputs.get("Image") or previous_output
        except Exception as exc:
            print(f"[AWFUL] compositor Glare unavailable: {exc}")

        if use_group_output:
            output = nodes.new("NodeGroupOutput")
            output.name = "AWFUL_GroupOutput"
            output.location = (650, 0)
            if previous_output and output.inputs.get("Image"):
                links.new(previous_output, output.inputs["Image"])
        else:
            output = nodes.new("CompositorNodeComposite")
            output.name = "AWFUL_Composite"
            output.location = (650, 0)
            if previous_output and output.inputs.get("Image"):
                links.new(previous_output, output.inputs["Image"])

    # Blender 5.0+ compositor API.
    if tuple(bpy.app.version) >= (5, 0, 0) and hasattr(scene, "compositing_node_group"):
        old = scene.compositing_node_group
        if old and is_managed(old):
            scene.compositing_node_group = None
            try:
                if old.users == 0:
                    bpy.data.node_groups.remove(old)
            except Exception:
                pass

        # Avoid hijacking a same-named user node group.
        name = "AWFUL_POST"
        existing = bpy.data.node_groups.get(name)
        if existing and not is_managed(existing):
            name = "AWFUL_POST_v4"
        tree = bpy.data.node_groups.get(name)
        if tree and is_managed(tree) and tree.users == 0:
            bpy.data.node_groups.remove(tree)
            tree = None
        if tree is None:
            tree = bpy.data.node_groups.new(name, "CompositorNodeTree")
        mark_managed(tree, "COMPOSITOR")
        scene.compositing_node_group = tree
        tree.nodes.clear()
        try:
            # A compositor root group needs an exposed first Image output.
            for item in list(tree.interface.items_tree):
                try:
                    tree.interface.remove(item)
                except Exception:
                    pass
            tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        except Exception as exc:
            print(f"[AWFUL] compositor interface setup failed: {exc}")
        wire_common(tree, True)
        return tree

    # Blender 4.x compatibility path.
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    wire_common(tree, False)
    return tree

# ============================================================
# 18 — VALIDATION
# ============================================================


def validate_static_configuration(scene=None):
    errors=[]
    width,depth,height=STUDIO_SPEC["width"],STUDIO_SPEC["depth"],STUDIO_SPEC["height"]
    area=width*depth
    if not (200.0 <= area <= 320.0): errors.append(f"Studio area {area:.1f} m² is outside v4 design range")
    if height < 6.0: errors.append("Studio ceiling must be at least 6 m")
    cyc=STUDIO_SPEC["cyc"]
    if cyc["width"] >= width: errors.append("Cyclorama must be narrower than room")
    if cyc["height"] >= height: errors.append("Cyclorama must stay below ceiling")
    win=STUDIO_SPEC["window"]
    if win["width"] < 6.0: errors.append("Studio window is too small")
    if win["glass_thickness"] > 0.012: errors.append("Window glass is too thick")
    if cyc["radius"] < 2.5: errors.append("Cyclorama cove radius is too tight for the v4 studio")
    if win["center_y"] - win["width"] * 0.5 <= STUDIO_SPEC["camera_y"]: errors.append("Window crosses camera-side wall")
    if win["center_y"] + win["width"] * 0.5 >= STUDIO_SPEC["background_y"]: errors.append("Window crosses background boundary")
    if win["top_z"] >= height or win["bottom_z"] <= 0: errors.append("Window vertical bounds are invalid")
    env = STUDIO_SPEC["product_envelope"]
    if env["target_xy"] > env["max_xy"] or env["target_height"] > env["max_height"]:
        errors.append("Product Auto Fit target exceeds the safe product envelope")
    if len(LIGHTING_PRESETS)!=16: errors.append(f"Expected 16 lighting presets, got {len(LIGHTING_PRESETS)}")
    for pid,p in LIGHTING_PRESETS.items():
        if pid!=p.id: errors.append(f"Preset key/id mismatch {pid}")
        if p.family not in LIGHT_FAMILY_ORDER: errors.append(f"{pid}: bad family")
        if p.environment not in WORLD_PRESET_ORDER: errors.append(f"{pid}: bad environment")
        if p.camera_lens <= 0: errors.append(f"{pid}: invalid lens")
        for ls in p.lights:
            if ls.role not in LIGHT_BANK_ROLES: errors.append(f"{pid}: unknown light {ls.role}")
            if ls.base_power < 0: errors.append(f"{pid}: negative power")
            if not (-6.0 <= ls.exposure_ev <= 6.0): errors.append(f"{pid}: unreasonable exposure on {ls.role}")
            if not ls.camera_local and ls.distance.minimum < 1.5: errors.append(f"{pid}: {ls.role} can get unrealistically close")
            if ls.kind == "AREA" and not ls.camera_local and (ls.size_x.minimum <= 0 or ls.size_y.minimum <= 0): errors.append(f"{pid}: invalid Area size rule")
    if errors: raise RuntimeError("AWFUL v4 static validation failed:\n- "+"\n- ".join(errors))
    return True


def validate_built_scene(scene):
    errors=[]
    roles=["ROOT","CYC","PEDESTAL","PRODUCT_STAGE","PRODUCT_MOTION","PRODUCT_GEOMETRY_ROOT","AIM_PRODUCT","CAMERA","CAMERA_DOLLY","LIGHT_RIG","ROOM_BACKGROUND","WINDOW_GLASS","WINDOW_PORTAL"]+list(LIGHT_BANK_ROLES)+list(SHAPER_ROLES)
    for role in roles:
        if role=="ROOT":
            if REG.collection("ROOT") is None: errors.append("Missing root collection")
        elif REG.object(role) is None: errors.append(f"Missing object role: {role}")
    camera=REG.object("CAMERA")
    if camera and scene.camera!=camera: errors.append("AWFUL camera is not active")
    flash=REG.object("LIGHT_CameraFlash")
    if flash and camera and flash.parent!=camera: errors.append("Camera flash is not parented to camera")
    portal=REG.object("WINDOW_PORTAL")
    if portal and portal.data.type!="AREA": errors.append("Window portal must be Area")
    if portal and CAPS and CAPS.get("portal") and not getattr(portal.data.cycles,"is_portal",False): errors.append("Area portal flag is not enabled")
    floor=REG.object("ROOM_FLOOR")
    if floor:
        floor_top=floor.location.z+floor.dimensions.z*0.5
        if floor_top>=-1e-4: errors.append("Physical room floor intersects cyclorama floor")
    for role in ("MAT_CYC","MAT_ROOM_BOUNCE","MAT_WINDOW_GLASS","MAT_DIAGNOSTIC"):
        if REG.material(role) is None: errors.append(f"Missing material {role}")
    material_coords = REG.object("MATERIAL_COORDS")
    if material_coords is None:
        errors.append("Missing shared MATERIAL_COORDS object")
    for role in ("MAT_CYC",):
        mat = REG.material(role)
        if mat and mat.use_nodes:
            coord = next((n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeTexCoord"), None)
            if coord is None or getattr(coord, "object", None) != material_coords:
                errors.append(f"{role} is not using shared physical Object coordinates")
    glass = REG.object("WINDOW_GLASS")
    if glass and abs(glass.dimensions.x - STUDIO_SPEC["window"]["glass_thickness"]) > 0.002:
        errors.append("Window glass thickness does not match studio spec")
    # The compositor/light-groups/pass pipeline is intentionally opt-in in v4.1+.
    # Core studio validation must not require it unless the user explicitly built it.
    if bool(scene.get(POST_PIPELINE_KEY, False)):
        if tuple(bpy.app.version) >= (5,0,0) and hasattr(scene, "compositing_node_group"):
            tree = scene.compositing_node_group
            if tree is None or not is_managed(tree):
                errors.append("Managed Blender 5 compositor group is missing")
            elif not any(n.bl_idname == "NodeGroupOutput" for n in tree.nodes):
                errors.append("Blender 5 compositor has no Group Output")
        else:
            tree = getattr(scene, "node_tree", None) if getattr(scene, "use_nodes", False) else None
            if tree is None or not any(n.bl_idname == "CompositorNodeComposite" for n in tree.nodes):
                errors.append("Managed compositor pipeline is missing")
    if errors: raise RuntimeError("AWFUL v4 runtime validation failed:\n- "+"\n- ".join(errors))
    print("[AWFUL v4] validation OK")
    return True

# ============================================================
# 19 — BUILD PIPELINE
# ============================================================


def collect_external_mounted_roots():
    content=REG.object("PRODUCT_CONTENT")
    if not content: return []
    roots=[]
    for child in list(content.children):
        if not is_managed(child): roots.append(child)
    return roots


def build_studio(preserve_product=True):
    global CAPS, REG
    validate_static_configuration()
    CAPS=detect_blender_capabilities()
    preserved=collect_external_mounted_roots() if preserve_product else []
    preserved_matrices = {o: o.matrix_world.copy() for o in preserved}
    for root in preserved:
        mw=root.matrix_world.copy(); root.parent=None; root.matrix_world=mw
    remove_managed_studio()
    REG=StudioRegistry(bpy.context.scene)
    cols=build_collection_tree()
    material_coords=add_empty("MATERIAL_COORDS", "MATERIAL_COORDS", (0,0,0), cols["CONTROLS"], "PLAIN_AXES", 0.30)
    mats=build_all_materials(material_coords)
    build_cyclorama(cols["STAGE"],mats["cyc"])
    build_pedestal(cols["STAGE"],mats["pedestal"])
    build_room(cols["ROOM"],cols["WINDOW"],mats["room_bounce"],mats["floor"],mats["frame"],mats["glass"])
    build_product_rig(cols["CONTROLS"],cols["PRODUCT"])
    build_camera_rig(cols["CAMERA"],cols["CONTROLS"])
    scene=bpy.context.scene
    setup_render(scene)
    # Build only the interactive studio core. Heavy render-pass/light-group/
    # compositor infrastructure is opt-in from Setup, not paid for on every build.
    build_light_bank(cols["LIGHTS"],cols["CONTROLS"],cols["SHAPERS"],mats)
    create_window_portal(cols["LIGHTS"])
    setup_world_nodes()

    if preserved:
        metrics=mount_product(preserved,scene.awful_studio.auto_fit)
    else:
        diagnostic=create_diagnostic_product(cols["DIAGNOSTICS"],mats["diagnostic"])
        metrics=mount_product([diagnostic],False)
    populate_link_collections()
    apply_product_motion(scene,scene.awful_studio.product_motion)
    apply_lighting_preset(scene,scene.awful_studio.studio_light_preset,True,True)
    apply_camera_motion(scene,scene.awful_studio.camera_motion)
    apply_room_visibility(scene)
    apply_environment_preset(scene,scene.awful_studio.world_preset,False)
    # A normal rebuild creates only the interactive studio core. Post is opt-in.
    scene[POST_PIPELINE_KEY] = False
    validate_built_scene(scene)
    scene.frame_set(1)
    for obj, matrix in preserved_matrices.items():
        obj.matrix_world = matrix
    bpy.context.view_layer.update()
    return metrics

# ============================================================
# 20 — UI STATE / OPERATORS
# ============================================================


def cycle_in_list(current, seq, step):
    try: idx=seq.index(current)
    except ValueError: idx=0
    return seq[(idx+step)%len(seq)]


def on_room_toggle(self, context):
    if REG.object("CYC"): apply_room_visibility(context.scene)


def on_natural_toggle(self, context):
    if context.scene.world: apply_environment_preset(context.scene,self.world_preset,False)


def on_glass_toggle(self, context):
    if REG.object("WINDOW_GLASS"): apply_room_visibility(context.scene)


def on_background_toggle(self, context):
    if context.scene.world: apply_environment_preset(context.scene,self.world_preset,False)


def on_studio_master(self, context):
    if REG.object("LIGHT_RIG"): apply_artificial_master(context.scene)


class AWFUL_StudioSettings(bpy.types.PropertyGroup):
    auto_fit: BoolProperty(name="Auto Fit", default=True)
    product_motion: EnumProperty(name="Product Motion",items=[(k,PRODUCT_PRESET_LABELS[k],"") for k in PRODUCT_PRESET_ORDER],default="SPIN_Z")
    camera_motion: EnumProperty(name="Camera Motion",items=[(k,CAMERA_PRESET_LABELS[k],"") for k in CAMERA_PRESET_ORDER],default="STATIC")
    studio_light_family: EnumProperty(name="Lighting Family",items=[(k,LIGHT_FAMILY_LABELS[k],"") for k in LIGHT_FAMILY_ORDER],default="COMMERCIAL")
    studio_light_preset: EnumProperty(name="Lighting Preset",items=[(k,LIGHT_PRESET_LABELS[k],"") for k in LIGHTING_PRESETS],default="COMMERCIAL_3LIGHT")
    studio_lights_enabled: BoolProperty(name="Studio",default=True,update=on_studio_master)
    reflective_room_enabled: BoolProperty(name="Room",default=True,update=on_room_toggle)
    natural_light_enabled: BoolProperty(name="World",default=False,update=on_natural_toggle)
    world_preset: EnumProperty(name="Environment",items=[(k,WORLD_PRESET_LABELS[k],"") for k in WORLD_PRESET_ORDER],default="FISH_HOEK")
    window_glass_enabled: BoolProperty(name="Glass",default=False,update=on_glass_toggle)
    show_environment_background: BoolProperty(name="BG",default=False,update=on_background_toggle)


class AWFUL_OT_BuildStudio(bpy.types.Operator):
    bl_idname="awful.build_studio_v4"; bl_label="Rebuild Studio"; bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        try: build_studio(True)
        except Exception as exc: self.report({"ERROR"},str(exc)); raise
        self.report({"INFO"},"AWFUL Studio v4 rebuilt")
        return {"FINISHED"}


def selected_user_product_roots(context):
    """Return topmost selected unmanaged object hierarchies for Use Selected."""
    selected = [o for o in getattr(context, 'selected_objects', ()) if not is_managed(o)]
    roots = []
    for obj in selected:
        root = obj
        while root.parent is not None and not is_managed(root.parent):
            root = root.parent
        if root not in roots:
            roots.append(root)
    return roots


class AWFUL_OT_UseSelectedProduct(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.scene is not None and REG.object("CYC") is not None

    bl_idname="awful.use_selected_product_v4"; bl_label="Use Selected"; bl_options={"REGISTER","UNDO"}
    bl_description = "Use selected unmanaged object hierarchy as the editable product"
    def execute(self,context):
        scene = context.scene
        roots=selected_user_product_roots(context)
        if not roots: self.report({"ERROR"},"Select user product object(s), not AWFUL studio controls"); return {"CANCELLED"}
        try:
            scene.awful_studio.product_mockup = 'NONE'
            mount_product(roots,scene.awful_studio.auto_fit)
            populate_link_collections()
            apply_product_motion(scene,scene.awful_studio.product_motion)
            apply_lighting_preset(scene,scene.awful_studio.studio_light_preset,False,False)
            apply_camera_motion(scene,scene.awful_studio.camera_motion)
        except Exception as exc: self.report({"ERROR"},str(exc)); return {"CANCELLED"}
        return {"FINISHED"}


class AWFUL_OT_FetchAssets(bpy.types.Operator):
    bl_idname = "awful.fetch_assets_v4"
    bl_label = "Download Selected HDRI / Retry"

    def execute(self, context):
        try:
            result = ensure_assets(True)
            if not result:
                self.report({"INFO"}, "Physical Sky needs no external asset")
                return {"FINISHED"}
            if not all(result.values()):
                self.report({"ERROR"}, asset_cache.last_error())
                return {"CANCELLED"}
            refresh_world_images()
        except (OSError, ValueError, RuntimeError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class AWFUL_OT_BuildPostPipeline(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.scene is not None and REG.object("CYC") is not None

    bl_idname = "awful.build_post_pipeline_v4"
    bl_label = "Build Post Pipeline"

    def execute(self, context):
        scene = context.scene
        try:
            setup_light_groups(scene)
            setup_passes(scene)
            build_compositor(scene)
            # Set only after all three stages succeed, then validate the optional pipeline.
            scene[POST_PIPELINE_KEY] = True
            validate_built_scene(scene)
        except Exception as exc:
            scene[POST_PIPELINE_KEY] = False
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Light Groups, render passes and AWFUL_POST created")
        return {"FINISHED"}


class AWFUL_OT_Validate(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.scene is not None and REG.object("CYC") is not None

    bl_idname="awful.validate_v4"; bl_label="Validate Studio"
    def execute(self,context):
        try: validate_static_configuration(context.scene); validate_built_scene(context.scene)
        except Exception as exc: self.report({"ERROR"},str(exc)); return {"CANCELLED"}
        self.report({"INFO"},"AWFUL Studio v4 validation OK")
        return {"FINISHED"}


class AWFUL_OT_CyclePreset(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.scene is not None and REG.object("CYC") is not None

    bl_idname="awful.cycle_preset_v4"; bl_label="Cycle Preset"; bl_options={"INTERNAL"}
    target:StringProperty(); direction:IntProperty(default=1)
    def execute(self,context):
        s=context.scene.awful_studio; step=1 if self.direction>=0 else -1
        if self.target=="PRODUCT":
            s.product_motion=cycle_in_list(s.product_motion,PRODUCT_PRESET_ORDER,step); apply_product_motion(context.scene,s.product_motion)
        elif self.target=="CAMERA":
            s.camera_motion=cycle_in_list(s.camera_motion,CAMERA_PRESET_ORDER,step); apply_camera_motion(context.scene,s.camera_motion)
        elif self.target=="LIGHT_FAMILY":
            s.studio_light_family=cycle_in_list(s.studio_light_family,LIGHT_FAMILY_ORDER,step)
            s.studio_light_preset=LIGHT_FAMILY_PRESETS[s.studio_light_family][0]
            apply_lighting_preset(context.scene,s.studio_light_preset,True,True)
            apply_camera_motion(context.scene,s.camera_motion)
        elif self.target=="LIGHT_PRESET":
            seq=LIGHT_FAMILY_PRESETS[s.studio_light_family]
            s.studio_light_preset=cycle_in_list(s.studio_light_preset,seq,step)
            apply_lighting_preset(context.scene,s.studio_light_preset,True,True)
            apply_camera_motion(context.scene,s.camera_motion)
        elif self.target=="WORLD":
            s.world_preset=cycle_in_list(s.world_preset,WORLD_PRESET_ORDER,step); apply_environment_preset(context.scene,s.world_preset,True)
        return {"FINISHED"}

# ============================================================
# 21 — MINIMAL N-PANEL
# ============================================================


def draw_cycle_row(layout,target,label):
    row=layout.row(align=True)
    op=row.operator("awful.cycle_preset_v4",text="",icon="TRIA_LEFT"); op.target=target; op.direction=-1
    row.label(text=label)
    op=row.operator("awful.cycle_preset_v4",text="",icon="TRIA_RIGHT"); op.target=target; op.direction=1


class AWFUL_PT_Main(bpy.types.Panel):
    bl_label="AWFUL STUDIO"; bl_idname="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"; bl_category="AWFUL STUDIO"
    def draw(self,context):
        layout=self.layout; s=context.scene.awful_studio
        if not REG.object("CYC"):
            layout.operator("awful.build_studio", icon="ADD")
            layout.operator("awful.migrate_scene", text="Upgrade Historical AWFUL Scene")
            return
        layout.operator("awful.use_selected_product_v4",icon="OBJECT_DATA")
        layout.prop(s,"auto_fit",toggle=True)


class AWFUL_PT_Lighting(bpy.types.Panel):
    bl_label="Lighting"; bl_idname="AWFUL_PT_LIGHTING_V4"; bl_parent_id="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"
    def draw(self,context):
        s=context.scene.awful_studio
        draw_cycle_row(self.layout,"LIGHT_FAMILY",LIGHT_FAMILY_LABELS.get(s.studio_light_family,s.studio_light_family))
        draw_cycle_row(self.layout,"LIGHT_PRESET",LIGHT_PRESET_LABELS.get(s.studio_light_preset,s.studio_light_preset))
        row=self.layout.row(align=True); row.prop(s,"studio_lights_enabled",toggle=True); row.prop(s,"reflective_room_enabled",toggle=True); row.prop(s,"natural_light_enabled",toggle=True)


class AWFUL_PT_Product(bpy.types.Panel):
    bl_label="Product"; bl_idname="AWFUL_PT_PRODUCT_V4"; bl_parent_id="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"; bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        s=context.scene.awful_studio; draw_cycle_row(self.layout,"PRODUCT",PRODUCT_PRESET_LABELS.get(s.product_motion,s.product_motion))


class AWFUL_PT_Camera(bpy.types.Panel):
    bl_label="Camera"; bl_idname="AWFUL_PT_CAMERA_V4"; bl_parent_id="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"; bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        s=context.scene.awful_studio; draw_cycle_row(self.layout,"CAMERA",CAMERA_PRESET_LABELS.get(s.camera_motion,s.camera_motion))


class AWFUL_PT_Environment(bpy.types.Panel):
    bl_label="Environment"; bl_idname="AWFUL_PT_ENVIRONMENT_V4"; bl_parent_id="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"; bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        s=context.scene.awful_studio; draw_cycle_row(self.layout,"WORLD",WORLD_PRESET_LABELS.get(s.world_preset,s.world_preset))
        row=self.layout.row(align=True); row.prop(s,"window_glass_enabled",toggle=True); bg=row.row(align=True); bg.enabled=s.natural_light_enabled; bg.prop(s,"show_environment_background",toggle=True)


class AWFUL_PT_Setup(bpy.types.Panel):
    bl_label="Setup"; bl_idname="AWFUL_PT_SETUP_V4"; bl_parent_id="AWFUL_PT_MAIN_V4"; bl_space_type="VIEW_3D"; bl_region_type="UI"; bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        col=self.layout.column(align=True)
        col.operator("awful.validate_v4",icon="CHECKMARK")
        col.operator("awful.build_post_pipeline_v4",icon="NODETREE")
        col.operator("awful.fetch_assets_v4",icon="FILE_REFRESH")
        col.operator("awful.rebuild_studio",icon="RECOVER_LAST")
        col.operator("awful.reset_system")
        col.operator("awful.remove_studio",icon="TRASH")

# ============================================================
# 22 — REGISTRATION / LEGACY CLEANUP
# ============================================================

CLASSES=(AWFUL_StudioSettings,AWFUL_OT_BuildStudio,AWFUL_OT_UseSelectedProduct,AWFUL_OT_FetchAssets,AWFUL_OT_BuildPostPipeline,AWFUL_OT_Validate,AWFUL_OT_CyclePreset,AWFUL_PT_Main,AWFUL_PT_Lighting,AWFUL_PT_Product,AWFUL_PT_Camera,AWFUL_PT_Environment,AWFUL_PT_Setup)

# Classes registered by the Extension lifecycle; no scene operations at import.
CLASSES = tuple(c for c in CLASSES if c is not AWFUL_OT_BuildStudio)
