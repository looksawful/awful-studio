"""Photo-derived LOW port positions, not manufacturing dimensions.

Apple side images crop the front of the device. Do not scale their full width
to the chassis depth. Instead use the visible USB-C opening as the local ruler.
An approximately 24 px opening is assigned 8.4 mm (rounded visual envelope).
The remaining centers are projected from the visible rear endpoint.
"""
from dataclasses import dataclass

MM_PER_PIXEL=8.4/24

@dataclass(frozen=True)
class Port:
    name: str
    side: int
    center_pixel: float
    rear_pixel: float
    width_mm: float
    height_mm: float

    @property
    def y_mm(self):
        return 221.2/2-abs(self.center_pixel-self.rear_pixel)*MM_PER_PIXEL

PORTS=(
    Port('MAGSAFE',-1,85.5,3,17.8,3.4),
    Port('TB_LEFT_1',-1,142,3,8.4,2.6),
    Port('TB_LEFT_2',-1,186,3,8.4,2.6),
    Port('HEADPHONE',-1,225,3,3.6,3.6),
    Port('HDMI',1,324,406,15,4.4),
    Port('SDXC',1,194,406,27.3,2.1),
    Port('TB_RIGHT',1,269,406,8.4,2.6),
)
