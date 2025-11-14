import json
from typing import Self

import numpy as np
import colour


class ColorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Color):
            return str(obj)
        return super().default(obj)


class Color:
    def __init__(self, h, s, v):
        self._rgb = np.array(colour.models.HSV_to_RGB(np.array([h, s, v], float)))

    def __str__(self):
        return colour.notation.RGB_to_HEX(self._rgb)

    # === dynamic color space access ===
    def __getattr__(self, name):
        try:
            return colour.convert(self._rgb, "RGB", name.upper())
        except Exception:
            raise AttributeError(name)

    # === base hsv ===
    @property
    def hsv(self):
        return tuple(map(float, colour.models.RGB_to_HSV(self._rgb)))

    @property
    def hex(self):
        return colour.notation.RGB_to_HEX(self._rgb)

    @property
    def rgb(self):
        return (self._rgb * 255).astype(int).tolist()

    # === constructors ===
    @classmethod
    def from_rgb(cls, r, g, b):
        obj = cls.__new__(cls)
        obj._rgb = np.array([r, g, b], float) / 255
        return obj

    @classmethod
    def from_hex(cls, hex_color):
        obj = cls.__new__(cls)
        obj._rgb = np.array(colour.notation.HEX_to_RGB(hex_color))
        return obj

    @classmethod
    def from_oklch(cls, l, c, h):
        obj = cls.__new__(cls)
        obj._rgb = np.array(colour.convert([l, c, h], "OKLCH", "RGB"))
        return obj

    # === oklch operations ===
    def set_lightness(self, l):
        lch = self.oklch
        return Color.from_oklch(l, lch[1], lch[2])

    def set_chroma(self, c):
        lch = self.oklch
        return Color.from_oklch(lch[0], c, lch[2])

    # === hsv-style ops ===
    def set_hue(self, h):
        hh, ss, vv = self.hsv
        return Color(h, ss, vv)

    def set_sat(self, s):
        hh, ss, vv = self.hsv
        return Color(hh, s, vv)

    def set_val(self, v):
        hh, ss, vv = self.hsv
        return Color(hh, ss, v)

    def hue_shift(self, delta):
        hh, ss, vv = self.hsv
        return Color((hh + delta) % 1.0, ss, vv)

    def hue_shifts(self, deltas):
        return [self.hue_shift(d) for d in deltas]

    def complementary(self):
        return self.hue_shift(0.5)

    def analogous(self, index=0):
        return self.hue_shifts([-1 / 12, 1 / 12])[index % 2]

    def triadic(self, index=0):
        return self.hue_shifts([1 / 3, 2 / 3])[index % 2]

    def tetradic(self, index=0):
        return self.hue_shifts([0.25, 0.5, 0.75])[index % 3]

    def tint(self, t):
        hh, ss, vv = self.hsv
        return Color(hh, ss + (1 - ss) * t, vv + (1 - vv) * t)

    def shade(self, t):
        hh, ss, vv = self.hsv
        return Color(hh, ss, vv * (1 - t))

    def lerp_target(self, target: Self, pos: float):
        sh, ss, sv = self.hsv
        th, ts, tv = target.hsv
        delta = ((th - sh + 1.5) % 1.0) - 0.5
        return Color(
            (sh + delta * pos) % 1.0, ss + (ts - ss) * pos, sv + (tv - sv) * pos
        )
