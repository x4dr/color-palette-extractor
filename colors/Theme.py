import re
from typing import Callable

from colors.Color import Color


class Theme:

    def __init__(self, colors, color_roles:dict[str, Color], variables:dict[str, str]):
        self.keys = {i: Color.from_hex(x) for i, x in enumerate(colors)}
        self.roles = {x: Color.from_hex(y) for x,y in  color_roles.items()}
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
        "HEX": Color.hex
    }

    def process_template(self, template: str) -> str:
        def p(s: str) -> list:
            return [float(x) for x in s.split(',') if x.strip()]

        def lam(func):
            return lambda match: str(func(Color.from_rgb(*p(match.group(1))),*p(match.group(2))).rgb).strip("[]")

        def prop(pr):
            return lambda match: str(pr.__get__(Color.from_rgb(*p(match.group(1)))))

        # A function to map regex patterns to replacement functions
        match_to_func: dict[re.Pattern, Callable] = {}

        for name, f in self.FUNCTIONS.items():
            match_to_func[re.compile(r'(\d+, ?\d+, ?\d+)\.' + name + r'\((.*?)\)')] = lam(f)

        for name, f in self.PROPERTIES.items():
            match_to_func[re.compile(r'(\d+, ?\d+, ?\d+)\.' + name + r'\b')] = prop(f)
        def handle_key(match):
            try:
                return str(self.keys.get(int(match.group(1))).rgb).strip("[]")
            except AttributeError:
                return match.group(0)
        def handle_role(match):
            try:
                return str(self.roles.get(match.group(1)).rgb).strip("[]")
            except AttributeError:
                return match.group(0)


        match_to_func[re.compile(r'ROLE\((\w+)\)')] = handle_role
        match_to_func[re.compile(r'KEY\((\d+)\)')] = handle_key
        #print_palette_terminal({"Roles": self.roles, "Colors": self.keys.values()},{})
        for k, v in self.variables.items():
            template = re.sub(k.upper() + ".REPLACE", v, template)
        change = True
        while change:
            change = False
            for pattern, f in match_to_func.items():
                try:
                    new_template = pattern.sub(f, template)

                    if new_template != template:
                        change = True
                        template = new_template
                except AttributeError:
                    #print("failed:", pattern)
                    pass # no substitution on error
        return template