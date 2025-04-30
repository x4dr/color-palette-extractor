import colorsys
import json

class ColorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Color):
            return str(obj)
        return super().default(obj)

class Color:
    def __init__(self, h, s, v):
        self.h = h
        self.s = s
        self.v = v
    def __str__(self):
        return self.hex

    @property
    def hsv(self):
        return self.h, self.s, self.v

    @property
    def hex(self):
        return self.hsv_to_hex(self.h, self.s, self.v)

    @property
    def rgb(self):
        return [int(x * 255) for x in colorsys.hsv_to_rgb(self.h, self.s, self.v)]

    @classmethod
    def from_rgb(cls, r, g, b):
        return cls(*colorsys.rgb_to_hsv(r/255, g/255, b/255))

    @classmethod
    def from_hex(cls, hex_color):
        return cls.from_rgb(*cls.hex_to_rgb(hex_color))

    @staticmethod
    def hex_to_rgb(h):
        try:
            return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
        except ValueError:
            raise ValueError("Invalid hex color format", h)

    @staticmethod
    def hsv_to_hex(h, s, v):
        if not all(0 <= x <= 1 for x in (h, s, v)):
            raise ValueError(h, s, v)
        return f"#{''.join(f'{int(c * 255):02x}' for c in colorsys.hsv_to_rgb(h, s, v))}"


    def hue_shift(self, delta):
        return Color((self.h + delta) % 1, self.s, self.v)

    def hue_shifts(self, deltas):
        return [Color((self.h + d) % 1, self.s, self.v) for d in deltas]

    def complementary(self, index= 0):
        return self.hue_shifts([-0.5])[0]

    def analogous(self, index= 0):
        return self.hue_shifts([-1 / 12, 1 / 12])[int(index%2)]

    def triadic(self,index= 0):
        return self.hue_shifts([1 / 3, 2 / 3])[int(index%2)]

    def tetradic(self,index= 0):
        return self.hue_shifts([0.25, 0.5, 0.75])[int(index%3)]

    def tint(self, t: float):
        s = self.s + (1 - self.s) * t
        v = self.v + (1 - self.v) * t
        return Color(self.h, s, v)
    def shade(self, t: float):
        return Color(self.h, self.s, self.v * (1 - t))

    def lerp_target(self, target, pos):
        return self.lerp(target.h,target.s,target.v, pos)

    def lerp(self, h, s, v, pos):
        delta = ((h - self.h + 1.5) % 1.0) - 0.5
        h_new = (self.h + delta * pos) % 1.0
        s_new = self.s + (s - self.s) * pos
        v_new = self.v + (v - self.v) * pos
        return Color(h_new, s_new, v_new)