import re
from typing import Callable
from colors.Color import Color


class Theme:

    def __init__(
        self, colors, color_roles: dict[str, Color], variables: dict[str, str]
    ):
        self.keys = {i: Color.from_hex(x) for i, x in enumerate(colors)}
        self.roles = {k: Color.from_hex(v) for k, v in color_roles.items()}
        self.variables = variables

    FUNCTIONS = {
        "HUE_SHIFT": Color.hue_shift,
        "LERP": Color.lerp,
        "TINT": Color.tint,
        "SHADE": Color.shade,
        "COMPLEMENTARY": Color.complementary,
        "TRIADIC": Color.triadic,
        "TETRADIC": Color.tetradic,
        "ANALOGOUS": Color.analogous,
        "HUE": Color.set_hue,
        "VAL": Color.set_val,
        "SAT": Color.set_sat,
    }

    PROPERTIES = {
        "HEX": Color.hex,
    }

    def process_template(self, template: str) -> str:

        def parse_nums(s: str) -> list[float]:
            return [float(x) for x in s.split(",") if x.strip()]

        def lam(func):
            return lambda m: str(
                func(
                    Color.from_rgb(*parse_nums(m.group(1))), *parse_nums(m.group(2))
                ).rgb
            ).strip("[]")

        def prop(pr):
            return lambda m: getattr(
                Color.from_rgb(*parse_nums(m.group(1))), pr.fget.__name__
            )

        match_to_func: dict[re.Pattern, Callable] = {}

        for name, f in self.FUNCTIONS.items():
            pattern = rf"(\d+,\s*\d+,\s*\d+)\.{name}\((.*?)\)"
            match_to_func[re.compile(pattern)] = lam(f)

        for name, f in self.PROPERTIES.items():
            pattern = rf"(\d+,\s*\d+,\s*\d+)\.{name}\b"
            match_to_func[re.compile(pattern)] = prop(f)

        # KEY(n)
        def handle_key(m):
            col = self.keys.get(int(m.group(1)))
            return str(col.rgb).strip("[]") if col else m.group(0)

        # ROLE(name)
        def handle_role(m):
            col = self.roles.get(m.group(1))
            return str(col.rgb).strip("[]") if col else m.group(0)

        match_to_func[re.compile(r"ROLE\((\w+)\)")] = handle_role
        match_to_func[re.compile(r"KEY\((\d+)\)")] = handle_key

        for k, v in self.variables.items():
            template = re.sub(k.upper() + r"\.REPLACE", v, template)
        changed = True
        while changed:
            changed = False
            for pattern, f in match_to_func.items():
                new_t = pattern.sub(f, template)
                if new_t != template:
                    changed = True
                    template = new_t

        return template
